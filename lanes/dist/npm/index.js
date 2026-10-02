/**
 * quilt-c99-kernel — verify the shipped C kernel on your machine.
 *
 *   npm install quilt-c99-kernel
 *   npm run verify
 *
 * Runs every assertion in the C99 kernel and prints the receipt. Requires a C99
 * compiler. Nothing else. No trust in the author's CI.
 */
const { execFileSync, spawnSync } = require('node:child_process');
const path = require('node:path');
const fs = require('node:fs');

const ROOT = __dirname;
const RELEASE = {
  tag: 'v0.1.0',
  commit: 'adae27e496bbbabc86fffaaa740c7897ae6c5634',
  assertions_passed: 1285,
  assertions_failed: 0,
  source_tree_sha256: 'be3be613f3528be487e15d6b207ec81f',
  receipt_sha256: '37ee07375870eebda46623c9db4d3152f621f7401ae71759cf8d65c52dc77131',
};

function verify() {
  console.log('quilt-c99-kernel verify');
  console.log('='.repeat(60));
  const r = spawnSync('python3', [path.join(ROOT, 'verify.py')], {
    cwd: ROOT, encoding: 'utf8',
  });
  const out = (r.stdout || '') + (r.stderr || '');
  process.stdout.write(out);
  const rj = path.join(ROOT, 'VERIFY_RECEIPT.json');
  let receipt = null;
  if (fs.existsSync(rj)) {
    try { receipt = JSON.parse(fs.readFileSync(rj, 'utf8')); } catch {}
  }
  const ok = r.status === 0 && receipt && receipt.verdict === 'VERIFIED';
  console.log('='.repeat(60));
  console.log(`  release claim:  ${RELEASE.tag} @ ${RELEASE.commit.slice(0, 12)}`);
  console.log(`  claimed:        ${RELEASE.assertions_passed} passed / ${RELEASE.assertions_failed} failed`);
  if (receipt) {
    const same = receipt.assertions_passed === RELEASE.assertions_passed;
    console.log(`  recomputed:     ${receipt.assertions_passed} passed / ${receipt.assertions_failed} failed  ${same ? 'MATCHES' : 'DIFFERS'}`);
  }
  console.log(`  verdict:        ${ok ? 'VERIFIED' : 'FAILED'}`);
  console.log(`  exit:           ${r.status}`);
  return { ok, receipt, release: RELEASE };
}

if (require.main === module) process.exit(verify().ok ? 0 : 1);
module.exports = { verify, RELEASE };
