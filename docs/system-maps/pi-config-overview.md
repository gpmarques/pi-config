# System Map: `pi-config` coarse overview

**Question:** How does this repository extend Pi, and what are its main boundaries and operating assumptions?
**Boundary:** The active `extensions/` and `skills/` trees, their setup dependencies, the external-extension stubs, and the `deprecated/` archive. The linked external repositories are not analyzed.
**Horizon:** Selecting and running pieces of this snapshot with a current Pi installation.
**Evidence basis:** Static inspection of the current repository snapshot and a local-only exercise of the `web-debug` command workflow with installed `agent-browser` 0.18.0. Runtime compatibility of the other components was not tested.

## At a glance

`pi-config` is a personal, pick-and-copy configuration catalogue, not an installable monolith. Its active layer contains seven functional extensions and four skills; two additional extension folders are pointers to external repositories. The decisive design choice is selective adoption: users copy only the capability they want, install that capability's local dependencies, and reload Pi.

That keeps the active tool surface and context cost controllable, but shifts integration, updates, credentials, and compatibility checks onto the user.

## Causal path

```text
A user selects one module
  → copies it into ~/.pi/agent/extensions or ~/.pi/agent/skills
  → installs module-local dependencies and credentials when required
  → reloads Pi, which auto-discovers the copied resource
  → an extension registers tools/events/UI, or a skill supplies a playbook plus scripts
  → the agent gains a focused capability during future turns
```

The path is conditional: the local browser extension also needs Chromium, web search needs Google credentials, `web-debug` needs an external `agent-browser` executable, PDF reading needs a PyMuPDF virtual environment, and YouTube transcripts need `yt-dlp`. The repository deliberately supplies no root package manifest or one-command installer.

## Parts

### Functional extensions

| Extension | Surface | Role |
|---|---|---|
| `ask-user-question.ts` | `ask_user_question` tool | Structured text, single-choice, and multi-choice user prompts, serialized through a shared UI lock. |
| `bash-guard/` | `tool_call` gate, `/bash-guard`, two flags | Prompts before broad classes of shell risk in interactive sessions and hard-blocks catastrophic patterns in subagents or autonomous mode. |
| `browser/` | Eight `browser_*` tools, `/browser` | Drives one persistent Playwright page and captures bounded console/network buffers; tools are inactive until `/browser on`. |
| `custom-header.ts` | startup event, `/builtin-header` | Replaces the TUI header with a custom Pi logo. |
| `prompt-snippets/` | input transform, `/snippets`, `Alt+S` | Applies selected one-shot Markdown instructions before or after the next user message. |
| `web-fetch/` | `web_fetch` tool | Extracts HTML, text, and PDFs; uses Readability/Turndown and falls back to Jina Reader. |
| `web-search/` | `web_search` tool | Queries Google Custom Search with structured exact-phrase, exclusion, and site filters. |

`interactive-subagents/` and `observational-memory/` are documentation stubs pointing to separate repositories, not local implementations.

### Skills

- `analyze-sessions/`: read-only Python utilities for session cost, prompt, transcript, and search analysis.
- `pdf-reader/`: a text-plus-rendering workflow backed by PyMuPDF scripts.
- `web-debug/`: a runtime-first frontend debugging playbook that drives the external `agent-browser` CLI through bash, using explicit isolated sessions and request-only network evidence.
- `youtube-transcript/`: a `yt-dlp`-backed title and English-caption extractor.

### Archive

`deprecated/` keeps nine older extensions and three older skills for reference. They are outside the advertised active setup; their presence preserves ideas without loading them when users follow the copy-only workflow.

## Generated behavior

- **Runtime-observation surfaces:** `web_search` discovers sources, `web_fetch` reads static content, `web-debug` uses installed `agent-browser` to reproduce → observe → hypothesize → verify live frontend behavior, and the optional local `browser_*` extension remains a separate automation surface.
- **Context-economy loop:** browser tools start inactive and prompt snippets reset after one message, so uncommon guidance does not continuously consume the system prompt. Users opt in again when the capability becomes relevant.
- **Manual-integration loop:** independent copying limits blast radius, but every upstream change or fresh machine requires the user to repeat setup and compatibility decisions. The repository is a source of pieces, not a synchronization mechanism.

