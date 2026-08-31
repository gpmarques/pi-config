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

Local implementations for the remaining active extensions and skills live here. Stub directories point to external projects rather than vendoring their code.

For an architectural overview, see the [coarse system map](docs/system-maps/pi-config-overview.md).

## Copy an extension

Single-file extension:

```bash
cp extensions/ask-user-question.ts ~/.pi/agent/extensions/
```

Directory extension:

```bash
cp -r extensions/browser ~/.pi/agent/extensions/
```

If the copied extension has a `package.json`, install its deps:

```bash
cd ~/.pi/agent/extensions/browser
npm install
```

Then restart pi or run `/reload`.

## Install an externally maintained extension

Directories described as stubs contain documentation only; do not copy them as extension implementations. For example, the upstream `pi-web-access` README currently documents:

```bash
pi install npm:pi-web-access
```

Use the [upstream README](https://github.com/nicobailon/pi-web-access#readme) as the authority for current installation, configuration, tools, requirements, and any future update guidance.

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
- `bash-guard/` — hooks that catch dangerous bash commands before they run, with an on/off toggle
- `browser/` — Playwright-driven headless Chromium the agent can drive (navigate, eval JS, inspect network/console, click, screenshot); off by default, enable with `/browser on`
- `custom-header.ts` — the big capital Π header
- `interactive-subagents/` — stub, see [gpmarques/pi-interactive-subagents](https://github.com/gpmarques/pi-interactive-subagents)
- `observational-memory/` — stub, see [elpapi42/pi-observational-memory](https://github.com/elpapi42/pi-observational-memory); documents the pinned npm 3.0.4 local-Qwen setup
- `prompt-snippets/` — small, reusable behavior rules toggled onto a message before sending; reset after send
- `web-access/` — stub, see [pi-web-access](https://github.com/nicobailon/pi-web-access)

### Skills

- `analyze-sessions/` — Python scripts to query past pi sessions: cost rollups, prompt-pattern mining, session rendering
- `pdf-reader/` — read PDFs (lecture notes, papers) into the context
- `web-debug/` — a runtime-first frontend debugging playbook driven through the installed `agent-browser` CLI (independent of the browser extension)
- `youtube-transcript/` — fetch a YouTube video's title and transcript as JSON

### Deprecated

`deprecated/` holds the extensions and skills from the two-month setup that are no longer in active use. They are kept for reference, not as a supported install set: some still work, while others reference removed extension paths or tool names and require adaptation or restored dependencies.

## Dependencies

Extension-local npm deps are kept with the extension. Run `npm install` only in copied extensions that include a `package.json`:

- `bash-guard/`
- `browser/` (also run `npx playwright install chromium` once)

`web-access/` has no local dependencies because it is a documentation-only reference; the implementation and its dependencies live in the external `pi-web-access` package.

`web-debug/` requires an external `agent-browser` executable; it is not an extension-local dependency. After copying the skill, check availability and version:

```bash
command -v agent-browser
agent-browser --version
```

The bundled workflows are validated against `agent-browser 0.18.0`. If another version is installed, consult its top-level and relevant subcommand help before using the examples. The skill fails closed when the executable is unavailable; it does not install or fall back to the separate browser extension.

Optional system tools:

```bash
brew install yt-dlp ffmpeg
```

Used by `youtube-transcript/`. Python 3 is needed for `youtube-transcript/` and `analyze-sessions/` (stdlib only).

PDF reader setup after copying `skills/pdf-reader/`:

```bash
python3 -m venv ~/.pi/agent/skills/pdf-reader/.venv
~/.pi/agent/skills/pdf-reader/.venv/bin/pip install -r ~/.pi/agent/skills/pdf-reader/requirements.txt
```
