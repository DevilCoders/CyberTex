# Language Target Field Guide

SAPL's polyglot toolchain now covers a broad spectrum of runtimes so playbooks
can be shared with partners who operate outside the Python ecosystem. The
sections below summarise what each emitter produces, the idioms it favours, and
the quickest way to obtain the output from the CLI.

## PHP

- **Command:** `sapl compile examples/language_targets.sapl --target php`
- **Highlights:** Generates `function sapl_main()` wrappers, `foreach`
  iterations, and `//` documentation comments that align with modern PHP
  tooling.
- **Use it when:** exchanging recon logic with web teams maintaining PHP
  application firewalls or CMS extensions.

## SQL

- **Command:** `sapl compile examples/language_targets.sapl --target sql`
- **Highlights:** Emits `BEGIN; ... COMMIT;` blocks, `SET` assignments, and
  comment-traced control flow to seed stored procedures or analyst notebooks.
- **Use it when:** data teams want to stage payloads or findings as SQL scripts
  for warehouse validation.

## Go

- **Command:** `sapl compile examples/language_targets.sapl --target go`
- **Highlights:** Outputs a `package main` file with `func main()` and
  range-based loops ready for quick embedding inside Go-based automation.
- **Use it when:** shipping SAPL-driven logic into cross-platform services or
  agent tooling written in Go.

## Java

- **Command:** `sapl compile examples/language_targets.sapl --target java`
- **Highlights:** Wraps routines inside a `public class SaplProgram` with a
  static `main` method plus `var` bindings for concise translation.
- **Use it when:** collaborating with enterprise defenders who rely on JVM
  pipelines or static analysis gateways.

## JavaScript

- **Command:** `sapl compile examples/language_targets.sapl --target javascript`
- **Highlights:** Provides `function` declarations, `let` bindings, and
  `for..of` loops that slot into Node.js scripts or browser extension
  prototypes.
- **Use it when:** front-end engineers or automation testers need to replay SAPL
  workflows in their JavaScript-based harnesses.

## Perl

- **Command:** `sapl compile examples/language_targets.sapl --target perl`
- **Highlights:** Adds shebangs, strict/warnings pragmas, and `sub main`
  wrappers with `my` declarations to align with long-lived Perl tooling.
- **Use it when:** maintaining legacy automation that still powers portions of
  the blue-team infrastructure.

## Rust

- **Command:** `sapl compile examples/language_targets.sapl --target rust`
- **Highlights:** Builds `fn main()` entry points, `let mut` bindings, and
  `for` loops for systems programmers who expect Rust-like ergonomics.
- **Use it when:** modelling low-level tasks or experiments destined for Rust
  agents and CLI utilities.

## Ruby

- **Command:** `sapl compile examples/language_targets.sapl --target ruby`
- **Highlights:** Emits idiomatic `def`/`end` blocks, `return` statements, and
  descriptive comments so Rubyists can inspect and adapt SAPL flows.
- **Use it when:** collaborating with incident-response teams powered by Ruby
  scripts or Rails automation.

## R

- **Command:** `sapl compile examples/language_targets.sapl --target r`
- **Highlights:** Generates `function()` wrappers, `return()` calls, and `for`
  loops that integrate neatly with statistical notebooks or R-based analytics
  jobs.
- **Use it when:** data-science partners want to replay SAPL tasks inside R for
  reporting or modelling.

## Advanced Compiler Integration

All emitters listed above are supported by the `sapl advanced-compile` command
and the `AdvancedCompiler` Python API. Selecting one of the targets populates
`artifact.payload` with the generated source while preserving metadata about the
original SAPL structure. This makes it easy to audit functions, payloads, and
classes regardless of the chosen output language.
