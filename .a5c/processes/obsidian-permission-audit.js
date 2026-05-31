/**
 * @process custom/obsidian-permission-audit
 * @description Survey + classify + recommend fixes for Obsidian access inconsistencies across cc-marketplace plugins. Pure analysis run — produces a report file, never edits plugin source.
 * @agent Explore
 * @agent general-purpose
 */

import { defineTask } from '@a5c-ai/babysitter-sdk';

export async function process(inputs, ctx) {
  const {
    repoRoot = '/Users/jacob/Projects/cc-marketplace',
    userSettingsPath = '/Users/jacob/dotfiles/claude/settings.json',
    projectSettingsPath = '/Users/jacob/Projects/cc-marketplace/.claude/settings.local.json',
    reportPath = '.docs/2026-05-31-obsidian-permission-audit.md',
  } = inputs;

  // ============================================================================
  // PHASE 1: SURVEY — fan out to four read-only agents in parallel
  // ============================================================================

  const [
    skillSurvey,
    agentSurvey,
    bodySurvey,
    settingsSurvey,
  ] = await ctx.parallel.all([
    () => ctx.task(surveySkillAllowedToolsTask, { repoRoot }),
    () => ctx.task(surveyAgentToolsTask, { repoRoot }),
    () => ctx.task(surveyBodyReferencesTask, { repoRoot }),
    () => ctx.task(surveySettingsPermissionsTask, { userSettingsPath, projectSettingsPath, repoRoot }),
  ]);

  // ============================================================================
  // BREAKPOINT 1 — survey complete, give user a chance to narrow scope
  // ============================================================================

  await ctx.breakpoint({
    question: `Survey complete. Found skill/agent/body/settings inventories. Proceed to classify + recommend across all 5 inconsistency categories, or narrow scope first?`,
    title: 'Survey complete — review or narrow scope?',
    options: ['Proceed full audit', 'Narrow scope (respond with categories to keep)'],
    expert: 'owner',
    tags: ['survey-gate'],
    context: {
      counts: {
        skills: skillSurvey?.skills?.length ?? null,
        agents: agentSurvey?.agents?.length ?? null,
        body_callsites: bodySurvey?.callsites?.length ?? null,
        settings_gaps: settingsSurvey?.gaps?.length ?? null,
      },
    },
  });

  // ============================================================================
  // PHASE 2: CLASSIFY — one agent synthesizes across the four surveys
  // ============================================================================

  const classification = await ctx.task(classifyInconsistenciesTask, {
    skillSurvey,
    agentSurvey,
    bodySurvey,
    settingsSurvey,
  });

  // ============================================================================
  // PHASE 3: RECOMMEND — prioritized action plan with effort + impact
  // ============================================================================

  const recommendations = await ctx.task(recommendActionsTask, {
    classification,
    skillSurvey,
    agentSurvey,
    bodySurvey,
    settingsSurvey,
    repoRoot,
  });

  // ============================================================================
  // BREAKPOINT 2 — review recommendations before writing the report
  // ============================================================================

  await ctx.breakpoint({
    question: `Review the prioritized action plan before I write the report? Quick wins are first; long-tail items at the bottom.`,
    title: 'Recommendations ready — write report?',
    options: ['Write the report', 'Adjust priorities first'],
    expert: 'owner',
    tags: ['recommend-gate'],
    context: {
      action_count: recommendations?.actions?.length ?? null,
      quick_wins_count: recommendations?.quickWins?.length ?? null,
    },
  });

  // ============================================================================
  // PHASE 4: WRITE REPORT — single .docs/ file with everything
  // ============================================================================

  const report = await ctx.task(writeReportTask, {
    repoRoot,
    reportPath,
    skillSurvey,
    agentSurvey,
    bodySurvey,
    settingsSurvey,
    classification,
    recommendations,
  });

  return {
    success: true,
    reportPath: report?.reportPath ?? reportPath,
    counts: {
      skills_surveyed: skillSurvey?.skills?.length ?? 0,
      agents_surveyed: agentSurvey?.agents?.length ?? 0,
      body_callsites: bodySurvey?.callsites?.length ?? 0,
      categories: classification?.categories?.length ?? 0,
      actions: recommendations?.actions?.length ?? 0,
    },
    metadata: {
      processId: 'custom/obsidian-permission-audit',
      timestamp: ctx.now(),
    },
  };
}

