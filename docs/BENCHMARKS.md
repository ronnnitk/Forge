# Forge Benchmarks

This file tracks the efficiency of the Forge Context Engine over time. 
Do not fabricate results; run the tasks in your environment and record the deterministic outcomes.

## Benchmark Template

| Repository | Task | Files Opened | Files Skipped | Est. Context Saved (Tokens) | Est. Token Reduction | Time | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `demo` | "Fix navbar spacing" | 1 (`Navbar.tsx`) | 2 | ~500 | 66% | <1s | Pass |
| | | | | | | | |
| | | | | | | | |

* **Files Opened**: Number of files the ranker confidently recommended for opening.
* **Files Skipped**: Number of files the ranker successfully ignored.
* **Est. Context Saved**: Roughly how many lines/tokens were avoided by skipping the files.
