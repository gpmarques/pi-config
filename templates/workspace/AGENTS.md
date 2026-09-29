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

Operate from the workspace as a pure high-level orchestrator:

1. Identify the target project before reading, editing, or running commands.
2. Use the target project or worktree as the explicit working directory.
3. Keep independent tasks isolated; use a dedicated worktree when work may
   conflict with another task or branch.
4. Outsource mechanical work—including file exploration, code reading, and
   implementation—to subagents; integrate and verify their results in the
   primary task context.
5. Keep the primary agent's context lean so its reasoning stays sharp; avoid
   bloating it by reading code directly.
6. Do not modify multiple projects or create cross-project coupling unless the
   request explicitly requires it.
7. Never push, force-push, publish, delete branches, or remove worktrees without
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

## Project tooling

Existing project guidance and configuration take precedence. Respect the current
manifest, runtime targets, lockfile, and established test commands. Do not
migrate Poetry, PDM, npm, pnpm, yarn, Node, or established test suites
automatically. Run commands from the owning task worktree and prefer existing
project scripts.

### New Python projects

- Default to `uv` managing `pyproject.toml`, `uv.lock`, and a local `.venv`.
- Use Ruff for linting and formatting, ty for type checking, and pytest for
  tests. Keep development tools declared as project-local dependencies.
- Treat `pyproject.toml` and `uv.lock` together as the authoritative dependency
  definition.
- For projects configured with these tools, representative checks are:

  ```sh
  uv sync --locked
  uv run --locked ruff check <paths>
  uv run --locked ruff format --check <paths>
  uv run --locked ty check <paths>
  uv run --locked pytest <paths>
  ```

### New TypeScript projects

- Default to TypeScript with Bun for dependencies, runtime, and tests; use Biome
  for linting and formatting, and `tsc --noEmit` for static checking.
- Bun runs and transpiles TypeScript but does not type-check it. Verify runtime
  and deployment compatibility before choosing Bun.
- Keep development tools declared as project-local dependencies. Treat
  `package.json` and the Bun lockfile together as authoritative.
- Where the project defines the corresponding scripts, representative commands
  are `bun install --frozen-lockfile` (with an existing lockfile), then
  `bun run lint`, `bun run format:check`, `bun run typecheck`, and
  `bun run test`. Do not assume those script names exist.

### Dependency and check discipline

- Use normal manager commands intentionally when first creating a lockfile or
  changing dependencies. Do not bypass stale locks or mix package managers.
- Do not use global installs without approval. Do not commit `.venv`,
  `node_modules`, or tool caches.
- Keep checks separate from autofix operations. Scope formatting and fixes to
  touched files, and report checks that could not run rather than claiming
  success.

## Verify; do not assume

Do not assume — verify. Verify critical facts rather than guessing. And ask me, if you cannot verify something. Only begin once you are 100% sure of what to do. If you catch yourself being even slightly unsure, that's a sign to check first.