// =============================================================================
// PHASE 1 — SURVEY TASKS (parallel, read-only)
// =============================================================================

export const surveySkillAllowedToolsTask = defineTask('survey-skill-allowed-tools', (args, taskCtx) => ({
  kind: 'agent',
  title: 'Survey skill allowed-tools for Obsidian access',
  description: 'Read every plugins/*/skills/*/SKILL.md frontmatter and extract Obsidian-related allowed-tools entries',
  agent: {
    name: 'Explore',
    prompt: {
      role: 'read-only frontmatter surveyor',
      task: 'Enumerate every SKILL.md across plugins/*/skills/*/ and extract Obsidian-related entries from allowed-tools',
      context: { repoRoot: args.repoRoot },
      instructions: [
        `Glob for ${args.repoRoot}/plugins/*/skills/*/SKILL.md and ${args.repoRoot}/plugins/*/skills/*/SKILL.md (also handle nested if present).`,
        `For each file, parse the YAML frontmatter (between the first two --- markers). You only need the fields: name, disable-model-invocation, context, agent, allowed-tools.`,
        `From allowed-tools, capture entries matching ANY of: "obsidian", "Obsidian", "mcp__obsidian", "CodeMCP__Obsidian", "Bash(obsidian", "Bash(obsidian-cli", "Read", "Write", "Edit". The Read/Write/Edit ones are only interesting if the skill body indicates vault paths.`,
        `For each skill, also peek at the body (first ~100 lines) to detect: (a) "~/Loose Ends" raw path references, (b) obsidian-cli inline invocations, (c) "agent: <name>" delegation pattern indicating it forks to a vault agent.`,
        `Return a SHORT structured table per skill — do NOT echo entire skill bodies back. Just: plugin, skill, allowedToolsSubset, delegatesTo (or null), bodyMentionsObsidianCli (bool), bodyMentionsRawVaultRead (bool), bodyMentionsMcpObsidian (bool).`,
        `Aggregate counts: total skills, skills with obsidian access, breakdown by access pattern (mcp__obsidian-mcp__*, mcp__CodeMCP__Obsidian__*, Bash(obsidian *), Bash(obsidian-cli *), raw Read/Edit on vault).`,
        `Return ONLY the JSON object — no markdown narration.`,
      ],
      outputFormat: 'JSON with skills (array), patternCounts (object), notes (array of observations)',
    },
    outputSchema: {
      type: 'object',
      required: ['skills', 'patternCounts'],
      properties: {
        skills: {
          type: 'array',
          items: {
            type: 'object',
            required: ['plugin', 'skill'],
            properties: {
              plugin: { type: 'string' },
              skill: { type: 'string' },
              allowedToolsSubset: { type: 'array', items: { type: 'string' } },
              delegatesTo: { type: ['string', 'null'] },
              bodyMentionsObsidianCli: { type: 'boolean' },
              bodyMentionsRawVaultRead: { type: 'boolean' },
              bodyMentionsMcpObsidian: { type: 'boolean' },
            },
          },
        },
        patternCounts: { type: 'object' },
        notes: { type: 'array', items: { type: 'string' } },
      },
    },
  },
  io: {
    inputJsonPath: `tasks/${taskCtx.effectId}/input.json`,
    outputJsonPath: `tasks/${taskCtx.effectId}/output.json`,
  },
  labels: ['survey', 'skills'],
}));

