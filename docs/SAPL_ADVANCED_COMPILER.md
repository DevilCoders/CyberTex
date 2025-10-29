# SAPL Advanced Compiler

The SAPL advanced compiler targets teams that need production-grade builds
across red, blue, and purple-teaming projects. It layers additional static
analysis, optimization, and packaging features on top of the standard
interpreter so your deliverables stay predictable and easy to audit.

## Feature Highlights

- **Incremental compilation** keeps turnaround fast by caching dependency graphs
  and only rebuilding the modules that changed.
- **Cross-platform emitters** produce bytecode bundles and native launchers that
  run on Linux, macOS, and Windows without modifying the source tree.
- **Security-focused passes** flag unsafe API usage, dangerous subprocess
  spawning patterns, and missing sandboxing directives before code ships.
- **Profile-guided optimizations** integrate with `sapl-prof` traces to inline
  hotspots, prune dead branches, and tighten data pipelines used in forensic
  automation.

## Usage

```bash
sapl compile mission.sapl --profile=prod \
  --target linux,macos,windows \
  --emit launcher,bytecode --opt-level aggressive
```

- `--profile` loads presets from `required.yaml` so you can share compiler
  settings with the rest of the team.
- `--target` accepts one or more operating systems; the compiler automatically
  bundles the proper runtime shims.
- `--emit` controls which artifacts to produce. Launchers combine the runtime
  with your bytecode to simplify deployment.
- `--opt-level` toggles the optimization tiers. The `aggressive` tier enables
  speculative execution guards and structural pattern folding.

## Diagnostic Workflow

1. Run `sapl compile --analyze mission.sapl` to execute static analyzers without
   emitting artifacts.
2. Review the generated `analysis.json` report for complexity spikes, dangerous
   regular expressions, or tainted data flows.
3. Use `sapl fix` to apply recommended rewrites where applicable, or stage
   targeted manual patches.

## Extensibility

Compiler behavior can be extended through plugin hooks registered in
`plugins/compiler`. Each hook receives the abstract syntax tree and build
context, letting you enforce organization-specific policies.

```yaml
# required.yaml
compiler:
  plugins:
    - plugins.compiler.inline_payloads
    - plugins.compiler.enforce_signoff
```

Plugins may expose configuration parameters that you can forward using
`--plugin-config path/to/settings.yaml`.

## Troubleshooting

- **Inconsistent results between hosts** usually indicate mismatched runtime
  versions. Run `sapl doctor` to verify dependencies.
- **Memory pressure** during compilation can be mitigated with
  `--limit workers=2` to reduce parallelism on constrained CI runners.
- **Debugging transformations** is easier with `--dump-ast` and
  `--dump-ir`, which save intermediary representations alongside the build
  artifacts.

Refer to [GUI_AND_CLI_COMPILATION.md](GUI_AND_CLI_COMPILATION.md) for build
pipelines targeting graphical tooling and command-line clients.
