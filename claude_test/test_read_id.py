"""Smoke test for PrecisionScaleController model and serial readout.

Runs the two SBI ID commands against a real Sartorius Entris-II
balance over USB-C and prints the captured values. Auto-detects the
port by Sartorius USB vendor ID ``0x24bc`` unless ``--port`` is
supplied.

Usage::

    python claude_test/test_read_id.py [--port /dev/ttyACM0]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# claude_test/ sits next to src/; add src/ to sys.path for imports.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from entris_ii import PrecisionScaleController  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", default=None)
    args = parser.parse_args(argv)

    port = args.port or PrecisionScaleController.find_port()
    if port is None:
        print("error: no Sartorius device detected", file=sys.stderr)
        return 2

    print(f"port: {port}")
    with PrecisionScaleController(port=port) as scale:
        model = scale.get_model_number()
        serial_no = scale.get_serial_number()
    print(f"model_number:  {model!r}")
    print(f"serial_number: {serial_no!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