export const surveyAgentToolsTask = defineTask('survey-agent-tools', (args, taskCtx) => ({
  kind: 'agent',
  title: 'Survey agent tools allowlists for Obsidian access',
  description: 'Read every plugins/*/agents/*.md frontmatter and extract tools list + delegation patterns',
  agent: {
    name: 'Explore',
    prompt: {
      role: 'read-only frontmatter surveyor',
      task: 'Enumerate every agent file across plugins/*/agents/*.md and extract Obsidian-related tools entries',
      context: { repoRoot: args.repoRoot },
      instructions: [
        `Glob for ${args.repoRoot}/plugins/*/agents/*.md.`,
        `For each file, parse the YAML frontmatter. Capture: name, model, tools (full list).`,
        `Classify the tools list: bashScope (one of "broad" if just "Bash", "narrow" if "Bash(...)" form, "none" if absent), mcpObsidianTools (subset), otherFileTools (Read/Edit/Write/Glob/Grep), notes.`,
        `Also peek at body (first ~80 lines) to detect: (a) "default to obsidian-cli" or similar tier guidance, (b) "Read ~/Loose Ends" patterns, (c) explicit tier-1 vs tier-2 docs.`,
        `Aggregate counts: total agents, agents with broad Bash, agents with narrow Bash, agents that use mcp obsidian, agents that mention obsidian-cli in body but lack it in tools allowlist (latent prompt risk).`,
        `Return ONLY the JSON object.`,
      ],
      outputFormat: 'JSON with agents (array), aggregates (object), notes (array)',
    },
    outputSchema: {
      type: 'object',
      required: ['agents', 'aggregates'],
      properties: {
        agents: {
          type: 'array',
          items: {
            type: 'object',
            required: ['plugin', 'agent', 'tools'],
            properties: {
              plugin: { type: 'string' },
              agent: { type: 'string' },
              model: { type: ['string', 'null'] },
              tools: { type: 'array', items: { type: 'string' } },
              bashScope: { type: 'string' },
              mcpObsidianTools: { type: 'array', items: { type: 'string' } },
              bodyMentionsObsidianCli: { type: 'boolean' },
              bodyMentionsRawVaultRead: { type: 'boolean' },
            },
          },
        },
        aggregates: { type: 'object' },
        notes: { type: 'array', items: { type: 'string' } },
      },
    },
  },
  io: {
    inputJsonPath: `tasks/${taskCtx.effectId}/input.json`,
    outputJsonPath: `tasks/${taskCtx.effectId}/output.json`,
  },
  labels: ['survey', 'agents'],
}));

export const surveyBodyReferencesTask = defineTask('survey-body-references', (args, taskCtx) => ({
  kind: 'agent',
  title: 'Survey raw body references to Obsidian tooling',
  description: 'Grep skill and agent bodies for inline obsidian-cli, MCP tool names, raw vault Read calls, and ${CLAUDE_PLUGIN_ROOT} reference reads',
  agent: {
    name: 'Explore',
    prompt: {
      role: 'read-only callsite surveyor',
      task: 'Find every inline reference to Obsidian tooling in skill/agent bodies (NOT frontmatter)',
      context: { repoRoot: args.repoRoot },
      instructions: [
        `Use ripgrep against ${args.repoRoot}/plugins/ — search recursively in *.md files.`,
        `Search for these patterns separately and collect file:line for each: (1) "obsidian-cli ", (2) "obsidian " followed by a subcommand, (3) "mcp__obsidian-mcp__", (4) "mcp__CodeMCP__Obsidian__", (5) "Read ~/Loose Ends", (6) "Read \\$\\{CLAUDE_PLUGIN_ROOT\\}/references", (7) "~/Loose Ends/" path appearing as a Read/Edit/Write argument hint.`,
        `For each callsite, note: file, line, pattern matched, and a 1-line snippet of context.`,
        `IMPORTANT: exclude frontmatter region (between first two ---). Only look at body content.`,
        `Aggregate: counts per pattern, plus list of files where multiple patterns coexist (indicating the file mixes access methods).`,
        `Return ONLY the JSON object.`,
      ],
      outputFormat: 'JSON with callsites (array), patternCounts (object), mixedAccessFiles (array)',
    },
    outputSchema: {
      type: 'object',
      required: ['callsites', 'patternCounts'],
      properties: {
        callsites: {
          type: 'array',
          items: {
            type: 'object',
            required: ['file', 'line', 'pattern'],
            properties: {
              file: { type: 'string' },
              line: { type: 'number' },
              pattern: { type: 'string' },
              snippet: { type: 'string' },
            },
          },
        },
        patternCounts: { type: 'object' },
        mixedAccessFiles: { type: 'array', items: { type: 'string' } },
      },
    },
  },
  io: {
    inputJsonPath: `tasks/${taskCtx.effectId}/input.json`,
    outputJsonPath: `tasks/${taskCtx.effectId}/output.json`,
  },
  labels: ['survey', 'body-references'],
}));

