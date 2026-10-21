"""Additive, data-built sections for teslaservice.co.uk pages. Idempotent: each block sits between
marker comments and is replaced on re-run; nothing outside the markers is changed (except one
<style id="enrich-css"> tag added to <head>).

  python3 tools/enrich.py garages [--max N] [--refresh]   "Charging near <garage>" on /dealer|authorised|hevra|other|parts/ pages
  python3 tools/enrich.py towns   [--max N] [--refresh]   "Tesla servicing in <town> at a glance" on /locations/<town> and county pages
  --max N    only add the block to N pages that don't have it yet (deploy batches); --refresh also rewrites existing blocks
  --urls F   write every teslachargers.co.uk URL used to file F (to verify them against the charger site's worker)

Charger data: teslachargers.co.uk source data.json (Open Charge Map contributors, CC BY-SA 4.0, and Tesla's UK site list)."""
import os, re, sys, json, html, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitelib import S, html_pages, url_of, garages, ts_places, miles, Chargers, strip_tags

TCS = 'https://teslachargers.co.uk'
CREDIT = ('Charger data: <a href="https://openchargemap.org/" rel="noopener">Open Charge Map</a> '
          '(<a href="https://creativecommons.org/licenses/by-sa/4.0/" rel="noopener">CC BY-SA 4.0</a>) and Tesla, '
          'via <a href="https://teslachargers.co.uk/">TeslaChargers.co.uk</a>. Straight-line distances; check live availability in your Tesla app before you set off.')
CSS = ('<style id="enrich-css">.charging h3,.glance h3{font-size:14.5px;margin:14px 0 6px;color:var(--ink-dim);font-weight:600}'
       '.glance{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:16px 20px;margin:0 0 26px}'
       '.glance h2{font-size:17px;margin:0 0 10px}.glance ul{margin:0 0 10px;padding-left:18px;font-size:14.5px}.glance li{margin:3px 0}'
       '.glance a,.charging p a{color:var(--accent)}.enrich-src{font-size:12.5px;color:var(--ink-dim)}.enrich-src a{color:var(--ink-dim)!important}</style>')
PRIVATE_ACCESS = {2, 5, 7}      # D.A: Private - staff/customers, Private - restricted, Privately owned
DOWN_STATUS = {2, 4}            # D.S: Not Operational, Temporarily Unavailable
esc = lambda s: html.escape(str(s), quote=True)
fmt = lambda d: '&lt;0.1 mi' if d < 0.05 else f'{d:.1f} mi' if d < 9.95 else f'{d:.0f} mi'

C = Chargers()
R = C.R
SUPER = [i for i, r in enumerate(R) if C.type(i) == 'Tesla Supercharger' and i not in C.DUP and r[13] not in DOWN_STATUS]
RAPID = [i for i, r in enumerate(R) if C.type(i) == 'Other network' and r[14] == 1 and i not in C.DUP
         and r[13] not in DOWN_STATUS and r[12] not in PRIVATE_ACCESS and (r[15] or 0) >= 50]
OPS = C.D['O']
CENT = {}
for ti, rows in enumerate(C.townRows):
    if rows and C.town_ok(ti):
        CENT[ti] = (sum(R[i][5] for i in rows) / len(rows), sum(R[i][6] for i in rows) / len(rows))
USED = set()


def nearest(lst, lat, lon, n, maxd):
    out = sorted((miles(lat, lon, R[i][5], R[i][6]), i) for i in lst)
    return [(d, i) for d, i in out[:n] if d <= maxd]


def charger_town(name, lat, lon):
    """teslachargers town page for this place: same-name town nearest to the point, else town of the nearest charger."""
    key = re.sub(r'\s*\(.*\)|,.*', '', name or '').strip().lower()
    best = None
    for ti, (a, b) in CENT.items():
        if C.TO[ti][0].lower() == key:
            d = miles(lat, lon, a, b)
            if d <= 15 and (best is None or d < best[0]): best = (d, ti)
    if best: return best[1]
    for d, i in sorted((miles(lat, lon, r[5], r[6]), i) for i, r in enumerate(R) if i not in C.DUP and abs(r[5] - lat) < .2 and abs(r[6] - lon) < .3):
        if d > 6: break
        if R[i][3] in CENT: return R[i][3]
    return None


def link(i, label):
    u = C.charger_url(i)
    if not u: return esc(label)
    USED.add(u); return f'<a href="{u}" rel="noopener">{esc(label)}</a>'


def town_link(ti, label=None):
    u = TCS + C.town_path(ti); USED.add(u)
    return f'<a href="{u}" rel="noopener">{label or "Tesla chargers in " + esc(C.TO[ti][0])} →</a>'


def put(text, start, end, block, anchor_re, before=True):
    """Replace the marked block, or insert it at the anchor. Returns new text or None if no anchor."""
    m = re.search(re.escape(start) + r'[\s\S]*?' + re.escape(end), text)
    full = start + '\n' + block + '\n' + end
    if m: return text[:m.start()] + full + text[m.end():]
    a = re.search(anchor_re, text)
    if not a: return None
    pos = a.start() if before else a.end()
    return text[:pos] + '\n  ' + full + text[pos:]


