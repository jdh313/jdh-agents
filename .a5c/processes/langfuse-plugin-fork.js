/**
 * @process custom/langfuse-plugin-fork
 * @description Vendor langfuse observability plugin into cc-marketplace with QoL trace metadata edits
 * @skill commits
 * @agent senior-developer
 * @agent general-purpose
 */

import { defineTask } from '@a5c-ai/babysitter-sdk';

export async function process(inputs, ctx) {
  const {
    upstreamPath = '/Users/jacob/.claude/plugins/cache/langfuse-observability/langfuse/1.0.0',
    targetPath = '/Users/jacob/Projects/cc-marketplace/plugins/langfuse',
    repoRoot = '/Users/jacob/Projects/cc-marketplace',
  } = inputs;

  // Phase 1: vendor upstream files + apply 6 edits (a-f) + write README
  const vendorResult = await ctx.task(vendorAndEditTask, {
    upstreamPath,
    targetPath,
  });

  // Phase 2: re-discover plugins -> rewrite marketplace.json
  const syncResult = await ctx.task(syncMarketplaceTask, { repoRoot });

  // Phase 3: validate schema + lint
  const validateResult = await ctx.task(validateAndLintTask, { repoRoot });

  // Phase 4: commit via commits skill (jj-aware)
  const commitResult = await ctx.task(commitTask, { repoRoot });

  // Phase 5: assemble final report for the user
  const reportResult = await ctx.task(finalReportTask, {
    vendorResult,
    syncResult,
    validateResult,
    commitResult,
    repoRoot,
    targetPath,
  });

  return {
    success: true,
    vendor: vendorResult,
    sync: syncResult,
    validate: validateResult,
    commit: commitResult,
    report: reportResult,
    metadata: {
      processId: 'custom/langfuse-plugin-fork',
      timestamp: ctx.now(),
    },
  };
}

// -----------------------------------------------------------------------------
// Phase 1: vendor + edits
// -----------------------------------------------------------------------------

