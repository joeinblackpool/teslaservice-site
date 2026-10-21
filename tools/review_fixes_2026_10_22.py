"""Fixes from two independent SEO reviews (22 Oct 2026). Idempotent.
1. Remove FAQPage JSON-LD everywhere (visible FAQ text stays). FAQ rich results are retired; on some pages the
   questions weren't visible, which is a structured-data policy risk.
2. HEVRA-listed garages (/hevra/): titles must not claim Tesla servicing (HEVRA accreditation doesn't confirm
   Tesla-specific experience). "<Name> – Tesla & EV servicing in <Town>" -> "<Name> – EV & Hybrid Servicing in <Town>".
   Only zero-click pages (all of these were retitled on 21 Oct, so none had clicks).
3. 21 town/county titles lost "& Repair" on 21 Oct: re-fit "Tesla Service & Repair in X — N Local Garages", falling back
   to shorter forms so the title stays under 575 px.
4. Sitemap <lastmod>: every page whose file changed since the 21 Oct mirror gets today's date."""
import os, re, sys, html, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitelib import px, html_pages, url_of
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site')
TODAY = '2026-10-22'
LD = re.compile(r'<script type="application/ld\+json">([\s\S]*?)</script>\s*', re.S)
def no_faq(text):
    n = 0
    def sub(m):
        nonlocal n
        try: j = json.loads(m.group(1))
        except Exception: return m.group(0)
        if isinstance(j, dict) and j.get('@type') == 'FAQPage': n += 1; return ''
        if isinstance(j, dict) and isinstance(j.get('@graph'), list):
            g = [x for x in j['@graph'] if not (isinstance(x, dict) and x.get('@type') == 'FAQPage')]
            if len(g) != len(j['@graph']):
                n += 1; j['@graph'] = g
                return '<script type="application/ld+json">' + json.dumps(j, ensure_ascii=False, indent=2) + '</script>\n'
        return m.group(0)
    return LD.sub(sub, text), n
def set_title(text, new):
    esc = html.escape(new, quote=False)
    text = re.sub(r'<title>[^<]*</title>', f'<title>{esc}</title>', text, count=1)
    text = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1) + html.escape(new) + m.group(2), text, count=1)
    text = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")', lambda m: m.group(1) + html.escape(new) + m.group(2), text, count=1)
    return text
changed = set(); faq = 0; hevra = 0; towns = 0
# titles retitled on 21 Oct (to know which town titles lost "& Repair")
old_titles = {}
diff = subprocess.run(['git', 'diff', '5ab2707~1', 'HEAD', '--', 'site/locations'], capture_output=True, text=True).stdout
cur = None
for line in diff.splitlines():
    if line.startswith('+++ b/'): cur = line[6:]
    elif line.startswith('-<title>') and cur: old_titles[cur] = html.unescape(re.sub(r'</?title>', '', line[1:]))
for f in html_pages():
    rel = os.path.relpath(f, os.path.join(S, '..'))
    t = open(f, encoding='utf-8').read(); o = t
    t, n = no_faq(t); faq += n
    m = re.search(r'<title>([^<]*)</title>', t); title = html.unescape(m.group(1)) if m else ''
    if '/hevra/' in f and ' – Tesla & EV servicing in ' in title:
        name, town = title.split(' – Tesla & EV servicing in ', 1)
        for cand in [f'{name} – EV & Hybrid Servicing in {town}', f'{name} – EV Specialist in {town}', f'{name} – EV Specialist']:
            if px(cand) < 575: t = set_title(t, cand); hevra += 1; break
    if rel in old_titles and '& Repair' in old_titles[rel] and '& Repair' not in title:
        o_t = old_titles[rel]
        mm = re.match(r'Tesla Service & Repair in (.+?) — (\d+) Local Garages', o_t)
        place = mm.group(1) if mm else re.sub(r'^Tesla Service (& Repair in )?', '', title).split(' — ')[0]
        n_g = mm.group(2) if mm else None
        cands = ([f'Tesla Service & Repair in {place} — {n_g} Garages', f'Tesla Service & Repair {place} — {n_g} Garages'] if n_g else []) + \
                [f'Tesla Service & Repair in {place}', f'Tesla Service & Repair {place}']
        for cand in cands:
            if px(cand) < 575: t = set_title(t, cand); towns += 1; break
    if t != o: open(f, 'w', encoding='utf-8').write(t)
# lastmod for every file changed since the mirror commit (bcb7a53), plus this run's changes
files = subprocess.run(['git', 'diff', '--name-only', 'bcb7a53', '--', 'site'], capture_output=True, text=True).stdout.split()
files += subprocess.run(['git', 'diff', '--name-only', '--', 'site'], capture_output=True, text=True).stdout.split()
urls = {'https://teslaservice.co.uk' + url_of(os.path.join(S, '..', p)) for p in files if p.endswith('.html')}
sm_p = os.path.join(S, 'sitemap.xml'); sm = open(sm_p, encoding='utf-8').read()
def lm(m):
    block = m.group(0); loc = re.search(r'<loc>([^<]+)</loc>', block).group(1)
    if loc in urls or loc.rstrip('/') in urls:
        block = re.sub(r'<lastmod>[^<]*</lastmod>', f'<lastmod>{TODAY}</lastmod>', block) if '<lastmod>' in block else block.replace('</loc>', f'</loc><lastmod>{TODAY}</lastmod>')
    return block
sm2 = re.sub(r'<url>[\s\S]*?</url>', lm, sm); open(sm_p, 'w', encoding='utf-8').write(sm2)
print(json.dumps({'faq_blocks_removed': faq, 'hevra_titles': hevra, 'town_titles_with_repair': towns, 'lastmod_updated': sm2.count(f'<lastmod>{TODAY}</lastmod>')}))
