# Loop guardrails

Code-enforced guards for autonomous Claude loops. Generalized from val26's
production loop runs (July 2026: voting pilot $8.54, discourse batch 8×8
areas, valkompass v3). The core lesson: **hooks, tool lists and model
instructions are configuration, not enforcement — only guards in code held.**

**Rule zero: no binary exit condition → no loop.** Loop only what is
deterministically verifiable (derivation, structure, thresholds, render,
lint rules). The loop builds a verified baseline; a human edits on top.
Aesthetic judgment is never a stop condition.

## Files

| File | Purpose |
|---|---|
| `run-loop.sh` | The v3 standard loop orchestrator (see "The v3 loop" below). |
| `lib.js` | State + cost engine (Node — floats live here). Fail-closed on anything unparsable. |
| `guards.sh` | Source-able bash guards. Every loop entrypoint sources this. |
| `loop.env.example` | Budget/branch/model/cap configuration template. |
| `prompts/worker-draft.md` | Draft-worker prompt skeleton — fill in the `{{PLACEHOLDERS}}` per task. |
| `prompts/worker-fix.md` | Fix-worker prompt skeleton — the orchestrator appends validator findings. |
| `validate-example.js` | Working example validator (derivation/coverage/structure/scope). Copy + adapt per loop. |
| `test-guards.sh` | Guard test suite. Run it green before trusting any loop. |

## The v3 loop (run-loop.sh)

```
INIT -> DRAFT -> VERIFY -> [FIX -> RE-VERIFY] -> SYMMETRY* -> DELIVER
        1 call   $0, grep   1 call    $0                       .loop/report.md
        expensive first     cheap
```

One draft by the expensive model (`LOOP_MODEL_DRAFT`), deterministic
verification FIRST (validators, zero tokens), at most ONE fix round by the
cheap model (`LOOP_MODEL_FIX`) against the exact findings, deterministic
re-verification. Findings that survive the fix round go to the report and
`.loop/issue-draft.md` for a human — never to more model rounds, and the
loop never lets one model judge another. `SYMMETRY` is a no-op placeholder
until MÅL 4.

Every model call is wrapped in: wall-clock gate, task budget gate, step
budget gate (all BEFORE the call), transient-only retry, fail-closed cost
ingest, and the HEAD-guard (self-heal + one redo; two tampers fail the
task). The loop never commits — the human (or an outer wrapper) commits
after reading `.loop/report.md`. Prompts instruct workers to fetch the
SPECIFIC listed resources and chunk large documents (compact sessions:
each step is its own `claude -p` call).

Testing without cost: point `LOOP_CLAUDE_BIN` at a stub that prints
`total_cost_usd` JSON — that is exactly what guard test 14 does.

Orchestrator-level exit codes on top of the contract below: `1` =
delivered with unresolved validator findings (report + issue draft
written), `2` = model call failed hard (non-limit).

## Exit-code contract

| Code | Name | Meaning | Retryable? |
|---|---|---|---|
| 0 | OK | Done / gate passed | — |
| 3 | BUDGET | Budget, iteration or wall-clock cap reached | **NEVER** |
| 4 | FAILCLOSED | A guard could not measure (unparsable state/cost, wrong branch, no sandbox, refused resume) | **NEVER** |
| 5 | TRANSIENT | Transient failure / usage limit | Yes — `retry_transient` only |
| 6 | SCOPE | Same scope violation two iterations in a row (worker↔validator deadlock) | **NEVER** — human decision |
| 7 | TAMPER | Worker committed; self-healed via soft-reset + incident log | Redo step; 2 per task ⇒ fail task |

Semantic codes (3/4/6/7) must never be classified as limits. Limit
detection via file grep must be mtime-scoped to the current step
(`limit_detect <dir> <sinceEpoch>`); greping old logs misclassifies
semantic stops as limits.

## Guard catalog

- `budget_gate <usd>` — checked BEFORE every paid call, never after.
- `step_budget_gate <spentBefore> <cap>` — per-step caps that sum to the task cap.
- `iteration_gate <i> <max>` / `wall_clock_gate <start> <maxSec>` — hard caps.
- `branch_guard <branch>` — loops never run on the wrong branch.
- `sandbox_check` — git work tree + writable state dir, before every writing iteration.
- `head_guard_snapshot` / `head_guard_enforce <sha> <task>` / `tamper_exceeded <task>` — workers never commit; tamper is self-healed, always incident-logged, two strikes fails the task.
- `limit_detect <dir> <since>` — mtime-scoped limit grep.
- `retry_transient <max> <backoff> <cmd…>` — retries exit 5 ONLY.
- `resume_guard` — resumes ONLY `status=usage_interrupted`, never starts fresh.
- `detached_launch <script> <log> [name]` — schtasks (Windows) / setsid (Linux); long runs must survive their parent.

`guards.sh` also exports `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` — mandatory in
all loop scripts (large WebFetch calls otherwise trigger a 1M-context
upgrade that requires usage credits and kills the run).

## Validator output contract

`lib.js scope-violations` parses validator failure text. Deterministic
validators should emit violations in one of these line formats (or set
`LOOP_SCOPE_TARGET_RE` / `LOOP_SCOPE_DIRTY_RE`):

```
- <key>: changed, but is not one of the N target entries
- unexpected modified tracked file: <path>
```

`check-scope-conflict` escalates (exit 6) when the same key fails two
iterations in a row — that deadlock is a human decision, not a retry.

## Delivery conventions (enforced by run-loop.sh)

The loop never commits per iteration. PR is the delivery unit, an issue is
the error channel, and no run ends silently: every exit path writes
`.loop/report.md` (per-step cost, validator outcome, remaining findings,
incidents). Deterministic verification first (grep against raw sources,
zero tokens), then ONE model fix round.
