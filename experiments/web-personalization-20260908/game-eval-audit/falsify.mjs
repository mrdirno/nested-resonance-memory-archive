#!/usr/bin/env node
// Author: Aldrin Payopay. Local experiment; no Persona500 source is copied.
import { readFile, writeFile, realpath } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const HERE = dirname(fileURLToPath(import.meta.url));
const EXPECTED_FUNCTION_HASH = '388a72b35fa739ad7a02088c44807f0f5fa2f99c18f9e0a76433f85185b805be';
const sha256 = value => createHash('sha256').update(value).digest('hex');
const suffix = '\n// Audit control: this comment changes no game instruction.\n\n';
const fixture = 'const state = { score: 0 };\nfunction press() { state.score += 1; return state.score; }\n';

function options(args) {
  const out = { repo: '/Volumes/dual/persona500', evaluator: null, output: 'receipt.json' };
  while (args.length) {
    const key = args.shift();
    if (!['--repo', '--evaluator', '--output'].includes(key) || !args.length) throw new Error('Unknown or incomplete argument');
    out[key.slice(2)] = args.shift();
  }
  if (!/^[a-z0-9._-]+\.json$/.test(out.output)) throw new Error('Output must be a simple JSON filename in this audit folder');
  return out;
}

function git(repo, args, allowFailure = false) {
  const r = spawnSync('git', ['--no-optional-locks', '-C', repo, ...args], {
    encoding: 'utf8', timeout: 5000, maxBuffer: 8 * 1024 * 1024,
  });
  if (r.error) throw r.error;
  if (r.status !== 0 && !allowFailure) throw new Error(`Read-only git ${args[0]} failed: ${r.stderr.trim()}`);
  return { args, status: r.status, stdout: r.stdout, stderr: r.stderr.trim() };
}

