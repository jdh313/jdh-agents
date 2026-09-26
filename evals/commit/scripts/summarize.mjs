#!/usr/bin/env node
// Pass^k gate: every row of every gated provider must pass. Promptfoo 0.123.1
// ships no pass^k metric, and its exit code would also fail on the baseline
// arm, whose pass rate is a comparison, not a requirement.
import { readFileSync } from 'node:fs';

const tracePath = process.argv[2];
if (!tracePath) {
  throw new Error('usage: summarize.mjs TRACE_JSON');
}

const rows = JSON.parse(readFileSync(tracePath, 'utf8')).results?.results ?? [];
const providers = {};
for (const row of rows) {
  const label = row.provider?.label || row.provider?.id || 'unknown';
  const key = `${label} | ${row.testCase?.description ?? 'unnamed case'}`;
  const entry = (providers[key] ??= {
    gated: !label.endsWith('-baseline'),
    runs: 0,
    passed: 0,
    costUsd: 0,
    maxLatencyMs: 0,
    metrics: {},
    failures: [],
  });
  entry.runs += 1;
  for (const [metric, score] of Object.entries(row.namedScores ?? {})) {
    const tally = (entry.metrics[metric] ??= { passed: 0, runs: 0 });
    tally.runs += 1;
    if (score >= 1) tally.passed += 1;
  }
  entry.costUsd += row.cost || 0;
  entry.maxLatencyMs = Math.max(entry.maxLatencyMs, row.latencyMs || 0);
  if (row.success) entry.passed += 1;
  else entry.failures.push({ fixture: row.testCase?.metadata?.fixtureId ?? null, reason: row.error || row.gradingResult?.reason || 'failed' });
}

const gated = Object.values(providers).filter((entry) => entry.gated);
const summary = {
  passed: gated.length > 0 && gated.every((entry) => entry.runs > 0 && entry.passed === entry.runs),
  providers,
};
process.stdout.write(`${JSON.stringify(summary, null, 2)}\n`);
process.exitCode = summary.passed ? 0 : 1;
