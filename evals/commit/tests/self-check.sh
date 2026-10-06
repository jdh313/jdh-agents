#!/usr/bin/env bash
set -euo pipefail

eval_dir=$(cd "$(dirname "$0")/.." && pwd)
temp_dir=$(mktemp -d "${TMPDIR:-/tmp}/commit-eval-self-check.XXXXXX")
trap 'rm -rf "$temp_dir"' EXIT
codex_artifact_count() {
  if [[ -d "$eval_dir/artifacts" ]]; then
    find "$eval_dir/artifacts" -maxdepth 1 -type d -name 'codex-*' | wc -l | tr -d ' '
  else
    printf '0\n'
  fi
}

for codex_sandbox_mode in workspace-write read-only; do
  codex_artifacts_before=$(codex_artifact_count)
  set +e
  codex_guard_output=$(COMMIT_EVAL_CODEX_SANDBOX_MODE="$codex_sandbox_mode" "$eval_dir/scripts/run.sh" codex 2>&1)
  codex_guard_exit=$?
  set -e
  codex_artifacts_after=$(codex_artifact_count)
  [[ $codex_guard_exit -eq 2 ]]
  [[ "$codex_guard_output" == *"Codex commit evaluation cannot run with $codex_sandbox_mode"* ]]
  [[ "$codex_guard_output" == *'COMMIT_EVAL_CODEX_SANDBOX_MODE=danger-full-access'* ]]
  [[ "$codex_artifacts_before" == "$codex_artifacts_after" ]]
done

set +e
profile_auth_output=$(env -u OPENAI_API_KEY CODEX_HOST_AUTH_PATH="$temp_dir/missing-auth.json" COMMIT_EVAL_CODEX_SANDBOX_MODE=permission-profile "$eval_dir/scripts/run.sh" codex 2>&1)
profile_auth_exit=$?
set -e
[[ $profile_auth_exit -eq 2 ]]
[[ "$profile_auth_output" == *"Codex needs OPENAI_API_KEY or an existing auth file at $temp_dir/missing-auth.json."* ]]

node "$eval_dir/scripts/patch-codex-app-server.mjs" > "$temp_dir/codex-app-server-adapter.log"
grep -q 'permission-profile adapter' "$temp_dir/codex-app-server-adapter.log"
node "$eval_dir/scripts/patch-codex-app-server.mjs" > "$temp_dir/codex-app-server-adapter-second.log"
grep -q 'already applied' "$temp_dir/codex-app-server-adapter-second.log"

"$eval_dir/scripts/create-fixture.sh" "$temp_dir/fixture"

set +e
node "$eval_dir/scripts/grade.mjs" "$temp_dir/fixture" > "$temp_dir/initial-grade.json"
grade_exit=$?
set -e
[[ $grade_exit -eq 1 ]]
node -e '
const report = require(process.argv[1]);
if (report.passed || !report.checks.some((check) => check.name === "exactly one new commit" && !check.passed)) process.exit(1);
' "$temp_dir/initial-grade.json"
git -C "$temp_dir/fixture/repo" add README.md
git -C "$temp_dir/fixture/repo" commit --quiet -m 'docs: clarify eval README'
node "$eval_dir/scripts/grade.mjs" "$temp_dir/fixture" > "$temp_dir/passing-grade.json"
node -e '
const report = require(process.argv[1]);
if (!report.passed) process.exit(1);
' "$temp_dir/passing-grade.json"
node -e '
const { checkMessage } = require(process.argv[1]);
const passes = (message) => checkMessage(message).every((check) => check.passed);
const ok = passes("docs: clarify eval README\n")
  && !passes("docs: clarify eval README\n\n1\n2\n3\n4\n5\n6\n")
  && !passes("docs: clarify eval README.\n");