export const vendorAndEditTask = defineTask('vendor-and-edit', (args, taskCtx) => ({
  kind: 'agent',
  title: 'Vendor langfuse plugin + apply edits a-f',
  description: 'Copy upstream langfuse plugin files into cc-marketplace and apply 6 trace-metadata edits',
  agent: {
    name: 'senior-developer',
    prompt: {
      role: 'senior python engineer adapting a forked Claude Code observability plugin',
      task: 'Vendor the upstream Langfuse plugin into the user cc-marketplace and apply 6 specified edits to the hook',
      context: {
        upstreamPath: args.upstreamPath,
        targetPath: args.targetPath,
        sdkConstraint: 'langfuse SDK 4.7.1 - all edits are confirmed-supported by signatures',
      },
      instructions: [
        `Create the target directory tree: ${args.targetPath}/.claude-plugin and ${args.targetPath}/hooks.`,
        `Copy ${args.upstreamPath}/.claude-plugin/plugin.json -> ${args.targetPath}/.claude-plugin/plugin.json. Keep the userConfig surface IDENTICAL (LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_BASE_URL, CC_LANGFUSE_DEBUG). Set version to "1.0.0". Set author to {"name": "Jacob Hoehler"}. Keep description; remove repository/homepage/license fields. Do NOT add a "category" field. Do NOT include explicit "hooks":"./hooks" or "skills":"./skills" paths -- rely on auto-discovery.`,
        `Copy ${args.upstreamPath}/hooks/hooks.json -> ${args.targetPath}/hooks/hooks.json unchanged.`,
        `Copy ${args.upstreamPath}/hooks/langfuse_hook.py -> ${args.targetPath}/hooks/langfuse_hook.py. Insert a single new comment line "# Forked from langfuse/Claude-Observability-Plugin v1.0.0" immediately after the existing shebang/docstring header (before "import json").`,
        `EDIT (a) - propagate_attributes() at upstream line 536-540. ADD user_id and richer tags. user_id = os.environ.get("LANGFUSE_USER_ID") or os.environ.get("USER"). tags = ["claude-code", f"cwd:{os.path.basename(payload.get('cwd') or os.getcwd())}", <mode>] where <mode> is one of "plan-mode"/"auto-mode"/"default-mode" -- derive by inspecting payload (look for keys like "permission_mode" / "mode" / "defaultMode"), fall back to "default-mode" if nothing usable. The payload is available in main(); thread cwd + mode into emit_turn() via a new small helper or extra params.`,
        `EDIT (b) - trace_name at upstream line 538/543. Replace "Claude Code - Turn {turn_num}" with a composed name: "[Turn {turn_num}] {first_60_chars_of_user_text}" -- strip newlines, ellipsize at 60 chars. If the first non-empty line begins with "/", prefix the slash command: e.g. "[/loop] [Turn 3] Check the deploy every 5 min". Update BOTH the trace_name in propagate_attributes AND the name= in _start_backdated to match.`,
        `EDIT (c) - trace metadata dict at upstream line 547-554. DROP keys "session_id" and "user_text". Keep "source", "turn_number", "transcript_path", "assistant_message_count".`,
        `EDIT (d) - tool observation at upstream line 649 (_start_backdated for "Tool: {tname}"). When tname in {"Skill", "Agent", "Task"}, pass as_type="agent" instead of as_type="tool".`,
        `EDIT (e) - tool observation kwargs at upstream line 649. Build a level kwarg: detect ERROR by (a) tr_entry.get("is_error") is True, OR (b) out_trunc/out_raw contains the substring "Error: ", OR (c) the output string starts with an HTTP 4xx/5xx code marker. If detected, pass level="ERROR" in the _start_backdated call. Otherwise omit level.`,
        `EDIT (f) - Langfuse(...) constructor at upstream line 715. Pass release= keyword. Add a NEW module-level helper _get_claude_version() that shells "claude --version" with subprocess.run, timeout=2s, captures stdout, strips whitespace, caches the result in a module-level variable, and on any failure returns None silently. Use release=os.environ.get("LANGFUSE_RELEASE") or _get_claude_version().`,
        `Write ${args.targetPath}/README.md describing this as a fork of langfuse/Claude-Observability-Plugin v1.0.0, listing the 6 trace-metadata QoL improvements (a-f) in short bullets, and noting the userConfig surface is unchanged so existing pluginConfigs work.`,
        `For each edit (a-f), return the resulting line range in the vendored copy (post-edit).`,
        `IMPORTANT: do all file work with Edit/Write tools. Do not invoke python3 -c (deny rule).`,
      ],
      outputFormat: 'JSON with files_created (array of absolute paths), edits_applied (array of {label, file, line_range, summary}), readme_path',
    },
    outputSchema: {
      type: 'object',
      required: ['files_created', 'edits_applied'],
      properties: {
        files_created: { type: 'array', items: { type: 'string' } },
        edits_applied: {
          type: 'array',
          items: {
            type: 'object',
            required: ['label', 'file', 'line_range'],
            properties: {
              label: { type: 'string' },
              file: { type: 'string' },
              line_range: { type: 'string' },
              summary: { type: 'string' },
            },
          },
        },
        readme_path: { type: 'string' },
      },
    },
  },
  io: {
    inputJsonPath: `tasks/${taskCtx.effectId}/input.json`,
    outputJsonPath: `tasks/${taskCtx.effectId}/output.json`,
  },
  labels: ['vendor', 'edit'],
}));

// -----------------------------------------------------------------------------
// Phase 2: sync marketplace
// -----------------------------------------------------------------------------

export const syncMarketplaceTask = defineTask('sync-marketplace', (args, taskCtx) => ({
  kind: 'shell',
  title: 'Sync marketplace.json',
  description: 'Run scripts/sync_marketplace.py to re-discover plugins and rewrite marketplace.json',
  shell: {
    command: `cd ${args.repoRoot} && python scripts/sync_marketplace.py`,
  },
  io: {
    outputJsonPath: `tasks/${taskCtx.effectId}/output.json`,
  },
  labels: ['shell', 'sync'],
}));

// -----------------------------------------------------------------------------
// Phase 3: validate + lint
// -----------------------------------------------------------------------------

