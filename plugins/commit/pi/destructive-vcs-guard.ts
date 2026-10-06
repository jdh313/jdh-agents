import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI, ToolCallEventResult } from "@earendil-works/pi-coding-agent";

const guardPath = fileURLToPath(new URL("../hooks/destructive-vcs-guard.sh", import.meta.url));
const timeoutMs = 5_000;

function couldNotRun(detail: string): ToolCallEventResult {
	return { block: true, reason: `[commit plugin] Guard could not run: ${detail}. Shell command blocked (fail closed).` };
}

function checkCommand(command: string, cwd: string): Promise<ToolCallEventResult | undefined> {
	return new Promise((resolve) => {
		// Execute directly (no shell), so missing files and execute permissions fail closed.
		const child = spawn(guardPath, [], { cwd, stdio: ["pipe", "ignore", "pipe"] });
		let stderr = "";
		let settled = false;
		const finish = (result: ToolCallEventResult | undefined) => {
			if (settled) return;
			settled = true;
			clearTimeout(timer);
			resolve(result);
		};
		const timer = setTimeout(() => {
			child.kill("SIGKILL");
			finish(couldNotRun(`timed out after ${timeoutMs / 1000} seconds`));
		}, timeoutMs);

		child.stderr.setEncoding("utf8");
		child.stderr.on("data", (data: string) => { stderr += data; });
		child.on("error", (error) => finish(couldNotRun(error.message)));
		child.stdin.on("error", (error) => {
			child.kill("SIGKILL");
			finish(couldNotRun(`could not write guard input: ${error.message}`));
		});
		child.on("close", (code, signal) => {
			if (code === 0) finish(undefined);
			else if (code === 2) finish({ block: true, reason: stderr.trim() || "[commit plugin] Blocked by destructive-VCS guard." });
			else finish(couldNotRun(`exit ${code ?? signal ?? "unknown"}${stderr.trim() ? `: ${stderr.trim()}` : ""}`));
		});
		child.stdin.end(JSON.stringify({ tool_name: "Bash", tool_input: { command } }));
	});
}

export default function (pi: ExtensionAPI) {
	pi.on("tool_call", async (event, ctx) => {
		if (event.toolName !== "bash") return;
		if (typeof event.input.command !== "string") return couldNotRun("invalid bash command input");
		try {
			return await checkCommand(event.input.command, ctx.cwd);
		} catch (error) {
			return couldNotRun(error instanceof Error ? error.message : String(error));
		}
	});
}
