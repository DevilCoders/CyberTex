# Creating Packages and Libraries

SAPL supports modular code through packages (`__init__.sapl`) and modules (`module.sapl`). This guide explains how to structure, distribute, and consume reusable components.

## Package Structure

```
packages/
└── cyber_ops/
    ├── __init__.sapl
    ├── recon.sapl
    ├── exploitation.sapl
    └── reporting.sapl
```

* `__init__.sapl` should expose the package API by importing or defining the objects you want consumers to use.
* Nested directories can include their own `__init__.sapl` to create subpackages.

## Exporting Symbols

Inside `__init__.sapl`, re-export helper functions or classes:

```sapl
IMPORT cyber_ops.recon
IMPORT cyber_ops.reporting

DEF load():
    RETURN recon.DEFAULT_PROFILES
```

Consumers can then use:

```sapl
IMPORT cyber_ops AS ops
SET profiles = ops.load()
```

## Distributing Packages

1. Commit the package under version control alongside `required.yaml`.
2. Document usage in `docs/PACKAGING.md` or your project README.
3. Optionally provide a `setup.py` or `pyproject.toml` if shipping mixed Python/SAPL projects.
4. Use tags/releases to distribute stable versions for internal consumers.
5. Publish to internal artifact repositories via `sapl package publish --index
   https://sapl.example.local`. Consumers can then list available versions with
   `sapl package search`.

## Local Module Loading

SAPL's module loader resolves packages relative to the executing script. Organise projects as:

```
project/
├── packages/
│   └── cyber_ops/
├── scripts/
│   └── engagement.sapl
└── required.yaml
```

Then execute scripts with:

```bash
sapl run scripts/engagement.sapl
```

The interpreter automatically adds the script directory to the search path, allowing `IMPORT cyber_ops` to succeed. Add extra
directories via the `paths` entry in `required.yaml` to share local libraries
without modifying `PYTHONPATH`.

## Publishing Libraries

For wider distribution:

* Bundle SAPL packages into a Python wheel alongside helper Python modules.
* Provide entry points that call `sapl.cli.main` with preconfigured arguments.
* Ship documentation covering installation, testing, and plugin usage.
* Generate SBOMs (`sapl package sbom`) to satisfy compliance teams.
* Include GUI and CLI compilation guides (see
  [GUI_AND_CLI_COMPILATION.md](GUI_AND_CLI_COMPILATION.md)) so consumers know how
  to emit launchers for their platforms.

With these practices, teams can develop rich SAPL libraries that mirror traditional software engineering workflows.
