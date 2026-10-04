import { expect, mock, test } from 'claude-code/testing'
import type { Engine } from 'claude-code/testing'
import type { On, RenderElement } from 'claude-code'

import { checksForCommit, parseFjCreate, parseFjTasks, parseFjView, remoteRepo } from '../hooks/register'

const PLUGIN = 'pr-watch'
const ORIGIN = { kind: 'composer' as const }
const SHA = 'c968e0637aa1b2c3d4e5f60718293a4b5c6d7e8f'
const GH_URL = 'https://github.com/jdh313/jdh-agents/pull/42'

// fj's own output, isolates and all, as the CLI prints it to a pipe.
const FJ_VIEW = [
  '⁨⁩⁨feat[pr-watch]: watch PR CI⁩ ⁨⁩#⁨11⁩⁨⁩',
  'By ⁨⁩⁨jacob⁩⁨⁩ — ⁨⁨⁩Open⁨⁩⁩ — ⁨⁩+⁨100⁩ ⁨⁩-⁨1⁩⁨⁩',
  '⁨From `⁨pr-watch⁩` into `⁨main⁩`⁩',
].join('\n')
const tasks = (status: string) =>
  [
    '3 tasks',
    `#26 (${SHA.slice(0, 10)}) ${status} validate 1m13s (pull_request): feat[pr-watch]: watch PR CI`,
    `#25 (${SHA.slice(0, 10)}) failure validate 21s (pull_request): feat[pr-watch]: watch PR CI`,
    '#24 (0000000000) success validate 1m9s (push): Merge pull request',
  ].join('\n')

type Answers = Record<string, string>

// Stands in for the engine beneath the plugin: the shell commands it runs
// (answered from `answers` by argv, a miss exits 1), panes, toasts, and the
// Bash calls whose output it reads.
const world = (on: On, answers: Answers, toasts: string[] = []) => {
  mock.store(on)
  const clock = mock.clock(on, { now: 1_000 })
  on('command.register', () => ({}) as never)
  on('ui.open', () => ({ value: undefined }) as never)
  on('ui.toast', ($, e) => {
    toasts.push(e.text)
    return undefined as never
  })
  on('process.run', ($, e) => {
    const stdout = answers[e.argv.join(' ')]
    return { value: { exitCode: stdout === undefined ? 1 : 0, stdout: stdout ?? '', stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }
  })
  on('tool.call', { tool: 'Bash' }, ($, e) => {
    const stdout = answers[`$ ${String(e.command)}`] ?? ''
    return { result: { stdout, stderr: '', interrupted: false }, text: stdout } as never
  })
  on('command.run', () => ({ text: '' }))
  on('ui.render', { component: 'Pane' }, ($, e) => h($.ui.resolve(e).Box, {}) as RenderElement)
  return clock
}

const bash = ($: Engine, command: string) => $.tool.call({ tool: 'Bash', command } as never)

const prs = ($: Engine, args = '') =>
  $.command.run({ command: 'prs', args, origin: ORIGIN, presentation: { isFullscreen: true, columns: 160 } })

// The pane's lines, one per row the plugin drew, identical on each surface.
const pane = async ($: Engine) => {
  const shown: string[] = []
  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({
      plugin: PLUGIN,
      surface,
      component: 'Pane',
      requestId: 'pr-watch',
      props: { title: 'Pull requests', isFocused: false, bodyColumns: 80, placement: 'dock', scroll: { offset: 0, bodyRows: 30 }, view: {} },
    } as never)
    const texts = await ui.findAll({ type: 'Text' })
    shown.push(texts.map(t => t.text).join('|'))
    await ui.unmount()
  }
  expect(shown[0]).toBe(shown[1])
  return shown[0]
}

const ghView = (state: string, checks: object[]) =>
  JSON.stringify({ title: 'Add pr-watch', state, headRefName: 'pr-watch', statusCheckRollup: checks })

