const { execFileSync } = require('node:child_process');
const { randomUUID } = require('node:crypto');
const { basename, join } = require('node:path');

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
  return {
    test: {
      ...test,
      options: { ...test.options, working_dir: join(fixture, 'repo') },
      // Saved results redact absolute paths; fixtureId stays readable in reports.
      metadata: { ...test.metadata, fixture, fixtureId: basename(fixture) },
    },
  };
}

module.exports = { beforeEach };
