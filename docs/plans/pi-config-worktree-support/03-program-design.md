# Program Design: isolated Git worktrees for spawned tasks

Gate 1 Product and Gate 2 Architecture were approved on 2026-09-01. This is focused Gate 3 rework only; it contains no implementation and no Gate 4 slices.

The implementation baseline is `pi-interactive-subagents` commit `9388cc9634eee84601ce7ee4b7d1cb648040d684` (`fix: preserve subagents across extension reloads`), `pi-config` baseline `c5bfcfd81ee2b386d5c06103264d25307889eef2`, Pi 0.84.4, and Git 2.36.0 or newer. The reload prerequisite is landed, not an open dependency.

## Files

### `pi-interactive-subagents`

- **`pi-extension/subagents/worktree-manager.ts` — new.** One deep module owns required policy, repository/cwd validation, terminal manifests, family records/locks, Git provisioning, lifecycle transitions, resume, selected-family inventory, cleanup authorization, and conservative rollback. Do not split these coupled invariants into shallow Git/registry/cwd/cleanup layers.
- **`pi-extension/subagents/index.ts` — change.** Pass explicit caller authority and unresolved cwd intent into the manager; coordinate parent-name ownership, loadout, surfaces, dispatch, landed reload handoff, kill, resume, and results. At baseline `9388cc9`, relevant seams are reload symbols/version at `84-112`, `RunningSubagent` at `1052-1096`, centralized delivery at `3205-3246`, watcher attachment at `3270-3314`, versioned handoff at `3316-3325`, and reload shutdown/start at `3334-3406`.
- **`pi-extension/subagents/session.ts` — change.** Add immutable workspace references to name/loadout records and replace best-effort loadout writing with one atomic, throwing, read-back-verified `.loadout.json` contract.
- **`pi-extension/subagents/mux.ts` and `mux-adapters.ts` — change.** Add only exact-backend surface probing needed by restart reconciliation. Git/workspace policy remains above mux.
- **`pi-extension/subagents/status.ts` — verify only.** Continue parsing only `status`; the manager reads `worktrees` from the same config object.
- **`config.json.example` — change.** Show required worktree mode. Manager root remains an explicit environment value.
- **`README.md` and `docs/system-maps/interactive-subagents-overview.md` — change.** Document direct/nested cwd, Git minimum, retention, exact resume fingerprint, inventory/cleanup, landed reload handoff, and supported boundaries.
- **`test/worktree-manager.test.ts` — new.** Real temporary Git repositories plus deterministic write/Git/lock fault seams.
- **`test/worktree-lifecycle-hermetic.test.ts` — new.** Coordinator lifecycle, loadout failure, reload handoff, deterministic races, and the required 10×5 overlap acceptance test using real temporary Git and fake mux/process barriers.
- **`test/lifecycle-registry-hermetic.test.ts`, `test/lifecycle-resume-hermetic.test.ts`, `test/lifecycle-kill-hermetic.test.ts`, `test/reload-preserves-subagents-hermetic.test.ts` — change.** Add workspace ownership/fingerprint/checkpoint assertions while preserving the landed reload guarantees.
- **`test/integration/mux-lifecycle-smoke.test.ts` and `test/integration/subagent-lifecycle.test.ts` — change.** Exercise retained worktrees, resume, cleanup, and direct/nested isolation through real backends/provider opt-ins.
- **`package.json` — change only if needed.** Add test scripts; add no runtime dependency.

### `pi-config`

- **`extensions/interactive-subagents/README.md` — change after feature review.** Pin the resulting feature commit and document config/root, Git ≥2.36.0, inventory, cleanup, and rollback.
- **`README.md` and `docs/system-maps/pi-config-overview.md` — change.** Update only the external integration summary and isolation boundary.

Approved Product, Architecture, and research artifacts remain unchanged.

## Types & signatures

### Explicit provision authority and cwd intent

The manager never infers spawn authority from ambient process state and never scans registries to discover a nested caller. `index.ts` constructs one small discriminated value and passes it explicitly.

