"""Build the data behind /places/ (nearest Tesla service for every town and village in Great Britain).

  python3 tools/places.py /path/to/IPN_GB_2023.csv
  python3 tools/places.py --sitemaps-only      (rewrite the sitemaps from worker/places-data.js)

Inputs
  - ONS Index of Place Names in Great Britain (IPN, 2023 release; OGL v3, contains OS data). Only the
    'LOC' (locality) and 'BUA' (built-up area) rows are used: wards, parishes and council rows are
    admin units that repeat the same places. Same-name rows within 3 km are one place.
  - tools/places_extra.json: GB airports (sourced coordinates), which the ONS list does not have as places.
  - this site's garages (assets/garages-data.js) and /locations/ town and county pages (assets/finder.js).

Outputs (both generated, commit them)
  - worker/places-data.js   compact data imported by worker/index.js
  - site/sitemap-places.xml + site/sitemap-places-N.xml   sitemap index and parts (static files)

Places that already have a /locations/<town> page here (same name within 8 miles) get no new page:
the area list links them to the existing page, so a town search still lands on that town's page.
Idempotent: the same inputs give byte-identical output (lastmod comes from BUILT, default the data date)."""
import os, re, sys, csv, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitelib import ROOT, S, garages, ts_places, miles, slugify

BUILT = os.environ.get('BUILT', '2026-11-09')
SITE = 'https://teslaservice.co.uk'
PART = 10000


def clean(s):
    s = re.sub(r'\s*/\s*', ' / ', re.sub(r'\s+', ' ', s)).strip()
    m = re.match(r"^([^,()/]+), ([A-Za-z'-]+)$", s)   # gazetteer order 'Mount, The' / 'Acton, East' -> 'The Mount' / 'East Acton'
    return f'{m.group(2)} {m.group(1)}' if m else s


def base_name(s):
    return re.split(r'\s*[(/]', s)[0].strip().rstrip(',') or s


def key(s):
    return slugify(base_name(s))


