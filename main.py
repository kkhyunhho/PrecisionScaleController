"""End-to-end demo of PrecisionScaleController.

Drives a real Sartorius Entris-II balance over USB-C SBI through every
feature the package exposes: ID queries, internal calibration with
ambient forced to "very unstable", a single stable read, and then a
continuous stable-weight stream that prints each new value until
Ctrl-C. Auto-detects the port by Sartorius USB vendor ID 0x24bc.

The continuous stream relies on :meth:`stream_stable_weights`, which
applies the library-level jitter + rising-guard filters by default
(see ``JITTER_THRESHOLD`` / ``RISING_WINDOW`` / ``RISING_THRESHOLD``
on ``PrecisionScaleController``).

The pan must be empty when this runs (the calibration step requires
it). For a flag-driven CLI see ``entris_ii.cli.diagnose`` (read-only)
and ``entris_ii.cli.measure`` (cal/read/watch). For narrower
per-feature bench scripts see ``claude_test/``.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Repo layout: main.py at repo root, package under src/entris_ii/.
# Add src/ to sys.path so the package imports without an editable
# install (no pyproject.toml in this iteration).
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from entris_ii import PrecisionScaleController  # noqa: E402


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        stream=sys.stderr,
    )

    port = PrecisionScaleController.find_port()
    if port is None:
        print("error: no Sartorius device detected", file=sys.stderr)
        return 2

    print(f"Using port: {port}")

    with PrecisionScaleController(port=port) as scale:
        # 1. Read-only identity queries (Esc x1_, Esc x2_).
        print(f"Model number:  {scale.get_model_number()}")
        print(f"Serial number: {scale.get_serial_number()}")

        # 2. Internal calibration with ambient forced to very unstable.
        #    Pan must be empty.
        print("Calibrating (ambient: very unstable)…")
        post_cal = scale.calibrate_internal_very_unstable()
        print(
            f"  post-cal: {post_cal.value:+.4f} {post_cal.unit} "
            f"(raw {post_cal.raw!r})"
        )

        # 3. One stable read.
        single = scale.read_stable_weight()
        print(
            f"Stable read:   {single.value:+.4f} {single.unit} "
            f"(raw {single.raw!r})"
        )

        # 4. Continuous stable-weight stream. The generator already
        #    applies the jitter + rising-guard filters; main.py
        #    just prints whatever it yields. Press Ctrl-C to stop.
        print("Streaming stable weights; press Ctrl-C to stop.")
        try:
            for reading in scale.stream_stable_weights():
                print(
                    f"  {reading.value:+.4f} {reading.unit} "
                    f"(raw {reading.raw!r})",
                    flush=True,
                )
        except KeyboardInterrupt:
            print("stopped.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