```ts
export type TaskId = string;
export type AttemptId = string;
export type FamilyKey = string;

export type SpawnAuthority =
  | { kind: "direct"; controllerCwd: string }
  | {
      kind: "nested";
      callerTaskId: TaskId;
      callerFamilyKey: FamilyKey;
      callerWorktreeRoot: string;
      callerCwd: string;
    };

export interface CwdIntent {
  source: "explicit" | "profile" | "fallback";
  raw: string;
  relativeBase: string;
}

export interface ProvisionRequest {
  authority: SpawnAuthority;
  cwd: CwdIntent;
  origin: {
    parentSessionId: string;
    parentSessionFile: string;
    displayName: string;
    agent: string;
  };
  taskId: TaskId;
  attemptId: AttemptId;
}
```

`index.ts` selects precedence but does not resolve `raw`: explicit request uses `params.cwd` and `process.cwd()`; profile cwd uses `profile.cwd` and `getAgentConfigDir()`; fallback uses the authority's caller cwd. Before resolving, `provision` validates direct context or directly addresses and validates the exact nested caller record. Nested resolution then remains inside the validated immediate caller root/family and preserves only its relative subdirectory. There is no ambient registry scan.

### Terminal manifest

```ts
export interface TerminalFingerprint {
  manifestVersion: 1;
  sha256: string;
  head: string;
  statusByteLength: number;
  pathCount: number;
  clean: boolean;
}
```

One SHA-256 digest covers a binary, NUL-safe, length-delimited stream. `field(tag, payload)` is `ASCII(tag) || NUL || uint64be(payload.byteLength) || payload`. Hash, in order: format marker `pi-subagent-terminal-manifest-v1`; raw committed `HEAD`; exact bytes from `git status --porcelain=v2 -z --untracked-files=all --ignore-submodules=none`; then every unique affected raw path sorted with `Buffer.compare`, followed by its current type marker, six-digit octal mode, and file bytes or raw symlink target. Rename sources/deletions use an `absent` marker; directories use a directory marker; special types fail closed.

Parse porcelain records as bytes, include both paths for record `2`, and use Buffer filesystem paths. Stability-check regular files and symlinks before/after reads. Compute the entire manifest twice consecutively and require identical `HEAD`, status, paths, metadata, and digest. Resume requires exact version/digest equality; display metadata never substitutes for the digest. A clean fingerprint has empty status and no path records.

### Workspace lifecycle API

