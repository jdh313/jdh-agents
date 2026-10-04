import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Check, PullRequest } from '../types'

// Watches the pull requests this session opens and the CI on their heads.
// A successful `gh pr create` or `fj pr create` adds one; a timer then asks
// the forge's own CLI for state and checks, so each CLI's login is the only
// credential involved: GitHub through `gh pr view --json`, Forgejo through
// `fj pr view` (state, head branch) and `fj actions tasks` (CI per commit).
const prs = atom({ plugin: 'pr-watch', key: 'prs' } as const, [])
const PANE = 'pr-watch'
const TITLE = 'Pull requests'
const TICK_MS = 20_000
// A settled PR (CI finished or never reported) is re-asked this often, so a
// later push that restarts CI is still seen.
const SETTLED_MS = 5 * 60_000
// How long a PR with no checks yet counts as waiting for CI to start.
const WARMUP_MS = 10 * 60_000
const GLYPH = { pending: '●', pass: '✓', fail: '✗', skip: '–' } as const

type Engine = EngineInterface
type Parsed = Pick<PullRequest, 'forge' | 'host' | 'repo' | 'number' | 'url'> & Partial<Pick<PullRequest, 'title' | 'head'>>

const keyOf = (p: Pick<PullRequest, 'host' | 'repo' | 'number'>) => `${p.host}/${p.repo}#${p.number}`

// The value of `--name value`, `--name=value` or `-n value` in a command line.
export const flagOf = (command: string, ...names: string[]): string | undefined => {
  for (const name of names) {
    const found = command.match(new RegExp(`(?:^|\\s)${name}(?:=|\\s+)(['"]?)([^\\s'"]+)\\1`))
    if (found) return found[2]
  }
  return undefined
}

// `host` and `owner/repo` from a remote URL in any of git's spellings.
export const remoteRepo = (url: string): { host: string; repo: string } | undefined => {
  const found = url.trim().match(/^(?:[a-z+]+:\/\/)?(?:[^@/\s]+@)?([^:/\s]+)(?::\d+)?[:/]([^/\s]+\/[^/\s]+?)(?:\.git)?\/?$/)
  const [, host, repo] = found ?? []
  return host && repo ? { host, repo } : undefined
}

// A PR URL on either forge: GitHub's `/pull/N`, Forgejo's `/pulls/N`.
export const parseUrl = (text: string): Parsed | undefined => {
  const found = text.match(/https?:\/\/([^/\s]+)\/([^/\s]+\/[^/\s]+)\/(pull|pulls)\/(\d+)/)
  const [url, host, repo, kind, number] = found ?? []
  if (!url || !host || !repo || !number) return undefined
  return { forge: kind === 'pull' ? 'github' : 'forgejo', host, repo, number: Number(number), url }
}

const GH_CREATE = /\bgh\s+pr\s+create\b/
const FJ_CREATE = /\bfj\b[^|;&\n]*\bpr\s+create\b/

// A `gh pr create` prints the new PR's URL.
export const parseGhCreate = (command: string, output: string): Parsed | undefined => {
  if (!GH_CREATE.test(command)) return undefined
  const pr = parseUrl(output)
  return pr?.forge === 'github' ? { ...pr, head: flagOf(command, '--head', '-H') } : undefined
}

