# ToDo

## GitHub README.md 작성

### 배경
CommonClaude.md 내용을 설명하는 README.md를 작성한다.
IDECommand.png, ShortCut.png 내용을 포함한다.

### 할 일

- [x] CommonClaude.md에 영어 작성 규칙 추가
- [x] README.md 작성 (영어)
  - [x] CommonClaude.md 내용 요약 및 설명
  - [x] IDE 명령어 정보 (IDECommand.png 참고)
  - [x] 단축키 정보 (ShortCut.png 참고)
- [x] GitHub 이슈 등록
- [x] 커밋 및 푸시
- [x] GitHub 이슈 업데이트

---

## CLAUDE.md 규칙을 Claude Code Hooks로 구현

### 배경
CLAUDE.md에 정의된 코딩 규칙(린트, 디버그 파일 배치, 작업관리 등)을 Claude Code hooks로 자동 강제하여, "읽고 따르는" 수준에서 "시스템이 자동 검증하는" 수준으로 강화한다.

### 할 일

- [x] `ruff.toml` 생성 (line-length=80, indent-width=4)
- [x] `.claude/hooks/` 디렉토리 생성
- [x] `pre-write-guard.sh` 작성 — tests/에 디버그 파일 쓰기 차단 (§2)
- [x] `post-write-lint.sh` 작성 — Python 파일 ruff check + format 피드백 (§5)
- [x] `post-write-debug-remind.sh` 작성 — claude_test/ 파일 추가 시 README 리마인더 (§2)
- [x] `.claude/settings.json` 작성 — Hook 설정 + Stop prompt hook (§3 ToDo/이슈 확인)
- [x] GitHub 이슈 등록
- [x] 커밋 및 푸시
- [x] GitHub 이슈 업데이트

---

## README.md에 /output-style 명령어 및 Hook 설명 추가

### 배경
README.md의 IDE Commands 표에 `/output-style`이 누락되어 있고, 직전에 추가된 Claude Code hooks 자동 강제 메커니즘에 대한 설명이 README에 없어 사용자가 프로젝트의 규칙 강제 방식을 이해하기 어렵다.

### 할 일

- [x] IDE Commands 표에 `/output-style` 행 추가
- [x] `Automated Enforcement (Hooks)` 섹션 신규 추가 (Convention Summary와 IDE Commands 사이)
- [x] GitHub 이슈 등록
- [x] 커밋 및 푸시
- [x] GitHub 이슈 업데이트

---

## Concept.md 내용 정리

### 배경
사용자가 Concept.md에 CommonClaude 개선 아이디어(ECC에서 선별 흡수할
Rule 재구조화, Token 최적화, Search-first, Learned Patterns 마이그레이션
등)를 작성하였다. 이를 읽고 섹션별로 구조화하여 사용자가 전체 구상을
한눈에 파악할 수 있도록 정리한다.
실제 적용은 본 작업 범위에서 제외하며, 이후 별도 세션에서 새 ToDo로
착수한다.

### 할 일

- [x] Concept.md 전체 내용 읽기
- [x] 6개 섹션으로 구조화된 요약 제공
      (철학 진단 / Rule 관점 / Rule 외 / 제외 항목 /
      Continuous-Learning 마이그레이션 Phase 0–5 / 최종 적용 순서)
