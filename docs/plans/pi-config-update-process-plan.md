# Proposal: Package-first Pi configuration updates with safe lifecycle tooling

**Status:** Proposed; planning only

**Evidence date:** 2026-08-30

**Validated Pi version:** 0.84.4

## Executive decision

Adopt a **hybrid, package-first design**:

1. Make this repository an explicit Pi package and register it as a **filtered local-path package** on the workstation where the repository is edited. Pi then loads selected resources directly from this checkout; a source edit, rename, or removal becomes effective after `/reload`, without copying or mirror deletion.
2. Support an **unpinned git package** for other machines. `pi update --extension <source>` can advance its checkout and reinstall root npm dependencies, but it is not the primary local-development update path.
3. Add a small repository-owned lifecycle CLI for read-only status/doctor checks, opt-in non-npm dependency setup, one-time migration of existing copies, backups, and rollback. It must **not** maintain a second steady-state copy of tracked resources.
4. Store repository-owned generated state outside package source trees, rooted at `PI_CODING_AGENT_DIR`: browser profiles, Python environments, setup stamps, and backups must survive package checkout replacement and must never enter the repository.

The three README-only external stubs are catalogue references, not package resources. In particular, if adopted, `pi-web-access` is installed and updated as a separately managed external Pi package; this repository's manifest and lifecycle CLI must not own its implementation, dependencies, configuration, credentials, or state.

This preserves Pi's package and resource-filter conventions while filling the gaps Pi does not cover: local package updates, existing-copy collisions, non-npm dependencies, generated state, migration, and rollback.

`pi update` alone is **not sufficient** for this repository:

- Pi 0.84.4's bare `pi update` updates Pi itself, not packages.
- Local-path packages are live references and are omitted from package update candidates; Pi neither copies them nor installs their dependencies.
- Git packages are updated, but a changed checkout is reset and cleaned with `git clean -fdx`; ignored `.venv`, profiles, caches, and other in-checkout state are deleted. Pi then installs only root npm dependencies.
- Pinned git refs are reconciled to that exact ref, not advanced; pinned npm versions are skipped.
- Pi does not migrate manually copied resources, detect same-logical-resource collisions at different paths, run Python/Chromium/system dependency hooks, or create configuration backups.

## Goal

### Target outcome

A user can update the effective global Pi configuration without selective `cp` commands and without risking unrelated global resources:

- On the editing workstation: update or edit this checkout, reconcile dependencies if their inputs changed, then run `/reload`.
- On another machine: update the configured git package, reconcile non-npm dependencies, then run `/reload`.
- At any time: inspect selection, collisions, drift, setup health, and pending actions before mutation.
- Roll back package registration and migrated copies from an explicit backup.

### User-visible proof

After adopting the current installed subset:

- `pi list` shows one filtered `pi-config` package in addition to the four existing unrelated packages.
- `ask-user-question`, `prompt-snippets`, `analyze-sessions`, `pdf-reader`, and `youtube-transcript` each load once from this package.
- Editing a selected source file changes behavior after `/reload`; no copy command is needed.
- Removing a selected path from the package manifest, or disabling it through `pi config`, removes it from the next resource load without deleting anything elsewhere in the global config.
- Existing unrelated packages, `extensions/herdr-agent-state.ts`, and unrelated global skills remain untouched.

### Quantitative checks

- Zero selected tracked files are duplicated under both the package source and top-level global resource directories after migration.
- Zero paths outside the explicit migration set change.
- Every mutating lifecycle command has a no-write dry run and a restorable backup.
- Repeating setup or migration after success is idempotent.
- Package discovery yields exactly 5 local extension entry points and 4 local skills from the catalogue; it yields 0 of the 3 external README stubs and 0 deprecated resources.
- Root dependency aggregation covers exactly the 2 local nested extension manifests and no external-stub package.

## Scope

### In scope

- A root Pi package manifest with an explicit active resource catalogue.
- Filtered global registration and selective enablement.
- Local-path and git-source operating modes.
- Root npm dependency resolution for the two local nested manifests, current Pi import namespaces, and opt-in setup/checks for Chromium, Python, `agent-browser`, `yt-dlp`, and `ffmpeg`.
- State-root correction for the local browser profile and PDF virtual environment.
- Read-only `status`, `doctor`, and dry-run planning.
- Transactional one-time migration from manually copied resources, including duplicate detection, backup, rollback, and generated-state relocation.
- Documentation, automated tests, and CI on supported desktop platforms.

### Out of scope

- Publishing this personal repository to npm.
- Automatically enabling every catalogue resource.
- Vendoring the external `interactive-subagents`, `observational-memory`, or `web-access` repositories.
- Installing, updating, configuring, migrating, or validating `pi-web-access` or another package named by an external stub; those remain separately managed Pi packages.
- Loading anything under `deprecated/`.
- Managing unrelated Pi settings, credentials, sessions, packages, extensions, skills, or `~/.agents/skills`.
- Installing Homebrew or another system package manager, changing shell startup files, or silently downloading Chromium/Python tools.
- A daemon, file watcher, automatic `/reload`, or mutation of a running Pi process.
- A general-purpose dotfile synchronizer.

