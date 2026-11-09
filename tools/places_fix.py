"""Tidy the /places data (worker/places-data.js). Idempotent: running it twice changes nothing.

  python3 tools/places_fix.py      (also called by tools/places.py on every rebuild)

Fixes found in the 9 Nov 2026 glitch scan:
  - names in ONS gazetteer form: 'Cray, St. Mary' -> 'St. Mary Cray', 'Scilly, Isles of' -> 'Isles of Scilly',
    'Corston (Bath and North East Somerset)' -> 'Corston' (the bracket is ONS's own tie-breaker; the page already
    names the area). URLs are unchanged.
  - one built-up area split into pieces, one per council it touches ('Brent' had pages in Barnet, Ealing, Harrow and
    Kensington; 'Hillingdon' in Buckinghamshire and Surrey): one page is kept, the others 301 to it (R below).
  - council names cut off or in list order: 'Bournemouth, Christchurch an', 'Bristol, City of'.
  - garages outside Great Britain (Belfast, Jersey, Isle of Man) are no longer the 'nearest' to a GB place across the sea.
  - Tesla Body Repair Centre Dartford is a bodyshop, not a Service Centre."""
import os, re, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitelib import ROOT, S

SITE = 'https://teslaservice.co.uk'
PART = 10000
DATA = os.path.join(ROOT, 'worker', 'places-data.js')

AREA_NAMES = {'Bournemouth, Christchurch an': 'Bournemouth, Christchurch and Poole', 'Bristol, City of': 'Bristol',
              'Herefordshire, County of': 'Herefordshire', 'Kingston upon Hull, City of': 'Kingston upon Hull'}
# council areas whose county page here has another slug (same area, other name)
COUNTY_PAGES = {'herefordshire-county-of': 'herefordshire', 'isle-of-anglesey': 'anglesey', 'dundee-city': 'dundee',
                'orkney-islands': 'orkney', 'shetland-islands': 'shetland', 'na-h-eileanan-siar': 'western-isles',
                'west-midlands': 'west-midlands-county'}
LEAD = {'st', 'st.', 'saint', 'the', 'upper', 'lower', 'higher', 'high', 'little', 'great', 'north', 'south', 'east',
        'west', 'old', 'new', 'nether', 'over', 'middle', 'isles', 'hill', 'city'}
TAIL_STOP = {'farm', 'street', 'road', 'lane', 'cottages', 'house'}
NON_GB = ('BT', 'JE', 'GY', 'IM')


def tidy(n):
    s = re.sub(r',(?=\S)', ', ', n).strip()
    while True:
        t = re.sub(r'\s*\([^()]*\)$', '', s).strip()
        if t == s or not t: break
        s = t
    m = re.match(r"^([^,()/]+), ([^,()/]+)$", s)
    if m:
        head, tail = m.group(1).strip(), m.group(2).strip()
        w = tail.split()
        if w and len(w) <= 3 and ' and ' not in f' {tail} ' and w[0].lower() in LEAD and w[-1].lower() not in TAIL_STOP:
            s = f'{tail} {head}'
    return s


def miles(a, b, c, d):
    R = math.pi / 180
    x, y = math.sin((c - a) * R / 2), math.sin((d - b) * R / 2)
    return 7917.6 * math.asin(math.sqrt(x * x + math.cos(a * R) * math.cos(c * R) * y * y))


def base(slug):
    return re.sub(r'-near-.*$', '', slug)


