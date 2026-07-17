#!/bin/bash
# run-loop.sh — the v3 standard loop orchestrator.
#
#   single DRAFT (expensive model, 1 call)
#     -> deterministic VERIFY (grep/validators FIRST, zero tokens)
#     -> ONE FIX round (cheap model, only against validator findings)
#     -> deterministic RE-VERIFY
#     -> DELIVER (.loop/report.md)
#
# No second draft, no evaluator iteration rounds: model-judges-model loops
# never converge on anything a validator couldn't have checked cheaper.
# Remaining findings after RE-VERIFY go to the report and an issue draft —
# never to another fix round.
#
# The loop NEVER commits. Commit/PR is done by the human (or an outer
# wrapper) after reading the report. Every model step is wrapped in the
# guards from guards.sh; every cap is enforced in code, not in prompts.
#
# Usage (from the repo root):
#   scripts/loop/run-loop.sh
# Configuration comes from loop.env next to this script (or the
# environment). Required: LOOP_BRANCH, LOOP_VALIDATE_CMD.
#
# Exit codes (contract in README.md):
#   0 delivered, validators green      3 budget/wall-clock cap
#   1 delivered WITH unresolved        4 fail-closed (guard cannot measure)
#     validator findings               5 transient failure after retries
#   2 model call failed hard           6 scope conflict — human decision
#     (non-limit)                      7 repeated git tamper — task failed
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/guards.sh"
# loop.env is optional if everything is already in the environment
if [[ -f "${LOOP_ENV_FILE:-$SCRIPT_DIR/loop.env}" ]]; then
  # shellcheck disable=SC1090
  source "${LOOP_ENV_FILE:-$SCRIPT_DIR/loop.env}"
fi
cd "$(git rev-parse --show-toplevel)" || exit 4

# ── Configuration (all caps enforced in code) ─────────────────
LOOP_CLAUDE_BIN="${LOOP_CLAUDE_BIN:-claude}"
LOOP_MODEL_DRAFT="${LOOP_MODEL_DRAFT:-claude-opus-4-8}"   # expensive: the single draft
LOOP_MODEL_FIX="${LOOP_MODEL_FIX:-claude-haiku-4-5-20251001}"  # cheap: the one fix round
LOOP_BUDGET_USD="${LOOP_BUDGET_USD:-25.00}"
LOOP_STEP_DRAFT_USD="${LOOP_STEP_DRAFT_USD:-18.00}"       # step caps sum to the task cap
LOOP_STEP_FIX_USD="${LOOP_STEP_FIX_USD:-7.00}"
LOOP_MAX_SECONDS="${LOOP_MAX_SECONDS:-7200}"
LOOP_RETRY_MAX="${LOOP_RETRY_MAX:-3}"
LOOP_RETRY_BACKOFF="${LOOP_RETRY_BACKOFF:-60}"
LOOP_PROMPT_DRAFT="${LOOP_PROMPT_DRAFT:-$SCRIPT_DIR/prompts/worker-draft.md}"
LOOP_PROMPT_FIX="${LOOP_PROMPT_FIX:-$SCRIPT_DIR/prompts/worker-fix.md}"
# Workers never get Bash: they cannot run git. Enforced anyway by the
# HEAD-guard — tool lists are configuration, not enforcement.
LOOP_WORKER_TOOLS="${LOOP_WORKER_TOOLS:-Read,Write,Edit,Grep,Glob,WebSearch,WebFetch}"
LOOP_DIR="${LOOP_DIR:-.loop}"
LOOP_REPORT="${LOOP_REPORT:-$LOOP_DIR/report.md}"

for req in LOOP_BRANCH LOOP_VALIDATE_CMD; do
  [[ -n "${!req:-}" ]] || { echo "FAIL-CLOSED: $req is not set" >&2; exit "$LOOP_EXIT_FAILCLOSED"; }
done
for f in "$LOOP_PROMPT_DRAFT" "$LOOP_PROMPT_FIX"; do
  [[ -f "$f" ]] || { echo "FAIL-CLOSED: prompt file '$f' missing" >&2; exit "$LOOP_EXIT_FAILCLOSED"; }