## Confirmed current state

### Repository

- The README explicitly says this is not one package and prescribes selective copies, separate `npm install`, and `/reload` for local resources (`README.md:9-44,56-66`). It directs external-stub users to authoritative upstream installation guidance instead of copying a stub (`README.md:46-54`).
- Dependency setup is resource-specific: two active nested npm manifests, optional Chromium, external `agent-browser`, system tools, and a PDF `.venv` (`README.md:92-123`; `extensions/bash-guard/package.json:1-11`; `extensions/browser/package.json:1-13`).
- The system map identifies the manual-integration loop and confirms there is no root package manifest, installer, test harness, or CI (`docs/system-maps/pi-config-overview.md:10-25,48-71`).
- The local active catalogue is five extension entry points and four skills. Three additional extension directories—`interactive-subagents/`, `observational-memory/`, and `web-access/`—are README-only external pointers and not local implementations (`README.md:68-90`; `extensions/interactive-subagents/README.md`; `extensions/observational-memory/README.md`; `extensions/web-access/README.md`).
- Three active extension entry points still import the old `@mariozechner/*` namespace, while two use `@earendil-works/*`; packaging should not preserve that ambiguity (`extensions/ask-user-question.ts:1`; `extensions/bash-guard/index.ts:1-4`; `extensions/browser/index.ts:37`; `extensions/custom-header.ts:11-13`; `extensions/prompt-snippets/index.ts:21-22`).
- Browser state currently defaults to a literal `~/.pi/agent/extensions/browser/.profile`, bypassing `PI_CODING_AGENT_DIR` (`extensions/browser/index.ts:30,135`). PDF commands expect `SKILL_DIR/.venv` (`skills/pdf-reader/SKILL.md:12-21`).
- The repository ignores `node_modules`, `.venv`, Python caches, and runtime data, so an installed copy can contain untracked state not represented by the catalogue (`.gitignore:1-31`).

### Effective global Pi configuration

Read-only inspection of the effective root from `PI_CODING_AGENT_DIR=/Users/guilhermemarques/.pi/agent` established:

- Global settings currently configure four unrelated packages: `pi-mcp-adapter`, `pi-autoresearch`, `pi-transcribe`, and local `pi-interactive-subagents` (`/Users/guilhermemarques/.pi/agent/settings.json:7-12`). They must remain byte-for-byte equivalent except for appending/replacing the one `pi-config` package entry.
- Manually copied catalogue resources are:
  - extensions: `ask-user-question.ts`, `prompt-snippets/`;
  - skills: `analyze-sessions/`, `pdf-reader/`, `youtube-transcript/`.
- Every inspected tracked file in those copies currently has the same SHA-256 as its repository counterpart.
- Generated installed state exists under those copies: `skills/analyze-sessions/scripts/__pycache__/` and `skills/pdf-reader/.venv/`.
- `extensions/herdr-agent-state.ts` and many other skills are unrelated resources and are outside ownership.
- `pi list` resolves the four existing package sources successfully. There is no existing `pi-config` package entry.

Do not encode the absolute username-specific path in implementation. All tooling must derive the root as described below.

### Verified Pi behavior

- Pi package docs support local, git, and npm sources; local paths are registered without copying (`docs/packages.md:18-54,107-114`).
- A package may explicitly list resources, and global settings may narrow them with exact `+path`/`-path` filters or `pi config` (`docs/packages.md:116-133,190-220`; `docs/settings.md:280-318`).
- Pi auto-discovers top-level global copies independently of packages (`docs/extensions.md:109-150`; `docs/skills.md:20-40`). Therefore a copied path and a package path are not deduplicated merely because they implement the same logical tool or skill.
- Pi skill-name collisions warn and keep the first (`docs/skills.md:177-189`); extension duplication can register duplicate/overriding tools, commands, and lifecycle hooks. Existing copies must be removed or disabled before reload.
- `/reload` reloads extensions, skills, prompts, themes, and context; extension runtime shutdown/start occurs during reload (`docs/extensions.md:1303-1325`). Package commands run in a separate process and do not reload an already running session.
- Verified CLI help for 0.84.4 says:
  - `pi update` defaults to self-update;
  - `pi update --extensions` updates packages;
  - `pi update --extension <source>` updates one package;
  - `pi config` is the resource-enable/disable TUI;
  - `pi install/remove` use global settings unless `-l` is passed.
