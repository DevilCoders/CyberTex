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

## Parameters and Return Values

* Positional arguments are listed first, followed by `*`, `*args`, keyword-only
  arguments, and optional `**kwargs`.
* The runtime enforces arity checks, default evaluation, and destructuring of
  tuple arguments where needed.
* `RETURN` exits the current function. Omitting `RETURN` yields `NONE`.

## Asynchronous Functions

* `ASYNC DEF` declares a coroutine compatible with Python's asyncio loop.
* Use `AWAIT` to pause execution inside async functions, or inside synchronous
  contexts when the runtime manages the event loop.
* Async tasks integrate with `sapl.runtime.async_tools` to orchestrate parallel
  scans or enrichment jobs.

## Flow Control Helpers

* `sapl.testing` surfaces async-aware test runners so asynchronous playbooks can
  be validated via `sapl test`.
* `sapl.stdlib.extended` offers utilities like `gather_async`, `run_in_executor`,
  and `async_retry` for resilient workflows.

## Practical Guidance

* Prefer small, documented functions for readability and linter friendliness.
* Use lambdas for filter and map operations in comprehensions; document complex
  logic via nearby `##` comments.
* Combine async IO with the advanced compiler to emit Python, Go, or Rust tasks
  while preserving concurrency semantics.

The examples `examples/async_patterns.sapl` and `examples/control_flow_showcase.sapl`
illustrate typical patterns for mixing synchronous and asynchronous code.
