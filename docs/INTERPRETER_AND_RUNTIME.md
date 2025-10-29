# Interpreter and Runtime

The SAPL interpreter combines a lightweight virtual machine with rich runtime
services, offering the familiarity of Python's REPL while catering to
security-focused workflows.

## Launching the Interpreter

```bash
sapl repl
sapl run script.sapl
```

- The REPL supports syntax highlighting, auto-completion, and inline
  documentation strings.
- Use `:load module.sapl` to pull code into the session, or `:save` to capture
  the current buffer as a reusable module.

## Input and Output

- `INPUT("Prompt")` reads from stdin, returning strings. Wrap with `INT()` or
  `BOOL()` for type conversion.
- `PRINT(value, *, style="info")` renders formatted output with optional color
  channels suitable for CLI dashboards.
- `LOG.info("message")` integrates with the runtime's structured logging, making
  telemetry available to the advanced website and SIEM exports.

## Runtime Services

- **Task Scheduler:** Coordinates synchronous and asynchronous functions,
  ensuring `AWAIT` works seamlessly with timers, network sockets, and file I/O.
- **Data Pipelines:** Built-in connectors stream data to/from JSON, CSV, SQL,
  and message queues.
- **Sandboxing:** The interpreter enforces capability-based restrictions derived
  from `required.yaml`, preventing unauthorized network or filesystem access.

## Embedding SAPL

The runtime exposes a C-compatible API alongside Python, Go, Rust, and .NET
wrappers. Link against `libsapl` to embed SAPL scripts inside host applications.

```c
sapl_vm_t *vm = sapl_vm_new();
sapl_vm_load(vm, "payload.sapl");
sapl_vm_call(vm, "run", NULL);
sapl_vm_free(vm);
```

Refer to [POLYGLOT_LANGUAGES.md](POLYGLOT_LANGUAGES.md) for language-specific
examples.

## Debugging Sessions

- `sapl repl --trace` annotates each executed line with timing and memory stats.
- `BREAKPOINT()` functions similarly to Python's `breakpoint()`, pausing
  execution for inspection.
- `sapl inspect` (documented in [SAPL_CLI.md](SAPL_CLI.md)) reveals object
  hierarchies, method signatures, and documentation strings.

## Best Practices

- Keep scripts idempotent so they can be rerun safely during investigations.
- Document REPL commands inside module docstrings for future reference.
- Capture transcripts with `sapl repl --record session.log` when sharing
  findings across teams.