test('gh pr create is tracked, and the toast fires once CI passes', async ($, on) => {
  const toasts: string[] = []
  const answers: Answers = {
    '$ gh pr create --base main --head pr-watch --fill': `${GH_URL}\n`,
    [`gh pr view ${GH_URL} --json title,state,headRefName,statusCheckRollup`]: ghView('OPEN', [
      { __typename: 'CheckRun', name: 'validate', status: 'IN_PROGRESS', conclusion: '' },
      { __typename: 'StatusContext', context: 'ci/lint', state: 'SUCCESS' },
    ]),
  }
  const clock = world(on, answers, toasts)
  await bash($, 'gh pr create --base main --head pr-watch --fill')
  expect(await pane($)).toBe('● #42| Add pr-watch|  jdh313/jdh-agents|  ● validate|  ✓ ci/lint')
  expect(toasts).toEqual([])

  answers[`gh pr view ${GH_URL} --json title,state,headRefName,statusCheckRollup`] = ghView('OPEN', [
    { __typename: 'CheckRun', name: 'validate', status: 'COMPLETED', conclusion: 'SUCCESS' },
    { __typename: 'StatusContext', context: 'ci/lint', state: 'SUCCESS' },
  ])
  await clock.advance(20_000)
  expect(await pane($)).toBe('✓ #42| Add pr-watch|  jdh313/jdh-agents|  ✓ validate|  ✓ ci/lint')
  expect(toasts).toEqual(['PR #42: CI passed'])
})

test('fj pr create is tracked from its flags, CI read from the head commit', async ($, on) => {
  const toasts: string[] = []
  const command = 'fj -H forgejo.example pr create -r jacob/jdh-agents --base main --head pr-watch --body-file b.md "feat"'
  const answers: Answers = {
    [`$ ${command}`]: 'created pull request #11: feat[pr-watch]: watch PR CI\n',
    'fj -H forgejo.example pr view jacob/jdh-agents#11': FJ_VIEW,
    'git rev-parse --verify --quiet refs/remotes/origin/pr-watch^{commit}': `${SHA}\n`,
    'fj -H forgejo.example actions tasks -r jacob/jdh-agents': tasks('running'),
  }
  const clock = world(on, answers, toasts)
  await bash($, command)
  expect(await pane($)).toBe('● #11| feat[pr-watch]: watch PR CI|  jacob/jdh-agents|  ● validate')

  answers['fj -H forgejo.example actions tasks -r jacob/jdh-agents'] = tasks('failure')
  await clock.advance(20_000)
  expect(toasts).toEqual(['PR #11: CI failed (validate)'])
  const listed = await prs($)
  expect(listed.text).toBe('✗ jacob/jdh-agents#11 feat[pr-watch]: watch PR CI\n  ✗ validate')
})

test('a merged PR toasts once, stops polling, and /prs clear drops it', async ($, on) => {
  const toasts: string[] = []
  const view = `gh pr view ${GH_URL} --json title,state,headRefName,statusCheckRollup`
  const answers: Answers = { [view]: ghView('OPEN', []) }
  const clock = world(on, answers, toasts)
  await prs($, `add ${GH_URL}`)
  answers[view] = ghView('MERGED', [])
  await clock.advance(20_000)
  expect(toasts).toEqual(['PR #42 merged'])
  delete answers[view]
  await clock.advance(10 * 60_000)
  expect(toasts).toEqual(['PR #42 merged'])
  expect((await prs($, 'clear')).text).toBe('Cleared merged and closed pull requests.')
  expect((await prs($)).text).toBe('No pull requests yet.')
})

test('other Bash commands and failed creates track nothing', async ($, on) => {
  world(on, { '$ gh pr list': `${GH_URL}\n`, '$ fj pr create "x"': 'error: no remote\n' })
  await bash($, 'gh pr list')
  await bash($, 'fj pr create "x"')
  expect((await prs($)).text).toBe('No pull requests yet.')
})

test('parsers: remotes in every spelling, fj view, tasks, and a create that inferred its repo', () => {
  expect(remoteRepo('ssh://git@forgejo.example/jacob/jdh-agents.git')).toEqual({ host: 'forgejo.example', repo: 'jacob/jdh-agents' })
  expect(remoteRepo('git@github.com:jdh313/jdh-agents.git')).toEqual({ host: 'github.com', repo: 'jdh313/jdh-agents' })
  expect(remoteRepo('https://forgejo.example/jacob/jdh-agents')).toEqual({ host: 'forgejo.example', repo: 'jacob/jdh-agents' })
  expect(parseFjView(FJ_VIEW)).toEqual({ title: 'feat[pr-watch]: watch PR CI', head: 'pr-watch', state: 'open' })
  expect(checksForCommit(parseFjTasks(tasks('success')), SHA)).toEqual([{ name: 'validate', state: 'pass' }])
  expect(parseFjCreate('fj pr create --head x "t"', 'created pull request #7: t', { host: 'h.example', repo: 'o/r' })).toEqual({
    forge: 'forgejo',
    host: 'h.example',
    repo: 'o/r',
    number: 7,
    url: 'https://h.example/o/r/pulls/7',
    title: 't',
    head: 'x',
  })
})
