# Maintainability Guidelines

Large SAPL projects benefit from consistent structure and tooling. This guide consolidates best practices for keeping playbooks, libraries, and tooling approachable.

## Project Layout

```
project/
├── sapl-required.yaml
├── packages/
│   └── your_package/
│       ├── __init__.sapl
│       └── modules...
├── scripts/
│   └── main.sapl
├── plugins/
│   └── enrich.py
└── tests/
    └── test_workflows.sapl
```

* Keep reusable code inside packages under `packages/`.
* Place standalone workflows under `scripts/`.
* Ship plugins alongside the project to provide custom behaviour.
* Mirror Python packaging conventions when distributing SAPL libraries.

## Linting and Testing

* Run `python -m sapl lint scripts/main.sapl` before executing or compiling to catch warnings early.
* Use the new `sapl-test` runner to validate behavioural contracts:
  ```bash
  python -m sapl test tests/
  ```
* Integrate linting and tests into CI workflows to prevent regressions.

## Documentation Strategy

* Document complex modules using docstrings at the top of each SAPL file.
* Link to the markdown guides in the `docs/` directory from your README so teams can reference detailed workflows.
* Capture operational knowledge inside `NOTE` blocks within tasks for runbook-friendly output.

## Plugin Management

* Use `sapl.plugins.load_plugins_from_directory` to dynamically register plugins stored alongside your project.
* Each plugin should expose a `register(interpreter)` function and call `interpreter.register_builtin` to add utilities.
* Track plugin provenance with version strings or metadata stored in the plugin module to aid auditing.

## Dependency Hygiene

* Keep `sapl-required.yaml` lean and review transitive dependencies periodically.
* Pin critical versions to avoid unexpected runtime changes.
* Provide installation scripts (`setup.ps1`, `setup.sh`) that wrap the instructions from `docs/INSTALLATION.md`.

## Code Review Checklist

* Does the change include corresponding tests (`sapl-test` or Python unit tests)?
* Are new modules added to `sapl/` accompanied by documentation?
* Have runtime backends been considered (machine code, bytecode, transpiled Python)?
* Is plugin registration idempotent to avoid duplicate built-ins during repeated runs?

Following these practices keeps SAPL projects resilient and easier to onboard new contributors.
