# Effective HTML (external skill collection)

This directory is a documentation-only catalogue stub for [`plannotator/effective-html`](https://github.com/plannotator/effective-html). It intentionally contains no `SKILL.md` or vendored implementation. Install the reviewed upstream package instead of copying this directory into Pi's skill directory.

## Reviewed pin and Pi 0.84.4 commands

The reviewed source is commit [`d95debbaef15af1d201fc6c10c77cf92b524a0d6`](https://github.com/plannotator/effective-html/commit/d95debbaef15af1d201fc6c10c77cf92b524a0d6). These commands omit `-l`, so they operate on Pi's global user settings under Pi 0.84.4.

Install at the reviewed pin:

```bash
pi install git:github.com/plannotator/effective-html@d95debbaef15af1d201fc6c10c77cf92b524a0d6
```

Reconcile or reinstall the checkout without moving the configured pin:

```bash
pi update git:github.com/plannotator/effective-html@d95debbaef15af1d201fc6c10c77cf92b524a0d6
```

Re-pin an existing installation to the reviewed commit (Pi matches the repository independently of its old ref and replaces the configured source):

```bash
pi install git:github.com/plannotator/effective-html@d95debbaef15af1d201fc6c10c77cf92b524a0d6
```

Remove the global package and its managed checkout:

```bash
pi remove git:github.com/plannotator/effective-html@d95debbaef15af1d201fc6c10c77cf92b524a0d6
```

Restart Pi or run `/reload` after changing the package.

> **Dated local-state note (2026-08-31):** The global Pi settings on the reviewed machine contain exactly the pinned source above, and its clean managed checkout resolves to `d95debbaef15af1d201fc6c10c77cf92b524a0d6`. This records one machine at one time; it is not an evergreen guarantee that this repository's users have the package installed.

## Pi-visible skills

Pi discovers these six upstream `SKILL.md` files:

| Skill | Purpose |
|---|---|
| `html` | Broad router and workflow for standalone HTML artifacts. |
| `design-artifact` | Creative direction for palette, type, layout, theme, and visual register. |
| `html-wireframe` | Low-fidelity structure, hierarchy, navigation, and task-flow exploration. |
| `html-prototype` | Polished mockups and bounded interactive prototypes. |
| `html-plan` | Traceable plans, roadmaps, rollouts, ownership, and dependencies. |
| `html-diagram` | Relationship, sequence, topology, state, hierarchy, and quantitative diagrams. |

The Pi-loaded integration is Markdown-only: the six `SKILL.md` files and their Markdown references. The upstream repository also contains a separate website and harness-specific metadata, but Pi's conventional package discovery does not load those as runtime code. There is no root `package.json`, Pi manifest, extension, executable, install hook, runtime authentication flow, or background service at this pin. In particular, Pi does not act on the OpenAI marketplace authentication metadata in `.agents/plugins/marketplace.json`.

The upstream `agents/openai.yaml` files distinguish two implicitly invocable skills from four direct-invocation specialists. Pi 0.84.4 does not interpret that OpenAI-specific `allow_implicit_invocation` policy. None of the six `SKILL.md` files sets Pi's `disable-model-invocation` frontmatter, so Pi places all six names and descriptions in the model-visible skill list unless the package's skill resources are filtered or disabled in Pi configuration. The specialists' descriptions still tell the model not to activate them independently, but that is an instruction rather than a Pi loader gate.

## Artifact, browser, and publication privacy

The skills produce self-contained HTML files in the working tree and do not upload them automatically. Those files can reproduce prompt, repository, or user-supplied content, so inspect them before sharing. The workflows ask the agent to validate artifacts in an available browser; that exposes the rendered file to the chosen browser process and whatever profile, cache, screenshots, or tool logs that browser integration retains. External dependencies are disallowed by default unless the user permits them; allowing remote assets or links can create ordinary browser network disclosure.

After an artifact is delivered, `design-artifact` instructs the agent to ask whether the user wants a public page. Publication with [`tot`](https://github.com/plannotator/tot) is allowed only after explicit consent, and installing `@plannotator/tot` also requires a separate explicit approval. A `tot` URL is publicly accessible to anyone who has it. Installing Effective HTML does not install `tot`.

> **Dated local-state note (2026-08-31):** `tot` was not installed on the reviewed machine (`command -v tot` did not resolve and the global npm package was absent).

Effective HTML itself has no runtime service or account requirement. Any later browser network access, optional `tot` installation, or consented publication is a separate action outside the installed Markdown skill collection.
