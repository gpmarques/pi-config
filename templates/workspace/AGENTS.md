# {{WORKSPACE_NAME}} workspace

## Organization

```text
{{WORKSPACE_NAME}}/
├── AGENTS.md
├── data/
├── docs/
├── projects/
│   └── <project>/
└── worktrees/
    └── <project>/
        └── <branch-or-task>/
```

- `docs/` is for workspace-level, cross-project research, plans, architecture
  notes, and decisions.
- `data/` is for workspace-level, cross-project datasets, experiment
  inputs/outputs, and shared artifacts.
- `projects/` contains the canonical checkout for each project. Each project owns
  its `.git` metadata, dependencies, configuration, and project-level guidance.
- `worktrees/` contains linked Git worktrees created from repositories under
  `projects/`. Group them by project and use a short branch or task name.
- Project-specific documentation and data should remain in the owning project
  when they belong in that project's history.

## Orchestration mode

Operate from the workspace as a coordinator:

1. Identify the target project before reading, editing, or running commands.
2. Use the target project or worktree as the explicit working directory.
3. Keep independent tasks isolated; use a dedicated worktree when work may
   conflict with another task or branch.
4. Delegate bounded, independent investigation when useful, but integrate and
   verify all results in the primary task context.
5. Do not modify multiple projects or create cross-project coupling unless the
   request explicitly requires it.
6. Never push, force-push, publish, delete branches, or remove worktrees without
   explicit approval.

## Simplicity and YAGNI

- Choose the smallest solution that satisfies the current verified need; future
  vision is context, not current requirements.
- Reuse existing or native capabilities before wrapping or reimplementing them.
- Do not add speculative frameworks, generalization, configuration, or recovery
  paths unless they are demonstrably needed.
- For nontrivial design, compare simpler alternatives and apply the
  small-interface and deletion tests; do not turn trivial edits into ritual
  multi-agent design.
- Remove pass-through layers that add no leverage. Keep changes, reviews, and
  tests bounded to current acceptance criteria, and track optional future
  hardening separately.
- Simplicity never excuses dropping verified correctness or security
  requirements.

## Verify; do not assume

Do not assume — verify. Verify critical facts rather than guessing. And ask me, if you cannot verify something. Only begin once you are 100% sure of what to do. If you catch yourself being even slightly unsure, that's a sign to check first.
