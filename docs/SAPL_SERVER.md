# SAPL Server

The SAPL server mirrors the ergonomics of `python -m http.server` while adding
security and observability features tuned for cyber operations. Use it to host
compiled bundles, share generated intelligence, or expose interactive payload
controls to teammates.

## Quick Start

```bash
sapl server --bind 127.0.0.1 --port 8000 --root dist/
```

- `--bind` selects the listening interface. Use `0.0.0.0` when deploying inside
  a container or lab network.
- `--port` defaults to `8000`, mirroring the Python reference implementation.
- `--root` sets the directory to expose. It accepts compiled launchers, report
  archives, and documentation folders.

## TLS and Authentication

```bash
sapl server --bind 10.0.5.2 --port 8443 \
  --root releases/ \
  --tls-cert certs/server.pem --tls-key certs/server.key \
  --auth basic --users ops:$(openssl rand -hex 12)
```

- Enable TLS for red-team drops or sensitive coordination.
- `--auth` supports `basic`, `token`, and `mTLS` modes.
- Credentials can be loaded from environment variables, Vault secrets, or
  `required.yaml` profiles.

## Live Reload and Hot Swaps

The server monitors the `--root` directory for changes. When new bundles appear,
connected clients automatically receive updated manifests without restarting the
process. Pair this with the advanced compiler's incremental builds for rapid
iteration.

## Extensibility Hooks

- **Custom routes:** Implement `ServerExtension` classes in
  `plugins/server/*.sapl` to add API endpoints or web sockets.
- **Request filtering:** Attach middleware to inspect headers and enforce
  network segmentation policies.
- **Event streaming:** Expose `--event-bus` to forward access logs to SIEM
  tooling in real time.

## Deployment Patterns

1. **Ad-hoc sharing** – run the server locally during tabletop exercises to hand
   off payloads securely.
2. **Staging pipeline** – embed `sapl server --once` in CI to publish nightly
   builds and documentation snapshots.
3. **Forward-deployed implant control** – combine TLS, mutual authentication,
   and plugin-based routing for hardened operations.

Consult [SAPL_WEBSITE.md](SAPL_WEBSITE.md) for guidance on publishing full web
properties and dashboards through the same tooling.
