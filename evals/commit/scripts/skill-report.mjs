#!/usr/bin/env node
import { existsSync, readFileSync } from 'node:fs';

const [provider, tracePath, pluginListPath] = process.argv.slice(2);
if (!provider || !tracePath) {
  throw new Error('usage: skill-report.mjs PROVIDER TRACE_JSON [CODEX_PLUGIN_LIST_JSON]');
}

let trace = null;
if (existsSync(tracePath)) {
  try {
    trace = JSON.parse(readFileSync(tracePath, 'utf8'));
  } catch {
    trace = null;
  }
}
const pluginList = pluginListPath && existsSync(pluginListPath) ? readFileSync(pluginListPath, 'utf8') : '';

const analyze = (root) => {
  const skillCallValues = [];
  const skillItemValues = [];
  const codexInstalledSkillReads = [];
  const claudeSkillFileReads = [];
  let traceExposesSkillEvidence = false;
  const walk = (value) => {
    if (Array.isArray(value)) value.forEach(walk);
    else if (value && typeof value === 'object') {
      if (
        value.type === 'commandExecution'
        && value.status === 'completed'
        && value.exitCode === 0
        && typeof value.command === 'string'
      ) {
        const path = value.command.match(/(?:^|[\s'"])(\/[^\s'"]*\/plugins\/cache\/jdh-agents\/commit\/[^/\s'"]+\/skills\/commit\/SKILL\.md)/)?.[1];
        if (path) codexInstalledSkillReads.push({ command: value.command, path });
      }
      // A slash-invoked skill expands into the prompt and never appears in
      // skillCalls; its Read of the plugin's own skill files is the evidence.
      if (value.name === 'Read' && typeof value.input?.file_path === 'string'
        && /\/plugins\/commit\/skills\/commit\//.test(value.input.file_path)) {
        claudeSkillFileReads.push(value.input.file_path);
      }
      for (const [key, child] of Object.entries(value)) {
        if (/^(skillCalls|attemptedSkillCalls)$/i.test(key) && Array.isArray(child)) {
          traceExposesSkillEvidence = true;
          skillCallValues.push(...child);
        }
        if (key === 'items' && Array.isArray(child)) {
          for (const item of child) {
            if (item && typeof item === 'object' && /skill/i.test(String(item.type || item.kind || ''))) {
              traceExposesSkillEvidence = true;
              skillItemValues.push(item);
            }
          }
        }
        walk(child);
      }
    }
  };
  walk(root);
  const named = (item) => typeof item === 'string' ? item : item?.name || item?.skill || item?.skillName || '';
  const namedSkillObserved = [...skillCallValues, ...skillItemValues].some((item) => named(item) === 'commit:commit');
  const uniqueCodexInstalledSkillReads = [...new Map(codexInstalledSkillReads.map((item) => [item.command, item])).values()];
  const uniqueClaudeSkillFileReads = [...new Set(claudeSkillFileReads)];
  const activationObserved = namedSkillObserved
    || (provider === 'codex' && uniqueCodexInstalledSkillReads.length > 0)
    || (provider === 'claude' && uniqueClaudeSkillFileReads.length > 0);
  const result = {
    activation: activationObserved ? 'observed' : traceExposesSkillEvidence ? 'not_observed' : 'unknown',
    evidence: namedSkillObserved
      ? 'Structured Promptfoo skill evidence names commit:commit.'
      : provider === 'codex' && uniqueCodexInstalledSkillReads.length > 0
        ? 'Successful structured commandExecution read the installed compiled commit SKILL.md.'
      : provider === 'claude' && uniqueClaudeSkillFileReads.length > 0
        ? 'A Read tool call opened a file inside the compiled commit skill.'
      : traceExposesSkillEvidence
        ? 'Structured Promptfoo skill evidence exists but does not name commit:commit.'
        : 'The saved trace exposes no structured skill event; activation cannot be determined.',
  };
  if (uniqueCodexInstalledSkillReads.length > 0) result.activationEvidence = uniqueCodexInstalledSkillReads;
  else if (provider === 'claude' && uniqueClaudeSkillFileReads.length > 0) result.activationEvidence = uniqueClaudeSkillFileReads;
  return result;
};

// One entry per eval row: each repeat and each provider arm ran in its own fixture.
const rows = (trace?.results?.results ?? []).map((row) => ({
  label: row.provider?.label || row.provider?.id || null,
  case: row.testCase?.description ?? null,
  fixture: row.testCase?.metadata?.fixtureId ?? null,
  success: Boolean(row.success),
  ...analyze(row),
}));
const count = (activation) => rows.filter((row) => row.activation === activation).length;
const report = {
  provider,
  trace: trace ? tracePath : null,
  compiledPluginSkill: 'commit:commit',
  activation: { observed: count('observed'), not_observed: count('not_observed'), unknown: count('unknown'), rows: rows.length },
  rows,
};

if (provider === 'claude') {
  report.pluginLoadBoundary = 'Promptfoo local-plugin loading against marketplaces/claude/plugins/commit';
  report.installationLifecycle = 'not_reproduced';
  report.installationGap = 'The Claude Agent SDK supports local plugin directories, not Claude marketplace installation.';
} else if (provider === 'codex') {
  report.pluginLoadBoundary = 'Codex marketplace registration and plugin installation in isolated CODEX_HOME';
  report.installationLifecycle = pluginList.includes('commit') ? 'verified_before_provider' : 'not_verified';
  report.pluginList = pluginListPath || null;
}

process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