done

mkdir -p "$LOOP_DIR"
RUN_START="$(date +%s)"
RUN_HEAD="$(git rev-parse HEAD)"

# ── Report bookkeeping ────────────────────────────────────────
STEP_ROWS=""       # markdown rows: | step | cost | outcome |
REMAINING=""       # unresolved validator findings after RE-VERIFY

note_step() { STEP_ROWS+="| $1 | $2 | $3 |"$'\n'; }

write_report() {
  # write_report <status> — no run ends silently, whatever the exit path.
  local status="$1" incidents="none" head_now
  [[ -f "$LOOP_INCIDENT_LOG" ]] && incidents="$(cat "$LOOP_INCIDENT_LOG")"
  head_now="$(git rev-parse HEAD)"
  lib set "status=$status" >/dev/null
  {
    echo "# Loop report — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo
    echo "- Status: **$status**"
    echo "- Branch: $LOOP_BRANCH"
    echo "- Models: draft=$LOOP_MODEL_DRAFT, fix=$LOOP_MODEL_FIX"
    echo "- Spent: \$$(lib get spent_usd) of \$$LOOP_BUDGET_USD"
    echo "- HEAD at start: $RUN_HEAD"
    echo "- HEAD at end:   $head_now $( [[ "$head_now" == "$RUN_HEAD" ]] && echo '(unchanged — loop made no commits)' )"
    echo
    echo "## Steps"
    echo
    echo "| Step | Cost (USD) | Outcome |"
    echo "|---|---|---|"
    printf '%s' "$STEP_ROWS"
    echo
    echo "## Remaining validator findings"
    echo
    if [[ -n "$REMAINING" ]]; then
      printf '%s\n' "$REMAINING"
      echo
      echo "See $LOOP_DIR/issue-draft.md — these go to a human, never to another fix round."
    else
      echo "None — validators green."
    fi
    echo
    echo "## Incidents"
    echo
    printf '%s\n' "$incidents"
  } > "$LOOP_REPORT"
  echo "Report: $LOOP_REPORT"
}

write_issue_draft() {
  # write_issue_draft <title> <body>
  { echo "# Issue draft: $1"; echo; printf '%s\n' "$2"; } > "$LOOP_DIR/issue-draft.md"
}

# ── Model step, fully guarded ─────────────────────────────────
_claude_once() {
  # _claude_once <model> <promptText> <outFile> <stepStartEpoch>
  local rc=0
  "$LOOP_CLAUDE_BIN" -p "$2" \
    --model "$1" \
    --allowedTools "$LOOP_WORKER_TOOLS" \
    --disallowedTools "Bash" \
    --output-format json > "$3" || rc=$?
  [[ $rc -eq 0 ]] && return 0
  # A failed call still costs money — book it best-effort (val26 incident:
  # $1.40 for a 429 call that was never accounted).
  lib ingest 0 failed-call "$3" >/dev/null 2>&1 || true
  if limit_detect "$LOOP_DIR" "$4"; then
    return "$LOOP_EXIT_TRANSIENT"   # usage/rate limit: retry_transient may retry
  fi
  echo "model call failed (exit $rc), not limit-classified — not retryable" >&2
  return 2
}

