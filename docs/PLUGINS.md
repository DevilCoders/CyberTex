# Plugin Development

SAPL plugins let you extend the interpreter with custom built-ins, analytics, or tooling integrations. Plugins are regular Python modules that expose a `register(interpreter)` function.

## Creating a Plugin

```python
# plugins/ip_enrich.py

def register(interpreter):
    def enrich(ip):
        return {
            "ip": ip,
            "asn": "AS64500",
            "source": "demo",
        }

    interpreter.register_builtin("enrich_ip", enrich)
```

Load the plugin when running a script:

```bash
python -m sapl run scripts/enrichment.sapl --plugin plugins.ip_enrich
```

## Directory-Based Discovery

Place plugins inside a directory and use `--plugin-dir` or `sapl.plugins.load_plugins_from_directory`:

```bash
python -m sapl run scripts/enrichment.sapl --plugin-dir plugins/
```

The loader scans `*.py` files and invokes their `register` function.

## Plugin Responsibilities

* Call `interpreter.register_builtin(name, value)` to expose helpers to SAPL code.
* Optionally mutate `interpreter.context` to configure default targets, payloads, or notes.
* Record metadata (for example `PLUGIN_VERSION = "1.0.0"`) to aid troubleshooting.

## Testing Plugins

* Write SAPL tests that exercise plugin-provided built-ins and run them with `python -m sapl test --plugin your.plugin tests/`.
* Use Python unit tests to verify the plugin registration logic.

## Error Handling

If plugin loading fails, the CLI surfaces a `PluginError` describing the problem. Ensure exceptions are informative and fail-fast so users can diagnose missing dependencies quickly.
