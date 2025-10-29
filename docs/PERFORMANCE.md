# Performance Considerations

SAPL balances expressiveness with runtime performance. This guide outlines strategies for building responsive workflows and diagnosing bottlenecks.

## Interpreter Optimisations

* Prefer list comprehensions and built-in helpers (`map_list`, `filter_list`) for data-heavy tasks.
* Reuse compiled regex objects via `regex_compile` when matching repeatedly.
* Cache expensive lookups inside functions rather than recomputing at every call site.
* Leverage `sapl profile` to capture flame graphs directly from SAPL execution
  without transpiling to Python.

## Asynchronous Workflows

* Mark network-bound functions as `ASYNC DEF` and use `AWAIT` to parallelise work.
* The interpreter automatically runs async coroutines using `asyncio.run`, but you can integrate custom event loops inside plugins when needed.

## Profiling

* Use Python's `cProfile` to profile transpiled Python output when targeting CLI
  or GUI builds.
* For direct SAPL execution, wrap heavy sections in timing helpers registered by plugins:

```python
# plugins/profile.py
import time

def register(interpreter):
    def measure(name, func):
        start = time.perf_counter()
        result = func()
        return {"name": name, "duration": time.perf_counter() - start, "result": result}

    interpreter.register_builtin("profile_call", measure)
```

Inside SAPL:

```sapl
SET report = profile_call("fetch hosts", lambda: fetch_hosts())
NOTE "Fetch hosts took {report['duration']}s"
```

## Large Projects

* Break workflows into packages and import only the modules required for each script.
* Use the advanced compiler metadata to understand dependency graphs before deployment. `sapl compile --analyze` emits JSON
  reports summarising hotspots and slow imports.
* Configure caching paths in `required.yaml` to reuse bytecode across hosts.

## Testing For Performance

* Integrate `sapl-test` suites that validate response times (for example asserting a function returns within a threshold).
* Run performance-sensitive tests on representative hardware to capture realistic metrics.
* Track performance budgets in `docs/PERFORMANCE.md` and surface them on the
  SAPL website to keep teams aligned.
