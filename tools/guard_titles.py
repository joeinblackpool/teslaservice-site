"""Guard for the additive-only rule: fails if any page with >=1 Search Console click (90 days, private
file outside the repo) had its <title>, H1 or meta description changed, or stopped resolving,
between a git ref (default: origin/main, i.e. what is live) and the working tree.
Usage: python3 tools/guard_titles.py [ref]   (exit 1 on any change; exit 0 with a note if the private file is absent)"""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitelib import ROOT, S, clicked_files, page_meta, resolve, url_of, final, load_redirects

ref = sys.argv[1] if len(sys.argv) > 1 else 'origin/main'
clicked = clicked_files()
if clicked is None:
    print('guard_titles: private Search Console file not found - skipped'); sys.exit(0)
bad = []; red = load_redirects()
for f, c in sorted(clicked.items()):
    rel = os.path.relpath(f, ROOT).replace(os.sep, '/')
    r = subprocess.run(['git', '-C', ROOT, 'show', f'{ref}:{rel}'], capture_output=True)
    if r.returncode != 0: continue          # page is new since ref
    old = page_meta(r.stdout.decode('utf-8', 'replace'))
    if not os.path.exists(f):
        st, _, _ = final(url_of(f), red)
        if st != 200: bad.append((rel, 'page removed without a working redirect'))
        continue
    new = page_meta(open(f, encoding='utf-8').read())
    for k in ('title', 'h1', 'desc'):
        if old[k] != new[k]: bad.append((rel, f'{k}: {old[k]!r} -> {new[k]!r}'))
print(f'guard_titles: {len(clicked)} pages with clicks checked against {ref}; changed: {len(bad)}')
for b in bad: print(' ', *b)
sys.exit(1 if bad else 0)
