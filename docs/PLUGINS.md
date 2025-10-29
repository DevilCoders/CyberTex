# Plugin Development

SAPL plugins let you extend the interpreter with custom built-ins, analytics, or tooling integrations. Plugins are regular Python modules stored with the `.sapl` suffix and expose a `register(interpreter)` function.

## Creating a Plugin

```python
# plugins/ip_enrich.sapl

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
sapl run scripts/enrichment.sapl --plugin plugins.ip_enrich
```

## Directory-Based Discovery

Place plugins inside a directory and use `--plugin-dir` or `sapl.plugins.load_plugins_from_directory`:

```bash
sapl run scripts/enrichment.sapl --plugin-dir plugins/
```

The loader exclusively targets `*.sapl` modules—legacy `.py` plugins are no longer
discovered now that the runtime, stdlib, and examples ship entirely with the
SAPL suffix. Every plugin must therefore be authored and stored with the
`.sapl` extension and expose the usual `register` entry point.

Declare optional `setup(interpreter)` and `teardown(interpreter)` hooks to
prepare resources or release them after execution. The CLI automatically calls
these when plugins opt-in via attributes on the module.

## Plugin Responsibilities

* Call `interpreter.register_builtin(name, value)` to expose helpers to SAPL code.
* Optionally mutate `interpreter.context` to configure default targets, payloads, or notes.
* Record metadata (for example `PLUGIN_VERSION = "1.0.0"`) to aid troubleshooting.
* Register CLI commands via `interpreter.cli.add_command` and advanced compiler
  passes via `interpreter.compiler.register_pass` to integrate end-to-end.
* Ship documentation under `docs/plugins/<name>.md` so users know how to adopt
  the extension.

## Testing Plugins

* Write SAPL tests that exercise plugin-provided built-ins and run them with `sapl-test --plugin your.plugin tests/`.
* Use Python unit tests to verify the plugin registration logic—the `.sapl`
  suffix is handled automatically by the import hook so you can `import` the
  module like any regular package.
* Validate interoperability with the SAPL server and website by running the
  integration tests defined in `tests/plugins/`.

## Error Handling

If plugin loading fails, the CLI surfaces a `PluginError` describing the problem. Ensure exceptions are informative and fail-fast so users can diagnose missing dependencies quickly.

## Built-in Plugin Gallery

The distribution ships with reference plugins for logging, telemetry export,
and compilation. Explore `plugins/builtin/` for examples covering:

* **sapl.plugins.audit** – enforces policy compliance during builds.
* **sapl.plugins.recon** – exposes data sources frequently used by red teams.
* **sapl.plugins.ui** – bridges CLI workflows into the advanced website.

Use these as blueprints when crafting custom plugins for your environment.