```ts
export type WorkspaceState =
  | "reserved" | "provisioning" | "ready" | "running"
  | "terminal-retained" | "uncertain" | "cleaned";
export type TerminalKind = "completed" | "killed" | "launch-failed";
export type SurfaceBackend = "tmux" | "herdr";

export interface WorktreePolicyConfig {
  mode: "required";
  managerRoot: string;
  familyLockTimeoutMs: 5_000;
  minimumGitVersion: "2.36.0";
}

export interface WorkspaceRef {
  schemaVersion: 1;
  taskId: TaskId;
  familyKey: FamilyKey;
  attemptId: AttemptId;
  recordPath: string;
  worktreeRoot: string;
  managedCwd: string;
  branchRef: string;
  baseHead: string;
}

export interface SessionBinding {
  sessionFile: string;
  sessionId: string | null;
  loadoutFile: string;
}

export interface SurfaceBinding {
  backend: SurfaceBackend;
  surface: string;
  launchScriptFile: string | null;
}

export interface TerminalCheckpoint {
  proof: "natural" | "termination-confirmed" | "unproven";
  kind: TerminalKind;
  exitCode: number | null;
  diagnostic: string | null;
}

export interface CallerAuthority {
  parentSessionId: string;
  callerTaskId: TaskId | null;
  callerFamilyKey: FamilyKey | null;
  callerManagedRoot: string | null;
}

export interface InventoryRequest {
  authority: CallerAuthority;
  repositorySelector: string | null;
}
export interface CleanupRequest extends InventoryRequest { taskId: TaskId }
export interface WorkspaceDiagnostic { code: string; message: string }

export interface WorkspaceSummary {
  taskId: TaskId;
  familyKey: FamilyKey;
  state: WorkspaceState;
  originalParentSessionId: string;
  parentTaskId: TaskId | null;
  displayName: string;
  agent: string;
  worktreeRoot: string;
  managedCwd: string;
  branchRef: string;
  baseHead: string;
  currentFingerprint: TerminalFingerprint | null;
  activeAttemptId: AttemptId | null;
  descendantStates: Partial<Record<WorkspaceState, number>>;
  diagnostics: WorkspaceDiagnostic[];
}

export class WorktreePolicyError extends Error {
  readonly code: string;
  readonly phase:
    | "configuration" | "source-validation" | "provision" | "dispatch"
    | "resume" | "checkpoint" | "inventory" | "cleanup";
  readonly taskId: TaskId | null;
  readonly retained: boolean;
}

export interface WorktreeManager {
  readonly config: WorktreePolicyConfig;
  provision(request: ProvisionRequest): WorkspaceRef;
  bindSession(ref: WorkspaceRef, session: SessionBinding): WorkspaceRef;
  beginDispatch(ref: WorkspaceRef, surface: SurfaceBinding): WorkspaceRef;
  confirmDispatch(ref: WorkspaceRef): WorkspaceRef;
  rollbackBeforeDispatch(ref: WorkspaceRef, diagnostic: string): WorkspaceSummary;
  retainDispatchFailure(ref: WorkspaceRef, proof: "termination-confirmed" | "unproven", diagnostic: string): WorkspaceSummary;
  checkpointTerminal(ref: WorkspaceRef, value: TerminalCheckpoint): WorkspaceSummary;
  claimResume(input: { taskId: TaskId; familyKey: FamilyKey; expectedSession: SessionBinding; attemptId: AttemptId }): WorkspaceRef;
  cancelResumeBeforeDispatch(ref: WorkspaceRef, diagnostic: string): WorkspaceSummary;
  reconcile(input: { taskId: TaskId; familyKey: FamilyKey; surfaceEvidence: "active" | "terminal" | "missing" | "unknown"; terminalCheckpoint: TerminalCheckpoint | null }): WorkspaceSummary;
  list(request: InventoryRequest): WorkspaceSummary[];
  cleanup(request: CleanupRequest): WorkspaceSummary;
}

export type WorktreeManagerInitialization =
  | { ok: true; manager: WorktreeManager }
  | { ok: false; error: WorktreePolicyError };
export function initializeWorktreeManager(options?: { configPath?: string; env?: NodeJS.ProcessEnv }): WorktreeManagerInitialization;
```

### Session/loadout contract

Use only `<sessionFile>.loadout.json`; add no second workspace/session persistence mechanism.

```ts
export interface DurableWorkspaceRef {
  schemaVersion: 1;
  taskId: string;
  familyKey: string;
  recordPath: string;
  worktreeRoot: string;
  managedCwd: string;
  branchRef: string;
  baseHead: string;
}

export interface NameRegistryEntry {
  sessionFile: string;
  sessionId: string | null;
  runState?: "pending" | "running" | "completed";
  runId?: string;
  workspace?: DurableWorkspaceRef;
}

export interface SubagentLoadout {
  cli: "pi" | "claude";
  agent: string | null;
  toolAllowlist: string | null;
  toolExtensions: string[] | null;
  toolExtensionIdentities: ToolExtensionIdentity[] | null;
  model: string | null;
  thinking: string | null;
  systemPromptMode: "append" | "replace" | null;
  identity: string | null;
  spawnable: string[] | null;
  autoExit: boolean;
  cwd: string | null;
  agentDir: string | null;
  workspace: DurableWorkspaceRef;
}

export function writeSubagentLoadout(sessionFile: string, loadout: SubagentLoadout): string;
```

The writer strictly validates, creates a mode-`0600` temp beside the target, writes/fsyncs, renames, fsyncs the directory, reopens the final regular non-symlink, verifies exact-byte SHA-256, parses through `readSubagentLoadout`, and deep-compares the normalized value. Every failure throws. It must complete before `bindSession`, surface, name activation, or dispatch for Pi and Claude. Legacy records without workspace are diagnostic-only under required policy.