export const surveySettingsPermissionsTask = defineTask('survey-settings-permissions', (args, taskCtx) => ({
  kind: 'agent',
  title: 'Survey settings.json Obsidian permissions and gaps',
  description: 'Read user + project settings.json, extract Obsidian-related allow/deny/ask entries, then cross-reference against surveyed plugin patterns',
  agent: {
    name: 'general-purpose',
    prompt: {
      role: 'permission-allowlist analyst',
      task: 'Extract Obsidian-related permission entries from user and project settings, then identify which surveyed plugin patterns lack a matching allow entry (i.e., prompt risks)',
      context: {
        userSettingsPath: args.userSettingsPath,
        projectSettingsPath: args.projectSettingsPath,
        repoRoot: args.repoRoot,
      },
      instructions: [
        `Read ${args.userSettingsPath} and parse as JSON. Extract entries from .permissions.allow, .permissions.deny, .permissions.ask matching: "obsidian", "Loose Ends", "mcp__obsidian", "CodeMCP__Obsidian".`,
        `Read ${args.projectSettingsPath} (if it exists; tolerate ENOENT). Extract the same.`,
        `Also note any Read(...) entries that grant vault path access (e.g., Read(//Users/jacob/Loose Ends/**)).`,
        `Cross-reference against the patterns commonly used in plugins (which you can survey lightly via ripgrep on ${args.repoRoot}/plugins): list the tools/paths that plugins USE but settings does NOT allow at the user level. These are the prompt-causing gaps.`,
        `Also report any deny entries that may inadvertently affect Obsidian work.`,
        `Return ONLY the JSON object.`,
      ],
      outputFormat: 'JSON with userAllow (array), userDeny (array), userAsk (array), projectEntries (object), gaps (array of {pattern, used_in, why_gap}), denyConcerns (array)',
    },
    outputSchema: {
      type: 'object',
      required: ['userAllow', 'gaps'],
      properties: {
        userAllow: { type: 'array', items: { type: 'string' } },
        userDeny: { type: 'array', items: { type: 'string' } },
        userAsk: { type: 'array', items: { type: 'string' } },
        projectEntries: { type: 'object' },
        gaps: {
          type: 'array',
          items: {
            type: 'object',
            required: ['pattern', 'why_gap'],
            properties: {
              pattern: { type: 'string' },
              used_in: { type: 'array', items: { type: 'string' } },
              why_gap: { type: 'string' },
            },
          },
        },
        denyConcerns: { type: 'array', items: { type: 'string' } },
      },
    },
  },
  io: {
    inputJsonPath: `tasks/${taskCtx.effectId}/input.json`,
    outputJsonPath: `tasks/${taskCtx.effectId}/output.json`,
  },
  labels: ['survey', 'settings'],
}));

// =============================================================================
// PHASE 2 — CLASSIFY
// =============================================================================