- Embedded 0.84.4 package-manager source confirms:
  - local install only validates path existence (`.../dist/core/package-manager.js.map`, embedded `src/core/package-manager.ts:1005-1024`);
  - update candidates include unpinned npm and git, but not local paths (`:1059-1148`);
  - git checkout changes run `reset --hard`, `clean -fdx`, then root dependency install (`:1831-1957`);
  - git dependency install defaults to `npm install --omit=dev` (`:1772-1778`);
  - resources are deduplicated by canonical filesystem path, not logical resource identity (`:2555-2593`).

## Alternatives considered

Scores are relative (5 is best). “Drift/removal” means detecting or eliminating divergence between catalogue and effective configuration.

| Criterion | Pi package only | Repository copy-sync | Recommended hybrid |
|---|---:|---:|---:|
| Safety for unrelated globals | 4 | 2 | 5 |
| Routine simplicity | 5 local / 4 git | 2 | 4 |
| Determinism | 4 | 5 | 5 |
| Selective adoption | 5 | 5 | 5 |
| Dependency handling | 2 | 4 | 5 |
| Drift/removal handling | 4 local / 3 git | 5 | 5 |
| Rollback | 2 | 4 | 5 |
| Portability | 4 | 3 | 4 |
| Maintenance burden | 5 | 2 | 3 |
| Fit with Pi conventions | 5 | 2 | 5 |

### Option 1: Pi package only

#### Design

Add a root `package.json` with explicit `pi.extensions` and `pi.skills`; register the checkout locally or install the git URL; use `pi config` for selection.

#### Local-path source

- **Strength:** no propagation step exists: Pi reads source directly. Tracked updates/removals appear after `/reload`.
- **Strength:** no mirror deletion can affect unrelated resources.
- **Limitation:** `pi update` intentionally does nothing to local packages. Git pull/edit remains the user's repository workflow.
- **Limitation:** local install does not run npm or other dependency setup.
- **Limitation:** deleting/moving the checkout breaks the package path.

#### Git source

- **Strength:** unpinned git sources can advance through `pi update --extension <source>` or `pi update --extensions`; root npm dependencies reinstall.
- **Strength:** portable to a second machine without a pre-existing checkout.
- **Limitation:** checkout changes use destructive reset and `git clean -fdx`; all ignored in-checkout generated state is disposable.
- **Limitation:** pinned refs do not advance. A new pinned ref must be installed explicitly.
- **Limitation:** only root npm dependencies are automatic. Chromium, Python environments, system commands, and repository-owned runtime state are not.

#### npm source

Technically supported, with unpinned versions updateable and exact versions skipped, but it adds publishing/versioning work and contradicts the repository's current private/personal role. Defer it.

#### Manifest, filtering, and collisions

An explicit manifest can exclude external README stubs and `deprecated/`, while settings filters preserve selection. However, existing top-level copies remain independently discoverable; canonical-path deduplication cannot identify them as the same logical resource. A package-only change lacks a safe migration and rollback path.

#### Conclusion

Use Pi packages as the steady-state loading mechanism, but not as the whole operational solution.

### Option 2: Repository-owned exact-mirror copy sync

#### Viable design if chosen

A cross-platform Node CLI would maintain an explicit resource inventory and a ledger under `$PI_CODING_AGENT_DIR/state/pi-config/install.json`. It would provide:

- `status`, `diff`, and default dry-run output;
- per-resource selection;
- content hashes for source/destination/last-applied state;
- staging and backups before replacement;
- exact-mirror deletion only for paths recorded as owned by the previous successful run;
- generated-state exclusions and relocation;
- dependency hooks and setup stamps;
- optimistic settings/file checks, rollback journal, and same-filesystem atomic rename where available.

It must never mirror the whole `extensions/` or `skills/` root, infer ownership from matching names alone, or delete unrecorded files. Removed catalogue resources could only delete their previously recorded destination roots after backup. Unknown or locally modified content would fail closed.

#### Tradeoffs

This offers strong copied-snapshot determinism and can work after the source checkout disappears, but it duplicates Pi's resource-selection model and retains the hardest parts of the current workflow: copied trees, ownership ledgers, deletion semantics, generated-file exceptions, and collision windows. A mistake has a much larger blast radius than a package reference. It is not recommended unless a future requirement explicitly demands standalone copied installs with no registered package source.

### Option 3: Hybrid package plus lifecycle tooling — selected

Use Pi for resource discovery, filtering, git/npm package mechanics, and reload. Use repository tooling only where Pi has verified gaps:

- preflight/status/doctor;
- selection-aware dependency setup;
- external state root management;
- migration of historical copies;
- backups and rollback;
- a safe wrapper that distinguishes local from git update semantics.

There is no ongoing file sync, no exact-mirror deletion, and no ownership claim over unrelated global roots.

## Selected architecture

### Package and state flow

