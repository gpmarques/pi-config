# System Map: `pi-config` coarse overview

**Question:** How does this repository extend Pi, and what are its main boundaries and operating assumptions?
**Boundary:** The active `extensions/` and `skills/` trees, their setup dependencies, four external-integration stubs, one external-skill stub, and the `deprecated/` archive. External review is limited to the evidence needed for those stubs.
**Horizon:** Selecting and running pieces of this snapshot with Pi 0.84.4; later versions require renewed compatibility checks.
**Evidence basis:** The current seven-skill active-tree inventory was statically inspected in this working tree on 2026-09-01. Runtime and external-integration claims retain the 2026-08-31 evidence: Pi 0.84.4 documentation and installed extension-loader source; the locally installed `software-factory` source copied unchanged at SHA-256 `49d55f83280d4860a1286a61bd48d5206456e3f26755f4cc9b9df90a43372326`; `gpmarques/pi-interactive-subagents` at `b403b02484aa545b72a0a852aee9ecce524fa6f8`; `plannotator/effective-html` at `d95debbaef15af1d201fc6c10c77cf92b524a0d6`; Herdr Annotate Lite at `ba4903b28fbb77dd0a4bc55a4a7ba3c1ef0913ea`; `pi-web-access` metadata and package surface; published `pi-observational-memory` 3.0.4 metadata/source plus a local-only Pi/llama.cpp smoke test; and a local-only exercise of `web-debug` with `agent-browser` 0.18.0. Runtime compatibility of the remaining components was not tested.

**Historical baseline (2026-08-31):** Committed revision `3cfd947d29bafb0bd6221fb571101fb0524ee81f` is the prior five-skill baseline; it does not contain the current `session-retrospective` skill or `close-retrospective` snippet. External behavior claims remain bounded by the exact pins above or the individual stub's documented evidence boundary.

## At a glance

`pi-config` is a personal, selectively adopted configuration catalogue, not an installable monolith. Its active layer contains three local functional extension implementations and seven local skills; four extension folders and one skill folder are README-only pointers to external integrations. Users copy only the local capability they want or follow an external stub's reviewed installation boundary.

That keeps the active tool surface and context cost controllable, but shifts integration, updates, credentials, and compatibility checks onto the user.

## Architecture and causal path

```text
pi-config catalogue
├─ local implementations ──copy selected file/directory──> Pi loads extension or skill
│  ├─ 3 extensions: ask-user-question, custom-header, prompt-snippets
│  └─ 7 skills: analyze-sessions, pdf-reader, session-retrospective,
│                simple-visual-presenter, software-factory, web-debug,
│                youtube-transcript
└─ README-only stubs ──follow reviewed external install──> separately managed runtime
   ├─ 4 integrations: Herdr Annotate, interactive-subagents,
   │                   observational-memory, web-access
   └─ 1 skill package: Effective HTML
```

A stub contributes no executable surface merely by existing in this tree. Herdr Annotate is not loaded by Pi at all; Herdr owns its plugin lifecycle. The path is conditional: `web-debug` needs `agent-browser` 0.18.0-compatible commands, PDF reading needs a PyMuPDF virtual environment, and YouTube transcripts need `yt-dlp`. The three local extensions need no nested npm setup. External package/plugin installation, configuration, credentials, state, and compatibility remain separately owned. This repository deliberately supplies no root package manifest or one-command installer.

## Parts

### Functional extensions

| Extension | Surface | Role |
|---|---|---|
| `ask-user-question.ts` | `ask_user_question` tool | Structured text, single-choice, and multi-choice user prompts, serialized through a shared UI lock. |
| `custom-header.ts` | startup event, `/builtin-header` | Replaces the TUI header with a custom Pi logo. |
| `prompt-snippets/` | input transform, `/snippets`, `Alt+S` | Applies selected one-shot Markdown instructions before or after the next user message, including [`close-retrospective.md`](../../extensions/prompt-snippets/snippets/close-retrospective.md) for invoking bounded retrospective closure. |

The four integration directories are documentation-only:

