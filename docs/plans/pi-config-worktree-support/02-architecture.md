# Architecture: isolated project workspaces for agent tasks

## Fit

### Intent and outcome

Every task launched through `pi-interactive-subagents`, including a task launched by another subagent, receives one separately owned local Git worktree before its process starts. The worktree starts from the selected source checkout's exact clean committed `HEAD`; a dirty or unsupported source fails closed and never falls back to a shared checkout. The already-running top-level Pi process remains the controller in the user's existing checkout.

The expected outcome is checkout isolation between the controller, direct children, nested children, and siblings while preserving task output for review and resume. This is checkout isolation only: linked worktrees still share Git objects and refs, and child processes still share the user's machine, credentials, services, ports, and caches.

### Responsibility split

The selected architecture is **`pi-interactive-subagents` lifecycle ownership plus mandatory `pi-config` policy**:

- **`pi-interactive-subagents`** owns source discovery, cwd policy, support checks, task/worktree identity, Git creation and locking, durable state, launch ordering, resume validation, terminal retention, repository-family inventory, reconciliation, and explicit cleanup.
- **`pi-config`** pins a compatible fork/release, makes isolated worktrees mandatory for supported project tasks, selects one controller-scoped private manager root, and documents operator review and cleanup. Profiles and individual spawn requests cannot opt out. If policy cannot be loaded, spawning is disabled rather than reverting to shared cwd.
- **Git** is authoritative for repository-family identity, worktree registration, branch and `HEAD`, lock state, and checkout cleanliness. The extension's registry is authoritative for product ownership and lifecycle state. Disagreement is an uncertain state, not permission to repair or delete.
- **The operator** explicitly reviews and integrates retained branches. This feature does not merge, cherry-pick, fetch, push, publish, stash, or discard task work.

Prompt/skill enforcement and a `pi-config` launch wrapper are rejected because neither can atomically own spawn, nested spawn, resume, kill, persistence, and cleanup. A local daemon and Pi core change are unnecessary for the local release.

### Cwd contract

The current direct-task ability to select a repository is preserved:

- A **top-level direct spawn** resolves explicit cwd, profile cwd, or caller fallback using the extension's existing precedence and base rules. The resolved path may be in any supported local Git repository. That selected repository and its exact clean `HEAD` are the task source. The path's repository-relative subdirectory is mapped into the new worktree.
- A **nested spawn** cannot select another repository. Its explicit cwd, profile cwd, or caller fallback must canonicalize inside the immediate caller's managed worktree and must resolve to the same canonical Git common-directory family. Only the path relative to the caller's worktree root is preserved and mapped into the nested child's new sibling worktree. An absolute or relative path that resolves outside the caller's managed worktree, crosses a symlink ownership boundary, or resolves to another repository/common-directory family is rejected before provisioning.

This distinction prevents nested agents from escaping their assigned project while preserving today's direct-task repository selection. Request/profile cwd is always source intent; the child process receives only the corresponding managed cwd.

### Existing modules and seams

Design baseline: `pi-config` `c5bfcfd81ee2b386d5c06103264d25307889eef2`, `pi-interactive-subagents` `eef62f9672b1e8fac4cf4ffff499ba304f0ce79f`, and Pi 0.84.4.

