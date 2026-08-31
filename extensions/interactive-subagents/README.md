# Interactive subagents

The implementation lives in a separate repository and is not vendored into `pi-config`:

- **Maintained fork:** [gpmarques/pi-interactive-subagents](https://github.com/gpmarques/pi-interactive-subagents)
- **Upstream lineage:** [amosblomqvist/pi-interactive-subagents](https://github.com/amosblomqvist/pi-interactive-subagents)

## Reviewed fork evidence

The behavioral facts in this stub were source-verified on **2026-08-31** against the fork endpoint [`b403b02484aa545b72a0a852aee9ecce524fa6f8`](https://github.com/gpmarques/pi-interactive-subagents/commit/b403b02484aa545b72a0a852aee9ecce524fa6f8), whose commit timestamp is **2026-08-30T20:59:06-03:00**. At that endpoint, package metadata reports version 3.7.2, still credits the upstream repository, and declares `@earendil-works/pi-coding-agent`, `@earendil-works/pi-tui`, and `typebox` as `"*"` peer dependencies, while the reviewed implementation contains the fork-specific tmux/Herdr lifecycle and web-capability hardening described below. The commit pin is a reproducible evidence boundary, not a claim about later branch state or any local worktree.

It provides asynchronous Pi subagents on tmux or Herdr terminal surfaces. Subagents can run concurrently, report live status, ask the orchestrator questions, receive completion results through parent follow-up turns, and be messaged, resumed, or killed by a persistent parent-scoped name. Agent profiles use explicit tool and nested-spawn allowlists; completed sessions retain their original sandbox when resumed.

## No bundled parent shell guard

`pi-config` no longer supplies a local shell-guard extension. Independently of that removal, the reviewed fork's restricted Pi children launch with `--no-extensions` and explicit tool/extension allowlists, so a separately installed parent extension would not be inherited. Bundled profiles listing `bash` use Pi's built-in tool without a fork-provided guard. Only `researcher` lists the fork's distinct `safe_bash` tool; no other bundled profile receives it. Parent-process shell protection must not be described as subagent protection.

## Researcher web access

At the reviewed endpoint, the fork's bundled `researcher` is the only bundled profile with web access. Its profile tools are exactly `web_search`, `fetch_content`, `get_search_content`, `source_check`, and `safe_bash`; the normal child-only `ask_question` support is added by the subagent runtime. Every other bundled profile omits all four web tools, including `worker`, which delegates external research to `researcher`.

The implementation is not supplied by this stub. Install the separately managed package:

```bash
pi install npm:pi-web-access
```

Restricted children still launch with ambient discovery disabled (`--no-extensions`) and an explicit `--tools` allowlist. For any of the four web tools, the fork requires exactly one unfiltered string `"npm:pi-web-access"` in the effective child agent directory's `settings.json`, then resolves only `<agent-dir>/npm/node_modules/pi-web-access`. It accepts exactly the verified `pi-web-access@0.27.0`, reads its single concrete `pi.extensions` entry, and requires the four canonical tools to remain enabled and unrenamed in `web-search.json`. Package, manifest, entrypoint, settings, and config paths must be canonical and contained; symlinks at those checked paths are rejected. The resolver neither scans unrelated global packages nor falls back to a stale package beside Pi's installation.

Before creating any researcher terminal surface, the fork starts a bounded fresh Pi RPC process in the exact child cwd and effective agent/package environment. It uses offline/no-session mode, `--no-extensions`, the exact four-tool allowlist, the canonical entrypoint, and a private inspector; only RPC state is queried. Pi's active tools must equal all four canonical names. Extension errors, zero/partial/renamed registration, malformed or unavailable state, nonzero exit, or the 5-second timeout fail closed and clean up the detached process group and nonce-bound temporary snapshot. This creates no persistent session or prompt and performs no model/provider or web call. The reviewed fork evidence records roughly 0.25–0.30 seconds for this preflight on its verified installation; that timing is evidence from the pinned review, not a portable performance guarantee.

Saved restricted loadouts are validation records, not copies of runnable old code. They retain the canonical entrypoint path/digest, package root/name/version and manifest digest, and complete/relevant `web-search.json` identity. Resume verifies those recorded fields before the same offline probe and again afterward; drift or a legacy record missing required identity fails before creating a surface. Treat every package or config update as requiring a fresh child. This focused guarantee does not hash the complete package/dependency tree or npm lock, so same-version helper or dependency mutation that leaves the recorded fields unchanged is outside the resume-identity guarantee.
