# teslaservice.co.uk

Static site served by the Cloudflare Worker `rough-snow-bc1f` (static assets, html_handling auto-trailing-slash, 404-page).

- `site/` - the deployed files (mirrored from the live site on 21 Oct 2026, the source of truth from now on)
- `site/_redirects`, `site/_headers` - Cloudflare asset rules, copied from the live deployment
- `tools/` - build and check scripts
