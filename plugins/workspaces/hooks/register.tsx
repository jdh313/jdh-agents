import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Placement } from '../types'

// Which subagent works in which jjx workspace. jjx puts every workspace at
// `<repo>-spaces/<slug>`, so a path of that shape in a spawn prompt or in one
// of the subagent's own tool calls places it; the latest sighting wins.
const agents = atom({ plugin: 'workspaces', key: 'agents' } as const, [])
const PANE = 'workspaces'
const TITLE = 'Workspaces'
const SPACE = /\/([^/\s'"`]+)-spaces\/([^/\s'"`]+)/g
// Tool arguments that carry a path or a command naming one.
const PATH_FIELDS = ['file_path', 'notebook_path', 'path', 'cwd', 'command'] as const
const NONE = '(no workspace)'
const RUNNING = '●'
const DONE = '✓'

type Engine = EngineInterface

// The last `<repo>-spaces/<slug>` the text names, as that string.
export const workspaceIn = (text: string | undefined): string | undefined => {
  if (!text) return undefined
  const found = [...text.matchAll(SPACE)].at(-1)
  return found && `${found[1]}-spaces/${found[2]}`
}

export const workspaceOfCall = (call: Record<string, unknown>): string | undefined => {
  for (const field of PATH_FIELDS) {
    const value = call[field]
    const space = typeof value === 'string' ? workspaceIn(value) : undefined
    if (space) return space
  }
  return undefined
}

const slugOf = (space: string) => space.slice(space.lastIndexOf('/') + 1)
const repoOf = (space: string) => space.slice(0, space.lastIndexOf('-spaces/'))

// Groups agents by workspace, sorted, the unplaced last.
export const byWorkspace = (list: readonly Placement[]) => {
  const groups = new Map<string, Placement[]>()
  for (const agent of list) {
    const key = agent.workspace ?? NONE
    groups.set(key, [...(groups.get(key) ?? []), agent])
  }
  return [...groups].sort(([a], [b]) => (a === NONE ? 1 : b === NONE ? -1 : a.localeCompare(b)))
}

const describe = (list: readonly Placement[]) =>
  byWorkspace(list)
    .map(([space, members]) =>
      [
        space,
        ...members.map(a => `  ${a.isDone ? 'done' : 'runs'} ${a.description} (${a.type})`),
      ].join('\n'),
    )
    .join('\n')

// Applies `change` to one agent; opens the pane when it lands somewhere new.
const touch = async ($: Engine, id: string, change: (a: Placement | undefined) => Placement | undefined) => {
  let moved = false
  await update($, agents, list => {
    const before = list.find(a => a.id === id)
    const after = change(before)
    if (after === undefined) return list
    moved = after.workspace !== undefined && after.workspace !== before?.workspace
    return before ? list.map(a => (a.id === id ? after : a)) : [...list, after]
  })
  if (moved) void $.ui.open({ id: PANE, title: TITLE }).catch(() => undefined)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'spaces',
      description: 'Show which subagents work in which jj workspaces',
      argumentHint: '[clear]',
    })
    return next(e)
  })

  on('agent.spawn', async ($, e, next) => {
    const started = await next(e)
    const { agentId } = started
    if (agentId === undefined) return started
    const workspace = workspaceIn(e.cwd) ?? workspaceIn(e.prompt)
    await touch($, agentId, () => ({
      id: agentId,
      description: e.description,
      type: e.subagentType,
      workspace,
      isDone: false,
    }))
    return started
  })

  // Only a subagent's own calls place it; the main loop's carry no agentId.
  on('tool.call', async ($, e, next) => {
    if (e.agentId !== undefined) {
      const workspace = workspaceOfCall(e as unknown as Record<string, unknown>)
      const known = (await read($, agents)).some(a => a.id === e.agentId)
      // Spawned before this module loaded: the roster still knows it.
      const info = !known && workspace ? (await $.agent.list()).find(i => i.id === e.agentId) : undefined
      if (info) {
        await touch($, info.id, () => ({ id: info.id, description: info.description, type: info.type, isDone: false }))
      }
      await touch($, e.agentId, a =>
        a && (a.isDone || (workspace && workspace !== a.workspace))
          ? { ...a, isDone: false, workspace: workspace ?? a.workspace }
          : undefined,
      )
    }
    return next(e)
  })

  // A subagent's run is one turn of its loop; a message may resume it later.
  on('turn.complete', async ($, e, next) => {
    if (e.agentId !== undefined) {
      await touch($, e.agentId, a => (a && !a.isDone ? { ...a, isDone: true } : undefined))
    }
    return next(e)
  })

  on('command.run', { command: 'spaces' }, async ($, e) => {
    const verb = e.args.trim()
    if (verb === 'clear') {
      await update($, agents, list => list.filter(a => !a.isDone))
      return { text: 'Cleared finished subagents.' }
    }
    if (verb !== '') return { text: 'Usage: /spaces [clear]' }
    await $.ui.open({ id: PANE, title: TITLE })
    const list = await read($, agents)
    return { text: list.length === 0 ? 'No subagents yet.' : describe(list) }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const groups = byWorkspace(await read($, agents))
    return (
      <Box flexDirection="column">
        {groups.length === 0 && <Text dimColor>No subagents yet.</Text>}
        {groups.map(([space, members]) => (
          <Box flexDirection="column" marginBottom={1}>
            <Box>
              <Text bold>{space === NONE ? NONE : slugOf(space)}</Text>
              {space !== NONE && <Text dimColor> {repoOf(space)}</Text>}
            </Box>
            {members.map(a => (
              <Box>
                <Text dimColor={a.isDone}>
                  {'  '}
                  {a.isDone ? DONE : RUNNING} {a.description}
                </Text>
                <Box flexShrink={1}>
                  <Text dimColor wrap="truncate-end">
                    {' '}
                    {a.type}
                  </Text>
                </Box>
              </Box>
            ))}
          </Box>
        ))}
      </Box>
    )
  })
}