process.exit(ok ? 0 : 1);
' "$eval_dir/assertions/house-style.js"
mkdir -p "$temp_dir/codex-home/plugins"
printf '%s\n' 'not-a-real-auth-token' > "$temp_dir/codex-home/auth.json"
printf '%s\n' '[plugins."commit@jdh-agents"]' 'enabled = true' > "$temp_dir/codex-home/config.toml"
node -e '
const { readFileSync } = require("node:fs");
const { join, resolve } = require("node:path");
const { writeFixturePermissionProfile } = require(process.argv[1]);
const [codexHome, fixture] = process.argv.slice(2);
const profile = writeFixturePermissionProfile({ codexHome, fixture, profile: "commit-eval" });
const repo = join(resolve(fixture), "repo");
const resolvedCodexHome = resolve(codexHome);
const config = readFileSync(join(resolvedCodexHome, "config.toml"), "utf8");
const checks = [
  profile.includes("\":root\" = \"deny\""),
  profile.includes("\":minimal\" = \"read\""),
  profile.includes("\":tmpdir\" = \"deny\""),
  profile.includes("\":slash_tmp\" = \"deny\""),
  profile.includes(`${JSON.stringify(repo)} = \"write\"`),
  profile.includes(`${JSON.stringify(join(resolvedCodexHome, "plugins"))} = \"read\"`),
  profile.includes(`${JSON.stringify(join(resolvedCodexHome, "auth.json"))} = \"deny\"`),
  profile.includes("[permissions.commit-eval.network]\nenabled = false"),
  config.includes(`[plugins."commit@jdh-agents"]\nenabled = true`),
  config.includes("[shell_environment_policy]\ninherit = \"core\"\nignore_default_excludes = false"),
  config.includes("[shell_environment_policy.filters]\n\"OPENAI_API_KEY\" = \"exclude\"\n\"CODEX_API_KEY\" = \"exclude\""),
  config.trimEnd().endsWith(profile.trimEnd()),
];
process.exit(checks.every(Boolean) ? 0 : 1);
' "$eval_dir/scripts/codex-profile.js" "$temp_dir/codex-home" "$temp_dir/fixture"
COMMIT_EVAL_FIXTURES="$temp_dir/hooked" COMMIT_EVAL_CODEX_HOME="$temp_dir/codex-home" COMMIT_EVAL_CODEX_PROFILE=commit-eval node -e '
const { existsSync } = require("node:fs");
const { beforeEach } = require(process.argv[1]);
(async () => {
  const test = { options: { keep: 1 }, metadata: {} };
  const [a, b] = [(await beforeEach({ test })).test, (await beforeEach({ test })).test];
  const ok = a.metadata.fixture !== b.metadata.fixture
    && a.options.working_dir === `${a.metadata.fixture}/repo`
    && a.options.keep === 1
    && a.options.permissions === `commit-eval-${a.metadata.fixtureId}`
    && b.options.permissions === `commit-eval-${b.metadata.fixtureId}`
    && existsSync(`${b.metadata.fixture}/repo/notes.txt`);
  process.exit(ok ? 0 : 1);
})();
' "$eval_dir/scripts/fixture-hook.js"
"$eval_dir/scripts/create-fixture.sh" "$temp_dir/jj-fixture" jj </dev/null
set +e
node "$eval_dir/scripts/grade.mjs" "$temp_dir/jj-fixture" > /dev/null
jj_grade_exit=$?
set -e
[[ $jj_grade_exit -eq 1 ]]
(cd "$temp_dir/jj-fixture/repo" && jj --no-pager commit --quiet -m 'docs: clarify eval README' README.md </dev/null)
node "$eval_dir/scripts/grade.mjs" "$temp_dir/jj-fixture" > "$temp_dir/jj-grade.json"
node -e '
const { judge, collectCommands } = require(process.argv[1]);
const claude = (command) => collectCommands({ toolCalls: [{ name: "Bash", input: { command } }] });
const codex = (command) => collectCommands({ items: [{ type: "commandExecution", command }] });
const ok = judge(claude("jj commit -m \"docs: x\" README.md")).pass
  && judge(codex("/bin/zsh -lc \"jj --no-pager commit -m docs README.md\"")).pass
  && !judge(claude("git add README.md && git commit -m docs")).pass
  && !judge(claude("jj st; git -C . commit -m docs")).pass
  && !judge(claude("git status")).pass;
process.exit(ok ? 0 : 1);
' "$eval_dir/assertions/vcs-choice.js"
printf 'self-check passed: Codex restrictive modes fail before artifacts; permission-profile accepts the normal auth-file fallback; the version-guarded app-server adapter is idempotent; the scoped profile renders fixture writes, minimal runtime and plugin reads, and temp and auth denials; git and jj fixtures reject their initial state and accept the expected outcome; beforeEach yields a distinct fixture per row; vcs-choice separates jj from git commits\n'
