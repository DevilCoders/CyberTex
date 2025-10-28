# Core Syntax Overview

This guide summarises the core SAPL constructs so newcomers can read and write
playbooks with confidence. The language keeps Python-inspired readability with
indentation-based blocks, significant newlines, and expressive statements aimed
at security workflows.

## Indentation and Layout

* Blocks are introduced by statements such as `TASK`, `FOR`, `IF`, `WHILE`,
  `DEF`, `ASYNC DEF`, and `CLASS` and continue for as long as the indentation is
  greater than the parent level.
* A newline terminates statements; trailing comments after a statement are
  supported via `#`, while multi-line context notes can use `##` and `##`
  delimiters.
* Tabs are expanded to four spaces internally, enabling mixed teams to keep a
  consistent look and feel.

## Top-Level Declarations

* `TARGET`, `SCOPE`, and `PAYLOAD` define context and reusable payload
  collections.
* `SET` introduces or reassigns variables. Multiple assignment is available via
  tuple unpacking, and destructuring works across lists, tuples, dictionaries,
  and sets.
* `IMPORT` and `FROM … IMPORT` expose Python modules, SAPL packages, and
  project-local `.sapl` modules.

## Expressions and Operators

* Numeric, string, boolean, and collection literals follow Python syntax.
* Operators include arithmetic (`+`, `-`, `*`, `/`, `//`, `%`, `**`), logical
  (`AND`, `OR`, `NOT`), comparisons, and membership checks (`IN`).
* Conditional expressions (`a IF cond ELSE b`) and comprehensions provide
  succinct data transformations for reporting and enrichment.

## Functions and Classes

* `DEF` declares synchronous functions with positional, keyword, variadic, and
  default parameters.
* `ASYNC DEF` exposes asynchronous coroutines that can leverage `AWAIT` and the
  event loop integration in the runtime.
* `CLASS` definitions support inheritance, encapsulation, and polymorphism. The
  runtime wires class bodies to constructors, methods, and attributes, exposing
  familiar `self` semantics.

## Flow Control

* `IF`/`ELIF`/`ELSE`, `WHILE`, and `FOR` implement branching and looping.
* `BREAK`, `CONTINUE`, and `PASS` mirror Python semantics for loop control.
* `RETURN` supports explicit return values in synchronous and asynchronous
  functions.

## Comments and Documentation

* Single-line comments begin with `#` and extend to the newline.
* Block comments use `##` on their own line to start and finish a two-or-more
  line comment block, perfect for temporary notes.
* String literals at the beginning of modules, tasks, functions, and classes act
  as documentation strings and are surfaced through the linter and inspector.

Refer to the accompanying guides for deeper dives into specific subsystems such
as IO, exceptions, async patterns, and module packaging.