run_model_step() {
  # run_model_step <role> <model> <promptText> <stepCapUsd>
  # One paid call, wrapped in: wall-clock, task budget, step budget (all
  # BEFORE the call), transient-only retry, cost ingest (fail-closed),
  # HEAD-guard with self-heal + single redo (two tampers fail the task).
  local role="$1" model="$2" prompt="$3" cap="$4"
  local before attempt rc head step_start out
  before="$(lib get spent_usd)"; before="${before:-0}"
  out="$LOOP_DIR/$role.json"
  for attempt in 1 2; do
    rc=0; wall_clock_gate "$RUN_START" "$LOOP_MAX_SECONDS" || rc=$?
    [[ $rc -ne 0 ]] && return "$rc"
    rc=0; budget_gate "$LOOP_BUDGET_USD" || rc=$?
    [[ $rc -ne 0 ]] && return "$rc"
    rc=0; step_budget_gate "$before" "$cap" || rc=$?
    [[ $rc -ne 0 ]] && return "$rc"
    rc=0; sandbox_check || rc=$?
    [[ $rc -ne 0 ]] && return "$rc"
    head="$(head_guard_snapshot)"
    step_start="$(date +%s)"
    rc=0; retry_transient "$LOOP_RETRY_MAX" "$LOOP_RETRY_BACKOFF" \
      _claude_once "$model" "$prompt" "$out" "$step_start" || rc=$?
    [[ $rc -ne 0 ]] && return "$rc"
    rc=0; lib ingest "$attempt" "$role" "$out" >/dev/null || rc=$?
    [[ $rc -ne 0 ]] && return "$LOOP_EXIT_FAILCLOSED"
    rc=0; head_guard_enforce "$head" "$role" || rc=$?
    if [[ $rc -eq 0 ]]; then
      STEP_COST="$(awk -v a="$(lib get spent_usd)" -v b="$before" 'BEGIN{printf "%.4f", a-b}')"
      return 0
    fi
    if [[ $rc -eq "$LOOP_EXIT_TAMPER" ]]; then
      if tamper_exceeded "$role"; then
        echo "GUARD head: two tampers in step '$role' — task failed." >&2
        return "$LOOP_EXIT_TAMPER"
      fi
      echo "redoing step '$role' once after tamper self-heal" >&2
      continue
    fi
    return "$rc"
  done
  return "$LOOP_EXIT_TAMPER"
}

run_validators() {
  # Deterministic, zero tokens. Sets VALIDATE_RC + VALIDATE_OUT.
  VALIDATE_RC=0
  VALIDATE_OUT="$(bash -c "$LOOP_VALIDATE_CMD" 2>&1)" || VALIDATE_RC=$?
}

scope_escalate_if_deadlocked() {
  # Same scope violation two verification passes in a row = worker and
  # validator are deadlocked. That is a human decision, never a retry.
  local keys rc=0
  keys="$(printf '%s\n' "$VALIDATE_OUT" | lib scope-violations)"
  printf '%s\n' "$keys" | lib check-scope-conflict || rc=$?
  if [[ $rc -eq 0 ]]; then
    echo "GUARD scope: repeated scope violation — escalating:" >&2
    printf '%s\n' "$keys" >&2
    write_issue_draft "Loop scope conflict on $LOOP_BRANCH" \
      "Repeated scope violation keys:"$'\n'"$keys"$'\n\n'"Validator output:"$'\n'"$VALIDATE_OUT"
    REMAINING="$VALIDATE_OUT"
    write_report scope_conflict
    exit "$LOOP_EXIT_SCOPE"
  fi
}

bail() { # bail <rc> <status> — guard-stop exit path, report always written
  write_report "$2"
  exit "$1"
}

# ── 1. INIT ───────────────────────────────────────────────────
echo "=== INIT (branch=$LOOP_BRANCH, budget=\$$LOOP_BUDGET_USD) ==="
rc=0; branch_guard "$LOOP_BRANCH" || rc=$?; [[ $rc -ne 0 ]] && exit "$rc"
rc=0; sandbox_check || rc=$?; [[ $rc -ne 0 ]] && exit "$rc"
rc=0; budget_gate "$LOOP_BUDGET_USD" || rc=$?; [[ $rc -ne 0 ]] && bail "$rc" budget_stop
lib set status=running >/dev/null

