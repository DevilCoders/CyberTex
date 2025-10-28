# Testing With `sapl-test`

`sapl-test` is a lightweight runner for executing SAPL-based test suites. It discovers functions whose names start with `test_` and reports pass/fail status along with execution time.

## Writing Tests

Create a file such as `tests/test_workflows.sapl`:

```sapl
DEF test_payload_generation():
    SET payloads = build_payloads()
    RETURN len(payloads) > 3

DEF test_enrichment_pipeline():
    SET result = enrich_ip("10.0.0.1")
    RETURN result["source"] == "demo"
```

## Running Tests

```bash
python -m sapl test tests/
```

Use `--json` to emit machine-readable output:

```bash
python -m sapl test tests/ --json > reports/test-results.json
```

## Plugins and Fixtures

Pass plugins to the test runner when suites depend on plugin-provided built-ins:

```bash
python -m sapl test tests/ --plugin plugins.ip_enrich
```

Plugins are invoked for each interpreter instance, ensuring isolation between test files.

## Skipped Tests

If a test file defines no `test_` functions, the runner records a skipped outcome to highlight missing coverage.

## Integrating With CI

* Add `python -m sapl test tests/` to your CI pipeline before compilation or deployment steps.
* Treat a non-zero exit code as a failure; the command exits with status `1` when any test fails or when no files are discovered.
* Archive JSON output to integrate with dashboards or coverage tooling.
