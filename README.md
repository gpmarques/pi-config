# pi-config

[![video](assets/thumbnail.png)](https://www.youtube.com/@EeroAlvar)

My personal [pi](https://github.com/earendil-works/pi) configuration.

The setup from [My Pi Setup After 6 Months](https://www.youtube.com/@EeroAlvar) (and its predecessor, [Pi Coding Agent Setup After 2 Months](https://www.youtube.com/watch?v=DWWrLlM3gwQ)).

This is **not** meant to be installed as one big package. Browse the repo and copy the pieces you want into your own Pi config.

Some extensions are big enough to live in their own repositories:

- **[pi-interactive-subagents](https://github.com/gpmarques/pi-interactive-subagents)** — async subagents on tmux or Herdr terminal surfaces, maintained in a separate fork
- **[pi-observational-memory](https://github.com/elpapi42/pi-observational-memory)** — V3 branch-local observations/reflections with deterministic compaction
- **[pi-web-access](https://github.com/nicobailon/pi-web-access)** — web search and content retrieval, replacing this catalogue's former local `web-search` and `web-fetch` extensions
- **[pi-dictate](https://github.com/amosblomqvist/pi-dictate)** — real-time voice dictation inside pi
- **[learn](https://github.com/amosblomqvist/learn)** — my AI learning system, built on top of this config

The active catalogue contains **three local extension implementations**, **four README-only external integration stubs**, **five local skill implementations**, and **one README-only external skill stub**. Stub directories point to external projects rather than vendoring their code.

For an architectural overview, see the [coarse system map](docs/system-maps/pi-config-overview.md).

## Copy an extension

Single-file extension:

```bash
cp extensions/ask-user-question.ts ~/.pi/agent/extensions/
```

Directory extension:

```bash
cp -r extensions/prompt-snippets ~/.pi/agent/extensions/
```

The three active local extensions have no extension-local package manifest or dependency-install step. External catalogue stubs are installed with the separately documented package or plugin command rather than copied from this repository.

Then restart pi or run `/reload`.

## Install an externally maintained integration

Directories described as stubs contain documentation only; do not copy them as implementations. Follow each stub's reviewed pin, requirements, state boundary, and upstream links:

- [`extensions/herdr-annotate/`](extensions/herdr-annotate/README.md) — pinned Herdr Annotate Lite plugin; a Herdr integration, not a Pi extension.
- [`extensions/interactive-subagents/`](extensions/interactive-subagents/README.md) — maintained fork for async tmux/Herdr child agents.
- [`extensions/observational-memory/`](extensions/observational-memory/README.md) — pinned npm V3 observational-memory package and local-model reproducibility notes.
- [`extensions/web-access/`](extensions/web-access/README.md) — external `pi-web-access` package.
- [`skills/effective-html/`](skills/effective-html/README.md) — pinned Pi package exposing six HTML artifact skills.

## Copy a skill

```bash
cp -r skills/pdf-reader ~/.pi/agent/skills/
```

Then restart pi or run `/reload`.

## Do not clone over your config

Avoid cloning this repo directly into `~/.pi/agent` unless it is a fresh setup. If you already use pi, copy individual files/folders instead so you don't replace your own config.

## Contents

### Extensions

- `ask-user-question.ts` — the agent asks you a question through a UI popup; popups from different extensions serialize via a shared UI lock
- `custom-header.ts` — the big capital Π header
- `herdr-annotate/` — README-only external stub for pinned Herdr Annotate Lite; it is a Herdr plugin, not a Pi extension
- `interactive-subagents/` — README-only external stub, see [gpmarques/pi-interactive-subagents](https://github.com/gpmarques/pi-interactive-subagents)
- `observational-memory/` — README-only external stub, see [elpapi42/pi-observational-memory](https://github.com/elpapi42/pi-observational-memory); documents the pinned npm 3.0.4 local-Qwen setup
- `prompt-snippets/` — small, reusable behavior rules toggled onto a message before sending; reset after send
- `web-access/` — README-only external stub, see [pi-web-access](https://github.com/nicobailon/pi-web-access)

### Skills

- `analyze-sessions/` — Python scripts to query past pi sessions: cost rollups, prompt-pattern mining, session rendering
- `effective-html/` — README-only external stub for a pinned Pi package providing six standalone HTML artifact skills
- `pdf-reader/` — read PDFs (lecture notes, papers) into the context
- `software-factory/` — a four-gate feature workflow—Product, Architecture, Program Design, then Vertical Slices—with explicit approval before implementation
- `web-debug/` — a runtime-first frontend debugging playbook driven through the installed `agent-browser` CLI
- `youtube-transcript/` — fetch a YouTube video's title and transcript as JSON

### Deprecated

`deprecated/` holds the extensions and skills from the two-month setup that are no longer in active use. They are kept for reference, not as a supported install set: some still work, while others reference removed extension paths or tool names and require adaptation or restored dependencies.

## Dependencies

The three local extensions have no extension-local package manifests or nested npm setup. README-only stubs have no local runtime dependencies because their implementations and setup remain external. The Herdr Annotate Lite integration requires Herdr 0.8.0 or later and Bun; Linux clipboard support also requires `wl-clipboard`, `xclip`, or `xsel`. Effective HTML is installed as a pinned Pi package and has no runtime service or account requirement.

`web-debug/` requires an external `agent-browser` executable; it is not an extension-local dependency. After copying the skill, check availability and version:

```bash
command -v agent-browser
agent-browser --version
```

The bundled workflows are validated against `agent-browser 0.18.0`. If another version is installed, consult its top-level and relevant subcommand help before using the examples. The skill fails closed when the executable is unavailable and does not install or switch to another browser provider.

Optional system tools:

```bash
brew install yt-dlp
```

Used by `youtube-transcript/`. Python 3 is needed for `youtube-transcript/` and `analyze-sessions/` (stdlib only).

PDF reader setup after copying `skills/pdf-reader/`:

```bash
python3 -m venv ~/.pi/agent/skills/pdf-reader/.venv
~/.pi/agent/skills/pdf-reader/.venv/bin/pip install -r ~/.pi/agent/skills/pdf-reader/requirements.txt
```
