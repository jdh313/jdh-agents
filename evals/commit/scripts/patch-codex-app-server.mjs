import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const evalDir = dirname(dirname(fileURLToPath(import.meta.url)));
const promptfooDir = join(evalDir, 'node_modules', 'promptfoo');
const packagePath = join(promptfooDir, 'package.json');
// Promptfoo's CLI entry point loads this three-byte export shim and its target.
// The other hashed provider bundles are used by library/browser entry points.
const providerPath = join(promptfooDir, 'dist', 'src', 'codex-app-server-B9-ncut6.js');
const expectedVersion = '0.123.1';

function replaceExactly(source, before, after, expectedCount, label) {
  const count = source.split(before).length - 1;
  if (count !== expectedCount) {
    throw new Error(`Promptfoo ${expectedVersion} ${label} changed: expected ${expectedCount} match(es), found ${count}. Refusing to patch.`);
  }
  return source.replaceAll(before, after);
}

function verifyPatched(source) {
  return source.includes('permissions: z$1.string().min(1).optional(),')
    && source.includes('...config.permissions ? { permissions: config.permissions } : { sandbox: config.sandbox_mode ?? "read-only" },')
    && source.includes('...config.permissions ? { permissions: config.permissions } : config.sandbox_policy || config.network_access_enabled !== void 0 ? { sandboxPolicy: this.buildSandboxPolicy(config) } : {},')
    && source.includes('permissionProfile: config.permissions ?? null,');
}

let packageJson;
try {
  packageJson = JSON.parse(readFileSync(packagePath, 'utf8'));
} catch (error) {
  throw new Error(`Promptfoo is not installed at ${promptfooDir}; run npm ci in ${evalDir}.`, { cause: error });
}
if (packageJson.version !== expectedVersion) {
  throw new Error(`Expected Promptfoo ${expectedVersion}, found ${packageJson.version ?? 'unknown'}. Refusing to patch.`);
}

let source;
try {
  source = readFileSync(providerPath, 'utf8');
} catch (error) {
  throw new Error(`Expected Promptfoo provider bundle is missing: ${providerPath}. Refusing to patch.`, { cause: error });
}

if (verifyPatched(source)) {
  process.stdout.write(`Codex app-server permission-profile adapter already applied: ${providerPath}\n`);
  process.exit(0);
}

source = replaceExactly(
  source,
  'sandbox_policy: z$1.record(z$1.string(), z$1.unknown()).optional(),\n\tnetwork_access_enabled:',
  'sandbox_policy: z$1.record(z$1.string(), z$1.unknown()).optional(),\n\tpermissions: z$1.string().min(1).optional(),\n\tnetwork_access_enabled:',
  1,
  'config schema',
);
source = replaceExactly(
  source,
  '\t\t\tsandbox: config.sandbox_mode ?? "read-only",',
  '\t\t\t...config.permissions ? { permissions: config.permissions } : { sandbox: config.sandbox_mode ?? "read-only" },',
  2,
  'thread sandbox fields',
);
source = replaceExactly(
  source,
  '\t\t\t...config.sandbox_policy || config.network_access_enabled !== void 0 ? { sandboxPolicy: this.buildSandboxPolicy(config) } : {},',
  '\t\t\t...config.permissions ? { permissions: config.permissions } : config.sandbox_policy || config.network_access_enabled !== void 0 ? { sandboxPolicy: this.buildSandboxPolicy(config) } : {},',
  1,
  'turn sandbox policy',
);
source = replaceExactly(
  source,
  '\t\t\t\tsandboxMode: config.sandbox_mode ?? "read-only",',
  '\t\t\t\tsandboxMode: config.permissions ? null : config.sandbox_mode ?? "read-only",\n\t\t\t\tpermissionProfile: config.permissions ?? null,',
  1,
  'trace metadata',
);

if (!verifyPatched(source)) {
  throw new Error('Promptfoo adapter did not produce the expected permission-profile payload. Refusing to write a partial patch.');
}
writeFileSync(providerPath, source, 'utf8');
process.stdout.write(`Applied Codex app-server permission-profile adapter to ${providerPath}\n`);