def add_css(text):
    if 'id="enrich-css"' in text: return re.sub(r'<style id="enrich-css">[\s\S]*?</style>', lambda _: CSS, text)
    return text.replace('</head>', CSS + '\n</head>', 1)


# ---------------- garages ----------------
def garage_block(name, lat, lon, pc, town):
    sc = nearest(SUPER, lat, lon, 3, 60)
    rp = nearest(RAPID, lat, lon, 3, 15)
    if not sc and not rp: return None
    h = [f'<section class="nearby charging" id="charging">', f'  <h2>Charging near {esc(name)}</h2>',
         f'  <p style="font-size:14px;color:var(--ink-dim);margin:0 0 6px;">Public chargers closest to {esc(name)}{" (" + esc(pc) + ")" if pc else ""}, handy if you wait for your car or need charge after the visit.</p>']
    if sc:
        h.append('  <h3>Nearest Tesla Superchargers</h3><ul>')
        for d, i in sc:
            r = R[i]; bits = [f'{r[16]} stalls' if r[16] else '', f'up to {r[15]:g} kW' if r[15] else '']
            h.append(f'<li>{link(i, r[1])} <span>— {esc(", ".join(b for b in bits if b))}{" · " if any(bits) else ""}{fmt(d)}</span></li>')
        h.append('</ul>')
    if rp:
        h.append('  <h3>Nearest other rapid chargers (50 kW+)</h3><ul>')
        for d, i in rp:
            r = R[i]; op = OPS[r[10]] if isinstance(r[10], int) and r[10] < len(OPS) else ''
            bits = [op, f'{r[15]:g} kW' if r[15] else '']
            h.append(f'<li>{link(i, r[1])} <span>— {esc(", ".join(b for b in bits if b))} · {fmt(d)}</span></li>')
        h.append('</ul>')
    ti = charger_town(town, lat, lon)
    if ti is not None: h.append(f'  <p>{town_link(ti)}</p>')
    h.append(f'  <p class="enrich-src">{CREDIT}</p>')
    h.append('</section>')
    return '\n'.join(h)


def do_garages(maxn, refresh):
    G = {g['url']: g for g in garages()}
    n = changed = 0
    for f in html_pages():
        u = url_of(f)
        if not re.match(r'^/(dealer|authorised|hevra|other|parts)/', u): continue
        t = open(f, encoding='utf-8').read(); has = '<!--enrich:start-->' in t
        if has and not refresh: continue
        if not has and maxn is not None and n >= maxn: continue
        g = G.get(u, {}); lat, lon = g.get('lat'), g.get('lon')
        if lat is None:
            m = re.search(r'"latitude":\s*(-?[\d.]+),\s*"longitude":\s*(-?[\d.]+)', t)
            if m: lat, lon = float(m.group(1)), float(m.group(2))
        if lat is None: continue
        name = strip_tags(re.search(r'<h1[^>]*>([\s\S]*?)</h1>', t).group(1))
        b = garage_block(name, lat, lon, g.get('pc', ''), g.get('town', ''))
        if not b: continue
        new = put(t, '<!--enrich:start-->', '<!--enrich:end-->', b, r'\n\s*<p class="source-note">')
        if new is None: continue
        new = add_css(new)
        if not has: n += 1
        if new != t: open(f, 'w', encoding='utf-8').write(new); changed += 1
    print(f'garages: {n} new blocks, {changed} files changed')


# ---------------- towns / counties ----------------
SECT = [('hevra', 'HEVRA-accredited EV specialists'), ('other', 'Other independent Tesla garages'),
        ('authorised', 'Tesla-approved body repair'), ('parts', 'Parts, accessories &amp; cosmetic')]


def sections(t):
    """Listing counts per section id, and the first dealer listing (name, href, distance text)."""
    parts = re.split(r'<h2 id="([a-z]+)"', t); counts = {}; dealer = None
    for k in range(1, len(parts) - 1, 2):
        sid, body = parts[k], parts[k + 1].split('<h2', 1)[0]
        counts[sid] = len(re.findall(r'<div class="listing">', body))
        if sid == 'dealer':
            m = re.search(r'<h3><a href="(/dealer/[^"]+)">([^<]+)</a></h3>[\s\S]*?<div class="dist">([\d.]+) miles', body)
            if m: dealer = (m.group(2), m.group(1), float(m.group(3)))
    return counts, dealer


def county_chargers(place):
    ci = next((k for k, c in enumerate(C.CO) if c[0].lower() == place.lower()), None)
    if ci is None: return None, []
    sc = [i for i in SUPER if C.TO[R[i][3]][1] == ci]
    has_towns = any(C.town_ok(ti) for ti, tt in enumerate(C.TO) if tt[1] == ci)
    return (TCS + f'/{C.NA[C.CO[ci][1]][1]}/{C.CO[ci][2]}/' if has_towns else None), sc


