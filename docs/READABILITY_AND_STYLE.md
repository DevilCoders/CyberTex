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

## Helpful Tooling

* Run `sapl lint` for instant feedback on unused variables, missing docstrings,
  and stylistic issues.
* `sapl highlight` provides ANSI-highlighted output to review scripts in the
  terminal.
* The inspector (`sapl inspect`) prints AST nodes, runtime bindings, and
  docstring summaries to help with onboarding.

## Learning Resources

* `docs/CORE_SYNTAX_OVERVIEW.md` for a language summary.
* `docs/DATA_STRUCTURES.md` for collection handling tips.
* `docs/FUNCTIONS_AND_ASYNC.md` for reusable patterns.
* The example gallery under `examples/` shows idiomatic code ranging from IO
  helpers to polyglot compilation pipelines.
