import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Ticket } from '../types'

// Active tickets for this session, most recent first. $.state survives hot
// reloads; team keys seen in issue results persist across sessions in $.store.
const tickets = atom({ plugin: 'linear', key: 'tickets' } as const, [])
const TEAM_KEYS = 'teamKeys'
const ISSUE_TOOLS = ['mcp__linear-server__get_issue', 'mcp__linear-server__save_issue']
const IDENTIFIER = /^[A-Z][A-Z0-9]{1,9}-\d+$/
const MENTION = /\b[A-Z]{2,10}-\d+\b/g
// Nerd Font md-ticket (U+F0516); Linear's own logo is in no terminal font.
const GLYPH = '\u{F0516}'

type Engine = EngineInterface

const teamKeyOf = (id: string) => id.slice(0, id.lastIndexOf('-'))

// Front-loads `seen`, keeping a known title when the new sighting has none.
const promote = (list: readonly Ticket[], seen: readonly Ticket[]) => {
  const known = new Map(list.map(t => [t.id, t]))
  const fresh = seen.map(t => ({ ...known.get(t.id), ...t, title: t.title ?? known.get(t.id)?.title }))
  const ids = new Set(fresh.map(t => t.id))
  return [...fresh, ...list.filter(t => !ids.has(t.id))]
}

const remember = async ($: Engine, seen: readonly Ticket[]) => {
  if (seen.length === 0) return
  await update($, tickets, list => promote(list, seen))
}

const readTeamKeys = async ($: Engine) => {
  const stored = await $.store.get(TEAM_KEYS)
  return new Set(Array.isArray(stored) ? stored.filter(k => typeof k === 'string') : [])
}

const learnTeamKey = async ($: Engine, id: string) => {
  const keys = await readTeamKeys($)
  if (keys.has(teamKeyOf(id))) return
  await $.store.set(TEAM_KEYS, [...keys, teamKeyOf(id)])
}

// get_issue and save_issue answer with the issue as JSON text: `id` is the
// identifier (JUN-468), `uuid` the database id.
export const parseIssue = (text: string | undefined): Ticket | undefined => {
  if (!text) return undefined
  try {
    const issue: unknown = JSON.parse(text)
    if (typeof issue !== 'object' || issue === null) return undefined
    const { id, identifier, title } = issue as Record<string, unknown>
    const key = [identifier, id].find(v => typeof v === 'string' && IDENTIFIER.test(v))
    if (typeof key !== 'string') return undefined
    return typeof title === 'string' ? { id: key, title } : { id: key }
  } catch {
    return undefined
  }
}

const describe = (list: readonly Ticket[]) =>
  list.map(t => (t.title ? `- ${t.id}: ${t.title}` : `- ${t.id}`)).join('\n')

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'ticket',
      description: 'Show, clear, or drop the Linear tickets this session tracks',
      argumentHint: '[clear | drop <ID>]',
    })
    return next(e)
  })

  on('tool.call', async ($, e, next) => {
    const ran = await next(e)
    if (!ISSUE_TOOLS.includes(e.tool) || ran.deny !== undefined || ran.isError) return ran
    const issue = parseIssue(ran.text)
    if (issue) {
      await learnTeamKey($, issue.id)
      await remember($, [issue])
    }
    return ran
  })

  on('prompt.submit', async ($, e, next) => {
    const keys = await readTeamKeys($)
    const ids = [...new Set(e.text.match(MENTION) ?? [])].filter(id => keys.has(teamKeyOf(id)))
    await remember($, ids.map(id => ({ id })))
    return next(e)
  })

  on('prompt.compose', async ($, e, next) => {
    const composed = await next(e)
    const list = await read($, tickets)
    if (list.length === 0) return composed
    const text = [
      '# Active Linear tickets',
      'This session is working on these Linear tickets, most recent first. Keep them in mind across compaction, and name them in commits and PRs where the repo convention asks for it.',
      describe(list),
    ].join('\n\n')
    return {
      sections: [...composed.sections, { id: 'linear:active', text, scope: 'session' as const }],
    }
  })

  // The band above the prompt: the newest ticket, its title dimmed and cut to
  // the row, and how many more are active. Reading the atom while drawing
  // redraws the band whenever the set changes.
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const [first, ...rest] = await read($, tickets)
    if (e.props.hasSurvey || first === undefined) return next(e)
    const { Box, Text } = $.ui.resolve(e)
    // marginTop: a blank row between the conversation and the band.
    return (
      <Box marginTop={1}>
        <Text bold>
          {GLYPH} {first.id}
        </Text>
        {first.title && (
          <Box flexShrink={1}>
            <Text dimColor wrap="truncate-end">
              {' '}
              {first.title}
            </Text>
          </Box>
        )}
        {rest.length > 0 && <Text dimColor> +{rest.length}</Text>}
      </Box>
    )
  })

  on('command.run', { command: 'ticket' }, async ($, e) => {
    const [verb = '', arg = ''] = e.args.trim().split(/\s+/)
    if (verb === 'clear') {
      await update($, tickets, () => [])
      return { text: 'Cleared the active Linear tickets.' }
    }
    if (verb === 'drop') {
      const id = arg.toUpperCase()
      if (!id) return { text: 'Usage: /ticket drop <ID>' }
      const before = await read($, tickets)
      if (!before.some(t => t.id === id)) return { text: `${id} is not an active ticket.` }
      await update($, tickets, list => list.filter(t => t.id !== id))
      return { text: `Dropped ${id}.` }
    }
    if (verb !== '') return { text: 'Usage: /ticket [clear | drop <ID>]' }
    const list = await read($, tickets)
    return { text: list.length === 0 ? 'No active Linear tickets.' : describe(list) }
  })
}