def glance_block(place, t, lat, lon, county_link, is_county=False):
    counts, dealer = sections(t)
    li = []
    if dealer and is_county:
        li.append(f'<li>Nearest official Tesla Service Centre: <a href="{dealer[1]}">{dealer[0]}</a></li>')
    elif dealer:
        li.append(f'<li>Nearest official Tesla Service Centre: <a href="{dealer[1]}">{dealer[0]}</a>, {dealer[2]:g} miles</li>')
    for sid, label in SECT:
        if sid in counts: li.append(f'<li>{label} listed: {counts[sid]}</li>')
    cu = None
    if is_county:
        cu, csc = county_chargers(place)
        if csc:
            names = ', '.join(link(i, R[i][1]) for i in sorted(csc, key=lambda i: R[i][1])[:6])
            li.append(f'<li>Tesla Superchargers in {esc(place)}: {len(csc)} ({names}{", …" if len(csc) > 6 else ""})</li>')
        elif cu:
            li.append(f'<li>Tesla Superchargers in {esc(place)}: none listed</li>')
    elif lat is not None:
        sc = nearest(SUPER, lat, lon, 50, 10)
        if sc:
            d, i = sc[0]
            li.append(f'<li>Tesla Superchargers within 10 miles: {len(sc)} (nearest: {link(i, R[i][1])}, {fmt(d)})</li>')
        else:
            near = nearest(SUPER, lat, lon, 1, 200)
            if near: li.append(f'<li>Nearest Tesla Supercharger: {link(near[0][1], R[near[0][1]][1])}, {fmt(near[0][0])}</li>')
    if len(li) < 2: return None
    h = ['<section class="glance" id="at-a-glance">', f'  <h2>Tesla servicing in {esc(place)} at a glance</h2>', '  <ul>' + ''.join(li) + '</ul>']
    links = []
    if cu:
        USED.add(cu); links.append(f'<a href="{cu}" rel="noopener">Tesla chargers in {esc(place)} →</a>')
    elif lat is not None and not is_county:
        ti = charger_town(place, lat, lon)
        if ti is not None: links.append(town_link(ti, 'Tesla chargers in ' + esc(place) if C.TO[ti][0].lower() == place.lower() else 'Tesla chargers near ' + esc(place) + ' (' + esc(C.TO[ti][0]) + ')'))
    if county_link: links.append(county_link)
    if links: h.append('  <p>' + '<br>'.join(links) + '</p>')
    h.append(f'  <p class="enrich-src">Counts are the listings on this page. {CREDIT if (lat is not None or cu) else ""}</p>')
    h.append('</section>')
    return '\n'.join(h)


REGIONS = {'east-midlands', 'east-of-england', 'greater-london', 'london', 'north-east', 'north-west', 'northern-ireland', 'scotland',
           'south-east', 'south-west', 'wales', 'west-midlands', 'yorkshire-and-humber', 'index'}


def do_towns(maxn, refresh):
    P = {p[3]: (p[1], p[2]) for p in ts_places()}
    n = changed = 0
    for f in html_pages():
        u = url_of(f)
        if not re.match(r'^/locations/(county/)?[^/]+$', u): continue
        t = open(f, encoding='utf-8').read()
        crumbs = re.search(r'<p class="breadcrumb">([\s\S]*?)</p>', t)
        if not crumbs: continue
        is_county = u.startswith('/locations/county/')
        cl = re.findall(r'<a href="(/locations/county/[^"]+)">([^<]+)</a>', crumbs.group(1))
        if not is_county and u.rsplit('/', 1)[-1] in REGIONS: continue
        has = '<!--enrich-glance:start-->' in t
        if has and not refresh: continue
        if not has and maxn is not None and n >= maxn: continue
        place = strip_tags(crumbs.group(1).rsplit('/', 1)[-1])
        lat, lon = P.get(u, (None, None))
        county_link = None
        if not is_county and cl:
            county_link = f'<a href="{cl[-1][0]}">Tesla service across {cl[-1][1]} →</a>'
        b = glance_block(place, t, lat, lon, county_link, is_county)
        if not b: continue
        new = put(t, '<!--enrich-glance:start-->', '<!--enrich-glance:end-->', b, r'\n\s*<h2>Nearby towns</h2>|\n\s*<p class="more-region">|\n</main>')
        if new is None: continue
        new = add_css(new)
        if not has: n += 1
        if new != t: open(f, 'w', encoding='utf-8').write(new); changed += 1
    print(f'towns: {n} new blocks, {changed} files changed')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('what', choices=['garages', 'towns'])
    ap.add_argument('--max', type=int); ap.add_argument('--refresh', action='store_true'); ap.add_argument('--urls')
    a = ap.parse_args()
    (do_garages if a.what == 'garages' else do_towns)(a.max, a.refresh)
    if a.urls: open(a.urls, 'w').write('\n'.join(sorted(USED)) + '\n')
