import { expect, test } from 'claude-code/testing'
import type { Engine } from 'claude-code/testing'
import type { On, RenderElement } from 'claude-code'

import { byWorkspace, workspaceIn, workspaceOfCall } from '../hooks/register'

const PLUGIN = 'workspaces'
const ORIGIN = { kind: 'composer' as const }
let spawned = 0

// Stands in for the engine beneath the plugin: command registration, agent
// spawns answered with fresh ids, panes, and the tools subagents call.
const world = (on: On) => {
  on('command.register', () => ({}) as never)
  on('agent.spawn', () => ({ model: 'sonnet', agentId: `agent-${++spawned}` }))
  on('ui.open', () => ({ value: undefined }) as never)
  on('tool.call', () => ({ result: {}, text: '' }) as never)
  on('turn.complete', ($, e) => ({ text: e.answer }))
  on('command.run', () => ({ text: '' }))
  on('ui.render', { component: 'Pane' }, ($, e) => h($.ui.resolve(e).Box, {}) as RenderElement)
}

const spawn = ($: Engine, description: string, prompt: string) =>
  $.agent.spawn({ description, prompt, subagentType: 'junior-dev' } as never)

const spaces = ($: Engine, args = '') =>
  $.command.run({ command: 'spaces', args, origin: ORIGIN, presentation: { isFullscreen: true, columns: 160 } })

// The pane's shown text, one line per Text run, identical on each surface.
const pane = async ($: Engine) => {
  const shown: string[] = []
  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({
      plugin: PLUGIN,
      surface,
      component: 'Pane',
      requestId: 'workspaces',
      props: { title: 'Workspaces', isFocused: false, bodyColumns: 60, placement: 'dock', scroll: { offset: 0, bodyRows: 20 }, view: {} },
    } as never)
    const texts = await ui.findAll({ type: 'Text' })
    shown.push(texts.map(t => t.text).join('|'))
    await ui.unmount()
  }
  expect(shown[0]).toBe(shown[1])
  return shown[0] ?? ''
}

test('a path names the last jjx workspace in it', () => {
  expect(workspaceIn('cd /p/app-spaces/auth-fix && jj st')).toBe('app-spaces/auth-fix')
  expect(workspaceIn('/a/app-spaces/one then /a/app-spaces/alpha__tests/src/x.ts')).toBe('app-spaces/alpha__tests')
  expect(workspaceIn('/p/app/src/x.ts')).toBeUndefined()
  expect(workspaceOfCall({ tool: 'Edit', file_path: '/p/app-spaces/fix-2/README.md' })).toBe('app-spaces/fix-2')
})

test('agents group by workspace, the unplaced last', () => {
  const groups = byWorkspace([
    { id: '1', description: 'scan', type: 'bulk-reader', isDone: false },
    { id: '2', description: 'b', type: 'junior-dev', workspace: 'app-spaces/zeta', isDone: false },
    { id: '3', description: 'a', type: 'junior-dev', workspace: 'app-spaces/alpha', isDone: true },
  ])
  expect(groups.map(([space]) => space)).toEqual(['app-spaces/alpha', 'app-spaces/zeta', '(no workspace)'])
})

test('a spawn whose prompt names a workspace places the agent there', async ($, on) => {
  world(on)
  await spawn($, 'fix auth', 'Work only inside /p/app-spaces/auth-fix.')
  await spawn($, 'read logs', 'Summarise the logs.')
  const text = await pane($)
  expect(text).toContain('auth-fix')
  expect(text).toContain('fix auth')
  expect(text).toContain('(no workspace)')
  expect(text.indexOf('auth-fix')).toBeLessThan(text.indexOf('(no workspace)'))
})

test('a finished agent is marked done and /spaces clear drops it', async ($, on) => {
  world(on)
  const { agentId } = await spawn($, 'fix auth', 'cd /p/app-spaces/auth-fix')
  await $.turn.complete({ answer: 'ok', durationMs: 1, isAborted: false, turnId: 't1', agentId, reason: 'answer' } as never)
  expect((await spaces($)).text).toContain('done fix auth')
  await spaces($, 'clear')
  expect((await spaces($)).text).toBe('No subagents yet.')
})

test("a subagent's own tool call moves it to the workspace the path names", async ($, on) => {
  world(on)
  const { agentId } = await spawn($, 'fix auth', 'No path here.')
  await $.tool.call({ tool: 'Read', file_path: '/p/app-spaces/auth-fix/src/x.ts', agentId } as never)
  expect((await spaces($)).text).toBe('app-spaces/auth-fix\n  runs fix auth (junior-dev)')
})
