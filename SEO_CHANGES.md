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
| 2026-10-21 | d30cc00 | tesla-approved-bodyshop/* (36), tesla-suspension-noise (1), windscreen-camera-calibration (1) - 0-click pages only | Shortened <title>/og:title to under 575 px, main keyword first (tools/retitle.py); pages with clicks untouched | watching |
| 2026-10-21 | cf57838 | /about | ADDED one "Sister site" paragraph linking TeslaChargers.co.uk (only site-wide-relevant link added; footer unchanged) | additive |
| 2026-10-21 | cf57838 | /a1c797c468201b408b268a3855091834.txt, .github/workflows/indexnow.yml | IndexNow key file + workflow: 3 min after each push that changes site/, POSTs changed page URLs to api.indexnow.org | new pages |
| 2026-10-22 | (this commit) | garage pages (603), /locations/* (348), /about | Gold-standard cross-site linking: charger names as plain text, one contextual link per page to the matching teslachargers town/county page (was ~4,900 links incl. a homepage credit on every page); credit as plain text naming the sister site; About page states both sites are run by the same team | additive |
| 2026-10-22 | (this commit) | all pages (JSON-LD), /hevra/* (289 titles), 9 /locations/* titles, sitemap.xml | Two-reviewer fixes: FAQPage JSON-LD removed from 533 pages (visible FAQ text kept); HEVRA garage titles no longer claim Tesla servicing ("EV & Hybrid Servicing"); "& Repair" restored in 9 town titles; per-URL sitemap lastmod. No page with clicks had its title/H1 changed. | technical |
| 2026-10-22 | (this commit) | /about, /privacy, /terms, 10 guide pages, / (JSON-LD only) | Named owner: "Mr Joseph" replaced with XKey Developments (xkey.co.uk) in text, author and founder markup (E-E-A-T; both reviewers) | additive |
| 2026-10-22 | (this commit) | /locations/dundee, /locations/stirling, /services/suspension (+ slash forms) | 301s for the last old URLs Search Console reports as 404 | additive |

## 2026-10-30 - Search Console 404 follow-up
- 301 /services/tesla-service(/) -> / (old service URL still reported 404).
- 301 junk URLs Google built from broken HTML (/locations/chelmsford/</p>..., /locations/chelm</p>...) -> /locations/chelmsford.
- Left as-is on purpose: noindex on thin community pages (owner-stories, meetups, logs, /suggest forms) - under 300 words, waiting for submissions.

## 2026-11-02 - service centres, body shops, warranty, city answer boxes
| Date | Commit | URLs affected | Change | Status |
|---|---|---|---|---|
| 2026-11-02 | (see git log) | /tesla-service-centers | ADDED section below the existing listings: table of every official Tesla service centre in the UK and NI (address, postcode, service hours, roadside number) re-read from Tesla's UK locator, with last-checked date; each row links to the /dealer/ page and the matching /locations/ town page. Also added a sourced "official vs independent" comparison, "how to book (Tesla app)" steps and "where can I get my Tesla serviced". Title/H1/intro unchanged | additive |
| 2026-11-02 | (see git log) | /, /locations/ | ADDED one contextual link each to /tesla-service-centers#every-centre (descriptive anchor); homepage also links /warranty-guide | additive |
| 2026-11-02 | (see git log) | /authorised-tesla-service, /bodywork-accident-repair | ADDED sourced section on what Tesla-approved means, Tesla's own Dartford body repair centre, approved vs independent, and insurance (Financial Ombudsman). No new hub page: this existing page already targets "Tesla approved body shops UK", and Tesla publishes no UK list of third-party approved shops. Bodywork guide gets one link | additive |
| 2026-11-02 | (see git log) | /warranty-guide (zero-click page) | Rewritten from Tesla's UK warranty page and GB warranty PDFs: basic/SRS/battery and drive unit terms by model, rust, used-vehicle warranty, exclusions, independent servicing (Tesla wording + MVBEO 2023), transfer, how to claim. Title and URL kept; H1 and meta description now say "UK". Links added from before-you-book-service, buying-used-checklist, range-battery-guide | rewrite |
| 2026-11-02 | (see git log) | /locations/greater-london, manchester, glasgow, nottingham, newcastle | ADDED "quick answer" box under the intro (tools/enrich.py quick, marker block): official centres, nearest centre and distance, approved body shops, independents (counts from the page's own listings), links to nearby towns and neighbouring city pages | additive |
| 2026-11-02 | (see git log) | /dealer/tesla-service-glasgow, /tesla-garage-contact-details | Wrong-page fix: added a descriptive link to /locations/glasgow from the Glasgow dealer page (plus Tesla's published hours); added a by-city link line to the contact-details page | additive |
| 2026-11-02 | (see git log) | /home-charging-guide | ADDED one contextual link to the sister site's teslachargers.co.uk guides (home charging is moving there); page kept and indexed | additive |

## 2026-11-02 - weekly guard (wrong-page links)
| Date | Commit | URLs affected | Change | Status |
|---|---|---|---|---|
| 2026-11-02 | (see git log) | /dealer/tesla-service-{leeds,st-albans,nottingham,guildford,northampton,lincoln,liverpool,sheffield}, /authorised/steer-nottingham, /hevra/north-manchester-auto-electrics, /other/tesla-specialist-birmingham-ltd | Wrong-page fix: town searches were landing on these pages, not the town page. ADDED one line above the "Before you book" note: "Looking for <town>? See every Tesla service option in <town>" linking /locations/<town>. No title/H1/text changes | additive |

Guard notes 2026-11-02 (no rollback): /hevra/* aggregate position and clicks fell (tiny numbers, single-digit clicks) but impressions per day rose ~70% from new deep-ranking pages; the pages that had clicks before held or improved position, so not attributed to a change. /locations/* position worse by ~4 with clicks per day down ~13% (under the 30% bar). Both re-check next week.
| 2026-11-02 | (this commit) | /home-charging-guide | Sister-site link now points at teslachargers.co.uk/guides/tesla-home-charging/ (was the guides hub) | additive |

## 2026-11-06 - zero-click snippet rewrite (Joe: grow clicks)
| Date | Commit | URLs affected | Change | Status |
|---|---|---|---|---|
| 2026-11-06 | (this commit) | 146 pages with 0 clicks in 3 months that rank in the top 15 (list in the private folder: targets_paths.txt): /locations/* (59 town/county), /hevra/* (30), /other/* (21), /authorised/* (20), /dealer/* (10), /parts/* (5), /contact-tesla-uk | tools/snippets.py: garage pages get a meta description from their own structured data (name, street, postcode, phone, type) instead of the shared boilerplate, and a title saying 'address & phone' (official centres: 'Tesla Service Centre <place>: address, phone & booking'); town/county titles lead with 'Tesla garage(s) in <place>: service, repair & specialists (n)' (site's top query 'tesla garage near me' 791 impr/28d); /contact-tesla-uk title leads with '01628 450660' (664 impr/28d for the number, pos 9-11, 0 clicks). H1s and page text unchanged; no page with a click in 3 months touched. Before (3 months to 3 Nov): these pages 8,778 impr, 0 clicks; site 28d 631 clicks, 41.3k impr, CTR 1.5%, pos 13.4 | watching |