export const classifyInconsistenciesTask = defineTask('classify-inconsistencies', (args, taskCtx) => ({
  kind: 'agent',
  title: 'Cluster survey findings into inconsistency categories',
  description: 'Take the four survey outputs and group findings into 5-7 named categories, ranked by estimated prompt-frequency impact',
  agent: {
    name: 'general-purpose',
    prompt: {
      role: 'permission ergonomics analyst',
      task: 'Synthesize the four surveys into a ranked list of inconsistency categories',
      context: {
        skillSurvey: args.skillSurvey,
        agentSurvey: args.agentSurvey,
        bodySurvey: args.bodySurvey,
        settingsSurvey: args.settingsSurvey,
      },
      instructions: [
        'Cluster findings into 5-7 categories. Suggested seeds (refine as evidence warrants): (A) multiple-MCP-servers (mcp__obsidian-mcp vs mcp__CodeMCP__Obsidian), (B) CLI binary name split (obsidian vs obsidian-cli), (C) allowed-tools granularity whiplash (wide Bash(obsidian *) vs narrow Bash(obsidian read *)), (D) agent over-broad Bash that defeats granular allowlists, (E) raw-Read against ~/Loose Ends paths not in settings allowlist, (F) skill allowed-tools listing tools used only by dispatched agents (no-op pre-approval).',
        'For each category, include: name, evidence_count (callsites/files affected), prompt_impact (low/medium/high — heuristic), examples (3-5 concrete file:line refs), why_it_prompts (1 sentence).',
        'Rank categories by prompt_impact * evidence_count.',
        'Flag any category that has zero evidence in the surveys and drop it.',
        'Return ONLY the JSON object.',
      ],
      outputFormat: 'JSON with categories (ranked array), totalIssuesFound (number), confidenceNotes (array)',
    },
    outputSchema: {
      type: 'object',
      required: ['categories'],
      properties: {
        categories: {
          type: 'array',
          items: {
            type: 'object',
            required: ['name', 'evidence_count', 'prompt_impact'],
            properties: {
              name: { type: 'string' },
              evidence_count: { type: 'number' },
              prompt_impact: { type: 'string', enum: ['low', 'medium', 'high'] },
              examples: { type: 'array', items: { type: 'string' } },
              why_it_prompts: { type: 'string' },
            },
          },
        },
        totalIssuesFound: { type: 'number' },
        confidenceNotes: { type: 'array', items: { type: 'string' } },
      },
    },
  },
  io: {
    inputJsonPath: `tasks/${taskCtx.effectId}/input.json`,
    outputJsonPath: `tasks/${taskCtx.effectId}/output.json`,
  },
  labels: ['classify'],
}));

// =============================================================================
// PHASE 3 — RECOMMEND
// =============================================================================

