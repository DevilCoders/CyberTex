# Compiling SAPL From Source

The SAPL toolchain ships with multiple backends, allowing you to compile scripts into machine listings, bytecode, or transpiled Python. This guide covers compilation workflows and platform-specific considerations.

## Prerequisites

* Python 3.11+
* The repository cloned locally (`git clone https://example.com/CyberTex.git`).
* Optional: a C/C++ toolchain for experimenting with the machine-code backend output.

## Quick Compilation

Compile a script into the default machine-code listing:

```bash
python -m sapl compile examples/basic.sapl
```

To emit bytecode or Python source:

```bash
python -m sapl compile examples/basic.sapl --target bytecode
python -m sapl compile examples/basic.sapl --target python
```

The advanced compiler provides metadata useful for build systems:

```bash
python -m sapl advanced-compile examples/basic.sapl --target python --json
```

## Building With Plugins

Plugins can extend the compiler pipeline—for example adding custom optimization passes. Pass one or more plugins using the CLI:

```bash
python -m sapl compile scripts/app.sapl --plugin my_plugins.optimizer
```

Plugins loaded during compilation can register additional built-ins or modify interpreter behaviour before bytecode generation.

## Continuous Integration

When compiling in CI:

1. Ensure the repository is checked out and dependencies installed (`pip install -r sapl/required.yaml`).
2. Run tests using `python -m sapl test` to validate the project before compilation.
3. Invoke the required compilation target, capturing the output artifact.
4. Archive generated files as CI artifacts for later deployment.

## Platform Notes

* **Linux/macOS** – Scripts run directly under Python; use `make` or shell scripts to automate compilation.
* **Windows** – Use PowerShell scripts or GitHub Actions workflows to drive `sapl` commands. Ensure the terminal supports UTF-8 for coloured diagnostics.

## Troubleshooting

* Ensure all imports resolve. The module loader searches relative to the script directory; packages must contain an `__init__.sapl` file.
* When compiling to Python, review the generated code to confirm any required Python dependencies are available at runtime.
* The machine-code backend emits a textual listing suitable for review; integrate with reverse-engineering or simulation tooling as required.
