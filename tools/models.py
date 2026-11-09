"""Builds the Models section: /models/ (hub) and /models/model-3, model-y, model-s, model-x.
Each page answers grouped questions (servicing, common faults, warranty, repairs) in short plain answers,
from Tesla's own manuals and warranty pages and the sources already cited elsewhere on this site.
No FAQPage JSON-LD (removed site-wide on 22 Oct 2026); Article + BreadcrumbList only.
Run: python3 tools/models.py   (rewrites site/models/*.html; idempotent)"""
import os, json, html

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site')
OUT = os.path.join(ROOT, 'models')
BASE = 'https://teslaservice.co.uk'
CHECKED = '2026-11-09'
CHECKED_TEXT = '9 November 2026'

# ---------- sources (every fact on these pages comes from one of these) ----------
SRC = {
    'm3int': ('https://www.tesla.com/ownersmanual/model3/en_nz/GUID-E95DAAD9-646E-4249-9930-B109ED7B1D91.html',
              "Tesla Model 3 Owner's Manual: Maintenance Service Intervals"),
    'myint': ('https://service.tesla.com/docs/Public/diy/modely/en_us/GUID-A84FDD77-7A8C-42F6-9385-E3F9CEE245A4.html',
              'Tesla Service: Model Y maintenance intervals'),
    'msint': ('https://service.tesla.com/docs/Public/diy/models/en_us/GUID-A84FDD77-7A8C-42F6-9385-E3F9CEE245A4.html',
              'Tesla Service: Model S vehicle service intervals'),
    'msold': ('https://www.tesla.com/ownersmanual/2012_2020_models/en_ie/GUID-E95DAAD9-646E-4249-9930-B109ED7B1D91.html',
              "Tesla Model S Owner's Manual (2012–2020 cars): Maintenance Service Intervals"),
    'mxint': ('https://service.tesla.com/docs/Public/diy/modelx/en_us/GUID-A84FDD77-7A8C-42F6-9385-E3F9CEE245A4.html',
              'Tesla Service: Model X vehicle service intervals'),
    'warr': ('https://www.tesla.com/en_GB/support/vehicle-warranty', 'Tesla UK: Vehicle Warranty'),
    'mot': ('https://www.gov.uk/getting-an-mot', 'GOV.UK: Getting an MOT'),
    'mot3': ('https://www.motscout.co.uk/cars/tesla/model-3/', 'MOT Scout: Tesla Model 3 MOT results 2025 (DfT anonymised MOT data)'),
    'sb2020': ('https://driveteslacanada.ca/?p=25923', 'Drive Tesla Canada: Tesla notifies Model 3 owners about upper control arm noise (SB-20-31-006)'),
    'sb2026': ('https://www.notateslaapp.com/news/4210/tesla-issues-service-bulletins-for-refreshed-model-y-suspension-creaks',
               'Not a Tesla App: Tesla service bulletins for refreshed Model Y suspension creaks (May 2026)'),
    'sbpdf': ('https://service.tesla.com/docs/ServiceBulletins/External/SB/SB-25-31-005_Replace_Suspension_Components_R1.pdf',
              'Tesla service bulletin SB-25-31-005: Replace Suspension Components'),
    'lv': ('https://tslna.com/en/tesla-12v-low-voltage-battery-guide-2026/', 'TSLNA: Tesla 12V / low-voltage battery explained (2026)'),
    'which': ('https://www.which.co.uk/news/2021/02/tesla-recalls-model-s-and-model-x-cars-in-the-uk/',
              'Which?: Tesla recalls Model S and Model X cars in the UK (Feb 2021)'),
    'recall': ('https://www.gov.uk/check-vehicle-recall', 'GOV.UK: Check if a vehicle has been recalled'),
}

FINDER = ('<div class="cta-box"><h2>{h}</h2><p>Independent EV specialists and Tesla Service Centres, sorted by distance '
          'from your postcode.</p><a class="cta-btn" href="/#finder">Search by postcode or town</a><p class="cta-links">'
          'Or browse: <a href="/hevra-tesla-service">HEVRA-accredited EV specialists</a> · <a href="/other-tesla-services">'
          'independent &amp; mobile garages</a> · <a href="/tesla-service-centers">Tesla Service Centres</a> · '
          '<a href="/places">near any town or village</a></p></div>')

NAV = ('<nav aria-label="Main"><ul><li><a href="/#finder">Find a specialist</a></li><li><a href="/guides">Guides</a></li>'
       '<li><a href="/models/"{cur}>Models</a></li><li><a href="/locations/">Locations</a></li><li><a href="/faq">FAQ</a></li>'
       '<li><a href="/resources">Resources</a></li><li><a href="/reviews">Reviews</a></li><li><a href="/calculator">Cost calculator</a></li></ul></nav>')