def apply(d, old=None):
    """old: the data as committed before a rebuild, so every URL it served keeps working (301 to its new page)."""
    A, P, L, G = d['A'], d['P'], d['L'], d['G']
    R = dict(d.get('R') or {})
    for a in A:
        a[0] = AREA_NAMES.get(a[0], a[0])
        if not a[3] and a[1] in COUNTY_PAGES and os.path.exists(os.path.join(S, 'locations', 'county', COUNTY_PAGES[a[1]] + '.html')):
            a[3] = '/locations/county/' + COUNTY_PAGES[a[1]]
    orig = {id(p): p[0] for p in P}
    for p in P:
        p[0] = tidy(p[0])
        if p[5]: p[5] = tidy(p[5])
    for l in L: l[0] = tidy(l[0])
    url = lambda p: f'/places/{A[p[1]][1]}/{p[4]}'
    # the ONS list often has a place twice, as 'Lower North Dean' and 'Dean, Lower North': once tidied, keep one
    sl = lambda n: re.sub(r'[^a-z0-9]+', '-', n.lower().replace("'", '')).strip('-')
    same, gone = {}, set()
    for i, p in enumerate(P): same.setdefault((p[1], sl(p[0])), []).append(i)
    for (ai, n), ids in same.items():
        if len(ids) < 2: continue
        ids.sort(key=lambda j: (base(P[j][4]) != n, P[j][4]))
        for j in ids[1:]:
            if j in gone: continue
            k = next((x for x in ids if x not in gone and x != j and miles(P[x][2], P[x][3], P[j][2], P[j][3]) <= 3), None)
            if k is not None and ids.index(k) < ids.index(j) and orig[id(P[k])] != orig[id(P[j])]: R[url(P[j])] = url(P[k]); gone.add(j)
    if gone: d['P'] = P = [p for i, p in enumerate(P) if i not in gone]
    # built-up areas split across councils: same name, built-up area, within 8 miles = one place
    groups = {}
    for i, p in enumerate(P):
        if p[6]: groups.setdefault(base(p[4]), []).append(i)
    lgroups = {}
    for l in L: lgroups.setdefault(re.sub(r'[^a-z0-9]+', '-', l[0].lower()).strip('-'), []).append(l)
    grid = {}
    for p in P: grid.setdefault((int(p[2] * 20), int(p[3] * 12)), []).append(p)
    def near_pts(la, lo, r):
        y, x = int(la * 20), int(lo * 12)
        return [q for dy in range(-2, 3) for dx in range(-2, 3) for q in grid.get((y + dy, x + dx), []) if miles(la, lo, q[2], q[3]) <= r]
    drop = set()
    for k, ids in groups.items():
        par = {i: i for i in ids}   # single-linkage clusters (pieces chain across a big built-up area)
        def root(i):
            while par[i] != i: i = par[i]
            return i
        for x in ids:
            for y in ids:
                if x < y and miles(P[x][2], P[x][3], P[y][2], P[y][3]) <= 8: par[root(y)] = root(x)
        cls = {}
        for i in ids: cls.setdefault(root(i), []).append(i)
        for cl in cls.values():
            cov = [l for l in lgroups.get(k, []) if any(miles(l[2], l[3], P[j][2], P[j][3]) <= 8 for j in cl)]
            if cov:   # the town has its own /locations page: every piece goes there
                for j in cl: R[url(P[j])] = cov[0][4]; drop.add(j)
                continue
            if len(cl) < 2: continue
            # the main piece: its council also holds most of the places around the town (fringe pieces sit on a boundary)
            la = sum(P[j][2] for j in cl) / len(cl); lo = sum(P[j][3] for j in cl) / len(cl)
            votes = {}
            for q in near_pts(la, lo, 2.5): votes[q[1]] = votes.get(q[1], 0) + 1
            keep = min(cl, key=lambda j: (k not in A[P[j][1]][1], -votes.get(P[j][1], 0), miles(la, lo, P[j][2], P[j][3])))
            for j in cl:
                if j != keep: R[url(P[j])] = url(P[keep]); drop.add(j)
    if drop: d['P'] = P = [p for i, p in enumerate(P) if i not in drop]
    # a built-up area named after a council ('Tower Hamlets', 'Haringey') belongs in that council, not the one next door
    AS = {a[1]: i for i, a in enumerate(A)}
    cen = {}
    for p in P: c = cen.setdefault(p[1], [0, 0, 0]); c[0] += p[2]; c[1] += p[3]; c[2] += 1
    taken = {(p[1], p[4]) for p in P}
    for p in P:
        ai = AS.get(base(p[4]))
        if not p[6] or ai is None or ai == p[1] or (ai, base(p[4])) in taken: continue
        c = cen[ai]
        if miles(p[2], p[3], c[0] / c[2], c[1] / c[2]) > 6: continue
        old = url(p); taken.discard((p[1], p[4])); p[1], p[4], p[5] = ai, base(p[4]), ''
        taken.add((p[1], p[4])); R[old] = url(p)
        for s_, t_ in R.items():
            if t_ == old: R[s_] = url(p)
    live = {url(p) for p in P}
    if old:   # pages from the previous build that are gone now: 301 to the same place's new page
        oA = old['A']; ourl = lambda p: f'/places/{oA[p[1]][1]}/{p[4]}'
        AS = {a[1]: i for i, a in enumerate(A)}
        bykey = {}
        for p in P: bykey.setdefault(base(p[4]), []).append(p)
        lk = {}
        for l in L: lk.setdefault(re.sub(r'[^a-z0-9]+', '-', l[0].lower()).strip('-'), []).append(l)
        for s_, t_ in (old.get('R') or {}).items(): R.setdefault(s_, t_)
        for p in old['P']:
            u = ourl(p)
            if u in live: continue
            if u in R and (R[u] in live or not R[u].startswith('/places')): continue
            c = sorted((miles(p[2], p[3], q[2], q[3]), url(q)) for q in bykey.get(base(p[4]), []))
            c = [x for x in c if x[0] <= 8]
            lc = [l[4] for l in lk.get(base(p[4]), []) if miles(p[2], p[3], l[2], l[3]) <= 8]
            ai = AS.get(oA[p[1]][1])
            R[u] = c[0][1] if c else lc[0] if lc else (f'/places/{A[ai][1]}' if ai is not None else '/places')
    # redirects must end on a live page (no chains)
    for _ in range(5):
        for s, t in R.items():
            if t in R: R[s] = R[t]
    R = {s: t for s, t in sorted(R.items()) if s not in live}
    d['R'] = R
    d['G'] = [([*g[:1], 'authorised', *g[2:]] if g[1] == 'dealer' and 'Body Repair' in g[0] else g) for g in G if not (g[8] or '')[:2] in NON_GB]
    return d


def load():
    js = open(DATA, encoding='utf-8').read()
    return {m.group(1): json.loads(m.group(2)) for m in re.finditer(r'^export const (\w+) = (.*);$', js, re.M)}


def save(d):
    keys = ['BUILT', 'A', 'P', 'L', 'G', 'LT', 'R']
    js = '// Generated by tools/places.py - do not edit by hand.\n' + ''.join(
        f'export const {k} = {json.dumps(d[k], ensure_ascii=False, separators=(",", ":"))};\n' for k in keys)
    open(DATA, 'w', encoding='utf-8').write(js)
    A, P, BUILT = d['A'], d['P'], d['BUILT']
    urls = [f'{SITE}/places'] + [f'{SITE}/places/{a[1]}' for a in A] + [f'{SITE}/places/{A[p[1]][1]}/{p[4]}' for p in P]
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
    return len(urls)


if __name__ == '__main__':
    d = load(); n0 = len(d['P'])
    apply(d, load()); n = save(d)
    print(json.dumps({'places': len(d['P']), 'merged_or_redirected': n0 - len(d['P']), 'redirects': len(d['R']), 'garages': len(d['G']), 'sitemap_urls': n}))
