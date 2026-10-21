"""Shorten <title> (and og:title) to under 575 px on pages with ZERO Search Console clicks in 90 days.
Pages with clicks are never touched (needs the private Search Console file; refuses to run without it).
Keeps the main keyword first. Usage: python3 tools/retitle.py [--max N] [--dry]"""
import os, re, sys, html, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitelib import html_pages, url_of, page_meta, px, clicked_files, garages

LIMIT = 570          # a little under 575 px for safety
MANUAL = {
    '/known-issues-by-model': 'Tesla Known Issues by Model: What UK Owners Report',
    '/owner-stories': 'Tesla Owner Stories UK — Real Experiences from Owners',
    '/owner-tips': 'Tesla Owner Tips UK — Depreciation, Reliability & Winter',
    '/tesla-suspension-noise': 'Tesla Suspension Creak or Knock: Causes & Fixes',
    '/windscreen-camera-calibration': 'Tesla Windscreen Replacement & Camera Calibration UK',
}
TYPE = {
    'dealer': ['– Official Tesla Service Centre', '– Tesla Service Centre', ''],
    'authorised': ['– Tesla-approved bodyshop, {town}', '– Tesla-approved bodyshop', '– Tesla bodyshop', ''],
    'hevra': ['– Tesla & EV servicing in {town}', '– Tesla & EV servicing, {town}', '– Tesla & EV servicing', '– EV specialist', ''],
    'other': ['– Tesla servicing in {town}', '– Tesla servicing, {town}', '– Tesla servicing', ''],
    'parts': ['– Tesla parts & cosmetic, {town}', '– Tesla parts & cosmetic', '– Tesla parts', ''],
}


def place_candidates(t):
    c = []
    a = t.replace('Tesla Service & Repair in ', 'Tesla Service ').replace('Tesla Approved Bodyshop near ', 'Tesla Approved Bodyshop ')
    c.append(a)
    for old, new in [(' — Nearest Garages & Specialists', ' — Garages & Specialists'), (' — Nearest Garages & Specialists', ' — Nearest Garages'),
                     (' — Nearest Repairers', ' — Repairers'), (' Approved Repairers', ' Repairers'), (' Approved Repairer', ' Repairer'),
                     (' — Nearest Options', ''), (' Garages & EV Specialists', ' Garages & Specialists'), (' Garages Listed', ' Garages')]:
        if old in a: c.append(a.replace(old, new))
    c.append(re.sub(r'\s+\(.*?\)', '', a))
    c.append(a.split(' — ')[0])
    return c


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--max', type=int); ap.add_argument('--dry', action='store_true'); a = ap.parse_args()
    clicked = clicked_files()
    if clicked is None: sys.exit('private Search Console file missing: refusing to retitle')
    G = {g['url']: g for g in garages()}
    pages = html_pages(); texts = {f: open(f, encoding='utf-8').read() for f in pages}
    taken = {page_meta(t)['title'] for t in texts.values()}
    n = 0
    for f in pages:
        if a.max is not None and n >= a.max: break
        if f in clicked: continue
        t = texts[f]; m = page_meta(t); u = url_of(f)
        if not m['title'] or px(m['title']) < 575: continue
        sec = u.split('/')[1] if u.count('/') > 1 else ''
        if u in MANUAL: cands = [MANUAL[u]]
        elif sec in TYPE:
            name = m['h1'][0]
            town = re.split(r'[,(–—]', (G.get(u) or {}).get('town', '') or '')[0].strip()
            if re.match(r'(?i)(see |nationwide|uk-wide|online|mobile|various)', town): town = ''
            cands = []
            for suf in TYPE[sec]:
                if '{town}' in suf and (not town or town.lower() in name.lower()): continue
                cands.append((name + ' ' + suf.format(town=town)).strip())
        else: cands = place_candidates(m['title'])
        new = next((c for c in cands if px(c) < LIMIT and c not in taken), None)
        if not new: print('no fit:', u, m['title']); continue
        taken.discard(m['title']); taken.add(new); n += 1
        if a.dry: print(f'{px(m["title"]):.0f}->{px(new):.0f} {u}: {new}'); continue
        e = html.escape(new, quote=False).replace('"', '&quot;')
        t2 = re.sub(r'<title>[\s\S]*?</title>', lambda _: f'<title>{html.escape(new, quote=False)}</title>', t, count=1)
        t2 = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda mm: mm.group(1) + e + mm.group(2), t2, count=1)
        open(f, 'w', encoding='utf-8').write(t2)
    print('retitled', n)


if __name__ == '__main__':
    main()
