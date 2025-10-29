# SAPL Environments and `required.yaml`

SAPL projects capture dependencies, runtime policies, and tooling requirements
in a declarative `required.yaml`. Combined with managed virtual environments,
this keeps development, testing, and deployment consistent across operating
systems.

## Declaring Requirements

```yaml
runtime:
  version: ">=1.6"
  features:
    - async
    - websockets
packages:
  sapl-security: ^3.2
  requests: ^2.31
  pywin32: optional
plugins:
  - plugins.compiler.inline_payloads
profiles:
  blue:
    packages:
      splunk-sdk: ^1.7
  red:
    packages:
      cobalt-toolkit: ^2.4
```

- The `runtime` section pins interpreter capabilities and feature flags.
- `packages` mixes SAPL modules, Python wheels, and OS-specific extras.
- Profiles allow role-based overrides, so each team pulls only what they need.

## Managing Virtual Environments

```bash
sapl env create        # creates .sapl-env using the current interpreter
sapl env activate      # activates the environment for the shell
sapl env sync --all    # installs base packages and active profile additions
sapl env prune         # removes unused dependencies
```

Environments encapsulate dependencies for Linux, macOS, and Windows, keeping
path handling and compiled extensions isolated per host. Use `--python` to point
at custom interpreters when embedding SAPL within other languages.

## Continuous Integration

Add the following snippet to CI pipelines to guarantee reproducibility:

```bash
sapl env create --path .ci-env
sapl env sync --profile $TEAM
sapl-test --format junit.xml
sapl compile mission.sapl --profile $TEAM
```

## Troubleshooting

- **Missing system libraries:** Document required OS packages in
  `docs/INSTALLATION.md` and link them from `required.yaml` using the `notes`
  field.
- **Conflicting versions:** Run `sapl env resolve --explain` to inspect the
  dependency graph and suggested upgrades or downgrades.
- **Offline mirrors:** Configure `--index-url` or set `SAPL_INDEX_URL` to pull
  from disconnected artifact repositories.

## Best Practices

- Commit `required.yaml` and lockfiles to version control.
- Create separate profiles for development, staging, and production to avoid
  shipping experimental dependencies.
- Document environment workflows alongside onboarding materials so newcomers can
  bootstrap quickly.
