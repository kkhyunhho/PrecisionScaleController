# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Conventions

For the big picture and all shared conventions — the "one cell, many
devices" architecture, code style, repo skeleton, codename naming, the
driver API contract, the FastAPI `/v1` server standard, the hybrid
integration model, testing strategy, and task/commit rules — see
**SDLClaude** (`kkhyunhho/SDLClaude`), the single source of truth.

This file holds only what is specific to **PrecisionScaleController**: the
Sartorius Entris-II balance, its SBI protocol and front-panel
prerequisites, and this project's commands. Where this file is silent,
SDLClaude governs.

This project is a **device driver** for the codename **`entris_ii`**:
package [src/entris_ii/](src/entris_ii/), class `PrecisionScaleController`,
console scripts `entris-ii-diagnose` / `entris-ii-measure`.

## Repository status

The driver lives at [src/entris_ii/](src/entris_ii/) as a single
`PrecisionScaleController` class, modelled on `sy01b`. Read/tare/calibrate
and identity queries over the Entris-II USB-C virtual COM port are shipped;
bench scripts live in [claude_test/](claude_test/). Per the SDLClaude v2
standard this project still needs a `server/` FastAPI `/v1` bridge and a
`tests/` suite (tracked as Phase 2 cleanup).

## Environment

| Item    | Detail                                                      |
|---------|-------------------------------------------------------------|
| Runtime | Docker container (`--privileged`)                           |
| OS      | Ubuntu 24.04 (Noble)                                        |
| Python  | >= 3.12                                                     |
| Pkgs    | `jq` (`apt install -y jq`) — `.claude/` hooks no-op without it (LP §Q1/§E2) |

The harness `env` block in [`.claude/settings.json`](.claude/settings.json):
`MAX_THINKING_TOKENS=10000`, `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50`.

## Commands

All projects share one conda env, **`sdl`** (Python 3.12), where every
driver package is `pip install -e`'d. New terminals activate it.

```bash
conda activate sdl          # one-time: pip install -e ".[dev]"

ruff check src claude_test main.py        # lint (80-col)
ruff format --check src claude_test main.py
mypy                                       # strict types on src/entris_ii
entris-ii-diagnose                         # read-only identity/weight probe
```

## Hardware / domain notes

**Device:** Sartorius Entris-II precision balance (BCE224I), USB-C CDC-ACM
virtual COM port. Identify by USB identity — Sartorius VID `24BC`, balance
PID `0010` (`24BC:0010`); `find_port()` auto-detects by the Sartorius VID.

**SBI front-panel prerequisites (menu-only, not settable over the wire).**
The balance must be in SBI mode with stable-weight auto-push before a run:

- `DEVICE → (USB or RS232) → DAT.REC = SBI`
- `DATA.OUT. → COM. SBI → COM.OUTP = AUTO W/`
- `STAB.RNG = V.FAST`

SBI serial defaults: **9600 / ODD / 8 / 1**. A balance returning `0x15`
(NAK) to SBI commands is in xBPI mode — wrong interface menu.

**Settling:** post-action weights should wait for N consecutive
in-tolerance readings (settled weight), not a single auto-pushed value,
which can fire before the liquid settles. See [LearnedPatterns.md](LearnedPatterns.md).
