# Modules, Packages, and Structured Codebases

Large engagements benefit from reusable components. SAPL makes it easy to split
logic into modules, import Python packages, and share reusable libraries.

## Importing Modules

* `IMPORT module` loads either Python modules, SAPL packages, or plugin-supplied
  helpers registered with the runtime.
* `FROM package IMPORT name` mirrors Python syntax for selective imports.
* The module loader respects `required.yaml`, automatically provisioning
  dependencies and virtual environments through `sapl environment`.
* Relative imports (`FROM .submodule IMPORT helper`) keep intra-package
  references explicit, strengthening maintainability.
* When embedding third-party languages, shim modules expose consistent SAPL
  interfaces across HTML, CSS, SQL, and compiled targets.

## Creating Custom Packages

* Place `.sapl` files inside a directory with an `__init__.sapl` to declare a
  package. Modules can export functions, classes, and constants via `EXPORT` or
  by returning values from top-level `SET` statements.
* Use the structured project template in `examples/structured_project` as a
  reference for organising blue, red, and purple team assets.
* Document package responsibilities in `README.md` files inside each directory
  and add per-module docstrings for discoverability.
* Register packages in `required.yaml` under the `packages` key to ensure
  teammates receive them automatically. See
  [SAPL_ENVIRONMENTS.md](SAPL_ENVIRONMENTS.md) for details.

## Built-in Modules and Plugins

* Standard library modules surface curated Python packages such as `asyncio`,
  `pathlib`, `ipaddress`, and regex helpers.
* Plugins discovered via `--plugin` or `--plugin-dir` can contribute additional
  modules, inject CLI commands, and participate in the testing harness.
* Built-in modules are versioned alongside the interpreter; pin versions in
  `required.yaml` to guarantee cross-platform compatibility.
* Create custom modules by placing `.sapl` files in `sapl_modules/` and adding
  that directory to `SAPL_PATH` or the `paths` section of `required.yaml`.

## Compilation and Distribution

* The advanced compiler emits Python, C, C++, C#, Go, Rust, Java, JavaScript,
  PHP, SQL, Ruby, R, Perl, HTML, CSS, and assembly outputs. Use `sapl compile`
  with `--target` to select the language or machine backend.
* `sapl package build` (documented in the packaging guide) bundles modules,
  plugins, and website assets for distribution across Linux, macOS, and Windows.
* `sapl package publish` pushes bundles to internal indexes or artifact hubs.
  Pair it with `sapl server` or the advanced website for seamless delivery.

## Virtual Environments

* `sapl environment create` provisions an isolated workspace using
  `required.yaml`.
* Integrate the environment into CI pipelines or local development for
  consistent dependency management.
* The CLI honours per-package post-install hooks declared in `required.yaml`,
  letting you run migrations or compile native extensions after installation.

Read `docs/STRUCTURED_CODEBASE.md` for a walkthrough of a full-featured project
that mixes CLI, server, and plugin components.
