# Workflow Playbooks

This guide shares opinionated workflows for combining SAPL tooling with real-world security research processes.

## Rapid Recon Prototyping

1. Start an interactive session: `sapl shell --script examples/basic.sapl`.
2. Use `:state` to inspect runtime variables such as payload libraries.
3. Iterate on new reconnaissance tasks, capturing them with `:run`.
4. Export the session delta using `--execute` snippets for reproducibility in CI.

## Automated Testing Loop

1. Author tests in `.sapl` files using the `sapl.testing` helpers.
2. Run `sapl test --json` to gather structured results.
3. Feed the JSON into dashboards or Slack notifications.
4. Pair with `sapl inspect` to ensure test suites define expected functions and payloads.

## Website Publication Pipeline

1. Run `sapl website --export ./public --overwrite` inside CI to generate the static site.
2. Publish the exported directory to an object store or CDN.
3. Use `sapl website --list` to verify asset integrity as part of smoke tests.
4. Deploy the SAPL HTTP server (`sapl website --serve`) for ad-hoc demos.

## Cross-Team Collaboration

- Commit curated documentation to `comprehensive_docs/` so teams share a consistent knowledge base.
- Use `sapl shell --script project.sapl --execute "OUTPUT \"Ready\""` in onboarding scripts to verify environment setup.
- Build custom plugins that enrich execution plans with ticket URLs or compliance references.

## Incident Response Readiness

Combine `sapl inspect` and `sapl run --json` to validate playbooks before and during incidents. Inspection ensures functions and payloads exist, while JSON execution output can be attached directly to case management systems.
