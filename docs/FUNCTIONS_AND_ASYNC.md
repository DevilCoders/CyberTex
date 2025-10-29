# Functions, Parameters, and Asynchronous Workflows

SAPL embraces both synchronous and asynchronous styles so analysts can build
modular pipelines that interact with live infrastructure.

## Defining Functions

* Use `DEF` for synchronous functions. Default arguments, keyword-only
  parameters, and arbitrary `*args`/`**kwargs` mirrors Python behaviour.
* Functions support docstrings, multi-line `##` comments, and decorators exposed
  through the plugin or module system.
* Lambda expressions provide lightweight, inline functions with captured scope
  semantics.
* Group related helpers into modules or classes to maintain a structured
  codebase and encourage reuse across teams.

```sapl
DEF collect_indicators(source, *, limit=100, normalise=TRUE):
    """Fetch indicators and optionally normalise them."""
    data = SOURCE_PULL(source, limit=limit)
    RETURN NORMALISE(data) IF normalise ELSE data
```

## Parameters and Return Values

* Positional arguments are listed first, followed by `*`, `*args`, keyword-only
  arguments, and optional `**kwargs`.
* The runtime enforces arity checks, default evaluation, and destructuring of
  tuple arguments where needed.
* `RETURN` exits the current function. Omitting `RETURN` yields `NONE`.
* Typed parameters use Python-style annotations to assist tooling and IDEs:
  `DEF hash_payload(payload: BYTES) -> STR:`.
* Multiple assignment works with returns: `SET status, data = fetch()`.

## Functional Helpers

* Lambda expressions combine with higher-order utilities (`map`, `filter`,
  `reduce`) for data wrangling.
* Built-in functions (`len`, `sum`, `min`, `max`, `sorted`, `enumerate`,
  `zip`) operate on SAPL collections and integrate with list comprehensions.
* Use `partial` from the functional library to pre-configure parameter sets for
  reuse in pipelines.

## Asynchronous Functions

* `ASYNC DEF` declares a coroutine compatible with Python's asyncio loop.
* Use `AWAIT` to pause execution inside async functions, or inside synchronous
  contexts when the runtime manages the event loop.
* Async tasks integrate with `sapl.runtime.async_tools` to orchestrate parallel
  scans or enrichment jobs.
* Combine async generators with `ASYNC FOR` loops to stream intelligence feeds
  without blocking.

## Flow Control Helpers

* `sapl.testing` surfaces async-aware test runners so asynchronous playbooks can
  be validated via `sapl test`.
* `sapl.stdlib.extended` offers utilities like `gather_async`, `run_in_executor`,
  and `async_retry` for resilient workflows.
* Structured concurrency primitives (`sapl.async.TaskGroup`) ensure spawned
  tasks finish cleanly, mirroring Python's `asyncio.TaskGroup` API.

## Error Handling and Contracts

* Raise domain-specific exceptions from functions to communicate failures—see
  [EXCEPTION_HANDLING.md](EXCEPTION_HANDLING.md).
* Document preconditions, side effects, and return types in docstrings; the
  advanced compiler validates these contracts when `--analyze` is enabled.
* Guard external input with type conversion helpers to maintain predictable
  behaviour across operating systems.

## Practical Guidance

* Prefer small, documented functions for readability and linter friendliness.
* Use lambdas for filter and map operations in comprehensions; document complex
  logic via nearby `##` comments.
* Combine async IO with the advanced compiler to emit Python, Go, or Rust tasks
  while preserving concurrency semantics.
* Expose key workflows via CLI commands (see [SAPL_CLI.md](SAPL_CLI.md)) so
  teammates can invoke them consistently.

The examples `examples/async_patterns.sapl` and `examples/control_flow_showcase.sapl`
illustrate typical patterns for mixing synchronous and asynchronous code.
