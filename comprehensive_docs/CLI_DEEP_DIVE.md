# SAPL CLI Deep Dive

The SAPL command line mirrors the ergonomics of Python's tooling while extending it with security-focused workflows. This document captures every subcommand, key option, and integration hint.

## Global Conventions

- All commands accept `--plugin` and `--plugin-dir` arguments where applicable, enabling you to preload Python hooks for custom behaviour.
- Any command returning structured information supports `--json` to emit machine-readable payloads suitable for automation.
- Invalid invocations return non-zero exit codes. Use these for CI gating and deployment pipelines.

## Core Commands

### `sapl run`
Execute a SAPL script from disk. Optional flags:

- `--lint`: run the linter before execution and abort on errors.
- `--json`: emit the execution plan in JSON format.
- `--plugin`/`--plugin-dir`: register runtime plugins prior to execution.

### `sapl lint`
Statically analyse scripts and return diagnostics. When integrating with editors, invoke with `--json` to produce structured messages referencing line numbers and severities.

### `sapl highlight`
Produces ANSI-highlighted output that can be piped through `less -R` or captured by terminal dashboards. Customize colour schemes with `--theme`.

### `sapl compile`
Generate machine code, bytecode, or transpiled Python. Combine with `sapl advanced-compile` to capture structural metadata for auditing purposes.

### `sapl advanced-compile`
Emits a combined artifact describing compilation output, optimisation metadata, and symbol tables. Supports `--json` for pipeline integration.

## Advanced Workflow Commands

### `sapl inspect`
Parse a script and report its structural components without execution. JSON output includes module docstrings, imports, functions (with async markers and default parameters), tasks, payloads, and summary statistics.

### `sapl shell`
Launch an interactive shell with persistent interpreter state.

- `--script path.sapl`: preload a script and expose its definitions.
- `--execute "STATEMENTS"`: run snippets non-interactively—useful for CI checks or templated scaffolding.
- `--json`: when used with `--execute`, emit shell deltas as JSON records.

Inside the shell, the following commands are available:

- `:run` — execute the buffered statements immediately.
- `:reset` — clear the interpreter state.
- `:load path.sapl` — load additional files into the current session.
- `:state` — print the current execution context.
- `:exit` — leave the shell.

### `sapl website`
Manage the bundled advanced website.

- `--list`: enumerate shipped assets.
- `--export ./public`: export the static site to a directory.
- `--serve --port 8090`: preview the site locally using the built-in HTTP server.

### `sapl test`
Discover and run SAPL-native test suites, respecting plugins and JSON reporting. Combine with `sapl shell --execute` to seed data before running tests.

### `sapl venv`
Create a virtual environment preloaded with `sapl-required.yaml`. Use `--print-required` to display the resolved dependency manifest.

## Automation Strategies

1. **Editor Integration**: pair `sapl lint --json` with your IDE to deliver inline diagnostics.
2. **CI Pipelines**: run `sapl compile --target machine` to validate compiler output, then `sapl test --json` to produce structured reports for dashboards.
3. **Interactive Prototyping**: start `sapl shell --script examples/extended_features.sapl` to explore data interactively before codifying automation.

For a catalogue of examples using these commands, see [WORKFLOWS.md](WORKFLOWS.md).