```text
tracked pi-config checkout or Pi-managed git clone
  ├─ package.json: explicit active catalogue + dependency metadata
  ├─ selected by one filtered settings.packages entry
  ├─ loaded directly by Pi
  └─ lifecycle CLI
       ├─ reads package manifest + effective settings
       ├─ reports duplicates/setup drift
       ├─ stores generated state below PI_CODING_AGENT_DIR/state/pi-config
       └─ backs migration data up below PI_CODING_AGENT_DIR/backups/pi-config

source change / git package update
  → npm dependency reconciliation when needed
  → explicit non-npm setup when selected and consented
  → status/doctor clean
  → user runs /reload in each active Pi session
```

### Root resolution and directory policy

All new code must use:

```text
agentDir = resolve(
  process.env.PI_CODING_AGENT_DIR
  ?? join(os.homedir(), ".pi", "agent")
)
stateDir = resolve(
  process.env.PI_CONFIG_STATE_DIR
  ?? join(agentDir, "state", "pi-config")
)
backupDir = join(agentDir, "backups", "pi-config")
```

Requirements:

- Resolve and canonicalize paths before ownership checks.
- Reject a configured state/backup path equal to or inside the package source.
- Never follow a symlink out of an owned migration root during enumeration or deletion.
- Keep the browser profile at `stateDir/browser/profile`, the PDF venv at `stateDir/pdf-reader/venv`, and setup hashes at `stateDir/install.json`.
- Treat root/package `node_modules` and Python bytecode caches as disposable. Keep durable browser profiles and venvs outside git package clones.
- Do not create or migrate `pi-web-access` configuration or credential paths; they belong to that separately managed package.
- Create state/backups with user-only permissions where supported; never print sensitive content.

### Root package manifest

Create `package.json` as the single authoritative catalogue. It should be private, ESM, tagged `pi-package`, and explicitly enumerate only:

**Extensions**

- `extensions/ask-user-question.ts`
- `extensions/bash-guard/index.ts`
- `extensions/browser/index.ts`
- `extensions/custom-header.ts`
- `extensions/prompt-snippets/index.ts`

**Skills**

- `skills/analyze-sessions/SKILL.md`
- `skills/pdf-reader/SKILL.md`
- `skills/web-debug/SKILL.md`
- `skills/youtube-transcript/SKILL.md`

The manifest must not use broad `extensions/**` or `skills/**` patterns. This is the enforceable boundary excluding all three external README stubs and `deprecated/`; in particular, `extensions/web-access/README.md` is not a package resource.

Aggregate the runtime dependency sets represented by the two active nested extension manifests at the root and commit a root `package-lock.json`. List Pi-provided current packages (`@earendil-works/pi-coding-agent`, `@earendil-works/pi-tui`, `typebox`, and other imported Pi core packages) as `peerDependencies: { "*" }`, following Pi package guidance. Normalize active imports away from `@mariozechner/*` and `@sinclair/typebox` before relying on that peer contract. Keep both nested manifests temporarily for standalone-resource compatibility; document them as compatibility manifests and add a test that their dependency ranges do not diverge from the root.

Add custom `piConfig` metadata in the same manifest, not a second resource inventory. It should map stable resource IDs to their Pi path, type, setup checks/actions, and durable-state keys. Tests must prove that `pi` and `piConfig` enumerate the same active resources.

### Selection model

- Selection lives in Pi's global `packages` object entry, using exact `+path` filters relative to package root.
- Omitted types do not imply selection during migration; the adoption command writes explicit `extensions`, `skills`, `prompts: []`, and `themes: []` arrays.
- Routine selection changes should use `pi config`; the lifecycle CLI only validates and reports the effective filters after migration.
- The initial migration default should be **derive from currently copied matching resources**, yielding the five-resource current subset. It must print the exact selection before apply.
- No local active catalogue resource is enabled merely because it was added upstream. A manifest addition remains disabled until selected, avoiding surprise tool/context growth.
- README-only stubs are never selectable `pi-config` resources. Installing or selecting `pi-web-access` happens through its own separately managed package entry, which adoption and update must preserve but never create or modify.

Illustrative settings shape (the exact source is chosen during adoption):

```json
{
  "source": "../../Projects/harness-lab/pi-config",
  "extensions": [
    "+extensions/ask-user-question.ts",
    "+extensions/prompt-snippets/index.ts"
  ],
  "skills": [
    "+skills/analyze-sessions/SKILL.md",
    "+skills/pdf-reader/SKILL.md",
    "+skills/youtube-transcript/SKILL.md"
  ],
  "prompts": [],
  "themes": []
}
```

### Dependency policy

| Dependency class | Mechanism | Update behavior |
|---|---|---|
| Root npm runtime dependencies | committed root manifest/lock | Git package install/update is handled by Pi; local checkout uses explicit deterministic reconciliation |
| Chromium binary | opt-in lifecycle setup for selected browser resource | hash/version checked; never downloaded by status/doctor |
| PDF Python venv | state-root venv + locked requirements input | rebuilt/reconciled only with `--apply` when requirements/Python ABI stamp changes |
| `agent-browser` | external command check | never auto-installed; validate compatible version/help |
| `yt-dlp`, `ffmpeg` | external command checks | never auto-install a system package manager |
| Browser profile | state root | migrated/backed up; never overwritten by dependency setup |

