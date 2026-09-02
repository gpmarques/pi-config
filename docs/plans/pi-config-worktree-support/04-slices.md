# Vertical Slices: isolated Git worktrees for spawned tasks

Gates 1–4 were approved on 2026-09-01. Implementation Slice 1 is authorized and is the next phase; it has not started. All six slices remain incomplete.

## Release boundary and fixed configuration

Start from `pi-interactive-subagents` `9388cc9634eee84601ce7ee4b7d1cb648040d684` and `pi-config` `c5bfcfd81ee2b386d5c06103264d25307889eef2`. Until Slice 6, new behavior is reachable only under literal `worktrees.mode = "required"`; the example/global install remain unchanged, and unavailable capabilities reject before surface creation without shared-cwd fallback. Slice 6 activates only after direct, nested, resume, reload, inventory/cleanup, deterministic-race, exact 10×5 same-file, and local-backend proofs pass.

Built-in root: `/Users/guilhermemarques/.local/share/pi-interactive-subagents/worktrees`. Create when absent; validate current-user ownership, canonical/non-symlink path, source/common-directory separation, and mode `0700`. `PI_SUBAGENT_WORKTREE_ROOT` is an optional absolute override with identical validation. No environment persistence or configuration decision remains open.

Gate 3 is normative for exact interfaces, transitions, Git commands, manifest, loadout, authority, cleanup, and tests. Preserve landed reload seams in `index.ts`, the existing `.loadout.json` in `session.ts`, config loading in `status.ts`, and narrow mux adapters.

## Slice 1 — Required-mode direct task tracer

- **Outcome:** direct task runs in a locked worktree, changes a tracked file without changing controller, and completes retained; provisioning/loadout failures create no session/surface.
- **Files/interfaces:** new `worktree-manager.ts` direct lifecycle (`provision`, bind/dispatch, rollback, checkpoint, manifest, root/default, Git check); `index.ts` managed ordering/workspace result; `session.ts` durable workspace plus atomic throwing/read-back-verified writer; new manager/lifecycle tests.
- **Proof:** focused direct/root/manifest/atomic tests, public direct lifecycle/controller-byte test, landed reload test, `npm test`, `git diff --check`.
- **Stop:** Pi/Claude bind only verified loadouts; retained direct manifest and all no-surface failures pass; nested/resume/inventory/cleanup still reject.
- **Rollback:** revert Slice 1 only; no global/example change; retain non-test work.
- **Commits:** (1) `feat: launch direct required-mode tasks with verified workspace loadouts`—writer and activation together; (2) `test: prove direct completion retains work without touching controller`. An inert tested writer may precede activation, but no worktree dispatch may use the best-effort writer.

## Slice 2 — Recursive direct/nested cwd isolation

- **Outcome:** direct alternate-repository cwd works; nested tasks stay inside immediate caller/family and clean caller `HEAD`; same tracked file remains isolated; invalid/dirty/unsupported requests launch nothing.
- **Files/interfaces:** `worktree-manager.ts` nested authority-before-cwd, mappings/checks/lineage; `index.ts` explicit `direct | nested` authority; manager/lifecycle/registry tests.
- **Proof:** focused nested/authority/cwd/dirty tests, parent-child same-file test, registry tests, all hermetic tests, `git diff --check`.
- **Stop:** every direct/nested cwd rule and safe rollback/refusal passes.
- **Rollback:** revert Slice 2; retain records/worktrees.
- **Commits:** authority validation; nested launch; unsupported/dirty/cross-family tests.

## Slice 3 — Exact resume, kill retention, and reload continuity

- **Outcome:** exact unchanged task resumes in same workspace/session; content drift refuses; kill retains; landed reload handoff delivers/checkpoints once.
- **Files/interfaces:** manager `claimResume`/cancel/exact manifest checks; `index.ts` resume/kill plus `RunningSubagent` handoff v2 fields; `session.ts` identity agreement; resume/kill/reload/manifest tests.
- **Proof:** manager manifest/resume tests; lifecycle resume/kill tests; landed reload suite; all hermetic tests.
- **Stop:** all normal/pending/mismatch paths have one state and no duplicate checkpoint.
- **Rollback:** no live children before v2 revert; disable spawning; retain work.
- **Commits:** exact resume; kill retention; handoff v2.

## Slice 4 — Family inventory, reconciliation, and safe cleanup

