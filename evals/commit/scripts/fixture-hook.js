const { execFileSync } = require('node:child_process');
const { randomUUID } = require('node:crypto');
const { basename, join } = require('node:path');
const { writeFixturePermissionProfile } = require('./codex-profile.js');

// Promptfoo merges test.options into the provider config at call time, so a
// fresh fixture per eval step keeps every repeat and every provider off a
// repository another row already committed to.
async function beforeEach({ test }) {
  const root = process.env.COMMIT_EVAL_FIXTURES;
  if (!root) {
    throw new Error('COMMIT_EVAL_FIXTURES is unset; run the eval through scripts/run.sh.');
  }
  const fixture = join(root, randomUUID().slice(0, 8));
  const vcs = test.vars?.vcs ?? 'git';
  execFileSync(join(__dirname, 'create-fixture.sh'), [fixture, vcs], { stdio: ['ignore', 'ignore', 'inherit'] });
  const fixtureId = basename(fixture);
  const profile = process.env.COMMIT_EVAL_CODEX_PROFILE ? `${process.env.COMMIT_EVAL_CODEX_PROFILE}-${fixtureId}` : undefined;
  if (process.env.COMMIT_EVAL_CODEX_PROFILE) {
    writeFixturePermissionProfile({
      codexHome: process.env.COMMIT_EVAL_CODEX_HOME,
      fixture,
      profile,
    });
  }
  return {
    test: {
      ...test,
      options: { ...test.options, working_dir: join(fixture, 'repo'), ...(profile ? { permissions: profile } : {}) },
      // Saved results redact absolute paths; fixtureId stays readable in reports.
      metadata: { ...test.metadata, fixture, fixtureId },
    },
  };
}

module.exports = { beforeEach };