Do not use npm lifecycle scripts to download Chromium, create a venv, or install system tools. Pi's git update may invoke npm automatically and should remain bounded to declared JS runtime dependencies. The dependency planner must ignore external stubs and must not inspect, install, update, or reconcile `pi-web-access`.

### Lifecycle CLI contract

Implement a thin Node entry point and testable pure/apply modules. Every mutating command defaults to dry-run and requires `--apply`.

```text
npm run pi-config -- status [--json]
npm run pi-config -- doctor [--json]
npm run pi-config -- setup [--resource <id> ...] [--apply]
npm run pi-config -- adopt --source <local-path|git-source> [--resource <id> ...] [--from-current] [--apply]
npm run pi-config -- update [--apply]
npm run pi-config -- rollback <backup-id> [--apply]
```

#### `status`

Read only. Report:

- Pi version and whether verified semantics still match 0.84.4 expectations;
- resolved agent/source/state roots;
- package registration source and exact selected local resources;
- source mode: local, unpinned git, pinned git, or npm;
- missing manifest paths and filters referencing removed paths;
- external-stub packages, if mentioned at all, as separately managed and outside lifecycle ownership;
- top-level copied collisions, classified as identical, modified, generated-only, or unknown-extra;
- root npm lock/install stamp and selected non-npm setup stamps;
- next action and whether `/reload` is required.

Never contact the network by default. JSON output must contain paths and statuses, not secret values.

#### `doctor`

Read only. In addition to `status`, verify executable availability/version, state permissions, manifest consistency, package-source existence, and import/load prerequisites for the nine local manifest resources. Exit nonzero for a selected local resource that cannot load; warn for unselected local optional resources. Do not health-check providers, credentials, or implementation details belonging to external-stub packages.

#### `setup`

Print planned subprocesses and state writes by default. With `--apply`, reconcile only selected/requested dependency groups using argv spawning with `shell: false`. Honor the effective `npmCommand` wrapper where compatible. Record input hashes only after success. A failed hook leaves the prior stamp and durable state intact.

#### `adopt`

One-time transactional migration:

1. Acquire an operation lock in `stateDir`; reject a live lock and provide explicit stale-lock recovery.
2. Resolve `PI_CODING_AGENT_DIR`, source, effective settings, catalogue, and selection.
3. Require a clean preflight: package source exists, filters are valid, dependencies are satisfiable, and every collision is classified.
4. Default to `--from-current`; print all paths that will be registered, backed up, relocated, removed from top-level discovery, or preserved.
5. Abort on a tracked-file difference or unknown extra unless the user explicitly chooses `--prefer-repo` after reviewing diff output. Never silently overwrite local edits.
6. Create `backupDir/<UTC timestamp>-<short id>/` containing:
   - original `settings.json` with original mode;
   - complete selected collision roots, including generated files;
   - `manifest.json` with source/destination hashes, selection, Pi version, and operation journal.
7. Relocate known durable generated state to `stateDir` without copying it into source. If a target state path already exists and differs, abort and require a user choice.
8. Register/update exactly one filtered package entry while preserving package order and all unrelated JSON keys. Use same-directory temp write, flush, mode preservation, optimistic original-hash check, and atomic replace where supported.
9. Remove only the selected collision roots already captured in the backup. Do not scan/delete sibling global resources.
10. Run doctor. On any failure, restore settings and moved roots from the journal before releasing the lock.
11. Print `/reload`; never reload automatically.

For a local source, normalize the settings path relative to `settings.json` as Pi does. For git, preserve Pi's accepted source string. If calling `pi install` is used internally, verify the post-command settings diff before continuing and roll it back on failure.

#### `update`

- **Local source:** do not call `pi update`; explain that tracked code is already live. Reconcile dependency input changes, run doctor, and print `/reload`.
- **Unpinned git source:** with `--apply`, invoke the exact verified `pi update --extension <configured-source>`, then reconcile non-npm setup, run doctor, and print `/reload`.
- **Pinned git source:** do not imply advancement; report the pin and require an explicit new ref through adoption/install workflow.
- **npm source:** support only if publishing is later approved; exact versions remain pinned.
- Refuse ambiguous duplicate `pi-config` package identities.

#### `rollback`

Dry-run first. Validate backup hashes and current ownership, restore the original settings atomically, restore only the paths recorded in the backup, and preserve post-migration durable state in a new recovery backup rather than deleting it. Print `/reload`.

### Reload guidance

- A package command or filesystem update does not change an already-running Pi session.
- After successful adoption/update/rollback, run `/reload` in every active session that should pick up the change.
- Reload invokes extension shutdown and creates new extension instances. Durable state must be on disk; code after a reload request must not rely on old in-memory state (`docs/extensions.md:1303-1325`).
- If doctor reports an extension load failure or a migration changed native/browser processes, restart Pi instead of repeatedly reloading.

