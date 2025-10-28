# Modules, Packages, and Structured Codebases

Large engagements benefit from reusable components. SAPL makes it easy to split
logic into modules, import Python packages, and share reusable libraries.

## Importing Modules

* `IMPORT module` loads either Python modules, SAPL packages, or plugin-supplied
  helpers registered with the runtime.
* `FROM package IMPORT name` mirrors Python syntax for selective imports.
* The module loader respects `sapl/required.yaml`, automatically provisioning
  dependencies and virtual environments through `sapl environment`.

## Creating Custom Packages

* Place `.sapl` files inside a directory with an `__init__.sapl` to declare a
  package. Modules can export functions, classes, and constants via `EXPORT` or
  by returning values from top-level `SET` statements.
* Use the structured project template in `examples/structured_project` as a
  reference for organising blue, red, and purple team assets.

## Built-in Modules and Plugins

* Standard library modules surface curated Python packages such as `asyncio`,
  `pathlib`, `ipaddress`, and regex helpers.
* Plugins discovered via `--plugin` or `--plugin-dir` can contribute additional
  modules, inject CLI commands, and participate in the testing harness.

## Compilation and Distribution

* The advanced compiler emits Python, C, C++, C#, Go, Rust, Java, JavaScript,
  PHP, SQL, Ruby, R, Perl, HTML, CSS, and assembly outputs. Use `sapl compile`
  with `--target` to select the language or machine backend.
* `sapl package build` (documented in the packaging guide) bundles modules,
  plugins, and website assets for distribution across Linux, macOS, and Windows.

## Virtual Environments

* `sapl environment create` provisions an isolated workspace using
  `sapl/required.yaml`.
* Integrate the environment into CI pipelines or local development for
  consistent dependency management.

Read `docs/STRUCTURED_CODEBASE.md` for a walkthrough of a full-featured project
that mixes CLI, server, and plugin components.
