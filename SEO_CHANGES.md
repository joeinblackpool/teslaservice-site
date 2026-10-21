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
| 2026-10-21 | (pending) | /hevra/*, /other/*, /parts/* (garage pages 451-600, alphabetical) | ADDED 'Charging near <garage>' section below existing content (Superchargers, rapid chargers, teslachargers town link; OCM CC BY-SA + Tesla credit) | additive |
