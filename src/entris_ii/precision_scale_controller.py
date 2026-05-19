"""PrecisionScaleController — SBI commands for the Sartorius Entris-II.

Single-class facade for the Sartorius Entris-II precision balance over
its USB-C virtual COM port, modelled on the SyringePumpController
pattern. SBI ASCII protocol per the Entris II Technical Note
"Commands (Data Input Format)" section.

Iteration 2 adds internal calibration with ambient forced to "very
unstable" (``Esc N`` + ``Esc Z`` with polling) and stable-weight reads
under the "Manual with stability" printer menu setting — "Approach A"
in the design notes (``Esc kP``). The original read-only ID commands
(``Esc x1_``, ``Esc x2_``) from iteration 1 are unchanged.

Hardware assumptions: factory-default USB-C settings per the Entris II
BCE manual §7.3.4 DEVICE/USB — SBI mode, 9600 baud, ODD parity, 8 data
bits, 1 stop bit, no handshake. The stable-read and stream behaviours
additionally require the printer menu (Code 3.1.1.x) set to "Manual
with stability" so the balance buffers each print until stable.
"""

from __future__ import annotations

import logging
import re
import sys
import time
from collections import deque
from collections.abc import Iterator
from types import TracebackType
from typing import ClassVar, NamedTuple, Self

import serial
import serial.tools.list_ports


class WeightReading(NamedTuple):
    """One parsed weight measurement from an SBI print response.

    Attributes:
        value: Signed numeric weight parsed from the SBI line.
        unit: Unit symbol exactly as the balance returned it
            (typically ``'g'`` on the BCE224I).
        raw: The full stripped SBI line for downstream inspection.
    """

    value: float
    unit: str
    raw: str


