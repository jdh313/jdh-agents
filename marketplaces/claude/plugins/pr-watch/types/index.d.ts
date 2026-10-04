// One CI check on a PR's head commit, reduced to the four states the pane
// draws: `pending` covers queued, running and waiting alike.
export type Check = {
  name: string
  state: 'pending' | 'pass' | 'fail' | 'skip'
}

// One pull request this session watches. `key` is `<host>/<repo>#<number>`.
// `head` is the source branch, which Forgejo needs to find the commit its
// tasks ran on. `verdict` is `none` until the forge reports a check. Times
// are `$.clock.now()` milliseconds.
export type PullRequest = {
  key: string
  forge: 'github' | 'forgejo'
  host: string
  repo: string
  number: number
  url: string
  title?: string
  head?: string
  state: 'open' | 'merged' | 'closed'
  checks: Check[]
  verdict: 'none' | 'pending' | 'pass' | 'fail'
  addedAt: number
  polledAt: number
}

declare module 'claude-code' {
  interface PluginState {
    'pr-watch': { prs: PullRequest[] }
  }
}
