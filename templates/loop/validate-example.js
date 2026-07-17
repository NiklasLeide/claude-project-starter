#!/usr/bin/env node
// validate-example.js — deterministic validator, v3-loop step VERIFY/RE-VERIFY.
//
// This is the example to copy when giving a loop its own validator, and it
// is REAL: it validates docs/STACKS.md as derived from new_project.py
// (STACK_PRESETS + STACK_TEST_COMMANDS) — the kit's pilot loop task.
//
// A validator checks ONLY binary-verifiable properties:
//   derivation — every row traces to a source entry (nothing invented)
//   coverage   — every source entry has a row (nothing missing)
//   structure  — the output parses as the promised format
//   scope      — the loop touched only its target files
// It costs zero tokens and its exit code is the loop's exit condition.
//
// Output contract (README.md §Validator output contract) — scope findings
// use these exact line formats so lib.js scope-violations can parse them:
//   - <key>: changed, but is not one of the N target entries
//   - unexpected modified tracked file: <path>
// Exit 0 = green, exit 1 = findings (printed one per line).
'use strict';
const { execSync } = require('child_process');
const fs = require('fs');

const SOURCE = process.env.LOOP_VALIDATE_SOURCE || 'new_project.py';
const TARGET = process.env.LOOP_VALIDATE_TARGET || 'docs/STACKS.md';

const findings = [];

// ── Parse the source of truth ─────────────────────────────────
const py = fs.readFileSync(SOURCE, 'utf8');
function pyBlock(name) {
  const m = py.match(new RegExp(`${name}\\s*=\\s*\\{([\\s\\S]*?)\\n\\}`));
  if (!m) { console.error(`FAIL-CLOSED: cannot find ${name} in ${SOURCE}`); process.exit(4); }
  return m[1];
}
const presets = {}; // key -> {label, stack}
for (const m of pyBlock('STACK_PRESETS').matchAll(
  /"(\d+)":\s*\("([^"]+)",\s*(?:"([^"]*)"|None)\)/g)) {
  presets[m[1]] = { label: m[2], stack: m[3] ?? null };
}
const testCmds = {}; // key -> cmd|null
for (const m of pyBlock('STACK_TEST_COMMANDS').matchAll(
  /"(\d+)":\s*(?:"([^"]*)"|None)/g)) {
  testCmds[m[1]] = m[2] ?? null;
}
if (Object.keys(presets).length === 0) { console.error('FAIL-CLOSED: parsed 0 presets'); process.exit(4); }

// ── Structure: the target is a markdown table with the promised columns ──
if (!fs.existsSync(TARGET)) {
  console.log(`- ${TARGET}: missing — the draft did not create it`);
  console.log(findingsFooter(1));
  process.exit(1);
}
const md = fs.readFileSync(TARGET, 'utf8');
const lines = md.split('\n');
const headerIdx = lines.findIndex((l) =>
  /^\|/.test(l) && /preset/i.test(l) && /tech stack/i.test(l) && /test command/i.test(l));
if (headerIdx < 0) {
  findings.push(`- ${TARGET}: no markdown table with columns Preset / Tech stack / Test command`);
} else if (!/^\|[\s:|-]+\|$/.test((lines[headerIdx + 1] || '').trim())) {
  findings.push(`- ${TARGET}: table header not followed by a |---| separator row`);
}

// ── Rows: derivation + coverage against the source ────────────
const rows = {}; // key -> [label, stack, testCmd]
if (headerIdx >= 0) {
  for (const l of lines.slice(headerIdx + 2)) {
    if (!/^\|/.test(l.trim())) break; // table ended
    const cells = l.split('|').slice(1, -1).map((c) => c.trim());
    if (cells.length < 4) { findings.push(`- ${TARGET}: row "${l.trim()}" has fewer than 4 columns`); continue; }
    const [key, label, stack, cmd] = cells;
    if (!presets[key]) {
      // invented row = outside the derived target set (scope line format)
      findings.push(`- ${key} ${label}: changed, but is not one of the ${Object.keys(presets).length} target entries`);
      continue;
    }
    if (rows[key]) findings.push(`- ${TARGET}: preset ${key} appears more than once`);
    rows[key] = [label, stack, cmd];
  }
}
for (const [key, p] of Object.entries(presets)) {
  const row = rows[key];
  if (!row) { findings.push(`- ${TARGET}: preset ${key} (${p.label}) missing from the table`); continue; }
  const [label, stack, cmd] = row;
  if (label !== p.label) findings.push(`- ${TARGET}: preset ${key} label "${label}" != source "${p.label}"`);
  const wantStack = p.stack ?? '—';
  if (stack !== wantStack) findings.push(`- ${TARGET}: preset ${key} tech stack "${stack}" != source "${wantStack}"`);
  const want = testCmds[key] ?? '—';
  if (cmd !== want) findings.push(`- ${TARGET}: preset ${key} test command "${cmd}" != source "${want}"`);
}

// ── Scope: the loop may only have touched TARGET ──────────────
const dirty = execSync('git diff --name-only HEAD', { encoding: 'utf8' })
  .split('\n').map((s) => s.trim()).filter(Boolean);
for (const f of dirty) {
  if (f !== TARGET) findings.push(`- unexpected modified tracked file: ${f}`);
}

function findingsFooter(n) { return `${n} finding(s).`; }
if (findings.length) {
  for (const f of findings) console.log(f);
  console.log(findingsFooter(findings.length));
  process.exit(1);
}
console.log(`OK: ${TARGET} derived from ${SOURCE} — ${Object.keys(presets).length} presets covered, scope clean.`);
