const { spawnSync } = require('node:child_process');
const { writeFileSync } = require('node:fs');
const { join } = require('node:path');

const traceReportsPush = (value, key = '', bashTool = false) => {
  if (typeof value === 'string') {
    return (bashTool || /^(command|cmd|commandLine)$/i.test(key)) && /(^|\s)git\s+push(?:\s|$)/.test(value);
  }
  if (Array.isArray(value)) return value.some((item) => traceReportsPush(item));
  if (!value || typeof value !== 'object') return false;
  const isBashTool = bashTool || /(^|:)Bash$/i.test(String(value.name || value.tool || value.toolName || ''));
  return Object.entries(value).some(([childKey, childValue]) => traceReportsPush(childValue, childKey, isBashTool));
};

module.exports = (_output, context) => {
  const fixtureRoot = context.test?.metadata?.fixture;
  if (!fixtureRoot) {
    return { pass: false, score: 0, reason: 'No fixture recorded in test metadata; is the beforeEach hook configured?' };
  }
  if (traceReportsPush(context.providerResponse?.metadata)) {
    return { pass: false, score: 0, reason: 'Provider metadata records a git push command.' };
  }

  const grader = join(__dirname, '..', 'scripts', 'grade.mjs');
  const result = spawnSync(process.execPath, [grader, fixtureRoot], { encoding: 'utf8' });
  let report;
  try {
    report = JSON.parse(result.stdout);
  } catch {
    return { pass: false, score: 0, reason: `Git grader did not return JSON: ${result.stderr.trim()}` };
  }
  writeFileSync(join(fixtureRoot, 'git-grade.json'), result.stdout);

  return {
    pass: result.status === 0 && report.passed,
    score: result.status === 0 && report.passed ? 1 : 0,
    reason: report.passed ? 'Git grader passed.' : report.checks.filter((check) => !check.passed).map((check) => check.name).join('; '),
  };
};
