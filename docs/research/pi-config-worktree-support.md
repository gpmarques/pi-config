# Per-task Git worktrees for Pi subagents

**Status:** Gate 1 approved decision brief, not an implementation plan
**Baselines:** `pi-config` `c5bfcfd81ee2b386d5c06103264d25307889eef2`; `pi-interactive-subagents` `eef62f9672b1e8fac4cf4ffff499ba304f0ce79f`; Pi **0.84.4** at tag object `b79e4cc834970cca69daebffab7df1da7d1e52c4`; current official Git documentation
**Labels:** **FACT** = verified behavior; **PROPOSAL** = recommendation; **APPROVED (GATE 1)** = accepted Product boundary/constraint; **UNKNOWN** = implementation uncertainty or spike required.

> **SUPERSEDED:** The earlier recommendation in this file—worktrees for parallel catalogue testing followed by a package-first stable promotion channel—is **superseded**. The feature evaluated now is: **every spawned agent task receives a separately owned project Git worktree, including nested agents**. Package promotion and generic worktree management are not this feature.

## Summary

**PROPOSAL — Lifecycle mechanics belong in `pi-interactive-subagents`; `pi-config` supplies mandatory policy.** The subagent extension already owns child cwd, session creation, durable run claims, process launch, nesting, resume, termination, and result delivery. Worktree creation, identity, validation, retention, and cleanup must join that transaction. A skill or profile prompt cannot enforce it.

**PROPOSAL — Approve a conservative local MVP.** Each invocation starts from the immediate caller's exact, clean `HEAD`, receives a locked worktree on a unique task branch, and launches only after canonical ownership is persisted. Completion and termination retain the checkout. Resume reuses and validates it. Explicit cleanup handles only a terminal, clean, exactly owned checkout, without force, and retains its branch.

**APPROVED (GATE 1) — Spawned-task boundary.** This design covers every recursively spawned `subagent` task. It treats the already-running top-level Pi session as the controller, not a spawned task. Provisioning that controller would require a separate pre-Pi launcher and is outside this feature.

## Findings

### 1. Current ownership stops at the child cwd

