"""Search-snippet rewrite for pages with ZERO Search Console clicks in the last 3 months that already rank
in the top 15 (list in the private folder: targets_paths.txt, built from Search Console on 6 Nov 2026).

- Garage pages (/authorised, /hevra, /other, /dealer, /parts): meta description built from the page's own
  structured data (name, street, postcode, phone, type) instead of the shared boilerplate; title says what
  the visitor gets ("address & phone") when it fits in 575 px.
- Town and county pages (/locations/*): title leads with "Tesla garage", the site's biggest search
  ("tesla garage near me"); description unchanged.
- /contact-tesla-uk: title answers the number people search for (01628 450660, stated on the page).
H1 and page text are never changed. Pages not in the list are never touched. Idempotent.
Usage: python3 tools/snippets.py [--write]"""
import os, re, sys, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitelib import S, PRIVATE, px

LIMIT = 570
WRITE = '--write' in sys.argv
targets = [l.strip() for l in open(os.path.join(PRIVATE, 'targets_paths.txt')) if l.strip()]

ROLE = {
    'Tesla-Approved Bodyshop': ('Tesla-approved bodyshop', 'Approved by Tesla for accident repair, not servicing.'),
    'HEVRA-Accredited': ('HEVRA EV specialist', 'HEVRA-accredited EV and hybrid specialist.'),
    'Independent Tesla/EV Specialist': ('Tesla specialist', 'Independent Tesla and EV specialist.'),
    'Official Tesla Service Centre': ('official Tesla Service Centre', 'Official Tesla centre: book through the Tesla app.'),
    'Accessories Retailer': ('Tesla parts & accessories', 'Tesla parts and accessories.'),
    'Advertises Tesla Servicing': ('garage for Tesla servicing', 'Independent garage that advertises Tesla servicing.'),
    'Battery/Drivetrain Specialist': ('EV battery & drivetrain specialist', 'EV battery and drivetrain specialist.'),
    'PPF/Wrap/Tint/Detailing': ('Tesla PPF, wraps & detailing', 'Paint protection film, wraps, tint and detailing.'),
    'Retrofit/Coding/Upgrades': ('Tesla retrofits & upgrades', 'Retrofits, coding and upgrades.'),
}
# shorter type names for titles, so 'Tesla' stays in the title when the full one does not fit
TSHORT = {'Tesla-Approved Bodyshop': 'Tesla bodyshop', 'HEVRA-Accredited': 'Tesla & EV specialist', 'Independent Tesla/EV Specialist': 'Tesla specialist',
          'Official Tesla Service Centre': 'Tesla Service Centre', 'Accessories Retailer': 'Tesla parts', 'Advertises Tesla Servicing': 'Tesla servicing',
          'Battery/Drivetrain Specialist': 'EV battery specialist', 'PPF/Wrap/Tint/Detailing': 'Tesla PPF & wraps', 'Retrofit/Coding/Upgrades': 'Tesla upgrades'}

def esc(s): return html.escape(s, quote=True)

def set_meta(s, title=None, desc=None):
    if title:
        s = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}</title>', s, count=1, flags=re.S)
        s = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1) + esc(title) + m.group(2), s, count=1)
        s = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")', lambda m: m.group(1) + esc(title) + m.group(2), s, count=1)
    if desc:
        for k in ('name="description"', 'property="og:description"', 'name="twitter:description"'):
            s = re.sub(r'(<meta ' + re.escape(k) + r' content=")[^"]*(")', lambda m: m.group(1) + esc(desc) + m.group(2), s, count=1)
    return s

def fit(parts, max_len=158):
    out = parts[0]
    for p in parts[1:]:
        if p and len(out + ' ' + p) <= max_len: out += ' ' + p
    return out

def garage(path, s):
    ld = None
    for m in re.finditer(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', s, re.S):
        try: j = json.loads(m.group(1))
        except Exception: continue
        if j.get('@id', '').endswith('#business'): ld = j; break
    badge = re.search(r'<span class="badge">(.*?)</span>', s)
    badge = html.unescape(badge.group(1)) if badge else ''
    if not ld or badge not in ROLE: return None, None
    short, role = ROLE[badge]
    name = html.unescape(ld['name']); a = ld.get('address', {})
    street = html.unescape(a.get('streetAddress', '')); pc = a.get('postalCode', ''); tel = ld.get('telephone', '')
    where = ', '.join(x for x in [street, pc] if x)
    lead = f'{name}: {short}' + (f', {where}.' if where else '.')
    desc = fit([lead, f'Phone {tel}.' if tel else '', role, 'What to check before you book.'])
    old_t = html.unescape(re.search(r'<title>(.*?)</title>', s, re.S).group(1))
    ts = TSHORT[badge]
    if badge == 'Official Tesla Service Centre':
        place = re.sub(r'^Tesla Service\s+', '', name)
        cands = [f'Tesla Service Centre {place}: address, phone & booking', f'Tesla Service Centre {place}: address & phone', old_t]
        return next((c for c in cands if px(c) <= LIMIT), old_t), desc
    cands = [f'{name}: {short}, address & phone', f'{name}: {ts}, address & phone', f'{name} – {ts}: address & phone', old_t]
    title = next((c for c in cands if px(c) <= LIMIT), old_t)
    return title, desc

def location(path, s):
    old_t = html.unescape(re.search(r'<title>(.*?)</title>', s, re.S).group(1))
    h1 = html.unescape(re.sub('<[^>]+>', '', re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S).group(1)))
    n = re.search(r'(\d+) (?:Local )?Garages', old_t) or re.search(r'— (\d+) ', old_t) or re.search(r'\((\d+)(?: listed)?\)$', old_t)
    if path.startswith('/locations/county/'):
        place = re.sub(r'^Tesla service (?:& repair )?in ', '', h1)
        cands = [f'Tesla garages in {place}: service & repair ({n.group(1)} listed)' if n else None, f'Tesla garages in {place}: service & repair']
    else:
        place = re.sub(r'^Tesla service (?:& repair )?in ', '', h1)
        cands = [f'Tesla garage in {place}: service, repair & specialists' + (f' ({n.group(1)})' if n else ''), f'Tesla garage {place}: service, repair & specialists' + (f' ({n.group(1)})' if n else ''), f'Tesla garage {place}: service & repair' + (f' ({n.group(1)})' if n else ''), f'Tesla garage {place}: service & repair']
    title = next((c for c in cands if c and px(c) <= LIMIT), old_t)
    return title, None

changed = []
for p in targets:
    f = os.path.join(S, p.lstrip('/') + '.html')
    if not os.path.exists(f): continue
    s = open(f, encoding='utf-8').read()
    sec = p.split('/')[1]
    if sec in ('authorised', 'hevra', 'other', 'dealer', 'parts'): t, d = garage(p, s)
    elif sec == 'locations': t, d = location(p, s)
    elif p == '/contact-tesla-uk':
        t, d = "01628 450660: Tesla UK phone number & how to contact Tesla", None
    else: continue
    if not t and not d: continue
    new = set_meta(s, t, d)
    if new != s:
        changed.append((p, t, d))
        if WRITE: open(f, 'w', encoding='utf-8').write(new)
print(('wrote' if WRITE else 'would change'), len(changed), 'pages')
from collections import Counter
print(Counter(p.split('/')[1] for p, t, d in changed))
for p, t, d in changed[:6] + [x for x in changed if x[0].split('/')[1] in ('hevra','dealer','other')][:6]: print(' ', p, '|', t, '|', d)
print('max title px', max([px(t) for p, t, d in changed if t] or [0]))
