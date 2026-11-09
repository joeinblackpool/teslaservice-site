"""Keep every static page on one template: same main menu, same page width, same body text spacing.
Idempotent; run after adding pages (tools/models.py and hand-made pages included).

  python3 tools/consistency.py          (fix)
  python3 tools/consistency.py --check  (exit 1 if any page differs; used by "Check site")

- Main menu: NAV below, on every page that has a <nav aria-label="Main">. The current page keeps aria-current.
  The /places Worker (worker/index.js) uses the same items.
- Page width: .wrap max-width 760px (the home page and the wide contact-details table keep their own).
- Body line-height 1.65.
Titles, H1s, descriptions and text are never touched."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitelib import S

ITEMS = [('/#finder', 'Find a specialist'), ('/guides', 'Guides'), ('/models/', 'Models'), ('/locations/', 'Locations'),
         ('/faq', 'FAQ'), ('/resources', 'Resources'), ('/reviews', 'Reviews'), ('/calculator', 'Cost calculator')]
KEEP_WIDTH = {'index.html', 'tesla-garage-contact-details.html', '404.html'}


def nav(current):
    return '<nav aria-label="Main"><ul>' + ''.join(
        f'<li><a href="{h}"{" aria-current=\"page\"" if h == current else ""}>{t}</a></li>' for h, t in ITEMS) + '</ul></nav>'


def fix(rel, s):
    m = re.search(r'<nav aria-label="Main">.*?</nav>', s, re.S)
    if m:
        url = '/' + rel[:-5]
        url = url[:-5] if url.endswith('/index') else url
        here = next((h for h, t in ITEMS if h.rstrip('/') == url.rstrip('/')), None)
        s = s[:m.start()] + nav(here) + s[m.end():]
    if rel not in KEEP_WIDTH:
        s = re.sub(r'(\.wrap\s*\{\s*max-width:\s*)\d+px', r'\g<1>760px', s, count=1)
    s = re.sub(r'(body\s*\{[^}]*line-height:\s*)1\.6(\s*;)', r'\g<1>1.65\2', s, count=1)
    return s


def main(check):
    bad = 0
    for dp, dn, fn in os.walk(S):
        for f in fn:
            if not f.endswith('.html'): continue
            p = os.path.join(dp, f); rel = os.path.relpath(p, S)
            s = open(p, encoding='utf-8').read(); t = fix(rel, s)
            if t != s:
                bad += 1
                if check: print('differs:', rel)
                else: open(p, 'w', encoding='utf-8').write(t)
    print({'pages_differing' if check else 'pages_changed': bad})
    return 1 if check and bad else 0


if __name__ == '__main__':
    sys.exit(main('--check' in sys.argv))