## Migration from the current manual installation

### Recommended initial choice

Adopt the local checkout and exactly the currently copied five resources. Do not enable the other four local resources—`bash-guard`, browser, custom header, or `web-debug`—merely because they are in the catalogue. The three external stubs are not migration candidates; `pi-web-access` remains a separate package choice.

### Proposed operator sequence

```bash
# From the pi-config checkout; all read-only.
npm run pi-config -- status
npm run pi-config -- doctor
npm run pi-config -- adopt --source "$PWD" --from-current

# Explicit mutations only after reviewing the plan.
npm run pi-config -- setup --apply
npm run pi-config -- adopt --source "$PWD" --from-current --apply

# Verify Pi's persisted package view.
pi list

# In every active Pi session.
/reload
```

Post-migration, the old PDF `.venv` is preserved in the backup and either safely relocated after compatibility checks or rebuilt under the state root. Python caches are disposable. If a future copied browser directory is migrated, preserve `.profile` through its explicit state mapping. Do not migrate separately managed `pi-web-access` state. Unknown generated content fails closed.

For a secondary machine:

```bash
pi install https://github.com/gpmarques/pi-config
# Configure only desired resources before the first reload:
pi config
# Then from Pi's reported git package path:
npm run pi-config -- setup --apply
```

Routine git-package update:

```bash
npm run pi-config -- update          # dry-run
npm run pi-config -- update --apply
# then /reload in active Pi sessions
```

Document prominently that bare `pi update` updates Pi itself; it does not update packages.

## Exact proposed repository changes

### New files

- `package.json` — Pi manifest, aggregated dependencies/peers, `piConfig` resource/setup metadata, and npm scripts.
- `package-lock.json` — deterministic root npm graph.
- `scripts/pi-config.mjs` — thin CLI argument parsing, help, exit codes.
- `scripts/lib/pi-config-core.mjs` — root resolution, manifest/settings parsing, selection, collision classification, immutable operation plans.
- `scripts/lib/pi-config-apply.mjs` — lock, backup journal, atomic settings/path operations, rollback.
- `scripts/lib/pi-config-dependencies.mjs` — setup plans, argv execution, stamps, external-command checks.
- `tests/pi-config-core.test.mjs` — manifest, filters, source modes, collision/status behavior.
- `tests/pi-config-migration.test.mjs` — temp-root adoption, fault injection, rollback, unrelated-resource preservation.
- `tests/pi-config-dependencies.test.mjs` — dry-run/no-network behavior, stamps, platform command construction.
- `tests/pi-package-load.test.mjs` — Pi package discovery/load smoke test against an isolated config root.
- `.github/workflows/pi-config.yml` — Linux/macOS/Windows manifest, unit, and non-network package-load checks.

### Modified files

- `README.md` — replace copy-first primary instructions with package-first local/git workflows; retain manual single-resource copying as a clearly unsupported legacy escape hatch if desired.
- `docs/system-maps/pi-config-overview.md` — replace the manual-integration causal path and record package/state/tooling boundaries.
- `extensions/ask-user-question.ts`
- `extensions/bash-guard/index.ts`
- `extensions/custom-header.ts` — normalize current Pi imports.
- `extensions/browser/index.ts` — use the shared `PI_CODING_AGENT_DIR`/state-root policy for its profile.
- `skills/pdf-reader/SKILL.md` — use the state-root venv and platform-correct interpreter location.
- `.gitignore` — ensure only repository-local disposable outputs are ignored; document that durable package state belongs outside the checkout.
- Nested active `extensions/*/package.json` and lockfiles only if needed to align dependency versions with the new root lock; do not remove them until standalone-copy compatibility is explicitly dropped.

No external README stub or deprecated file should be altered merely to make package discovery work; explicit manifest boundaries solve that problem. No package or state named by an external stub should be managed by the `pi-config` lifecycle CLI.

## Staged implementation plan

Each stage should be a reviewable, passing commit.

1. **`build: define the explicit pi-config package boundary`**
   - Add root manifest/lock and exact active resource lists.
   - Normalize active Pi/typebox imports and peer dependency declarations.
   - Add manifest-consistency and isolated discovery tests proving 5 local extensions, 4 local skills, none of the 3 stubs, and no deprecated resources.
2. **`feat: add read-only pi-config status and doctor`**
   - Add root/state resolution, settings parsing, filtered-selection model, source-mode detection, collision classifier, JSON output, and read-only tests.
   - Verify no status/doctor code writes, installs, fetches, or invokes Pi update.
3. **`fix: externalize durable generated package state`**
   - Update local browser profile and PDF venv resolution; do not add state handling for external packages.
   - Add `PI_CODING_AGENT_DIR` and `PI_CONFIG_STATE_DIR` tests, including paths with spaces and Windows path forms.
