import { expect, mock, test } from 'claude-code/testing'
import type { Engine } from 'claude-code/testing'
import type { On, RenderElement } from 'claude-code'

const PLUGIN = 'linear'
const ISSUE = { id: 'JUN-468', uuid: '8a6335aa', title: 'Phone-width pass on the SPA (gated: desktop usable)' }

// Stands in for the engine beneath the plugin: command registration, the
// store, the Linear MCP server, and an empty band when the plugin yields.
const world = (on: On, store: Record<string, unknown> = {}) => {
  mock.store(on, store)
  on('command.register', () => ({}) as never)
  on('tool.call', { tool: 'mcp__linear-server__get_issue' }, ($, e) => ({ result: ISSUE, text: JSON.stringify({ ...ISSUE, id: e.id }) }))
  on('prompt.submit', ($, e) => ({ text: e.text }))
  on('prompt.compose', () => ({ sections: [{ id: 'intro', text: 'base', scope: 'shared' as const }] }))
  on('command.run', () => ({ text: '' }))
  on('ui.render', { component: 'AbovePrompt' }, ($, e) => h($.ui.resolve(e).Box, {}) as RenderElement)
}

const COMPOSE = {
  model: 'claude-opus-5-5',
  promptModel: 'claude-opus-5-5',
  surfaces: ['terminal' as const],
  tools: [],
  outputStyle: null,
  traits: [],
}

const COMPOSER = { kind: 'composer' as const }

const submit = ($: Engine, text: string) => $.prompt.submit({ text, wait: false, origin: COMPOSER })

const ticket = ($: Engine, args: string) =>
  $.command.run({ command: 'ticket', args, origin: COMPOSER, presentation: { isFullscreen: false, columns: 120 } })

const getIssue = ($: Engine, id: string) =>
  $.tool.call({ tool: 'mcp__linear-server__get_issue', id })

// The band's shown text on each surface, '' when the plugin drew nothing.
const band = async ($: Engine) => {
  const shown: string[] = []
  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({
      plugin: PLUGIN,
      surface,
      component: 'AbovePrompt',
      props: { hasSurvey: false, isWorking: false, maxRows: 10, bodyColumns: 80, scroll: { offset: 0, bodyRows: 10 }, view: {} },
    })
    const texts = await ui.findAll({ type: 'Text' })
    shown.push(texts.map(t => t.text).join(''))
    await ui.unmount()
  }
  expect(shown[0]).toBe(shown[1])
  return shown[0]
}

test('a get_issue result becomes the active ticket, title dimmed beside it', async ($, on) => {
  world(on)
  await getIssue($, 'JUN-468')
  expect(await band($)).toBe('◩ JUN-468 Phone-width pass on the SPA (gated: desktop usable)')
})

test('a prompt mention of a known team key is tracked; unknown keys are not', async ($, on) => {
  world(on, { teamKeys: ['JUN'] })
  await submit($, 'Pick up JUN-12, it is UTF-8 safe')
  expect(await band($)).toBe('◩ JUN-12')
})

test('a prompt before any key is known tracks nothing, and the band stays empty', async ($, on) => {
  world(on)
  await submit($, 'Pick up JUN-12')
  expect(await band($)).toBe('')
  const listed = await ticket($, '')
  expect(listed.text).toBe('No active Linear tickets.')
})

test('both signals stack most recent first, and compose injects them', async ($, on) => {
  world(on)
  await getIssue($, 'JUN-468')
  await submit($, 'also JUN-470 please')
  expect(await band($)).toBe('◩ JUN-470 +1')
  const { sections } = await $.prompt.compose(COMPOSE)
  const mine = sections.find(s => s.id === `${PLUGIN}:active`)
  expect(mine?.scope).toBe('session')
  expect(mine?.text).toContain('- JUN-470\n- JUN-468: Phone-width pass')
})

test('/ticket drop and clear empty the set', async ($, on) => {
  world(on)
  await getIssue($, 'JUN-468')
  await submit($, 'and JUN-470')
  const dropped = await ticket($, 'drop jun-470')
  expect(dropped.text).toBe('Dropped JUN-470.')
  expect(await band($)).toMatch(/^◩ JUN-468 /)
  await ticket($, 'clear')
  expect(await band($)).toBe('')
})