// A `fj pr create` prints `created pull request #N: <title>`; the host and
// repo come from its flags, or from `remote` when it inferred them.
export const parseFjCreate = (
  command: string,
  output: string,
  remote?: { host: string; repo: string },
): Parsed | undefined => {
  if (!FJ_CREATE.test(command)) return undefined
  const created = output.match(/created pull request #(\d+): ?(.*)/)
  if (!created) return undefined
  const host = flagOf(command, '-H', '--host') ?? remote?.host
  const repo = flagOf(command, '-r', '--repo') ?? remote?.repo
  if (!host || !repo) return undefined
  const number = Number(created[1])
  return {
    forge: 'forgejo',
    host,
    repo,
    number,
    url: `https://${host}/${repo}/pulls/${number}`,
    title: created[2]?.trim() || undefined,
    head: flagOf(command, '--head'),
  }
}

export const verdictOf = (checks: readonly Check[]): PullRequest['verdict'] =>
  checks.length === 0
    ? 'none'
    : checks.some(c => c.state === 'fail')
      ? 'fail'
      : checks.some(c => c.state === 'pending')
        ? 'pending'
        : 'pass'

type GhCheck = { __typename?: string; name?: string; context?: string; status?: string; conclusion?: string; state?: string }

// `gh pr view --json title,state,headRefName,statusCheckRollup`: check runs
// carry status + conclusion, legacy commit statuses carry context + state.
export const parseGhView = (json: string): Pick<PullRequest, 'title' | 'head' | 'state' | 'checks'> => {
  const v = JSON.parse(json) as { title?: string; state?: string; headRefName?: string; statusCheckRollup?: GhCheck[] }
  const checks = (v.statusCheckRollup ?? []).map((c): Check => {
    if (c.context !== undefined) {
      const state = c.state === 'SUCCESS' ? 'pass' : c.state === 'PENDING' || c.state === 'EXPECTED' ? 'pending' : 'fail'
      return { name: c.context, state }
    }
    const done = c.status === 'COMPLETED'
    const state = !done
      ? 'pending'
      : c.conclusion === 'SUCCESS'
        ? 'pass'
        : c.conclusion === 'NEUTRAL' || c.conclusion === 'SKIPPED'
          ? 'skip'
          : 'fail'
    return { name: c.name ?? '?', state }
  })
  return {
    title: v.title,
    head: v.headRefName,
    state: v.state === 'MERGED' ? 'merged' : v.state === 'CLOSED' ? 'closed' : 'open',
    checks,
  }
}

// fj wraps every interpolated value in Unicode isolates (U+2068, U+2069).
const plain = (text: string) => text.replace(/[⁦-⁩]/g, '').replace(/\u001b\[[0-9;]*m/g, '')

// `fj pr view`: `<title> #N`, then `By <user> — <State> — +a -b`, then
// "From `<head>` into `<base>`".
export const parseFjView = (output: string): Pick<PullRequest, 'title' | 'head' | 'state'> => {
  const lines = plain(output).split('\n')
  const title = lines[0]?.replace(/\s+#\d+\s*$/, '').trim() || undefined
  const state = lines[1]?.match(/\b(Open|Draft|Merged|Closed)\b/)?.[1]
  const head = lines[2]?.match(/From `([^`]+)`/)?.[1]
  return { title, head, state: state === 'Merged' ? 'merged' : state === 'Closed' ? 'closed' : 'open' }
}

export type Task = { id: number; sha: string; status: string; name: string; event: string }

// `fj actions tasks`, newest first:
// `#24 (c968e0637a) success validate 1m13s (pull_request): <commit title>`.
export const parseFjTasks = (output: string): Task[] =>
  plain(output)
    .split('\n')
    .flatMap(line => {
      const [, id, sha, status, rest, event] = line.match(/^#(\d+) \(([0-9a-f]+)\) (\S+) (.+?) \(([\w-]+)\): /) ?? []
      if (!id || !sha || !status || !rest || !event) return []
      return [{ id: Number(id), sha, status, name: rest.replace(/\s+\S*\d+s$/, ''), event }]
    })

const taskState = (status: string): Check['state'] =>
  status === 'success' ? 'pass' : status === 'skipped' ? 'skip' : status === 'failure' || status === 'cancelled' ? 'fail' : 'pending'

// The newest task per workflow job on commit `sha`, as checks.
export const checksForCommit = (tasks: readonly Task[], sha: string): Check[] => {
  const seen = new Map<string, Check>()
  for (const t of tasks) {
    if (sha.startsWith(t.sha) && !seen.has(t.name)) seen.set(t.name, { name: t.name, state: taskState(t.status) })
  }
  return [...seen.values()]
}

const run = async ($: Engine, argv: string[]) => {
  try {
    const out = await $.process.run(argv, { timeoutMs: 20_000 })
    return out.exitCode === 0 ? out.stdout : undefined
  } catch {
    return undefined
  }
}

// The commit a branch points at, as last pushed (a jj bookmark is exported
// to the same refs in a colocated repo).
const shaOf = async ($: Engine, head: string) => {
  for (const ref of [`refs/remotes/origin/${head}`, `refs/heads/${head}`]) {
    const sha = (await run($, ['git', 'rev-parse', '--verify', '--quiet', `${ref}^{commit}`]))?.trim()
    if (sha) return sha
  }
  return undefined
}

type Fresh = Pick<PullRequest, 'title' | 'head' | 'state' | 'checks'>

const askGitHub = async ($: Engine, pr: PullRequest): Promise<Fresh | undefined> => {
  const json = await run($, ['gh', 'pr', 'view', pr.url, '--json', 'title,state,headRefName,statusCheckRollup'])
  if (json === undefined) return undefined
  try {
    return parseGhView(json)
  } catch {
    return undefined
  }
}

const askForgejo = async ($: Engine, pr: PullRequest): Promise<Fresh | undefined> => {
  const view = await run($, ['fj', '-H', pr.host, 'pr', 'view', `${pr.repo}#${pr.number}`])
  if (view === undefined) return undefined
  const seen = parseFjView(view)
  const head = seen.head ?? pr.head
  const sha = head && (await shaOf($, head))
  const tasks = sha ? await run($, ['fj', '-H', pr.host, 'actions', 'tasks', '-r', pr.repo]) : undefined
  return { ...seen, head, checks: sha && tasks ? checksForCommit(parseFjTasks(tasks), sha) : pr.checks }
}

const isDue = (pr: PullRequest, now: number) => {
  if (pr.state !== 'open') return false
  const waiting = pr.verdict === 'pending' || (pr.verdict === 'none' && now - pr.addedAt < WARMUP_MS)
  return waiting || now - pr.polledAt >= SETTLED_MS
}

// What changed between two polls of one PR that is worth a toast.
export const newsOf = (before: PullRequest, after: PullRequest): string | undefined => {
  const label = `PR #${after.number}`
  if (before.state === 'open' && after.state !== 'open') return `${label} ${after.state}`
  if (after.verdict === before.verdict) return undefined
  if (after.verdict === 'pass') return `${label}: CI passed`
  if (after.verdict === 'fail') {
    const failed = after.checks.filter(c => c.state === 'fail').map(c => c.name)
    return `${label}: CI failed (${failed.join(', ')})`
  }
  return undefined
}

let isPolling = false

const poll = async ($: Engine, force = false) => {
  if (isPolling) return
  isPolling = true
  try {
    const now = await $.clock.now()
    for (const pr of await read($, prs)) {
      if (!force && !isDue(pr, now)) continue
      const fresh = pr.forge === 'github' ? await askGitHub($, pr) : await askForgejo($, pr)
      if (!fresh) continue
      const after: PullRequest = {
        ...pr,
        ...fresh,
        title: fresh.title ?? pr.title,
        verdict: verdictOf(fresh.checks),
        polledAt: now,
      }
      await update($, prs, list => list.map(p => (p.key === pr.key ? after : p)))
      const news = newsOf(pr, after)
      if (news) $.ui.toast(news, { timeoutMs: 8000 })
    }
  } finally {
    isPolling = false
  }
}

let ticker: { cancel: () => void } | undefined

const ensureTicking = ($: Engine) => {
  ticker ??= $.clock.every(TICK_MS, () => void poll($))
}

const track = async ($: Engine, found: Parsed) => {
  const now = await $.clock.now()
  const key = keyOf(found)
  const fresh: PullRequest = { ...found, key, state: 'open', checks: [], verdict: 'none', addedAt: now, polledAt: 0 }
  await update($, prs, list => [list.find(p => p.key === key) ?? fresh, ...list.filter(p => p.key !== key)])
  void $.ui.open({ id: PANE, title: TITLE }).catch(() => undefined)
  ensureTicking($)
  await poll($)
}

// What a Bash call printed, from its record or from the text the model got.
const outputOf = (ran: { result?: unknown; text?: string }) => {
  const record = ran.result as { stdout?: unknown } | undefined
  return [typeof record?.stdout === 'string' ? record.stdout : '', ran.text ?? ''].join('\n')
}

const remoteOf = async ($: Engine, command: string) => {
  const url = await run($, ['git', 'remote', 'get-url', flagOf(command, '-R', '--remote') ?? 'origin'])
  return url ? remoteRepo(url) : undefined
}

const describe = (list: readonly PullRequest[]) =>
  list
    .map(pr =>
      [
        `${pr.state === 'open' ? GLYPH[pr.verdict === 'none' ? 'pending' : pr.verdict] : pr.state} ${pr.repo}#${pr.number}${pr.title ? ` ${pr.title}` : ''}`,
        ...pr.checks.map(c => `  ${GLYPH[c.state]} ${c.name}`),
      ].join('\n'),
    )
    .join('\n')

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'prs',
      description: 'Show the pull requests this session watches and their CI',
      argumentHint: '[add <url> | refresh | clear]',
    })
    if ((await read($, prs)).some(p => p.state === 'open')) ensureTicking($)
    return next(e)
  })

  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    const ran = await next(e)
    if (ran.deny !== undefined || ran.isError) return ran
    const command = String(e.command ?? '')
    if (!GH_CREATE.test(command) && !FJ_CREATE.test(command)) return ran
    const output = outputOf(ran)
    const needsRemote = FJ_CREATE.test(command) && !(flagOf(command, '-H', '--host') && flagOf(command, '-r', '--repo'))
    const found =
      parseGhCreate(command, output) ??
      parseFjCreate(command, output, needsRemote ? await remoteOf($, command) : undefined)
    if (found) await track($, found)
    return ran
  })

  on('command.run', { command: 'prs' }, async ($, e) => {
    const [verb = '', arg = ''] = e.args.trim().split(/\s+/)
    if (verb === 'add') {
      const found = parseUrl(arg)
      if (!found) return { text: 'Usage: /prs add <PR URL>' }
      await track($, found)
      return { text: `Watching ${found.repo}#${found.number}.` }
    }
    if (verb === 'refresh') {
      await poll($, true)
    } else if (verb === 'clear') {
      await update($, prs, list => list.filter(p => p.state === 'open'))
      return { text: 'Cleared merged and closed pull requests.' }
    } else if (verb !== '') {
      return { text: 'Usage: /prs [add <url> | refresh | clear]' }
    }
    await $.ui.open({ id: PANE, title: TITLE })
    const list = await read($, prs)
    return { text: list.length === 0 ? 'No pull requests yet.' : describe(list) }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const list = await read($, prs)
    return (
      <Box flexDirection="column">
        {list.length === 0 && <Text dimColor>No pull requests yet.</Text>}
        {list.map(pr => {
          const isOpen = pr.state === 'open'
          const verdict = pr.verdict === 'none' ? 'pending' : pr.verdict
          const color = !isOpen ? undefined : verdict === 'pass' ? 'green' : verdict === 'fail' ? 'red' : 'yellow'
          return (
            <Box flexDirection="column" marginBottom={1}>
              <Box>
                <Text bold color={color} dimColor={!isOpen}>
                  {isOpen ? GLYPH[verdict] : pr.state} #{pr.number}
                </Text>
                <Box flexShrink={1}>
                  <Text dimColor={!isOpen} wrap="truncate-end">
                    {' '}
                    {pr.title ?? ''}
                  </Text>
                </Box>
              </Box>
              <Text dimColor wrap="truncate-end">
                {'  '}
                {pr.repo}
                {isOpen && pr.checks.length === 0 ? ' · no checks yet' : ''}
              </Text>
              {isOpen &&
                pr.checks.map(c => (
                  <Text dimColor={c.state === 'pass' || c.state === 'skip'} wrap="truncate-end">
                    {'  '}
                    {GLYPH[c.state]} {c.name}
                  </Text>
                ))}
            </Box>
          )
        })}
      </Box>
    )
  })
}