4. **`feat: reconcile selected dependencies safely`**
   - Add dry-run/apply setup plans, root npm lock handling, optional Chromium/PDF hooks, external executable checks, and content-hash stamps.
   - Keep system package installation advisory only.
5. **`feat: migrate copied resources transactionally`**
   - Add adopt/rollback, operation lock, full backup journal, optimistic settings writes, generated-state mapping, conflict refusal, and fault-injection tests.
   - Prove unrelated settings/resources survive byte-for-byte.
6. **`feat: wrap source-aware package updates`**
   - Implement local/live, unpinned-git, pinned-git, and future npm branches using verified Pi CLI arguments.
   - Add fake-git fixture tests demonstrating ignored checkout state is never used for durability.
7. **`docs: switch pi-config to the package-first operating model`**
   - Update README/system map with migration, selection, update, reload, recovery, platform, and troubleshooting instructions.
8. **`ci: verify package lifecycle on supported platforms`**
   - Add non-mutating CI matrix checks. Do not download Chromium or mutate a real global config in CI.

## Tests and verification

### Automated commands

```bash
npm ci
npm test
npm run check
```

Define `npm test` as Node's built-in test runner over `tests/**/*.test.mjs`. Define `npm run check` to run manifest validation, tests, and an isolated package-load smoke test with `PI_OFFLINE=1` and a temporary `PI_CODING_AGENT_DIR`.

### Required test cases

1. Exact manifest discovery includes only the 9 local active resources: 5 extensions and 4 skills; all 3 external stubs and every deprecated resource are excluded.
2. Package filters enable only exact selected paths; empty prompt/theme arrays enable none.
3. Local registration resolves relative to the global settings directory and local update planning never calls `pi update`.
4. Unpinned git update constructs `pi update --extension <exact configured source>`; pinned refs report no advancement.
5. Bare `pi update` is never emitted by lifecycle tooling.
6. Duplicate top-level copies are detected even though their canonical paths differ.
7. Identical copies, modified tracked files, known generated state, unknown extras, broken symlinks, and symlink escapes are classified correctly.
8. Dry runs leave settings, source, destination, state, backups, mtimes, and subprocess logs unchanged.
9. Adoption preserves unrelated package entries/order, unrelated extensions/skills, unknown settings keys, and file modes.
10. Adoption backs up selected roots completely and removes only journaled collision roots.
11. A settings race, failed dependency hook, failed rename, interrupted operation, or failed doctor triggers deterministic recovery.
12. Rollback restores pre-adoption settings/copies and retains newer durable state in a recovery backup.
13. Repeated setup/adopt/update is idempotent.
14. Git-update fixture runs a `clean -fdx` equivalent and proves all durable test state remains outside the clone.
15. Windows tests use `Scripts/python.exe`; POSIX tests use `bin/python`; paths with spaces are passed as argv, not shell strings.
16. Status/doctor do not expose browser-profile or other sensitive file contents and do not contact the network.
17. Current copied subset migration produces exactly the five-resource selection listed above.
18. Adoption, setup, status, doctor, update, and rollback never select a stub path or create, modify, remove, or health-check separately managed `pi-web-access`; its settings entry may be parsed only as unrelated data to preserve, and its configuration/state are never read.
19. Root dependency aggregation and range-consistency checks cover exactly the two local nested manifests and exclude every external stub.

### Manual acceptance checks

Use a disposable `PI_CODING_AGENT_DIR` first, then the real root only after review:

1. `status`, `doctor`, and `adopt` dry-run show no writes.
2. Apply adoption; `pi list` shows the filtered package plus all four pre-existing packages.
3. Start Pi offline with the disposable root; verify selected tools/skills appear once and unselected catalogue resources do not appear.
4. Change a prompt snippet in the checkout, run `/reload`, and observe the changed snippet without copying.
5. Disable that resource with `pi config`, reload, and observe it disappear while an unrelated global sentinel remains.
6. Run rollback, reload, and confirm the original copied setup returns.
7. For git mode, update a fixture remote, apply update, and confirm code/root npm changes plus preserved external durable state.
8. With a separately managed external-package sentinel in disposable settings, apply adoption/update/rollback and confirm its entry and state remain unchanged.

## Acceptance criteria

The proposal is complete when implementation demonstrates all of the following:

- Package registration is the only steady-state link between this catalogue and Pi; no sync copy is maintained.
- The current five-resource subset migrates without changing unrelated global state.
- Local source changes require only dependency reconciliation when inputs changed and `/reload`.
- Git source updates are explicit, source-targeted, and honest about pins and destructive checkout cleaning.
- Durable/install state survives git package updates because it is outside the clone.
- Resource additions/removals are deterministic through the explicit nine-resource manifest and filters; all three external stubs remain excluded.
- Root dependency aggregation is locked and consistent with exactly the two local nested manifests; external-stub packages contribute no dependencies.
- Separately managed packages, including `pi-web-access`, and their configuration/state remain unchanged by every lifecycle operation.
- Dry-run, status, doctor, backup, rollback, and failure recovery are tested.
- Documentation never tells users that bare `pi update` updates packages.

