const { execFileSync } = require('node:child_process');
const { join } = require('node:path');

// The commit skill's house style (plugins/commit/skills/commit/references/detection.md).
// Co-Authored-By is deliberately unchecked: the skill honors a user-level mandate
// to add it, and Claude Code's own system prompt supplies one, so the trailer
// reflects the harness rather than the skill.
const checkMessage = (message) => {
  const [subject = '', ...rest] = message.replace(/\n+$/, '').split('\n');
  const body = rest.join('\n').trim();
  return [
    { name: 'subject has no trailing period', passed: !subject.trimEnd().endsWith('.') },
    { name: 'body is at most 5 lines', passed: body === '' || body.split('\n').length <= 5 },
  ];
};

const assertion = (_output, context) => {
  const fixtureRoot = context.test?.metadata?.fixture;
  if (!fixtureRoot) {
    return { pass: false, score: 0, reason: 'No fixture recorded in test metadata; is the beforeEach hook configured?' };
  }
  let message;
  try {
    message = execFileSync('git', ['log', '-1', '--format=%B'], { cwd: join(fixtureRoot, 'repo'), encoding: 'utf8' });
  } catch (error) {
    return { pass: false, score: 0, reason: `Could not read the commit message: ${error.message}` };
  }
  const failed = checkMessage(message).filter((check) => !check.passed).map((check) => check.name);
  return {
    pass: failed.length === 0,
    score: failed.length === 0 ? 1 : 0,
    reason: failed.length === 0 ? 'House style holds.' : failed.join('; '),
  };
};

module.exports = assertion;
module.exports.checkMessage = checkMessage;
