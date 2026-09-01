# Interactive subagents

The implementation lives in a separate repository and is not vendored into `pi-config`:

- **Maintained fork:** [gpmarques/pi-interactive-subagents](https://github.com/gpmarques/pi-interactive-subagents)
- **Upstream lineage:** [amosblomqvist/pi-interactive-subagents](https://github.com/amosblomqvist/pi-interactive-subagents)

## Reviewed fork evidence

The behavioral facts in this stub were source-verified on **2026-09-01** against the exact fork endpoint [`eef62f9672b1e8fac4cf4ffff499ba304f0ce79f`](https://github.com/gpmarques/pi-interactive-subagents/commit/eef62f9672b1e8fac4cf4ffff499ba304f0ce79f), whose commit timestamp is **2026-08-31T21:47:21-03:00**. At that endpoint, package metadata reports version 3.7.2, still credits the upstream repository, and declares `@earendil-works/pi-coding-agent`, `@earendil-works/pi-tui`, and `typebox` as `"*"` peer dependencies. The reviewed implementation contains the fork-specific tmux/Herdr lifecycle and pinned web-capability policy described below. This commit is the reproducible evidence boundary, not a claim about later branch state.

Fresh no-provider/no-live verification at this endpoint passed unit 205/205 across 38 suites and top-level hermetic/offline 38/38. A six-runtime bundled-profile capability check passed 1/1 under an isolated temporary exact-pin configuration with installed Pi 0.84.4; it made no model or web call and did not mutate global settings. Historical provider-backed and live-surface evidence remains documented in the fork and was not rerun for this documentation update.

It provides asynchronous Pi subagents on tmux or Herdr terminal surfaces. Subagents can run concurrently, report live status, ask the orchestrator questions, receive completion results through parent follow-up turns, and be messaged, resumed, or killed by a persistent parent-scoped name. Agent profiles use explicit tool and nested-spawn allowlists; completed Pi sessions can resume only through their current parent's exact-name registry and validated saved sandbox.

## Install the reviewed fork

Pi packages execute code with the user's privileges. Review the pinned source before installing it. With Pi 0.84.4, use the command for the intended scope:

```bash
# User scope (~/.pi/agent/settings.json)
pi install git:github.com/gpmarques/pi-interactive-subagents@eef62f9672b1e8fac4cf4ffff499ba304f0ce79f

# Project scope (.pi/settings.json); run from the project root
pi install git:github.com/gpmarques/pi-interactive-subagents@eef62f9672b1e8fac4cf4ffff499ba304f0ce79f -l
```

A commit-pinned git registration is reconciled, but never advanced, by `pi update --extensions`, `pi update --all`, or targeted `pi update`. Moving to another revision requires reviewing it and explicitly replacing the ref with `pi install ...@<new-reviewed-commit>`.

Switching the existing user-level local-path registration to this git pin is a separate source migration, not part of web-access normalization. Stop Pi, enter the registered checkout, and take a timestamped backup of both the effective settings and effective npm root. Local and git sources have different identities, so removal of the local registration is required:

```bash
set -euo pipefail
cd /path/to/existing/pi-interactive-subagents
FORK_CHECKOUT=$(pwd -P)
export EFFECTIVE_PI_AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
STAMP=$(date +%Y%m%d-%H%M%S)
export BACKUP="$EFFECTIVE_PI_AGENT_DIR/backups/interactive-subagents-source-$STAMP"
mkdir -p "$BACKUP"
cp -p "$EFFECTIVE_PI_AGENT_DIR/settings.json" "$BACKUP/settings.json"
cp -a "$EFFECTIVE_PI_AGENT_DIR/npm" "$BACKUP/npm"
printf 'Backup: %s\n' "$BACKUP"

pi remove "$FORK_CHECKOUT"
pi install git:github.com/gpmarques/pi-interactive-subagents@eef62f9672b1e8fac4cf4ffff499ba304f0ce79f
```

Rollback is valid only in the same maintenance window with no intervening settings/package changes. Stop Pi and use the complete safe staged restore procedure under **Researcher web access** below with the concrete `interactive-subagents-source-<timestamp>` backup path instead of the web-access backup path. The snapshot restores both package registrations and npm state, so do **not** run a preliminary `pi remove`; the referenced local checkout was not deleted. That procedure validates and stages the complete snapshot, atomically renames the current files aside, verifies activation, and puts the pre-rollback state back if activation or verification fails.

## No bundled parent shell guard

`pi-config` no longer supplies a local shell-guard extension. Independently of that removal, the reviewed fork's restricted Pi children launch with `--no-extensions` and explicit tool/extension allowlists, so a separately installed parent extension would not be inherited. Bundled profiles listing `bash` use Pi's built-in tool without a fork-provided guard. Only `researcher` lists the fork's distinct `safe_bash` tool; no other bundled profile receives it. Parent-process shell protection must not be described as subagent protection.

## Researcher web access

At the reviewed endpoint, the fork's bundled `researcher` is the only bundled profile with web access. Its profile tools are exactly `web_search`, `fetch_content`, `get_search_content`, `source_check`, and `safe_bash`; the normal child-only `ask_question` support is added by the subagent runtime. Every other bundled profile omits all four web tools, including `worker`, which delegates external research to `researcher`.

The implementation is not supplied by this stub. The common migration target is the global Pi agent directory: `PI_CODING_AGENT_DIR` when explicitly set, otherwise `~/.pi/agent`. When an explicitly requested or profile-defined child cwd contains `<cwd>/.pi/agent`, however, that resolver-specific directory wins for that child and must independently contain both `<cwd>/.pi/agent/settings.json` with the exact selector and `<cwd>/.pi/agent/npm/node_modules/pi-web-access` with the pinned package. This custom nested `agent` directory is **not** Pi's standard project-local `-l` package scope: `-l` writes `<cwd>/.pi/settings.json` and `<cwd>/.pi/npm`, which this resolver does not read. Trusted standard project-scoped web-package semantics remain unsupported.

For the currently verified lone global string registration, use Pi 0.84.4's non-destructive same-identity replacement. The snippet initializes `EFFECTIVE_PI_AGENT_DIR` to the common global target; for a child that selects a custom `<cwd>/.pi/agent`, replace that assignment with the custom directory's absolute path and repeat the entire backup/install/verification procedure independently. Stop all Pi parents/children, then back up both the effective settings and full effective npm root before installing:

```bash
set -euo pipefail
export EFFECTIVE_PI_AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
STAMP=$(date +%Y%m%d-%H%M%S)
export BACKUP="$EFFECTIVE_PI_AGENT_DIR/backups/pi-web-access-$STAMP"
mkdir -p "$BACKUP"
cp -p "$EFFECTIVE_PI_AGENT_DIR/settings.json" "$BACKUP/settings.json"
cp -a "$EFFECTIVE_PI_AGENT_DIR/npm" "$BACKUP/npm"
printf 'Backup: %s\n' "$BACKUP"

PI_CODING_AGENT_DIR="$EFFECTIVE_PI_AGENT_DIR" pi install npm:pi-web-access@0.27.0

node <<'NODE'
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const root = process.env.EFFECTIVE_PI_AGENT_DIR;
const expected = "npm:pi-web-access@0.27.0";
const settingsPath = path.join(root, "settings.json");
const settings = JSON.parse(fs.readFileSync(settingsPath, "utf8"));
function identifiesPiWebAccess(source) {
  if (source.startsWith("npm:")) return /^npm:pi-web-access(?:@|$)/.test(source);
  const withoutRef = source.replace(/[?#].*$/, "").replace(/@[^/@]*$/, "");
  const basename = withoutRef.replace(/[\\/]+$/, "").split(/[\\/:]/).at(-1)?.replace(/\.git$/, "");
  if (basename === "pi-web-access") return true;
  if (/^(?:git:|https?:|ssh:)/.test(source)) return false;
  try {
    const local = path.resolve(path.dirname(settingsPath), source);
    const manifest = fs.statSync(local).isDirectory() ? path.join(local, "package.json") : local;
    return JSON.parse(fs.readFileSync(manifest, "utf8")).name === "pi-web-access";
  } catch { return false; }
}
const matches = (settings.packages ?? []).filter((entry) => {
  const source = typeof entry === "string" ? entry : entry?.source;
  return typeof source === "string" && identifiesPiWebAccess(source);
});
assert.equal(matches.length, 1, "expected one pi-web-access registration of any source type");
assert.equal(matches[0], expected, "registration must be the exact unfiltered string pin");
const manifest = JSON.parse(fs.readFileSync(
  path.join(root, "npm/node_modules/pi-web-access/package.json"),
  "utf8",
));
assert.equal(manifest.name, "pi-web-access");
assert.equal(manifest.version, "0.27.0");
console.log("verified exact selector and installed pi-web-access@0.27.0");
NODE
```

This is verified for the current lone unpinned string registration. It is not a generic cleanup for duplicates or object/filter entries; if that precondition changes, stop and review settings rather than using destructive remove/install normalization. Exact npm pins are skipped by `pi update --extensions` and `pi update --all`; plain `pi update` updates Pi itself. No `pi update` form advances or repairs this pin.

After verification, restart the parent and spawn a fresh researcher; never resume an old child across this migration. Keep the printed backup path. Roll back only in the same maintenance window with no other package changes. Stop Pi, set `EFFECTIVE_PI_AGENT_DIR` to the directory that was migrated (the common global directory or a custom `<cwd>/.pi/agent`), and replace the placeholder below with the concrete printed backup path:

```bash
set -euo pipefail
export EFFECTIVE_PI_AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
BACKUP="$EFFECTIVE_PI_AGENT_DIR/backups/pi-web-access-YYYYMMDD-HHMMSS"
case "$BACKUP" in
  ""|*YYYYMMDD-HHMMSS*) echo "Set BACKUP to the concrete printed backup path" >&2; exit 1 ;;
esac

test -d "$EFFECTIVE_PI_AGENT_DIR"
test -d "$BACKUP" && test ! -L "$BACKUP"
EFFECTIVE_PI_AGENT_DIR=$(cd "$EFFECTIVE_PI_AGENT_DIR" && pwd -P)
BACKUP=$(cd "$BACKUP" && pwd -P)
case "$BACKUP/" in
  "$EFFECTIVE_PI_AGENT_DIR/backups/"*) ;;
  *) echo "BACKUP must be a concrete snapshot below $EFFECTIVE_PI_AGENT_DIR/backups" >&2; exit 1 ;;
esac
test -f "$BACKUP/settings.json" && test -r "$BACKUP/settings.json" && test ! -L "$BACKUP/settings.json"
test -d "$BACKUP/npm" && test ! -L "$BACKUP/npm"

audit_paths() {
  SNAPSHOT_SETTINGS="$1" SNAPSHOT_NPM="$2" node <<'NODE'
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const settingsPath = process.env.SNAPSHOT_SETTINGS;
const npmRoot = process.env.SNAPSHOT_NPM;
const regular = (file) => fs.lstatSync(file).isFile() && !fs.lstatSync(file).isSymbolicLink();
const directory = (dir) => fs.lstatSync(dir).isDirectory() && !fs.lstatSync(dir).isSymbolicLink();
assert(regular(settingsPath), "settings.json must be a regular file");
const settings = JSON.parse(fs.readFileSync(settingsPath, "utf8"));
assert(Array.isArray(settings.packages), "settings.json must contain a packages array");
assert(directory(npmRoot), "complete npm backup directory is missing");
assert(regular(path.join(npmRoot, "package.json")), "npm/package.json is missing");
assert(regular(path.join(npmRoot, "package-lock.json")), "npm/package-lock.json is missing");
assert(directory(path.join(npmRoot, "node_modules")), "npm/node_modules is missing");
const webRoot = path.join(npmRoot, "node_modules/pi-web-access");
const webManifest = path.join(webRoot, "package.json");
assert(directory(webRoot), "pi-web-access package directory is missing");
assert(regular(webManifest), "pi-web-access package manifest is missing");
const web = JSON.parse(fs.readFileSync(webManifest, "utf8"));
assert.equal(web.name, "pi-web-access");
assert.equal(web.version, "0.27.0");
NODE
}

audit_paths "$BACKUP/settings.json" "$BACKUP/npm"
RESTORE_ID="$(date +%Y%m%d-%H%M%S)-$$"
STAGE_SETTINGS="$EFFECTIVE_PI_AGENT_DIR/.settings.restore-$RESTORE_ID"
STAGE_NPM="$EFFECTIVE_PI_AGENT_DIR/.npm.restore-$RESTORE_ID"
OLD_SETTINGS="$EFFECTIVE_PI_AGENT_DIR/.settings.before-restore-$RESTORE_ID"
OLD_NPM="$EFFECTIVE_PI_AGENT_DIR/.npm.before-restore-$RESTORE_ID"
FAILED_SETTINGS="$EFFECTIVE_PI_AGENT_DIR/.settings.failed-restore-$RESTORE_ID"
FAILED_NPM="$EFFECTIVE_PI_AGENT_DIR/.npm.failed-restore-$RESTORE_ID"
for path in "$STAGE_SETTINGS" "$STAGE_NPM" "$OLD_SETTINGS" "$OLD_NPM" "$FAILED_SETTINGS" "$FAILED_NPM"; do
  test ! -e "$path"
done

# These copies stage the complete restore on the live targets' filesystem.
cp -p "$BACKUP/settings.json" "$STAGE_SETTINGS"
cp -a "$BACKUP/npm" "$STAGE_NPM"
audit_paths "$STAGE_SETTINGS" "$STAGE_NPM"

test -f "$EFFECTIVE_PI_AGENT_DIR/settings.json" && test ! -L "$EFFECTIVE_PI_AGENT_DIR/settings.json"
test -d "$EFFECTIVE_PI_AGENT_DIR/npm" && test ! -L "$EFFECTIVE_PI_AGENT_DIR/npm"
rollback_activation() {
  reason="$1"
  set +e
  test ! -e "$EFFECTIVE_PI_AGENT_DIR/settings.json" || mv "$EFFECTIVE_PI_AGENT_DIR/settings.json" "$FAILED_SETTINGS"
  failed_settings_status=$?
  test ! -e "$EFFECTIVE_PI_AGENT_DIR/npm" || mv "$EFFECTIVE_PI_AGENT_DIR/npm" "$FAILED_NPM"
  failed_npm_status=$?
  mv "$OLD_SETTINGS" "$EFFECTIVE_PI_AGENT_DIR/settings.json"
  old_settings_status=$?
  mv "$OLD_NPM" "$EFFECTIVE_PI_AGENT_DIR/npm"
  old_npm_status=$?
  set -e
  if (( failed_settings_status || failed_npm_status || old_settings_status || old_npm_status )); then
    echo "CRITICAL: restore activation failed and automatic rollback was incomplete: $reason" >&2
  else
    echo "Restore rejected; original working state was put back: $reason" >&2
  fi
  return 1
}

# Pi is stopped; each same-filesystem mv is an atomic rename.
mv "$EFFECTIVE_PI_AGENT_DIR/settings.json" "$OLD_SETTINGS"
if ! mv "$EFFECTIVE_PI_AGENT_DIR/npm" "$OLD_NPM"; then
  if ! mv "$OLD_SETTINGS" "$EFFECTIVE_PI_AGENT_DIR/settings.json"; then
    echo "CRITICAL: live npm could not be moved and settings rollback also failed" >&2
  fi
  echo "Could not move live npm aside; restore was not activated" >&2
  exit 1
fi
if ! mv "$STAGE_SETTINGS" "$EFFECTIVE_PI_AGENT_DIR/settings.json"; then
  rollback_activation "settings activation failed" || exit 1
fi
if ! mv "$STAGE_NPM" "$EFFECTIVE_PI_AGENT_DIR/npm"; then
  rollback_activation "npm activation failed" || exit 1
fi
if ! audit_paths "$EFFECTIVE_PI_AGENT_DIR/settings.json" "$EFFECTIVE_PI_AGENT_DIR/npm"; then
  rollback_activation "restored-state verification failed" || exit 1
fi

printf 'Restore verified. Previous settings: %s\nPrevious npm: %s\n' "$OLD_SETTINGS" "$OLD_NPM"
# Optional only after reviewing the verified restore and the paths printed above:
# rm -f -- "$OLD_SETTINGS"
# rm -rf -- "$OLD_NPM"
```

The live npm root is never deleted before the backup and staged copy pass validation. Failed activation or restored-state verification moves the attempted restore aside and renames the original working state back into place. A later rollback would overwrite unrelated settings or packages; take a new backup instead.

Restricted children still launch with ambient discovery disabled (`--no-extensions`) and an explicit `--tools` allowlist. The fork requires **exactly one unfiltered string** `"npm:pi-web-access@0.27.0"` in the effective child agent directory's `settings.json`, then resolves only `<agent-dir>/npm/node_modules/pi-web-access`. The installed manifest must also report exactly `pi-web-access@0.27.0`. An unpinned selector, range, wrong pin, object/filter entry, duplicate, or any second registration that could identify `pi-web-access` fails closed.

The resolver reads the package's single concrete `pi.extensions` entry and requires the four canonical tools to remain enabled and unrenamed in `web-search.json`. Package, manifest, entrypoint, settings, and config paths must be canonical and contained; symlinks at those checked paths are rejected. It neither scans unrelated global packages nor falls back to a stale package beside Pi's installation.

Before creating any researcher terminal surface, the fork starts a bounded fresh Pi RPC process in the exact child cwd and effective agent/package environment. It uses offline/no-session mode, `--no-extensions`, the exact four-tool allowlist, the canonical entrypoint, and a private inspector; only RPC state is queried. Pi's active tools must equal all four canonical names. Extension errors, zero/partial/renamed registration, malformed or unavailable state, nonzero exit, or the 5-second timeout fail closed and clean up the detached process group and nonce-bound temporary snapshot. This creates no persistent session or prompt and performs no model/provider or web call.

## Resume and migration implications

Saved restricted loadouts are validation records, not copies of runnable old code. They retain the canonical entrypoint path/digest, package root/name/version and manifest digest, and complete/relevant `web-search.json` identity. Resume verifies those recorded fields before the same offline probe and again afterward; drift or a legacy record missing required identity fails before creating a surface.

Updating the fork to `eef62f9`, changing the `pi-web-access` selector/package, or changing its configuration requires a **fresh child**. A completed child created against the older fork is expected to fail resume after the fork entrypoint digest changes. After migration, restart the parent Pi process and spawn a new researcher rather than resuming an old one. This focused guarantee does not hash the complete package/dependency tree or npm lock, so same-version helper or dependency mutation that leaves the recorded fields unchanged is outside the resume-identity guarantee.
