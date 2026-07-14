# Forge

A Claude Code plugin that helps Claude work more efficiently. Pure Skills — no scripts, hooks, or configuration.

## Skills

### Context Shield (`/context-shield`)

Minimizes context usage before Claude reads any files. Instead of sweeping the repository, Claude:

1. Extracts keywords from the request and predicts candidate files.
2. Ranks candidates by simple relevance signals — user-provided filenames, stack traces, filename and directory similarity, exported symbols, import relationships.
3. Forms a brief reasoning report: which files it will read, why, which it is skipping, and the estimated context savings.
4. Opens only the top-ranked files, and expands one step at a time only while confidence is low.

### Style Sync (`/style-sync`)

Keeps generated code consistent with the existing codebase. Before writing code, Claude observes nearby files and infers the project's naming, formatting, file organization, import ordering, commenting style, and architectural patterns — then mirrors them exactly. It never introduces new conventions unless explicitly asked.

## Context Ranker

The first executable component of Forge. The Context Ranker is a lightweight, purely deterministic CLI tool that ranks likely relevant files based on a task description.

- **What it does**: Extracts keywords from a request, scans filenames first, then selectively scans text/symbols, and outputs a ranked list of candidate files with confidence scores and reasoning.
- **What it intentionally does NOT do**: It does not read full source files, build indexes, run caching layers, use machine learning, or rely on embeddings/vector databases. It relies on the Python standard library for maximum simplicity.
- **How to run it**: 
  ```bash
  python src/context_ranker.py --repo <path_to_repo> --task "<your task description>"
  ```

## Structure

```
forge/
├── .claude-plugin/
│   └── plugin.json          # plugin manifest
├── skills/
│   ├── context-shield/
│   │   └── SKILL.md
│   └── style-sync/
│       └── SKILL.md
├── LICENSE
└── README.md
```

## Development

Validate the plugin locally:

```bash
claude plugin validate .
```

## License

[MIT](LICENSE)
