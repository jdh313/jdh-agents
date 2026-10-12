import { execFile } from "node:child_process";
import { randomUUID } from "node:crypto";
import { readFile, realpath, stat } from "node:fs/promises";
import { basename, dirname, isAbsolute, join, resolve } from "node:path";
import type { WorkspaceProvider, WorkspacePrepareContext } from "@gotgenes/pi-subagents";

export type Policy = Readonly<Record<string, { from?: string }>>;
export type Runner = (command: string, args: string[], cwd: string) => Promise<{ stdout: string; stderr: string }>;

// No shell interpolation. Bounds cover each command, including jjx seed hooks.
// Timeout kills the direct child, not necessarily arbitrary grandchildren of seed hooks.
export const run: Runner = (command, args, cwd) => new Promise((accept, reject) => {
  execFile(command, args, { cwd, timeout: 30_000, maxBuffer: 256 * 1024, encoding: "utf8", killSignal: "SIGKILL" }, (error, stdout, stderr) => {
    if (error) reject(new Error(`${command} failed: ${error.message}\nstdout: ${stdout}\nstderr: ${stderr}`));
    else accept({ stdout, stderr });
  });
});

export function parsePolicy(value: unknown): Policy {
  if (value === undefined || value === "") return {};
  if (typeof value !== "string" || value.length > 16_384) throw new Error("--jjx-workspaces must be a bounded JSON object");
  const parsed: unknown = JSON.parse(value);
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) throw new Error("--jjx-workspaces must be an object keyed by exact agent type");
  for (const [type, options] of Object.entries(parsed)) {
    if (!type || type.length > 128 || !options || typeof options !== "object" || Array.isArray(options)) throw new Error("Invalid jjx agent policy");
    for (const [key, val] of Object.entries(options)) {
      if (key !== "from" || typeof val !== "string" || !val.trim() || val.length > 1024 || /[\x00-\x1f\x7f]/.test(val)) throw new Error("Only a nonempty bounded from revision is supported");
    }
  }
  return parsed as Policy;
}

export function safeSlug(type: string, id: string, nonce = randomUUID()): string {
  const clean = (s: string) => s.toLowerCase().replace(/[^a-z0-9-]+/g, "-").slice(0, 24).replace(/^-+|-+$/g, "") || "agent";
  return `pi-${clean(type)}-${clean(id)}-${clean(nonce)}`;
}

function onePath(stdout: string): string {
  const path = stdout.replace(/\r?\n$/, "");
  if (!isAbsolute(path) || /[\x00-\x1f\x7f]/.test(path)) throw new Error("Expected exactly one absolute workspace path");
  return path;
}

async function repoIdentity(root: string): Promise<string> {
  const pointer = join(root, ".jj", "repo");
  const info = await stat(pointer);
  return realpath(info.isDirectory() ? pointer : resolve(dirname(pointer), (await readFile(pointer, "utf8")).trim()));
}

function supported(stdout: string, binary: string, major: number, minor: number) {
  const match = new RegExp(`^${binary} ${major}\\.${minor}\\.\\d+(?:\\s|$)`).exec(stdout.trim());
  if (!match) throw new Error(`Supported ${binary} version is ${major}.${minor}.x; got ${stdout.trim()}`);
}

// Serialization is per shared repository, across adapter instances in this process.
const LOCK_KEY = Symbol.for("jdh:jjx-workspaces:creation-locks:v1");
const globals = globalThis as typeof globalThis & { [LOCK_KEY]?: Map<string, Promise<void>> };
const locks = globals[LOCK_KEY] ??= new Map<string, Promise<void>>();
async function serialized<T>(key: string, action: () => Promise<T>): Promise<T> {
  const previous = locks.get(key) ?? Promise.resolve();
  let release!: () => void;
  const tail = new Promise<void>((done) => { release = done; });
  locks.set(key, tail);
  await previous;
  try { return await action(); }
  finally { release(); if (locks.get(key) === tail) locks.delete(key); }
}

export interface WorkspaceRecord {
  agentId: string;
  repo: string;
  path: string;
  name: string;
  from?: string;
  createdAt: number;
  released: boolean;
}

export function createProvider(policy: () => Policy, runner: Runner = run) {
  const records = new Map<string, WorkspaceRecord>();
  const provider: WorkspaceProvider = {
    async prepare(ctx: WorkspacePrepareContext) {
      const configured = policy();
      if (!Object.hasOwn(configured, ctx.agentType)) return undefined;
      const options = configured[ctx.agentType];
      if (!isAbsolute(ctx.baseCwd)) throw new Error("jjx requires an absolute baseCwd");
      let artifact: string | undefined;
      let diagnostics = "";
      try {
        supported((await runner("jjx", ["--version"], ctx.baseCwd)).stdout, "jjx", 0, 6);
        supported((await runner("jj", ["--version"], ctx.baseCwd)).stdout, "jj", 0, 46);
        const root = await realpath(onePath((await runner("jj", ["root", "--ignore-working-copy"], ctx.baseCwd)).stdout));
        const repo = await repoIdentity(root);
        const mainRoot = dirname(dirname(repo));
        const spaces = resolve(`${mainRoot}-spaces`);
        return await serialized(repo, async () => {
          const slug = safeSlug(ctx.agentType, ctx.agentId);
          const args = ["open", "--unique", ...(options.from ? ["--from", options.from] : []), slug];
          const result = await runner("jjx", args, ctx.baseCwd);
          diagnostics = result.stderr;
          artifact = result.stdout;
          const returned = onePath(result.stdout);
          const path = await realpath(returned);
          // Canonical parents prevent symlink escapes; leaf must be an actual directory.
          if (path !== resolve(returned) || dirname(path) !== await realpath(spaces) || path === root || !(await stat(path)).isDirectory()) throw new Error("Unexpected or symlinked workspace path");
          const name = basename(path);
          if (!new RegExp(`^(?:.+__)?${slug}(?:-[0-9]+)?$`).test(name)) throw new Error("Unexpected workspace name");
          const childRoot = await realpath(onePath((await runner("jj", ["root", "--ignore-working-copy"], path)).stdout));
          if (childRoot !== path || await repoIdentity(path) !== repo) throw new Error("Workspace belongs to another root/repository");
          const registeredRoot = await realpath(onePath((await runner("jj", ["workspace", "root", "--name", name, "--ignore-working-copy"], ctx.baseCwd)).stdout));
          if (registeredRoot !== path) throw new Error("Workspace is not registered at returned path");
          const record: WorkspaceRecord = { agentId: ctx.agentId, repo, path, name, from: options.from, createdAt: Date.now(), released: false };
          records.set(ctx.agentId, record);
          return {
            cwd: path,
            dispose() {
              if (record.released) return undefined;
              record.released = true;
              return { resultAddendum: `\n[jjx workspace lease released; checkout AND jj registration retained]\n${path}\nInspect/integrate this workspace manually. Ordinary completed children cannot resume after lease disposal; retaining disk is not a live session. No jjx rm was run.${diagnostics ? `\njjx diagnostics: ${diagnostics}` : ""}` };
            },
          };
        });
      } catch (error) {
        throw new Error(`jjx isolation failed for ${ctx.agentType}/${ctx.agentId}; no parent-cwd fallback. ${String(error)}\nPossible partial checkout/registration retained; inspect jj workspace list and sibling directories.${artifact ? `\nReported artifact: ${artifact}` : ""}${diagnostics ? `\nstderr: ${diagnostics}` : ""}`);
      }
    },
  };
  return { provider, records };
}
