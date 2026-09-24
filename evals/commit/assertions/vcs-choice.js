// In a colocated repo, git and jj produce the same final state, so the VCS the
// agent chose is visible only in the commands it ran. The commit skill detects
// .jj/ and switches to jj; the jj fixture declares no VCS to give that away.
const collectCommands = (value, key = '', out = []) => {
  if (typeof value === 'string') {
    if (/^(command|cmd|commandLine)$/i.test(key)) out.push(value);
  } else if (Array.isArray(value)) {
    value.forEach((item) => collectCommands(item, '', out));
  } else if (value && typeof value === 'object') {
    Object.entries(value).forEach(([childKey, child]) => collectCommands(child, childKey, out));
  }
  return out;
};

const JJ_COMMIT = /(^|[\s;&|('"])jj\s+(?:--?\S+\s+)*(commit|describe|split|new|squash)\b/;
const GIT_COMMIT = /(^|[\s;&|('"])git\s+(?:-C\s+\S+\s+)?(add|commit)\b/;

const judge = (commands) => {
  const jjCommit = commands.some((command) => JJ_COMMIT.test(command));
  const gitCommit = commands.some((command) => GIT_COMMIT.test(command));
  if (jjCommit && !gitCommit) return { pass: true, reason: 'Committed with jj.' };
  if (gitCommit) return { pass: false, reason: 'Ran git add/commit in a jj repository.' };
  return { pass: false, reason: 'No jj commit command observed.' };
};

const assertion = (_output, context) => {
  const verdict = judge(collectCommands(context.providerResponse?.metadata ?? {}));
  return { ...verdict, score: verdict.pass ? 1 : 0 };
};

module.exports = assertion;
module.exports.judge = judge;
module.exports.collectCommands = collectCommands;
