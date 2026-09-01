---
name: session-retrospective
description: Runs a bounded, evidence-based session retrospective and carries approved general lessons through implementation and verification. Use when closing a substantial session, reviewing how agent work went, or turning session lessons into durable improvements.
---

# Session Retrospective

Close the learning loop without turning the transcript into permanent prompt clutter.

## 1. Freeze the evidence boundary

1. Locate the canonical **parent** session JSONL, not a subagent transcript, render, or copied artifact.
2. Capture one fixed cutoff at the final byte of the last complete newline-terminated JSONL record available when the retrospective starts. Record the file identity, cutoff byte, and complete-record count.
3. Parse only complete parent records ending at or before that cutoff. Ignore a trailing partial record and never advance the cutoff, including after a turn change or reload.

If the parent file or a safe complete-record cutoff cannot be established, report the block instead of substituting a different transcript.

## 2. Build a minimal evidence ledger

- Separate observations from interpretations. Cite only the record number or timestamp and the relevant command, result, decision, or file.
- Redact credentials, tokens, personal data, private URLs, and unrelated content before notes or chat output.
- Do not copy the raw transcript into chat or an artifact. Preserve only the smallest paraphrased evidence needed to support a lesson.
- Distinguish a process failure from an expected exploration, an external failure, or a good recovery.

## 3. Deduplicate before proposing work

Inspect relevant durable status files, plans, artifacts, issues or ADRs, repository status and worktrees, and live run/subagent state. Reuse valid work and link to an existing owner or artifact. Do not create a retry, replacement, or second tracking item for work that is active, complete, or already represented.

## 4. Translate lessons into the smallest durable mechanism

For each supported lesson, choose the earliest adequate layer in this order:

1. code invariant
2. automation or test
3. skill or template
4. opt-in prompt snippet
5. documentation
6. temporary guardrail with an owner and removal condition

Prefer a systemic fix to a permanent prohibition. Keep speculative hardening outside the current scope. Do not make every lesson a snippet, and do not preserve incident-specific detail when a general invariant is sufficient.

## 5. Get disposition on a small action set

Propose only the highest-leverage actions, usually one to three. For each action state:

- evidence-backed lesson;
- chosen mechanism;
- exactly one owner and one canonical path or resource;
- implementation boundary;
- behavioral proof that will count as verified.

Ask for an explicit disposition for every action: **approved**, **deferred**, **rejected**, or **superseded**. Resolve overlap before implementation; approval is not permission for adjacent cleanup.

## 6. Implement, sync, and verify

- Implement only approved, general changes at their assigned paths. Preserve unrelated work.
- When a changed resource is maintained in `pi-config`, discover the effective loaded global destination, compare source and destination first, and sync only that resource. Never overwrite unrelated or divergent global content silently; merge narrowly or stop for disposition. Reload only when the resource type requires it.
- Verify behavior, not merely file presence: exercise the invariant or automation, confirm skill discovery/frontmatter, invoke the snippet loader path, or perform the resource's smallest real smoke test.
- Record concise proof and any limitation for each action. “Should work,” a clean diff, or successful copying alone is not behavioral verification.

## 7. Status and closure

**Analysis complete** means the cutoff-bounded evidence was reviewed and lessons/actions were proposed. It does not mean the work is closed.

Mark the retrospective **CLOSED** only when every approved action is applied and behaviorally verified, or has since been explicitly deferred, rejected, or superseded. An applied but unverified action remains open. Report proof or disposition beside every action.

Do not create a status artifact for a single-turn retrospective. If work must span turns or a reload, keep at most one compact status Markdown file containing the fixed cutoff, action owner/path, disposition, proof, and next step. Update or remove that file rather than creating parallel notes; never put raw transcript text in it.