class PrecisionScaleController:
    """SBI controller for the Sartorius Entris-II precision balance.

    Operators import a single name from this package::

        from entris_ii import PrecisionScaleController

        with PrecisionScaleController(port="/dev/ttyACM0") as scale:
            print(scale.get_model_number())
            print(scale.get_serial_number())

    The class wraps a ``serial.Serial`` instance and exposes the two
    read-only ID commands in this iteration; the rest of the SBI
    surface (zero, tare, print, calibrate) lands in follow-up tasks.
    """

    # Sartorius USB vendor ID, used by ``find_port`` auto-detection.
    SARTORIUS_VID: ClassVar[int] = 0x24BC

    # SBI framing bytes (Technical Note, "Format for Control Commands").
    ESC: ClassVar[bytes] = b"\x1b"
    CR: ClassVar[bytes] = b"\r"
    LF: ClassVar[bytes] = b"\n"

    # Format-1 single/short command characters (Technical Note, commands table).
    CMD_AMBIENT_VERY_UNSTABLE: ClassVar[bytes] = b"N"
    CMD_PRINT_KEY: ClassVar[bytes] = b"kP"
    CMD_CANCEL: ClassVar[bytes] = b"s3_"

    # Format-2 command characters (Technical Note, commands table).
    CMD_INTERNAL_CAL: ClassVar[bytes] = b"x0_"
    CMD_MODEL_NUMBER: ClassVar[bytes] = b"x1_"
    CMD_SERIAL_NUMBER: ClassVar[bytes] = b"x2_"

    # Note: Format-1 ``Esc Z`` ("Perform internal adjustment") only
    # opens the internal-cal menu on the BCE224I — it shows
    # ``Stat Cal.Int.`` on the display and waits for confirmation
    # rather than executing. Format-2 ``Esc x0_`` actually runs the
    # procedure, so that is what ``CMD_INTERNAL_CAL`` points to.

    # Factory-default USB-C SBI parameters (Manual §7.3.4 DEVICE/USB).
    DEFAULT_BAUDRATE: ClassVar[int] = 9600
    DEFAULT_PARITY: ClassVar[str] = serial.PARITY_ODD
    DEFAULT_BYTESIZE: ClassVar[int] = serial.EIGHTBITS
    DEFAULT_STOPBITS: ClassVar[float] = serial.STOPBITS_ONE
    DEFAULT_TIMEOUT_S: ClassVar[float] = 2.0

    # Timing knobs for the calibration polling loop and stable read.
    CAL_POLL_INTERVAL_S: ClassVar[float] = 1.0
    CAL_TIMEOUT_S: ClassVar[float] = 120.0
    STABLE_READ_TIMEOUT_S: ClassVar[float] = 30.0

    # Width (chars) of the elapsed/total progress bar rendered to
    # stderr during ``calibrate_internal_very_unstable``.
    CAL_PROGRESS_BAR_WIDTH: ClassVar[int] = 20

    # Default filter knobs applied by ``stream_stable_weights``.
    # ``JITTER_THRESHOLD`` suppresses readings whose absolute change
    # from the last emitted value is below this band. ``RISING_*``
    # implement a still-rising guard: once the rolling window of the
    # last ``RISING_WINDOW`` readings is full, the current reading is
    # held back while ``current - min(window) >= RISING_THRESHOLD``,
    # i.e. the balance is still meaningfully climbing. Pass
    # ``jitter_threshold=0`` or ``rising_window=0`` on the call to
    # opt out per-call.
    JITTER_THRESHOLD: ClassVar[float] = 0.01
    RISING_WINDOW: ClassVar[int] = 5
    RISING_THRESHOLD: ClassVar[float] = 0.05

    # Parse one signed decimal weight + unit anywhere in an SBI line.
    # Covers both the 16-char and 22-char (ID-coded) output formats —
    # the leading ID label (e.g. "N") never contains a sign-prefixed
    # decimal followed by a unit, so the search is unambiguous.
    _WEIGHT_RE: ClassVar[re.Pattern[str]] = re.compile(
        r"([+-]?)\s*(\d+(?:\.\d+)?)\s+([a-zA-Z]+)"
    )

    # Fallback for ID-coded lines emitted without a trailing unit,
    # e.g. ``'G         0.0000'`` observed on the BCE224I when the
    # balance prints the gross-weight ID label but omits the unit
    # field. Matches ``<id-label> <signed-numeric>`` with optional
    # trailing whitespace; the ID label is letters/digits/``#``.
    # Used only when ``_WEIGHT_RE`` misses, so unit-suffixed lines
    # continue to take the primary path.
    _WEIGHT_RE_ID_NO_UNIT: ClassVar[re.Pattern[str]] = re.compile(
        r"^([A-Za-z][A-Za-z0-9#]*)\s+"
        r"([+-]?)\s*(\d+(?:\.\d+)?)\s*$"
    )

    # Leading markers that indicate a status (not a real weight).
    # ``Stat`` is the explicit unstable indicator; ``H``/``High`` and
    # ``L``/``Low`` flag over- and under-load. These must raise
    # ``ValueError`` even when a numeric placeholder follows them,
    # otherwise the no-unit fallback above would silently treat an
    # unstable or out-of-range reading as a valid weight.
    _STATUS_PREFIX_RE: ClassVar[re.Pattern[str]] = re.compile(
        r"^(?:Stat|High|Low|H|L)\b"
    )

    # Error markers per Technical Note "Error Codes" tables.
    _ERROR_RE: ClassVar[re.Pattern[str]] = re.compile(
        r"\b(?:Err\s*\d+|APP\.ERR|DIS\.ERR|PRT\.ERR)\b"
    )

    @classmethod
    def find_port(cls) -> str | None:
        """Return the first detected Sartorius port path, or None.

        Scans available serial ports for a USB CDC ACM device whose
        vendor ID matches ``SARTORIUS_VID``. Used by demo and
        smoke-test scripts to avoid hard-coded device paths; the
        controller itself still requires an explicit ``port`` argument
        on construction.
        """
        for info in serial.tools.list_ports.comports():
            if info.vid == cls.SARTORIUS_VID:
                return info.device
        return None

    def __init__(
        self,
        port: str,
        baudrate: int = DEFAULT_BAUDRATE,
        parity: str = DEFAULT_PARITY,
        bytesize: int = DEFAULT_BYTESIZE,
        stopbits: float = DEFAULT_STOPBITS,
        timeout: float = DEFAULT_TIMEOUT_S,
    ) -> None:
        """Configure but do not yet open the serial connection.

        Args:
            port: Device path of the USB-C virtual COM port
                (typically ``/dev/ttyACM0`` on Linux).
            baudrate: SBI baud rate; factory default 9600.
            parity: Parity bit; factory default ``PARITY_ODD``.
            bytesize: Data bits; factory default 8.
            stopbits: Stop bits; factory default 1.
            timeout: Read timeout in seconds.
        """
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.bytesize = bytesize
        self.stopbits = stopbits
        self.timeout = timeout
        self._serial: serial.Serial | None = None
        self._log = logging.getLogger(self.__class__.__name__)

    def __enter__(self) -> Self:
        self.open()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def open(self) -> None:
        """Open the serial connection if it is not already open."""
        if self._serial is not None and self._serial.is_open:
            return
        self._serial = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            parity=self.parity,
            bytesize=self.bytesize,
            stopbits=self.stopbits,
            timeout=self.timeout,
            rtscts=False,
            xonxoff=False,
        )

    def close(self) -> None:
        """Close the serial connection if it is currently open."""
        if self._serial is not None and self._serial.is_open:
            self._serial.close()

    def _send_command(self, payload: bytes) -> None:
        """Send one SBI command, framed as ``ESC <payload> CR LF``.

        Args:
            payload: Command character(s) without framing bytes.

        Raises:
            RuntimeError: If the port is not open.
        """
        if self._serial is None or not self._serial.is_open:
            raise RuntimeError("Serial port is not open")
        frame = self.ESC + payload + self.CR + self.LF
        self._log.debug("SBI tx: %r", frame)
        self._serial.reset_input_buffer()
        self._serial.write(frame)
        self._serial.flush()

    def _read_response(self, timeout: float | None = None) -> str:
        """Read one CR-LF terminated SBI response, stripped.

        Args:
            timeout: Optional one-shot override of the port's read
                timeout (seconds). The previous timeout is restored on
                return regardless of outcome. When ``None`` the port's
                configured timeout is used.

        Returns:
            The decoded response with trailing CR/LF and surrounding
            whitespace removed.

        Raises:
            RuntimeError: If the port is not open.
            TimeoutError: If CR-LF is not observed before the read
                window expires.
        """
        if self._serial is None or not self._serial.is_open:
            raise RuntimeError("Serial port is not open")
        if timeout is None:
            line = self._serial.read_until(self.CR + self.LF)
            effective = self.timeout
        else:
            saved = self._serial.timeout
            try:
                self._serial.timeout = timeout
                line = self._serial.read_until(self.CR + self.LF)
            finally:
                self._serial.timeout = saved
            effective = timeout
        if not line.endswith(self.CR + self.LF):
            raise TimeoutError(
                f"no CR-LF within {effective}s; partial={line!r}"
            )
        self._log.debug("SBI rx: %r", line)
        return line.rstrip(b"\r\n").decode("ascii", errors="replace").strip()

    @classmethod
    def _parse_weight_line(cls, line: str) -> WeightReading:
        """Parse one SBI print response into a ``WeightReading``.

        Two response shapes are accepted:

        * Standard 16-char and 22-char forms with a trailing unit
          (e.g. ``'+    0.0000 g'`` or ``'N       0.0000 g'``).
        * ID-coded form without a trailing unit observed on the
          BCE224I (e.g. ``'G         0.0000'``). The returned
          ``unit`` is an empty string in this case so callers can
          still tell that no unit was reported.

        Lines whose leading marker is ``Stat`` (unstable), ``H`` /
        ``High`` (overload), or ``L`` / ``Low`` (underload) raise
        ``ValueError`` even when a numeric placeholder follows them.

        Args:
            line: One stripped SBI response line.

        Returns:
            ``WeightReading(value, unit, raw=line)`` for a numeric
            weight reply.

        Raises:
            RuntimeError: If the line carries an SBI error marker
                (``Err###``, ``APP.ERR``, ``DIS.ERR``, ``PRT.ERR``).
            ValueError: If the line is not parseable as a weight —
                e.g. ``Cal.Ext.`` (cal in progress), ``Stat``
                (unstable; menu misconfigured for Approach A),
                ``High`` (overload) or ``Low`` (underload).
        """
        if cls._ERROR_RE.search(line):
            raise RuntimeError(f"balance error response: {line!r}")
        if cls._STATUS_PREFIX_RE.match(line):
            raise ValueError(
                f"non-numeric SBI response (special/unstable): {line!r}"
            )
        match = cls._WEIGHT_RE.search(line)
        if match is not None:
            sign, digits, unit = match.groups()
        else:
            id_match = cls._WEIGHT_RE_ID_NO_UNIT.match(line)
            if id_match is None:
                raise ValueError(
                    f"non-numeric SBI response (special/unstable): {line!r}"
                )
            _, sign, digits = id_match.groups()
            unit = ""
        value = float(f"{sign or '+'}{digits}")
        return WeightReading(value=value, unit=unit, raw=line)

    def get_model_number(self) -> str:
        """Return the balance model number via SBI ``Esc x1_``."""
        self._send_command(self.CMD_MODEL_NUMBER)
        return self._read_response()

    def get_serial_number(self) -> str:
        """Return the balance serial number via SBI ``Esc x2_``."""
        self._send_command(self.CMD_SERIAL_NUMBER)
        return self._read_response()

    def calibrate_internal_very_unstable(
        self,
        timeout: float = CAL_TIMEOUT_S,
        poll_interval: float = CAL_POLL_INTERVAL_S,
    ) -> WeightReading:
        """Run internal calibration with ambient forced to very unstable.

        Sequence:
            1. ``Esc s3_`` (CANCEL) clears any leftover menu state.
            2. ``Esc N`` sets ambient conditions to "very unstable".
            3. ``Esc x0_`` triggers the internal calibration cycle.
            4. ``Esc kP`` is polled until a numeric weight response
               returns (``Cal.Run.`` / ``Cal.End`` / unit-less interim
               readings are treated as in-progress).

        The balance must carry the internal calibration weight option
        (e.g. ``BCE224I-1SKR``). The pan must be empty when this is
        called; the post-calibration reading is returned so the caller
        can verify the zero baseline.

        While polling, an elapsed/total progress bar is written to
        ``sys.stderr`` once per poll iteration and finalized with a
        newline on both the success and timeout paths.

        Args:
            timeout: Maximum seconds to wait for calibration to
                complete. Default ``CAL_TIMEOUT_S``.
            poll_interval: Seconds between ``Esc kP`` polls. Default
                ``CAL_POLL_INTERVAL_S``.

        Returns:
            The first parseable ``WeightReading`` (with unit) observed
            after the calibration finishes.

        Raises:
            TimeoutError: If no parseable weight response is observed
                within ``timeout`` seconds.
            RuntimeError: If the balance returns an error code during
                polling.
        """
        self._send_command(self.CMD_CANCEL)
        time.sleep(poll_interval)
        self._send_command(self.CMD_AMBIENT_VERY_UNSTABLE)
        self._send_command(self.CMD_INTERNAL_CAL)

        start = time.monotonic()
        deadline = start + timeout
        try:
            while time.monotonic() < deadline:
                time.sleep(poll_interval)
                self._render_cal_progress(time.monotonic() - start, timeout)
                self._send_command(self.CMD_PRINT_KEY)
                try:
                    line = self._read_response(timeout=poll_interval * 2)
                except TimeoutError:
                    continue
                try:
                    reading = self._parse_weight_line(line)
                except ValueError:
                    # Cal.Run. / Cal.End / Stat / unit-less post-cal —
                    # not done yet. Keep polling for the next response.
                    continue
                # Pin the bar to 100% before the trailing newline so
                # the final on-screen state matches the success.
                self._render_cal_progress(timeout, timeout)
                return reading
        finally:
            # Always close the carriage-return line so subsequent
            # log output starts on a fresh line — covers success,
            # timeout, and any unexpected raise from inside the loop.
            sys.stderr.write("\n")
            sys.stderr.flush()
        raise TimeoutError(
            f"internal calibration did not complete within {timeout}s"
        )

    def _render_cal_progress(
        self,
        elapsed: float,
        total: float,
    ) -> None:
        """Render the calibration progress bar to stderr in-place.

        Writes one carriage-returned line of the form
        ``  [##########..........] 45/90 s`` and flushes. The caller
        is responsible for emitting the final newline once polling
        finishes.
        """
        # Clamp so the bar never overshoots when the loop is about to
        # exit on the timeout boundary.
        clamped = max(0.0, min(elapsed, total))
        ratio = clamped / total if total > 0 else 1.0
        filled = int(ratio * self.CAL_PROGRESS_BAR_WIDTH)
        empty = self.CAL_PROGRESS_BAR_WIDTH - filled
        bar = "#" * filled + "." * empty
        sys.stderr.write(f"\r  [{bar}] {int(clamped):2d}/{int(total):2d} s")
        sys.stderr.flush()

    def read_stable_weight(
        self,
        timeout: float = STABLE_READ_TIMEOUT_S,
    ) -> WeightReading:
        """Read one stable weight value (Approach A).

        Sends ``Esc kP`` and reads one SBI response. Approach A assumes
        the printer menu (Code 3.1.1.x) is set to "Manual with
        stability" so the balance buffers the print until the reading
        stabilizes.

        Args:
            timeout: Read timeout in seconds. Default
                ``STABLE_READ_TIMEOUT_S``.

        Returns:
            The parsed ``WeightReading``.

        Raises:
            TimeoutError: If no response arrives within ``timeout``.
            ValueError: If the response is non-numeric — a ``Stat``
                prefix here indicates the menu is misconfigured for
                Approach A.
            RuntimeError: If the response carries an SBI error code.
        """
        self._send_command(self.CMD_PRINT_KEY)
        line = self._read_response(timeout=timeout)
        return self._parse_weight_line(line)

    def stream_stable_weights(
        self,
        timeout: float = STABLE_READ_TIMEOUT_S,
        interval: float = 0.1,
        jitter_threshold: float = JITTER_THRESHOLD,
        rising_window: int = RISING_WINDOW,
        rising_threshold: float = RISING_THRESHOLD,
    ) -> Iterator[WeightReading]:
        """Yield each new stable weight, with jitter + rising filters.

        Repeatedly calls :meth:`read_stable_weight`. Two filters
        decide whether a reading is yielded:

        * **Jitter** — readings whose absolute change vs. the last
          *yielded* value is below ``jitter_threshold`` are dropped.
          Pass ``0`` to fall back to exact-float deduplication only.
        * **Rising guard** — a rolling window of the last
          ``rising_window`` *jitter-passing* readings is kept; while
          the window is full and
          ``current - min(window) >= rising_threshold`` the current
          reading is held back as still-climbing. Pass
          ``rising_window=0`` to disable.

        Transient ``ValueError`` from :meth:`_parse_weight_line` is
        logged at debug level and skipped so a one-off non-numeric
        SBI line (``Stat``, overload markers, or the unit-less
        ID-coded shape) never tears down the loop.

        Args:
            timeout: Per-read timeout in seconds.
            interval: Sleep between consecutive
                :meth:`read_stable_weight` calls. A non-zero value
                keeps the loop from spinning hot once the balance
                has settled at the same reading.
            jitter_threshold: Inclusive lower bound on the change
                magnitude required for emission. Defaults to
                :attr:`JITTER_THRESHOLD`.
            rising_window: Size of the rolling history used by the
                rising guard. ``0`` disables the guard. Defaults to
                :attr:`RISING_WINDOW`.
            rising_threshold: Increase versus ``min(window)`` that
                marks the value as still climbing. Defaults to
                :attr:`RISING_THRESHOLD`.

        Yields:
            ``WeightReading`` instances that survive both filters.
        """
        last_yielded: float | None = None
        recent: deque[float] = deque(
            maxlen=rising_window if rising_window > 0 else 1
        )
        while True:
            try:
                reading = self.read_stable_weight(timeout=timeout)
            except ValueError as exc:
                # Transient non-numeric responses (``Stat``, overload,
                # or other unstable markers) should not kill the
                # stream — surface them at debug level and keep going
                # so the caller observes liveness on the next stable
                # tick.
                self._log.debug("skipping non-numeric SBI line: %s", exc)
                if interval > 0:
                    time.sleep(interval)
                continue
            val = reading.value
            # Jitter filter. ``delta == 0.0`` also covers exact-float
            # duplicates when the caller opts out of the jitter band
            # with ``jitter_threshold=0``.
            if last_yielded is not None:
                delta = abs(val - last_yielded)
                if delta == 0.0 or delta < jitter_threshold:
                    if interval > 0:
                        time.sleep(interval)
                    continue
            # Rising guard. Compare to the past window before
            # appending so the current reading is judged against
            # history; update the window regardless so the trend
            # keeps tracking.
            if rising_window > 0:
                rising = (
                    len(recent) == rising_window
                    and val - min(recent) >= rising_threshold
                )
                recent.append(val)
                if rising:
                    if interval > 0:
                        time.sleep(interval)
                    continue
            yield reading
            last_yielded = val
            if interval > 0:
                time.sleep(interval)
