# SAPL Advanced Website

The SAPL website stack delivers rich operational dashboards, documentation
portals, and customer-facing control centers. It complements the CLI and server
by providing a polished interface for collaboration and reporting.

## Architecture Overview

- **Static site generator** – renders Markdown documentation, test reports, and
  data sheets using the same templates across teams.
- **Interactive widgets** – embed live charts, timeline replays, and code
  editors powered by the SAPL runtime sandbox.
- **Role-aware navigation** – tailor menus and content blocks for blue, red, and
  purple-team personas without duplicating markup.

## Building the Site

```bash
sapl website build --source website/ --output dist/site
```

- Markdown files in `website/docs` are transformed into responsive pages.
- Playbook examples from `examples/` are executed, and their outputs are
  attached automatically.
- Use `--theme` to swap between dark, light, and high-contrast palettes.

## Local Preview

```bash
sapl website serve --open --port 4100
```

The preview server supports hot reload, inline linting, and accessibility
checks. Pair it with `sapl server --proxy` to tunnel authenticated APIs during
demos.

## Customization

- **Layouts:** Override templates in `website/templates` to integrate brand
  guidelines or embed additional telemetry.
- **Plugins:** Register render hooks in `plugins/website` to pull data from SIEM
  platforms, ticketing systems, or honeypots.
- **Search:** Enable `--search lunr` for fully client-side indexing or
  `--search elastic` to connect to an Elasticsearch cluster.

## Deployment

1. Build the site for each target OS profile to include platform-specific
   guidance.
2. Push the `dist/site` directory to a CDN, GitHub Pages, or the built-in SAPL
   server.
3. Automate rebuilds from CI after each merge to keep documentation current.

## Integration with Tooling

- Publish `sapl-test` reports directly under `/quality` for quick access.
- Host API references generated from the advanced compiler's symbol tables.
- Embed interactive REPLs backed by the interpreter for training workshops.

For details on hosting, refer to [SAPL_SERVER.md](SAPL_SERVER.md). Combine the
website with the packaging and distribution strategies outlined in
[PACKAGING.md](PACKAGING.md) to deliver a cohesive product.