### Landed reload handoff

At `9388cc9`, `Symbol.for("pi-subagents/running-handoff")` uses version 1. Add workspace/backend/checkpoint guard to `RunningSubagent`, workspace summary to `SubagentResult`, and bump `RUNNING_HANDOFF_VERSION` to 2. Existing reload shutdown publishes those same live objects; reload start consumes and reattaches them. Pending results carry workspace. Reject mismatch rather than reconstructing identity; upgrade requires no live v1 children. Checkpoint only in landed centralized `deliverWatcherResult` before name completion/result delivery.

### Public lifecycle tools

`subagent_worktrees` accepts only an optional top-level `repository`; `subagent_cleanup` accepts exact `taskId` plus optional top-level `repository`. Add both to lifecycle tools. Neither supports global/all, force, repair, prune, expiry, GC, or branch deletion.

## Call stack

### Configuration, root, atomicity, and Git minimum

Require literal config `worktrees.mode = "required"`, absolute private `PI_SUBAGENT_WORKTREE_ROOT`, and support literal `PI_SUBAGENT_SPAWN_DISABLED=1`. Require a canonical existing current-user root, private permissions, no symlink, outside selected source/common directory, and macOS/Linux. Do not call `diskutil`, inspect mounts, or classify filesystems. Stage registry/loadout writes beside targets and fail closed on actual filesystem/Git errors. Parse `git --version` and require ≥2.36.0 before mutation because NUL-delimited worktree porcelain is mandatory.

The family lock is an exclusive mode-`0600` `registry.lock` acquired by `open("wx")`, bounded to five seconds, exact-token released, and never broken by age/PID inference. Parent-name mutation precedes family lock; no reverse acquisition.

### Durable family record

For canonical common directory `C`, family key is SHA-256 of `C`. Store only under `<managerRoot>/v1/families/<key>/` with `family.json`, `registry.json`, `registry.lock`, and `worktrees/<taskId>/`. Use one revisioned registry. Branch is `refs/heads/pi-subagents/v1/<taskId>` and lock reason `pi-interactive-subagents:v1:<taskId>`.

Transitions are absent → reserved → provisioning → ready → running → terminal-retained/uncertain; exact pre-dispatch rollback may clean ready; resume moves terminal-retained to ready; exact clean cleanup moves terminal-retained to cleaned; cleaned is terminal. Persist intent before Git/process mutation. Reconcile only addressed records; otherwise uncertain. No adoption, recreation, repair, or broad scan.

### Source and cwd validation

`index.ts` builds authority and unresolved cwd intent. Manager validates authority before relative resolution, then canonicalizes repository/path, valid committed `HEAD`, containment, and supported state. Nested cwd must remain inside exact caller root/family; map only relative subdirectory. Require zero raw status bytes before provisioning. Reject non-Git/bare/unborn, submodules, LFS, sparse/partial/promisor/alternate/replace-ref ambiguity, and in-progress operations. Git execution is argv-based, strips repository-selection environment overrides, and makes no network call.

### Initial spawn

Reserve name/task/attempt; provision and validate locked worktree before capabilities/session; use managed cwd for discovery; create/seed session; atomically write/read back complete workspace loadout; bind session; only then create surface, activate name, begin/send/confirm dispatch, track, and attach landed watcher. Pre-dispatch failures may remove only exact clean owned worktree and retain branch/tombstone; at/after ambiguous send retain/uncertain.

### Completion, reload, kill, resume

Central delivery computes/stores double-read manifest once before name completion/result. Confirmed kill checkpoints and retains; uncertain termination remains owned. Reload handoff v2 performs no Git transition. Resume requires exact name/loadout/workspace/registration/lock/branch/session/manifest and uses the same dispatch sequence. Same `HEAD`/porcelain status with differing content is rejected.

### Inventory and cleanup

Top-level directly addresses one selected family and includes prior sessions; nested uses exact lineage and proper descendants only. Cleanup requires exact terminal-retained task, no active operation/unsafe descendant, exact Git identity, and zero status. Persist intent; ordinary unlock/remove; verify absence and retained branch/head; tombstone. Never force, recursive-delete, prune, repair, reset, clean, stash, expire, GC, or branch-delete. Ambiguity is uncertain.

