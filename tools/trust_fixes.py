"""Additive trust/UX fixes on every static page (idempotent; re-run any time):

  python3 tools/trust_fixes.py

1. Footer: a "Contact" link (to /about#contact) right after the footer's About link.
2. Phone numbers shown in listing meta lines (/locations/*, /, garage pages) become tap-to-call tel: links.
3. Freshness: pages whose JSON-LD has no dateModified get it from that page's sitemap.xml <lastmod> (the date of
   its last real content change; template-only edits don't move it). CollectionPage/Article nodes get the property;
   other pages get a small WebPage node.
Titles, H1s, descriptions and visible text stay as they are."""
import os, re, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitelib import S

SITE = 'https://teslaservice.co.uk'
LASTMOD = dict(re.findall(r'<loc>https://teslaservice\.co\.uk([^<]*)</loc><lastmod>([^<]+)</lastmod>', open(os.path.join(S, 'sitemap.xml'), encoding='utf-8').read()))
PHONE = re.compile(r'(?<![\d>"])((?:\+44\s?|0)(?:\d\s?){9,10}\d?)(?=\s*(?:</div>|·|<br|$))')


def tel(m):
    num = m.group(1).strip()
    digits = re.sub(r'\D', '', num)
    if not (10 <= len(digits) <= 12): return m.group(0)
    return f'<a href="tel:{"+" if num.startswith("+") else ""}{digits}">{num}</a>'


def fix(text, url):
    # 1. footer Contact link
    fm = re.search(r'<footer[\s\S]*?</footer>', text)
    if fm and 'href="/about#contact"' not in fm.group(0):
        a = re.search(r'<a href="/about"([^>]*)>About</a>', fm.group(0))
        if a:
            sep = ' &middot; ' if '&middot;' in fm.group(0) else ' · '
            new = fm.group(0)[:a.end()] + f'{sep}<a href="/about#contact"{a.group(1)}>Contact</a>' + fm.group(0)[a.end():]
            text = text[:fm.start()] + new + text[fm.end():]
    # 2. tel: links inside listing meta lines
    text = re.sub(r'(<div class="meta">)([^<]*)(</div>)', lambda m: m.group(1) + PHONE.sub(tel, m.group(2)) + m.group(3), text)
    # 3. dateModified
    lm = LASTMOD.get(url)
    if lm and 'dateModified' not in text:
        done = False
        def add(m):
            nonlocal done
            try: j = json.loads(m.group(2))
            except Exception: return m.group(0)
            if isinstance(j, dict) and j.get('@type') in ('CollectionPage', 'Article', 'WebPage', 'AboutPage') and not done:
                j['dateModified'] = lm; done = True
                compact = ': ' not in m.group(2)
                return m.group(1) + (json.dumps(j, ensure_ascii=False, separators=(',', ':')) if compact else json.dumps(j, ensure_ascii=False)) + m.group(3)
            return m.group(0)
        text = re.sub(r'(<script type="application/ld\+json">\s*)(.*?)(\s*</script>)', add, text, flags=re.S)
        if not done and '</head>' in text:
            node = {'@context': 'https://schema.org', '@type': 'WebPage', 'url': SITE + url, 'dateModified': lm}
            text = text.replace('</head>', f'<script type="application/ld+json">{json.dumps(node, separators=(",", ":"))}</script>\n</head>', 1)
    return text


def main():
    changed = 0
    for root, _, files in os.walk(S):
        for f in files:
            if not f.endswith('.html') or f == '404.html': continue
            p = os.path.join(root, f); u = '/' + os.path.relpath(p, S)[:-5]
            if u.endswith('/index'): u = u[:-5]
            if u == '/index': u = '/'
            old = open(p, encoding='utf-8').read(); new = fix(old, u)
            if new != old: open(p, 'w', encoding='utf-8').write(new); changed += 1
    print('pages changed', changed)


if __name__ == '__main__':
    main()
