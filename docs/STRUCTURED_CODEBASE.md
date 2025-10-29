# Structured Codebase Walkthrough

This guide highlights how to combine modules, plugins, the advanced compiler,
and the website manager into a cohesive project suitable for blue, red, and
purple team collaboration.

## Layout Overview

```
project/
├── sapl_ops/
│   ├── __init__.sapl
│   ├── entities.sapl
│   ├── reports.sapl
│   └── teams/
│       ├── __init__.sapl
│       ├── blue.sapl
│       ├── red.sapl
│       └── purple.sapl
├── pipelines/
│   ├── recon.sapl
│   ├── detection.sapl
│   └── response.sapl
├── plugins/
│   └── enrichment.sapl
├── required.yaml
└── website/
    └── ...
```

## Key Practices

* Separate reusable modules (`sapl_ops`) from workflow pipelines so teams can
  import only what they need.
* Capture shared constants (targets, credentials, schedule windows) in
  `__init__.sapl` modules.
* Use dedicated directories for blue, red, and purple team utilities—inheritance
  enables polymorphic task definitions that share logging infrastructure.

## Automation Tooling

* `sapl compile` with the advanced compiler exports machine code, bytecode, or
  polyglot sources for integration with other toolchains.
* `sapl server` hosts website assets for documentation and operator dashboards.
* `sapl test` validates unit tests located in the project tree, including async
  workflows and plugin-driven assertions.

## Dependency Management

* `required.yaml` declares Python packages and plugin entry points.
* `sapl environment` provisions a virtual environment with cross-platform
  compatibility for Linux, macOS, and Windows operators.

## Further Reading

* `docs/MODULES_AND_PACKAGES.md` for import mechanics.
* `docs/PLUGINS.md` for extending the runtime.
* `docs/GUI_AND_CLI_COMPILATION.md` for delivery patterns covering GUI and CLI
  deployments.
* `docs/SAPL_CLI.md`, `docs/SAPL_SERVER.md`, and `docs/SAPL_WEBSITE.md` for
  end-to-end tooling orchestration.
* `docs/SAPL_ENVIRONMENTS.md` for environment automation linked to
  `required.yaml` profiles.
