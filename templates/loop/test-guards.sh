#!/bin/bash
# test-guards.sh — guard test suite. Every guard has a test that simulates
# its failure mode in a scratch git repo and asserts the exit-code contract.
# Pattern from val26's test-loop-guards.sh / test-batch-guards.sh.
#
# Usage: bash test-guards.sh          (safe: runs entirely in mktemp dirs)
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PASS=0; FAIL=0

pass() { PASS=$((PASS+1)); echo "  PASS  $1"; }
fail() { FAIL=$((FAIL+1)); echo "  FAIL  $1"; }
check() { # check <desc> <expected_rc> <actual_rc>
  if [[ "$3" -eq "$2" ]]; then pass "$1 (rc=$3)"; else fail "$1 (expected rc=$2, got rc=$3)"; fi
}

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Scratch git repo with the guards installed
REPO="$TMP/repo"
mkdir -p "$REPO/scripts/loop"
cp "$SCRIPT_DIR/lib.js" "$SCRIPT_DIR/guards.sh" "$REPO/scripts/loop/"
cd "$REPO"
git init -q -b loop-test
git config user.email test@example.com
git config user.name "Guard Test"
echo base > base.txt
git add -A && git commit -qm "base"

export LOOP_STATE_FILE="$REPO/.loop/state.json"
export LOOP_INCIDENT_LOG="$REPO/.loop/incidents.log"
# shellcheck disable=SC1091
source "$REPO/scripts/loop/guards.sh"

echo "── 1. fail-closed on unparsable state/cost ──"
mkdir -p .loop && echo "not json{" > "$LOOP_STATE_FILE"
lib get spent_usd >/dev/null 2>&1; check "unparsable state file fails closed" 4 $?
rm -f "$LOOP_STATE_FILE"
echo "not json{" > "$TMP/resp.json"
lib ingest 1 worker "$TMP/resp.json" >/dev/null 2>&1; check "unparsable response fails closed" 4 $?
echo '{"result":"x"}' > "$TMP/resp2.json"
lib ingest 1 worker "$TMP/resp2.json" >/dev/null 2>&1; check "missing total_cost_usd fails closed" 4 $?

echo "── 2. budget gate (checked BEFORE calls) ──"
rm -f "$LOOP_STATE_FILE"
echo '{"total_cost_usd": 24.50, "modelUsage": {"m": 1}}' > "$TMP/cost.json"
lib ingest 1 worker "$TMP/cost.json" >/dev/null
budget_gate 25.00 2>/dev/null; check "under budget passes" 0 $?
budget_gate 24.00 2>/dev/null; check "over budget returns BUDGET" 3 $?
lib set spent_usd=garbage
budget_gate 25.00 2>/dev/null; check "unmeasurable spend fails closed" 4 $?

echo "── 3. per-step budget gate ──"
rm -f "$LOOP_STATE_FILE"
lib set spent_usd=10.00
step_budget_gate 4.00 7.00 2>/dev/null; check "step under its cap passes" 0 $?
step_budget_gate 2.00 7.00 2>/dev/null; check "step at/over its cap returns BUDGET" 3 $?

echo "── 4. iteration + wall-clock gates ──"
iteration_gate 8 8 2>/dev/null; check "iteration at cap passes" 0 $?
iteration_gate 9 8 2>/dev/null; check "iteration over cap returns BUDGET" 3 $?
wall_clock_gate "$(( $(date +%s) - 10 ))" 3600 2>/dev/null; check "inside wall clock passes" 0 $?
wall_clock_gate "$(( $(date +%s) - 100 ))" 50 2>/dev/null; check "wall clock exceeded returns BUDGET" 3 $?

