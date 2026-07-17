#!/usr/bin/env node
// lib.js — loop state + cost helper. All float arithmetic lives here (bash
// cannot do floats). Exit 4 = fail-closed: a guardrail that cannot measure
// must stop the loop, never let it continue with spent=0.
//
// Generalized from val26's scripts/loop-lib.js (proven in production July 2026).
// State file defaults to .loop/state.json; override with LOOP_STATE_FILE so
// sister loops can keep separate state without colliding.
'use strict';
const fs = require('fs');
const path = require('path');

const STATE_FILE = process.env.LOOP_STATE_FILE || '.loop/state.json';
const FAIL_CLOSED = 4;

function defaultState() {
  return {
    next_iteration: 1,
    spent_usd: '0',
    status: 'new',
    worker_session_id: '',
    last_verdict: '',
    model_usage: [],
    last_scope_violation_keys: [],
  };
}

function loadState() {
  if (!fs.existsSync(STATE_FILE)) return defaultState();
  try {
    return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
  } catch (e) {
    console.error(`FAIL-CLOSED: ${STATE_FILE} exists but cannot be parsed: ${e.message}`);
    process.exit(FAIL_CLOSED);
  }
}

function saveState(s) {
  s.updated = new Date().toISOString();
  fs.mkdirSync(path.dirname(path.resolve(STATE_FILE)), { recursive: true });
  fs.writeFileSync(STATE_FILE, JSON.stringify(s, null, 2) + '\n');
}

function readResponse(file) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (e) {
    console.error(`FAIL-CLOSED: cannot parse claude response ${file}: ${e.message}`);
    process.exit(FAIL_CLOSED);
  }
}

function asFinite(label, raw) {
  const n = Number(raw);
  if (!isFinite(n)) {
    console.error(`FAIL-CLOSED: ${label} "${raw}" is not parsable`);
    process.exit(FAIL_CLOSED);
  }
  return n;
}

const [cmd, ...args] = process.argv.slice(2);

switch (cmd) {
  case 'ingest': {
    // ingest <iteration> <role> <responseFile>
    // Adds total_cost_usd to spent, logs modelUsage. Prints new spent.
    const [iteration, role, file] = args;
    const resp = readResponse(file);
    const cost = resp.total_cost_usd;
    if (typeof cost !== 'number' || !isFinite(cost)) {
      console.error(`FAIL-CLOSED: total_cost_usd missing or not a number in ${file}`);
      process.exit(FAIL_CLOSED);
    }
    const state = loadState();
    const prev = asFinite('stored spent_usd', state.spent_usd);
    state.spent_usd = (prev + cost).toFixed(6);
    state.model_usage.push({
      iteration: Number(iteration),
      role,
      models: Object.keys(resp.modelUsage || {}),
      cost_usd: cost,
      is_error: resp.is_error === true,
    });
    saveState(state);
    console.log(state.spent_usd);
    break;
  }

  case 'under-budget': {
    // under-budget <budgetUsd> — exit 0 under, 1 at/over, 4 unparsable
    const state = loadState();
    const spent = asFinite('spent_usd', state.spent_usd);
    const budget = asFinite('budget', args[0]);
    process.exit(spent < budget ? 0 : 1);
  }

  case 'step-under-budget': {
    // step-under-budget <spentBeforeStepUsd> <stepCapUsd>
    // Per-step budget (val26 LOOP_BACKLOG finding: step caps must be
    // coordinated with the task cap). Exit 0 under, 1 at/over, 4 unparsable.
    const state = loadState();
    const spent = asFinite('spent_usd', state.spent_usd);
    const before = asFinite('spentBeforeStep', args[0]);
    const cap = asFinite('stepCap', args[1]);
    process.exit(spent - before < cap ? 0 : 1);
  }

  case 'get': {
    const state = loadState();
    const v = state[args[0]];
    console.log(v === undefined || v === null ? '' : String(v));
    break;
  }

  case 'set': {
    // set key=value [key=value ...]
    const state = loadState();
    for (const kv of args) {
      const i = kv.indexOf('=');
      if (i < 1) { console.error(`bad set arg: ${kv}`); process.exit(1); }
      const key = kv.slice(0, i);
      const val = kv.slice(i + 1);
      state[key] = /^\d+$/.test(val) ? Number(val) : val;
    }
    saveState(state);
    break;
  }

  case 'result': {
    const resp = readResponse(args[0]);
    console.log(resp.result ?? resp.response ?? '');
    break;
  }

  case 'session': {
    const resp = readResponse(args[0]);
    console.log(resp.session_id ?? '');
    break;
  }

  case 'scope-violations': {
    // Reads validator failure text from stdin, prints the unique
    // scope-violation keys it contains (one per line, empty if none).
    // Validators must emit these line formats (see README.md, "Validator
    // output contract"); override the regexes via env for other formats.
    const text = fs.readFileSync(0, 'utf8');
    const targetRe = new RegExp(process.env.LOOP_SCOPE_TARGET_RE
      || '^- (.+): changed, but is not one of the \\d+ target entries$');
    const dirtyRe = new RegExp(process.env.LOOP_SCOPE_DIRTY_RE
      || '^- unexpected modified tracked file: (.+)$');
    const keys = new Set();
    for (const line of text.split('\n')) {
      const t = targetRe.exec(line); if (t) keys.add(t[1]);
      const d = dirtyRe.exec(line); if (d) keys.add(d[1]);
    }
    for (const k of keys) console.log(k);
    break;
  }

  case 'check-scope-conflict': {
    // Reads this iteration's scope-violation keys from stdin (one per line,
    // possibly empty). Exit 0 = same key was also flagged last iteration
    // (worker and validator are deadlocked on it) -> caller must escalate
    // (semantic exit 6). Exit 1 = no conflict. Always records the current
    // keys for the next comparison.
    const text = fs.readFileSync(0, 'utf8');
    const current = text.split('\n').map((s) => s.trim()).filter(Boolean);
    const state = loadState();
    const prev = Array.isArray(state.last_scope_violation_keys) ? state.last_scope_violation_keys : [];
    const conflict = current.some((k) => prev.includes(k));
    state.last_scope_violation_keys = current;
    saveState(state);
    process.exit(conflict ? 0 : 1);
  }

  case 'reset-scope-conflict': {
    // Called after a validation pass to break the "consecutive" streak that
    // check-scope-conflict tracks.
    const state = loadState();
    state.last_scope_violation_keys = [];
    saveState(state);
    break;
  }

  default:
    console.error(`unknown command: ${cmd}`);
    process.exit(1);
}
