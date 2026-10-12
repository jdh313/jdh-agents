import { expect, test } from "bun:test";
import { execFile } from "node:child_process";
import { mkdtemp, mkdir, readFile, realpath, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { createProvider, type Runner } from "../provider.ts";

// Explicit paths to already-installed fixture APIs; no dependency installation,
// credentials, model registration, session prompting, or live settings access.
const sdkRoot = process.env.WORKSPACES_TEST_PI_ROOT;
const coreRoot = process.env.WORKSPACES_TEST_SUBAGENTS_ROOT;
test.skipIf(!sdkRoot || !coreRoot)("disposable jjx: fan-out, secondary base, seven Pi tools, retained bracket", async () => {
  const fixture = await realpath(await mkdtemp(join(tmpdir(), "jjx-provider-real-")));
  const root = join(fixture, "repo");
  await mkdir(root);
  const config = join(fixture, "jj.toml");
  await writeFile(config, '[user]\nname = "Fixture"\nemail = "fixture@example.invalid"\n');
  const env = { ...process.env, JJ_CONFIG: config, GIT_CONFIG_NOSYSTEM: "1", GIT_CONFIG_GLOBAL: "/dev/null" };
  const runner: Runner = (command, args, cwd) => new Promise((accept, reject) => {
    execFile(command, args, { cwd, env, timeout: 30_000, maxBuffer: 256 * 1024, encoding: "utf8" }, (error, stdout, stderr) => error ? reject(new Error(`${error.message}\n${stdout}\n${stderr}`)) : accept({ stdout, stderr }));
  });
  try {
    await runner("jj", ["git", "init", "--colocate"], root);
    await writeFile(join(root, "marker.txt"), "parent WIP\n");
    const { provider, records } = createProvider(() => ({ Worker: {} }), runner);
    const context = (id: string, baseCwd = root) => ({ agentId: id, agentType: "Worker", baseCwd });
    const [a, b] = await Promise.all([provider.prepare(context("a")), provider.prepare(context("b"))]);
    expect(a!.cwd).not.toBe(b!.cwd);
    expect(await readFile(join(a!.cwd, "marker.txt"), "utf8")).toBe("parent WIP\n");
    const secondary = await provider.prepare(context("nested", a!.cwd));
    expect(secondary!.cwd).toContain(`${records.get("a")!.name}__pi-worker-nested-`);
    const { provider: explicit } = createProvider(() => ({ Worker: { from: "root()" } }), runner);
    const clean = await explicit.prepare(context("explicit"));
    await expect(readFile(join(clean!.cwd, "marker.txt"), "utf8")).rejects.toThrow();
    await expect(createProvider(() => ({ Worker: { from: "missing-fixture-revision" } }), runner).provider.prepare(context("invalid"))).rejects.toThrow("no parent-cwd fallback");

    // Actual Pi 1.1.0 builtins consume the provider cwd. This exercises tool
    // factories directly, NOT foreground/background subagent session binding.
    const sdk = await import(join(sdkRoot!, "dist/index.js"));
    const invoke = (factory: Function, input: object) => factory(a!.cwd).execute("fixture", input);
    const text = (result: any) => result.content.filter((c: any) => c.type === "text").map((c: any) => c.text).join("\n");
    expect(text(await invoke(sdk.createReadTool, { path: "marker.txt" }))).toContain("parent WIP");
    await invoke(sdk.createWriteTool, { path: "new.txt", content: "child only\n" });
    await invoke(sdk.createEditTool, { path: "marker.txt", edits: [{ oldText: "parent WIP", newText: "child edit" }] });
    expect(text(await invoke(sdk.createBashTool, { command: "pwd" }))).toContain(a!.cwd);
    expect(text(await invoke(sdk.createGrepTool, { pattern: "child edit", path: "." }))).toContain("marker.txt");
    expect(text(await invoke(sdk.createFindTool, { pattern: "new.txt", path: "." }))).toContain("new.txt");
    expect(text(await invoke(sdk.createLsTool, { path: "." }))).toContain("new.txt");
    expect(await readFile(join(root, "marker.txt"), "utf8")).toBe("parent WIP\n");
    expect(await readFile(join(b!.cwd, "marker.txt"), "utf8")).toBe("parent WIP\n");
    await expect(readFile(join(root, "new.txt"), "utf8")).rejects.toThrow();

    const { WorkspaceBracket } = await import(join(coreRoot!, "src/lifecycle/workspace-bracket.ts"));
    const bracket = new WorkspaceBracket(() => ({ prepare: async () => a }));
    expect(await bracket.prepare(context("a"))).toBe(a!.cwd);
    expect(bracket.wasDisposed()).toBe(false); // held lease, not a resume test
    expect(bracket.dispose({ status: "completed", description: "fixture" })).toContain("registration retained");
    expect(bracket.wasDisposed()).toBe(true); // disk retention cannot undo this
    expect(bracket.dispose({ status: "aborted", description: "again" })).toBe("");
    for (const ws of [b!, secondary!, clean!]) ws.dispose({ status: "stopped", description: "fixture" });
    const listed = (await runner("jj", ["workspace", "list", "--ignore-working-copy", "-T", 'name ++ "\\n"'], root)).stdout;
    const names = listed.trim().split("\n").map((name) => name.startsWith('"') ? JSON.parse(name) : name);
    for (const row of records.values()) expect(names).toContain(row.name);
    expect(await readFile(join(a!.cwd, "marker.txt"), "utf8")).toBe("child edit\n");
    console.log(`Disposable fixture passed: jjx 0.6 / jj 0.46; retained ${records.size + 1} workspaces before fixture teardown.`);
  } finally {
    // Only our complete disposable fixture is removed, never jjx rm/forget.
    await rm(fixture, { recursive: true, force: true });
  }
}, 90_000);
