# Plan: migrate `web-debug` from pi browser tools to `agent-browser`

> **Implemented historical plan:** Commit [`ca15706ab524a760cbbea8979b7ecd909e278807`](https://github.com/gpmarques/pi-config/commit/ca15706ab524a760cbbea8979b7ecd909e278807) implemented this migration on 2026-08-30. This file is retained as design provenance, not as current setup guidance. In particular, its “Confirmed current facts” section records the pre-migration state. The separate `extensions/browser/` implementation that this plan said to retain was removed from the active catalogue on 2026-08-31, so all claims below that it remains present are historical. Consult the current skill, reference, README, and system map for present behavior.

## Proposal

Rewrite `pi-config/skills/web-debug` around the installed `agent-browser` 0.18.0 CLI while preserving its runtime-first **reproduce → observe → hypothesize → verify** discipline. Keep `SKILL.md` focused on triggering, safety, the core loop, and common playbooks; move version-sensitive command details and limitations into one bundled reference. Update catalogue documentation that still says the skill depends on the pi browser extension.

The new skill must never imply capabilities that 0.18.0 does not expose. In particular, `network requests` records request URL, method, request headers, timestamp, and resource type, but not response headers, response status, or response body. It also begins request tracking only when the command is first read without `--clear`. The workflows must prime tracking before reproduction and report response evidence as unavailable unless obtained by a separately justified, bounded probe.

No material user preference blocks implementation. Runtime choices that still require user consent are using an existing browser/profile, persisting auth, receiving credentials or tokens, and performing state-changing actions against production.

## Intent and expected outcome

- A pi agent loads `web-debug` for frontend runtime failures and invokes the installed `agent-browser` binary through `bash`; it does not look for `browser_*` tools or instruct the user to install/fallback to another browser system.
- The skill reproduces behavior in a uniquely named, explicit browser session, gathers bounded evidence, distinguishes observation from inference, and closes only its own session.
- Authentication, storage, JWT, production, and network investigations avoid exposing secrets or overstating what the CLI observed.
- The skill remains useful when `agent-browser` is absent or incompatible by failing closed with a clear blocked result rather than installing software.

## Scope

### In scope

- Trigger/frontmatter changes for `web-debug`.
- Prerequisite and version checks for the installed CLI.
- Exact 0.18.0 workflows for navigation, snapshots/refs, form interaction, eval, console/errors, request capture, screenshots, cookies/storage, auth, JWT inspection, production comparison, and end-to-end verification.
- Session isolation, optional persistence, cleanup, output bounding, shell quoting, ref invalidation, error recovery, and security guidance.
- A compact version-sensitive reference under the skill.
- Synchronizing repository descriptions of the skill and its dependency.

### Out of scope

- Removing or modifying `pi-config/extensions/browser`; it remains a separate catalogue component.
- Installing `agent-browser`, Chromium, `browser-use`, Playwright, or any fallback.
- Implementing a new pi browser extension or adding new browser capabilities.
- General-purpose browser automation, scraping, or visual QA guidance beyond debugging a reported frontend behavior.
- Claiming response-header/status parity with the old browser extension.

## Confirmed current facts at planning time (pre-migration)

### Repository

- `pi-config/skills/web-debug/SKILL.md:1-46` triggers correctly for runtime frontend failures but names unavailable `browser_*` tools and assumes implicit persistence across pi restarts.
- `pi-config/skills/web-debug/SKILL.md:50-172` defines useful auth, request, storage, JWT, form, blank-screen, production, and verification playbooks; these should be retained conceptually, not transliterated mechanically.
- `pi-config/skills/web-debug/SKILL.md:174-201` contains browser-extension-specific buffer and selector pitfalls mixed with generally useful eval/DOM guidance.
- `pi-config/README.md:45-51` documents skills as copyable units, while `pi-config/README.md:71-76` still describes `web-debug` as using the browser extension. Dependency guidance is at `pi-config/README.md:82-103`.
- `pi-config/docs/system-maps/pi-config-overview.md:43-58` describes `web-debug` and the runtime-observation loop as coupled to `browser_*`; extension-specific facts at lines 29-39 and 66-73 remain independently valid.
- Pi discovers a directory containing `SKILL.md` and loads full skill content on demand (`/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/docs/skills.md:36-40,65-72`). `scripts/` and `references/` are conventional optional subdirectories (`skills.md:93-106`), and a specific description controls triggering (`skills.md:163-175`). `allowed-tools` is experimental (`skills.md:138-150`).

### Installed `agent-browser`

- `command -v agent-browser` resolves to `/opt/homebrew/bin/agent-browser`; `agent-browser --version` reports `0.18.0`.
- The installed README documents authentication/session choices at `/opt/homebrew/lib/node_modules/agent-browser/README.md:313-440`, opt-in security controls at lines 441-462, output/snapshot controls at lines 463-509, configuration precedence at lines 510-585, timeout behavior at lines 586-602, refs at lines 603-651, and JSON workflow at lines 652-679.
- The bundled upstream skill emphasizes cleanup, fresh refs, eval via quoted stdin, and explicit waits (`/opt/homebrew/lib/node_modules/agent-browser/skills/agent-browser/SKILL.md:430-551`). Its generic automation scope is a caution, not a replacement for the diagnostic philosophy of `web-debug`.
- `browser-use` is also installed, but its broad cloud/profile/tunnel workflow and separate daemon are not a fallback or implementation model. The updated skill should explicitly avoid switching to it when `agent-browser` is unavailable.
- In 0.18.0, request capture stores request headers and no response metadata (`/opt/homebrew/lib/node_modules/agent-browser/dist/browser.js:378-397`). `network requests --clear` returns before tracking starts; a non-clear read starts tracking (`/opt/homebrew/lib/node_modules/agent-browser/dist/actions.js:1038-1046`). Repeated non-clear reads attach another request listener in this version, so later captures can duplicate entries.
- Console messages and page errors are attached during page setup and remain until explicitly cleared (`dist/browser.js:1510-1526`); unlike the old extension, reads do not drain them.
- Internal daemon code contains a response-body waiter with status (`dist/actions.js:1840-1857`), but 0.18.0 does not expose it in CLI help. The skill must not rely on hidden protocol actions.

## Selected design and decisions

### 1. Keep the diagnostic philosophy; replace the transport layer

The core loop becomes:

1. **Reproduce:** open the supplied URL, wait for a meaningful condition, snapshot, and perform the minimum action that triggers the failure.
2. **Observe:** collect page state, `console`, `errors`, a pre-primed filtered request log, targeted storage/eval output, and screenshots only when visual evidence matters.
3. **Hypothesize:** label the smallest explanation consistent with evidence; do not infer status/headers the CLI did not expose.
4. **Verify:** repeat the same observable scenario after a change, preferably in a fresh isolated session when auth/cache are not part of the hypothesis.

### 2. Use explicit ephemeral sessions by default

- Generate one sanitized semantic name per investigation, such as `web-debug-<project>-<short-unique-suffix>`; record it and pass `--session <name>` before every command.
- Never use the default session, close all sessions, or rely on a shell variable surviving separate bash calls.
- Keep the session open across the reproduce/observe/verify loop, then run `agent-browser --session <name> close` in a finally-style cleanup.
- Treat `--session` (live isolated browser) and `--session-name` (auto-saved cookies/localStorage across restarts) as different concepts.
- Use `--session-name`, `--profile`, `--state`, `--auto-connect`, or CDP only after explicit user consent. Prefer ephemeral state; persistent profiles include IndexedDB/cache/service workers, while session-name persistence is narrower.

### 3. Use bounded, machine-readable observations

- Use `--json` for snapshots, storage, cookies, request logs, console/errors, and eval results when structured parsing helps.
- Apply `--content-boundaries` to page-derived output and a documented default `--max-output 20000`; scope/filter first before raising the limit.
- Prefer `snapshot -i -c`, `-d <depth>`, or `-s <selector>` over full DOM/HTML. Return primitive, allowlisted, size-bounded values from eval.
- Never treat truncation as absence. If output is truncated, narrow the selector, route filter, storage key, console time window, or returned object.
- Screenshots should use an explicit user-approved or temporary path; report the path and remove temporary evidence when it is no longer needed.

### 4. Prefer snapshot refs, with strict ref lifecycle

- `open` → meaningful `wait` → `snapshot -i -c` → use `@eN` refs.
- Re-snapshot after navigation, submission, modal/dropdown changes, hydration, or any dynamic rerender before reusing a ref.
- Use semantic `find role|label|text|testid` when refs are stale/unavailable; use quoted CSS selectors only as a fallback.
- Quote URLs, selectors, and all multiword/user-derived values. Use a single-quoted heredoc with `eval --stdin` for complex JS; reserve simple single-quoted expressions for trivial evals.
- Do not chain commands when intermediate output determines the next ref or action. Chaining is acceptable only for deterministic steps such as `open && wait`.

### 5. Make the network limitation a first-class constraint

The reference will prescribe this 0.18.0 sequence:

1. Open the page and establish baseline state.
2. Clear old request records.
3. Call `network requests --json` once **before** the action to attach tracking.
4. Perform exactly one reproduction action.
5. Read `network requests --filter '<narrow route>' --json` and immediately redact sensitive request headers before quoting/reporting them.
6. If another clean capture is required, prefer a fresh named session because repeated reads in 0.18.0 can add listeners and produce duplicates.

Document that this proves only request URL/method/request headers/timing/resource type. It does **not** prove response status, response headers, or body. For missing response facts:

- First use UI state, console/page errors, and server logs supplied by the user.
- For a safe, idempotent endpoint only, a separately identified page-context `fetch` probe may return status and an allowlist of non-secret response headers, consume and truncate the body, and obey same-origin/CORS behavior. Label this as a new probe, not observation of the SPA's original request.
- Never replay a mutation, auth exchange, payment, email, deletion, or production write merely to obtain status.
- Do not use undocumented internal protocol commands or claim a Playwright trace is directly queryable through the CLI.

### 6. Handle secrets and production conservatively

- Never ask the user to paste a password, bearer token, cookie, full storage dump, or raw JWT into chat or a shell command.
- Prefer user-completed headed login or a pre-existing named auth-vault entry. If creating a vault entry is explicitly requested, require `--password-stdin`; never use `--password` or `echo 'secret'` examples.
- Treat `--auto-connect`, CDP, existing profiles, state files, and persistent session names as access to real authenticated state. Explain scope and obtain consent before use.
- State files contain tokens; keep them outside the repository, encrypt where supported, restrict permissions, and delete them after the task. Never run `state clear --all`.
- Read specific storage keys instead of dumping all storage. For JWT diagnosis, eval should decode only the requested token in browser memory and return allowlisted claims (`iss`, `aud`, `sub` if needed, `role`, `iat`, `exp`, derived expiry); never return the compact token or signature, and state that decoding does not verify authenticity.
- Request logs can contain `authorization`, cookies, API keys, and query tokens. Redact values before including evidence; output limits are not a redaction mechanism.
- For production, default to read-only reproduction. Require confirmation before login attempts, form submits, state changes, route interception/mocking, global headers, offline mode, uploads/downloads, or any destructive action. Use separate dev/prod sessions so cookies, storage, and caches do not cross-contaminate comparisons.
- Use `--allowed-domains` where the target's app/API/auth/CDN domains are known; add only observed legitimate dependencies. Note that allowlisting blocks nonlisted subresources and can itself cause a false reproduction.

### 7. Split stable guidance from version-sensitive details

Recommended structure:

```text
pi-config/skills/web-debug/
├── SKILL.md
└── references/
    └── agent-browser-workflows.md
```

- `SKILL.md`: precise trigger, prerequisite/fail-closed policy, core diagnostic loop, safety/session contract, short playbooks, limits, and link to the reference.
- `references/agent-browser-workflows.md`: validated 0.18.0 command mappings, quoting examples, network priming/limitations, storage/JWT snippets, auth modes, recovery matrix, and cleanup checklist.

Do **not** add a helper script in this change. A wrapper could sanitize ambient configuration, but it would add a second command interface, complicate opt-in auth/persistence, and require its own portability/security tests in a repository with no skill test harness. Instead, the skill must inspect only the names (not values) of active `AGENT_BROWSER_*` variables and whether user/project config files exist, explain that config/env can select profiles/providers/proxies/extensions, and ask before inheriting shared or persistent modes. If repeated misuse demonstrates that prose is insufficient, add a narrowly tested launcher in a follow-up.

Do not copy the installed upstream skill into the repository; its maintainers warn copied node-module content becomes stale, and its generic automation guidance is broader than this debugging skill.

## Command mapping to encode

| Old concept | `agent-browser` 0.18.0 workflow | Important difference |
|---|---|---|
| Navigate | `agent-browser --session <s> open '<url>'`, then `wait --load domcontentloaded` or a route/selector condition | `networkidle` is optional and can hang on streaming apps. |
| Discover/interact | `snapshot -i -c`; `fill @eN`, `click @eN`, `select`, `check`; semantic `find` fallback | Re-snapshot after state changes; refs are not stable. |
| Eval | `eval '<simple expression>'`; complex JS via `eval --stdin <<'EVALEOF'` | Return primitives/bounded objects; quoted heredoc avoids shell expansion. |
| Console | `console --json`; `errors --json`; clear deliberately before a clean run | Reads retain data; they do not drain by default. |
| Network | prime `network requests` before action; then filtered `network requests --json` | Request metadata only; no response headers/status/body; repeated reads may duplicate future entries. |
| Screenshot | `screenshot '<path>'`, `--full`, or `--annotate` when labels help | Save to an explicit/temp path and inspect the image; annotated refs also become stale after changes. |
| Local/session storage | `storage local get '<key>' --json`, `storage session get '<key>' --json` | Prefer a key; do not dump token-bearing stores. |
| Cookies | `cookies get --json` or a narrowly justified cookie operation | Output is sensitive; HttpOnly cookies are visible to the CLI even though page JS cannot read them. |
| IndexedDB/runtime state | targeted `eval --stdin` | `storage` does not cover IndexedDB; profile persistence does. |
| Auth | headed user completion or `auth login <provided-vault-name>`; opt-in `--profile`/`--state`/`--session-name` | Do not put secrets in argv, examples, logs, or chat. |
| JWT | targeted eval that base64url-decodes and returns allowlisted claims only | Decode is not signature verification; never return raw token. |
| Production comparison | separate named sessions, same minimal scenario and viewport, bounded evidence | Read-only by default; no shared state or mutation without consent. |
| Close | `agent-browser --session <s> close` | Close only the investigation session; persistence cleanup is separate and opt-in. |

## Error recovery to encode

| Failure | Recovery |
|---|---|
| `agent-browser` absent | Report blocked with the failed check; do not install and do not use `browser-use` or Playwright as fallback. |
| Version differs from validated 0.18.0 | Run relevant `--help`, avoid unsupported examples, and report compatibility uncertainty; do not silently assume parity. |
| Browser binary/daemon launch fails | Report prerequisite failure; retry once only after closing the named session. Never `killall` or close unrelated sessions. |
| Stale/missing ref | Wait for the expected condition, take a fresh scoped snapshot, and reacquire the element semantically. |
| Timeout | Prefer selector/text/URL/function waits; avoid arbitrary long sleeps and warn that timeouts above 30s can hit the CLI IPC limit. |
| Empty request log | Confirm tracking was primed before the action; reproduce in a fresh session. Do not conclude no request occurred from an unprimed log. |
| Duplicate request entries | Deduplicate by method/URL/timestamp for reporting or use a fresh session; identify this as 0.18.0 listener behavior. |
| Missing response status/headers | State the limitation; use non-network evidence or a separately approved safe probe. Do not infer. |
| Truncated output | Narrow scope/filter/key/returned fields before increasing `--max-output`. |
| Allowed-domain breakage | Identify the exact legitimate blocked origin and add it deliberately, or rerun without the allowlist only with user approval. |
| Auth state fails to load | Close that session first, validate state path/permissions, and retry; never inspect or print token contents. |
| Cleanup fails | Report the session name and failure accurately; do not claim cleanup succeeded or close all sessions. |

## Exact target files

1. **Rewrite** `pi-config/skills/web-debug/SKILL.md`.
   - Keep `name: web-debug`.
   - Replace the description with an `agent-browser`-specific runtime-debugging trigger covering login/auth, 401/403/CORS, storage/JWT/session, forms, blank/hydration/stale-data failures, prod-only behavior, and end-to-end verification.
   - Consider `allowed-tools: Bash(agent-browser:*)` only if validated in the installed pi; because the field is experimental and prerequisite checks also need ordinary shell inspection, omission is preferable to a misleading incomplete allowlist.
   - Replace all `browser_*` names and implicit persistence claims.
   - Preserve the original playbook categories but route details to the reference.

2. **Add** `pi-config/skills/web-debug/references/agent-browser-workflows.md`.
   - Mark command examples as validated against 0.18.0 and instruct future agents to consult `agent-browser <command> --help` when the installed version differs.
   - Include exact safe command shapes, network priming, unsupported response behavior, auth/state/JWT cautions, and the recovery/cleanup matrix.

3. **Update** `pi-config/README.md`.
   - Change the skill catalogue entry so `web-debug` uses installed `agent-browser`, not the pi browser extension.
   - Add `agent-browser` as an external prerequisite for this skill with availability/version checks; do not add install commands or imply it is an extension-local dependency.
   - Leave the separate browser extension entry and setup intact.

4. **Update** `pi-config/docs/system-maps/pi-config-overview.md`.
   - Change only `web-debug` coupling and runtime-observation statements to the CLI-based design.
   - Preserve accurate facts about the still-present browser extension.
   - Refresh the map's evidence-basis wording if needed so it does not claim the updated text describes only commit `f82da56`.

No other production file is planned.

## Staged implementation plan

### Stage 1 — Rewrite the skill contract

1. Update frontmatter description and introductory language in `SKILL.md`.
2. Add a fail-closed prerequisite block: resolve an executable with `command -v`, print/check `--version`, never install, and never fall back.
3. Define explicit unique-session naming, per-command session targeting, lifecycle, cleanup, and the consent boundary for persistent/shared browser modes.
4. Recast the core loop as reproduce → observe → hypothesize → verify, separating evidence from inference.
5. Add compact routing from symptom wording to the retained playbooks.

**Acceptance:** the skill can be understood without the old extension, contains no `browser_*` command, and makes ephemeral explicit sessions the default.

### Stage 2 — Encode exact workflows and limitations

1. Create `references/agent-browser-workflows.md` with the command mapping above.
2. Provide short runnable shapes for auth, bad request, targeted storage, safe JWT claim decode, form submission, blank screen, dev/prod comparison, and post-change verification.
3. For every example, use a named session, quoted values, current snapshot refs, bounded output, and deliberate waits.
4. Add the 0.18.0 network priming sequence and explicit response status/header/body limitation.
5. Add output handling, secret redaction, production safety, and error recovery.
6. Link the reference from `SKILL.md` only where detailed commands are needed, preserving progressive disclosure.

**Acceptance:** every required area has an exact CLI path or an explicit unsupported statement; no example exposes a literal password/token or relies on undocumented commands.

### Stage 3 — Synchronize catalogue documentation

1. Update `pi-config/README.md` skill/dependency descriptions.
2. Update only affected `web-debug` relationships in the system map, leaving the browser extension documented as a separate optional component.

**Acceptance:** repository documentation no longer says `web-debug` requires the browser extension, while still accurately listing that extension.

### Stage 4 — Static and controlled verification

1. Verify no old commands remain:
   - `rg -n 'browser_(goto|fill|click|console|network|eval|screenshot|close)|browser_\*' pi-config/skills/web-debug`
   - Expected: no matches.
2. Verify command vocabulary in examples against `agent-browser 0.18.0 --help` and relevant subcommand help. Pay special attention to global-flag placement, `storage ... get`, `cookies get`, `snapshot -i -c`, `eval --stdin`, and `network requests`.
3. Validate frontmatter manually against pi conventions: valid name, nonempty specific description under 1024 characters, and no unsupported required tool declaration.
4. Check all relative links from `SKILL.md` resolve and all Markdown fences/heredoc delimiters balance.
5. Use a temporary, local-only HTTP fixture outside the repository for runtime acceptance; do not navigate production:
   - page with a form, dynamic rerender, console message, uncaught error route, local/session storage, a dummy JWT, and an API route;
   - exercise open/wait/snapshot/ref/fill/click/resnapshot/eval/console/errors/screenshot;
   - prime request tracking before a fetch, verify request URL/method/header visibility, and confirm the documented absence of response headers/status in `network requests` output;
   - verify a separately labeled safe GET probe can return a status without being mistaken for the original request;
   - verify scoped JSON output and truncation guidance;
   - use only dummy credentials/tokens.
6. Run lifecycle scenarios:
   - two named sessions do not share ephemeral state;
   - stale refs require a new snapshot;
   - the exact test session closes successfully;
   - no test session remains in `session list`;
   - no state/auth/screenshot fixture remains outside explicitly retained evidence.
7. Simulate an unavailable executable with a restricted `PATH` while reviewing the documented branch; confirm the instructions block rather than install/fallback.
8. Review the final diff for accidental changes outside the four target paths.

**Acceptance:** all static checks pass; the controlled fixture demonstrates the documented commands and limitations; cleanup leaves no named test session, auth state, or secret-bearing artifact.

## Risks and mitigations (premortem)

1. **The migration mechanically renames commands but preserves false old semantics.**
   - Mitigation: explicitly test persistence, console retention, network priming, refs, and unsupported response metadata against 0.18.0 rather than mapping by name alone.

2. **Network debugging produces a confident but false diagnosis.**
   - Mitigation: prime capture before action, narrow the route, disclose request-only evidence, label duplicate-listener behavior, and prohibit inferred status/response headers.

3. **The skill leaks production auth through logs, storage, argv, screenshots, or saved state.**
   - Mitigation: ephemeral sessions, targeted keys/claims, vault/headed login preference, redaction before reporting, explicit consent for shared state, temporary paths, and finally-style cleanup.

4. **Output flooding or hostile page text overwhelms the agent.**
   - Mitigation: content boundaries, 20k default limit, scoped snapshots, filtered request logs, primitive eval output, and scope-first recovery.

5. **Version drift silently invalidates examples.**
   - Mitigation: mark the reference as validated for 0.18.0, check installed version on every use, consult subcommand help on mismatch, and keep version-sensitive detail out of the main skill.

6. **An allowlist or clean session changes the behavior being diagnosed.**
   - Mitigation: record isolation settings, add required app/API/auth/CDN domains deliberately, and use shared/persistent state only when the hypothesis requires it and the user consents.

## Rollback and recovery

- The change is documentation/skill-only. Roll back by restoring the prior versions of `SKILL.md`, `README.md`, and the system map and deleting the new reference file.
- No data migration is required.
- Runtime sessions created during verification are isolated and should be closed by exact name. Never use global cleanup as rollback.
- If network parity proves insufficient, retain the safe CLI migration and open a separate enhancement for an upstream-supported response-inspection command; do not reintroduce missing `browser_*` calls as a hidden fallback.

## Open questions

None materially block implementation.

Runtime consent remains mandatory for:

- inheriting an existing Chrome/CDP/profile/session or ambient persistent configuration;
- creating/reusing saved auth state or an auth-vault entry;
- handling any credential/token through a user-approved secure channel;
- executing a production action that may mutate data;
- relaxing domain restrictions or retaining screenshots/traces/state artifacts.
