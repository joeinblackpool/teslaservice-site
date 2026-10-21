"""Shared helpers for teslaservice.co.uk tools: page inventory, titles/H1s, pixel widths,
Search Console clicks (private file, never committed), garage data and teslachargers data."""
import os, re, json, html, math, unicodedata, urllib.parse

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
S = os.path.join(ROOT, 'site')
PRIVATE = os.environ.get('TS_PRIVATE', '/home/claude/teslaservice-private')
TC = os.environ.get('TC_SOURCE', '/home/claude/teslachargers-site/source/tc')


def load_redirects():
    red = {}
    for line in open(os.path.join(S, '_redirects'), encoding='utf-8'):
        p = line.split('#')[0].split()
        if len(p) >= 2:
            red[p[0]] = (p[1], int(p[2]) if len(p) > 2 else 302)
    return red


def resolve(path, red=None):
    """(status, file_or_location) as Cloudflare static assets would serve it."""
    red = load_redirects() if red is None else red
    if path in red:
        return red[path][1], red[path][0]
    p = urllib.parse.unquote(path)
    f = os.path.join(S, p.lstrip('/'))
    if p.endswith('/'):
        if os.path.isfile(os.path.join(f, 'index.html')): return 200, os.path.join(f, 'index.html')
        if os.path.isfile(f.rstrip('/') + '.html'): return 307, p.rstrip('/')
    else:
        if os.path.isfile(f) and not p.endswith('.html'): return 200, f
        if os.path.isfile(f + '.html'): return 200, f + '.html'
        if os.path.isfile(os.path.join(f, 'index.html')): return 307, p + '/'
    return 404, None


def final(path, red=None, hops=5):
    """Follow redirects; return (status_of_last, file, final_path)."""
    red = load_redirects() if red is None else red
    for _ in range(hops):
        st, x = resolve(path, red)
        if st == 200: return 200, x, path
        if st == 404: return 404, None, path
        path = x
    return 0, None, path


def url_of(fpath):
    rel = os.path.relpath(fpath, S).replace(os.sep, '/')
    if rel == 'index.html': return '/'
    if rel.endswith('/index.html'): return '/' + rel[:-10]
    return '/' + rel[:-5]


def html_pages():
    out = []
    for d, _, fs in os.walk(S):
        for f in fs:
            if f.endswith('.html'):
                out.append(os.path.join(d, f))
    return sorted(out)


TITLE_RE = re.compile(r'<title>([\s\S]*?)</title>')
H1_RE = re.compile(r'<h1[^>]*>([\s\S]*?)</h1>')
DESC_RE = re.compile(r'<meta name="description" content="([^"]*)"')


