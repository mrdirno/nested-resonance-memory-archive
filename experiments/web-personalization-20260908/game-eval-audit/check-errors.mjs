#!/usr/bin/env node
// Author: Aldrin Payopay. Verify that unknown evidence cannot become a pass.
import { mkdtemp, writeFile, rm, readFile } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const temp = await mkdtemp(join(here, '.error-controls-'));
const receiptBefore = await readFile(join(here, 'receipt.json'), 'utf8');
try {
  const absent = join(temp, 'missing.mjs');
  const unknown = join(temp, 'unknown.mjs');
  const changed = join(temp, 'changed.mjs');
  await writeFile(unknown, 'export const unrelated = true;\n');
  await writeFile(changed, 'async function fingerprintFromText(src) {\n  return {};\n}\n\nasync function main() {}\n');
  const cases = [
    ['missing_evaluator', absent, /ENOENT/],
    ['unknown_extraction', unknown, /extraction unknown/],
    ['changed_extracted_function', changed, /function changed/],
  ].map(([name, path, expected]) => {
    const result = spawnSync(process.execPath, [join(here, 'falsify.mjs'), '--evaluator', path], {
      encoding: 'utf8', timeout: 5000,
    });
    return { name, exit_code: result.status, stdout: result.stdout, stderr: result.stderr.trim(),
      passed: !result.error && result.status === 2 && expected.test(result.stderr) && /audit_error/.test(result.stderr) };
  });
  const receiptUnchanged = receiptBefore === await readFile(join(here, 'receipt.json'), 'utf8');
  const passed = cases.every(row => row.passed) && receiptUnchanged;
  await writeFile(join(here, 'negative-controls.json'), JSON.stringify({
    schema: 'game-eval-error-controls/v1', measured_at: new Date().toISOString(),
    status: passed ? 'passed' : 'failed', successful_receipt_unchanged: receiptUnchanged, cases,
  }, null, 2) + '\n');
  console.log(JSON.stringify({ passed, cases: cases.map(({ name, exit_code, passed }) => ({ name, exit_code, passed })), receiptUnchanged }, null, 2));
  process.exitCode = passed ? 0 : 1;
} finally {
  await rm(temp, { recursive: true, force: true });
}
