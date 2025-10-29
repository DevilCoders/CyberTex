# Runtime Semantics and Memory Model

Understanding the SAPL runtime is crucial for building reliable automation. This reference explains how programs flow through the interpreter, how memory is represented, and how concurrency primitives are coordinated.

## Execution Overview

1. **Lexing & Parsing**: Source code is tokenised and parsed into the `nodes.Program` AST. Structural docstrings are lifted out of suites to simplify downstream processing.
2. **Interpreter Bootstrapping**: The interpreter constructs an `ExecutionContext`, loads builtins (including functional utilities, IO helpers, and exception factories), and applies registered plugins.
3. **Statement Dispatch**: Each top-level statement is evaluated in order, mutating the context or scheduling actions.

## Memory Model

- **Global Frame**: `context.variables` stores module-level bindings. Destructuring assignments and augmented assignments operate here unless inside a function or class body.
- **Frame Stack**: `context.frames` models lexical scoping. New frames are pushed for function calls, context managers, and loop scopes.
- **Task Stack**: `context._task_stack` tracks nested `TASK` execution, ensuring actions are attributed to the correct task when recorded.
- **Embedded Asset Registry**: `context.embedded_assets` stores `EMBED` statements with normalised language labels, metadata, and content. Each entry is mirrored in `ExecutionResult.embedded_assets` and surfaced to the shell/CLI for packaging. Unsupported language identifiers raise a runtime error before execution proceeds.

Mutable objects (lists, dictionaries, sets) are stored by reference, mirroring Python semantics. The shell and inspector render them using JSON-friendly projections to avoid exposing unserialisable callables.

## Control Flow Signals

The interpreter uses sentinel exceptions to model `BREAK`, `CONTINUE`, and `RETURN`. Each signal is intercepted by the nearest enclosing loop or function boundary.

## Async Coordination

- `ASYNC DEF` functions register coroutine factories.
- `AWAIT` expressions delegate to `asyncio` under the hood, allowing SAPL programs to orchestrate asynchronous reconnaissance tasks.
- The runtime ensures awaited values propagate correctly through the memory snapshot returned in `ExecutionResult`.

## Builtin IO Hooks

`INPUT` and `OUTPUT` statements resolve to Python's `input` and `print` functions by default. In tests or non-interactive contexts, replace them via `interpreter.context.builtins`.

## Plugin Lifecycle

Plugins receive the interpreter instance and may register additional builtins, import modules, or mutate the execution context. The shell replays plugin registration whenever state is reset to keep behaviours consistent.

For further exploration of extension points, consult [PLUGIN_ARCHITECTURE.md](PLUGIN_ARCHITECTURE.md).
