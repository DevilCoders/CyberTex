# IDE Integration

Optimise the SAPL development experience by configuring your editor or IDE to understand the language and tooling.

## Syntax Highlighting

* Use the ANSI highlighter via `sapl highlight script.sapl --theme dark` to preview colouring.
* For editors that support TextMate grammars, adapt the token list from `sapl/lexer.py` to build custom syntax definitions.

## Linting On Save

* Configure your editor to run `sapl lint <file>` on save and surface diagnostics in the editor gutter.
* Many editors (VS Code, JetBrains IDEs) support problem matchers; capture lines formatted by the linter to display inline errors.

## Running Tests

* Register a task that invokes `sapl-test tests/`.
* Capture JSON output (`--format json`) to integrate with IDE test explorers.

## Debugging

* Transpile SAPL to Python (`sapl compile --target python`) and leverage your IDE's Python debugger to step through logic.
* Alternatively, wrap suspect sections in additional `NOTE` statements or plugin-based logging to inspect runtime state.

## Auto-Completion

* Export Python stubs for standard library helpers by introspecting `sapl.stdlib.extended.EXTRA_FUNCTIONS` and generating `.pyi` files.
* Register plugin-provided built-ins in stubs so IDEs can suggest names and types.

## Recommended Extensions

* **VS Code** – configure tasks for linting and testing, and install the *Better TOML* or *YAML* extensions for editing `required.yaml`.
* **PyCharm/IntelliJ** – add a Python run configuration for `sapl.cli.main` and enable *File Watchers* to run linting on file changes.
