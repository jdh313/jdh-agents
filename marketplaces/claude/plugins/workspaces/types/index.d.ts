// One subagent of this session and the jjx workspace it was last seen in:
// `workspace` is `<repo>-spaces/<slug>`, absent until a path names one.
export type Placement = {
  id: string
  description: string
  type: string
  workspace?: string
  isDone: boolean
}

declare module 'claude-code' {
  interface PluginState {
    'workspaces': { agents: Placement[] }
  }
}