# ── 2. DRAFT — expensive model, exactly one draft ─────────────
echo "=== DRAFT ($LOOP_MODEL_DRAFT, cap \$$LOOP_STEP_DRAFT_USD) ==="
rc=0; run_model_step draft "$LOOP_MODEL_DRAFT" "$(cat "$LOOP_PROMPT_DRAFT")" "$LOOP_STEP_DRAFT_USD" || rc=$?
case $rc in
  0) note_step DRAFT "$STEP_COST" "ok" ;;
  "$LOOP_EXIT_BUDGET")  note_step DRAFT - "stopped by budget gate"; bail "$rc" budget_stop ;;
  "$LOOP_EXIT_TAMPER")  note_step DRAFT - "task failed: repeated tamper"; bail "$rc" tamper_failed ;;
  "$LOOP_EXIT_TRANSIENT") note_step DRAFT - "transient failure persisted"; lib set status=usage_interrupted >/dev/null; write_report usage_interrupted; exit "$rc" ;;
  *) note_step DRAFT - "failed (exit $rc)"; bail "$rc" draft_failed ;;
esac

# ── 3. VERIFY — deterministic, grep first, zero tokens ────────
echo "=== VERIFY (deterministic, \$0) ==="
run_validators
if [[ $VALIDATE_RC -eq 0 ]]; then
  note_step VERIFY 0 "green"
  lib reset-scope-conflict >/dev/null
else
  note_step VERIFY 0 "findings (see below)"
  printf '%s\n' "$VALIDATE_OUT"
  scope_escalate_if_deadlocked

  # ── 4. FIX — cheap model, ONE round, only against findings ──
  echo "=== FIX ($LOOP_MODEL_FIX, cap \$$LOOP_STEP_FIX_USD) ==="
  FIX_PROMPT="$(cat "$LOOP_PROMPT_FIX")"$'\n\n'"## Validator findings — fix ONLY these"$'\n\n'"$VALIDATE_OUT"
  rc=0; run_model_step fix "$LOOP_MODEL_FIX" "$FIX_PROMPT" "$LOOP_STEP_FIX_USD" || rc=$?
  case $rc in
    0) note_step FIX "$STEP_COST" "ok" ;;
    "$LOOP_EXIT_BUDGET")  note_step FIX - "stopped by budget gate"; REMAINING="$VALIDATE_OUT"; bail "$rc" budget_stop ;;
    "$LOOP_EXIT_TAMPER")  note_step FIX - "task failed: repeated tamper"; REMAINING="$VALIDATE_OUT"; bail "$rc" tamper_failed ;;
    "$LOOP_EXIT_TRANSIENT") note_step FIX - "transient failure persisted"; REMAINING="$VALIDATE_OUT"; lib set status=usage_interrupted >/dev/null; write_report usage_interrupted; exit "$rc" ;;
    *) note_step FIX - "failed (exit $rc)"; REMAINING="$VALIDATE_OUT"; bail "$rc" fix_failed ;;
  esac

  # ── 5. RE-VERIFY — deterministic again; NEVER a second fix ──
  echo "=== RE-VERIFY (deterministic, \$0) ==="
  run_validators
  if [[ $VALIDATE_RC -eq 0 ]]; then
    note_step RE-VERIFY 0 "green"
    lib reset-scope-conflict >/dev/null
  else
    note_step RE-VERIFY 0 "findings remain — handing to a human"
    printf '%s\n' "$VALIDATE_OUT"
    scope_escalate_if_deadlocked
    REMAINING="$VALIDATE_OUT"
    write_issue_draft "Loop delivered with unresolved validator findings" "$VALIDATE_OUT"
  fi
fi

# ── 6. SYMMETRY — placeholder hook ────────────────────────────
symmetry_step() {
  # TODO(MÅL 4): symmetry verification hook. Will compare the deliverable
  # against its counterpart artifacts for coverage symmetry. Deliberately a
  # no-op until MÅL 4 — do not implement here.
  echo "=== SYMMETRY (placeholder, no-op) ==="
}
symmetry_step
note_step SYMMETRY 0 "placeholder (MÅL 4)"

# ── 7. DELIVER — report; commit happens OUTSIDE the loop ──────
if [[ -n "$REMAINING" ]]; then
  write_report delivered_with_findings
  echo "Delivered WITH unresolved findings — see the report and issue draft."
  exit 1
fi
write_report delivered
echo "Delivered, validators green. Total: \$$(lib get spent_usd). Commit is yours (outside the loop)."
exit 0