- **Outcome:** fresh top-level session lists one family; nested callers see descendants; exact terminal clean cleanup removes worktree but keeps branch/tombstone; unsafe targets refuse.
- **Files/interfaces:** manager `reconcile`/`list`/`cleanup` and three races; `index.ts` exact public tools; mux/adapters only `probeSurface`; manager/lifecycle/registry tests.
- **Proof:** inventory/cleanup/reconcile/race tests in both forced orders; public fresh-session/subtree tests; full hermetic suite.
- **Stop:** authorization, refusal, partial uncertainty, clean cleanup, tombstones, and races pass without sleeps.
- **Rollback:** revert tools/probe without mutating records.
- **Commits:** family inventory; exact cleanup; deterministic races.

## Slice 5 — Frozen release-candidate isolation proof

After Slice 4 record clean `PRODUCTION_CANDIDATE_SHA`. Slice 5 changes only `test/worktree-lifecycle-hermetic.test.ts`, `test/integration/mux-lifecycle-smoke.test.ts`, supplemental `test/integration/subagent-lifecycle.test.ts`, and `package.json`; production diff remains empty. Record clean `SLICE5_PROOF_SHA`. A production defect reopens its owning Slice 1–4 with named files and focused fix/regression commit, then Slice 5 restarts from command 1 against new SHAs.

- **Outcome:** 10 rounds × (3 direct + 2 nested) overwrite the same tracked file with distinct bytes; controller/all worktrees match expected bytes before/during/after; tmux and Herdr pass.
- **Proof, unconditional at current SHA:** exact named 10×5 test; manager/lifecycle/reload/registry/resume/kill and complete hermetic suites; `npm test`; `test:integration:surface`; `test:integration:lifecycle-smoke`; clean tree, exact SHA, empty production diff, `git diff --check`.
- **Provider:** supplemental `test:integration:lifecycle`; record current-SHA PASS/FAIL or **NOT RUN — credentials/provider unavailable**. Never substitute prior evidence or waive mandatory gates.
- **Stop:** all 50 tasks, races, hermetic gate, and both local backends pass at exact SHA.
- **Rollback:** revert test/package commits if harness wrong; production defects invalidate and restart Slice 5.
- **Commits:** exact 10×5 test; tmux/Herdr smoke; supplemental provider coverage.

## Slice 6 — Mandatory activation, docs, and rollback proof

- **Outcome:** exact reviewed fork globally active with required isolation and built-in root/optional override; users inventory/clean and can disable safely.
- **Entry:** exact current-SHA 10×5 and both local-backend gates passed with no production drift.
- **Files/interfaces:** fork manager/index final fail-closed boundary/default root; `config.json.example`; fork README/system map; `pi-config` integration README/root README/system map; status after proof. No GC/Vercel/Windows/remote/dashboard/daemon/refactor/derived HTML.
- **Activation:** validate built-in `0700` root (or optional override); stop Pi/children; back up settings/packages; install exact pin filtered off; audit/rehearse disabled rollback; enable and smoke direct/nested/resume/reload/inventory/cleanup while byte-checking controller; record SHA/versions/root/evidence/backup.
- **Proof:** rerun mandatory policy, exact 10×5, reload, full hermetic, tmux, Herdr, and docs/pin consistency at current SHA.
- **Stop:** one pin/root; all lifecycle smoke; emergency disable; filtered rollback has no tools; docs agree; no implicit deletion.
- **Rollback:** emergency-disable, stop, filter extension off, prove tools absent, then restore any old pin still disabled; preserve all roots/records/worktrees/branches/sessions.
- **Commits:** final mandatory/default-root boundary; fork docs/evidence; `pi-config` pin/docs; operational activation has no code commit.

## Dependencies

```text
1 direct → 2 nested → 3 resume/kill/reload → 4 inventory/cleanup
  → 5 frozen proof → 6 mandatory activation/docs/rollback
```

After each implemented slice, run its proof, check only that slice in `00-status.md`, and ask `Continue to slice N+1, or re-steer?`

## Decisions and risks

No decisions remain open. Prevent early activation via the required-mode boundary; horizontal growth by implementing only exercised Gate 3 interfaces; reload regression via landed tests; weak isolation proof via six-location same-file comparisons; Slice 5 drift via frozen SHAs; unsafe rollback via extension filtering before old pins; unavailable provider access via honest current-SHA NOT RUN without affecting mandatory hermetic/local gates.