| Current area | Verified behavior | Architectural change |
|---|---|---|
| `pi-interactive-subagents/pi-extension/subagents/index.ts:1637-1701,2446-2524` | Reserves a parent-scoped durable name and activates run ownership before dispatch. | Bind the reservation to durable worktree ownership before session/surface creation. |
| `pi-interactive-subagents/pi-extension/subagents/index.ts:2532-2839` | Resolves request/profile cwd, creates session/loadout, creates a surface, and dispatches. | Apply the direct-versus-nested cwd contract, acquire a worktree, and make its mapped cwd authoritative downstream. |
| `pi-interactive-subagents/pi-extension/subagents/index.ts:3305-3506` | Applies nested allowlists and routes every depth through the same spawn lifecycle. | Enforce same-caller-worktree and same-common-directory containment at every nested depth. |
| `pi-interactive-subagents/pi-extension/subagents/index.ts:1989-2396` | Resume validates session/loadout ownership but replays cwd without Git identity validation. | Reuse the exact checkout only after registry, path, registration, lock, branch, `HEAD`, and status validation. |
| `pi-interactive-subagents/pi-extension/subagents/index.ts:1824-1925,2943-3229` | Kill and watcher completion settle process/session ownership; uncertain disappearance is retained. | Checkpoint Git state after terminal proof and retain the worktree on completion and kill. |
| `pi-interactive-subagents/pi-extension/subagents/index.ts:3236-3275` | Reload/shutdown clears in-memory tracking but preserves durable process/session state. | Preserve worktree ownership across fresh parent sessions and reconcile it from repository-family records. |
| `pi-interactive-subagents/pi-extension/subagents/session.ts:62-158,184-604` | Persists cwd/loadout, durable names, and atomic resume claims. | Persist immutable task/worktree references and original lineage beside these artifacts. |
| `pi-interactive-subagents/pi-extension/subagents/mux.ts:121-238,334-415` | Exposes backend-neutral surface lifecycle operations. | Keep worktree policy above mux; pass only a validated managed cwd. |
| `pi-interactive-subagents/pi-extension/subagents/mux-adapters.ts:68-141,237-318` | tmux and Herdr create local shells; dispatched commands currently perform `cd`. | Both backends must start and dispatch in the managed cwd without owning Git lifecycle. |
| `pi-interactive-subagents/pi-extension/subagents/subagent-done.ts:146-166,277-355` | Publishes terminal state atomically. | Git checkpointing and terminal retention follow proven terminal publication. |
| `pi-interactive-subagents/config.json.example:1-5` | Configuration currently covers status only. | Add mandatory controller-level workspace policy and manager-root selection; exact shape is Gate 3. |
| `pi-interactive-subagents/README.md:61-94,136-150,185-206` | Documents cwd, resume, kill, profiles, Claude, and role-folder cwd. | Document the direct/nested cwd distinction, retention, cross-session discovery, and cleanup. |
| `pi-config/extensions/interactive-subagents/README.md` | Integrates the external extension into pi-config. | Pin and document mandatory policy, support boundaries, and operator lifecycle. |

The architecture follows `pi-config/docs/plans/pi-config-worktree-support/01-product.md:3-15` and `pi-config/docs/research/pi-config-worktree-support.md`.

### Scope

In scope:

- Direct and recursively nested Pi or Claude subagent tasks launched by the extension.
- One unique task branch and external sibling worktree per invocation.
- Local macOS/Linux repositories with a valid committed `HEAD` and no staged, unstaged, or untracked project changes.
- Direct selection of any supported Git repository; nested cwd selection constrained to the caller's managed worktree and repository family.
- Main and linked source worktrees when canonical identity can be proved.
- Durable identity, fresh-session repository-family discovery, restart reconciliation, terminal retention, and explicit safe cleanup.
- Equivalent lifecycle through tmux and Herdr.

Out of scope:

- Provisioning or relocating the top-level controller.
- Dirty-state transfer, synthetic commits, snapshots, stashes, or copied ignored/generated files.
- Automatic integration, conflict resolution, fetch, push, publication, branch deletion, prune, repair, force removal, expiry, GC, or stale-lock adoption.
- A global scan across unrelated repositories or foreign Git worktrees.
- Non-Git, bare, or unborn repositories; submodules; Git LFS; network/removable manager roots; Windows; and remote execution.
- Isolation of shared Git administration, credentials, environment, home directory, processes, services, ports, caches, network, or containers.

### Architecture boundary

The child lifecycle coordinator remains the orchestration boundary. A local workspace owner sits between final task/name reservation and all session, capability, surface, and process work. Workspace identity and terminal-surface identity are separate: a task owns one durable workspace across execution attempts, while each initial launch or resume has one single-writer attempt and possibly a new terminal surface.

Project resources are evaluated from the managed cwd. Session, transcript, loadout, registry, and workspace-control artifacts remain in private controller-managed storage outside removable worktrees. Immutable records preserve the original parent session and nested lineage even when a later top-level session discovers the retained worktree; discovery does not adopt or reassign ownership.

## Endpoints

These are Pi extension tool surfaces, not HTTP endpoints:

