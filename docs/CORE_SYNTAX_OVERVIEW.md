# Core Syntax Overview

This guide summarises the core SAPL constructs so newcomers can read and write
playbooks with confidence. The language keeps Python-inspired readability with
indentation-based blocks, significant newlines, and expressive statements aimed
at security workflows. Every example intentionally mirrors Pythonic phrasing so
teams can transition with minimal friction.

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
* Primitive variables include integers, floats, booleans, and strings. Literals
  follow Python syntax (`TRUE`, `FALSE`, quoted strings, numeric underscores).
* Collection literals span lists (`[1, 2, 3]`), tuples (`(1, 2)`), dictionaries
  (`{"key": "value"}`), and sets (`{1, 2, 3}`).
* `IMPORT` and `FROM … IMPORT` expose Python modules, SAPL packages, and
  project-local `.sapl` modules.

## Expressions and Operators

* Numeric, string, boolean, and collection literals follow Python syntax.
* Operators include arithmetic (`+`, `-`, `*`, `/`, `//`, `%`, `**`), logical
  (`AND`, `OR`, `NOT`), comparisons, membership checks (`IN`), and identity
  (`IS`, `IS NOT`). Bitwise operators are available for low-level tooling.
* Conditional expressions (`a IF cond ELSE b`), list/dict/set comprehensions,
  and generator expressions provide succinct data transformations for reporting
  and enrichment.
* Type conversion helpers mirror Python (`INT()`, `FLOAT()`, `STR()`, `BOOL()`,
  `LIST()`, `DICT()`), making it easy to normalise external data sources.

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
* Pattern-based `MATCH` statements evaluate structural conditions without
  nested `IF` blocks, improving readability.

## Comments and Documentation

* Single-line comments begin with `#` and extend to the newline.
* Block comments use `##` on their own line to start and finish a two-or-more
  line comment block, perfect for temporary notes.
* String literals at the beginning of modules, tasks, functions, and classes act
  as documentation strings and are surfaced through the linter and inspector.
* Inline TODOs can be tagged with `# TODO(team|date)` to integrate with
  maintainability dashboards described in [MAINTAINABILITY.md](MAINTAINABILITY.md).

## Example Walkthrough

```sapl
"""Demonstrate variables, loops, and flow control."""

SET counter, limit = 0, 5

FOR value IN RANGE(limit):
    PRINT(f"Iteration {value}")
    IF value IS 2:
        CONTINUE
    IF value > 3:
        BREAK
    counter += value

RESULT = counter IF counter > 0 ELSE NONE
```

This snippet highlights multiple assignment, formatted strings, `FOR` loops,
conditional logic, and the ternary expression form. The flow mirrors Python,
so security teams can focus on mission logic rather than syntax hurdles.

Refer to the accompanying guides for deeper dives into specific subsystems such
as IO, exceptions, async patterns, and module packaging.