## Causal regimes

- **Does selecting and copying a component expose its declared Pi surface after reload in this snapshot? — Complicated, medium confidence:** the registration paths are statically visible, but successful loading depends on Pi API compatibility and local dependencies. **Classification challenge:** Clear, if a current-version smoke suite repeatedly loads every active component. **Discriminator:** run isolated load and minimal invocation tests against the target Pi version.
- **Does `bash-guard` prevent all destructive agent actions during a session? — Clear, high confidence (answer: no):** it intercepts only `bash` tool calls, and its protection changes by interactive/subagent/disabled mode; edits, writes, user shell commands, and unrecognized command shapes remain outside that gate. **Classification challenge:** Complicated, if shell parsing or Pi event ordering changes the observed boundary. **Discriminator:** adversarial tests across every mutation surface and execution mode.
- **Does the modular copy workflow reduce always-on context cost? — Complicated, medium confidence:** browser tools explicitly leave the active set until enabled and snippets are one-shot, but total prompt impact from a real selected configuration is unmeasured. **Classification challenge:** Complex, if model/tool selection behavior changes materially as combinations vary. **Discriminator:** compare system-prompt tokens and task behavior across representative module combinations.

## Established

- **Catalogue, not package:** the README says not to install the repository as one package and documents per-resource copying (`README.md`, introduction and “Copy an extension/skill”).
- **Seven local extension implementations:** their entry points and registrations are under `extensions/`; the two remaining extension directories contain only external-repository pointers.
- **Selective safety and context controls:** `extensions/bash-guard/index.ts` documents its mode-specific gate; `extensions/browser/index.ts` removes all eight tools from the active set by default; `extensions/prompt-snippets/index.ts` clears enabled snippets after input.
- **Per-module setup:** npm manifests exist only beside `bash-guard`, `browser`, and `web-fetch`; other external requirements, including `agent-browser` for `web-debug`, are listed in `README.md` and the relevant skill documents.
- **Mixed Pi API namespaces:** five active extension entry points import the older `@mariozechner/*` packages, while `browser` and `prompt-snippets` import `@earendil-works/*` (`extensions/**/*.ts`, import declarations).
- **No repository-level validation harness:** the tracked tree contains no test suite, continuous-integration configuration, root package manifest, or lockfile.

## Hypotheses

- **Optimized for high-agency interactive use:** UI clarification, shell confirmation, one-shot prompting, and live browser inspection suggest the author values autonomy with selective human control. **Falsifier:** usage instructions or telemetry showing these modules are primarily run headlessly without interaction.
- **Manual selection is intended to prevent configuration bloat:** the copy-only instruction and default-off browser gate point in this direction. **Falsifier:** an omitted canonical installer or sync workflow that routinely installs the full active tree.
- **Namespace mixing may create current-version load failures:** the repository appears to span a Pi package rename. **Falsifier:** loading all seven extensions successfully against the intended current Pi runtime without compatibility aliases or edits.

## Fog

- **Current runtime compatibility:** **Needed:** isolated load and smoke-test results for all seven functional extensions against the user's installed Pi version.
- **Actual adopted subset:** **Needed:** compare this catalogue with the user's `~/.pi/agent/extensions` and `skills` directories; repository contents alone do not show what is in use.
- **Operational security posture:** browser state persists on disk and network buffers can hold sensitive headers, while web search accepts local credentials. **Needed:** permissions, retention, and redaction checks in the installed environment—not credential values.

## Frontier

- **Compatibility zoom:** Which active modules load unchanged on the installed Pi version, and what migration edits are required?
- **Safety zoom:** Where are the practical bypasses and false positives in `bash-guard` and the persistent browser profile?
- **Adoption zoom:** Which pieces overlap with the user's remaining installed packages (`pi-mcp-adapter`, `pi-autoresearch`, and `pi-transcribe`)?
