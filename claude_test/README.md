# claude_test/

Index of debug and exploratory scripts. Scope and rules: see
[CLAUDE.md §3](../CLAUDE.md).

| Script | Purpose | Findings |
|---|---|---|
| [`test_read_id.py`](test_read_id.py) | Smoke-test `PrecisionScaleController.get_model_number` and `get_serial_number` against a real Sartorius Entris-II balance over USB-C SBI. | 2026-05-19 — passed on `/dev/ttyACM0`; balance replied with `'Model  BCE224I-1SKR'` and `'SerNo.    0047304196'`. Reply uses the 22-character "ID code" format (6-char label + 16-char value, per Technical Note); the class returns the raw stripped line so the label and value are both visible. |
| [`test_cal_and_read.py`](test_cal_and_read.py) | Smoke-test `calibrate_internal_very_unstable`, `read_stable_weight`, and `stream_stable_weights` on an empty pan. Verifies (a) post-cal value is within ±0.01 g of zero, (b) single stable read is within ±0.01 g of zero, (c) the stream yields exactly one initial zero and no further updates within the bounded observation window. | 2026-05-19 — passed on `/dev/ttyACM0` (BCE224I-1SKR). Cal sequence: `Esc s3_` → `Esc N` → `Esc x0_`, then ~15 s of polling `Esc kP` traversing `Stat Cal.Run.` → `Stat Cal.End` → unit-less drift values (-0.0007 → +0.0001) → final `G         0.0000 g`. Post-cal read = `+0.0000 g`. Stream first yield at +0.40 s = `+0.0000 g`; 16 subsequent stable reads over the 8 s window all returned `0.0` — no further yields. **Important finding**: Format-1 `Esc Z` only opens the internal-cal *menu* on this balance (shows `Stat Cal.Int.`) and waits for confirmation; Format-2 `Esc x0_` is what actually executes the procedure, so `CMD_INTERNAL_CAL` is set to `b"x0_"`. |
