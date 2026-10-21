"""Mirror the live static site (Cloudflare Workers static assets, html_handling=auto-trailing-slash) into site/.
URL /a/b -> site/a/b.html ; /a/b/ -> site/a/b/index.html ; / -> site/index.html. Also fetches every local
asset referenced by the pages, plus robots.txt, sitemap.xml, llms*.txt and the 404 page."""
import re, os, sys, json, urllib.request, urllib.parse, concurrent.futures as cf
BASE = 'https://teslaservice.co.uk'
OUT = 'site'
UA = {'User-Agent': 'Mozilla/5.0 (compatible; TeslaServiceMirror/1.0; +https://github.com/joeinblackpool/teslaservice-site)'}
def get(path):
    req = urllib.request.Request(BASE + path, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.geturl(), r.read()
    except urllib.error.HTTPError as e:
        return e.code, BASE + path, e.read()
def fpath(path):
    p = urllib.parse.unquote(path.split('?')[0].split('#')[0])
    if p == '/' or p == '': return os.path.join(OUT, 'index.html')
    if p.endswith('/'): return os.path.join(OUT, p.strip('/'), 'index.html')
    if re.search(r'\.[A-Za-z0-9]{1,5}$', p.rsplit('/', 1)[-1]): return os.path.join(OUT, p.lstrip('/'))
    return os.path.join(OUT, p.lstrip('/') + '.html')
def save(path, body):
    f = fpath(path); os.makedirs(os.path.dirname(f), exist_ok=True); open(f, 'wb').write(body)
log = {'pages': 0, 'assets': 0, 'errors': [], 'redirected': []}
st, _, sm = get('/sitemap.xml')
urls = re.findall(rb'<loc>([^<]+)</loc>', sm)
paths = sorted({urllib.parse.urlparse(u.decode()).path or '/' for u in urls})
for extra in ['/', '/robots.txt', '/sitemap.xml', '/llms.txt', '/llms-full.txt', '/favicon.svg', '/favicon.ico', '/og-image.png', '/og-image-v2.png', '/manifest.webmanifest', '/site.webmanifest', '/BingSiteAuth.xml', '/apple-touch-icon.png', '/suggest.html', '/404.html']:
    if extra not in paths: paths.append(extra)
assets = set()
RED = set()
if os.path.exists(os.path.join(OUT, '_redirects')):
    for line in open(os.path.join(OUT, '_redirects'), encoding='utf-8'):
        q = line.split('#')[0].split()
        if len(q) >= 2: RED.add(q[0])
def page(p):
    s, final, b = get(p)
    fin = urllib.parse.urlparse(final).path
    if s != 200: return p, s, None
    if fin != p: log['redirected'].append([p, fin])
    save(fin, b)
    if fin.endswith('.html') or not re.search(r'\.[a-z0-9]{1,5}$', fin):
        for m in re.findall(rb'<a [^>]*href="(/[^"#?]*)', b):
            l = m.decode()
            if not re.search(r'\.[A-Za-z0-9]{1,5}$', l): links.add(l)
        for m in re.findall(rb'(?:href|src|content)="(/[^"#?]+)', b):
            a = m.decode()
            if re.search(r'\.(css|js|mjs|png|jpe?g|webp|svg|ico|gif|avif|woff2?|ttf|json|webmanifest|xml|txt|pdf)$', a, re.I): assets.add(a)
    return p, s, fin
links = set()
OPTIONAL = ('/favicon.ico', '/manifest.webmanifest', '/site.webmanifest', '/BingSiteAuth.xml', '/apple-touch-icon.png', '/404.html', '/suggest.html', '/llms-full.txt', '/og-image-v2.png')
done = set(); batch = list(paths)
while batch:
    with cf.ThreadPoolExecutor(12) as ex:
        for p, s, fin in ex.map(page, batch):
            done.add(p)
            if s == 200: log['pages'] += 1
            elif p not in OPTIONAL: log['errors'].append([p, s])
    batch = sorted(l for l in links if l not in done and l not in RED)
    log.setdefault('found_by_links', 0); log['found_by_links'] += len(batch)
def asset(a):
    s, final, b = get(a)
    if s == 200: save(urllib.parse.urlparse(final).path, b); return 1
    log['errors'].append([a, s]); return 0
with cf.ThreadPoolExecutor(12) as ex:
    log['assets'] = sum(ex.map(asset, sorted(assets)))
s, _, b = get('/this-page-does-not-exist-mirror-check')
open(os.path.join(OUT, '404.html'), 'wb').write(b); log['404_status'] = s
json.dump(log, open('tools/mirror_log.json', 'w'), indent=1)
print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in log.items()}))
