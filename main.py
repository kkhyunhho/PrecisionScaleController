"""End-to-end demo of PrecisionScaleController read-only ID commands.

Reads the model number and serial number from a Sartorius Entris-II
balance over USB-C SBI and prints them. Auto-detects the port by
Sartorius USB vendor ID 0x24bc.

For a CLI with --port and --verbose flags, see
``entris_ii.cli.diagnose``. For narrower per-feature bench scripts,
see ``claude_test/``.
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
