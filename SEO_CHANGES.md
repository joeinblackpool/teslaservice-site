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

## 2026-11-09 - Tesla fix it yourself (DIY) page
| Date | Commit | URLs affected | Change | Status |
|---|---|---|---|---|
| 2026-11-09 | (see git log) | /tesla-fix-it-yourself (new); /guides, /diy-jobs-ranked (one link each); sitemap.xml, llms.txt | New page: which common Tesla faults UK owners can safely fix themselves (cabin filters, window and camera calibration, resets, frozen handles, stuck charge cable, 12V checks, tyre rotation) with steps summarised from Tesla's own DIY guides and manuals (20 cited sources), plus a "leave to a pro" section correcting risky forum advice (HV battery deep discharge, ball-joint grease injection, heater removal). Article + BreadcrumbList JSON-LD. Targets "tesla fix it yourself / tesla diy repair" searches. No title, H1 or text changed on existing pages | new page |

## 2026-11-09 - Tesla repair near every town and village (/places)
| Date | Commit | URLs affected | Change | Status |
|---|---|---|---|---|
| 2026-11-09 | (this commit) | /places, /places/<area> (176), /places/<area>/<place> (58,348) (new); sitemap-places.xml (+6 parts) in robots.txt | New pages: "Tesla repair near <place>" for every locality and built-up area in the ONS Index of Place Names (GB, 2023) plus 22 GB airports: nearest official Tesla Service Centres (distance, direction, directions button), nearest HEVRA/independent garages, Tesla-approved bodyshops and parts from our own listings, counts within 10/20/50 miles, advice by distance, nearby places. Served by a Worker script only on /places (static site unchanged). 478 places that already have a /locations/<town> page get no new page: the area list links the existing page, so town searches still land there. Targets "tesla repair/service near <place>" for places with no page today | new pages |
| 2026-11-09 | (this commit) | /locations/ (1), /locations/county/* (91), /locations/<town> (277) | Additive links between markers: hub link on /locations/, area link on county pages, "Tesla repair near villages around <town>" (10 nearest place pages) on town pages. Titles, H1s, descriptions and existing text unchanged | additive |
| 2026-11-09 | (this commit) | /places/<NI council> (11 new), /places/<NI council>/<place> (667 new); /places hub (title now "...in the UK", count); /locations/belfast, /locations/lisburn, 6 NI county pages, /locations/ (links) | Northern Ireland added: GeoNames populated places (CC BY 4.0; the OSNI gazetteer download refuses our build machine) grouped by the 11 councils. Belfast and Lisburn keep their existing town pages (linked, no new page). No existing /places URL changed (sitemap diff: 0 removed) | new pages |


## 2026-11-09 - /places: better links from town pages
| Date | Commit | URLs affected | Change | Status |
|---|---|---|---|---|
| 2026-11-09 | (this commit) | /locations/<town> (285) | Between the places-links markers only: the "Tesla repair near villages around <town>" line now links the 10 nearest built-up-area place pages (e.g. Manchester: Salford, Stretford, Prestwich) instead of the nearest hamlets/street names. All 58,348 place pages stay indexable and in the sitemap (Joe, 9 Nov: every place gets its own page). Titles, H1s and text unchanged | additive |
| 2026-11-09 | (this commit) | /places/<area>/<place> (193 merged into one page each, 301), place names on ~1,000 pages, 4 area names; worker 301s | Glitch scan fixes. ONS gazetteer names tidied ("Cray, St. Mary" -> "St. Mary Cray", "Corston (Bath and North East Somerset)" -> "Corston"); URLs unchanged. Built-up areas split per council (Brent had pages in Barnet, Ealing, Harrow, Kensington; Romford's page linked "Havering" three times) merged to one page, the rest 301 to it (`R` in worker/places-data.js, from tools/places_fix.py). Names like "Bournemouth, Christchurch an" and "Bristol, City of" fixed in text. Belfast/Jersey/Isle of Man garages no longer shown as nearest to GB places across the sea; Tesla Body Repair Centre Dartford listed as a bodyshop, not a Service Centre. Place descriptions now name the area or "near" town (16 duplicates gone). Pages are 1 day old, so no ranking to lose | new pages (fix) |
| 2026-11-09 | (this commit) | /guides, /resources, /reviews, /suggest, /calculator, /locations/ (footer added); 7 garage pages (long URLs wrap on phones) | Layout glitches: 6 hub pages had lost their footer (About, Privacy, Terms links); 7 pages scrolled sideways on phones because a long source URL did not wrap. No title, H1, description or text changed | additive |
| 2026-11-09 | (this commit) | /places/<area>/<place> (~350 pages moved to the right council, old URL 301s) | Rebuilt from the ONS file: a built-up area that crosses councils now keeps only its main piece (the council with most wards/parishes named after it, then the town-centre locality), so Stourbridge is under West Midlands, Stamford under Lincolnshire, Consett under County Durham. Every URL the first build served still works (301 to the same place's page) | new pages (fix) |
## 2026-11-09 - Models tab (Joe: more content in a new tab)
| Date | Commit | URLs affected | Change | Status |
|---|---|---|---|---|
| 2026-11-09 | (this commit) | /models/, /models/model-3, /models/model-y, /models/model-s, /models/model-x (new); sitemap.xml; llms.txt | New "Models" section (tools/models.py): grouped short-answer Q&A per model (servicing, common faults, warranty, repairs), each fact cited to Tesla's owner's manuals / service-interval pages, Tesla UK warranty page, GOV.UK, or sources already cited on this site. Article + BreadcrumbList JSON-LD only (no FAQPage, per 22 Oct). Targets "tesla model 3/y/s/x service/servicing/repair" searches with no dedicated page today | new pages |
| 2026-11-09 | (this commit) | every static page with the main nav (1,234) + worker /places template | ADDED a "Models" item to the main nav after Guides. No title, H1, description or body text changed | additive |
| 2026-11-09 | (this commit) | /guides, /known-issues-by-model | ADDED one link line each to the new model pages | additive |

## 2026-11-09 - Tesla service cost page
| Date | Commit | URLs affected | Change | Status |
|---|---|---|---|---|
| 2026-11-09 | (this commit) | /tesla-service-cost (new) | New guide for "how much does a Tesla service cost (UK)", a search with no page here: Cap HPI three-year/60k figures (servicing £338, brakes £113, tyres £2,377, total £2,946) via EV Fleet World 7 May 2024, Tesla's maintenance intervals (owner's manual), owner-posted TMC invoices labelled as single examples, official vs independent, MOT (GOV.UK), cost-saving links. Article + BreadcrumbList JSON-LD | new pages |
| 2026-11-09 | (this commit) | /guides, /tesla-service-schedule, /before-you-book-service, sitemap.xml, llms.txt | ADDED one link each to /tesla-service-cost. No titles, H1s or text changed | additive |
| 2026-11-09 | (this commit) | every static page (1,182) + /places Worker pages | Clean-up, no content change: one main menu everywhere (Models added where missing; /places pages now show Reviews like the rest of the site instead of an extra Places item, which stays linked from /locations and every place breadcrumb); current section marked in the menu; one page width (760px, was 600-820px depending on when the page was built, so the menu no longer wraps on About, Calculator, Suggest); body line spacing 1.65 everywhere. tools/consistency.py keeps it that way and runs in "Check site". Titles, H1s, descriptions, URLs and text unchanged | layout only |

## 2026-11-09 - /places business schema
| Date | Commit | URLs affected | Change | Status |
|---|---|---|---|---|
| 2026-11-09 | (this commit) | /places/<area>/<place> (all) | JSON-LD only: the page's ItemList now holds each listed business as a typed node (AutomotiveBusiness / AutoRepair / AutoBodyShop / LocalBusiness) with address and geo, @id matching the business's own page (same entity). Bodyshops and parts added to the list. No visible change | technical |

## 2026-11-09 - homepage links to popular town pages
| Date | Commit | URLs affected | Change | Status |
|---|---|---|---|---|
| 2026-11-09 | (this commit) | / | ADDED one line under the region links (top-towns markers): "Tesla service in popular towns:" linking 24 big-town /locations pages (Reading, Birmingham, Manchester, ...). Joe: "Tesla service Reading" shows no page from the site; town pages were only reachable via region/county pages. Title, H1, text unchanged | additive |

## 2026-11-09 - /places: named places from parishes, Welsh communities and London wards

| Date | Commit | URLs affected | Change | Status |
|---|---|---|---|---|
| 2026-11-09 | (this commit) | 2,902 new /places/<area>/<place> URLs; county pages' place counts | ADDED pages for named places the ONS list only has as a civil parish (Abinger), Welsh community (Beddgelert) or London ward (Canons). Total 61,715 place pages. No existing URL changes: a name already in the same council area or within 8 miles gets no new page; electoral divisions, wards outside London and admin labels skipped | additive |

## 2026-11-09 Single sitemap index
- Added /sitemap-index.xml (sitemap.xml + the 7 places parts) so one URL covers all 63,130 pages; robots.txt now points only to it. Old sitemap URLs still served unchanged.
