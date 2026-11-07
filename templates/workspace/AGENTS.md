# {{WORKSPACE_NAME}} workspace

## Organization

- `docs/`: workspace-level, cross-project research, plans, architecture, and decisions.
- `data/`: workspace-level datasets, experiment inputs/outputs, and shared artifacts.
- `projects/<project>/`: canonical checkouts; each owns its Git metadata,
  dependencies, configuration, guidance, and project-specific docs/data.
- `worktrees/<project>/<branch-or-task>/`: linked worktrees from `projects/`.

## Orchestration mode

This is a pure high-level orchestrator session. Outsource mechanical work — file exploration, code reading, implementation — to subagents. Keep your own context window lean so your reasoning stays sharp; do not bloat it by reading code yourself.

- Identify the target project before reading, editing, or running commands;
  use that project or task worktree as the explicit working directory.
- Keep independent tasks isolated; use a dedicated worktree when work may conflict.
- Integrate and verify subagent results in the primary task context.
- Do not modify multiple projects or create cross-project coupling unless requested.
- Never push, force-push, publish, delete branches, or remove worktrees without
  explicit approval.

## Communication

For explanations, summaries, overviews, or any communication of ideas for any reason, use both `simple-english` and `show-me` skills.
For `show-me`, presenting directly in chat is enough. HTML is not required.

## Simplicity and YAGNI

- Choose the smallest solution for the current verified need, not future vision.
- Reuse existing/native capabilities; avoid speculative frameworks,
  generalization, configuration, or recovery paths.
- For nontrivial design, compare simpler alternatives and apply small-interface
  and deletion tests; do not ritualize trivial edits with multi-agent design.
- Remove pass-through layers that add no leverage. Bound changes, reviews, and
  tests to acceptance criteria; track optional hardening separately.
- Never drop verified correctness or security requirements for simplicity.

## Project tooling

Existing project guidance and configuration take precedence. Respect manifests,
runtime targets, lockfiles, and established test commands; do not automatically
migrate package managers, runtimes, or test suites. Prefer existing project scripts
and run them from the owning task worktree.

### New Python projects

- Default to `uv`, `pyproject.toml`, `uv.lock`, and a local `.venv`;
  the manifest and lockfile together define dependencies.
- Use Ruff for lint/format, ty for type checking, and pytest for tests;
  declare development tools as project-local dependencies.

### New TypeScript projects

- Default to TypeScript with Bun for dependencies, runtime, and tests;
  Biome for lint/format; `tsc --noEmit` for static checking.
- Bun transpiles but does not type-check. Verify runtime/deployment compatibility.
- Declare development tools locally; `package.json` and the Bun lockfile together
  define dependencies. Verify scripts exist before running them.

### Dependency and check discipline

- Use normal manager commands to create/change locks and dependencies;
  do not bypass stale locks or mix package managers.
- No global installs without approval; never commit `.venv`, `node_modules`, or caches.
- Separate checks from autofix; scope fixes/formatting to touched files.
  Report checks that could not run; never claim unverified success.

## Verify; do not assume

Do not assume — verify. Verify critical facts rather than guessing. And ask me, if you cannot verify something. Only begin once you are 100% sure of what to do. If you catch yourself being even slightly unsure, that's a sign to check first.
