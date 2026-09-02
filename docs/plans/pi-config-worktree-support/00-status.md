# Status: pi-config worktree support

- Gate 1 — Product: APPROVED 2026-09-01
- Gate 2 — Architecture: APPROVED 2026-09-01
- Gate 3 — Program Design: APPROVED 2026-09-01
- Gate 4 — Slice plan: APPROVED 2026-09-01
- Next phase — Implementation Slice 1: authorized, not started

## Slices
- [ ] Slice 1 — required-mode direct task tracer
- [ ] Slice 2 — recursive direct/nested cwd isolation
- [ ] Slice 3 — exact resume, kill retention, and reload continuity
- [ ] Slice 4 — family inventory, reconciliation, and safe cleanup
- [ ] Slice 5 — release-candidate same-file isolation proof
- [ ] Slice 6 — mandatory activation, repository documentation, and rollback proof

## Notes for a fresh session
Gates 1–4 are approved as of 2026-09-01. The next phase is implementation Slice 1, which is authorized but not started; all six slices remain unchecked and no implementation is claimed. The implementation baseline is `pi-interactive-subagents` commit `9388cc9634eee84601ce7ee4b7d1cb648040d684`, plus `pi-config` baseline `c5bfcfd81ee2b386d5c06103264d25307889eef2`, Pi 0.84.4, and Git 2.36.0 or newer.

Scope is one isolated project Git worktree for every spawned subagent task, including nested tasks; the top-level controller remains in the user's checkout. Dirty, ambiguous, or unsupported sources fail closed with no shared-cwd fallback. Finished/stopped work is retained; cleanup is explicit, exact, clean-only, non-forceful, and branch-retaining. There is no automatic integration/publication, branch deletion, expiry, GC, broad scan, Vercel, Windows, remote execution, or top-level controller provisioning.

The built-in manager root is `/Users/guilhermemarques/.local/share/pi-interactive-subagents/worktrees`; it is created when absent and validated as a canonical, current-user-owned, non-symlinked mode-`0700` directory outside source/common directories. `PI_SUBAGENT_WORKTREE_ROOT` is an optional absolute-path override subject to the same validation. No shell or environment persistence is required, and no configuration decision remains open.

Implementation follows `04-slices.md` one slice at a time. Slice 1 must land the atomic throwing/read-back-verified loadout writer together with direct required-mode activation, or land the writer first only as an inert tested primitive. The checked-in example and global pin remain unchanged until Slice 6. A worker owns removal of the derived Gate 3 HTML; do not recreate it.