- [x] GitHub 이슈 등록 (#12)
- [x] 커밋 및 푸시
- [x] GitHub 이슈 업데이트

---

## CommonClaude Improvement Track (from Concept.md)

### Background
Concept.md proposes seven incremental improvements adopted selectively
from ECC to strengthen CommonClaude while preserving its minimalist
philosophy. This entry decomposes that plan into seven independently
executable, independently rollbackable tasks. Each task gets its own
GitHub issue and its own commit. User approval is required at every
checkpoint marked **[APPROVAL]**. Phase 4 (continuous accumulation) is
a standing practice that begins once Tasks 1-7 land, and is therefore
not a discrete task here.

### Diagnosis Baseline (captured 2026-04-22)
- ToDo.md Completed: 4 top-level doc/setup tasks. Sample below the
  10-item threshold for pattern extraction; Task 5 will follow the
  "insufficient sample -> Phase 2 only" branch (Concept.md L99-101).
- CLAUDE.md: sections Overview, Environment, §1-§5 present. Missing:
  priority-override statement, Exceptions subsections, Research
  Before Coding section, Learned Patterns Reference section.
- Hooks present: pre-write-guard, post-write-lint,
  post-write-debug-remind, Stop prompt. Missing: Bash secret scan,
  Read env-file guard.
- MCP: no MCP config exists in repo. Task 3 is effectively null op
  unless the user decides to add filesystem MCP.

### Task 1. Restructure CLAUDE.md rule layer
Risk: low. Rollback: `git revert`.
Bundled with Tasks 2 and 4 under issue #14 per user decision.
- [x] Add priority-override statement near the top of CLAUDE.md
      ("Project-level CLAUDE.md rules override this global file")
- [x] Add Exceptions subsection under §2 Debug Files (waive 80-col
      and docstring requirements inside `claude_test/`)
- [x] Add Exceptions subsection under §4 Testing (allow magic
      numbers in one-off exploratory scripts when intent comment
      is present at file top)
- [x] **[APPROVAL]** Bundled approval granted 2026-04-22
- [x] GitHub issue register and cross-link (#14)
- [x] Commit and push (aa15cb9)
- [x] GitHub issue update (#14 closed)

### Task 2. Add token-optimization env vars
Risk: low. Rollback: `git revert`.
Bundled with Tasks 1 and 4 under issue #14 per user decision.
- [x] Add `env` block to `.claude/settings.json` with
      `MAX_THINKING_TOKENS=10000` and
      `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50`
- [x] Verify existing `hooks` block is untouched
- [x] **[APPROVAL]** Values confirmed as-is per user 2026-04-22
- [x] GitHub issue register (#14)
- [x] Commit and push (aa15cb9)
- [x] GitHub issue update (#14 closed)

### Task 3. MCP reconfiguration decision
Risk: low (decision only). Rollback: n/a (no repo change).
Resolved by user 2026-04-22: keep Context7 MCP as-is. No repo MCP
config is introduced. This task closes without file changes.
- [x] User decision: keep Context7 MCP, add nothing else
- [ ] GitHub issue register and close immediately as "no change"

### Task 4. Add Search-first section to CLAUDE.md
Risk: low. Rollback: `git revert`.
Bundled with Tasks 1 and 2 under issue #14 per user decision.
- [x] Draft a new §6 "Research Before Coding" covering doc lookup,
      prior-implementation search, and the rule against guessing
      APIs from memory
- [x] **[APPROVAL]** Bundled approval granted 2026-04-22
- [x] GitHub issue register (#14)
- [x] Commit and push (aa15cb9)
- [x] GitHub issue update (#14 closed)

### Task 5. Phase 0-1 diagnosis and (abridged) pattern extraction
Risk: low. Rollback: discard draft file.
Tracked under issue #16.
- [x] Document diagnosis outcome: sample < 10, Phase 1 extraction
      skipped per Concept.md L99-101 (recorded in #16 body)
- [x] Produce a short seed list of candidate patterns from the
      four Completed tasks plus current session — five
      workflow-level lessons L1-L5 (recorded in #16 body)
- [x] Superseded by #19 which applied the full §10 Bootstrap
      extraction across all ToDo.md Completed items; seed list
      content preserved in LearnedPatterns.md §4 Workflow Lessons
      (commit 24b6349). #16 closed 2026-04-22.

### Task 6. Create LearnedPatterns.md and wire it into CLAUDE.md
Risk: low. Rollback: delete file + `git revert` CLAUDE.md.
- [ ] Create `LearnedPatterns.md` seeded with Task 5 output and
      the section skeleton (§1-§5) from Concept.md L131-164
- [ ] Add §7 "Learned Patterns Reference" to CLAUDE.md instructing
      Claude to consult `LearnedPatterns.md` before drafting ToDo
- [ ] **[APPROVAL]** Show both artifacts
- [ ] GitHub issue register
- [ ] Commit and push
- [ ] GitHub issue update

### Task 7. Add secret-scan and env-file-guard hooks
Risk: medium (false positives can block legitimate work).
Rollback: disable in `settings.json` + `git revert` scripts.
- [x] Write `.claude/hooks/pre-bash-secret-scan.sh` blocking
      Bash commands that contain `sk-`, `ghp_`, `AKIA`, or
      obvious password literals (expanded to cover more vendor
      prefixes and `api_key=` / `access_token=` / etc.)
- [x] Write `.claude/hooks/pre-read-env-guard.sh` blocking
      reads of `.env`, `.pem`, `.key` (renamed from
      `pre-read-envfile-guard.sh` per user 2026-04-22)
- [x] ~~Add fixture scripts under `claude_test/`~~ dropped per
      user 2026-04-22; manual verification scenarios used instead
- [x] Wire both hooks into `.claude/settings.json` under
      `PreToolUse` with matchers `Bash` and `Read` respectively
- [x] **[APPROVAL]** Demonstrated block behaviour live in session
- [x] GitHub issue register (#15)
- [x] Commit and push (72fef2c — landed alongside Task 5 update)
- [x] GitHub issue update (#15 closed)

### Task Ordering and Independence
- Tasks 1, 2, 4 are independent and may be executed in any order.
- Task 3 is a decision gate and can run in parallel with others.
- Task 5 must precede Task 6.
- Task 7 is self-contained but its fixtures must land together
  with the hook scripts.

### Out of Scope
- Phase 4 ongoing accumulation: standing workflow, begins after
  Tasks 1-7 land.
- Phase 5 Stop-hook extension: deferred until pattern accumulation
  demonstrates a real need.

### Meta-task checklist (this drafting session)
- [x] GitHub umbrella issue registered (#13)
- [x] Commit and push draft (84d99f5)
- [x] User approved plan; Tasks 1+2+4 bundle executed in aa15cb9
- [x] Umbrella issue updated to reflect bundle closure

---

## Task 7 execution: secret-scan and env-file-guard hooks

### Background
Executing Task 7 from the umbrella plan (#13). Scope refinements
agreed with the user on 2026-04-22:
- Rename `pre-read-envfile-guard.sh` -> `pre-read-env-guard.sh`
  to match the user's preferred filename.
- Expand Bash scan to include `api_key=` literal in addition to
  `sk-`, `ghp_`, `AKIA`, `password=`.
- Drop `claude_test/` fixtures; use manual verification scenarios
  supplied by the assistant.

Verification strings such as `sk-test1234567890abcdef` are
illustrative test tokens, not real credentials.

### Work items
- [x] Write `.claude/hooks/pre-bash-secret-scan.sh`
- [x] Write `.claude/hooks/pre-read-env-guard.sh`
- [x] `chmod +x` both scripts
- [x] Register both hooks in `.claude/settings.json`
- [x] Manual verification: `sk-*`, `ghp_*`, `password=`, `api_key=`
      blocked via Bash; `.env` blocked via Read; benign `ls`
      command and `README.md` read pass through
- [x] GitHub issue register (#15)
- [x] Commit and push (72fef2c)
- [x] GitHub issue update and tick remaining Task 7 boxes

### Side fix
- [x] Install `jq` via apt; the existing three hooks also depend on
      it and were silently no-op'd before this fix.

### Scope notes
Bash pattern set finalized as: `sk-`, `ghp_`, `gho_`, `ghu_`, `ghs_`,
`github_pat_`, `AKIA*`, `AIza*`, `xox[baprs]-*`, `glpat-*`, plus
generic literal assignments `password=`, `api_key=`, `access_token=`,
`secret_key=`, `auth_token=`. Expanded beyond the original five per
user direction "암호 뿐만 아니라 API 키도 거부하도록".

---

## CLAUDE.md §7 — Learned Patterns Bootstrap rule

### Background
Splits Task 6 of the umbrella plan (#13) into Part A (rule) and
Part B (generate the file). User directed adding the bootstrap
procedure to `CLAUDE.md` now, so future sessions know how to
generate `LearnedPatterns.md` from `ToDo.md` when it is absent.
Tracked under issue #17.

### Rule outline
- Classify `[x]` items into §1-§5 plus §99 fallback.
- Each entry: Problem / Cause / Fix / Rule (one-liner each).
- Append `(from ToDo#N)` for traceability.
- `ToDo.md` stays append-only; `LearnedPatterns.md` is a new
  file in repo root; content in English; ambiguous items go
  to §99 rather than being guessed.

### Work items
- [x] Add §7 "Learned Patterns Bootstrap" to `CLAUDE.md`
- [x] GitHub issue register (#17)
- [x] Commit and push (4628a61)
- [x] GitHub issue update (#17 closed)

---

## CLAUDE.md restructure — Rule Priority, Exceptions, Learned Patterns Reference

### Background
User direction 2026-04-22: promote the existing `## Priority`
subsection and the two `### Exceptions` subsections to proper
numbered top-level sections, and add a new `Learned Patterns
Reference` section (distinct from the generation-rule §7
`Learned Patterns Bootstrap` that just landed). Tracked under
issue #18. No file change until the diff preview is approved.

### Work items
- [x] Draft proposed numbering map and new-section text
- [x] GitHub issue register (#18)
- [x] **[APPROVAL]** User approved 2026-04-22
- [x] Apply restructure (renumber §1-§7, add §1 Rule Priority,
      add §8 Exceptions, add §9 Learned Patterns Reference,
      move former §7 to §10 Learned Patterns Bootstrap)
- [x] Update internal cross-references (§1 Structure ->
      §2 Structure; §1 Documentation -> §2 Documentation;
      §1 Language rule -> §2 Language rule)
- [x] Commit and push (b2a39a1)
- [x] GitHub issue update (#18 closed)

---

## CLAUDE.md §8 — ToDo.md checkbox update exception

### Background
User direction 2026-04-22: the append-only rule in §4 Task
Management Rule 2 and the "do not modify ToDo.md" constraint in
§10 Learned Patterns Bootstrap were written to preserve history,
not to prohibit progress marking. Every task-completion step
flips a `[ ]` to `[x]`; this behavior needs an explicit carve-out
so future sessions do not misread the rule. Tracked under issue
#20.

### Work items
- [x] Add `ToDo.md checkbox updates` subsection under §8
- [x] GitHub issue register (#20)
- [x] Commit and push (17dee39)
- [x] GitHub issue update (#20 closed)

---

## Task 6 Part B — generate LearnedPatterns.md

### Background
Executes the §10 Learned Patterns Bootstrap procedure (added in
commit 4628a61, §7 at the time, §10 after restructure b2a39a1) to
materialize `LearnedPatterns.md` in the repo root. Classifies every
`[x]` item across `ToDo.md` into §1-§5 plus §99 per the bootstrap
rules. Task 5 seed list (#16) feeds into §4 Workflow Lessons but
the full analysis scans every Completed item, not just that seed.
Tracked under issue #19.

### Work items
- [x] Classify every `[x]` item in `ToDo.md` per CLAUDE.md §10
- [x] Write `LearnedPatterns.md` in repo root with 15 patterns
      across §1-§5 plus a §99 Uncategorized residual
- [x] GitHub issue register (#19)
- [x] Commit and push (24b6349)
- [x] GitHub issue update (#19 closed)

---

## Concept.md coverage verification

### Background
User asked whether every recommendation in `Concept.md` has been
reflected in the repo. This task cross-checks Concept.md's two parts
(Part 1 items 1-7, Part 2 Phase 0-5) and the final application order
L197-204 against landed commits, surfacing any gaps for decision.
Tracked under issue #21.

### Work items
- [x] Map each Concept.md recommendation to a commit or decision
- [x] Produce Done / Partial / Deferred table
- [x] Identify remaining gaps for user decision
- [x] GitHub issue register (#21)
- [ ] Commit and push
- [ ] GitHub issue update

---

## CLAUDE.md §11–§17 — Embed GitConvention.md Git workflow rules

### Background
User organized Git/GitHub workflow rules (Conventional Commits,
GitHub Flow, .gitignore, SemVer, PR guidelines, pre-commit
automation) in a new `GitConvention.md`. Embed the full content
into `CLAUDE.md` as §11–§17 so Claude has a single, complete
instruction set, and extend `§4 Task Management` workflow to
include branch-creation and PR-creation steps. Approved plan:
`/root/.claude/plans/github-pr-shiny-dahl.md` (2026-05-19).

### Work items
- [x] Apply Change A: expand §4 Workflow to 10 steps and extend
      the non-negotiable Reminder line
- [x] Apply Change B: append §11–§17 (Commit Messages, Branching,
      .gitignore, Versioning, PR Guidelines, Git Automation,
      References) with editorial adjustments — drop closing
      italic, dedupe MIT CommLab row in §17, add §2 Language
      cross-ref line at the top of §11
- [x] Verify §1–§17 numbering and internal `§N.M` cross-refs;
      confirm no contradiction with §2 Language or §6 Linting
- [x] GitHub issue register (#22)
- [x] Commit and push (c09781f, PR #23)
- [x] GitHub issue update — closure pending PR #23 merge

---

## Audit past GitHub issues per new CLAUDE.md §11/§15 rules

### Background
User direction 2026-05-19: now that §11 (Conventional Commits) and
§15 (Pull Request Guidelines) live in `CLAUDE.md`, retroactively
reformat issues #1–#21 to follow the new conventions. Issue #22
already conforms.

### Scope
- Title: reformat to `<type>(<scope>): <description>` per §11.
- Korean issues (#1, #2, #3 — title or body): translate to English
  per §2 Language.
- Body: align to §15.2 template — Changes / Why / Testing /
  Related Issues — preserving existing content where it fits.

### Execution
- Bundled into PR #23 per LP §W2 (low-risk, adjacent scope,
  pre-approved together by user follow-up).
- No new branch; work continues on `docs/embed-git-convention`.

### Work items
- [x] Draft proposed (title, body) for each of #1–#21
      (preserved at `/tmp/audit-proposal.md` during execution)
- [x] Present batch for user approval (approved 2026-05-19)
- [x] Apply via `gh issue edit` per issue (#1–#21 all updated)
- [x] GitHub issue register (audit meta-issue #24)
- [x] Commit ToDo.md updates and push (bundled into PR #23)
- [x] GitHub issue update — #24 to be closed via PR #23 merge

### PR audit note
Only PR #23 exists at this time and was authored to the new
conventions from the start. No retroactive PR edits required.

---

## Rename to PrecisionScaleController and apply CLAUDE.md /init improvements

### Background
User direction 2026-05-19: pivot this repo from a pure conventions
repository to the PrecisionScaleController project (Sartorius Entris-II
scale controller). The repo will be published as a new GitHub repo
named `PrecisionScaleController`. At the same time, apply the eight
self-init improvements surfaced by `/init`:
1. Fix broken `CommonClaude.md` self-references (file does not exist).
2. Update Overview to reflect the ScaleController project pivot.
3. Add a top-level Commands section.
4. Mark CLAUDE.md §10 Bootstrap as satisfied (LearnedPatterns.md exists).
5. Surface `jq` as a required system package in Environment.
6. Document the `env` block in `.claude/settings.json`.
7. Cross-link Stop-hook enforcement to §4 to remove duplication.
8. Add a Files index near the Overview.

### Work items
- [x] Append this ToDo.md entry
- [x] Cut working branch `docs/rename-and-init-improvements`
- [x] Apply eight CLAUDE.md improvements
- [x] Update README.md (broken references, project rename)
- [x] Stage explicit paths and commit (LP §W4)
- [x] Create new GitHub repo `PrecisionScaleController`
- [x] Retarget `origin` to the new repo and push
- [x] GitHub issue register and PR open
- [x] GitHub issue update on merge

---

## Scaffold PrecisionScaleController package (entris_ii)

### Background
Lay down the package skeleton modeled on
[coport-uni/SyringePumpController](https://github.com/coport-uni/SyringePumpController)
before any SBI implementation lands. Directory layout, package name,
and entry-point shape are decided in this step; concrete commands
ship in a follow-up ToDo entry.

### Design decisions (user 2026-05-19)
- Mirror SyringePumpController package layout, deferring
  `pyproject.toml`, `tests/`, `DESIGN.md`, and CI to later iterations.
- Package name `entris_ii` — device-model lowercase, matches the
  `sy01b` precedent.
- Class file `precision_scale_controller.py` (snake_case of class).
- Entry point `main.py` at repo root for end-to-end demo.
- `claude_test/` scripts use `sys.path.insert(0, "src")`; no install.
- Dependency: `requirements.txt` with `pyserial>=3.5`.
- `cli/` subpackage deferred — added when a second command lands.
- Scaffold = empty modules with one-line docstring; no function
  bodies in this commit. Hardware verification deferred to the
  follow-up implementation task per user direction.

### Work items
- [x] Append this ToDo entry
- [x] Cut working branch `chore/scaffold-entris-ii`
- [x] Create `requirements.txt` (`pyserial>=3.5`)
- [x] Create `src/entris_ii/__init__.py` (re-export stub)
- [x] Create `src/entris_ii/precision_scale_controller.py`
      (class stub with docstring)
- [x] Create `main.py` (entry stub with docstring + sys.path setup)
- [x] Create `claude_test/README.md` (index table header)
- [x] Create `claude_test/test_read_id.py` (stub with docstring +
      sys.path setup)
- [x] Ruff check + format pass on all `.py` files (§6)
- [x] GitHub issue register (#3)
- [x] Commit and push (7e9185d)
- [x] Open PR per §15.2 (#4)
- [x] GitHub issue update on merge (PR #4 merged as 222e856)

---

## Implement PrecisionScaleController read-only ID commands (entris_ii)

### Background
First runtime behaviour for PrecisionScaleController. Implements the
two factory-default read-only SBI commands and verifies them against
a real Sartorius Entris-II balance over USB-C. Builds on PR #4
scaffold (merged to main as 222e856).

References:
- [`entris-ii-technical-note-en-sartorius.pdf`](entris-ii-technical-note-en-sartorius.pdf)
  "Commands (Data Input Format)" — Format 2 `Esc x1_` / `Esc x2_`.
- [`manual-entris-bce-precisionbalances-wbc6001bo-pdf-62843--data.pdf`](manual-entris-bce-precisionbalances-wbc6001bo-pdf-62843--data.pdf)
  §7.3.4 DEVICE/USB — factory defaults: SBI, 9600 baud, ODD parity,
  8 data bits, 1 stop bit, no handshake.

### Hardware probe (2026-05-19, pre-task)
| Item | Value |
|---|---|
| Port | `/dev/ttyACM0` |
| VID:PID | `0x24bc:0x0010` (Sartorius) |
| Manufacturer | `Sartorius` |
| Product | `Sartorius Composite device` |

### Design decisions (user 2026-05-19)
- Class-level constants: `UPPER_CASE` + `ClassVar` per
  SyringePumpController precedent.
- Class requires explicit `port` argument; auto-detection via
  Sartorius VID `0x24bc` lives in `test_read_id.py` and `main.py`,
  with a manual `--port` override.
- LP §E4 (ruff missing from base image) bundled into this PR.

### Work items
- [x] Append this ToDo entry
- [x] Cut working branch `feature/sbi-readonly-id`
- [x] Install `pyserial` via `pip3 install --break-system-packages`
- [x] Implement `PrecisionScaleController` class
- [x] Wire `src/entris_ii/__init__.py` re-export
- [x] Implement `claude_test/test_read_id.py` (auto-detect by
      Sartorius VID, `--port` override)
- [x] Implement `main.py` (calls both methods, prints results)
- [x] Add LP §E4 — "Ubuntu 24.04 base image lacks `ruff`"
- [x] Ruff check + format pass
- [x] **Hardware verify** — passed on `/dev/ttyACM0`; balance returned
      `'Model  BCE224I-1SKR'` and `'SerNo.    0047304196'` in 22-char
      ID-code format
- [x] Update `claude_test/README.md` Findings column
- [x] GitHub issue register (#5)
- [x] Commit and push (cdf5c5d)
- [x] Open PR per §15.2 (#6)
- [x] GitHub issue update on merge (auto-closed by `Closes #5` in PR #6, merge ea43d8a)

---

## Refactor: extract CLI from main.py to entris_ii.cli (continues #5)

### Background
User direction 2026-05-19 after PR #6 was opened: `main.py` mixes the
end-to-end demo with argparse plumbing, which does not match the
SyringePumpController layout. Split the CLI surface into a
`entris_ii.cli` subpackage (parallel to `sy01b.cli`) so `main.py`
becomes a hard-coded demo and the parser logic lives in a dedicated
module. The refactor lands as additional commits on the same
`feature/sbi-readonly-id` branch and the same PR #6.

### Design decisions (user 2026-05-19)
- `main.py` is a no-argparse end-to-end demo with hard-coded sensible
  defaults (auto-detect port, INFO logging, run both ID queries).
- CLI lives at `src/entris_ii/cli/diagnose.py`, mirroring
  `sy01b/cli/diagnose.py`.
- `entris_ii.cli.diagnose` is invoked as a package module
  (`PYTHONPATH=src python -m entris_ii.cli.diagnose`); no sys.path
  manipulation inside the module.
- `claude_test/test_read_id.py` keeps its own argparse — it is a
  self-contained smoke script (CLAUDE.md §8 allows looseness in
  `claude_test/`).

### Work items
- [x] Append this ToDo entry
- [x] Create GitHub issue (#7)
- [x] Strip argparse from `main.py`
- [x] Create `src/entris_ii/cli/__init__.py`
- [x] Create `src/entris_ii/cli/diagnose.py` with `_build_parser` +
      `main(argv)` mirroring the `sy01b.cli.diagnose` pattern
- [x] Ruff check + format pass
- [x] **Hardware verify** — both `python main.py` and
      `PYTHONPATH=src python -m entris_ii.cli.diagnose` returned the
      same readout (`Model  BCE224I-1SKR` / `SerNo.    0047304196`);
      `-v` confirmed SBI tx `\x1bx1_\r\n` / `\x1bx2_\r\n`
- [x] Commit and push (081c562, lands on PR #6)
- [x] Comment on PR #6 noting the scope addition
- [x] GitHub issue update on merge (auto-closed by `Closes #7` added to PR #6 body, merge ea43d8a)

---

## Implement internal calibration (very-unstable mode) and stable weight read (entris_ii)

### Background
Second runtime increment for PrecisionScaleController. Adds two SBI
behaviours requested by user 2026-05-19, plus a streaming extension
clarified during ToDo review:

1. Internal calibration triggered with ambient conditions forced to
   "very unstable", to be executed when nothing rests on the pan.
2. Stable-weight read assuming the balance menu is configured for
   "Manual with stability" output (Approach A); the controller just
   sends the print command and reads the (already-stable) response.
3. Stable-weight stream: a generator and matching `watch` CLI
   subcommand that polls the stable read in a loop and emits each
   new stable value once (exact-float dedup), stopping only on
   Ctrl-C.

References:
- [`entris-ii-technical-note-en-sartorius.pdf`](entris-ii-technical-note-en-sartorius.pdf)
  Commands (Data Input Format): Format-1 `Esc N` (ambient: very
  unstable), `Esc Z` (perform internal adjustment — only for
  balances with internal weight), `Esc kP` (Key PRINT to all
  interfaces). Special Codes `Cal.Ext.`, `Stat`. Error codes
  `Err###`, `APP.ERR`, `DIS.ERR`, `PRT.ERR`.
- 22-char ID-code output format already observed in PR #6 hardware
  run (`Model  BCE224I-1SKR` — the `I-1S` suffix denotes the
  internal-weight option, so internal calibration is supported).

### Design decisions (user 2026-05-19)
- Branch base: `feature/cal-and-stable-read` cut from `main` after
  PR #6 merged (ea43d8a).
- Function 1 wait strategy: polling. After `Esc N` + `Esc Z`, poll
  `Esc kP` every `CAL_POLL_INTERVAL_S` until a non-`Cal.Ext.`,
  non-error weight response returns or `CAL_TIMEOUT_S` elapses.
- Function 2 return type: `WeightReading` NamedTuple with `.value`
  (float), `.unit` (str), `.raw` (str). Both parsed view and the raw
  SBI line are accessible.
- Stream dedup: exact float equality (`value != last_value`). No
  epsilon, no automatic stop condition — Ctrl-C only.
- CLI: new `src/entris_ii/cli/measure.py` (separate from
  `diagnose.py`, which is documented as never moving/zeroing/cal'ing).
  Subcommands `cal`, `read`, `watch`. Auto-detect port by Sartorius
  VID; `--port` override; `-v` verbose mirrors `diagnose`.
- `main.py` stays as the ID demo — no changes this PR.
- Internal helper: extend `_read_response` with an optional per-call
  `timeout` override so polling and stable-wait can use longer read
  windows without permanently bumping `self.timeout`.

### Approach A precondition (Function 2 and stream)
The balance menu must be configured to "Manual with stability"
(printer setting Code 3.1.1.x — factory default is `IND.NO`, manual
without stability). When configured this way, the balance buffers the
print request internally until the reading stabilizes and then emits
the value, so the controller only needs to send `Esc kP` and read one
line. The CLI prints a warning if a `Stat` prefix is observed in the
response (menu is misconfigured for Approach A).

### Work items
- [x] Append this ToDo entry
- [x] Create GitHub issue (#8)
- [x] Cut working branch `feature/cal-and-stable-read` from main
- [x] Add SBI command constants
      (`CMD_AMBIENT_VERY_UNSTABLE`, `CMD_INTERNAL_CAL`,
      `CMD_PRINT_KEY`, `CMD_CANCEL`)
- [x] Add `WeightReading` NamedTuple and `_parse_weight_line` helper
- [x] Extend `_read_response` with an optional per-call `timeout`
- [x] Implement `calibrate_internal_very_unstable(timeout)`
- [x] Implement `read_stable_weight(timeout)`
- [x] Implement `stream_stable_weights()` generator (with `interval`
      sleep to avoid hot-spinning when the stable value is unchanged)
- [x] Create `src/entris_ii/cli/measure.py` with `cal`, `read`,
      `watch` subcommands
- [x] Re-export `WeightReading` from `src/entris_ii/__init__.py`
- [x] Add `claude_test/test_cal_and_read.py` smoke script
- [x] Update `claude_test/README.md` index row
- [x] Ruff check + format pass
- [x] **Hardware verify** — passed on `/dev/ttyACM0` (BCE224I-1SKR):
      cal completed in ~15 s with `Esc s3_` → `Esc N` → `Esc x0_` and
      `Esc kP` polling; post-cal value `+0.0000 g`; single
      `read_stable_weight` `+0.0000 g`; `stream_stable_weights` first
      yield `+0.0000 g` at +0.40 s, 16 subsequent reads over 8 s all
      `0.0` — no further yields
- [x] Append LearnedPatterns §Q3 — `Esc Z` opens cal menu only;
      `Esc x0_` is what actually executes internal calibration
- [x] Scope addition (user 2026-05-19): extend `main.py` to demo the
      new features alongside the existing ID queries — runs cal +
      single stable read + first stream yield, supersedes the
      original "main.py stays as the ID demo" design decision
- [x] Commit and push (a2ec578)
- [x] Open PR per §15.2 (#9)
- [x] Scope addition (user 2026-05-19): bump `CAL_TIMEOUT_S`
      60 s → 90 s and render an elapsed/total progress bar on
      stderr from inside `calibrate_internal_very_unstable`
      (e.g. `[##########..........] 45/90 s`). Bar updates once
      per poll iteration via carriage return; final newline
      emitted on both success and timeout via try/finally so the
      bar never hangs without a line break. Library-internal
      output per user direction.
- [x] Ruff check + format pass on the patched module
- [x] Commit and push onto `feature/cal-and-stable-read` (4d3d1d8)
- [x] Update PR #9 with a comment reflecting the new scope
      (PR #9 comment 4488064721)
- [x] Follow-up tweak (user 2026-05-19): hardware test showed the
      90 s budget still gets exceeded, so bump `CAL_TIMEOUT_S`
      90 s → 120 s. Progress-bar denominator and clamp follow the
      new value automatically (no further code change required
      beyond the constant). Ruff pass, commit on
      `feature/cal-and-stable-read`, note on PR #9.
- [x] Follow-up tweak (user 2026-05-19): convert the final stage
      of `main.py` from a single `next(stream)` demo into a
      Ctrl-C-bounded continuous loop over `stream_stable_weights`
      so the printed value keeps refreshing as the balance reading
      changes. Mirrors `cli/measure.py watch` so `main.py` doubles
      as a live readout. Update the module docstring to match.
      Ruff pass, commit on `feature/cal-and-stable-read`, note on
      PR #9.
- [x] Bug fix (user 2026-05-19): hardware emits ID-coded SBI lines
      without a trailing unit (e.g. `'G         0.0000'`), which
      the current `_WEIGHT_RE` cannot parse and crashes
      `stream_stable_weights` with `ValueError`. Extend the parser
      with a fallback regex for `<id-label> <signed-value>` form
      (unit defaults to `""`), explicitly reject `Stat` / `H` /
      `L` / `High` / `Low` status prefixes via a new
      `_STATUS_PREFIX_RE`, and have `stream_stable_weights` swallow
      `ValueError` so transient non-numeric lines no longer kill
      the loop. Append a LearnedPatterns §3 entry for the quirk
      (LP §Q4). Ruff pass, commit on `feature/cal-and-stable-read`,
      note on PR #9.
- [ ] Follow-up tweak (user 2026-05-19): apply two output filters
      to `stream_stable_weights` inside the library
      (`src/entris_ii/precision_scale_controller.py`), not at the
      demo layer:
      1) jitter — drop readings whose absolute change vs. the last
      *emitted* value is below 0.001 (`JITTER_THRESHOLD`);
      2) rising guard — keep a rolling window of the last 5
      jitter-passing readings, and only emit the current reading
      when `current - min(window) < 0.05` (`RISING_THRESHOLD`,
      tightened from the initially proposed 0.1 per user).
      Expose all three knobs as keyword arguments on
      `stream_stable_weights` with class-constant defaults so the
      CLI `measure watch` and `main.py` benefit by default while
      callers can still override. `main.py` reverts to a plain
      stream consumer. Ruff pass, commit on
      `feature/cal-and-stable-read`, note on PR #9.
- [x] Final tweak (user 2026-05-19): `RISING_THRESHOLD` lowered
      from 0.1 to 0.05 to wait for a tighter steady state before
      emitting. Confirmed via the mocked-stream smoke test —
      the 0.2001 reading that previously emitted under 0.1 is now
      held until the value settles closer to 0.21.
- [ ] Final tuning before merge (user 2026-05-19):
      `JITTER_THRESHOLD` widened 0.001 → 0.01 to suppress
      hardware-observed wobble at the 0.001-g level; `main.py`
      calibration block re-enabled (previously commented out
      during streaming-only experiments) so the end-to-end demo
      again exercises cal → stable read → stream.
- [x] GitHub issue update on merge (closed via "Closes #8" footer
      in PR #9; merge commit 7a39d5d on main)

---

## Task #10 (2026-05-19): SBI intro in README + small post-merge tuning

Reorient the project README for a newcomer to balance/SBI work,
and clear two trailing post-merge items. GitHub issue #10, branch
`docs/sbi-intro-readme` cut from main at 7a39d5d.

References:
- [`entris-ii-technical-note-en-sartorius.pdf`](entris-ii-technical-note-en-sartorius.pdf)
  for the SBI command/response framing and special markers.
- LearnedPatterns §Q3 (`Esc Z` vs `Esc x0_`) and §Q4 (unit-less
  ID-coded response form) — both feed the protocol primer.

### Work items
- [x] Append this ToDo entry
- [x] Create GitHub issue (#10)
- [x] Cut working branch `docs/sbi-intro-readme` from main
- [x] Commit pending working-tree edit `CAL_TIMEOUT_S` 120 → 180
      as a standalone `chore(cal)` commit (acc9b87)
- [x] Update `README.md`:
      1) add a short "What this project does" + quick-start block;
      2) add a Mermaid `flowchart` rendering of `main.py`;
      3) add an SBI protocol primer (serial settings, command
         framing, Format-1 vs Format-2, the two response shapes
         incl. LP §Q4 unit-less form, status/error markers,
         "Manual with stability" menu requirement);
      4) add a brief package-layout pointer.
- [x] Flip the `[ ] GitHub issue update on merge` checkbox on the
      Task #8 entry
- [ ] Commit the README + ToDo updates separately from the
      `CAL_TIMEOUT_S` commit
- [ ] Push and open PR per §15.2 (closes #10)
- [ ] GitHub issue update on merge

---

## Task #11 (2026-05-20): Document menu-only calibration preconditions (STAB.RNG, COM.OUTP)

### Background
User asked whether `STAB.RNG=V.FAST` and `COM.OUTP=AUTO W/` can be set
via SBI as part of `calibrate_internal_very_unstable`. Research against
the Sartorius reference material confirmed both are **menu-only** on
the Entris-II BCE224I — there is no SBI command for either parameter:

- [`entris-ii-technical-note-en-sartorius.pdf`](entris-ii-technical-note-en-sartorius.pdf)
  p.4 SBI command tables list no command for STAB.RNG or COM.OUTP.
- [`manual-entris-bce-precisionbalances-wbc6001bo-pdf-62843--data.pdf`](manual-entris-bce-precisionbalances-wbc6001bo-pdf-62843--data.pdf)
  p.18 §7.3.1 (STAB.RNG) and p.22 §7.3.6 (COM.OUTP) define both as
  front-panel menu items only.

Since automation is impossible, document the requirement as a
hardware precondition in code docstrings, the README, and
LearnedPatterns. Decision (user 2026-05-20): merge both STAB.RNG and
COM.OUTP into a single docs branch `docs/cal-menu-preconditions`
(Option A) rather than splitting them.

### Design decisions (user 2026-05-20)
- Branch base: `docs/cal-menu-preconditions` cut from `main`.
- Recommended values:
  - `STAB.RNG = V.FAST` — fastest stability filter for the
    very-unstable ambient mode forced by `Esc N` during calibration.
  - `COM.OUTP = IND.AFTR` (manual after stability) — matches the
    current "Approach A" controller flow. Note in the docs that
    `AUTO W/` would push auto data on stability and would conflict
    with the polling-based Approach A, so it is intentionally not
    recommended despite the user's original question being about
    that value.
- AMBIENT is intentionally not added to the precondition list: it
  is SBI-settable (`Esc K/L/M/N`) and already driven by
  `calibrate_internal_very_unstable`, so operators do not need to
  pre-set it.
- LearnedPatterns gets two entries (§Q5 STAB.RNG and §Q6 COM.OUTP)
  rather than one combined entry, so each menu parameter is
  individually grep-able and traces back to a specific manual page.

### Work items
- [x] Append this ToDo entry
- [x] Create GitHub issue (#12)
- [x] Cut working branch `docs/cal-menu-preconditions` from main
- [x] Update `src/entris_ii/precision_scale_controller.py`:
      1) module docstring — extend the "Hardware assumptions"
         paragraph to list the two menu-only preconditions
         (STAB.RNG=V.FAST, COM.OUTP=IND.AFTR);
      2) `calibrate_internal_very_unstable` docstring — add an
         explicit "Preconditions" section that calls out the two
         menu settings and explains they cannot be set via SBI.
- [x] Update `README.md`:
      1) Quick Start step 1 — extend the comment block to mention
         pre-setting STAB.RNG=V.FAST in addition to the existing
         "Manual with stability" guidance;
      2) add a new subsection near "Manual with stability" titled
         "Menu-only calibration preconditions" covering the
         AMBIENT-vs-STAB.RNG distinction, the COM.OUTP value menu,
         the SBI-unsupported fact, and the front-panel menu paths.
- [x] Append `LearnedPatterns.md` §Q5 entry — "STAB.RNG is
      menu-only on the Entris-II; do not confuse with AMBIENT
      (Esc K/L/M/N)" using the Problem / Cause / Fix / Rule format.
- [x] Append `LearnedPatterns.md` §Q6 entry — "COM.OUTP (auto vs
      manual print, with/without stability) is menu-only; SBI only
      exposes the per-shot trigger via `Esc P` / `Esc kP`" using
      the Problem / Cause / Fix / Rule format.
- [x] Ruff check + format check on the modified Python file
- [x] Commit and push with `docs(scale):` Conventional Commits prefix (687e37a)
- [x] Open PR per §15.2 (closes #12) — PR #13
- [ ] GitHub issue update on merge (auto via `Closes #12` in PR #13)