export const validateAndLintTask = defineTask('validate-and-lint', (args, taskCtx) => ({
  kind: 'shell',
  title: 'Validate schema + lint plugins',
  description: 'Run validate_schema.py then lint_plugins.py',
  shell: {
    command: `cd ${args.repoRoot} && python scripts/validate_schema.py && python scripts/lint_plugins.py`,
  },
  io: {
    outputJsonPath: `tasks/${taskCtx.effectId}/output.json`,
  },
  labels: ['shell', 'validate'],
}));

// -----------------------------------------------------------------------------
// Phase 4: commit via commits skill (jj-aware)
// -----------------------------------------------------------------------------

export const commitTask = defineTask('commit-langfuse-plugin', (args, taskCtx) => ({
  kind: 'skill',
  title: 'Commit new langfuse plugin via commits skill',
  description: 'Use the commits skill to author a single atomic commit scoped to plugins/langfuse and marketplace.json',
  skill: {
    name: 'commits',
    context: {
      cwd: args.repoRoot,
      scope_hint: 'Stage ONLY plugins/langfuse/** and .claude-plugin/marketplace.json. Do NOT include other in-flight changes (the working tree has unrelated .a5c/runs/** entries from this run -- exclude them).',
      message_format: 'Repo convention is `type[scope]: subject (vX.Y.Z)`. Example: `feat[langfuse]: vendor langfuse observability plugin (v1.0.0)`.',
      instructions: [
        'This repo is jj-colocated (a .jj/ directory exists at the repo root). The commits skill auto-detects jj.',
        'Author a single atomic commit for the new langfuse plugin.',
        'Stage only plugins/langfuse/** and .claude-plugin/marketplace.json.',
        'Use commit format `feat[langfuse]: vendor langfuse observability plugin (v1.0.0)` (or close variant matching the existing log).',
        'Return the resulting commit hash/ID and the final commit message.',
      ],
    },
  },
  io: {
    inputJsonPath: `tasks/${taskCtx.effectId}/input.json`,
    outputJsonPath: `tasks/${taskCtx.effectId}/output.json`,
  },
  labels: ['skill', 'commit'],
}));

// -----------------------------------------------------------------------------
// Phase 5: final report
// -----------------------------------------------------------------------------

export const finalReportTask = defineTask('final-report', (args, taskCtx) => ({
  kind: 'agent',
  title: 'Compose final user-facing report',
  description: 'Synthesize files-changed list, settings.json diff for manual application, smoke test command, and edit-line summary',
  agent: {
    name: 'general-purpose',
    prompt: {
      role: 'orchestration reporter producing a concise markdown deliverable',
      task: 'Compose the final report the user will see',
      context: {
        targetPath: args.targetPath,
        repoRoot: args.repoRoot,
        vendor: args.vendorResult,
        sync: args.syncResult,
        validate: args.validateResult,
        commit: args.commitResult,
      },
      instructions: [
        'Write a concise markdown report with these sections (in order):',
        '  1. Files created/modified - list absolute paths from the vendor task output',
        '  2. Settings.json diff for the user to apply BY HAND (do not edit settings.json):',
        '     - enabledPlugins: flip "langfuse@langfuse-observability": true -> false; add "langfuse@cc-marketplace": true',
        '     - pluginConfigs: rename key "langfuse@langfuse-observability" -> "langfuse@cc-marketplace" (values unchanged)',
        '     Render as a unified-style diff block so the user can copy/apply.',
        '  3. One smoke-test command - e.g. `claude /plugin install langfuse@cc-marketplace` followed by an instruction to run any short `claude` session and inspect the next trace via `swamp model method run langfuse-local listTraces`',
        '  4. Edits a-f - one line each citing the FINAL line ranges in the new vendored file (from vendor task output)',
        '  5. Commit reference - short hash/ID + message from the commit task',
        'Use file paths in path:line format where useful. No emojis. List-first format.',
      ],
      outputFormat: 'Markdown',
    },
    outputSchema: {
      type: 'object',
      required: ['report_markdown'],
      properties: {
        report_markdown: { type: 'string' },
      },
    },
  },
  io: {
    inputJsonPath: `tasks/${taskCtx.effectId}/input.json`,
    outputJsonPath: `tasks/${taskCtx.effectId}/output.json`,
  },
  labels: ['report'],
}));
