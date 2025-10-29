# Full-Stack Website Workflows

SAPL's security web builders now extend beyond individual components into
complete full-stack experiences. The enhanced `FullStackApp` builder records
frontend modules, backend services, and automation pipelines so you can
materialise an executable bundle or spin up a preview server directly from a
`.sapl` blueprint.

## Building a blueprint

Start by describing the frontends, APIs, and deployment gates that make up the
application. The new `add_frontend`, `add_backend`, and `add_automation` helpers
accept other builders—such as `WebApp`, `Component`, `WebAPI`, and
`SecureDeployment`—and attach their structured configuration to the
`FullStackApp`.

```sapl
SET portal = (
    FullStackApp("cyber-operations-portal")
    .summary("Security-first frontends, APIs, and automation pipelines")
    .frontend("reactive-threat-board")
    .backend("real-time-api")
    .authentication("fido2-mfa")
    .database("postgresql-encrypted")
)

SET login_form = (
    Component("OpsLoginForm")
    .state(username="", password="", token="")
    .security(rate_limiting="5 attempts per minute", csrf_protection=True)
)

SET operations_dashboard = (
    WebApp("operations-hub")
    .frontend("react-like-components")
    .backend("async-api-gateway")
    .authentication("mfa-required")
)
operations_dashboard.register_component(login_form)

portal.add_frontend(operations_dashboard)
portal.add_frontend(login_form)
```

Use `add_backend` and `add_automation` in the same way to connect APIs and
deployment pipelines to the blueprint.

## Scaffolding the project

`scaffold_fullstack_app` materialises the blueprint into a runnable directory
structure. The helper writes `.sapl` stubs for the frontend and backend,
generates a JSON summary for CI automation, and produces an HTML dashboard for
visual inspection.

```sapl
SET bundle = scaffold_fullstack_app(portal, "build/cyber_portal")
NOTE "Bundle created at {bundle['root']}"
NOTE "HTML preview available at {bundle['index']}"
```

When `destination` is omitted, the scaffolder creates a temporary directory and
returns its location in `bundle['root']`. The generated structure includes:

- `frontend/app.sapl` – task-oriented notes that mirror the recorded components.
- `frontend/index.html` – a rendered dashboard of frontend, backend, and
  automation modules.
- `backend/service.sapl` – orchestration notes covering API services and
  middleware.
- `docs/README.md` – regeneration guidance for collaborators.
- `metadata.json` – the machine-readable summary of the blueprint.

## Previewing the website

`preview_fullstack_app` wraps the scaffolder and creates an `SAPLServer` pointing
at the generated frontend directory. Pass `start_preview=True` to launch the
HTTP server immediately or call `.start()` on the returned server object when
ready.

```sapl
SET preview = preview_fullstack_app(
    portal,
    destination="build/cyber_portal_preview",
    port=0,
    start_preview=True,
)
NOTE "Preview running at {preview['server'].server_address}"
```

Stop the preview with `preview['server'].stop()` when finished. The helper uses
port `0` by default so the operating system chooses an available socket, making
it safe to run in automated pipelines.

## Complete example

`examples/fullstack_site_preview.sapl` combines the blueprint, scaffolding, and
preview workflow into a single script. Execute it with:

```bash
python -m sapl run examples/fullstack_site_preview.sapl
```

The script generates a build directory under `build/`, prints a formatted JSON
summary, and exposes the front-end preview directory so you can launch the
server immediately or hand the bundle to another tool.
