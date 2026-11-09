"""Additive links from the static pages into /places (so Google finds the place pages from pages it already crawls).
Idempotent: each block sits between <!--places-links:start--> and <!--places-links:end--> and is replaced on re-run.

  python3 tools/places_links.py      (run after tools/places.py)

- /locations/ index: one line linking the /places hub.
- /locations/county/<x>: one link to the matching /places/<area> page.
- /locations/<town>: 'Tesla repair near villages around <town>': the 10 nearest indexable (built-up area) place pages + the area page.
Nothing outside the markers changes; titles, H1s and existing text stay as they are."""
import os, re, sys, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitelib import ROOT, S, ts_places, miles

START, END = '<!--places-links:start-->', '<!--places-links:end-->'
esc = lambda s: html.escape(str(s), quote=True)
fmt = lambda d: f'{d:.1f} mi' if d < 9.95 else f'{d:.0f} mi'


def load():
    js = open(os.path.join(ROOT, 'worker', 'places-data.js'), encoding='utf-8').read()
    return {m.group(1): json.loads(m.group(2)) for m in re.finditer(r'^export const (\w+) = (.*);$', js, re.M)}


def put(text, block, anchor_re, after=False):
    full = START + '\n' + block + '\n' + END
    m = re.search(re.escape(START) + r'[\s\S]*?' + re.escape(END), text)
    if m: return text[:m.start()] + full + text[m.end():]
    a = re.search(anchor_re, text)
    if not a: return None
    pos = a.end() if after else a.start()
    return text[:pos] + full + '\n' + text[pos:]


def main():
    D = load(); A, P = D['A'], D['P']
    url = lambda p: f'/places/{A[p[1]][1]}/{p[4]}'
    name = lambda p: f'{p[0]} (near {p[5]})' if p[5] else p[0]
    changed = 0

    def write(f, new):
        nonlocal changed
        old = open(f, encoding='utf-8').read()
        if new and new != old: open(f, 'w', encoding='utf-8').write(new); changed += 1

    # hub link on /locations/
    f = os.path.join(S, 'locations', 'index.html'); t = open(f, encoding='utf-8').read()
    total = len(P) + len(D['L'])
    write(f, put(t, f'  <p class="note" style="margin-bottom:12px">Smaller town or village? See <a href="/places" style="color:var(--accent);">Tesla repair near every town and village in Great Britain</a>: the nearest Tesla Service Centre, EV specialists and garages for {total:,} places.</p>',
                 r'  <div class="note">⚠ Don'))
    # county pages
    by_county = {a[3]: i for i, a in enumerate(A) if a[3]}
    cnt = {}
    for p in P: cnt[p[1]] = cnt.get(p[1], 0) + 1
    tsp, seen = [], set()
    for x in ts_places():
        if x[3] not in seen: seen.add(x[3]); tsp.append(x)
    for n, la, lo, u in tsp:
        if '/county/' not in u: continue
        f = os.path.join(S, u.lstrip('/') + '.html')
        if not os.path.exists(f): continue
        if u in by_county: ais = [by_county[u]]
        else:   # county page with no same-name area (e.g. Bedfordshire -> Bedford, Central Bedfordshire): areas of the places nearest its centre
            ais = []
            for d, k in sorted((miles(la, lo, p[2], p[3]), k) for k, p in enumerate(P) if abs(p[2] - la) < 0.4 and abs(p[3] - lo) < 0.6)[:60]:
                if P[k][1] not in ais: ais.append(P[k][1])
            ais = ais[:3]
        if not ais: continue
        t = open(f, encoding='utf-8').read()
        write(f, put(t, '  <p class="more-region">' + '<br>'.join(f'<a href="/places/{A[ai][1]}">Tesla repair near every town and village in {esc(A[ai][0])} ({cnt[ai]:,} places) →</a>' for ai in ais) + '</p>',
                     r'</main>'))
    # town pages
    for n, la, lo, u in tsp:
        if '/county/' in u: continue
        f = os.path.join(S, u.lstrip('/') + '.html')
        if not os.path.exists(f): continue
        near = sorted((miles(la, lo, p[2], p[3]), k) for k, p in enumerate(P) if p[6] and abs(p[2] - la) < 0.25 and abs(p[3] - lo) < 0.4)   # indexable (built-up area) pages only
        near = [(d, k) for d, k in near if d > 0.3][:10]
        if not near: continue
        areas = []
        for d, k in near:
            if P[k][1] not in areas: areas.append(P[k][1])
        block = (f'  <h2>Tesla repair near villages around {esc(n)}</h2><p class="nearby-towns">'
                 + ' · '.join(f'<a href="{url(P[k])}">{esc(name(P[k]))}</a> <span>({fmt(d)})</span>' for d, k in near) + '</p>'
                 + '<p class="more-region">' + '<br>'.join(f'<a href="/places/{A[ai][1]}">Tesla repair near every place in {esc(A[ai][0])} →</a>' for ai in areas[:2]) + '</p>')
        t = open(f, encoding='utf-8').read()
        write(f, put(t, block, r'  <p class="more-region">'))
    print('pages changed', changed)


if __name__ == '__main__':
    main()
