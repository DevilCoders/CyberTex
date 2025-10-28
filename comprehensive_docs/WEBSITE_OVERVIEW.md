# Advanced Website Overview

The SAPL advanced website is a static documentation portal designed for internal enablement. It complements the Markdown guides with a browsable interface.

## Directory Layout

```
website/
├── index.html
├── assets/
│   ├── styles.css
│   └── app.js
├── sections/
│   ├── cli.html
│   ├── plugins.html
│   └── workflows.html
```

- **index.html**: Landing page with navigation and hero content.
- **assets/styles.css**: Responsive styling tuned for dark and light modes.
- **assets/app.js**: Lightweight enhancements including navigation toggles and search stubs.
- **sections/**: Pre-rendered fragments loaded dynamically by `app.js`.

## Publishing

1. Export the site with `sapl website --export ./public`.
2. Host via any static site provider (GitHub Pages, Netlify, S3 + CloudFront).
3. Optionally run `sapl website --serve --port 8080` for local previews.

## Customisation Tips

- Modify `assets/styles.css` to align branding with your organisation.
- Add new HTML fragments under `sections/` and update the navigation list in `index.html`.
- Extend `assets/app.js` with fetch hooks that call SAPL plugins or remote APIs.

For the authoritative CLI reference that powers the website content, read [CLI_DEEP_DIVE.md](CLI_DEEP_DIVE.md).
