# Plugin Architecture

SAPL plugins are Python callables that receive an `Interpreter` instance. This document explains lifecycle hooks, packaging strategies, and testing approaches.

## Registration Flow

1. The CLI resolves plugin specifications provided via `--plugin` and `--plugin-dir`.
2. Each plugin is imported and executed with the interpreter instance.
3. Plugins may register new builtins, monkey-patch the module loader, or enqueue actions.
4. The interpreter records plugin identifiers for inspection (`interpreter.active_plugins`).

## Recommended Structure

```python
# plugins/reporting.py
def register(interpreter):
    interpreter.register_builtin("notify", lambda message: print(f"[notify] {message}"))
    register.__sapl_plugin_name__ = "reporting"
```

Bundle plugins inside packages with explicit entry points. When distributing to collaborators, publish them on an internal index and add the package to `sapl-required.yaml` so virtual environments include the dependency automatically.

## Plugin Safety Tips

- Avoid blocking IO operations; prefer async functions and `AWAIT` inside SAPL code.
- Namespaces should be unique to prevent collisions with builtins and other plugins.
- Use the inspector to validate structural changes triggered by plugin augmentation.

## Testing Plugins

Leverage the `sapl test` runner to exercise plugin-driven scripts:

```bash
sapl test tests/plugins --plugin company.plugins:register
```

The new `sapl shell` command can also bootstrap plugins non-interactively:

```bash
sapl shell --plugin company.plugins:register --execute "NOTE \"Plugin ready\""
```

For an end-to-end example, see `examples/plugins/enrichment.sapl` and `examples/plugins/ip_enricher.py`.
