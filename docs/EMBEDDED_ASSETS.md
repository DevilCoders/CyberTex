# Embedded Assets & Polyglot Bundles

SAPL scripts can now register language snippets, configuration fragments, and packaged
resources directly in the execution plan using the `EMBED` statement. Embedded assets keep
mission-critical payloads, UI templates, or client tooling alongside playbook logic while
remaining easy to read and easy to share across interpreters, the advanced compiler, and the
static website workflow.

## Quick start

```sapl
TARGET ["https://portal.internal"]

EMBED html landing = """
<h1>Welcome {target}</h1>
<p>Rendered for {len(targets)} assets</p>
""" USING {"path": "website/landing.html", "tags": ["ui", "demo"]}

TASK "Publish":
    NOTE "Landing content length: {len(embed_landing)}"
    NOTE "Metadata tags: {', '.join(embed_landing_meta['tags'])}"
```

* The first argument selects the language label, making it simple to organise HTML, CSS,
  SQL, shell, or compiled payloads.
* The content expression supports docstrings, triple quoted blocks, comprehensions, and
  string interpolation so code stays readable.
* Optional metadata describes packaging or deployment hints. Provide any dictionary and
  include structured data such as output paths, plugin names, or compilation switches.

## Syntax reference

```
EMBED <language> <name> = <expression> [USING <metadata>]
```

* `<language>` – identifier or string describing the embedded language. Common values
  include `html`, `css`, `javascript`, `sql`, `python`, `rust`, `asm`, or `config`.
* `<name>` – identifier used when looking up the asset inside execution results or when
  exporting through the CLI and website managers.
* `<expression>` – any expression resolving to `str` or `bytes`. Triple quoted strings are
  ideal for multi-line templates; helper functions, lambda results, or file reads work too.
* `USING <metadata>` – optional dictionary that travels with the asset. Use it to store
  target filenames, templating parameters, package manifests, or GUI/CLI build profiles.

## Runtime behaviour

* Embedded assets are recorded in `ExecutionResult.embedded_assets` with language, content,
  and metadata. The runtime also emits a structured `embed` action containing previews for
  traceability and auditing.
* `ExecutionContext.format_context()` exposes each asset as `embed_<name>`, making it
  trivial to feed previews into `NOTE`, `OUTPUT`, or logging helpers.
* The interactive shell lists new assets inside delta summaries, making exploratory scripting
  easy to follow.

## Toolchain integration

* `python -m sapl run --json` now includes the `embedded_assets` map alongside tasks,
  findings, and payloads. The advanced compiler exposes them in the JSON summary so
  downstream tooling can bundle resources or trigger custom build steps.
* `python -m sapl inspect` prints embedded assets with scope, metadata, and trimmed content
  previews. Use `--json` to consume the raw dictionary.
* `examples/embedding_demo.sapl` demonstrates combining the feature with GUI-ready HTML,
  CLI snippets, and metadata-driven paths. The website manager can consume the metadata to
  copy assets into export directories.

## Cross-platform packaging

Embedded assets simplify packaging for Linux, macOS, and Windows:

* Ship GUI templates, CLI wrappers, or plugin manifests without leaving the SAPL project.
* Include `required.yaml` references or virtual environment bootstrap scripts as embedded
  YAML strings, then materialise them in packaging hooks.
* Store blue team, red team, and purple team playbook snippets in dedicated languages while
  keeping a single structured codebase.

Use `EMBED` to keep your SAPL playbooks readable, richly documented, and ready for delivery
across interpreters, advanced compilers, and the SAPL website builder.
