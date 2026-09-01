---
name: simple-visual-presenter
description: Creates simple, decision-ready visual HTML presentations from reports, plans, architectures, decisions, retrospectives, analyses, and approval artifacts. Use when the user asks to present, explain, show, or visualize one of these artifacts.
---

# Simple Visual Presenter

Turn an authoritative source document into the smallest visual that makes its main question easier to understand or decide. The HTML is derived; it never replaces the source.

## 1. Load the required skills

Read and follow the installed `show-me` skill and the broad Effective HTML `html` skill. Let `html` route to `html-plan`, `html-diagram`, `html-prototype`, or the general HTML workflow, and follow the selected contract plus `design-artifact` when routed there.

If `show-me`, `html`, or a skill required by the selected route is unavailable or unreadable, stop and name the missing dependency. Do not silently imitate it or substitute a look-alike workflow.

## 2. Find the one useful view

- Read the source and identify its audience, purpose, and exact decision or approval question.
- Use `show-me` to choose the one essential mental model and content hierarchy.
- Preserve the source's terminology, decisions, commitments, ordering, and unknowns. Clearly separate **decided** from **pending**. Never invent content, certainty, metrics, dates, owners, or scope.
- Build one primary view. Add at most three compact supporting views (prefer two or fewer), and only when they materially clarify it.

Example: an architecture approval can lead with one dependency diagram and use one compact decided-versus-pending list; it does not need a dashboard.

## 3. Keep the artifact simple

Produce one self-contained, offline, accessible, responsive `.html` file with inline CSS and only necessary JavaScript. Use a deliberate but restrained visual direction, readable light and dark themes, semantic structure, visible focus, and useful mobile reflow.

Prefer direct reading over controls. Use progressive disclosure only for genuinely secondary detail. Avoid decorative complexity, dashboard or card grids by default, gratuitous animation, repeated summaries, dead controls, and speculative detail. Do not publish or offer to publish the file.

## 4. Verify, open, and hand off

1. Run bounded static checks for source coverage, document structure, local-only dependencies, accessibility basics, and accidental external requests.
2. Delegate visual QA to the existing `visual-tester` with the local file URL and a bounded scope: desktop in light and dark modes, one mobile viewport, keyboard and focus behavior, overflow, console or page errors, and unexpected network requests.
3. Fix observed failures and rerun only the affected checks. If `visual-tester` is unavailable, report QA as blocked; do not claim the artifact is ready.
4. After QA passes, open the file locally.
5. Return its absolute path, the primary-view summary, the QA verdict, and any structural interpretation introduced.
6. Ask the source workflow's exact decision question verbatim. If the source workflow has no decision question, do not invent one.

After approval, remove the derived HTML unless the user explicitly asks to retain it. Never remove or silently rewrite the authoritative source.