- `subagent` — **invoke** — for a top-level direct call, resolve explicit/profile/fallback cwd to any supported Git repository and provision from its clean `HEAD`; for a nested call, require the resolved cwd inside the immediate caller's managed worktree and same Git common-directory family, preserve only its relative subdirectory, and reject outside/cross-repository paths.
- `subagent_resume` — **invoke** — resume a completed task in the same exactly validated worktree and session; refuse missing, changed, active, or uncertain ownership.
- `subagent_message` — **invoke** — steer a live execution without changing workspace ownership; its compatibility resume path uses the same validation as `subagent_resume`.
- `subagent_kill` — **invoke** — terminate the process, checkpoint after terminal proof, and mark the task terminal-retained; never remove or unlock its worktree.
- `subagents_list` — **query** — continue listing available profiles only.
- `subagent_worktrees` — **query** — at top level, resolve exactly one requested repository family (defaulting to the controller's current family) and report all exactly owned durable task records in that family, including records created by prior parent sessions; for a nested caller, report only its own descendant task subtree.
- `subagent_cleanup` — **invoke** — discover/resolve the target under the same top-level repository-family or nested-subtree scope, then remove one terminal, clean, exactly owned worktree after descendant and Git revalidation; retain its branch and tombstone.

A top-level controller can select another supported repository path when inventorying or cleaning tasks previously launched there, but each operation is scoped to that one canonical common-directory family. It does not scan every manager directory, every Git repository, or foreign worktree registrations. A nested controller cannot use a repository selector to escape its descendant subtree.

Original parent-session ownership and lineage are immutable. A fresh top-level session receives repository-family authority to inspect or clean exactly owned durable records; it does not become their recorded creator. Cosmetic names remain convenience lookups only where unambiguous. Cleanup resolves to and returns the immutable task identity before mutation.

Spawn, completion, kill, and resume results expose task identity, managed path, branch, base, current `HEAD`, workspace state, and descendant summary. Diagnostics redact credentials. There are no web routes, webhooks, or database endpoints.

## Data

### Durable records

No SQL database or remote collection is introduced. The feature extends local atomic registries:

1. **Parent-session task reference** — maps parent-scoped names to immutable task identity, session/loadout, original lineage, current execution attempt, and repository-family record. It remains the authority for live message/resume/kill behavior.
2. **Repository-family workspace registry** — contains one schema-versioned durable record per exactly owned task under a private manager root, grouped by a full digest of canonical `--git-common-dir` identity. It persists source root and relative cwd, base, branch, managed path, Git lock identity, expected `HEAD` and status fingerprint, original parent session/lineage, timestamps, execution linkage, and lifecycle state. This is the cross-session source for top-level inventory and cleanup discovery.
3. **Existing session/loadout artifacts** — preserve model, tools, extensions, sandbox, spawn allowlist, and managed cwd, bound to the immutable task identity.
4. **Git-owned state** — unique task branch, linked-worktree registration, per-worktree index/`HEAD`, and worktree lock. Custom state is never stored inside `.git`.

The controller selects one absolute private manager root once at startup. Repository-family lookup addresses one exact family key; there is no global enumeration API. Records retain original ownership and lineage permanently. A later top-level session may be authorized to act on an exact record in a selected repository family, but no record is adopted, copied, or reassigned.

### Identity and state

- **Repository family key:** digest of canonical common Git directory, with canonical identity retained for mismatch detection.
- **Task identity:** opaque collision-resistant owner assigned once and retained across resume and parent-session changes.
- **Execution attempt:** distinct initial/resume writer; only one may be active.
- **Task branch/path:** deterministic functions of immutable task identity under reserved/private namespaces; cosmetic names and prompts never become ref/path components.
- **Lineage:** immutable original parent task and parent session. Nested authorization always follows this lineage.

Workspace states are **reserved → provisioning → ready → running → terminal-retained or uncertain → cleaned**. Resume adds an execution attempt to the same workspace. `cleaned` is a tombstone; the retained branch and audit metadata survive.

Logical queries are:

- Resolve a live parent-scoped name for message/resume/kill.
- Resolve exactly one canonical repository family from a top-level inventory/cleanup request and enumerate only exactly owned durable records in that family, regardless of originating parent session.
- Filter a nested inventory/cleanup request to descendants of the caller's immutable task identity.
- Compare one durable record to NUL-delimited Git inventory/status and verify exact ownership.
- Determine whether active or uncertain descendants block cleanup.
- Reconcile known records after reload without inferring ownership from names, PIDs, branch patterns, or broad filesystem/Git scans.

A newly selected source must be completely clean. A completed task may be dirty; resume is allowed only when current state exactly matches its terminal fingerprint. Out-of-band change fails closed.

### Concurrency, locking, and retention

Repository-family creation, reconciliation, resume claim, inventory snapshots that require consistency, checkpoint, and cleanup are serialized with one bounded cross-process family lock. Agent execution remains concurrent. Existing parent-session locking and one-writer claims remain in force. Locks are not broken based only on age or PID reuse.

Natural completion, confirmed kill, parent exit, reload, fresh session, controller crash, and uncertain disappearance retain worktree registration and Git lock. There is no time-based cleanup, expiry, GC, broad scan, prune, or repair. Explicit cleanup removes only the exact linked checkout and retains its branch and tombstone.

## Flow

### Direct spawn

1. Validate authorization and reserve the parent-scoped name plus immutable task identity.
2. Resolve explicit cwd, profile cwd, or caller fallback with the existing direct-call precedence/base semantics. The canonical result may select any supported local Git repository.
3. Discover that selected checkout's root and common directory, record only the repository-relative subdirectory, and require local macOS/Linux, valid `HEAD^{commit}`, complete staged/unstaged/untracked cleanliness, and no detected submodules or Git LFS. Failure occurs before session, surface, or process creation.
4. Under the selected repository-family lock, repeat source validation, persist intent, create a collision-refusing task branch from exact `HEAD`, create and lock an external sibling worktree, and validate canonical path, common directory, registration, branch, base, and `HEAD`.
5. Map the recorded relative subdirectory beneath the new worktree. Recheck containment, symlink boundaries, and repository identity.
6. Persist workspace, session, loadout, trust, and parent references outside the checkout, all pointing to the managed cwd.
7. Create the tmux/Herdr surface in the managed cwd, activate the execution attempt, and dispatch.
8. After terminal proof, checkpoint Git state, mark terminal-retained, close the surface, and report handoff metadata without unlocking/removing the worktree.

The selected source commit and status are checked around the family lock. A move or dirtying race aborts launch.

### Nested spawn

1. Resolve the nested explicit cwd, profile cwd, or fallback, then canonicalize it against the immediate caller's managed checkout.
2. Require the canonical path to be contained inside that caller worktree and to report the same canonical Git common directory. Reject any outside path, cross-repository path, nested foreign repository, or symlink escape before a branch, worktree, session, or surface is created.
3. Preserve only the path relative to the caller's worktree root. Do not carry the caller's absolute managed path into child state.
4. Require the caller worktree's exact `HEAD` and staged/unstaged/untracked cleanliness. The nested base is this immediate caller commit, never a top-level branch or separately selected repository.
5. Provision a new sibling worktree in the same repository family and map the preserved relative subdirectory into it, then continue through the direct flow's persistence, launch, checkpoint, and retention steps.

The nested child receives a new task identity, branch, session, process, and sibling worktree. A parent cannot be cleaned while a descendant is running or uncertain; terminal-retained descendants remain independently owned.

### Inventory and retained discovery

1. A top-level request resolves one repository selector (or the controller cwd default) to one canonical common-directory family.
2. The extension opens that family's durable registry directly and returns exactly owned records across all originating parent sessions, including terminal worktrees retained before the current session started.
3. Each record is correlated with Git registration using immutable task identity, canonical path/common directory, branch, and lock. Foreign registrations and mismatches are diagnostic only.
4. A nested request skips repository-wide authorization and filters durable records to the caller's immutable descendant subtree.

Inventory never scans unrelated family registries, arbitrary filesystem paths, or all worktrees on the machine. It never adopts records, expires them, garbage-collects them, or changes their original ownership.

### Resume

1. Resolve the completed task and require terminal-retained workspace, session/loadout, no live or uncertain writer, and no cleaned tombstone.
2. Under its family lock, validate manager-root containment, common-directory identity, exact Git registration/lock, branch, expected `HEAD`, and exact terminal status fingerprint.
3. Claim a new execution attempt only after validation. Missing, moved, repointed, unlocked, or modified state launches nothing and remains diagnostic; never recreate a missing checkout.
4. Create a surface in the same managed cwd, dispatch the saved loadout/session, and return to watcher/checkpoint flow.

### Completion, kill, reload, and reconciliation

- **Natural completion:** terminal evidence, Git checkpoint, terminal-retained publication.
- **Confirmed kill:** prove process termination, checkpoint, and mark killed-retained; do not clean.
- **Uncertain kill/disappearance:** retain checkout, lock, claim, and diagnostic; refuse resume and cleanup until exact reconciliation.
- **Reload/fresh session/crash:** never unlock or remove. Reconcile known repository-family records and live evidence. Fresh-session inventory remains possible because discovery is not limited to the current parent-session registry.

### Explicit cleanup

1. Resolve the target through top-level single-family discovery or nested descendant-subtree discovery and require an exact immutable task identity and terminal-retained state.
2. Acquire the family lock and revalidate record, manager containment, common directory, exact Git registration/branch/lock, and absence of running or uncertain descendants.
3. Require a completely clean task worktree; dirty output is retained and cleanup fails.
4. Unlock only the exact registration and use ordinary non-force worktree removal. Never recursively delete, force, prune, repair, stash, reset, delete the branch, expire records, or run GC.
5. Persist a cleaned tombstone and retained branch/commit. On partial failure, relock only if exact safety is proved; otherwise mark uncertain and retain state.

### Rollback and failure behavior

Before dispatch, rollback may affect only an exact manager-contained, registered, clean worktree after ownership revalidation; any created branch remains recorded. After dispatch or whenever process/identity/cleanup outcome is uncertain, retain everything. The source checkout and source branch are never rewritten.

| Failure | Required outcome |
|---|---|
| Dirty, unsupported, unsafe, or ambiguous source | No session/surface/process and no shared-cwd fallback. |
| Nested cwd outside caller worktree or in another common-directory family | Reject before provisioning; do not reinterpret it as a direct repository selection. |
| Source `HEAD`/status changes during provisioning | Abort; remove only an exact clean pre-dispatch worktree and retain any branch/record. |
| Branch/path collision or foreign registration | Fail without force, replacement, deletion, prune, repair, or adoption. |
| Durable write, dispatch, liveness, or terminal checkpoint is ambiguous | Retain as uncertain with one-writer ownership. |
| Resume identity/fingerprint differs | Launch nothing; retain and diagnose. |
| Inventory encounters a foreign/mismatched registration | Report diagnostic; do not mutate or broaden the scan. |
| Cleanup is dirty, active, uncertain, foreign, mislocked, or descendant-unsafe | Refuse without mutation. |
| Cleanup partially fails | Relock only when exact; otherwise uncertain-retained; never recursive-delete. |
| Legacy session lacks durable worktree identity | Do not resume under mandatory policy; require a fresh task. |

Operational rollback stops new spawning and reaches terminal/known state for active tasks. `pi-config` must disable subagent spawning if an older extension would restore shared-cwd behavior. Retained branches/worktrees are not automatically removed.

### Architecture acceptance checks

Gate 3 will name concrete tests and commands. The implementation must make these observable:

- Direct explicit/profile cwd can select another supported repository and maps its relative subdirectory into a worktree there.
- Nested explicit/profile cwd works only inside the caller's managed worktree and same common-directory family; outside and cross-repository paths launch nothing.
- Fresh top-level sessions can select one repository family and discover/clean exactly owned retained records from prior parent sessions; nested controllers see only descendants.
- Inventory performs no global/broad scan and cleanup preserves immutable ownership, exact checks, branches, and tombstones.
- Overlapping direct/nested tasks have distinct paths, branches, sessions, owners, and processes; edits never cross checkouts.
- Resume uses the same task path/branch/session and rejects missing or modified state.
- Completion, kill, reload, and crash retain output; cleanup is never implicit and never forceful.
- Unsupported repositories/platforms and collision/lock/write failures fail before unsafe dispatch or remain diagnosably uncertain.

## External

### Git

The local Git CLI is the only new runtime integration. Use canonical `rev-parse`, path-safe status, and NUL-delimited worktree porcelain; preserve ordinary `worktree add`, lock, unlock, and remove safeguards. No operation may require network access, `--force`, branch replacement/deletion, broad unlock, prune, repair, expiry, or GC.

Linked worktrees share objects, refs, configuration, hooks, and much administration. This prevents accidental working-file overlap, not malicious same-user Git/filesystem access.

### Pi, tmux, and Herdr

Pi 0.84.4 session/loadout/trust behavior remains the process contract. Managed cwd controls committed project-resource discovery; trust is a one-run decision derived from the controller and does not copy credentials or persist broader trust.

tmux and Herdr remain local terminal/process adapters. Worktree provisioning completes before either creates or dispatches a child surface, and backend choice cannot alter cwd restrictions, discovery scope, retention, resume, cleanup, or failure semantics.

### Policy and environment

`pi-config` supplies mandatory policy and one controller-scoped external manager root. Exact configuration keys and environment-variable names remain Gate 3 decisions. Profiles, prompts, nested agents, and tool parameters cannot disable isolation. A global emergency control may disable spawning, but cannot select shared cwd.

Manager storage is local, private, and outside source repositories. Repository-family access is by exact canonical key, not a broad scan. No credentials, SSH material, `.env` files, trust-store entries, or shell history are copied into task worktrees.

### Unsupported cases

The release rejects non-Git directories, bare/unborn repositories, detected submodules, detected Git LFS, unsafe path/symlink mappings, unsupported linked-worktree states, Windows, remote tasks, and network/removable manager roots. Nested paths outside the immediate caller's managed checkout or in another repository family are also unsupported, even when that other repository would be valid for a top-level direct call. There is no degraded shared-workspace mode.

Ignored/generated dependencies are not inherited. Non-LFS filters, unusual hooks/configuration, sparse/partial clones, and alternates require verification before support expands; ambiguous cases fail closed.

### Future Vercel boundary

Vercel Sandbox is not a mux adapter and is outside this release. The durable model separates task, workspace, execution attempt, and terminal surface so a future remote controller can supply a different workspace kind. Remote sandbox/snapshot identity, source acquisition, credentials, persistence, nested coordination, cancellation, resume, transfer, retention, and destruction require a separate architecture and cannot reuse local paths, common-directory identity, mux assumptions, or local locks.

### Premortem and accepted risks

| Assumption or failure mode | Mitigation / accepted risk |
|---|---|
| Stable task identity binds registry, session, Git registration, and branch across sessions. | Persist before provisioning; retain original lineage; validate every authority on resume, inventory, and cleanup. |
| Cross-session discovery could overreach. | Require one selected canonical repository family and exactly owned records; nested callers remain subtree-limited; never globally scan/adopt. |
| Nested cwd can escape through absolute paths, profile bases, symlinks, or embedded repositories. | Canonicalize before provisioning and require caller-root containment plus identical common-directory identity. |
| Session/control artifacts survive cleanup. | Store them outside worktrees; cleaned tasks are tombstoned and not resumable. |
| Git locks and records prevent accidental lifecycle overlap. | Serialize family transitions and validate both; malicious same-user tampering remains out of scope. |
| Strict clean-parent behavior blocks delegation after edits. | Give commit/finish guidance; dirty snapshots remain a separate feature. |
| Retained branches/worktrees accumulate. | Provide family-scoped inventory and explicit safe cleanup; no expiry/GC until separately designed. |
| Reload or partial dispatch makes process truth uncertain. | Retain locks and claims until exact evidence proves terminal state. |

### Gate 2 decisions requiring approval

1. Direct explicit/profile cwd preserves today's ability to select any supported repository; nested cwd is confined to the immediate caller's managed worktree and same Git common-directory family, preserving only its relative subdirectory.
2. Lifecycle mechanics live in `pi-interactive-subagents`; `pi-config` makes them mandatory with disable-spawning—not shared-cwd—as the emergency behavior.
3. Each invocation owns an opaque durable task identity, deterministic task branch/path, and immutable original lineage; resume attempts and surfaces have separate identities.
4. Top-level inventory/cleanup discovery selects exactly one repository family and includes exactly owned retained records from prior parent sessions; nested callers remain limited to descendants. There is no global scan, adoption, expiry, or GC.
5. Completion and confirmed kill retain worktrees; ambiguous termination is uncertain-retained.
6. Resume requires the same exact worktree, lock, branch, `HEAD`, and fingerprint; legacy sessions and missing worktrees are not reconstructed.
7. Cleanup is terminal, exact-owner, descendant-safe, clean, non-forceful, and branch-retaining, with immutable ownership preserved.
8. Repository transitions are serialized per common directory while execution remains concurrent; nested tasks use sibling worktrees from the immediate caller's clean commit.
9. Worktree lifecycle remains above tmux/Herdr and separate from future Vercel execution/storage.
10. The first release is a strict local macOS/Linux Git subset and fails closed for dirty, ambiguous, or unsupported state.

Gate 3 must still decide concrete files, types/signatures, configuration/environment names, record/lock formats, Git command details, diagnostics, and named tests. No Product decision is reopened.
