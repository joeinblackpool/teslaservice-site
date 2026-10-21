"""Local check of site/ as Cloudflare would serve it (static assets, html_handling auto-trailing-slash,
not_found 404-page, _redirects). Crawls the sitemap + every internal link: must report bad 0.
Usage: python3 tools/check.py   (exit 1 on any problem)"""
import os, re, sys, json, html, urllib.parse
from html.parser import HTMLParser
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site')
RED = {}; seen_dynamic = False; static_after_dynamic = []
for line in open(os.path.join(S, '_redirects'), encoding='utf-8'):
    p = line.split('#')[0].split()
    if len(p) >= 2:
        RED[p[0]] = (p[1], int(p[2]) if len(p) > 2 else 302)
        dyn = '*' in p[0] or ':' in p[0]
        if dyn: seen_dynamic = True
        elif seen_dynamic: static_after_dynamic.append(p[0])   # Cloudflare rejects the deploy: static rules must come first
def resolve(path):
    """Return (status, location_or_file)."""
    if path in RED: return RED[path]
    p = urllib.parse.unquote(path)
    f = os.path.join(S, p.lstrip('/'))
    if p.endswith('/'):
        if os.path.isfile(os.path.join(f, 'index.html')): return 200, os.path.join(f, 'index.html')
        if os.path.isfile(f.rstrip('/') + '.html'): return 307, p.rstrip('/')   # auto-trailing-slash drops the slash
    else:
        if os.path.isfile(f) and not p.endswith('.html'): return 200, f
        if os.path.isfile(f + '.html'): return 200, f + '.html'
        if os.path.isfile(os.path.join(f, 'index.html')): return 307, p + '/'
        if p.endswith('.html') and os.path.isfile(f): return 307, p[:-5] if not p.endswith('/index.html') else p[:-10]
    return 404, None
class A(HTMLParser):
    def __init__(s): super().__init__(); s.links = []; s.title = ''; s._t = False; s.h1 = 0; s.canon = None; s.robots = ''
    def handle_starttag(s, t, a):
        a = dict(a)
        if t == 'a' and a.get('href', '').startswith('/') and not a['href'].startswith('//'): s.links.append(a['href'].split('#')[0].split('?')[0])
        if t == 'title': s._t = True
        if t == 'h1': s.h1 += 1
        if t == 'link' and a.get('rel') == 'canonical': s.canon = a.get('href')
        if t == 'meta' and a.get('name') == 'robots': s.robots = a.get('content', '')
    def handle_endtag(s, t):
        if t == 'title': s._t = False
    def handle_data(s, d):
        if s._t: s.title += d
sm = open(os.path.join(S, 'sitemap.xml'), encoding='utf-8').read()
todo = [urllib.parse.urlparse(u).path for u in re.findall(r'<loc>([^<]+)</loc>', sm)]
smset = set(todo); seen = {}; bad = []; titles = {}; redir_links = []; noindex_in_sm = []; ld_bad = []
while todo:
    p = todo.pop()
    if p in seen or not p: continue
    st, x = resolve(p); seen[p] = st
    if st != 200:
        (bad if st == 404 else redir_links).append([p, st, x]); continue
    if not x.endswith('.html'): continue
    b = open(x, encoding='utf-8', errors='replace').read(); a = A(); a.feed(b)
    if p in smset:
        titles.setdefault(html.unescape(a.title.strip()), []).append(p)
        if 'noindex' in a.robots: noindex_in_sm.append(p)
    for m in re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>', b):
        try: json.loads(m)
        except Exception: ld_bad.append(p)
    todo.extend(l for l in a.links if l not in seen)
dup = {t: v for t, v in titles.items() if len(v) > 1}
redir_targets_bad = [[k, v[0]] for k, v in RED.items() if v[0].startswith('/') and resolve(v[0])[0] == 404]
internal_redirect_links = [r for r in redir_links if r[0] not in smset]
out = {'sitemap': len(smset), 'pages_checked': sum(1 for v in seen.values() if v == 200), 'broken_links': len(bad),
       'links_to_redirects': len(internal_redirect_links), 'dup_titles': len(dup), 'noindex_in_sitemap': len(noindex_in_sm),
       'bad_jsonld': len(ld_bad), 'redirects': len(RED), 'redirect_targets_404': len(redir_targets_bad), 'static_after_dynamic': len(static_after_dynamic)}
print(json.dumps(out))
for name, v in [('broken', bad[:10]), ('links_to_redirects', internal_redirect_links[:10]), ('dup', list(dup.items())[:5]), ('redirect_targets_404', redir_targets_bad[:10]), ('static_after_dynamic', static_after_dynamic[:10])]:
    if v: print(name, v)
sys.exit(1 if (bad or dup or ld_bad or noindex_in_sm or redir_targets_bad or static_after_dynamic) else 0)
