import { afterEach, describe, expect, test } from "bun:test";
import { mkdtemp, mkdir, readFile, realpath, rm, symlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { createProvider, parsePolicy, safeSlug, run, type Runner } from "../provider.ts";
import extension, { LEASE_KEY, requireWorkspaceService } from "../extension.ts";

const fixtures: string[] = [];
afterEach(async () => { for (const path of fixtures.splice(0)) await rm(path, { recursive: true, force: true }); delete (globalThis as any)[LEASE_KEY]; delete (globalThis as any)[Symbol.for("@gotgenes/pi-subagents:service")]; });
async function fixture() {
  const dir = await realpath(await mkdtemp(join(tmpdir(), "jjx-provider-unit-")));
  fixtures.push(dir);
  const root = join(dir, "repo");
  await mkdir(join(root, ".jj", "repo"), { recursive: true });
  const paths: string[] = [];
  const calls: { command: string; args: string[]; cwd: string }[] = [];
  let active = 0, maximum = 0;
  const runner: Runner = async (command, args, cwd) => {
    calls.push({ command, args, cwd });
    if (args[0] === "--version") return { stdout: command === "jjx" ? "jjx 0.6.0\n" : "jj 0.46.0\n", stderr: "" };
    if (command === "jjx") {
      maximum = Math.max(maximum, ++active);
      await new Promise((done) => setTimeout(done, 5));
      const path = join(`${root}-spaces`, args.at(-1)!);
      await mkdir(join(path, ".jj"), { recursive: true });
      await writeFile(join(path, ".jj", "repo"), join(root, ".jj", "repo"));
      paths.push(path);
      --active;
      return { stdout: `${path}\n`, stderr: "seed warning" };
    }
    return { stdout: `${args[0] === "workspace" ? join(`${root}-spaces`, args[3]) : cwd}\n`, stderr: "" };
  };
  return { root, runner, calls, paths, maximum: () => maximum };
}
const context = (root: string, id = "id") => ({ agentId: id, agentType: "Worker", baseCwd: root });

describe("policy and prepare", () => {
  test("default none; strict bounded policy; exact types", async () => {
    expect(parsePolicy(undefined)).toEqual({});
    expect(parsePolicy('{"Worker":{"from":"root()"}}')).toEqual({ Worker: { from: "root()" } });
    for (const value of ['[]', '{"Worker":true}', '{"Worker":{"cleanup":true}}', '{"Worker":{"from":""}}', "x".repeat(17000)]) expect(() => parsePolicy(value)).toThrow();
    const { provider } = createProvider(() => ({}), async () => { throw new Error("must not run"); });
    expect(await provider.prepare(context("/nonexistent"))).toBeUndefined();
    const configured = createProvider(() => ({ Worker: {} }), async () => { throw new Error("must not run"); });
    expect(await configured.provider.prepare({ ...context("/nonexistent"), agentType: "worker" })).toBeUndefined();
  });
  test("bounded subprocess reports nonzero stderr and rejects excessive output", async () => {
    const f = await fixture();
    await expect(run(process.execPath, ["-e", 'console.error("fixture stderr"); process.exit(7)'], f.root)).rejects.toThrow("fixture stderr");
    await expect(run(process.execPath, ["-e", 'console.log("x".repeat(300000))'], f.root)).rejects.toThrow("failed");
  });
  test("slug is bounded safe ASCII even for hostile type/id; nonce distinguishes", () => {
    const a = safeSlug("../../;💣", "id $(touch bad)", "one");
    expect(a).toMatch(/^pi-[a-z0-9-]+$/);
    expect(a.length).toBeLessThan(100);
    expect(a).not.toBe(safeSlug("../../;💣", "id $(touch bad)", "two"));
  });
  test("explicit baseCwd, argv base, unique paths, serialized creation; synchronous retain dispose", async () => {
    const f = await fixture();
    const { provider, records } = createProvider(() => ({ Worker: { from: 'root() | bookmarks("x;y")' } }), f.runner);
    const workspaces = await Promise.all([provider.prepare(context(f.root, "a")), provider.prepare(context(f.root, "b"))]);
    expect(f.maximum()).toBe(1);
    expect(workspaces[0]!.cwd).not.toBe(workspaces[1]!.cwd);
    const opens = f.calls.filter((call) => call.command === "jjx" && call.args[0] === "open");
    expect(opens.every((call) => call.cwd === f.root && call.args[1] === "--unique" && call.args[3] === 'root() | bookmarks("x;y")')).toBe(true);
    const result = workspaces[0]!.dispose({ status: "completed", description: "done" });
    expect(result).not.toBeInstanceOf(Promise);
    expect(result!.resultAddendum).toContain("checkout AND jj registration retained");
    expect(result!.resultAddendum).toContain("cannot resume");
    expect(workspaces[0]!.dispose({ status: "aborted", description: "again" })).toBeUndefined();
    expect(records.get("a")!.released).toBe(true);
    expect(await readFile(join(workspaces[0]!.cwd, ".jj", "repo"), "utf8")).toBe(join(f.root, ".jj", "repo"));
    expect(f.calls.some((call) => call.args.includes("rm") || call.args.includes("forget"))).toBe(false);
  });
  test("failed creation releases same-repo queue without deleting a partial artifact", async () => {
    const f = await fixture();
    let first = true;
    const runner: Runner = async (command, args, cwd) => {
      const result = await f.runner(command, args, cwd);
      if (command === "jjx" && args[0] === "open" && first) { first = false; throw new Error(`partial artifact: ${result.stdout}`); }
      return result;
    };
    const { provider } = createProvider(() => ({ Worker: {} }), runner);
    const outcomes = await Promise.allSettled([provider.prepare(context(f.root, "failed")), provider.prepare(context(f.root, "next"))]);
    // Async repo probes may admit either caller first; the queue must recover
    // regardless of which caller receives the injected first-creation failure.
    expect(outcomes.filter((result) => result.status === "rejected")).toHaveLength(1);
    expect(outcomes.filter((result) => result.status === "fulfilled")).toHaveLength(1);
    expect(f.maximum()).toBe(1);
    expect(await readFile(join(f.paths[0], ".jj", "repo"), "utf8")).toBeTruthy();
  });
  test("opted-in errors reject, including unsupported version/missing binary/non-jj", async () => {
    const f = await fixture();
    for (const runner of [async () => { throw new Error("ENOENT"); }, async () => ({ stdout: "jjx 0.5.0", stderr: "" }), async (cmd: string, args: string[], cwd: string) => { if (args[0] === "root") throw new Error("not jj"); return f.runner(cmd, args, cwd); }]) {
      const { provider } = createProvider(() => ({ Worker: {} }), runner);
      await expect(provider.prepare(context(f.root))).rejects.toThrow("no parent-cwd fallback");
    }
  });
  test("malformed/foreign/symlink output and missing registration fail and retain artifacts", async () => {
    for (const mode of ["multiple", "relative", "foreign", "symlink", "registration"]) {
      const f = await fixture();
      const runner: Runner = async (command, args, cwd) => {
        const result = await f.runner(command, args, cwd);
        if (command === "jjx" && args[0] === "open") {
          if (mode === "multiple") return { ...result, stdout: `${result.stdout}/another\n` };
          if (mode === "relative") return { ...result, stdout: "relative\n" };
          if (mode === "foreign") { await writeFile(join(f.paths[0], ".jj", "repo"), f.root); }
          if (mode === "symlink") { const link = `${f.paths[0]}-link`; await symlink(f.paths[0], link); return { ...result, stdout: `${link}\n` }; }
        }
        if (mode === "registration" && args[0] === "workspace") throw new Error("not registered");
        return result;
      };
      await expect(createProvider(() => ({ Worker: {} }), runner).provider.prepare(context(f.root))).rejects.toThrow("Possible partial checkout/registration retained");
      expect(await readFile(join(f.paths[0], ".jj", "repo"), "utf8")).toBeTruthy();
    }
  });
});

function fakePi() {
  const events = new Map<string, Function>();
  return { events, on: (name: string, handler: Function) => { events.set(name, handler); }, registerFlag: () => {}, getFlag: () => '{"Worker":{}}' };
}
describe("registration ownership", () => {
  test("captures parent; inherited child factory/shutdown cannot register or unregister parent", () => {
    const serviceKey = Symbol.for("@gotgenes/pi-subagents:service");
    let registrations = 0, unregistrations = 0;
    const parent = { registerWorkspaceProvider: () => { registrations++; return () => { unregistrations++; }; } };
    (globalThis as any)[serviceKey] = parent;
    const root = fakePi(); extension(root as any);
    expect(requireWorkspaceService()).toBe(parent);
    (globalThis as any)[serviceKey] = { registerWorkspaceProvider: () => { throw new Error("child service must not be used"); } };
    const child = fakePi(); extension(child as any);
    expect(child.events.size).toBe(0);
    expect(requireWorkspaceService()).toBe(parent);
    delete (globalThis as any)[serviceKey]; // Core child shutdown unpublishes it.
    root.events.get("session_shutdown")!(); root.events.get("session_shutdown")!();
    expect(registrations).toBe(1); expect(unregistrations).toBe(1);
  });
  test("tool boundary does not intercept direct service.spawn: readiness is required", () => {
    let spawns = 0;
    const service = { spawn: () => { spawns++; }, registerWorkspaceProvider: () => { throw new Error("conflict"); } };
    (globalThis as any)[Symbol.for("@gotgenes/pi-subagents:service")] = service;
    const pi = fakePi(); extension(pi as any);
    expect(pi.events.get("tool_call")!({ toolName: "subagent" }).block).toBe(true);
    expect(() => requireWorkspaceService()).toThrow();
    service.spawn(); // Deliberate unsupported bypass, not an isolated execution.
    expect(spawns).toBe(1);
  });
  test("missing service and provider conflicts fail visibly and block subagent dispatch", () => {
    for (const service of [undefined, { registerWorkspaceProvider: () => { throw new Error("only one is supported"); } }]) {
      (globalThis as any)[Symbol.for("@gotgenes/pi-subagents:service")] = service;
      const pi = fakePi(); extension(pi as any);
      expect(() => pi.events.get("session_start")!()).toThrow("workspaces-pi unavailable");
      expect(() => requireWorkspaceService()).toThrow();
      expect(pi.events.get("tool_call")!({ toolName: "subagent" }).block).toBe(true);
      expect(pi.events.get("tool_call")!({ toolName: "read" })).toBeUndefined();
      pi.events.get("session_shutdown")!();
    }
  });
});
