# SEO change log (read by the weekly SEO guard)

Rollback rule: a change "clearly hurt" only if ALL hold for its URL pattern, comparing the 14 days before with the days since (at least 10 days): 200+ impressions before; average position worse by 3+; clicks down 30%+; and not matched by a similar site-wide drop.

| Date | Commit | URLs affected | Change | Status |
|---|---|---|---|---|
| 2026-10-21 | (repo set-up) | all | Site moved to GitHub; identical files | baseline |
| 2026-10-21 | (first Git deploy) | all | First deploy from GitHub: identical pages; removed the copy of Cloudflare's auto-injected analytics tag (the edge adds it itself) | baseline |
| 2026-10-21 | 301 old GSC URLs | /garages/*/, /services/*/ (52 old paths, with and without slash: 104 rules) | 301 to the same garage's current /dealer/ or /other/ page, else the town /locations/ page, /services/x/ to the matching guide | watching |
