# Readability and Style Guide

The SAPL ecosystem emphasises clarity so teams can collaborate across red,
blue, and purple operations. This guide captures conventions that keep code
approachable for newcomers and experts alike.

## General Principles

* Prefer expressive names for variables, functions, and classes.
* Use docstrings to describe modules, tasks, and functions. The inspector and
  linter surface these descriptions automatically.
* Keep statements short—leverage helper functions and modules to encapsulate
  complex logic.
* Pair every complex branch with a quick comment explaining intent. Future you
  (or a teammate) should understand the why in seconds.
* Maintain consistent ordering: constants, configuration, functions, classes,
  then execution logic. This structure mirrors the onboarding flow described in
  [STRUCTURED_CODEBASE.md](STRUCTURED_CODEBASE.md).

## Comments

* Use `#` for brief notes beside statements.
* Multi-line commentary should use the `##` … `##` form so readers immediately
  see the scope of temporary instructions.
* Avoid commented-out code; instead, move experiments into dedicated examples or
  plugins.

## Layout

* Follow indentation-based structure with four spaces per level.
* Group related `SET` statements together and separate logical stages with blank
  lines.
* Align comprehension clauses and chained function calls for readability.
* Keep lines under 100 characters to avoid awkward wrapping in terminals and
  IDE preview panes.
* When wrapping function arguments, hang them beneath the opening parenthesis
  and include trailing commas to minimise diff noise.

## Helpful Tooling

* Run `sapl lint` for instant feedback on unused variables, missing docstrings,
  and stylistic issues.
* `sapl highlight` provides ANSI-highlighted output to review scripts in the
  terminal.
* The inspector (`sapl inspect`) prints AST nodes, runtime bindings, and
  docstring summaries to help with onboarding.
* IDE extensions (see [IDE_INTEGRATION.md](IDE_INTEGRATION.md)) supply
  auto-formatting, semantic tokens, and comment templates.
* `sapl fmt` harmonises spacing, comment layout, and docstring quoting.

## Learning Resources

* `docs/CORE_SYNTAX_OVERVIEW.md` for a language summary.
* `docs/DATA_STRUCTURES.md` for collection handling tips.
* `docs/FUNCTIONS_AND_ASYNC.md` for reusable patterns.
* The example gallery under `examples/` shows idiomatic code ranging from IO
  helpers to polyglot compilation pipelines.
* Browse `docs/MAINTAINABILITY.md` to align readability goals with long-term
  upkeep, including code review checklists and refactoring playbooks.
