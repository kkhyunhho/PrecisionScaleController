"""End-to-end demo of PrecisionScaleController.

Drives a real Sartorius Entris-II balance over USB-C SBI through every
feature the package exposes: ID queries, internal calibration with
ambient forced to "very unstable", a single stable read, and the first
stable-stream yield. Auto-detects the port by Sartorius USB vendor ID
0x24bc.

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

        # 4. First yield from the stable-weight stream — confirms the
        #    generator surface. Use the CLI's ``measure watch``
        #    subcommand for continuous monitoring.
        stream = scale.stream_stable_weights()
        try:
            first = next(stream)
        finally:
            stream.close()
        print(
            f"Stream first:  {first.value:+.4f} {first.unit} "
            f"(raw {first.raw!r})"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
