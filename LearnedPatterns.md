# LearnedPatterns.md

> Patterns extracted from `ToDo.md` Completed items. Consult the relevant sections before drafting new ToDo entries. Append new patterns after each task completes (see CLAUDE.md §9 Learned Patterns Reference).
>
> Last updated: 2026-05-20
> Total patterns: 19
>
> Provenance format: `(from ToDo#N)` where N is the 1-based index of the top-level `##` section in `ToDo.md` at the time of extraction.

---

## §1. Recurring Issues

### R1. Stop hook halts tasks missing ToDo entry or GitHub issue

- **Problem**: Session ended with the Stop hook blocking because the user request had been fulfilled but no `ToDo.md` entry or GitHub issue existed for it.
- **Cause**: The SDLClaude Stop hook enforces a ToDo entry and a GitHub issue for every user-requested task, including read-only or informational ones; the check runs regardless of surface task type.
- **Fix**: Register a ToDo entry and a GitHub issue before responding to informational asks, not only before "code" work.
- **Rule**: Always create a ToDo entry and a GitHub issue for every user request, even read-only summaries or document reviews. (from ToDo#4, ToDo#5)

---

## §2. Solved Gotchas

### G1. `Edit(replace_all=true)` flips sibling skeletons

- **Problem**: Marking one task's checkboxes with `replace_all=true` also flipped identical `- [ ] Commit and push` / `- [ ] GitHub issue update` lines in unrelated sibling tasks.
- **Cause**: Checkbox skeleton lines repeat verbatim across many task entries, so the global replacement matched every instance.
- **Fix**: Reverted the unintended sibling changes via narrow context-scoped edits and re-committed.
- **Rule**: Never use `replace_all=true` on short skeleton lines that repeat across sibling sections. Scope the match with unique surrounding context instead. (from ToDo#5)

### G2. Unrelated staged changes ride along on commits

- **Problem**: A commit scoped to `ToDo.md` also included hook scripts and `settings.json` wiring because the git index already held earlier user-side edits.
- **Cause**: `git add <path>` adds to the existing index rather than defining the final commit set; unrelated staged changes carry over.
- **Fix**: Documented the bundling on the relevant issue and continued; all included content was intentional at the repo level.
- **Rule**: Always run `git status` and `git diff --cached --stat` immediately before `git commit`. Treat unexpected files in the index as an alert. (from ToDo#5, ToDo#6)

### G3. IDE auto-trim creates phantom whitespace diffs

- **Problem**: Opening `Concept.md` in the IDE produced a 2-blank-line trim that would have polluted commits scoped to other files.
- **Cause**: The IDE trims trailing blank lines on save or open; the change appears in `git status` as `modified:` even though the assistant did not touch the file.
- **Fix**: Staged only the intentionally modified files and left `Concept.md` unstaged.
- **Rule**: When `git status` shows modifications to files you did not touch, stage explicit paths only; never use `git add -A` or `git add .`. (from ToDo#5)

### G4. `gh issue close` after `Closes #N` commit returns "already closed"

- **Problem**: A follow-up `gh issue close` call reported the issue was already closed because the preceding commit carried `Closes #N` in its message.
- **Cause**: GitHub auto-closes issues referenced with `Closes/Fixes/Resolves #N` when the commit lands on the default branch.
- **Fix**: Used `gh issue comment` to attach trailing notes instead of a redundant close call.
- **Rule**: Never chain `gh issue close` after a commit whose message already contains `Closes #N`; use `gh issue comment` for trailing notes. (from ToDo#5)

---

## §3. Library Quirks

### Q1. `jq` is required by hooks but not pre-installed

- **Problem**: Three existing hook scripts silently no-op'd because `jq` was missing from the container image.
- **Cause**: Base Ubuntu 24.04 ships without `jq`, and the hooks parse tool-input JSON through it.
- **Fix**: Installed `jq` via `apt install -y jq` as a side fix during Task 7.
- **Rule**: Always verify `jq` is present in hook scripts with `command -v jq` and surface a clear error when it is missing. (from ToDo#6)

### Q2. Secret-scan PreToolUse hook inspects the entire Bash command string

- **Problem**: Heredoc bodies passed to `gh issue create --body` or `git commit -m` can match credential-like patterns even when the literal strings are illustrative, tripping the secret-scan hook.
- **Cause**: The hook scans the full Bash `command` string before execution, including everything inside `<<'EOF' ... EOF` blocks.
- **Fix**: Describe credential patterns with wildcards or obfuscated variants (for example `sk-*`, `ghp_*`) in Bash payloads. Keep literal test strings confined to file content written via Write or Edit.
- **Rule**: Never embed literal credential prefixes in Bash command strings; such strings are safe only in files written via Write/Edit. (from ToDo#6)

### Q3. Sartorius SBI Format-1 `Esc Z` opens cal menu but does not execute

- **Problem**: Calibration command `Esc Z` ("Perform internal adjustment", Format 1) caused the BCE224I-1SKR to display `Stat Cal.Int.` and wait for confirmation indefinitely. `Esc kP` polling returned `Stat Cal.Int.` and (after polling resumed) `Stat Cal.Run.` but the procedure never produced a post-cal weight.
- **Cause**: On this Entris-II model, Format-1 `Esc Z` only opens the internal-cal *menu* (the same screen the front-panel CAL key opens) and waits for user confirmation. The PDF "Commands (Data Input Format)" table lists both `Z` (Format 1) and `x0_` (Format 2) under footnote ¹⁾ "only for balances with internal weight" but does not explain that they have different effects.
- **Fix**: Use Format-2 `Esc x0_` ("Internal calibration") to actually trigger the procedure. Cal completes in ~15 s on an empty pan; polling traverses `Stat Cal.Run.` → `Stat Cal.End` → a few unit-less drift values (e.g. `G   -   0.0007`) → the final unit-bearing zero (`G         0.0000 g`).
- **Rule**: Always use Format-2 `Esc x0_` for SBI-driven internal calibration on Entris-II. Treat Format-1 `Esc Z` as a "show menu" command, not an execute command. (from ToDo#21)

### Q4. Sartorius SBI emits unit-less ID-coded lines during normal operation

- **Problem**: `stream_stable_weights` crashed with `ValueError: non-numeric SBI response (special/unstable): 'G         0.0000'` on hardware. The initial `read_stable_weight` succeeded, then subsequent stream reads occasionally returned ID-coded lines with no trailing unit field, which the unit-suffixed-only regex could not parse.
- **Cause**: The BCE224I sometimes emits the 16-char ID-coded form `<ID-label> <signed-value>` without a unit suffix even after `Cal.End` — not only as a brief drift line during internal calibration (already covered by Q3) but also intermittently during normal Approach-A stable reads. The original `_WEIGHT_RE` only matched `<value> <unit>`, so any unit-less line raised `ValueError` and propagated up through `read_stable_weight` into the generator.
- **Fix**: Added a `_WEIGHT_RE_ID_NO_UNIT` fallback regex (`<id-label> <signed-numeric>`, unit defaults to `""`) and a `_STATUS_PREFIX_RE` so unstable/overload/underload markers (`Stat` / `H` / `High` / `L` / `Low`) still raise `ValueError` even when followed by a numeric placeholder. `stream_stable_weights` additionally catches `ValueError` and logs the skip at debug level so a transient non-numeric line never kills the loop.
- **Rule**: Always accept the unit-less ID-coded SBI shape as a valid weight reading (with `unit=""`), and always make long-running SBI streams tolerant of transient `ValueError` from the parser. Never let status-prefixed lines (`Stat`, `H`, `L`) slip through the no-unit fallback. (from ToDo#28)

### Q5. Sartorius STAB.RNG is menu-only — distinct from AMBIENT (Esc K/L/M/N)

- **Problem**: User requested code that also sets `STAB.RNG = V.FAST` whenever `calibrate_internal_very_unstable` runs, expecting it to be SBI-settable alongside the AMBIENT hint that the method already emits via `Esc N`.
- **Cause**: The Entris-II Technical Note p.4 SBI command tables list no Format-1 or Format-2 command for `STAB.RNG`. The BCE manual §7.3.1 p.18 defines STAB.RNG as a front-panel menu item only (values `V.ACC.` / `ACC.` / `FAST` / `V.FAST`). It is visually adjacent to AMBIENT in the menu and they read like the same parameter, but only AMBIENT has SBI commands `Esc K` (V.STABLE) / `Esc L` (STABLE) / `Esc M` (UNSTABL.) / `Esc N` (V.UNSTBL.).
- **Fix**: Cannot be automated. Documented as a hardware precondition in the module docstring, the `calibrate_internal_very_unstable` docstring, and a new README "Menu-only calibration preconditions" subsection. Operators must set `STAB.RNG = V.FAST` on the front panel once at setup; the balance persists it across power cycles.
- **Rule**: Always check the SBI command tables (Technical Note p.4) before promising automation of a Sartorius menu parameter. Never conflate STAB.RNG with AMBIENT — STAB.RNG is menu-only on the Entris-II BCE224I; only AMBIENT is SBI-controlled. (from ToDo#30)

### Q6. Sartorius COM.OUTP is menu-only; mixing Esc kP with AUTO W/ makes the balance beep continuously

- **Problem**: PR #13 (Task #11) initially recommended `COM.OUTP = IND.AFTR` and framed `AUTO W/` as conflicting with `Esc kP` polling on the grounds that AUTO W/ "would push auto data on stability". The framing was wrong on the stability axis — both values are stability-gated — and missed the empirically observed real issue: with `COM.OUTP = AUTO W/` set on the balance, the current `Esc kP` polling code does work end-to-end, but the balance beeps continuously in a "device busy" state because each `Esc kP` request overlaps with the auto-push stream and keeps the print engine running.
- **Cause**: AUTO W/ has the balance autonomously emit one line on each stability event; `IND.AFTR` has the balance emit one line in response to each `Esc kP`. Issuing `Esc kP` while AUTO W/ is also pushing causes both paths to be active simultaneously, which the firmware reports as the audible busy state. The two COM.OUTP values are equivalent on stability gating; the meaningful axis is **who initiates the read** (host-polled vs. balance-pushed). Technical Note p.4 lists no SBI command that selects between the four COM.OUTP values, so the choice is forced into the front-panel menu (BCE manual §7.3.6, p.22).
- **Fix**: Recommend `COM.OUTP = AUTO W/` paired with a passive read loop (Task #12, "Approach B"). `read_stable_weight` no longer issues `Esc kP` and simply calls `_read_response`; `stream_stable_weights` reads the auto-push stream directly with the existing jitter / rising-guard filters and no `interval` sleep (cadence is now data-driven). The calibration polling loop inside `calibrate_internal_very_unstable` keeps `Esc kP` because it needs `Cal.Run.` / `Cal.End` progress markers that AUTO W/ does not push spontaneously.
- **Rule**: Always pair the COM.OUTP value with the matching host-side read pattern — `AUTO W/` with passive read, `IND.AFTR` with `Esc kP` polling. Never mix `Esc kP` with `AUTO W/` outside calibration progress polling, or the balance will continuously beep from the busy state. (from ToDo#31)

---

## §4. Workflow Lessons

### W1. Informational tasks still require the full SDLClaude workflow

- **Lesson**: Read-and-summarize requests were initially treated as workflow-exempt and triggered a Stop hook block at the end of the session.
- **Rule**: Always write a ToDo entry and open a GitHub issue for every user request, including summaries, code reviews, and exploratory reads. (from ToDo#4)

### W2. Bundle low-risk independent tasks under one issue when pre-approved

- **Lesson**: Tasks 1, 2, 4 of the improvement plan landed as a single commit under issue #14 because the three edits were independent, low-risk, and approved together.
- **Rule**: Bundle only when tasks are (a) low-risk, (b) independent of each other, and (c) pre-approved together by the user. Otherwise keep one commit per task. (from ToDo#5)

### W3. User prefers diff-first approval for structural edits

- **Lesson**: The CLAUDE.md restructure was presented as a structured proposal and approved before any file edit ran.
- **Rule**: Always preview structural edits (renumbering, section reorganization, content migration) as text or a preview diff before executing. Apply only after explicit user approval. (from ToDo#8)

### W4. Stage explicit file paths; never `git add -A` or `git add .`

- **Lesson**: Broad staging risks pulling in IDE auto-trim whitespace changes, unrelated scratch files, or previously-staged artifacts.
- **Rule**: Always stage files by explicit path and verify the staged set with `git status` plus `git diff --cached --stat` before committing. (from ToDo#5)

### W5. Use `Closes #N` in commit messages to auto-close issues

- **Lesson**: `Closes #N` in the commit body closes the referenced issue when the commit lands on the default branch; explicit `gh issue close` afterwards is redundant and errors.
- **Rule**: Always write `Closes #N` (or `Refs #N` for partial work) in commit messages. Follow up with `gh issue comment` for trailing notes instead of `gh issue close`. (from ToDo#5)

---

## §5. Environment Specifics

### E1. Docker `--privileged` warrants strict Read guards on credentials

- **Note**: The container runs with `--privileged`, which raises the impact of any accidental read of `.env`, `.pem`, or `.key` files.
- **Rule**: Always gate reads of credential-bearing files behind a PreToolUse hook in any `--privileged` Docker environment. (from ToDo#6)

### E2. Ubuntu 24.04 base image lacks `jq`

- **Note**: Hook scripts that parse JSON input with `jq` fail silently because the binary is absent from the base image.
- **Rule**: Always verify `jq` availability in the hook prelude and install via `apt install -y jq` as a one-time setup step. (from ToDo#6)

### E3. `$CLAUDE_PROJECT_DIR` is the portable repo-root path in hooks

- **Note**: Hooks are invoked from arbitrary working directories, so absolute paths must be derived from `$CLAUDE_PROJECT_DIR`.
- **Rule**: Never hardcode a repo path in hook scripts; always reference `$CLAUDE_PROJECT_DIR`. (from ToDo#2)

### E4. Ubuntu 24.04 base image lacks `ruff`

- **Note**: CLAUDE.md §6 mandates `ruff check` and `ruff format --check` before every commit, but the base image ships without `ruff`. Commands fail with `ruff: command not found` on first attempt.
- **Rule**: Always verify `ruff` availability before the first Python edit; install via `pip3 install --break-system-packages ruff` (PEP 668 override is required on Ubuntu 24.04+ system Python). (from ToDo#15)

---

## §99. Uncategorized

Items that recur across nearly every top-level ToDo task as procedural ritual rather than distinct patterns. Preserved here so the full `[x]` inventory from `ToDo.md` is accounted for, per CLAUDE.md §10 Bootstrap rule 3.

- Per-task workflow steps: `GitHub 이슈 등록`, `커밋 및 푸시`, `GitHub 이슈 업데이트`. These are workflow scaffolding captured in §4 Task Management of CLAUDE.md, not lessons.
- Content writes that are task-specific and yield no transferable rule: README sections (from ToDo#1, ToDo#3), individual CLAUDE.md section bodies added during the improvement track (from ToDo#5, ToDo#7, ToDo#8, ToDo#9).
- One-shot directory or config creations: `ruff.toml`, `.claude/hooks/` directory, `.claude/settings.json` base structure (from ToDo#2).
- Per-task approval checkpoints (`[APPROVAL]`) — subsumed into W3.
- Manual verification steps for hook behavior (from ToDo#6) — subsumed into Q2.
