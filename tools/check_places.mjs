// Check every /places page the Worker serves: node tools/check_places.mjs   (exit 1 on any problem)
// Renders the hub, every area and every place page; checks unique titles and descriptions, valid JSON-LD,
// one H1, canonical = own URL, no 'undefined'/'NaN', every internal link resolves (Worker page or static file),
// that only built-up-area place pages are indexable (localities carry noindex, follow), and that the sitemap
// files list exactly the indexable pages.
import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..'), S = path.join(ROOT, 'site');
const w = await import(path.join(ROOT, 'worker', 'index.js'));
const { A, P } = await import(path.join(ROOT, 'worker', 'places-data.js'));
const idxUrls = new Set(['/places', ...A.map(a => `/places/${a[1]}`), ...P.filter(w.indexable).map(p => `/places/${A[p[1]][1]}/${p[4]}`)]);
const red = new Set(fs.readFileSync(path.join(S, '_redirects'), 'utf8').split('\n').map(l => l.split('#')[0].trim().split(/\s+/)[0]).filter(Boolean));
const staticOk = p => { p = decodeURIComponent(p); const f = path.join(S, p);
  return p === '/' || red.has(p) || (fs.existsSync(f) && fs.statSync(f).isFile()) || fs.existsSync(f + '.html') || fs.existsSync(path.join(f, 'index.html')) || fs.existsSync(f.replace(/\/$/, '') + '.html'); };
const urls = ['/places', ...A.map(a => `/places/${a[1]}`), ...P.map(p => `/places/${A[p[1]][1]}/${p[4]}`)];
const served = new Set(urls), titles = new Map(), descs = new Map(), bad = [], links = new Set();
let words = 0, maxBytes = 0, maxUrl = '';
const t0 = Date.now();
for (const u of urls) {
  const h = w.render(u);
  if (!h) { bad.push(['no page', u]); continue; }
  if (h.length > maxBytes) { maxBytes = h.length; maxUrl = u; }
  if (/undefined|NaN/.test(h)) bad.push(['undefined/NaN', u]);
  if (h.includes('<meta name="robots" content="noindex') === idxUrls.has(u)) bad.push(['robots meta', u]);
  if ((h.match(/<h1>/g) || []).length !== 1) bad.push(['h1 count', u]);
  if (!h.includes(`<link rel="canonical" href="https://teslaservice.co.uk${u}">`)) bad.push(['canonical', u]);
  const t = Buffer.from(h.match(/<title>(.*?)<\/title>/)[1]).toString(), d = Buffer.from(h.match(/<meta name="description" content="(.*?)">/)[1]).toString();   // copy: a regex match keeps the whole page alive
  titles.set(t, (titles.get(t) || 0) + 1); descs.set(d, (descs.get(d) || 0) + 1);
  if (d.length > 165) bad.push(['long description', u, d.length]);
  for (const m of h.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) { try { JSON.parse(m[1]); } catch (e) { bad.push(['bad JSON-LD', u]); } }
  for (const m of h.matchAll(/href="(\/[^"#?]*)/g)) if (!links.has(m[1])) links.add(Buffer.from(m[1]).toString());
  if (u.split('/').length === 4) words += h.replace(/<(script|style)[\s\S]*?<\/\1>/g, ' ').replace(/<[^>]+>/g, ' ').split(/\s+/).filter(Boolean).length;
}
for (const l of links) if (!(l.startsWith('/places') ? served.has(l) : staticOk(l))) bad.push(['broken link', l]);
// sitemaps
const sm = new Set();
for (const f of fs.readdirSync(S)) if (/^sitemap-places-\d+\.xml$/.test(f)) for (const m of fs.readFileSync(path.join(S, f), 'utf8').matchAll(/<loc>https:\/\/teslaservice\.co\.uk([^<]+)<\/loc>/g)) sm.add(m[1]);
const smMissing = [...idxUrls].filter(u => !sm.has(u)).length, smExtra = [...sm].filter(u => !idxUrls.has(u)).length;
// static pages that link into /places must point at real pages
const dupT = [...titles].filter(x => x[1] > 1), dupD = [...descs].filter(x => x[1] > 1);
const out = { pages: urls.length, indexable: idxUrls.size, secs: (Date.now() - t0) / 1000, avg_words_place_page: Math.round(words / P.length), biggest_kb: Math.round(maxBytes / 1024), biggest: maxUrl,
  internal_links: links.size, bad: bad.length, dup_titles: dupT.length, dup_descriptions: dupD.length, sitemap_missing: smMissing, sitemap_extra: smExtra };
console.log(JSON.stringify(out));
if (bad.length) console.log(bad.slice(0, 20));
if (dupT.length) console.log('dup titles', dupT.slice(0, 10));
process.exit(bad.length || dupT.length || smMissing || smExtra ? 1 : 0);
