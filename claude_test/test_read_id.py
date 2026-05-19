"""Smoke test for PrecisionScaleController model and serial readout.

Scaffolding stub. Body lands with the follow-up SBI command task and is
run against a real Sartorius Entris-II balance over USB-C SBI.
"""

import sys
from pathlib import Path

# claude_test/ sits next to src/; add src/ to sys.path for imports.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
