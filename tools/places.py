"""Build the data behind /places/ (nearest Tesla service for every town and village in Great Britain).

  python3 tools/places.py /path/to/IPN_GB_2023.csv [/path/to/geonames/GB.txt]   (GB.txt: Northern Ireland, see below)
  python3 tools/places.py --sitemaps-only      (rewrite the sitemaps from worker/places-data.js)

Inputs
  - ONS Index of Place Names in Great Britain (IPN, 2023 release; OGL v3, contains OS data). Only the
    'LOC' (locality) and 'BUA' (built-up area) rows are the places; parish, Welsh community and ward
    names add the named places those miss (see admin_rows). Same-name rows within 3 km are one place.
  - optional: GeoNames GB.txt (download.geonames.org/export/dump/GB.zip, CC BY 4.0) for Northern Ireland's
    towns, villages and localities. Without it Northern Ireland gets no place pages.
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
NI_COUNCILS = {'N09000001': 'Antrim and Newtownabbey', 'N09000002': 'Armagh City, Banbridge and Craigavon', 'N09000003': 'Belfast',
               'N09000004': 'Causeway Coast and Glens', 'N09000005': 'Derry City and Strabane', 'N09000006': 'Fermanagh and Omagh',
               'N09000007': 'Lisburn and Castlereagh', 'N09000008': 'Mid and East Antrim', 'N09000009': 'Mid Ulster',
               'N09000010': 'Newry, Mourne and Down', 'N09000011': 'Ards and North Down'}


def clean(s):
    s = re.sub(r'\s*/\s*', ' / ', re.sub(r'\s+', ' ', s)).strip()
    m = re.match(r"^([^,()/]+), ([A-Za-z'-]+)$", s)   # gazetteer order 'Mount, The' / 'Acton, East' -> 'The Mount' / 'East Acton'
    return f'{m.group(2)} {m.group(1)}' if m else s


def base_name(s):
    return re.split(r'\s*[(/]', s)[0].strip().rstrip(',') or s


def key(s):
    return slugify(base_name(s))


def write_sitemaps(A, out):
    """Sitemap index + parts: hub, area pages and every place page."""
    urls = [f'{SITE}/places'] + [f'{SITE}/places/{a[1]}' for a in A] + [f'{SITE}/places/{A[p[1]][1]}/{p[4]}' for p in out]
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


GENERIC = set("""abbey castle cathedral central priory harbour riverside village valley park parks hill hills moor moors forest marsh
market quay docks dock bridge university station heath green common town city centre center north south east west
great little upper lower nether over bay sands island islands
northern southern eastern western rural urban coast coastal lakes vale downs fields meadows marina""".split())
SUFFIX = {'north', 'south', 'east', 'west', 'central', 'rural', 'urban', 'town', 'without', 'within', 'ward', 'ed',
          'northeast', 'northwest', 'southeast', 'southwest', 'north-east', 'north-west', 'south-east', 'south-west', 'centre', 'village', 'and',
          'upper', 'lower', 'great', 'little'}


def admin_rows(ipn):
    """Parish (PAR) and Welsh community (COM) names, and London ward (WD) names (London wards are its neighbourhoods;
    elsewhere they are mostly council labels), split at '&' / 'and' / 'with' / ',' / ':'."""
    out = []
    with open(ipn, encoding='cp1252', newline='') as f:
        for x in csv.DictReader(f):
            t = x['descnm']
            if t not in ('PAR', 'COM', 'WD') or not x['lat'] or t == 'WD' and x['rgn22nm'] != 'London': continue
            nm = re.sub(r'\s*\([^)]*\)\s*$', '', x['place22nm']).strip()
            if re.search(r'\d|unparished|\bED$|\bWard\b|\bDistrict\b|\bScotland\b|shire$|\bSide$|\bFields$', nm, re.I): continue
            area = x['lad22nm'] if x['cty22nm'] in ('', 'Inner London', 'Outer London') else x['cty22nm']
            for part in re.split(r'\s*(?:&|,|\band\b|\bwith\b|\bgyda\b|\ba\b|/|:)\s*', nm):
                part = clean(part.strip(' -'))
                w = part.lower().split()
                if len(part) < 3 or not w or w[-1] in SUFFIX: continue
                if len(w) == 1 and w[0] in GENERIC or all(v in GENERIC for v in w) or t == 'WD' and w[0] in ('st', 'st.', 'saint', 'all', 'holy'): continue
                out.append((part, False, float(x['lat']), float(x['long']), area, x['lad22nm'], x['ctry22nm']))
    out.sort(key=lambda r: (key(r[0]), r[2], r[3]))
    return out


def main(ipn, ni=None):
    # a built-up area that crosses councils has one BUA row per council (splitind 1): keep only its main piece.
    # Main = the council with most wards/parishes named after the town, then the one holding the same-name
    # locality (the town-centre point), then the council the town is named after.
    split, loc, admin = {}, {}, []
    with open(ipn, encoding='cp1252', newline='') as f:
        for x in csv.DictReader(f):
            if not x['lat']: continue
            if x['descnm'] == 'BUA' and x['splitind'] == '1': split.setdefault(x['bua22cd'], []).append(x)
            elif x['descnm'] == 'LOC': loc.setdefault(key(clean(x['place22nm'])), []).append(x)
            elif x['descnm'] in ('WD', 'PAR'): admin.append((key(x['place22nm']), float(x['lat']), float(x['long']), x['lad22nm']))
    akey = {}
    for k, la, lo, lad in admin: akey.setdefault(k.split('-')[0], []).append((k, la, lo, lad))
    main = {}
    for code, xs in split.items():
        la, lo = sum(float(x['lat']) for x in xs) / len(xs), sum(float(x['long']) for x in xs) / len(xs)
        k = key(clean(xs[0]['place22nm'])); lads = [x['lad22nm'] for x in xs]; nm = clean(xs[0]['place22nm']).lower()
        wards = {}
        for ak, a_la, a_lo, lad in akey.get(k.split('-')[0], []):
            if (ak == k or ak.startswith(k + '-')) and lad in lads and miles(la, lo, a_la, a_lo) <= 6: wards[lad] = wards.get(lad, 0) + 1
        lc = sorted((miles(la, lo, float(l['lat']), float(l['long'])), l['lad22nm']) for l in loc.get(k, []))
        lc = [lad for d, lad in lc if d <= 6 and lad in lads]
        main[code] = max(lads, key=lambda l: (wards.get(l, 0), bool(lc) and lc[0] == l, nm in l.lower(), -lads.index(l)))

    rows = []
    with open(ipn, encoding='cp1252', newline='') as f:
        for x in csv.DictReader(f):
            if x['descnm'] not in ('LOC', 'BUA'): continue
            nm = clean(x['place22nm'])
            if not nm or not x['lat']: continue
            if x['descnm'] == 'BUA' and x['splitind'] == '1' and x['lad22nm'] != main.get(x['bua22cd'], x['lad22nm']): continue
            area = x['lad22nm'] if x['cty22nm'] in ('', 'Inner London', 'Outer London') else x['cty22nm']   # London: the borough
            rows.append((nm, x['descnm'] == 'BUA', float(x['lat']), float(x['long']), area, x['lad22nm'], x['ctry22nm']))
    # Northern Ireland (not in the GB list): GeoNames GB.txt (CC BY 4.0), populated places (feature class P) with
    # admin1 NIR, grouped by the 11 councils (GeoNames admin2 = council GSS code; names from admin2Codes.txt).
    # The official OSNI gazetteer (336 places) refuses downloads from our build machine, so GeoNames is used.
    if ni:
        for x in csv.reader(open(ni, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE):
            if x[10] != 'NIR' or x[6] != 'P' or x[11] not in NI_COUNCILS: continue
            nm = clean(x[1])
            if nm: rows.append((nm, x[7] != 'PPLX', round(float(x[4]), 5), round(float(x[5]), 5), NI_COUNCILS[x[11]], NI_COUNCILS[x[11]], 'Northern Ireland'))
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
    # named places that are only in the list as a parish, Welsh community or neighbourhood ward (e.g. Abinger,
    # Beddgelert, Abbeymead): a page each when no same-name place is within 4 miles. Joined names
    # ('Abbas and Templecombe') are split into their places. Electoral divisions and admin-only ward names
    # ('Aberaman North', 'St Mary's', 'Abbey') are skipped: they are not places people search for.
    # Existing pages never change: a name already listed in the same council area, or within 8 miles, is skipped
    # (otherwise the old page would gain a 'near X' URL). Ward names led by their town ('Falmouth Penwerris')
    # lose the town word first.
    in_area = {(key(p[0]), p[4]) for p in places}
    for r in admin_rows(ipn):
        w = r[0].split()
        for i in range(len(w) - 1, 0, -1):
            if any(miles(r[2], r[3], p[2], p[3]) < 8 for p in bykey.get(key(' '.join(w[:i])), [])):
                r = (' '.join(w[i:]),) + r[1:]; break
        k = key(r[0])
        if len(r[0]) < 3 or r[0].lower() in GENERIC or (k, r[4]) in in_area or any(miles(r[2], r[3], p[2], p[3]) < 8 for p in bykey.get(k, [])): continue
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
    A = [[a[0], aslug[i], a[1], county_pages.get(aslug[i], '') or ('/locations/northern-ireland' if a[1] == 'Northern Ireland' else '')] for i, a in enumerate(areas)]
    def in_ni(u):   # town page whose breadcrumb sits under Northern Ireland
        f = os.path.join(S, u.lstrip('/') + '.html')
        return 1 if os.path.exists(f) and re.search(r'class="breadcrumb"[^\n]*href="/locations/northern-ireland"', open(f, encoding='utf-8').read()) else 0
    LT = [[n, u, la, lo, in_ni(u)] for n, la, lo, u in towns]   # [4] = 1 in Northern Ireland

    data = {'BUILT': BUILT, 'A': A, 'P': out, 'L': links, 'G': G, 'LT': LT}
    import places_fix; places_fix.apply(data, places_fix.load() if os.path.exists(places_fix.DATA) else None); out = data['P']   # tidy names, merge split towns, redirects in R
    os.makedirs(os.path.join(ROOT, 'worker'), exist_ok=True)
    js = '// Generated by tools/places.py - do not edit by hand.\n' + ''.join(
        f'export const {k} = {json.dumps(v, ensure_ascii=False, separators=(",", ":"))};\n' for k, v in data.items())
    open(os.path.join(ROOT, 'worker', 'places-data.js'), 'w', encoding='utf-8').write(js)

    urls = write_sitemaps(A, out)
    print(json.dumps({'places': len(out), 'linked_to_locations': len(links), 'areas': len(A), 'garages': len(G), 'sitemap_urls': len(urls),
                      'data_kb': len(js.encode()) // 1024}))


if __name__ == '__main__':
    sitemaps_only() if sys.argv[1] == '--sitemaps-only' else main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
