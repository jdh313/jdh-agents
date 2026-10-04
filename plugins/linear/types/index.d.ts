export type Ticket = { id: string; title?: string }

declare module 'claude-code' {
  interface PluginState {
    'linear': { tickets: Ticket[] }
  }
}
