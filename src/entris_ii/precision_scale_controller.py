"""PrecisionScaleController — SBI commands for the Sartorius Entris-II.

Single-class facade for the Sartorius Entris-II precision balance over
its USB-C virtual COM port, modelled on the SyringePumpController
pattern. SBI ASCII protocol per the Entris II Technical Note
"Commands (Data Input Format)" section.

This iteration ships the two read-only ID commands: model number
(``Esc x1_``) and serial number (``Esc x2_``). Write/control commands
(zero, tare, print, calibrate) are intentionally out of scope here.

Hardware assumptions: factory-default USB-C settings per the Entris II
BCE manual §7.3.4 DEVICE/USB — SBI mode, 9600 baud, ODD parity, 8 data
bits, 1 stop bit, no handshake.
"""

from __future__ import annotations

import logging
from types import TracebackType
from typing import ClassVar, Self

import serial
import serial.tools.list_ports


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

    # Format-2 command characters (Technical Note, commands table).
    CMD_MODEL_NUMBER: ClassVar[bytes] = b"x1_"
    CMD_SERIAL_NUMBER: ClassVar[bytes] = b"x2_"

    # Factory-default USB-C SBI parameters (Manual §7.3.4 DEVICE/USB).
    DEFAULT_BAUDRATE: ClassVar[int] = 9600
    DEFAULT_PARITY: ClassVar[str] = serial.PARITY_ODD
    DEFAULT_BYTESIZE: ClassVar[int] = serial.EIGHTBITS
    DEFAULT_STOPBITS: ClassVar[float] = serial.STOPBITS_ONE
    DEFAULT_TIMEOUT_S: ClassVar[float] = 2.0

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

    def _read_response(self) -> str:
        """Read one CR-LF terminated SBI response, stripped.

        Returns:
            The decoded response with trailing CR/LF and surrounding
            whitespace removed.

        Raises:
            RuntimeError: If the port is not open.
            TimeoutError: If CR-LF is not observed within the
                configured timeout.
        """
        if self._serial is None or not self._serial.is_open:
            raise RuntimeError("Serial port is not open")
        line = self._serial.read_until(self.CR + self.LF)
        if not line.endswith(self.CR + self.LF):
            raise TimeoutError(
                f"no CR-LF within {self.timeout}s; partial={line!r}"
            )
        self._log.debug("SBI rx: %r", line)
        return line.rstrip(b"\r\n").decode("ascii", errors="replace").strip()

    def get_model_number(self) -> str:
        """Return the balance model number via SBI ``Esc x1_``."""
        self._send_command(self.CMD_MODEL_NUMBER)
        return self._read_response()

    def get_serial_number(self) -> str:
        """Return the balance serial number via SBI ``Esc x2_``."""
        self._send_command(self.CMD_SERIAL_NUMBER)
        return self._read_response()
