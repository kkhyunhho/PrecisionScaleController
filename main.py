"""End-to-end demo for PrecisionScaleController.

Run from the repo root::

    python main.py [--port /dev/ttyACM0] [--verbose]

Auto-detects the Sartorius Entris-II by USB vendor ID ``0x24bc`` when
``--port`` is omitted; falls back to the explicit device path
otherwise.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Repo layout: main.py at repo root, package under src/entris_ii/.
# Add src/ to sys.path so the package imports without an editable
# install (no pyproject.toml in this iteration).
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from entris_ii import PrecisionScaleController  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Read model and serial number from a Sartorius Entris-II "
            "balance over USB-C SBI."
        ),
    )
    parser.add_argument(
        "--port",
        default=None,
        help=(
            "Serial device path (e.g., /dev/ttyACM0). "
            "Default: auto-detect by Sartorius VID 0x24bc."
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable SBI tx/rx debug logging.",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        stream=sys.stderr,
    )

    port = args.port or PrecisionScaleController.find_port()
    if port is None:
        print(
            "error: no Sartorius device detected; pass --port",
            file=sys.stderr,
        )
        return 2

    print(f"Using port: {port}")
    with PrecisionScaleController(port=port) as scale:
        print(f"Model number:  {scale.get_model_number()}")
        print(f"Serial number: {scale.get_serial_number()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
