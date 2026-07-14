---
name: style-sync
description: Match the existing codebase's conventions in every code change. Use before writing or editing code — infer naming, formatting, imports, comments, and architecture from surrounding code, then mirror them exactly.
---

# Style Sync

## Purpose

Make generated code indistinguishable from code the project's own maintainers would write. The codebase is the style guide; consistency beats personal preference.

## Activation

Before writing or modifying any code in an existing project. Not needed for greenfield files in an empty repository, where the user's stated preferences apply instead.

## Workflow

1. **Observe.** Before writing, look at the file being edited and one or two nearby files of the same kind (a sibling component, a neighboring module, an existing test).
2. **Infer the conventions** from what you see:
   - **Naming** — casing of files, functions, classes, variables, constants; prefixes and suffixes (`use*`, `*Service`, `*_test`).
   - **Formatting** — indentation, quote style, semicolons, line length, trailing commas, brace placement.
   - **File organization** — where each kind of file lives, one-thing-per-file vs. grouped, how tests sit relative to source.
   - **Import ordering** — grouping (stdlib / external / internal), sorting, relative vs. absolute paths, aliases.
   - **Commenting style** — density, doc-comment format (JSDoc, docstrings), whether comments explain "why" or are absent.
   - **Architectural patterns** — error handling style, state management, how existing features are layered, what abstractions are already in use.
3. **Mirror.** Write the change as if the original author had. Reuse existing helpers and patterns instead of inventing parallels.
4. **Verify.** Reread the diff: would it pass review without a single style comment? If any line looks foreign next to its neighbors, fix it.

## Core Principles

1. **The codebase outranks your defaults.** If the project uses a style you wouldn't choose, use it anyway.
2. **Local beats global.** Match the file being edited first, then its directory, then the repo at large.
3. **Consistency over correctness of taste.** A consistent "suboptimal" pattern is better than a mixed one.
4. **No new conventions unless explicitly requested.** Improving style is a separate task the user must ask for.

## Rules

- Match comment density: don't add comments to a sparsely-commented codebase, or omit doc comments where every function has one.
- Copy the error-handling idiom already in use (exceptions vs. result values, logging style) rather than your preferred one.
- Follow the existing test style — framework, naming, structure of arrange/act/assert — when adding tests.
- Never reformat lines you aren't changing; keep diffs limited to the actual change.
- Never introduce a new dependency, utility, or abstraction when the project already has one for the job.
- When the project has a linter or formatter config, treat it as authoritative over inferred style.

## Examples

**Adding a function to a module** where functions are `snake_case`, have one-line docstrings, and raise exceptions: the new function does exactly that — even if you'd normally write it differently.

**Creating a new React component** in a repo where components are function declarations in PascalCase files with styles co-located: the new component follows that shape, not an arrow-function-plus-CSS-modules pattern from elsewhere.

**Writing a test** in a suite that uses `describe`/`it` with plain asserts and no mocking library: the new test uses the same tools, not a mocking framework the repo doesn't have.

## Edge Cases

- **Inconsistent codebase:** match the dominant or most recent convention, favoring the files closest to the change. Note the inconsistency to the user only if it materially affects the work.
- **No comparable code exists** (first test, first API route): borrow from the nearest analogue in the repo; fall back to the ecosystem's standard style only if there is none.
- **User's request conflicts with the codebase style:** the user's explicit instruction wins — apply it to the new code without restyling the rest.
- **Linter config contradicts the actual code:** follow the config; the code is likely drifting.

## Things To Avoid

- Restyling, reformatting, or "cleaning up" code the task didn't touch.
- Introducing your habitual patterns (different quote style, extra abstraction layers, defensive comments) into a codebase that doesn't use them.
- Mixing conventions within one change.
- Adding style-guide commentary to the output — just write conforming code.
- Treating this skill as a license to audit style; it governs new code, not existing code.
