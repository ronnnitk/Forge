---
name: context-shield
description: Minimize context usage when exploring a repository. Use before reading any files for a code task — rank candidate files by relevance, read only the top-ranked ones, and expand gradually only when confidence is low.
---

# Context Shield

## Purpose

Reduce token usage by reading the fewest files needed to complete a task correctly. Context is a budget: every file read must earn its place, and the reasoning behind each read should be explicit.

## When it activates

Before the first file read of any code task — implementing a feature, fixing a bug, answering a question about the code, or refactoring. It does not apply once the relevant files are already in context.

## Core principles

1. **Predict before you read.** Form a hypothesis about which files are involved from the request alone, then verify it cheaply.
2. **Rank before you open.** Score candidates by relevance signals and open only the top of the list.
3. **Search is cheaper than reading.** A search result costs a few lines; an opened file costs hundreds. Filenames (Glob) before contents (Grep), contents before full reads.
4. **Expand incrementally.** Grow context one step at a time from evidence, never by sweeping directories.
5. **Be explainable.** Every file opened has a stated reason; every plausible file skipped has one too.

## Workflow

1. **Understand the request.** Restate it in one line: what feature, bug, or component is involved?
2. **Extract keywords.** Feature names, error messages, UI strings, function or route names, filenames the user mentioned.
3. **Predict candidate files.** Locate them cheaply: Glob for likely filenames first; Grep contents only if names don't resolve it.
4. **Assign each candidate a relevance score** (high / medium / low), judged from these signals — no formulas, just reasoning:
   - **User-provided filenames** — the user named the file or path. Strongest signal.
   - **Stack traces** — a file appears in an error trace. Nearly as strong.
   - **Filename similarity** — the name matches the task's keywords (`login`, `export`, `retry`).
   - **Directory similarity** — the file lives where this kind of code belongs (`auth/`, `cli/`, `api/`).
   - **Exported symbol names** — search shows it defines the function, class, or route in question.
   - **Import relationships** — it is imported by, or imports, a file already confirmed relevant.
5. **Rank the candidates** and produce the reasoning report (below).
6. **Open only the highest-ranked files** — typically 1–5. For large files, read the relevant section, not the whole file. Low-ranked files stay closed unless evidence promotes them.
7. **Reassess confidence:**
   - **High (>80%)** — the code in context explains the behavior or is clearly where the change goes. Stop expanding; do the task.
   - **Low** — follow one concrete lead (an import, a caller, a config key), re-rank, and reassess. One hop at a time.

## Reasoning report

Before reading, form a brief internal report — a few lines, not a document:

- **Task:** one line.
- **Confidence:** high / medium / low, before reading.
- **Candidates:** each file with its score and the signal that earned it ("`auth/login.ts` — high: filename match + defines `handleLogin`").
- **Skipped:** plausible-looking files deliberately not opened, and why.
- **Expected reads:** roughly how much will be read (e.g. "2 files, ~200 lines").
- **Estimated savings:** what a naive sweep would have read instead.

Keep it terse. It guides the file selection; it is not a deliverable and must not become verbose or repeated at every step.

## Rules

- Never recursively read a repository or list every directory "to get oriented."
- Never open a file without a stated reason it is relevant.
- Never open a low-ranked file while higher-ranked ones remain unread.
- Prefer reading a symbol's definition (found via search) over reading the whole file that contains it.
- Follow imports and references outward from confirmed-relevant files; don't guess sideways.
- If two candidates tie, check both cheaply (grep for the key symbol) rather than reading both fully.
- Tests, docs, and generated files are read only when the task is about them or they are the only evidence of intended behavior.

## Examples

**Bug: "Login button does nothing on mobile"**
Keywords: login, button, mobile. Candidates: `LoginButton.tsx` (high — filename match), `auth/api.ts` (low — backend, no evidence yet), `useAuth.ts` (medium — likely imported by the button). Read the button component; follow its handler only if it points elsewhere. Backend stays closed.

**Feature: "Add a --json flag to the export command"**
Glob `*export*` → `commands/export.js` (high — filename + directory match). Read it, plus one sibling command that already has a flag (medium — pattern reference). Two files total; the CLI framework stays closed.

**Question: "Where is the retry logic for API calls?"**
Grep `retry` → answer from the definition site shown in search context. Possibly zero full file reads.

## Edge cases

- **Unfamiliar repo layout:** one shallow listing of the root (top level only) is allowed to learn conventions — not a recursive walk.
- **Search terms find nothing:** the user's vocabulary may differ from the code's. Try synonyms and related terms before widening scope.
- **All candidates rank low:** confidence is low by definition — take one cheap step (a targeted grep, a shallow listing of the most plausible directory) to generate better candidates instead of opening weak ones.
- **Cross-cutting change (rename, API migration):** grep for the symbol to enumerate affected sites; read each site narrowly rather than each file fully.
- **Task genuinely requires broad context (architecture review):** state that up front, then still rank — entry points and summaries before leaf files.

## Things to avoid

- Reading files "just in case" or to confirm what search already showed.
- Re-reading files already in context.
- Opening every file in a directory because one file there was relevant.
- Expanding scope after confidence is already high.
- Treating low confidence as license for a full-repo sweep — it means take the next single step.
- Inflating the reasoning report into a ceremony; a few lines before reading is enough.