CSS = """<style>
  :root{--bg:#0B1113;--panel:#171F22;--ink:#F2F5F4;--ink-dim:#93A6A3;--accent:#33E0C0;--line:#222C2E;--radius:6px;
    box-sizing:border-box; padding-top:env(safe-area-inset-top,0px); padding-bottom:env(safe-area-inset-bottom,0px);}
  *{box-sizing:border-box;} html{scroll-padding-top:env(safe-area-inset-top,0px);}
  body{margin:0; background:var(--bg); color:var(--ink); font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif; line-height:1.65;}
  h1,h2,h3,.brand{font-family:ui-sans-serif,system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;}
  .wrap{max-width:760px; margin:0 auto; padding:0 24px 60px;}
  header{padding:24px 0; border-bottom:1px solid var(--line); margin-bottom:32px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;}
  .brand{font-size:17px; font-weight:600;} .brand span{color:var(--accent);} .brand a{text-decoration:none; color:var(--ink);}
  nav ul{list-style:none; display:flex; gap:18px; margin:0; padding:0; font-size:14px; flex-wrap:wrap;}
  nav a{text-decoration:none; color:var(--ink-dim);} nav a:hover, nav a[aria-current]{color:var(--ink);}
  .crumbs{font-size:12.5px; color:var(--ink-dim); margin:0 0 14px;} .crumbs a{color:var(--ink-dim);}
  h1{font-size:27px; margin:0 0 8px;}
  .lede{color:var(--ink-dim); font-size:15px; max-width:60ch; margin:0 0 12px;}
  .fact-checked{color:var(--ink-dim); font-size:13px; margin:0 0 32px;}
  .guide{border-top:1px solid var(--line); padding:24px 0;} .guide:first-of-type{border-top:none;}
  .tag{font-size:12px; color:var(--accent); margin:0 0 6px;}
  .guide h2{font-size:20px; margin:0 0 6px;}
  .guide h3{font-size:16px; margin:20px 0 6px; color:var(--ink);}
  .guide p{color:var(--ink-dim); font-size:14.5px; margin:0 0 10px;}
  .guide ul{color:var(--ink-dim); font-size:14.5px; margin:0 0 10px; padding-left:20px;} .guide li{margin-bottom:6px;}
  .guide a{color:var(--accent);}
  .tbl{width:100%; overflow-x:auto;} table{border-collapse:collapse; width:100%; font-size:14px; color:var(--ink-dim);}
  th,td{text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); vertical-align:top;} th{color:var(--ink); font-weight:600;}
  td a{color:var(--accent);}
  .cards{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin:8px 0 0;}
  .card{background:var(--panel); border:1px solid var(--line); border-radius:var(--radius); padding:16px; text-decoration:none; color:var(--ink-dim); font-size:14px;}
  .card strong{display:block; color:var(--ink); font-size:16px; margin-bottom:4px;} .card:hover{border-color:var(--accent);} .guide a.card{color:var(--ink-dim);} td:first-child{white-space:nowrap;}
  .cross{background:var(--panel); border:1px solid var(--line); border-radius:var(--radius); padding:16px 18px; margin:32px 0; font-size:14px;}
  .cross a{color:var(--accent);}
  .cta-box{background:var(--panel);border:1px solid var(--accent);border-radius:var(--radius);padding:20px 22px;margin:28px 0}.cta-box h2{font-size:18px;margin:0 0 6px}.cta-box p{color:var(--ink-dim);font-size:14.5px;margin:0 0 14px}.cta-btn{display:inline-block;background:var(--accent);color:#06201B;font-weight:700;text-decoration:none;padding:11px 18px;border-radius:var(--radius);margin:0 10px 8px 0}.cta-links{font-size:13.5px;color:var(--ink-dim)}.cta-links a{color:var(--accent)}
  .sources{font-size:13px;color:var(--ink-dim);padding-left:20px}.sources a{color:var(--ink-dim)}sup a{color:var(--accent);text-decoration:none;font-size:11px}
  footer{padding:40px 0;} footer p{color:var(--ink-dim); font-size:13px; max-width:60ch;}
</style>
<style id="tap-targets">@media (max-width:720px){nav ul{gap:2px 16px;} nav a{display:inline-block; padding:10px 0;} .crumbs a, footer a{display:inline-block; padding:11px 0;} footer p, .by-region{line-height:2.1;}}</style>"""

