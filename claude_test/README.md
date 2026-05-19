# claude_test/

Index of debug and exploratory scripts. Scope and rules: see
[CLAUDE.md §3](../CLAUDE.md).

| Script | Purpose | Findings |
|---|---|---|
| [`test_read_id.py`](test_read_id.py) | Smoke-test `PrecisionScaleController.get_model_number` and `get_serial_number` against a real Sartorius Entris-II balance over USB-C SBI. | 2026-05-19 — passed on `/dev/ttyACM0`; balance replied with `'Model  BCE224I-1SKR'` and `'SerNo.    0047304196'`. Reply uses the 22-character "ID code" format (6-char label + 16-char value, per Technical Note); the class returns the raw stripped line so the label and value are both visible. |