def write_sitemaps(A, out):
    """Sitemap index + parts: hub, area pages and built-up-area place pages only. Locality ('LOC') pages are
    served with noindex, follow (worker/index.js indexable()), so they are left out here."""
    urls = [f'{SITE}/places'] + [f'{SITE}/places/{a[1]}' for a in A] + [f'{SITE}/places/{A[p[1]][1]}/{p[4]}' for p in out if p[6]]
    for f in os.listdir(S):
        if re.match(r'sitemap-places(-\d+)?\.xml$', f): os.remove(os.path.join(S, f))
    parts = [urls[i:i + PART] for i in range(0, len(urls), PART)]
    for n, part in enumerate(parts, 1):
        body = ''.join(f'  <url><loc>{u}</loc><lastmod>{BUILT}</lastmod></url>\n' for u in part)
        open(os.path.join(S, f'sitemap-places-{n}.xml'), 'w', encoding='utf-8').write(
            '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + '</urlset>\n')
    idx = ''.join(f'  <sitemap><loc>{SITE}/sitemap-places-{n}.xml</loc><lastmod>{BUILT}</lastmod></sitemap>\n' for n in range(1, len(parts) + 1))
    open(os.path.join(S, 'sitemap-places.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + idx + '</sitemapindex>\n')
    return urls


def sitemaps_only():
    """Rewrite the sitemaps from the committed worker/places-data.js (no ONS file needed)."""
    d = {}
    for line in open(os.path.join(ROOT, 'worker', 'places-data.js'), encoding='utf-8'):
        m = re.match(r'export const (\w+) = (.*);$', line.rstrip('\n'))
        if m: d[m.group(1)] = json.loads(m.group(2))
    urls = write_sitemaps(d['A'], d['P'])
    print(json.dumps({'sitemap_urls': len(urls)}))


def main(ipn):
    rows = []
    with open(ipn, encoding='cp1252', newline='') as f:
        for x in csv.DictReader(f):
            if x['descnm'] not in ('LOC', 'BUA'): continue
            nm = clean(x['place22nm'])
            if not nm or not x['lat']: continue
            area = x['lad22nm'] if x['cty22nm'] in ('', 'Inner London', 'Outer London') else x['cty22nm']   # London: the borough
            rows.append((nm, x['descnm'] == 'BUA', float(x['lat']), float(x['long']), area, x['lad22nm'], x['ctry22nm']))
    # airports (tools/places_extra.json): not places in the ONS list; area = that of the nearest listed place
    for e in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'places_extra.json'), encoding='utf-8'))['places']:
        n = min(rows, key=lambda r: (r[2] - e['lat']) ** 2 + ((r[3] - e['lon']) * 0.6) ** 2)
        rows.append((e['name'], True, e['lat'], e['lon'], n[4], n[5], n[6]))
    # one place per name cluster: BUA rows first (their point is the centre of the built-up area)
    rows.sort(key=lambda r: (key(r[0]), not r[1], r[0], r[2], r[3]))
    places, bykey = [], {}
    for r in rows:
        k = key(r[0])
        if any(miles(r[2], r[3], p[2], p[3]) < 1.9 for p in bykey.get(k, [])): continue
        bykey.setdefault(k, []).append(r); places.append(r)

    # existing /locations/ pages
    tsp = ts_places()
    towns = [(n, la, lo, u) for n, la, lo, u in tsp if '/county/' not in u]
    county_pages = {u.rsplit('/', 1)[1]: u for n, la, lo, u in tsp if '/county/' in u}

    def covered(r):
        k = key(r[0])
        for n, la, lo, u in towns:
            if key(n) == k and miles(r[2], r[3], la, lo) <= 8: return u
        return None

    areas = sorted({(r[4], r[6]) for r in places}, key=lambda a: (a[1], a[0]))
    AI = {a[0]: i for i, a in enumerate(areas)}
    aslug = [slugify(a[0]) for a in areas]
    assert len(set(aslug)) == len(aslug), 'area slug clash'

    # biggest places (BUA) as 'near X' anchors for same-name places in one area
    bua = [r for r in places if r[1]]
    grid = {}
    for r in bua: grid.setdefault((int(r[2] * 10), int(r[3] * 6)), []).append(r)

    def near_names(r):
        """'near X' candidates: towns with their own page here (within 15 miles) first, then built-up areas, nearest first."""
        c = sorted((miles(r[2], r[3], la, lo), n) for n, la, lo, u in towns if key(n) != key(r[0]) and miles(r[2], r[3], la, lo) <= 15)
        b = []
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                for x in grid.get((int(r[2] * 10) + dy, int(r[3] * 6) + dx), []):
                    if key(x[0]) != key(r[0]): b.append((miles(r[2], r[3], x[2], x[3]), x[0]))
        seen, out = set(), []
        for d, n in c[:2] + sorted(b)[:15] + c[2:]:
            n = base_name(n)
            if slugify(n) not in seen: seen.add(slugify(n)); out.append(n)
        return out

    out, links = [], []
    by_area_slug = {}
    for r in sorted(places, key=lambda r: (AI[r[4]], key(r[0]), r[2], r[3])):
        by_area_slug.setdefault((AI[r[4]], key(r[0])), []).append(r)
    for (ai, k), grp in sorted(by_area_slug.items()):
        multi = len(grp) > 1
        used = set()
        for r in grp:
            u = covered(r)
            if u:
                links.append([r[0], ai, round(r[2], 4), round(r[3], 4), u]); continue
            slug, near = k, ''
            if multi:
                for nn in near_names(r) + [r[5]]:
                    slug, near = f'{k}-near-{slugify(nn)}', nn
                    if slug not in used: break
                n = 2
                while slug in used: slug, near = f'{k}-near-{slugify(near)}-{n}', near; n += 1
                if slug.endswith(f'-{n - 1}') and n > 2: print('numbered slug', slug)
            used.add(slug)
            out.append([r[0], ai, round(r[2], 4), round(r[3], 4), slug, near, 1 if r[1] else 0])
    # a lone place whose base slug is taken by a 'covered' one is fine: covered places have no page

    G = [[g['n'], g['c'], g['url'], round(g['lat'], 5), round(g['lon'], 5), g.get('town') or '', 1 if g.get('hevra') else 0, re.sub(r'\s*\(earlier listings?:[^)]*\)', '', g.get('addr') or ''), g.get('pc') or '']
         for g in garages() if g.get('lat') and g.get('url')]
    A = [[a[0], aslug[i], a[1], county_pages.get(aslug[i], '')] for i, a in enumerate(areas)]
    LT = [[n, u, la, lo] for n, la, lo, u in towns]

    data = {'BUILT': BUILT, 'A': A, 'P': out, 'L': links, 'G': G, 'LT': LT}
    os.makedirs(os.path.join(ROOT, 'worker'), exist_ok=True)
    js = '// Generated by tools/places.py - do not edit by hand.\n' + ''.join(
        f'export const {k} = {json.dumps(v, ensure_ascii=False, separators=(",", ":"))};\n' for k, v in data.items())
    open(os.path.join(ROOT, 'worker', 'places-data.js'), 'w', encoding='utf-8').write(js)

    urls = write_sitemaps(A, out)
    print(json.dumps({'places': len(out), 'linked_to_locations': len(links), 'areas': len(A), 'garages': len(G), 'sitemap_urls': len(urls),
                      'data_kb': len(js.encode()) // 1024}))


if __name__ == '__main__':
    sitemaps_only() if sys.argv[1] == '--sitemaps-only' else main(sys.argv[1])