FOOTER = """<footer class="wrap">
  <p>TeslaService.co.uk is an independent, self-funded, not-for-profit resource for UK Tesla owners. We are not affiliated with Tesla, Inc. Always check your own vehicle's specifics and current official guidance before relying on general information.</p>
  <p style="margin-top:10px;"><a href="/about" style="color:var(--ink-dim);">About</a> &middot; <a href="/privacy" style="color:var(--ink-dim);">Privacy</a> &middot; <a href="/terms" style="color:var(--ink-dim);">Terms</a> &middot; <a href="/suggest" style="color:var(--ink-dim);">Suggest a garage</a></p>
</footer>"""


class Cites:
    """Numbers sources in order of first use on a page."""
    def __init__(s): s.order = []
    def __call__(s, *keys):
        out = []
        for k in keys:
            if k not in s.order: s.order.append(k)
            out.append(f'<a href="#src-{k}">{s.order.index(k) + 1}</a>')
        return '<sup>' + ', '.join(out) + '</sup>'
    def html(s):
        return '<ol class="sources">' + ''.join(
            f'<li id="src-{k}"><a href="{SRC[k][0]}" rel="nofollow noopener" target="_blank">{html.escape(SRC[k][1])}</a></li>'
            for k in s.order) + '</ol>'


def page(slug, title, desc, h1, lede, crumb, body, cites, headline):
    url = f'{BASE}/models/{slug}' if slug else f'{BASE}/models/'
    crumbs = [('Tesla Service UK', f'{BASE}/'), ('Models', f'{BASE}/models/')]
    if slug: crumbs.append((crumb, url))
    bc = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(crumbs)]}
    art = {'@context': 'https://schema.org', '@type': 'Article', '@id': url + '#article', 'headline': headline,
           'description': desc, 'url': url, 'mainEntityOfPage': url, 'datePublished': CHECKED, 'dateModified': CHECKED,
           'inLanguage': 'en-GB', 'image': f'{BASE}/og-image-v2.png',
           'author': {'@type': 'Organization', 'name': 'XKey Developments', 'url': 'https://xkey.co.uk/'},
           'publisher': {'@id': f'{BASE}/#organization', '@type': 'Organization', 'name': 'TeslaService.co.uk', 'url': f'{BASE}/'},
           'citation': [SRC[k][0] for k in cites.order]}
    crumb_html = ('<a href="/">Tesla Service UK</a> / <a href="/models/">Models</a> / ' + html.escape(crumb)) if slug \
        else '<a href="/">Tesla Service UK</a> / Models'
    t, d = html.escape(title), html.escape(desc)
    src = ('<div class="guide" id="sources"><p class="tag">Sources</p><h2>Where this information comes from</h2>'
           + cites.html() + '</div>') if cites.order else ''
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en-GB" href="{url}">
<link rel="alternate" hreflang="x-default" href="{url}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="article">
<meta property="og:image" content="{BASE}/og-image-v2.png">
<meta name="twitter:card" content="summary_large_image">
{CSS}
<script type="application/ld+json">{json.dumps(bc, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(art, ensure_ascii=False)}</script>
</head>
<body>
<div class="wrap">
  <header>
    <div class="brand"><a href="/">TeslaService<span>.co.uk</span></a></div>
    {NAV.format(cur=' aria-current="page"' if not slug else '')}
  </header>
<main>
  <p class="crumbs">{crumb_html}</p>
  <h1>{html.escape(h1)}</h1>
  <p class="lede">{lede}</p>
  <p class="fact-checked">Last fact-checked: <time datetime="{CHECKED}">{CHECKED_TEXT}</time> by the XKey Developments team. General guidance — always check your own car's details and current official sources. Repair costs vary by car and garage, so we don't quote prices: ask for a written quote.</p>
{body}
{src}
</main>
</div>
{FOOTER}
</body>
</html>
"""


def section(sid, tag, h2, qas, intro=''):
    out = [f'  <div class="guide" id="{sid}">', f'    <p class="tag">{tag}</p>', f'    <h2>{h2}</h2>']
    if intro: out.append(f'    {intro}')
    for q, a in qas:
        out.append(f'    <h3>{q}</h3>')
        out.append(f'    {a}')
    out.append('  </div>')
    return '\n'.join(out)


def interval_list(c, m):
    """Maintenance list for model m ('3','Y','S','X'), each item cited to that model's own Tesla page."""
    k = {'3': 'm3int', 'Y': 'myint', 'S': 'msint', 'X': 'mxint'}[m]
    if m == '3': cabin = f'every 2 years{c(k)}'
    elif m == 'Y': cabin = f'every 2 years; HEPA and carbon filters, where fitted, every 3 years{c(k)}'
    elif m == 'S': cabin = (f'every 3 years, and the HEPA filter every 3 years{c(k)}. The owner\'s manual for 2012–2020 cars '
                            f'gives 2 years for the cabin filter{c("msold")}, so check the maintenance summary on your own touchscreen')
    else: cabin = f'every 3 years, and the HEPA and carbon filters every 3 years{c(k)}'
    coolant = (f'<li><strong>Battery coolant:</strong> under most circumstances it does not need replacing for the life of the car'
               f'{c("m3int" if m == "3" else "msold")}.</li>') if m in '3S' else ''
    return (f'<ul><li><strong>Brake fluid:</strong> health check every 4 years, replaced if necessary{c(k)}. Tesla says not to top it up yourself.</li>'
            f'<li><strong>Cabin air filter:</strong> {cabin}.</li>'
            f'<li><strong>Tyre rotation:</strong> every 6,250 miles (10,000 km), or sooner if the tread depth difference between tyres is 1.5 mm or more{c(k)}.</li>'
            f'<li><strong>Brake calipers:</strong> clean and lubricate every year or 12,500 miles if you drive on roads that are salted in winter{c(k)}, which covers most of the UK.</li>'
            f'<li><strong>Wiper blades:</strong> replace every year{c(k)}.</li>{coolant}</ul>'
            f'<p>Brake pads, tyres, the low-voltage battery and other wear parts have no fixed interval: they are replaced when worn. '
            f'See the full <a href="/tesla-service-schedule">Tesla service schedule</a>.</p>')


def mot_q(c, model):
    return (f'When does a {model} need an MOT?',
            f'<p>Like any car, at 3 years old in England, Scotland and Wales, then every year{c("mot")}; in Northern Ireland the first test is at 4 years. '
            f'There is no emissions test, but tyres, brakes, suspension, lights and steering are all checked. '
            f'Check when yours is due and its MOT history on GOV.UK. See our <a href="/tesla-mot-guide">Tesla MOT guide</a>.</p>')


def independent_q(c, model):
    return (f'Can an independent garage service my {model}?',
            f'<p>Yes, for non-warranty work. Tesla\'s UK warranty page says you may have the car serviced at a Tesla Service Centre '
            f'or a non-Tesla service centre, but warranty repairs must be done by Tesla, and Tesla is not responsible for problems '
            f'caused by improper third-party repair{c("warr")}. In practice an EV specialist can do tyres, brakes, suspension and filters. '
            f'Keep every invoice. More in our <a href="/warranty-guide#independent-servicing">warranty guide</a>.</p>')


def lv_q(c, model, text):
    return (f'Does my {model} have a 12V or a 16V battery?',
            f'<p>{text}{c("lv")} The two types are not interchangeable, so ask the garage to confirm from the VIN before buying one. '
            f'If the low-voltage battery fails the car may not unlock or drive, even with a full main battery. '
            f'See our <a href="/tesla-low-voltage-battery">12V / 16V battery guide</a>.</p>')


def recall_q(c, model):
    return (f'How do I check a {model} for recalls?',
            f'<p>Enter the registration on GOV.UK\'s vehicle recall checker{c("recall")}. Recall work and service bulletins are '
            f'booked with Tesla through the app. If you are buying used, also read our <a href="/buying-used-checklist">used Tesla checklist</a>.</p>')


def related(extra):
    return ('<div class="cross">Other models: ' + ' · '.join(extra) +
            ' · <a href="/models/">compare all models</a>. Common faults: <a href="/tesla-suspension-noise">suspension noise</a> · '
            '<a href="/tesla-brake-caliper-seized">seized brakes</a> · <a href="/tesla-tyre-wear">tyre wear</a> · '
            '<a href="/tesla-touchscreen-black">touchscreen black</a></div>')


MODELS = {}


def model_3():
    c = Cites(); M = 'Model 3'
    b = []
    b.append(section('servicing', 'Servicing', 'Tesla Model 3 servicing', [
        ('Does a Tesla Model 3 need an annual service?',
         f'<p>No fixed one. There is no oil to change, and Tesla\'s Model 3 owner\'s manual lists individual items, each with its own interval, '
         f'instead of a yearly service{c("m3int")}. Many owners still have a yearly check to catch tyre, brake and suspension wear early.</p>'),
        ('What maintenance does a Model 3 need, and when?', interval_list(c, '3')),
        mot_q(c, M),
    ]))
    b.append(FINDER.format(h='Find a Model 3 garage near you'))
    b.append(section('common-faults', 'Common faults', 'What goes wrong on a Model 3?', [
        ('Why do Model 3s fail the MOT?',
         f'<p>Mostly tyres. In 2025 tyres were involved in 71.9% of Model 3 initial MOT failures, and were an advisory on 27.7% of all tests{c("mot3")}. '
         f'Suspension was the next most common reason, in 15.3% of initial failures{c("mot3")}, and brakes were an advisory on 10.4% of initial tests{c("mot3")}. '
         f'The car is heavy and quick, so check the inside edge of each tyre before the test. See <a href="/tesla-tyre-wear">Tesla tyre wear</a>.</p>'),
        ('Why does my Model 3 creak when I turn the wheel?',
         f'<p>On 2018–2020 cars, the classic cause is water getting into the front upper control arm ball joints. Tesla service bulletin SB-20-31-006 covers it, '
         f'describes it as a noise-only issue, and Tesla contacted owners to reseal or repair the joint free of charge{c("sb2020")}. '
         f'Ask Tesla in the app whether it has been done on your car. More in <a href="/tesla-suspension-noise">suspension noise</a>.</p>'),
        ('Why are my Model 3 brakes rusty or grinding?',
         f'<p>Regenerative braking does most of the slowing, so the discs and calipers rarely get used and can corrode, especially on salted UK roads. '
         f'Tesla\'s manual lists a yearly caliper clean and lubricate where roads are salted{c("m3int")}. See <a href="/tesla-brake-caliper-seized">seized brakes</a>.</p>'),
        lv_q(c, M, 'Model 3s built before late 2021 have a 12V lead-acid battery; cars from late 2021, and the refreshed Model 3, have a lithium-ion one (usually about 16V).'),
        ('My Model 3 door won\'t open. What do I do?',
         '<p>Pull up the manual release in front of the window switches on the front doors; the rear doors have a cable under a cover in the door pocket. '
         'Use it only when needed. A failing low-voltage battery is the usual reason the doors stop responding. See <a href="/tesla-door-wont-open">door won\'t open</a>.</p>'),
    ]))
    b.append(section('warranty', 'Warranty', 'Model 3 warranty', [
        ('How long is the Model 3 battery warranty?',
         f'<p>8 years, with at least 70% of battery capacity retained: up to 100,000 miles on the Model 3 RWD, and up to 120,000 miles on the '
         f'Premium Long Range and Performance versions, whichever comes first{c("warr")}.</p>'),
        ('What does the basic warranty cover?',
         f'<p>Tesla\'s Basic Vehicle Limited Warranty is 4 years or 60,000 miles for cars bought after 1 January 2024; older cars keep the terms in force '
         f'when they were bought{c("warr")}. See our <a href="/warranty-guide">Tesla warranty guide</a> for exclusions and how to claim.</p>'),
        independent_q(c, M),
    ]))
    b.append(section('repairs', 'Repairs', 'Getting a Model 3 repaired', [
        ('Does a Model 3 windscreen need calibrating after replacement?',
         '<p>Yes. The driver-assistance cameras sit behind the windscreen and need recalibrating after new glass is fitted. Ask the glass company whether '
         'it calibrates in-house. See <a href="/windscreen-camera-calibration">windscreen &amp; camera calibration</a>.</p>'),
        ('Who repairs Model 3 accident damage?',
         '<p>Your insurer handles accident claims. Tesla\'s own body repair centre and Tesla-approved body shops can do the work. '
         'See <a href="/bodywork-accident-repair">bodywork &amp; accident repair</a> and <a href="/authorised-tesla-service">approved body shops</a>.</p>'),
        recall_q(c, M),
    ]))
    b.append(related(['<a href="/models/model-y">Model Y</a>', '<a href="/models/model-s">Model S</a>', '<a href="/models/model-x">Model X</a>']))
    return page('model-3', 'Tesla Model 3 Service & Repair UK: Questions Answered',
                'Tesla Model 3 servicing in the UK: maintenance intervals, MOT fail points, the control arm creak, 12V or 16V battery, battery warranty and where to get it repaired.',
                'Tesla Model 3 service and repair: your questions answered',
                'Short, sourced answers to what Model 3 owners in the UK ask most: what servicing it needs, what tends to go wrong, what the warranty covers and where to get it fixed.',
                'Model 3', '\n'.join(b), c, 'Tesla Model 3 service and repair: your questions answered')


def model_y():
    c = Cites(); M = 'Model Y'
    b = []
    b.append(section('servicing', 'Servicing', 'Tesla Model Y servicing', [
        ('Does a Tesla Model Y need an annual service?',
         f'<p>No fixed one. Tesla lists individual maintenance items for the Model Y, each with its own interval, rather than a yearly service{c("myint")}. '
         f'A yearly check of tyres, brakes and suspension is still a good idea on a heavy car.</p>'),
        ('What maintenance does a Model Y need, and when?', interval_list(c, 'Y')),
        mot_q(c, M),
    ]))
    b.append(FINDER.format(h='Find a Model Y garage near you'))
    b.append(section('common-faults', 'Common faults', 'What goes wrong on a Model Y?', [
        ('Why does my new Model Y knock or creak over bumps?',
         f'<p>On the refreshed (2026) Model Y, Tesla issued service bulletins SB-25-31-005 and SB-26-31-003 in May 2026 for creaking, rattling or knocking '
         f'from the front at low speed and on rough roads{c("sb2026", "sbpdf")}. The repair replaces the front upper control arm mounts, replaces the front '
         f'dampers on Premium and Performance versions, and removes the wiper-bracket braces that carried the noise{c("sb2026")}. Book it with Tesla and quote '
         f'the bulletin numbers. See <a href="/tesla-suspension-noise">suspension noise</a>.</p>'),
        ('Does the Model 3 control arm creak affect the Model Y?',
         f'<p>Tesla\'s bulletin SB-20-31-006 for front upper control arm creaks mainly covers 2018–2020 Model 3, but also includes some Model Y built '
         f'before the part was sealed at the factory{c("sb2020")}. Ask Tesla in the app whether it applies to your VIN.</p>'),
        ('Why are my Model Y brakes rusty?',
         f'<p>Regenerative braking does most of the slowing, so the friction brakes can corrode, especially on salted winter roads. Tesla lists a yearly '
         f'caliper clean and lubricate where roads are salted{c("myint")}. See <a href="/tesla-brake-caliper-seized">seized brakes</a>.</p>'),
        lv_q(c, M, 'Model Ys built before late 2021 have a 12V lead-acid battery; cars from late 2021, and the refreshed Model Y, have a lithium-ion one (usually about 16V).'),
        ('My Model Y cabin smells musty. What should I do?',
         f'<p>Start with the cabin filter: Tesla gives 2 years, or 3 years for HEPA and carbon filters where fitted{c("myint")}. If the smell stays after a new '
         f'filter, a garage with air-conditioning equipment can check the system. See <a href="/tesla-cabin-filter">cabin filter &amp; A/C smell</a>.</p>'),
    ]))
    b.append(section('warranty', 'Warranty', 'Model Y warranty', [
        ('How long is the Model Y battery warranty?',
         f'<p>8 years, with at least 70% of battery capacity retained: up to 100,000 miles on the Model Y RWD, and up to 120,000 miles on the '
         f'Premium Long Range and Performance versions, whichever comes first{c("warr")}.</p>'),
        ('What does the basic warranty cover?',
         f'<p>4 years or 60,000 miles for cars bought after 1 January 2024; older cars keep the terms in force when they were bought{c("warr")}. '
         f'See our <a href="/warranty-guide">Tesla warranty guide</a>.</p>'),
        independent_q(c, M),
    ]))
    b.append(section('repairs', 'Repairs', 'Getting a Model Y repaired', [
        ('Can I change the Model Y cabin filter myself?',
         f'<p>Tesla publishes do-it-yourself guides for the Model Y filters on its service website{c("myint")}. Follow the guide for your exact car, or ask a '
         f'garage to do it with other checks. See <a href="/diy-jobs-ranked">DIY jobs ranked</a>.</p>'),
        ('Who repairs Model Y accident damage?',
         '<p>Your insurer handles accident claims; Tesla\'s own body repair centre and Tesla-approved body shops can do the work. A new windscreen needs '
         'the cameras recalibrating. See <a href="/bodywork-accident-repair">bodywork &amp; accident repair</a> and '
         '<a href="/windscreen-camera-calibration">windscreen calibration</a>.</p>'),
        recall_q(c, M),
    ]))
    b.append(related(['<a href="/models/model-3">Model 3</a>', '<a href="/models/model-s">Model S</a>', '<a href="/models/model-x">Model X</a>']))
    return page('model-y', 'Tesla Model Y Service & Repair UK: Questions Answered',
                'Tesla Model Y servicing in the UK: maintenance intervals, the 2026 front suspension knock bulletins, 12V or 16V battery, battery warranty and where to get it repaired.',
                'Tesla Model Y service and repair: your questions answered',
                'Short, sourced answers to what Model Y owners in the UK ask most: what servicing it needs, what tends to go wrong, what the warranty covers and where to get it fixed.',
                'Model Y', '\n'.join(b), c, 'Tesla Model Y service and repair: your questions answered')


def model_sx(m):
    c = Cites(); M = f'Model {m}'
    other = 'X' if m == 'S' else 'S'
    mcu_years = '2012–2018' if m == 'S' else '2016–2018'
    b = []
    b.append(section('servicing', 'Servicing', f'Tesla {M} servicing', [
        (f'Does a Tesla {M} need an annual service?',
         f'<p>No fixed one. Tesla lists individual maintenance items for the {M}, each with its own interval, instead of a yearly service'
         f'{c("msint" if m == "S" else "mxint")}. On an older or high-mileage {M}, a yearly check of suspension, tyres and brakes is still worthwhile.</p>'),
        (f'What maintenance does a {M} need, and when?', interval_list(c, m)),
        mot_q(c, M),
    ]))
    b.append(FINDER.format(h=f'Find a {M} specialist near you'))
    faults = [
        (f'What goes wrong on an older {M}?',
         f'<p>Worn suspension arms and bushes are a known issue on some older Model S and Model X; the car is heavy and has instant torque, so control arms, '
         f'ball joints and bushes work hard. A clunk under braking, a pull to one side or uneven tyre wear means it should be checked soon. '
         f'See <a href="/tesla-suspension-noise">suspension noise</a>.</p>'),
        (f'Why has my {M} touchscreen gone black?',
         f'<p>{M}s built {mcu_years} used an 8GB memory chip in the media control unit that can wear out, leaving the screen blank even after a restart. '
         f'Tesla recalled these cars in the UK in February 2021 and replaces the chip with a 64GB unit; cars built from March 2018 already had the larger chip{c("which")}. '
         f'See <a href="/tesla-touchscreen-black">touchscreen black</a>.</p>'),
        lv_q(c, M, f'{M}s built before the 2021 refresh have a 12V lead-acid battery; the 2021-on {M} has a lithium-ion one (usually about 16V).'),
        (f'Does my {M} have air suspension?',
         f'<p>Many Model S and Model X do. If yours does, turn on Jack Mode before the car is lifted on a ramp or jack, and tell the tyre or MOT garage. See <a href="/tesla-tyre-wear">tyre wear</a> and the <a href="/tesla-mot-guide">MOT guide</a>.</p>'),
    ]
    if m == 'X':
        faults.insert(1, ('Is the Model X covered by the control arm creak bulletin?',
                          f'<p>Tesla\'s bulletin SB-20-31-006 for front upper control arm creaks mainly covers 2018–2020 Model 3, but also includes some Model X{c("sb2020")}. '
                          f'Ask Tesla in the app whether it applies to your VIN.</p>'))
    b.append(section('common-faults', 'Common faults', f'What goes wrong on a {M}?', faults))
    b.append(section('warranty', 'Warranty', f'{M} warranty', [
        (f'How long is the {M} battery warranty?',
         f'<p>8 years or 150,000 miles, whichever comes first, with at least 70% of battery capacity retained{c("warr")}.</p>'),
        ('What does the basic warranty cover?',
         f'<p>4 years or 60,000 miles for cars bought after 1 January 2024; older cars keep the terms in force when they were bought. '
         f'A used Tesla bought from Tesla gets the rest of the basic warranty and then 1 year or 10,000 miles{c("warr")}. '
         f'See our <a href="/warranty-guide">Tesla warranty guide</a>.</p>'),
        independent_q(c, M),
    ]))
    b.append(section('repairs', 'Repairs', f'Getting a {M} repaired', [
        (f'Where can I get an out-of-warranty {M} repaired?',
         '<p>A Tesla Service Centre, or an independent EV specialist for work outside the warranty such as suspension, brakes, tyres and the low-voltage battery. '
         'Ask whether the garage has worked on your model before, and get a written quote. Compare <a href="/hevra-tesla-service">HEVRA-accredited specialists</a> '
         'and <a href="/other-tesla-services">independent garages</a>.</p>'),
        (f'Who repairs {M} accident damage?',
         '<p>Your insurer handles accident claims; Tesla\'s own body repair centre and Tesla-approved body shops can do the work. '
         'See <a href="/bodywork-accident-repair">bodywork &amp; accident repair</a> and <a href="/authorised-tesla-service">approved body shops</a>.</p>'),
        recall_q(c, M),
    ]))
    others = [f'<a href="/models/model-{x.lower()}">Model {x}</a>' for x in ('3', 'Y', other)]
    b.append(related(others))
    extra = 'touchscreen recall' if m == 'S' else 'control arm bulletin'
    return page(f'model-{m.lower()}', f'Tesla {M} Service & Repair UK: Questions Answered',
                f'Tesla {M} servicing in the UK: maintenance intervals, suspension wear, the {extra}, air suspension, 12V or 16V battery, 8-year battery warranty and repairs.',
                f'Tesla {M} service and repair: your questions answered',
                f'Short, sourced answers to what {M} owners in the UK ask most: what servicing it needs, what tends to go wrong, what the warranty covers and where to get it fixed.',
                M, '\n'.join(b), c, f'Tesla {M} service and repair: your questions answered')


def hub():
    c = Cites()
    cards = ''.join(f'<a class="card" href="/models/model-{k}"><strong>Model {n}</strong>{d}</a>' for k, n, d in [
        ('3', '3', 'Servicing, MOT fail points, the control arm creak, warranty.'),
        ('y', 'Y', 'Servicing, the 2026 suspension knock bulletins, filters, warranty.'),
        ('s', 'S', 'Servicing, suspension wear, touchscreen recall, air suspension.'),
        ('x', 'X', 'Servicing, suspension, touchscreen recall, air suspension.')])
    table = (
        '<div class="tbl"><table><thead><tr><th>Model</th><th>Battery &amp; drive unit warranty</th><th>Cabin filter</th><th>Low-voltage battery</th></tr></thead><tbody>'
        f'<tr><td><a href="/models/model-3">Model 3</a></td><td>8 years; 100,000 miles (RWD) or 120,000 miles (Long Range, Performance){c("warr")}</td><td>2 years{c("m3int")}</td><td>12V lead-acid before late 2021, lithium after{c("lv")}</td></tr>'
        f'<tr><td><a href="/models/model-y">Model Y</a></td><td>8 years; 100,000 miles (RWD) or 120,000 miles (Long Range, Performance){c("warr")}</td><td>2 years; HEPA/carbon 3 years{c("myint")}</td><td>12V lead-acid before late 2021, lithium after{c("lv")}</td></tr>'
        f'<tr><td><a href="/models/model-s">Model S</a></td><td>8 years or 150,000 miles{c("warr")}</td><td>3 years{c("msint")}</td><td>12V lead-acid before the 2021 refresh, lithium after{c("lv")}</td></tr>'
        f'<tr><td><a href="/models/model-x">Model X</a></td><td>8 years or 150,000 miles{c("warr")}</td><td>3 years{c("mxint")}</td><td>12V lead-acid before the 2021 refresh, lithium after{c("lv")}</td></tr>'
        '</tbody></table></div>'
        '<p>Every battery and drive unit term includes at least 70% battery capacity retained over the period. All four models share the same brake fluid check (every 4 years), '
        'tyre rotation (6,250 miles), yearly wiper blades and yearly caliper service on salted roads.</p>')
    b = [section('choose', 'Choose your model', 'Service and repair answers for each Tesla', [], intro=f'<div class="cards">{cards}</div>'),
         section('compare', 'At a glance', 'Tesla models compared: warranty and maintenance', [], intro=table),
         section('all-models', 'Every model', 'Questions that apply to every Tesla', [
             ('Do Teslas need servicing?',
              f'<p>Yes, but not an annual oil-and-filter service. Each model has a short list of maintenance items with their own intervals{c("m3int")}. '
              f'See the <a href="/tesla-service-schedule">Tesla service schedule</a> and <a href="/before-you-book-service">before you book a service</a>.</p>'),
             ('What goes wrong most on a Tesla?',
              '<p>Tyres, suspension and brakes come up most often, along with the low-voltage battery. Our <a href="/known-issues-by-model">known issues guide</a> '
              'and the <a href="/symptom-checker">symptom checker</a> cover what owners report.</p>'),
             ('Where can I get a Tesla repaired?',
              '<p>At a Tesla Service Centre, booked in the app, or at an independent EV specialist for work outside the warranty. Use the finder below, or see '
              '<a href="/places">Tesla repair near any town or village</a>.</p>'),
         ]),
         FINDER.format(h='Find a Tesla garage near you')]
    return page('', 'Tesla Service & Repair by Model: 3, Y, S and X (UK)',
                'Service and repair answers for each Tesla model in the UK: maintenance intervals, known faults, battery warranty and low-voltage battery for the Model 3, Y, S and X.',
                'Tesla service and repair by model',
                'Pick your Tesla for short, sourced answers on servicing, common faults, warranty and repairs, or compare all four models at a glance.',
                'Models', '\n'.join(b), c, 'Tesla service and repair by model')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    pages = {'index.html': hub(), 'model-3.html': model_3(), 'model-y.html': model_y(),
             'model-s.html': model_sx('S'), 'model-x.html': model_sx('X')}
    for f, t in pages.items():
        open(os.path.join(OUT, f), 'w', encoding='utf-8').write(t)
    print('wrote', len(pages), 'pages to site/models/')