- [`herdr-annotate/`](../../extensions/herdr-annotate/README.md) records Herdr Annotate Lite at `ba4903b28fbb77dd0a4bc55a4a7ba3c1ef0913ea`. Herdr 0.8.0+ and Bun are required; Linux clipboard integration additionally needs `wl-clipboard`, `xclip`, or `xsel`. Lite stores annotation JSONL under Herdr-owned state, uses the system clipboard, and has no runtime network client. It is a Herdr plugin, not a Pi extension.
- [`interactive-subagents/`](../../extensions/interactive-subagents/README.md) records the maintained fork at `b403b02484aa545b72a0a852aee9ecce524fa6f8`. Restricted children launch with `--no-extensions` and explicit allowlists; a separately installed parent shell guard would not be inherited. Only `researcher` receives the fork's distinct `safe_bash`.
- [`observational-memory/`](../../extensions/observational-memory/README.md) points to `elpapi42/pi-observational-memory` and documents pinned npm version 3.0.4, its branch-local ledger, and a machine-specific local-model reproducibility record.
- [`web-access/`](../../extensions/web-access/README.md) points to external `pi-web-access`, which provides web search and content retrieval. The stub itself registers nothing.

### Skills

- `analyze-sessions/`: read-only Python utilities for session cost, prompt, transcript, and search analysis.
- `pdf-reader/`: a text-plus-rendering workflow backed by PyMuPDF scripts.
- [`session-retrospective/`](../../skills/session-retrospective/SKILL.md): a cutoff-bounded, evidence-based workflow that implements and verifies explicitly approved general lessons before closure.
- [`simple-visual-presenter/`](../../skills/simple-visual-presenter/SKILL.md): a source-faithful visual-presentation workflow that composes the separately installed `show-me`, Effective HTML, and `visual-tester` resources, fails clearly when required presentation resources are unavailable, and keeps generated HTML local and derived.
- `software-factory/`: a self-contained four-gate workflow—Product, Architecture, Program Design, and Vertical Slices—that requires explicit approval before implementation.
- `web-debug/`: a runtime-first frontend debugging playbook that drives the external `agent-browser` CLI through bash, using explicit isolated sessions and request-only network evidence.
- `youtube-transcript/`: a `yt-dlp`-backed title and English-caption extractor.

[`effective-html/`](../../skills/effective-html/README.md) is a README-only external skill stub, not a local implementation. Its pinned Pi git package at `d95debbaef15af1d201fc6c10c77cf92b524a0d6` provides `html`, `design-artifact`, `html-wireframe`, `html-prototype`, `html-plan`, and `html-diagram`. Generated files are local by default; any publication is an explicit user decision.

### Archive

`deprecated/` keeps nine older extensions and three older skills for reference. They are outside the advertised active setup; their presence preserves ideas without loading them when users follow the copy-only workflow.

## Generated behavior

- **Runtime-observation surfaces:** `web-debug` uses installed `agent-browser` to reproduce → observe → hypothesize → verify live frontend behavior. Static web search and retrieval are not implemented locally; the `web-access/` stub registers nothing unless the external package is separately installed.
- **Context-economy loop:** prompt snippets reset after one message, so optional guidance does not continuously consume the system prompt. Users opt in again when the capability becomes relevant.
- **Manual-integration loop:** independent copying of local modules and upstream-managed installation of external packages limit this repository's blast radius, but every fresh machine or upstream change leaves setup and compatibility decisions with the user. The repository is a catalogue, not a synchronization mechanism.

## Causal regimes

- **Does adopting a catalogue entry expose its declared Pi surface in this snapshot? — Complicated, medium confidence:** local registration paths are statically visible, while external stubs are non-executable and depend entirely on separately installed upstream packages; successful loading still depends on Pi API compatibility and dependencies. **Classification challenge:** Clear, if current-version smoke tests repeatedly load each local component and each adopted external package. **Discriminator:** run isolated load and minimal invocation tests against the target Pi version.
- **Does a README-only stub expose a runtime surface? — Clear, high confidence (answer: no):** no stub contains `index.ts`, `SKILL.md`, a package manifest, or vendored executable code. A separately installed upstream package/plugin is a different trust and lifecycle boundary. **Classification challenge:** Complicated if a future edit adds executable files beneath a stub. **Discriminator:** inventory stub contents and inspect the runtime's configured package/plugin sources.
- **Does the modular copy workflow reduce always-on context cost? — Complicated, medium confidence:** snippets are one-shot and users choose which local modules or external packages to adopt, but total prompt impact from a real selected configuration is unmeasured. **Classification challenge:** Complex, if model/tool selection behavior changes materially as combinations vary. **Discriminator:** compare system-prompt tokens and task behavior across representative module combinations.