echo "── 5. HEAD-guard: tamper self-heal, incident log, two strikes ──"
rm -f "$LOOP_STATE_FILE" "$LOOP_INCIDENT_LOG"
EXPECTED=$(head_guard_snapshot)
echo rogue > rogue.txt && git add -A && git commit -qm "rogue worker commit"
head_guard_enforce "$EXPECTED" areaX 2>/dev/null; check "tamper detected returns TAMPER" 7 $?
[[ "$(git rev-parse HEAD)" == "$EXPECTED" ]] && pass "self-heal: HEAD soft-reset to snapshot" || fail "self-heal: HEAD not restored"
[[ -f "$LOOP_INCIDENT_LOG" ]] && grep -q "TAMPER task=areaX" "$LOOP_INCIDENT_LOG" && pass "incident ALWAYS logged" || fail "incident log missing"
tamper_exceeded areaX && fail "one tamper should not exceed" || pass "one tamper: not exceeded"
git rm -q --cached rogue.txt 2>/dev/null; rm -f rogue.txt
echo rogue2 > rogue2.txt && git add -A && git commit -qm "rogue again"
head_guard_enforce "$EXPECTED" areaX 2>/dev/null
tamper_exceeded areaX && pass "two tampers: task fails (exceeded)" || fail "two tampers should exceed"
git rm -q --cached rogue2.txt 2>/dev/null; rm -f rogue2.txt
head_guard_enforce "$(head_guard_snapshot)" areaX 2>/dev/null; check "clean HEAD passes" 0 $?

echo "── 6. branch + sandbox guards ──"
branch_guard loop-test 2>/dev/null; check "correct branch passes" 0 $?
branch_guard other-branch 2>/dev/null; check "wrong branch fails closed" 4 $?
sandbox_check 2>/dev/null; check "sandbox ok passes" 0 $?
( cd "$TMP" && sandbox_check 2>/dev/null ); check "outside git repo fails closed" 4 $?

echo "── 7. mtime-scoped limit detection ──"
LOGDIR="$TMP/logs"; mkdir -p "$LOGDIR"
echo "we hit a rate limit here" > "$LOGDIR/old.log"
touch -d "2 hours ago" "$LOGDIR/old.log"
STEP_START=$(( $(date +%s) - 60 ))
limit_detect "$LOGDIR" "$STEP_START"; check "old limit file (pre-step) is IGNORED" 1 $?
echo "usage limit reached" > "$LOGDIR/fresh.log"
limit_detect "$LOGDIR" "$STEP_START"; check "fresh limit file is detected" 0 $?

echo "── 8. retry_transient: retries 5 ONLY, never semantic codes ──"
CNT="$TMP/cnt"; echo 0 > "$CNT"
flaky() { n=$(<"$CNT"); n=$((n+1)); echo "$n" > "$CNT"; [[ $n -ge 3 ]] && return 0 || return 5; }
retry_transient 5 0 flaky 2>/dev/null; check "transient retried until success" 0 $?
[[ "$(<"$CNT")" -eq 3 ]] && pass "took exactly 3 attempts" || fail "attempt count wrong: $(<"$CNT")"
for code in 3 4 6 7; do
  echo 0 > "$CNT"
  semantic() { n=$(<"$CNT"); echo $((n+1)) > "$CNT"; return "$code"; }
  retry_transient 5 0 semantic 2>/dev/null; check "semantic exit $code NOT retried (returned as-is)" "$code" $?
  [[ "$(<"$CNT")" -eq 1 ]] && pass "semantic exit $code: single attempt" || fail "semantic exit $code was retried"
done
always5() { return 5; }
retry_transient 2 0 always5 2>/dev/null; check "still transient after max attempts returns 5" 5 $?

echo "── 9. resume guard: only usage_interrupted ──"
rm -f "$LOOP_STATE_FILE"
lib set status=done
resume_guard 2>/dev/null; check "status=done refused" 4 $?
lib set status=worker_git_tamper
resume_guard 2>/dev/null; check "status=worker_git_tamper refused" 4 $?
lib set status=usage_interrupted
resume_guard 2>/dev/null; check "status=usage_interrupted allowed" 0 $?

echo "── 10. scope-conflict escalation ──"
rm -f "$LOOP_STATE_FILE"
V1="- entryA: changed, but is not one of the 5 target entries"
echo "$V1" | lib scope-violations | lib check-scope-conflict; check "first violation: no conflict" 1 $?
echo "$V1" | lib scope-violations | lib check-scope-conflict; check "same violation twice: conflict (escalate)" 0 $?
lib reset-scope-conflict
echo "$V1" | lib scope-violations | lib check-scope-conflict; check "after reset: no conflict" 1 $?