1. **FACT — Children are separate Pi/Claude processes.** The tool accepts `agent`, `task`, cosmetic `name`, optional `model`, and optional `cwd`. Tool cwd, profile cwd, and caller fallback determine where the child starts and therefore which local `.pi`, context, skills, and extensions it discovers. [`index.ts` parameters](https://github.com/gpmarques/pi-interactive-subagents/blob/eef62f9672b1e8fac4cf4ffff499ba304f0ce79f/pi-extension/subagents/index.ts#L110-L155), [`resolveSubagentPaths`](https://github.com/gpmarques/pi-interactive-subagents/blob/eef62f9672b1e8fac4cf4ffff499ba304f0ce79f/pi-extension/subagents/index.ts#L770-L795), [`launchSubagent`](https://github.com/gpmarques/pi-interactive-subagents/blob/eef62f9672b1e8fac4cf4ffff499ba304f0ce79f/pi-extension/subagents/index.ts#L2545-L2830)

2. **FACT — The existing transaction is the natural worktree owner.** Before dispatch, the extension reserves a parent-scoped name, creates a child session, snapshots the model/tool/extension/spawn/cwd loadout, activates a durable run claim, and only then sends the command. Registry changes use atomic replacement and an exclusive lock; uncertain failures retain claims. [`loadout`](https://github.com/gpmarques/pi-interactive-subagents/blob/eef62f9672b1e8fac4cf4ffff499ba304f0ce79f/pi-extension/subagents/session.ts#L84-L164), [`name registry`](https://github.com/gpmarques/pi-interactive-subagents/blob/eef62f9672b1e8fac4cf4ffff499ba304f0ce79f/pi-extension/subagents/session.ts#L318-L445), [`launch ownership`](https://github.com/gpmarques/pi-interactive-subagents/blob/eef62f9672b1e8fac4cf4ffff499ba304f0ce79f/pi-extension/subagents/index.ts#L2470-L2543)

3. **FACT — Resume is fail-closed for session capability, but not Git identity.** It resolves a completed parent-scoped name, prevents concurrent writers, validates the saved loadout and backing extensions, and replays saved cwd. That cwd can currently be missing, repointed, or contain another checkout without Git validation. [`resumeRegisteredSubagent`](https://github.com/gpmarques/pi-interactive-subagents/blob/eef62f9672b1e8fac4cf4ffff499ba304f0ce79f/pi-extension/subagents/index.ts#L2095-L2404)

4. **FACT — Process termination and session teardown do not own a checkout.** Current termination suppresses stale delivery and removes only its run mapping after terminal proof. Session teardown aborts watchers and clears in-memory tracking; it does not establish a worktree disposal policy. [`killSubagent`](https://github.com/gpmarques/pi-interactive-subagents/blob/eef62f9672b1e8fac4cf4ffff499ba304f0ce79f/pi-extension/subagents/index.ts#L1817-L1884), [session lifecycle](https://github.com/gpmarques/pi-interactive-subagents/blob/eef62f9672b1e8fac4cf4ffff499ba304f0ce79f/pi-extension/subagents/index.ts#L3235-L3275)

5. **FACT — Nested launches use the same core path.** Profiles with `subagent_agents` receive lifecycle tools and a strict allowlist at every depth; bundled `worker` and `planner` may spawn `scout` and `researcher`. One core provisioning hook can therefore enforce a fresh worktree recursively. [`nested gate`](https://github.com/gpmarques/pi-interactive-subagents/blob/eef62f9672b1e8fac4cf4ffff499ba304f0ce79f/pi-extension/subagents/index.ts#L3277-L3408), [profiles](https://github.com/gpmarques/pi-interactive-subagents/tree/eef62f9672b1e8fac4cf4ffff499ba304f0ce79f/agents)

6. **FACT — No inspected module persists or manages Git worktree ownership.** The current “sandbox” is a Pi tool/extension loadout, not filesystem or OS isolation.

### 2. Git supplies safe primitives, not product lifecycle

1. **FACT — Linked worktrees separate checkout state while sharing repository state.** They have per-worktree `HEAD` and index, but share objects, refs, and most administration. A linked checkout normally has a `.git` *file*, not a directory. [Git worktree details](https://git-scm.com/docs/git-worktree#_details), [repository layout](https://git-scm.com/docs/gitrepository-layout)

2. **FACT — Use Git's canonical interfaces.** `git rev-parse --show-toplevel` identifies the checkout; `--git-dir` its administration; `--git-common-dir` the repository family. `git worktree list --porcelain -z` is the stable, path-safe inventory and reports head, branch/detached, locked, and prunable state. [git-rev-parse](https://git-scm.com/docs/git-rev-parse), [worktree porcelain](https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt---porcelain)

3. **FACT — Git's refusals are safety properties to preserve.** It normally refuses an already-occupied branch, refuses `-b` when the branch exists, and refuses removal of an unclean worktree. Force options override those protections. Worktree locks protect against accidental prune, move, and deletion. [git-worktree options](https://git-scm.com/docs/git-worktree#_options)

4. **FACT — Prune and repair are broad administrative recovery operations.** They can affect registrations outside this feature's ownership and must not be routine automated cleanup. [git-worktree commands](https://git-scm.com/docs/git-worktree#_commands)

5. **FACT — Git calls submodule support for multiple checkouts incomplete and advises against multiple superproject checkouts.** [git-worktree bugs](https://git-scm.com/docs/git-worktree#_bugs)

6. **UNKNOWN — Git LFS is unvalidated here.** Smudge/download behavior, cache sharing, offline operation, and credentials require a separate matrix. The MVP should reject detected LFS use; it should not claim Git itself forbids it.

### 3. Pi makes cwd, persistence, and trust part of ownership

1. **FACT — Pi 0.84.4 sessions are cwd-organized and store cwd in the session header.** Extensions can persist non-context custom entries, execute subprocesses, and receive session lifecycle events. Pi requires idempotent cleanup of session-scoped resources. [sessions](https://github.com/earendil-works/pi/blob/b79e4cc834970cca69daebffab7df1da7d1e52c4/packages/coding-agent/docs/sessions.md), [session format](https://github.com/earendil-works/pi/blob/b79e4cc834970cca69daebffab7df1da7d1e52c4/packages/coding-agent/docs/session-format.md), [extensions](https://github.com/earendil-works/pi/blob/b79e4cc834970cca69daebffab7df1da7d1e52c4/packages/coding-agent/docs/extensions.md)

2. **FACT — Session replacement tears down and rebinds runtime ownership.** Old session-bound objects become stale, so worktree identity cannot exist only in an extension closure. [Pi session replacement](https://github.com/earendil-works/pi/blob/b79e4cc834970cca69daebffab7df1da7d1e52c4/packages/coding-agent/docs/extensions.md#session-replacement-lifecycle-and-footguns)

3. **FACT — Project trust is path-sensitive input loading, not a sandbox.** Pi runs with the user's permissions, regards same-user-writable files as one local trust boundary, and recommends a container/VM/remote sandbox for untrusted or unattended work. One-run approval/denial is available without persisting broad trust. [Pi 0.84.4 security](https://github.com/earendil-works/pi/blob/b79e4cc834970cca69daebffab7df1da7d1e52c4/packages/coding-agent/docs/security.md)

4. **FACT — Pi recognizes linked-worktree layout in selected discovery paths.** Its Git helper follows gitfiles and `commondir`; resource loading uses that awareness. This supports compatibility but does not create or own worktrees. [Git path helper](https://github.com/earendil-works/pi/blob/b79e4cc834970cca69daebffab7df1da7d1e52c4/packages/coding-agent/src/core/footer-data-provider.ts), [resource loader](https://github.com/earendil-works/pi/blob/b79e4cc834970cca69daebffab7df1da7d1e52c4/packages/coding-agent/src/core/resource-loader.ts)

## Ownership alternatives

| Alternative | Evidence and decision |
|---|---|
| Skill/profile instructions | **FACT:** cannot run before session creation, atomically bind process/session/checkout, constrain resume, or guarantee cleanup. **PROPOSAL: reject as enforcement.** |
| `pi-config`-only wrapper around child tools | **FACT:** duplicates launch/resume/termination state and creates split ownership. **PROPOSAL: reject as child owner.** A pre-Pi wrapper is relevant only if the root controller is in scope. |
| `pi-interactive-subagents` core + `pi-config` policy | **FACT:** the extension already owns every relevant child lifecycle boundary. **PROPOSAL: approve.** |
| Standalone daemon/controller | **PROPOSAL:** defer locally; reconsider for leases, multi-host work, or Vercel. |
| Pi core change | **FACT:** Pi exposes the required extension, cwd, process, persistence, and lifecycle APIs. **PROPOSAL:** no upstream change for local MVP. |

**PROPOSAL — Responsibility split:**

- `pi-interactive-subagents`: Git discovery, provisioning transaction, durable ownership, locks, cwd mapping, rollback, nested enforcement, resume checks, handoff metadata, and cleanup.
- `pi-config`: mandatory defaults, supported profile policy, manager-root configuration, and operator documentation. Profiles cannot opt out silently.
- Operator/parent: review and explicitly merge or cherry-pick retained branches.
- Future remote controller: sandbox identity, credentials, persistence, and artifact transport.

## Recommended lifecycle contract

### Durable identity

**PROPOSAL — Use an opaque run ID, never cosmetic name or cwd, as owner.** Persist schema version, parent session/run, child run/session, mux surface, canonical source root, source-relative cwd, canonical common directory, base commit, task branch ref, canonical managed root, expected current `HEAD`, status fingerprint, trust mode, timestamps, and lifecycle state.

**PROPOSAL — Keep state outside Git administration.** Store a parent-session reference beside existing artifacts and a repository-family registry under a configurable private manager root (mode `0700`), keyed by a hash of canonical common-dir identity. Use atomic replacement and a bounded exclusive lock. Never put custom state in `.git`; never guess ownership from PID age or branch naming.

**PROPOSAL — Lock the Git worktree with a reason as well.** The external record is product authority; the Git lock prevents accidental maintenance. Neither resists a malicious same-user process.

### Creation, base, branch, and cwd

**PROPOSAL — Apply one policy at every nesting depth:**

1. Resolve/canonicalize requested cwd and require it inside a supported non-bare Git worktree.
2. Discover source root/common directory with `rev-parse`; record the source-relative subdirectory.
3. Require a valid, unchanged `HEAD` and no staged, unstaged, or untracked files. Do not import dirty state.
4. Reject detected submodules and LFS; do not fetch.
5. Use exact `HEAD^{commit}` as base, not a remote/default-branch guess.
6. Under the repository-family lock, write a creation intent and create a locked external worktree with a collision-resistant branch such as `pi-agents/<parent-session-id>/<run-id>`. Branch creation must refuse collisions; no branch replacement or force.
7. Validate path, common directory, branch, base, and Git registration through NUL-delimited porcelain before marking ready.
8. Map the original relative cwd beneath the new root, prove no traversal/symlink escape, seed the child session with it, mirror the controller's resolved trust decision for that run, then dispatch.

**PROPOSAL — Dirty source is a hard failure, including nested source.** A nested child starts at its immediate parent's clean `HEAD`, never the top-level branch. If its parent has begun editing, spawning fails with guidance to commit or finish first. Ordinary worktrees cannot faithfully inherit arbitrary staged, unstaged, untracked, ignored, generated, or running-service state.

**APPROVED (GATE 1) — Strict dirty-parent behavior.** Synthetic commits, patches plus untracked files, or filesystem snapshots are larger future features with rules for secrets, ignores, filters, executable bits, symlinks, conflicts, object retention, and handoff; they are not alternatives in this release.

**APPROVED (GATE 1) — Task branches rather than detached worktrees.** Unique branches make commits and handoff durable. The choice is uniform and not profile-dependent. Detached mode would require a separate durable-ref protocol and is outside this release.

### Running, concurrency, and nesting

**PROPOSAL — Ready checkout precedes process activation.** Order: reserve run/name → persist checkout intent → create/validate checkout → create session/loadout → activate both owners → dispatch. Before dispatch, rollback may affect only the exact owned clean checkout. After dispatch starts or state becomes uncertain, retain and report.

**PROPOSAL — Serialize transitions, not agent execution.** Creation/cleanup/recovery take one repository-family cross-process lock with a documented order relative to the current registry lock. Siblings then run concurrently in separate paths/branches. Existing one-writer session claims remain mandatory for resume.

**PROPOSAL — Every nested invocation gets a sibling managed worktree.** It never reuses the parent's path and is never nested beneath another checkout. Persist lineage. Block parent cleanup while any descendant is active or uncertain; terminal retained descendants remain independently owned.

**FACT — Worktrees do not isolate shared objects, refs, hooks, configuration, or arbitrary Git commands.** A shell-capable same-user agent can still fetch, alter shared refs/configuration, or target another checkout. This design prevents accidental working-file overlap, not adversarial Git access.

### Completion, handoff, resume, termination, and cleanup

**PROPOSAL — Completion retains output.** Return run ID, path, branch, base, current `HEAD`, dirty summary, and descendant state. Do not automatically integrate files or commits. Capture branch, head, and a path-safe status fingerprint after terminal proof; capture failure produces an uncertain retained state.

**PROPOSAL — Resume continues the same task in the same checkout.** Before pane/process creation, validate parent-scoped completed ownership, no live writer, record/session/loadout linkage, canonical private-root containment, common-dir identity, exact Git registration and lock, branch, expected `HEAD`, status fingerprint, and supported features. Any mismatch fails closed. A missing checkout is not recreated because that can hide lost uncommitted work.

**PROPOSAL — Termination does not mean cleanup.** Confirmed termination checkpoints and marks the checkout retained. Uncertain termination retains uncertain ownership. Parent exit, reload, session switch, or crash never unlocks/removes a checkout; restart reconstructs state from durable registries, Git porcelain, session claims, and mux evidence.

**PROPOSAL — Cleanup is explicit.** It requires terminal exact ownership, no active/uncertain descendants, correct canonical identities/registration/lock, and a clean worktree. It unlocks and uses ordinary non-force worktree removal. It retains the task branch, including committed work. Dirty output is never cleaned.

**PROPOSAL — Never automate broad/destructive Git maintenance.** No automatic prune, repair, force removal, broad unlock, state discard, stash, branch replacement, or branch deletion. Status may diagnose foreign, missing, moved, locked, prunable, and uncertain records; repair/adoption is a later operator workflow.

**PROPOSAL — Rollback is ownership recovery, not source-history rewriting.** Before process dispatch, a failed creation may undo only its exact clean checkout after revalidating ownership; any created task branch remains recorded for explicit operator review. After dispatch, retain the branch/worktree and report it. The source checkout is never rewritten; reverting an adopted task branch is an explicit operator action outside this lifecycle.

### Generated state, credentials, trust, and security

**FACT — Checkout separation covers files below each worktree only.** It does not isolate `$HOME`, environment variables, SSH agents/config, credential helpers, provider tokens, package/language caches, sockets, ports, containers, or services. Pi sessions are unique and cwd-organized, but global agent configuration can remain shared. [Pi sessions](https://github.com/earendil-works/pi/blob/b79e4cc834970cca69daebffab7df1da7d1e52c4/packages/coding-agent/docs/sessions.md), [environment variables](https://github.com/earendil-works/pi/blob/b79e4cc834970cca69daebffab7df1da7d1e52c4/packages/coding-agent/docs/environment-variables.md)

**PROPOSAL — Promise checkout isolation only.** Give each run private session/artifact/temp locations; never copy credentials, SSH keys, `.env`, trust stores, or normal history into the checkout. Preserve the existing explicit tool/extension sandbox. Per-run homes, caches, network policy, and secret brokerage are separate work.

**PROPOSAL — Trust follows the controller decision for one run.** If source project resources were trusted, use one-run approval for the exact managed checkout; otherwise use one-run denial. Do not save broad parent trust or mutate the user's trust store.

**PROPOSAL — Treat paths and Git output as hostile.** Prefer argument arrays, parse NUL-delimited porcelain, validate canonical containment and refs, reject ownership-boundary symlinks, use private permissions, and redact diagnostics. Task text and cosmetic names never become refs, paths, commands, or lock identities.

**FACT — Same-user children can tamper with same-user state.** Markers prevent bugs, not a malicious shell-capable child. Hostile repositories or unattended code require an OS/remote sandbox and scoped credentials. [Pi security](https://github.com/earendil-works/pi/blob/b79e4cc834970cca69daebffab7df1da7d1e52c4/packages/coding-agent/docs/security.md#running-untrusted-or-unmonitored-work)

## Runtime and portability

### tmux and Herdr

**FACT — tmux and Herdr are local terminal-surface adapters, not filesystem backends.** Lifecycle policy intentionally sits above adapters. [mux abstraction](https://github.com/gpmarques/pi-interactive-subagents/blob/eef62f9672b1e8fac4cf4ffff499ba304f0ce79f/pi-extension/subagents/mux.ts#L1-L75), [Herdr adapter](https://github.com/gpmarques/pi-interactive-subagents/blob/eef62f9672b1e8fac4cf4ffff499ba304f0ce79f/pi-extension/subagents/mux-adapters.ts#L237-L322)

**PROPOSAL — Provision before either local surface dispatches and pass the validated managed cwd into launch.** Keep worktree logic out of `mux-adapters.ts`; both backends must produce identical ownership and failure behavior.

### Vercel Sandbox

**FACT — A local linked worktree cannot be copied as a portable remote checkout.** Its gitfile points to local common administration. Remote execution needs clone/archive/bundle or another transfer protocol. [Git repository layout](https://git-scm.com/docs/gitrepository-layout)

**FACT — Vercel has a distinct persistent-sandbox/snapshot lifecycle, and private GitHub cloning needs explicit Git credentials.** [Persistent sandboxes](https://vercel.com/docs/sandbox/concepts/persistent-sandboxes), [snapshots](https://vercel.com/docs/sandbox/concepts/snapshots), [private repositories](https://vercel.com/kb/guide/sandbox-private-github-repositories)

**PROPOSAL — Vercel is not another pane adapter.** A remote controller must own sandbox/snapshot ID, source commit, remote checkout, scoped short-lived credentials, result/diff/commit transfer, questions, nested tasks, cancellation, resume, retention, and destruction. It should implement the same abstract task lifecycle using a remote clone/snapshot, not local `git worktree add`.

**UNKNOWN — Remote policy remains unresolved.** Reachable source, push authority, persistence entitlement, retention, artifact transfer, and secret brokerage require separate approval. Keep Vercel outside MVP and use the existing [viability brief](https://github.com/gpmarques/pi-interactive-subagents/blob/eef62f9672b1e8fac4cf4ffff499ba304f0ce79f/docs/research/vercel-sandbox-subagents-herdr-viability.md) as a separate input.

### Platforms

**FACT — Git porcelain is portable, but the current launcher emits POSIX shell scripts and relies on tmux/Herdr.** Worktree support alone does not provide Windows compatibility.

**PROPOSAL — MVP supports macOS and Linux local filesystems.** Test spaces, Unicode, symlinks, case-folding, gitfiles, and ordinary `.git` directories. Reject network/removable manager roots until tested. Windows remains unsupported pending launcher/path/lock design.

## Gate 1 approvals

| Decision | Approved decision |
|---|---|
| Boundary | Every recursively spawned task; root Pi is controller. Add pre-Pi launcher only if root is declared a task. |
| Owner | `pi-interactive-subagents` core; `pi-config` mandatory policy. |
| Base | Immediate caller's exact clean `HEAD`; no dirty inheritance. |
| Branch | Unique opaque task branch, retained by default. |
| Location | Private configurable external root, never nested in source repo. |
| Nested | Fresh sibling worktree at every depth; dirty parent fails. |
| Completion/handoff | Retain and report; no automatic integration. |
| Resume | Same checkout with exact identity/head/status validation. |
| Termination | Stop process only; retain output. |
| Cleanup | Explicit, terminal, exact-owner, clean, no-force; retain branch. |
| Submodules/LFS | Detected use hard-fails in MVP. |
| Non-Git cwd | Hard-fail; no shared-cwd fallback. |
| Trust | Mirror resolved parent decision for one run; do not persist broad trust. |
| Security | Checkout isolation only, not credential/process/ref isolation. |
| Platforms | macOS/Linux local; Windows and network/removable roots excluded. |
| Vercel | Separate future controller/protocol. |

## Bounded MVP

**PROPOSAL — In scope:**

1. Backend-neutral worktree lifecycle module integrated at spawn, settled result, resume, termination, list/status, teardown, and recovery boundaries.
2. Canonical Git identity and NUL-delimited worktree inventory.
3. Private external state, atomic registry, bounded cross-process locks, and Git lock reasons.
4. Clean-`HEAD`, branch-per-task provisioning for every local nested depth before dispatch.
5. Safe cwd mapping, one-run trust propagation, persisted identity, resume validation, and handoff metadata.
6. Retain-on-completion/termination and explicit safe cleanup without force or branch deletion.
7. tmux/Herdr parity on macOS/Linux.
8. Read-only reconciliation diagnostics for missing, moved, foreign, locked, prunable, active, terminal, and uncertain records.
9. `pi-config` wiring that makes isolation mandatory for supported project tasks.

**PROPOSAL — Out of scope:** package/catalogue promotion; generic user worktree management; dirty-state transfer; automatic merge/cherry-pick/push/fetch; destructive Git maintenance; submodules/LFS/bare/non-Git tasks; Windows; full home/cache/secret/network/process isolation; Vercel; root-controller provisioning unless Gate 1 expands scope.

## Acceptance criteria

1. **Per-task separation:** simultaneous siblings get distinct paths, branches, sessions, owners, and processes; same-file edits do not cross checkouts.
2. **Nested separation:** parent/child/sibling paths are distinct with durable lineage; immediate clean parent `HEAD` is base; dirty parent fails before leaks.
3. **Cwd and trust:** repository subdirectory maps to the same relative location in the child and resources follow recorded one-run trust.
4. **Layouts/paths:** main and linked sources, gitfile and directory layouts, spaces, Unicode, symlinks, and case folding pass on supported platforms.
5. **Crash consistency:** injected failure at each transition either rolls back only an exact pre-dispatch clean owner or leaves locked diagnosable state.
6. **Concurrency:** parallel launches/status/cleanup/resume have one durable owner, bounded locking, and never share a child session/worktree.
7. **Resume:** same path/session/loadout/branch resumes. Missing/repointed path, wrong common dir/registration/branch/head/status/lock, or live/uncertain owner launches nothing.
8. **Handoff:** result reports owner, path, branch, base, head, status, and descendants; dirty files and commits survive controller restart.
9. **Termination/teardown:** output is retained; uncertain state remains owned; exit/reload/session switch never removes or unlocks checkouts; restart reconstructs status.
10. **Cleanup:** active, uncertain, foreign, dirty, wrong-identity/branch/lock, and active-descendant cases fail; terminal clean owners remove normally and branches survive.
11. **Unsupported input:** dirty/untracked, unborn/bare, non-Git, detected submodule, and detected LFS fail before process launch with no shared-cwd fallback.
12. **Security:** task/name cannot inject path/ref/shell content; manager paths cannot escape; logs redact secrets; no credential/trust-store copy or mutation occurs.
13. **Backend parity:** lifecycle tests pass through tmux and Herdr on macOS/Linux, or unsupported combinations fail before provisioning.
14. **No escape hatch:** no implicit force, branch replacement/deletion, broad maintenance, or recursive deletion without exact ownership/containment proof.

## Hard failures

**PROPOSAL — Launch no process and stop further mutation when:**

- cwd is outside one supported non-bare Git worktree or relative mapping escapes/crosses identity;
- `HEAD` is absent, changes during provisioning, or source is staged/unstaged/untracked dirty;
- submodule or LFS use is detected;
- canonical source/common-dir/path identity cannot be proved consistently;
- path/ref collides, is foreign, lies outside private root, or crosses an ownership-boundary symlink;
- a required lock is unavailable, stale/ambiguous, or lock order is violated;
- creation requires force, branch replacement, network access, or yields an unvalidated checkout;
- durable intent, registry, session, or loadout cannot be written and reread exactly;
- trust mode cannot be derived;
- resume identity/registration/branch/head/status/lock/session/loadout differs;
- cleanup cannot prove terminal, exact, clean, descendant-safe ownership;
- dispatch/termination becomes uncertain after activation—in that case retain and report;
- remote execution is selected without a durable remote lifecycle protocol.

## Gaps and risks

- **APPROVED (GATE 1) — Dirty-state ergonomics:** clean-parent policy may block delegation after editing starts; snapshots remain a separate future feature.
- **APPROVED (GATE 1) — Task branches and retention:** MVP accumulates task branches. The branch choice and retention policy are accepted; later GC still needs merge/reachability/retention proof and an explicit design.
- **UNKNOWN — Hooks/filters:** checkout hooks, non-LFS filters, sparse/partial clones, alternates, and unusual configuration need fixtures before broad claims.
- **UNKNOWN — Generated state:** ignored dependencies are not inherited; child-generated ignored files disappear on explicit cleanup. Reproducible setup/cache policy is separate.
- **UNKNOWN — Recovery UX:** adoption of external edits, stale-lock resolution, and moved-worktree repair need later operator design. MVP diagnoses only.
- **UNKNOWN — Root semantics and Vercel:** both require lifecycle outside the present child extension boundary.
- **FACT — Shared Git administration and same-user permissions remain the central security limitation.**

## Sources

### Kept

- [Git `git-worktree`](https://git-scm.com/docs/git-worktree) — creation, shared/per-worktree state, locks, porcelain, cleanup safeguards, recovery, and submodules.
- [Git `git-rev-parse`](https://git-scm.com/docs/git-rev-parse) and [repository layout](https://git-scm.com/docs/gitrepository-layout) — canonical identity and gitfile/common-dir structure.
- [Pi 0.84.4 release](https://github.com/earendil-works/pi/releases/tag/v0.84.4), pinned [extensions](https://github.com/earendil-works/pi/blob/b79e4cc834970cca69daebffab7df1da7d1e52c4/packages/coding-agent/docs/extensions.md), [sessions](https://github.com/earendil-works/pi/blob/b79e4cc834970cca69daebffab7df1da7d1e52c4/packages/coding-agent/docs/sessions.md), [session format](https://github.com/earendil-works/pi/blob/b79e4cc834970cca69daebffab7df1da7d1e52c4/packages/coding-agent/docs/session-format.md), and [security](https://github.com/earendil-works/pi/blob/b79e4cc834970cca69daebffab7df1da7d1e52c4/packages/coding-agent/docs/security.md) — version-pinned Pi contract.
- [`pi-interactive-subagents` lifecycle at `eef62f9`](https://github.com/gpmarques/pi-interactive-subagents/tree/eef62f9672b1e8fac4cf4ffff499ba304f0ce79f/pi-extension/subagents) — current launch, nested, registry, resume, termination, and local backend behavior.
- [Vercel persistence](https://vercel.com/docs/sandbox/concepts/persistent-sandboxes), [snapshots](https://vercel.com/docs/sandbox/concepts/snapshots), and [private repository guidance](https://vercel.com/kb/guide/sandbox-private-github-repositories) — primary remote lifecycle/credential constraints.
- Local [`pi-config` system map](../system-maps/pi-config-overview.md) and [Vercel/Herdr viability brief](https://github.com/gpmarques/pi-interactive-subagents/blob/eef62f9672b1e8fac4cf4ffff499ba304f0ce79f/docs/research/vercel-sandbox-subagents-herdr-viability.md) — repository-specific boundaries.

### Dropped

- Earlier package-first promotion direction — explicitly superseded; it answers deployment, not per-task isolation.
- Generic tutorials and agent-framework blogs — primary Git/Pi sources are stronger.
- Unversioned Pi docs where 0.84.4 source exists — excluded to avoid drift.
- Git LFS anecdotes — insufficient to establish this integration's lifecycle, so LFS remains unvalidated.
- Vercel marketing examples without ownership/resume/credential detail — insufficient for design decisions.
