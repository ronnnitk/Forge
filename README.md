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