echo "── 11. detached launch survives its parent ──"
if command -v setsid >/dev/null 2>&1 || command -v schtasks.exe >/dev/null 2>&1; then
  WORKER="$TMP/worker.sh"; MARKER="$TMP/marker"; DLOG="$TMP/detached.log"
  printf '#!/bin/bash\nsleep 1\necho done > "%s"\n' "$MARKER" > "$WORKER"
  chmod +x "$WORKER"
  bash -c "source '$REPO/scripts/loop/guards.sh'; detached_launch '$WORKER' '$DLOG' loop-guard-test" >/dev/null 2>&1
  # the launching shell above has already exited; worker must still finish
  sleep 3
  [[ -f "$MARKER" ]] && pass "detached worker survived parent exit" || fail "detached worker died with parent"
else
  echo "  SKIP  no setsid/schtasks available"
fi

echo "── 12. 1M-context pin exported by guards ──"
grep -q 'export CLAUDE_CODE_DISABLE_1M_CONTEXT=1' "$REPO/scripts/loop/guards.sh" \
  && pass "guards.sh exports the 1M pin" || fail "1M pin missing in guards.sh"
[[ "${CLAUDE_CODE_DISABLE_1M_CONTEXT:-}" == "1" ]] \
  && pass "pin active after sourcing" || fail "pin not active after sourcing"

echo "── 13. commit.sh: never stages silently (repo without src/) ──"
COMMIT_SH="${COMMIT_SH:-}"
if [[ -z "$COMMIT_SH" ]]; then
  KIT_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || true)"
  [[ -n "$KIT_ROOT" && -f "$KIT_ROOT/commit.sh" ]] && COMMIT_SH="$KIT_ROOT/commit.sh"
fi
if [[ -n "$COMMIT_SH" && -f "$COMMIT_SH" ]]; then
  CREPO="$TMP/commit-repo"; CORIGIN="$TMP/commit-origin.git"
  git init -q --bare "$CORIGIN"
  mkdir -p "$CREPO/docs" && cd "$CREPO"
  git init -q -b master
  git config user.email test@example.com
  git config user.name "Guard Test"
  git remote add origin "$CORIGIN"
  echo "# log" > docs/CHANGELOG.md
  git add -A && git commit -qm init && git push -qu origin master 2>/dev/null
  cp "$COMMIT_SH" ./commit.sh && chmod +x commit.sh
  echo "change" >> docs/CHANGELOG.md          # docs-only change, NO src/ present
  OUT="$(./commit.sh "test: docs change" 2>&1)"; RC=$?
  check "commit.sh succeeds in repo without src/" 0 $RC
  echo "$OUT" | grep -qi "staged" && pass "commit.sh reports what it staged" || fail "commit.sh silent about staging"
  git log --oneline -1 | grep -q "test: docs change" && pass "docs change actually committed" || fail "docs change not committed"
  cd "$REPO"
else
  echo "  SKIP  commit.sh not found (set COMMIT_SH=/path/to/commit.sh)"
fi

echo "── 14. run-loop.sh: full v3 dry-run with stubbed claude ──"
LREPO="$TMP/loop-repo"
mkdir -p "$LREPO/scripts/loop/prompts"
cp "$SCRIPT_DIR/lib.js" "$SCRIPT_DIR/guards.sh" "$SCRIPT_DIR/run-loop.sh" "$LREPO/scripts/loop/"
cp "$SCRIPT_DIR/prompts/worker-draft.md" "$SCRIPT_DIR/prompts/worker-fix.md" "$LREPO/scripts/loop/prompts/"
cd "$LREPO"
git init -q -b loop-v3
git config user.email test@example.com
git config user.name "Guard Test"
echo base > base.txt && git add -A && git commit -qm base
HEAD0=$(git rev-parse HEAD)

# Deterministic scratch validator: target.txt must contain exactly VALID
cat > validate.js <<'VEOF'
const fs = require('fs');
let t = ''; try { t = fs.readFileSync('target.txt', 'utf8').trim(); } catch (e) {}
if (t !== 'VALID') { console.log('- target.txt: content is not VALID'); process.exit(1); }
console.log('OK');
VEOF

