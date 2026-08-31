# System Map: `pi-config` coarse overview

**Question:** How does this repository extend Pi, and what are its main boundaries and operating assumptions?
**Boundary:** The active `extensions/` and `skills/` trees, their setup dependencies, the external-extension stubs, and the `deprecated/` archive. Linked external repositories are not analyzed beyond the metadata and documentation needed to verify the `pi-web-access` stub and the published `pi-observational-memory` 3.0.4 package used by its stub.
**Horizon:** Selecting and running pieces of this snapshot with a current Pi installation.
**Evidence basis:** Static inspection of the current repository snapshot; `pi-web-access` repository metadata, README, package/Pi manifest, and license on its `main` branch; published `pi-observational-memory` 3.0.4 metadata and source plus a local-only Pi/llama.cpp runtime and worker smoke test; and a local-only exercise of the `web-debug` command workflow with installed `agent-browser` 0.18.0. Runtime compatibility of the remaining components was not tested.

## At a glance

`pi-config` is a personal, selectively adopted configuration catalogue, not an installable monolith. Its active layer contains five local functional extension implementations and four local skills; three additional extension folders are documentation pointers to external repositories. Users copy only the local capability they want or follow an external stub to its authoritative installation instructions.

That keeps the active tool surface and context cost controllable, but shifts integration, updates, credentials, and compatibility checks onto the user.

## Causal path

```text
A user selects one catalogue entry
  → for a local implementation, copies it into ~/.pi/agent/extensions or ~/.pi/agent/skills
    or, for an external stub, follows the linked project's installation instructions
  → satisfies that component's dependencies and configuration
  → reloads or restarts Pi as relevant
  → the selected implementation contributes tools/events/UI or a skill playbook
```

The path is conditional: the local browser extension also needs Chromium, `web-debug` needs an external `agent-browser` executable, PDF reading needs a PyMuPDF virtual environment, and YouTube transcripts need `yt-dlp`. The `web-access/` stub has no runtime surface or local setup; installation, provider configuration, credentials, and compatibility are owned by `pi-web-access` upstream. The `observational-memory/` stub likewise registers nothing locally, but documents its reviewed npm pin and an explicitly manual, loopback-only Qwen/llama.cpp worker setup. This repository deliberately supplies no root package manifest or one-command installer.

## Parts

### Functional extensions

| Extension | Surface | Role |
|---|---|---|
| `ask-user-question.ts` | `ask_user_question` tool | Structured text, single-choice, and multi-choice user prompts, serialized through a shared UI lock. |
| `bash-guard/` | `tool_call` gate, `/bash-guard`, two flags | Prompts before broad classes of shell risk in interactive sessions and hard-blocks catastrophic patterns in subagents or autonomous mode. |
| `browser/` | Eight `browser_*` tools, `/browser` | Drives one persistent Playwright page and captures bounded console/network buffers; tools are inactive until `/browser on`. |
| `custom-header.ts` | startup event, `/builtin-header` | Replaces the TUI header with a custom Pi logo. |
| `prompt-snippets/` | input transform, `/snippets`, `Alt+S` | Applies selected one-shot Markdown instructions before or after the next user message. |

`interactive-subagents/`, `observational-memory/`, and `web-access/` are README-only stubs pointing to separate repositories, not local implementations. `observational-memory/` points specifically to `elpapi42/pi-observational-memory` and documents the pinned V3 npm package, its branch-local session ledger, and the verified manual local-model command; it is not the different parallel-observer implementation. `web-access/` replaces the former local `web-fetch/` and `web-search/` catalogue entries with a reference to external `pi-web-access`, which provides web search and content retrieval at a high level.

### Skills

- `analyze-sessions/`: read-only Python utilities for session cost, prompt, transcript, and search analysis.
- `pdf-reader/`: a text-plus-rendering workflow backed by PyMuPDF scripts.
- `web-debug/`: a runtime-first frontend debugging playbook that drives the external `agent-browser` CLI through bash, using explicit isolated sessions and request-only network evidence.
- `youtube-transcript/`: a `yt-dlp`-backed title and English-caption extractor.

### Archive

`deprecated/` keeps nine older extensions and three older skills for reference. They are outside the advertised active setup; their presence preserves ideas without loading them when users follow the copy-only workflow.

## Generated behavior

- **Runtime-observation surfaces:** `web-debug` uses installed `agent-browser` to reproduce → observe → hypothesize → verify live frontend behavior, while the optional local `browser_*` extension remains a separate automation surface. Static web search and retrieval are no longer implemented locally; the `web-access/` stub registers nothing unless the external package is separately installed.
- **Context-economy loop:** browser tools start inactive and prompt snippets reset after one message, so uncommon guidance does not continuously consume the system prompt. Users opt in again when the capability becomes relevant.
- **Manual-integration loop:** independent copying of local modules and upstream-managed installation of external packages limit this repository's blast radius, but every fresh machine or upstream change leaves setup and compatibility decisions with the user. The repository is a catalogue, not a synchronization mechanism.