## Test plan

### Named blocker tests

1. **`resume refuses same porcelain status and HEAD when changed file content differs`**.
2. **`terminal manifest hashes raw filenames file bytes symlink targets modes and deletion markers`**.
3. **`terminal manifest rejects an unstable two-pass snapshot`**.
4. **`loadout write failure prevents bind surface and dispatch`**.
5. **`loadout readback failure prevents bind surface and dispatch`**.
6. **`pi and claude use the same atomic loadout contract`**.
7. **`provision validates nested authority before resolving cwd`**.
8. **`direct provision receives controller cwd explicitly`**.
9. **`nested provision directly addresses one caller record`**.
10. **`git below 2.36.0 refuses before mutation`**.
11. **`atomic files stage and rename only beside their targets`**.
12. **`handoff v2 preserves workspace identity and checkpoints once after reload`**.
13. **`handoff version mismatch never reconstructs workspace identity`**.
14. **`family lock serializes resume versus cleanup`**.
15. **`family lock serializes checkpoint versus cleanup`**.
16. **`family lock serializes nested provision versus ancestor cleanup`**.

Each test asserts the exact Gate 3 behavior: raw/content-aware fingerprints, no surface on invalid state, no scan/classifier/second persistence system, strict landed handoff, and both forced family-lock acquisition orders with exact final Git/registry state.

### Exact overlap acceptance test

Add exactly **`ten rounds of five overlapping tasks leak no checkout state`**. Each round has three direct tasks and two nested tasks (from two parents before those parents edit), all in one family. The fixture has committed `shared-overwrite.txt`. All five overwrite that same tracked file with task/round-distinct bytes and commit on their own branches; sentinels are supplementary only.

Use barriers, never sleeps. Before writes, compare controller plus all five worktrees and require baseline bytes. During, block after all five commits and require controller baseline plus each task's own payload in its worktree, checked through filesystem and Git. After terminal retention, repeat all six comparisons and verify manifests. Clean nested then direct tasks; require paths/registrations absent, controller baseline, and each retained branch blob containing only its own payload. Across ten rounds require 50 unique ids/branches/paths/attempts/sessions, 50 isolated payloads, no cross-round/controller/sibling/lineage leak, no orphan surface/path/registration, and one tombstone per task.

### Verification

```bash
node --test test/worktree-manager.test.ts
node --test test/worktree-lifecycle-hermetic.test.ts
node --test test/reload-preserves-subagents-hermetic.test.ts
node --test test/lifecycle-registry-hermetic.test.ts \
  test/lifecycle-resume-hermetic.test.ts \
  test/lifecycle-kill-hermetic.test.ts
npm test
node --test test/*-hermetic.test.ts
npm run test:integration:surface
npm run test:integration:lifecycle-smoke
npm run test:integration:lifecycle
git diff --check
```

No test fetches or contacts a remote except documented provider-opt-in integration. Real mux smoke runs under tmux and Herdr on supported local macOS/Linux.

## Least confident decisions

1. **Synchronous manager methods.** Retained for simple ownership ordering; reconsider only with measured local-Git UI blocking.
2. **Killed tasks remain non-resumable by name.** Preserves current contract while retaining task work.
3. **One JSON registry per family.** One lock gives exact races/lineage without a second persistence scheme.
4. **Ignored local resources are absent.** Follows committed-worktree semantics; hydration is separate.

Resolved P1 decisions: content-aware NUL-safe manifest; explicit validated direct/nested authority before cwd resolution; no mount classifier; landed reload commit `9388cc9634eee84601ce7ee4b7d1cb648040d684` with handoff v2; fixed Git ≥2.36.0; one atomic verified loadout write before bind/surface/dispatch; and exact 10×5 same-tracked-file barriers plus deterministic races.

The only expected implementation-time value still unknown is the final reviewed feature commit used for the `pi-config` pin. Gates 3 and 4 are approved, and Slice 1 is authorized but not started.
