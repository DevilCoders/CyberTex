# Exception Handling and Reliability

Robust automation requires defensive error handling. SAPL mirrors Python's
structured exception semantics while adding tooling for security operations.

## Language Constructs

* `TRY` / `EXCEPT` / `FINALLY` blocks work exactly like Python. Multiple
  `EXCEPT` clauses, bare `EXCEPT`, and `ELSE` blocks are available.
* `RAISE` rethrows the current exception or raises a custom error instance
  created via `CLASS`.
* Custom exceptions can inherit from `Error`, `RuntimeError`, or any Python
  exception exposed through imports.
* Combine `TRY`/`FINALLY` to guarantee resource cleanup when working with files,
  sockets, or temporary environments.
* Exception hierarchies mirror Python's semantics, letting you trap broad
  categories while still raising team-specific subclasses.

## Runtime Helpers

* The extended standard library exposes helpers such as `guard`, `retry`, and
  `capture_exception` to wrap risky calls.
* `sapl.testing` integrates exception assertions for both synchronous and async
  playbooks.
* Use `with suppress_errors(ErrorType):` to intentionally swallow known-safe
  failures during exploratory operations.

## Reporting Failures

* Use `NOTE` or `FINDING` inside `EXCEPT` blocks to document the impact and
  mitigation of observed failures.
* The advanced compiler can emit structured traces for Python, Rust, Go, and C
  targets, ensuring downstream tooling receives the same reliability insights.
* Emit metrics (`METRIC failure_count += 1`) inside handlers to feed dashboards
  on the SAPL website.

## Example

See `examples/control_flow_showcase.sapl` for a demonstration combining
exception handling, flow control, and logging across blue, red, and purple team
scenarios.
