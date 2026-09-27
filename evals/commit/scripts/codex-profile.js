const { existsSync, readFileSync, writeFileSync } = require('node:fs');
const { isAbsolute, join, resolve } = require('node:path');

function tomlString(value) {
  return JSON.stringify(value);
}

function writeFixturePermissionProfile({ codexHome, fixture, profile }) {
  if (!isAbsolute(codexHome) || !isAbsolute(fixture)) {
    throw new Error('codexHome and fixture must be absolute paths.');
  }
  if (!/^[a-z][a-z0-9-]*$/.test(profile)) {
    throw new Error('profile must be a lowercase kebab-case identifier.');
  }

  const resolvedCodexHome = resolve(codexHome);
  const repo = join(resolve(fixture), 'repo');
  const profileConfig = [
    '# Generated for one disposable commit-eval fixture. Do not reuse outside this run.',
    `[permissions.${profile}]`,
    'description = "Allow only the fixture repository to be changed during this eval."',
    '',
    `[permissions.${profile}.filesystem]`,
    '":root" = "deny"',
    '":minimal" = "read"',
    '":tmpdir" = "deny"',
    '":slash_tmp" = "deny"',
    `${tomlString(repo)} = "write"`,
    `${tomlString(join(resolvedCodexHome, 'plugins'))} = "read"`,
    // Keep the authentication symlink unreadable to commands in the eval.
    `${tomlString(join(resolvedCodexHome, 'auth.json'))} = "deny"`,
    '',
    `[permissions.${profile}.network]`,
    'enabled = false',
    '',
  ].join('\n');

  // Promptfoo supplies the API key to the app-server process. Keep it out of
  // the environment inherited by commands the model chooses to run.
  const shellPolicy = [
    '[shell_environment_policy]',
    'inherit = "core"',
    'ignore_default_excludes = false',
    '',
    '[shell_environment_policy.filters]',
    '"OPENAI_API_KEY" = "exclude"',
    '"CODEX_API_KEY" = "exclude"',
  ].join('\n');

  const configPath = join(resolvedCodexHome, 'config.toml');
  // Plugin registration is already in this isolated home. Profiles get a fresh
  // name per fixture, so append instead of replacing that registration or a
  // prior row's audit metadata.
  const existingConfig = existsSync(configPath) ? readFileSync(configPath, 'utf8').trimEnd() : '';
  if (existingConfig.includes('[shell_environment_policy]') && !existingConfig.includes(shellPolicy)) {
    throw new Error('Isolated CODEX_HOME has a conflicting shell environment policy.');
  }
  const policyPrefix = existingConfig.includes(shellPolicy) ? '' : `${shellPolicy}\n\n`;
  const combinedConfig = `${existingConfig}${existingConfig ? '\n\n' : ''}${policyPrefix}${profileConfig}`;
  writeFileSync(configPath, combinedConfig, { encoding: 'utf8', mode: 0o600 });
  return profileConfig;
}

module.exports = { writeFixturePermissionProfile };