## Risks and premortem

| Load-bearing assumption / failure mode | Consequence | Mitigation |
|---|---|---|
| Pi package/filter semantics change after 0.84.4 | Wrong resources load or update command changes | Check Pi version, integration-test the installed resolver/CLI contract, warn and fail closed on unsupported semantics |
| Copied and packaged resources coexist for one reload | Duplicate tools, commands, hooks, or first-wins skills | Adoption removes/disables selected collisions before instructing reload; doctor blocks clean status while collisions remain |
| Git update deletes ignored state | Lost browser profile or venv | Durable state is outside clone; test with destructive-clean fixture; backup migration inputs |
| A user modified a copied resource only in global config | Migration silently loses work | Three-way/hash classification, full backup, visible diff, default abort; explicit `--prefer-repo` only |
| Root dependency aggregation diverges from either of the two nested manifests | Local copies and package loads behave differently | Root/nested consistency test; document compatibility period; one lock is authoritative for package mode |
| Settings are edited concurrently by Pi or another process | Lost settings update | Optimistic hash check, operation lock, same-dir atomic replace, original mode/backup, rollback journal |
| A new resource is added and auto-enabled | Unexpected tool/context/security surface | Exact filters and explicit migration selection; additions remain disabled pending user opt-in |
| External setup becomes nonportable | Selected resource fails on Windows/Linux | Pure Node path/argv handling, platform-specific venv executable, advisory system dependencies, OS CI |
| Backup contains sensitive state | Browser/session data exposure | User-only permissions, no content in logs, backups stay local, documented retention and deletion |
| Lifecycle CLI grows into a second package manager | High maintenance and conflicting semantics | Keep Pi authoritative for resource loading/git/npm; prohibit ongoing copy sync and self-update logic |

## Rollback and recovery

- **Adoption failure:** automatic journal replay restores original settings and selected top-level roots. Keep the failed-operation backup for inspection.
- **After successful local adoption:** `rollback <backup-id> --apply`, then `/reload`. This removes/restores only the recorded `pi-config` entry and roots.
- **After a bad local source change:** use the repository's normal git recovery, run setup/doctor, then `/reload`; the global config is not recopied.
- **After a bad unpinned git update:** install a known commit/tag as the new explicit ref or restore the previous settings backup, then setup/doctor and `/reload`. Durable state remains external.
- **If package source disappears:** status reports the missing source; rollback restores copied resources. Do not automatically fall back to stale copies while the package remains configured.
- Never use `git clean`, wholesale global-directory restore, or deletion of unjournaled resources as recovery.

## Open decisions requiring user preference

These do not change the recommendation, but must be chosen before implementation defaults are finalized:

1. **Primary source on this workstation:** recommended default is the current local checkout for immediate edits; choose git if independence from the workspace path matters more.
2. **Initial selection:** recommended default is the five currently copied resources. Decide whether `web-debug` should also be enabled now; it is present in the repo but not in the effective global subset.
3. **Git release policy for secondary machines:** recommended default is unpinned `main` plus explicit update for convenience. Choose commit/tag pins for stronger reproducibility and manual ref advancement.
4. **Conflict policy:** recommended default is abort on any modified tracked copy or unknown extra. Decide whether to expose `--prefer-repo` in v1 or require manual conflict resolution only.
5. **Backup retention:** recommended default is no automatic deletion in v1. A later bounded retention policy needs an explicit age/count preference and separate dry-run cleanup.
6. **Standalone-copy compatibility:** recommended default is retain both nested manifests and legacy manual-copy documentation for one transition period. Decide when they may be removed.
7. **Heavy optional setup:** recommended default is never download Chromium or install PDF dependencies unless that resource is selected and the user passes `--apply`.

## Project Compass

### Starting point

The smallest faithful first milestone is a filtered local package containing only the current five-resource selection, plus read-only status and an isolated package-load test. It exercises the complete path—manifest, settings filter, Pi discovery, source edit, reload—without migration deletion or optional heavy dependencies. All manifest/tests carry forward.

### Search space

- **Held fixed:** Pi remains the resource loader; unrelated globals are out of scope; selection is explicit; no ongoing copied mirror.
- **Allowed choices:** local versus git package source, selected resource set, local non-npm dependency opt-ins, pin strategy.
- **Riskiest unknown:** safe migration of unknown generated/local state from historical copies.

### First experiment

- **Hypothesis:** a filtered local package can load the current five resources exactly once from an isolated config root, and a source change becomes visible after reload without copying.
- **Evidence:** package-manager resolver output, extension/skill provenance, zero duplicate paths, and a changed snippet observed after reload.
- **Gate:** do not implement migration apply or git-update wrapping until this end-to-end baseline passes repeatedly.