async function main() {
  const opts = options(process.argv.slice(2));
  const repo = await realpath(resolve(opts.repo));
  const evaluatorPath = await realpath(resolve(opts.evaluator || resolve(repo, 'public/games/_shared/cycle_eval.mjs')));
  const source = await readFile(evaluatorPath, 'utf8');
  const matches = [...source.matchAll(/^async function fingerprintFromText\(src\) \{\n[\s\S]*?^\}\n(?=\nasync function main)/gm)];
  if (matches.length !== 1) throw new Error('Expected exactly one known fingerprintFromText function; extraction unknown');
  const extracted = matches[0][0];
  if (sha256(extracted) !== EXPECTED_FUNCTION_HASH) throw new Error('Extracted function changed; inspect and explicitly repin before running');
  if (!source.includes('const path = `games/${gameName}/game.js`;')) throw new Error('Legacy history path shape changed; audit interpretation must be reviewed');
  // The hash pin is the trust boundary. vm is only execution isolation, not a
  // security sandbox for arbitrary code. No import or module main is evaluated.
  const context = vm.createContext({ createHash }, { codeGeneration: { strings: false, wasm: false } });
  new vm.Script(extracted).runInContext(context, { timeout: 1000 });
  async function fingerprint(text) {
    context.input = text;
    const value = await new vm.Script('fingerprintFromText(input)').runInContext(context, { timeout: 1000 });
    delete context.input;
    if (!value || !/^[a-f0-9]{16}$/.test(value.fingerprint) || !Number.isInteger(value.loc)) throw new Error('Unexpected fingerprint output');
    return JSON.parse(JSON.stringify(value));
  }
  function fixtureTrace(text) {
    return new vm.Script(text + '\n[press(), press(), press()]').runInNewContext({}, { timeout: 1000 });
  }
  const before = await fingerprint(fixture);
  const after = await fingerprint(fixture + suffix);
  const traceBefore = [...fixtureTrace(fixture)];
  const traceAfter = [...fixtureTrace(fixture + suffix)];
  const tracked = git(repo, ['ls-files', '--', 'public/games/pulse-desk/game.js']).stdout.trim();
  if (tracked !== 'public/games/pulse-desk/game.js') throw new Error('Expected real tracked game missing');
  const head = git(repo, ['rev-parse', 'HEAD']).stdout.trim();
  const actual = git(repo, ['show', `${head}:${tracked}`]);
  const legacy = git(repo, ['show', `${head}:games/pulse-desk/game.js`], true);
  const actualBlob = git(repo, ['rev-parse', `${head}:${tracked}`]).stdout.trim();
  const currentText = await readFile(resolve(repo, tracked), 'utf8');
  const realBefore = await fingerprint(currentText);
  const realAfter = await fingerprint(currentText + suffix);
  const changedOnlyLoc = (a, b) => Object.keys(a).every(k => ['loc', 'fingerprint'].includes(k) || JSON.stringify(a[k]) === JSON.stringify(b[k]));
  const reproduced = before.fingerprint !== after.fingerprint
    && realBefore.fingerprint !== realAfter.fingerprint
    && JSON.stringify(traceBefore) === JSON.stringify(traceAfter)
    && changedOnlyLoc(before, after) && changedOnlyLoc(realBefore, realAfter)
    && actual.status === 0 && legacy.status !== 0;
  const receipt = {
    schema: 'game-eval-falsifier/v1', measured_at: new Date().toISOString(),
    status: reproduced ? 'falsifier_reproduced' : 'falsifier_not_reproduced',
    runtime: { node: process.version, platform: process.platform, arch: process.arch },
    evaluator: { path: evaluatorPath, source_sha256: sha256(source), function_sha256: sha256(extracted),
      extraction: 'Exact function between fingerprintFromText and main; pinned inspected bytes; no module import or main execution' },
    fixture: { before_input: fixture, appended_input: suffix, after_input: fixture + suffix,
      before_sha256: sha256(fixture), after_sha256: sha256(fixture + suffix), before, after,
      executed_press_trace_before: traceBefore, executed_press_trace_after: traceAfter },
    real_game: { repo, head, path: tracked, head_blob: actualBlob,
      head_source_sha256: sha256(actual.stdout), working_source_sha256: sha256(currentText),
      working_matches_head: currentText === actual.stdout, byte_length_before: Buffer.byteLength(currentText),
      exact_after_input: 'Working source with recorded SHA-256 plus appended_input, UTF-8; no other change',
      appended_input: suffix, after_sha256: sha256(currentText + suffix), before: realBefore, after: realAfter,
      full_source_preserved: false, source_note: 'Reopen recorded Git blob/working source locally; proprietary source is not copied to the research archive' },
    history_lookup: { valid: { args: actual.args, status: actual.status, stdout_sha256: sha256(actual.stdout) },
      legacy: { args: legacy.args, status: legacy.status, stderr: legacy.stderr },
      implication: 'The legacy priorFingerprint converts a failed root games/ lookup into no prior, which main labels NEW' },
    limits: [
      'Falsifies fingerprint difference as evidence of gameplay or product improvement; does not establish game health, usability, or enjoyment.',
      'The fixture is an explicit constructed negative control. Only its three-call trace is executed; the real game source is fingerprinted without running it.',
      'Comments are appended only in memory. The application checkout, history, and index are not mutated.',
      'Checks one inspected evaluator version and one real tracked game, with the exact source and function hashes recorded.',
      'No browser, deployment, model, external network, account, or scientific-engine validation is implied.',
    ],
  };
  await writeFile(resolve(HERE, opts.output), JSON.stringify(receipt, null, 2) + '\n');
  console.log(JSON.stringify({ status: receipt.status, receipt: resolve(HERE, opts.output),
    fixture_fingerprints: [before.fingerprint, after.fingerprint],
    real_game_fingerprints: [realBefore.fingerprint, realAfter.fingerprint],
    history_exit_codes: [actual.status, legacy.status] }, null, 2));
  process.exitCode = reproduced ? 0 : 1;
}

main().catch(error => {
  console.error(JSON.stringify({ status: 'audit_error', error: error.message }));
  process.exitCode = 2;
});
