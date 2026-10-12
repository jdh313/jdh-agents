import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import type { SubagentsService } from "@gotgenes/pi-subagents";
import { createProvider, parsePolicy } from "./provider.ts";

const SERVICE_KEY = Symbol.for("@gotgenes/pi-subagents:service");
export const LEASE_KEY = Symbol.for("jdh:jjx-workspaces:owner:v1");
interface Lease { token: object; service?: SubagentsService; unregister?: () => void; error?: string; validatePolicy?: () => void }
const bridge = globalThis as typeof globalThis & { [SERVICE_KEY]?: SubagentsService; [LEASE_KEY]?: Lease };

// Programmatic callers must use this captured service, not the mutable core
// symbol, and check readiness before dispatch. This does not intercept spawn().
export function requireWorkspaceService(): SubagentsService {
  const owner = bridge[LEASE_KEY];
  if (!owner?.service || owner.error || !owner.unregister) throw new Error(owner?.error ?? "workspaces-pi is not registered; isolated dispatch is unavailable");
  owner.validatePolicy?.();
  return owner.service;
}

// One root session per process. Inherited child factories must not acquire or
// release the parent's provider, even if core republished its global service.
export default function jjxWorkspaces(pi: ExtensionAPI) {
  if (bridge[LEASE_KEY]) return;
  const owner: Lease = { token: {}, service: bridge[SERVICE_KEY] };
  bridge[LEASE_KEY] = owner;
  pi.registerFlag("jjx-workspaces", {
    description: 'Opt-in JSON policy keyed by exact subagent type, e.g. {"Worker":{}}',
    type: "string",
    default: "",
  });
  owner.validatePolicy = () => { parsePolicy(pi.getFlag("jjx-workspaces")); };
  const { provider } = createProvider(() => parsePolicy(pi.getFlag("jjx-workspaces")));
  try {
    if (!owner.service || typeof owner.service.registerWorkspaceProvider !== "function") throw new Error("Load @gotgenes/pi-subagents 23.4.0 before workspaces-pi");
    owner.unregister = owner.service.registerWorkspaceProvider(provider);
  } catch (error) {
    owner.error = `workspaces-pi unavailable: ${String(error)}. Do not dispatch opted-in agents; fix load order/provider conflict and reload.`;
  }

  // A factory exception alone is insufficient: Pi can continue after load errors.
  // Fail closed at the core's model-tool boundary, including nested tool calls.
  pi.on("tool_call", (event) => {
    if (event.toolName !== "subagent") return;
    if (owner.error) return { block: true, reason: owner.error };
    try { parsePolicy(pi.getFlag("jjx-workspaces")); }
    catch (error) { return { block: true, reason: `Invalid jjx policy: ${String(error)}` }; }
  });
  pi.on("session_start", () => {
    if (owner.error) throw new Error(owner.error);
    parsePolicy(pi.getFlag("jjx-workspaces"));
  });
  pi.on("session_shutdown", () => {
    if (bridge[LEASE_KEY]?.token !== owner.token) return;
    owner.unregister?.(); // Captured parent service, never a child's current symbol.
    delete bridge[LEASE_KEY];
  });
}