# Stubbed claude: draft model writes a defect, fix model corrects it. Logs
# every call. STUB_TAMPER=1 additionally commits (rogue worker). Prints the
# cost JSON the orchestrator ingests — a whole run costs $0.
cat > stub-claude <<'SEOF'
#!/bin/bash
model=""
while [[ $# -gt 0 ]]; do [[ "$1" == "--model" ]] && model="$2"; shift; done
echo "call model=$model" >> calls.log
if [[ "$model" == "draft-model" ]]; then echo WRONG > target.txt
elif [[ "$model" == "fix-model" ]]; then echo VALID > target.txt; fi
if [[ "${STUB_TAMPER:-0}" == "1" ]]; then
  git add -A >/dev/null 2>&1 && git commit -qm "stub rogue commit" >/dev/null 2>&1
fi
echo "{\"total_cost_usd\": ${STUB_COST:-0.50}, \"result\": \"ok\", \"session_id\": \"stub\", \"modelUsage\": {\"$model\": 1}}"
SEOF
chmod +x stub-claude

loop_env=(LOOP_CLAUDE_BIN="$LREPO/stub-claude" LOOP_BRANCH=loop-v3
  LOOP_VALIDATE_CMD="node validate.js"
  LOOP_MODEL_DRAFT=draft-model LOOP_MODEL_FIX=fix-model
  LOOP_STATE_FILE="$LREPO/.loop/state.json" LOOP_INCIDENT_LOG="$LREPO/.loop/incidents.log")

# 14a. Happy path: draft -> verify(fail) -> ONE fix -> re-verify(green) -> deliver
rc=0
env "${loop_env[@]}" LOOP_BUDGET_USD=25.00 LOOP_STEP_DRAFT_USD=18.00 LOOP_STEP_FIX_USD=7.00 \
  bash scripts/loop/run-loop.sh >/dev/null 2>&1 || rc=$?
check "v3 run delivers green (rc=0)" 0 $rc
[[ "$(cat calls.log)" == $'call model=draft-model\ncall model=fix-model' ]] \
  && pass "step order held: one draft call, then one fix call" \
  || fail "step order wrong: $(tr '\n' ';' < calls.log)"
[[ "$(cat target.txt 2>/dev/null)" == "VALID" ]] && pass "fix round corrected the deliverable" || fail "deliverable not corrected"
[[ -f .loop/report.md ]] && pass "report written" || fail "report missing"
grep -q '| DRAFT | 0.5000 | ok |' .loop/report.md && grep -q '| FIX | 0.5000 | ok |' .loop/report.md \
  && pass "per-step costs in report" || fail "per-step costs missing in report"
[[ "$(git rev-parse HEAD)" == "$HEAD0" ]] && pass "git log unchanged after run" || fail "loop touched git history"

# 14b. step_budget_gate stops a step: tampering draft costs more than its
# cap — the redo attempt must be blocked BEFORE the second paid call.
rm -rf .loop calls.log target.txt
rc=0
env "${loop_env[@]}" STUB_TAMPER=1 STUB_COST=6.00 \
  LOOP_BUDGET_USD=25.00 LOOP_STEP_DRAFT_USD=5.00 LOOP_STEP_FIX_USD=7.00 \
  bash scripts/loop/run-loop.sh >/dev/null 2>&1 || rc=$?
check "over-cap step stopped by step_budget_gate (rc=3)" 3 $rc
[[ "$(wc -l < calls.log)" -eq 1 ]] && pass "no second paid call after cap" || fail "redo call was paid despite cap"
[[ "$(git rev-parse HEAD)" == "$HEAD0" ]] && pass "tamper self-healed: git log unchanged" || fail "rogue commit survived"
grep -q 'budget_stop' .loop/report.md 2>/dev/null && pass "budget stop reported" || fail "budget stop not reported"
grep -q 'TAMPER' .loop/incidents.log 2>/dev/null && pass "tamper incident logged" || fail "tamper incident missing"
cd "$REPO"

echo
echo "════════════════════════════════════════"
echo " PASS: $PASS   FAIL: $FAIL"
echo "════════════════════════════════════════"
[[ $FAIL -eq 0 ]] || exit 1
