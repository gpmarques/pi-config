# Herdr Annotate Lite (external Herdr integration)

This directory is a documentation-only catalogue stub for [`plannotator/herdr-annotate`](https://github.com/plannotator/herdr-annotate). **Herdr Annotate is a Herdr plugin, not a Pi extension.** It is catalogued under `extensions/` only by this repository's external-integrations convention. There is no plugin implementation to copy from this directory and nothing here is loaded by Pi or Herdr.

## Reviewed pin and install commands

The reviewed Lite source is commit [`ba4903b28fbb77dd0a4bc55a4a7ba3c1ef0913ea`](https://github.com/plannotator/herdr-annotate/commit/ba4903b28fbb77dd0a4bc55a4a7ba3c1ef0913ea), using its [`lite/herdr-plugin.toml`](https://github.com/plannotator/herdr-annotate/blob/ba4903b28fbb77dd0a4bc55a4a7ba3c1ef0913ea/lite/herdr-plugin.toml).

Install Lite at the reviewed pin:

```bash
herdr plugin install --ref ba4903b28fbb77dd0a4bc55a4a7ba3c1ef0913ea --yes plannotator/herdr-annotate/lite
```

Update or reinstall Lite at that same immutable pin:

```bash
herdr plugin uninstall annotate
herdr plugin install --ref ba4903b28fbb77dd0a4bc55a4a7ba3c1ef0913ea --yes plannotator/herdr-annotate/lite
```

Uninstall the plugin:

```bash
herdr plugin uninstall annotate
```

The plugin ID is `annotate`, which is why uninstall and action commands use that name rather than the repository name.

> **Dated local-state note (2026-08-31):** The reviewed machine has Herdr Lite enabled with requested and resolved commit `ba4903b28fbb77dd0a4bc55a4a7ba3c1ef0913ea`; the managed checkout is clean, its manifest path is the Lite manifest, and its plugin ID is `annotate`. This records one machine at one time, not an evergreen repository guarantee.

## Requirements and configured surface

The reviewed manifest requires Herdr 0.8.0 or later and Bun on `PATH`; it supports macOS, Linux, and preview/best-effort Windows plugin operation. Linux clipboard access additionally needs one of `wl-clipboard`, `xclip`, or `xsel`; Windows uses PowerShell. The dated reviewed machine has Herdr 0.8.2 and Bun 1.3.10.

Lite registers exactly three actions and two Herdr-owned panes:

| Kind | ID | Behavior |
|---|---|---|
| Action | `annotate.capture` | Opens a comment editor for the focused terminal selection, with clipboard fallback. |
| Action | `annotate.copy-context` | Copies all active annotations to the system clipboard as Markdown. |
| Action | `annotate.manage` | Opens the annotation manager. |
| Pane | `editor` | Popup for writing and saving a comment. |
| Pane | `manager` | Popup for browsing, copying, archiving, restoring, and deleting annotations. |

The reviewed Herdr configuration binds:

| Binding | Action |
|---|---|
| `prefix+a` | `annotate.capture` |
| `prefix+shift+a` | `annotate.copy-context` |
| `prefix+m` | `annotate.manage` |

Bindings are user configuration, not plugin-owned cleanup. After adding or changing them, validate and reload Herdr with `herdr config check` and `herdr server reload-config`.

## Lite boundary and blocked Pi skill

Lite runs the TypeScript actions with Bun and deliberately excludes the Full install's downloaded native `plannotator-tui` binary. It therefore has no whole-document, agent-reply, or transcript-review actions. The Full plugin is not installed on the reviewed machine; the managed checkout's `bin/` contains no native binary.

Do **not** install the upstream bundled `plannotator-tui` Pi skill at this commit. It is blocked for this reviewed integration for two independent reasons: Lite has no `plannotator-tui` executable, and the skill's raw fallback opens `--plugin plannotator-tui` while the actual Herdr plugin ID is `annotate`. That plugin-ID mismatch makes the fallback invalid even though the repository bundles the skill. Re-review a later upstream commit before reconsidering it.

## Storage, clipboard, privacy, and network

On save, Lite stores the selected text, the human's comment, capture/create timestamps, and a small Herdr provenance record (workspace, tab, focused pane, pane working directory, and detected agent fields when available). Active annotations and archived annotation sets are local mode-`0600` JSONL records under Herdr's plugin state directory; on the reviewed machine that directory is `~/.local/state/herdr/plugins/annotate/`. Archives retain the complete selected text, comments, timestamps, and provenance until restored or permanently deleted.

Capture prefers Herdr's selected text, then a short-lived same-host handoff file, then reads the system clipboard. Copy actions write formatted annotation text to the system clipboard. Clipboard contents can outlive the plugin and may be retained by the operating system, a clipboard manager, or another application; copying is not a privacy boundary.

The reviewed Lite runtime imports only Bun/Node built-ins, invokes Herdr, and uses local clipboard commands. Its action and pane code contains no network client or runtime service. Installing or reinstalling the plugin does contact GitHub to obtain the pinned checkout; that install-time fetch is distinct from Lite's local runtime behavior.

Uninstall is not complete data erasure. It does not remove the three manually configured keybindings or clear the system clipboard, and plugin state/config can be retained separately from the managed source. Before cleanup, back up any annotations that must survive; afterward, inspect and deliberately remove retained data under `~/.local/state/herdr/plugins/annotate/` and `~/.config/herdr/plugins/config/annotate/` if erasure is intended. Do not assume deleting active annotations deletes archived sets, or that deleting local files clears clipboard-manager history.