def strip_tags(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()


def page_meta(text):
    t = TITLE_RE.search(text); d = DESC_RE.search(text)
    return {'title': html.unescape(t.group(1).strip()) if t else '',
            'h1': [strip_tags(h) for h in H1_RE.findall(text)],
            'desc': html.unescape(d.group(1)) if d else None}


def main_words(text):
    m = re.search(r'<main[^>]*>([\s\S]*?)</main>', text)
    body = m.group(1) if m else text
    body = re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', body)
    return len(re.findall(r"[A-Za-z0-9£'’-]+", strip_tags(re.sub(r'<[^>]+>', ' ', body))))


# ---------- pixel width (Liberation Sans = Arial metrics) ----------
_FONT = None
def px(s, size=20):
    global _FONT
    if _FONT is None:
        from PIL import ImageFont
        _FONT = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', size)
    return _FONT.getlength(s)


# ---------- Search Console (private) ----------
def gsc_rows():
    fn = os.path.join(PRIVATE, 'gsc_pages_90d.txt')
    rows = {}
    if not os.path.exists(fn): return None
    for line in open(fn, encoding='utf-8'):
        parts = line.rstrip('\n').split('|')
        if len(parts) < 5 or not parts[0].startswith('/'): continue
        path = parts[0].split(' Copy URL')[0].strip()
        try: c, i = int(parts[1]), int(parts[2])
        except ValueError: continue
        if path in rows:
            pc, pi, pp = rows[path]; rows[path] = (max(pc, c), max(pi, i), pp)
        else:
            rows[path] = (c, i, parts[4])
    return rows


def clicked_files():
    """Set of site files whose page (directly or via redirect / slash / #fragment) had >=1 click."""
    rows = gsc_rows()
    if rows is None: return None
    red = load_redirects(); out = {}
    for p, (c, i, pos) in rows.items():
        if c < 1: continue
        st, f, _ = final(p.split('#')[0] or '/', red)
        if f and f.endswith('.html'):
            out[f] = out.get(f, 0) + c
    return out


# ---------- garages ----------
def garages():
    s = open(os.path.join(S, 'assets', 'garages-data.js'), encoding='utf-8').read()
    return json.loads(re.search(r'const ALL_GARAGES = (\[[\s\S]*\]);', s).group(1))


def ts_places():
    s = open(os.path.join(S, 'assets', 'finder.js'), encoding='utf-8').read()
    return json.loads(re.search(r'const TS_PLACES = (\[[\s\S]*?\]);', s).group(1))


def miles(a, b, c, d):
    r = 3958.8; p1, p2 = math.radians(a), math.radians(c)
    dp, dl = p2 - p1, math.radians(d - b)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


# ---------- teslachargers.co.uk data (port of tpl_core.js) ----------
def slugify(s):
    s = unicodedata.normalize('NFKD', str(s))
    s = re.sub(r'[^\x00-\x7f]', '', s).lower().replace('’', '').replace("'", '').replace('&', ' and ')
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:70].strip('-')
    return s or 'x'


class Chargers:
    def __init__(self):
        D = json.load(open(os.path.join(TC, 'data.json'), encoding='utf-8'))
        self.D = D; R = D['R']; TO = D['T']; CO = D['C']; NA = D['N']
        self.R, self.TO, self.CO, self.NA = R, TO, CO, NA
        byIdL = {str(r[0]).lower(): i for i, r in enumerate(R)}
        self.DUP = {}
        for a, b in D.get('DUP') or []:
            ia, ib = byIdL.get(str(a).lower()), byIdL.get(str(b).lower())
            if ia is not None and ib is not None: self.DUP[ia] = ib
        self.SLUG = []
        for r in R:
            t = TO[r[3]][0]; inT = t.lower() in r[1].lower()
            self.SLUG.append(slugify(r[1] if inT else r[1] + ' ' + t) + '-' + str(r[0]).lower())
        self.townRows = [[] for _ in TO]
        for i, r in enumerate(R):
            if i not in self.DUP: self.townRows[r[3]].append(i)
        self.stray = {ti for ti, t in enumerate(TO) if t[0] == 'London' and CO[t[1]][0] != 'Greater London'}
        self.moved = {a for a, b in D.get('TMOVE') or []}
        self.townByPath = {}
        for i, t in enumerate(TO):
            k = self.town_path(i)
            if k not in self.townByPath or self.townRows[i]: self.townByPath[k] = i

    def town_path(self, ti):
        t = self.TO[ti]; c = self.CO[t[1]]
        return f'/{self.NA[c[1]][1]}/{c[2]}/{t[2]}/'

    def town_ok(self, ti):
        """Town page is live, indexable (>=2 chargers) and not moved."""
        if ti in self.stray or ti in self.moved: return False
        if self.townByPath.get(self.town_path(ti)) != ti: return False
        return len(self.townRows[ti]) >= 2

    def type(self, i): return self.D['T_'][self.R[i][11]]

    def charger_url(self, i):
        j = self.DUP.get(i, i)
        if self.R[j][21]: return None   # thin pages are noindex: do not link
        return 'https://teslachargers.co.uk/charger/' + self.SLUG[j] + '/'

    def live(self, i):
        return i not in self.DUP and self.D['S'][self.R[i][13]] != 'Not Operational' if isinstance(self.R[i][13], int) else i not in self.DUP
