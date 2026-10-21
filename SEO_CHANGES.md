# SEO change log (read by the weekly SEO guard)

Rollback rule: a change "clearly hurt" only if ALL hold for its URL pattern, comparing the 14 days before with the days since (at least 10 days): 200+ impressions before; average position worse by 3+; clicks down 30%+; and not matched by a similar site-wide drop.

| Date | Commit | URLs affected | Change | Status |
|---|---|---|---|---|
| 2026-10-21 | (repo set-up) | all | Site moved to GitHub; identical files | baseline |
| 2026-10-21 | (first Git deploy) | all | First deploy from GitHub: identical pages; removed the copy of Cloudflare's auto-injected analytics tag (the edge adds it itself) | baseline |
| 2026-10-21 | ac941fd | /garages/*/, /services/*/ (52 old paths, with and without slash: 104 rules) | 301 to the same garage's current /dealer/ or /other/ page, else the town /locations/ page, /services/x/ to the matching guide | watching |
| 2026-10-21 | d2ba013 | /dealer/*, /authorised/*, /hevra/* (first 150 garage pages, alphabetical) | ADDED "Charging near <garage>" section below existing content: nearest 3 Tesla Superchargers (60 mi), nearest 3 public rapid chargers 50 kW+ (15 mi), link to the teslachargers.co.uk town page; credited Open Charge Map CC BY-SA 4.0 + Tesla. No title/H1/text changes | additive |
| 2026-10-21 | dd19e41 | /hevra/* (garage pages 151-300, alphabetical) | ADDED 'Charging near <garage>' section below existing content (Superchargers, rapid chargers, teslachargers town link; OCM CC BY-SA + Tesla credit) | additive |
| 2026-10-21 | c9be4f9 | /hevra/*, /other/* (garage pages 301-450, alphabetical) | ADDED 'Charging near <garage>' section below existing content (Superchargers, rapid chargers, teslachargers town link; OCM CC BY-SA + Tesla credit) | additive |
| 2026-10-21 | f256b54 | /hevra/*, /other/*, /parts/* (garage pages 451-600, alphabetical) | ADDED 'Charging near <garage>' section below existing content (Superchargers, rapid chargers, teslachargers town link; OCM CC BY-SA + Tesla credit) | additive |
| 2026-10-21 | 200d4e1 | /other/*, /parts/* (remaining garage pages with coordinates) | ADDED 'Charging near <garage>' section below existing content (Superchargers, rapid chargers, teslachargers town link; OCM CC BY-SA + Tesla credit) | additive |
| 2026-10-21 | e9fcce3 | /locations/<town>, /locations/county/<x> (first 150, alphabetical) | ADDED at-a-glance box below the listings: counts by type (from the page's own listings), nearest official Tesla Service Centre, Superchargers nearby/in county, link to teslachargers.co.uk town/county page and to the county page | additive |
| 2026-10-21 | 31433a5 | /locations/<town>, /locations/county/<x> (next 150) | ADDED at-a-glance box below the listings (counts from the page's own listings, nearest Tesla Service Centre, Superchargers, teslachargers + county links) | additive |
| 2026-10-21 | 6cae0cb | /locations/<town> (remaining) | ADDED at-a-glance box below the listings (counts from the page's own listings, nearest Tesla Service Centre, Superchargers, teslachargers + county links) | additive |
| 2026-10-21 | 5ab2707 | authorised/* (62), dealer/* (20), hevra/* (68) - 0-click pages only | Shortened <title>/og:title to under 575 px, main keyword first (tools/retitle.py); pages with clicks untouched | watching |
| 2026-10-21 | e222bcf | hevra/* (150) - 0-click pages only | Shortened <title>/og:title to under 575 px, main keyword first (tools/retitle.py); pages with clicks untouched | watching |
| 2026-10-21 | 98db335 | hevra/* (71), known-issues-by-model (1), locations/* (21), other/* (57) - 0-click pages only | Shortened <title>/og:title to under 575 px, main keyword first (tools/retitle.py); pages with clicks untouched | watching |
| 2026-10-21 | 2d36159 | other/* (81), owner-stories (1), owner-tips (1), parts/* (66), tesla-approved-bodyshop/* (1) - 0-click pages only | Shortened <title>/og:title to under 575 px, main keyword first (tools/retitle.py); pages with clicks untouched | watching |
| 2026-10-21 | (pending) | tesla-approved-bodyshop/* (36), tesla-suspension-noise (1), windscreen-camera-calibration (1) - 0-click pages only | Shortened <title>/og:title to under 575 px, main keyword first (tools/retitle.py); pages with clicks untouched | watching |
