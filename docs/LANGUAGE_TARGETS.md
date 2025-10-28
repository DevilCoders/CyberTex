# Polyglot Compilation Targets

The `sapl` CLI now understands additional compilation targets so that the same
SAPL source can be rendered as pseudo assembly, C, C++, C#, PHP, SQL, Go, Java,
JavaScript, Perl, Rust, Ruby, or R listings.

## Command Line Usage

Use the `compile` subcommand with the `--target` flag to select the desired
output language.

```bash
sapl compile examples/language_targets.sapl --target assembly
sapl compile examples/language_targets.sapl --target c
sapl compile examples/language_targets.sapl --target cpp
sapl compile examples/language_targets.sapl --target csharp
sapl compile examples/language_targets.sapl --target php
sapl compile examples/language_targets.sapl --target sql
sapl compile examples/language_targets.sapl --target go
sapl compile examples/language_targets.sapl --target java
sapl compile examples/language_targets.sapl --target javascript
sapl compile examples/language_targets.sapl --target perl
sapl compile examples/language_targets.sapl --target rust
sapl compile examples/language_targets.sapl --target ruby
sapl compile examples/language_targets.sapl --target r
```

Each target prints the generated listing to standard output, making it trivial
to redirect the content into version-controlled artefacts or feed it into
language-specific toolchains for further experimentation.

## Target Overview

- **PHP (`php`)** – emits idiomatic function wrappers and foreach loops for
  security teams that need to share reconnaissance logic with PHP-based stacks.
- **SQL (`sql`)** – serialises statements into stored procedure style scripts
  with annotated control-flow, ideal for data teams reviewing payload logic.
- **Go (`go`)** – produces `package main` scaffolding and range-based loops for
  teams embedding SAPL-derived flows into Go services.
- **Java (`java`)** – wraps functions inside a `SaplProgram` class and exposes
  a static `main` method suitable for JVM-based validation pipelines.
- **JavaScript (`javascript`)** – outputs `function` declarations and `for..of`
  loops for browser or Node.js automation flows.
- **Perl (`perl`)** – delivers `sub main` entries with pragma headers ready for
  quick prototyping in legacy scripting environments.
- **Rust (`rust`)** – composes `fn main()` scaffolding and `let mut` bindings so
  that systems programmers can reason about variable lifetimes.
- **Ruby (`ruby`)** – generates `def`/`end` blocks for sharing workflows across
  Ruby-centric operations teams.
- **R (`r`)** – emits `function()` definitions and `return()` statements for
  analysts integrating SAPL logic into statistical notebooks.

## Advanced Compiler Integration

The `advanced-compile` command and the Python `AdvancedCompiler` API accept the
same targets. When compiling through the advanced interface the payload contains
the generated source, and the metadata still records functions, classes, payloads,
and tasks discovered in the original SAPL program.

```python
from sapl.advanced_compiler import AdvancedCompiler

compiler = AdvancedCompiler()
artifact = compiler.compile_path(Path("examples/language_targets.sapl"), target="csharp")
print(artifact.metadata["functions"])
print(artifact.payload)
```

The pseudo code produced by these emitters favours readability and traceability,
showing how SAPL constructs map to familiar control-flow and function patterns in
popular systems languages. Use the outputs as hand-off documentation, to seed
further manual translations, or to reason about how SAPL flows behave on other
platforms.
