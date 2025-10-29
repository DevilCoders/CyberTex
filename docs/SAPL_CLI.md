# SAPL Command-Line Interface

The SAPL CLI provides a cohesive toolbox for authoring, testing, and deploying
projects. It embraces a discoverable syntax with descriptive subcommands and
human-friendly defaults so new operators can become productive quickly.

## Getting Help

```bash
sapl --help
sapl <command> --help
```

Each command surfaces usage examples, common options, and configuration hints.
Context-aware suggestions propose the next logical steps based on your current
workspace layout.

## Project Scaffolding

```bash
sapl init mission-kit --template purple-team
sapl new module reconnaissance --into src/playbooks
sapl fmt
```

- `sapl init` bootstraps folder structures, `required.yaml`, and starter tests.
- Templates encapsulate best practices for blue, red, or purple workflows.
- `sapl fmt` enforces the readability conventions described in
  [READABILITY_AND_STYLE.md](READABILITY_AND_STYLE.md).

## Environment Management

```bash
sapl env create
sapl env info
sapl env sync --profile ops
```

The CLI integrates with the virtual environment tooling described in
[SAPL_ENVIRONMENTS.md](SAPL_ENVIRONMENTS.md), ensuring dependencies remain
consistent across platforms.

## Testing with `sapl-test`

`sapl-test` offers pytest-inspired ergonomics for validating playbooks,
compilers, and plugins.

```bash
sapl-test tests/ --focus payloads --report junit.xml
```

- Test discovery recognises `.sapl` fixtures alongside `.yaml` helpers when
  required. Python sources no longer need `.py` companions because the runtime
  imports SAPL modules directly.
- Assertions cover runtime output, emitted artifacts, and compliance policies.
- Rich reports integrate with CI dashboards and the SAPL website build pipeline.

## Advanced Tooling

- `sapl graph` renders data-flow diagrams and execution timelines as Graphviz
  files for documentation.
- `sapl inspect` introspects modules, classes, and functions, exposing type
  information and docstrings.
- `sapl profile` captures performance traces consumable by the advanced
  compiler's optimization passes.

## Automation and Scripting

All commands support machine-readable output via `--format json`. Combine this
with shell pipelines or Python scripts to orchestrate large-scale operations.

```bash
sapl compile project.sapl --format json | jq '.artifacts[] | select(.os == "linux")'
```

Use `sapl run <script.sapl>` to execute ad-hoc scripts with the interpreter, or
`--watch` to rerun tasks when inputs change.

## Extensibility

CLI plugins register under `plugins/cli` and can add new commands, flags, or
output renderers. Document custom interfaces in the project README so teammates
can discover them quickly.
