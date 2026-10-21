# teslaservice.co.uk

Static site served by the Cloudflare Worker `rough-snow-bc1f` using Workers static assets
(`html_handling: auto-trailing-slash`, `not_found_handling: 404-page`). Settings in `wrangler.jsonc`.

- `site/` - every deployed file. This repo is now the source of truth (copied from the live site on 21 Oct 2026; the copy matched the live crawl: 1,234 pages, 836 redirects).
- `site/_redirects`, `site/_headers` - Cloudflare asset rules (copied exactly from the live deployment, version 31).
- `tools/check.py` - local crawl of `site/` as Cloudflare serves it. Must pass (broken links 0, duplicate titles 0, valid JSON-LD, no noindex page in the sitemap, every redirect target exists). Runs on every push (GitHub Actions "Check site").
- `tools/mirror.py` + workflow "Mirror live site" - manual only; re-copies the live site.
- `tools/guard_titles.py` - run before every push: fails if a page with Search Console clicks (private file, not in git) had its title, H1 or meta description changed.
- `tools/enrich.py` - idempotent data blocks between marker comments: `garages` ("Charging near <garage>", from the teslachargers.co.uk data) and `towns` ("at a glance" box on town/county pages). `tools/retitle.py` - shortens long titles on zero-click pages only.
- `_redirects`: static rules must stay ABOVE the splat rules (`/garages/*`), or the Cloudflare build fails; check.py enforces it.
- Workflows: "Wrangler dry run", "Live check" (fetches changed pages 3 min after a push; results as check-run annotations), "IndexNow" (pings changed pages; key file in site/).
- `SEO_CHANGES.md` - log of every change that could move rankings (read by the weekly SEO guard, which rolls back changes that clearly hurt).

## Rules (same as teslachargers.co.uk)
Additive only on pages that already get clicks: never change the title, H1, URL or main text of a page with clicks in the last 28 days. A town search must land on that town's page, a county search on the county page. Facts only from sources actually read; never invent prices, reviews or ratings. Titles under 575 px. Old URLs always 301 to the new page. Open web pages only from search results (search-before-fetch). Nothing is sent in Joe's name without his yes.

## Deploy
Push to `main` -> Cloudflare Workers Builds runs `npx wrangler deploy` (about 2 minutes). Roll back from the dashboard (Worker > Deployments) if a deploy goes wrong; the pre-repo deployment is version 31.