export const recommendActionsTask = defineTask('recommend-actions', (args, taskCtx) => ({
  kind: 'agent',
  title: 'Produce prioritized action plan with effort + impact',
  description: 'For each classified category, propose 1-N concrete actions. Each action has effort (S/M/L), impact (prompts avoided per session, qualitative), affected files, and a 1-line why.',
  agent: {
    name: 'general-purpose',
    prompt: {
      role: 'remediation planner',
      task: 'Produce a prioritized, concrete action plan',
      context: {
        classification: args.classification,
        skillSurvey: args.skillSurvey,
        agentSurvey: args.agentSurvey,
        bodySurvey: args.bodySurvey,
        settingsSurvey: args.settingsSurvey,
        repoRoot: args.repoRoot,
      },
      instructions: [
        'For each category from the classification, propose 1-3 concrete actions. Each action MUST include: title, target_files (list of repo-relative paths), exact_change_description (one paragraph max), effort (S=<30min, M=30-90min, L=>90min), impact (qualitative: low/medium/high prompts avoided), risk (none/low/medium/high), prerequisites (other actions that must run first), why (1 sentence linking to the inconsistency).',
        'Rank actions globally by impact desc then effort asc. Mark the top 3-5 as "Quick Wins" (S effort, medium-or-high impact).',
        'Include a separate quickWins array (subset of actions) for surfacing in the report.',
        'Where settings.json changes are recommended, give the literal JSON snippet that should be added to .permissions.allow.',
        'Where plugin frontmatter changes are recommended, give the exact before/after lines.',
        'Do NOT recommend changes outside the cc-marketplace repo and the user settings.json. No vault content changes.',
        'Return ONLY the JSON object.',
      ],
      outputFormat: 'JSON with actions (ranked array), quickWins (array, subset of actions), longTail (array, optional, subset for lower-priority items), summary (string, 2-3 sentences)',
    },
    outputSchema: {
      type: 'object',
      required: ['actions', 'quickWins'],
      properties: {
        actions: {
          type: 'array',
          items: {
            type: 'object',
            required: ['title', 'effort', 'impact'],
            properties: {
              title: { type: 'string' },
              target_files: { type: 'array', items: { type: 'string' } },
              exact_change_description: { type: 'string' },
              effort: { type: 'string', enum: ['S', 'M', 'L'] },
              impact: { type: 'string', enum: ['low', 'medium', 'high'] },
              risk: { type: 'string', enum: ['none', 'low', 'medium', 'high'] },
              prerequisites: { type: 'array', items: { type: 'string' } },
              why: { type: 'string' },
            },
          },
        },
        quickWins: { type: 'array', items: { type: 'object' } },
        longTail: { type: 'array', items: { type: 'object' } },
        summary: { type: 'string' },
      },
    },
  },
  io: {
    inputJsonPath: `tasks/${taskCtx.effectId}/input.json`,
    outputJsonPath: `tasks/${taskCtx.effectId}/output.json`,
  },
  labels: ['recommend'],
}));

// =============================================================================
// PHASE 4 — WRITE REPORT
// =============================================================================

export const writeReportTask = defineTask('write-report', (args, taskCtx) => ({
  kind: 'agent',
  title: 'Write final audit report to .docs/',
  description: 'Produce a single Markdown report at .docs/<date>-obsidian-permission-audit.md combining survey, classification, recommendations, and quick wins.',
  agent: {
    name: 'general-purpose',
    prompt: {
      role: 'technical writer',
      task: 'Write a single audit report file using the Write tool. No commit; no plugin source edits.',
      context: {
        repoRoot: args.repoRoot,
        reportPath: args.reportPath,
        skillSurvey: args.skillSurvey,
        agentSurvey: args.agentSurvey,
        bodySurvey: args.bodySurvey,
        settingsSurvey: args.settingsSurvey,
        classification: args.classification,
        recommendations: args.recommendations,
      },
      instructions: [
        `Ensure ${args.repoRoot}/.docs/ exists (mkdir -p via Bash if needed).`,
        `Write the report file at ${args.repoRoot}/${args.reportPath}.`,
        `Use this top-level structure: (1) TL;DR — 3-5 bullets, (2) Quick wins — top 3-5 actions with effort/impact, (3) Findings by category — each category with examples and impact estimate, (4) Full action plan — table of every action sorted by impact, (5) Raw survey appendix — counts only (not full tables; keep the file scannable).`,
        `For each action in the action-plan table, include columns: Title, Category, Effort, Impact, Risk, Target files.`,
        `Use file:line references (e.g. plugins/coach/skills/today/SKILL.md:8) for all citations.`,
        `No emojis. ASCII-only. Lists over prose.`,
        `Do NOT edit any plugin source files. Do NOT touch marketplace.json. The ONLY file write is the report.`,
        `Return JSON with reportPath (absolute) and byteCount.`,
      ],
      outputFormat: 'JSON with reportPath (string), byteCount (number)',
    },
    outputSchema: {
      type: 'object',
      required: ['reportPath'],
      properties: {
        reportPath: { type: 'string' },
        byteCount: { type: 'number' },
      },
    },
  },
  io: {
    inputJsonPath: `tasks/${taskCtx.effectId}/input.json`,
    outputJsonPath: `tasks/${taskCtx.effectId}/output.json`,
  },
  labels: ['report', 'write'],
}));
