# Interactive subagents

The implementation lives in a separate repository and is not vendored into `pi-config`:

- **Workspace fork:** [gpmarques/pi-interactive-subagents](https://github.com/gpmarques/pi-interactive-subagents)
- **Upstream:** [amosblomqvist/pi-interactive-subagents](https://github.com/amosblomqvist/pi-interactive-subagents)

In this workspace, the fork is checked out beside `pi-config` as `pi-interactive-subagents/`.

It provides asynchronous Pi subagents on tmux or Herdr terminal surfaces. Subagents can run concurrently, report live status, ask the orchestrator questions, receive completion results through parent follow-up turns, and be messaged, resumed, or killed by a persistent parent-scoped name. Agent profiles use explicit tool and nested-spawn allowlists; completed sessions retain their original sandbox when resumed.