## Causal regimes

- **Does adopting a catalogue entry expose its declared Pi surface in this snapshot? — Complicated, medium confidence:** local registration paths are statically visible, while external stubs are non-executable and depend entirely on separately installed upstream packages; successful loading still depends on Pi API compatibility and dependencies. **Classification challenge:** Clear, if current-version smoke tests repeatedly load each local component and each adopted external package. **Discriminator:** run isolated load and minimal invocation tests against the target Pi version.
- **Does `bash-guard` prevent all destructive agent actions during a session? — Clear, high confidence (answer: no):** it intercepts only `bash` tool calls, and its protection changes by interactive/subagent/disabled mode; edits, writes, user shell commands, and unrecognized command shapes remain outside that gate. **Classification challenge:** Complicated, if shell parsing or Pi event ordering changes the observed boundary. **Discriminator:** adversarial tests across every mutation surface and execution mode.
- **Does the modular copy workflow reduce always-on context cost? — Complicated, medium confidence:** browser tools explicitly leave the active set until enabled and snippets are one-shot, but total prompt impact from a real selected configuration is unmeasured. **Classification challenge:** Complex, if model/tool selection behavior changes materially as combinations vary. **Discriminator:** compare system-prompt tokens and task behavior across representative module combinations.

## Established

- **Catalogue, not package:** the README says not to install the repository as one package, documents per-resource copying, and distinguishes external stubs from local implementations (`README.md`, introduction and setup sections).
- **Five local extension implementations:** their entry points and registrations are under `extensions/`; the other three extension directories contain only README pointers to external repositories.
- **Selective safety and context controls:** `extensions/bash-guard/index.ts` documents its mode-specific gate; `extensions/browser/index.ts` removes all eight tools from the active set by default; `extensions/prompt-snippets/index.ts` clears enabled snippets after input.
- **Per-module setup:** npm manifests exist only beside `bash-guard` and `browser`; external requirements, including `agent-browser` for `web-debug`, are listed in `README.md` and the relevant skill documents. External-stub implementations remain upstream-owned; the observational-memory stub records the reviewed npm 3.0.4 pin and machine-specific local runtime integration without vendoring it.
- **Mixed Pi API namespaces:** three active extension entry points import the older `@mariozechner/*` packages, while `browser` and `prompt-snippets` import `@earendil-works/*` (`extensions/**/*.ts`, import declarations).
- **No repository-level validation harness:** the tracked tree contains no test suite, continuous-integration configuration, root package manifest, or lockfile.

## Hypotheses

- **Optimized for high-agency interactive use:** UI clarification, shell confirmation, one-shot prompting, and live browser inspection suggest the author values autonomy with selective human control. **Falsifier:** usage instructions or telemetry showing these modules are primarily run headlessly without interaction.
- **Manual selection is intended to prevent configuration bloat:** the copy-only instruction and default-off browser gate point in this direction. **Falsifier:** an omitted canonical installer or sync workflow that routinely installs the full active tree.
- **Namespace mixing may create current-version load failures:** the repository appears to span a Pi package rename. **Falsifier:** loading all five local extensions successfully against the intended current Pi runtime without compatibility aliases or edits.

## Fog

- **Current runtime compatibility:** Published `pi-observational-memory` 3.0.4 was loaded and exercised in isolation against Pi 0.84.4 with local llama.cpp 9430; compatibility of the five local functional extensions and the other external stubs still needs isolated smoke tests.
- **Actual adopted subset:** The observational-memory npm package is confirmed globally adopted for the documented machine; a complete comparison with the user's global extension and skill directories is still needed because repository contents alone do not show the full active set.
- **External package drift and security:** `web-access/` intentionally does not pin or vendor `pi-web-access`; its provider, credential, storage, and network behavior can change independently. Observational memory is pinned to npm 3.0.4, but its model-generated records, session/clipboard storage, session-model fallback, and accepted lifecycle/empty-compaction behavior still form a trust boundary. **Needed:** review each installed upstream version and its current documentation before changing a pin.

## Frontier

- **Compatibility zoom:** Which active modules load unchanged on the installed Pi version, and what migration edits are required?
- **Safety zoom:** Where are the practical bypasses and false positives in `bash-guard` and the persistent browser profile?
- **Adoption zoom:** Which pieces overlap with the user's remaining installed packages (`pi-mcp-adapter`, `pi-autoresearch`, and `pi-transcribe`)?