## Established

- **Catalogue, not package:** the README says not to install the repository as one package, documents per-resource copying, and distinguishes external stubs from local implementations (`README.md`, introduction and setup sections).
- **Three local extension implementations:** their entry points are `extensions/ask-user-question.ts`, `extensions/custom-header.ts`, and `extensions/prompt-snippets/index.ts`. The four other extension directories contain README pointers only.
- **Seven local skills plus one external skill stub:** `analyze-sessions`, `pdf-reader`, `session-retrospective`, `simple-visual-presenter`, `software-factory`, `web-debug`, and `youtube-transcript` contain `SKILL.md`; `effective-html` is documentation only.
- **No active local shell guard or browser wrapper:** the former `extensions/bash-guard/` and `extensions/browser/` directories were removed rather than deprecated. Historical plans may name them only as dated provenance; they are not current setup guidance.
- **Per-module setup:** no active local extension has a package manifest. Requirements such as `agent-browser` for `web-debug`, PyMuPDF for `pdf-reader`, and `yt-dlp` for `youtube-transcript` are listed in `README.md` and component documents. `software-factory` consists only of its `SKILL.md` and adds no setup step. External-stub implementations remain upstream-owned.
- **Legacy imports currently rely on an explicit 0.84.4 compatibility layer:** `ask-user-question.ts` and `custom-header.ts` import `@mariozechner/pi-coding-agent` and/or `@mariozechner/pi-tui`; `prompt-snippets/index.ts` uses `@earendil-works/*`. Pi 0.84.4's installed loader still maps those legacy specifiers to current bundled modules, but the old imports are outside the documented package interface and have no forward-compatibility guarantee. No extension-load success is claimed because that smoke test was not run.
- **No repository-level validation harness:** the tracked tree contains no test suite, continuous-integration configuration, root package manifest, or lockfile.

## Hypotheses

- **Optimized for high-agency interactive use:** UI clarification, one-shot prompting, and the `web-debug` live-browser workflow suggest the author values autonomy with selective human control. **Falsifier:** usage instructions or telemetry showing these modules are primarily run headlessly without interaction.
- **Manual selection is intended to prevent configuration bloat:** the copy-only instruction and documentation-only external boundaries point in this direction. **Falsifier:** an omitted canonical installer or sync workflow that routinely installs the full active tree.

## Fog

- **Current runtime compatibility:** Published `pi-observational-memory` 3.0.4 was loaded and exercised in isolation against Pi 0.84.4 with local llama.cpp 9430. The three local functional extensions were not load-smoke-tested; for the two legacy-importing entries, static inspection confirms only the exact-version loader aliases described above, not end-to-end behavior or future support. Other external integrations still need isolated smoke tests beyond their scoped source review.
- **Actual adopted subset:** The observational-memory npm package is confirmed globally adopted for the documented machine; a complete comparison with the user's global extension and skill directories is still needed because repository contents alone do not show the full active set.
- **External package drift and security:** `web-access/` intentionally does not pin or vendor `pi-web-access`; its provider, credential, storage, and network behavior can change independently. Observational memory is pinned to npm 3.0.4, but its model-generated records, session/clipboard storage, session-model fallback, and accepted lifecycle/empty-compaction behavior still form a trust boundary. **Needed:** review each installed upstream version and its current documentation before changing a pin.

## Frontier

- **Compatibility zoom:** Which active modules load unchanged on the installed Pi version, and what migration edits are required?
- **External-boundary zoom:** Which reviewed pins, state stores, clipboard paths, credentials, and publication choices apply to each separately installed integration?
- **Adoption zoom:** Which pieces overlap with the user's remaining installed packages (`pi-mcp-adapter`, `pi-autoresearch`, and `pi-transcribe`)?
