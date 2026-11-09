// Live browser check of the garage finder's place search: node tools/live_search.mjs [base-url]
// Opens the finder pages in Chromium (desktop and phone), types each place, presses Search (and Enter on the
// phone) and checks the note names the right place and garages are listed. Exit 1 on any miss.
import { chromium, devices } from 'playwright';
const BASE = process.argv[2] || 'https://teslaservice.co.uk';
const CASES = [
  ['Poulton', 'Poulton-le-Fylde'], ['Brixton', 'Brixton, Lambeth'], ['Peckham', 'Peckham, Southwark'],
  ['Crystal Palace', 'Crystal Palace'], ['Newport', 'Newport, Wales'], ['brixton', 'Brixton, Lambeth'],
  ['Peckham ', 'Peckham, Southwark'], ['Kent', 'Kent'], ['M1 1AE', 'M1 1AE'],
];
const PAGES = ['/', '/tesla-service-centers'];
const b = await chromium.launch();
let bad = 0;
for (const [label, ctxOpts, useEnter] of [['desktop', {}, false], ['phone', { ...devices['iPhone 13'] }, true]]) {
  const ctx = await b.newContext(ctxOpts);
  for (const pagePath of PAGES) {
    const pg = await ctx.newPage();
    const errs = [], calls = [];
    pg.on('pageerror', e => errs.push(e.message));
    pg.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    pg.on('request', r => { if (/places\/find|postcodes\.io/.test(r.url())) calls.push(r.url().replace(BASE, '')); });
    await pg.goto(BASE + pagePath + '?nocache=' + Date.now(), { waitUntil: 'networkidle' });
    const js = await pg.$$eval('script[src*="finder.js"]', s => s.map(x => x.getAttribute('src')));
    for (const [q, want] of CASES) {
      calls.length = 0;
      await pg.fill('#search', q);
      if (useEnter) await pg.press('#search', 'Enter'); else await pg.click('#searchBtn');
      await pg.waitForFunction(() => !/Finding/.test(document.getElementById('finderNote').textContent), null, { timeout: 15000 }).catch(() => {});
      const note = (await pg.textContent('#finderNote')).trim();
      const n = await pg.$$eval('#listings .listing', e => e.length);
      const ok = note.startsWith('Closest results to ' + want) && n > 0;
      if (!ok) bad++;
      console.log(`${ok ? 'ok  ' : 'FAIL'} ${label} ${pagePath} [${js}] "${q}" -> ${n} rows | ${note.slice(0, 140)} | calls: ${calls.join(' ')}${errs.length ? ' | errors: ' + errs.join('; ') : ''}`);
      errs.length = 0;
    }
    await pg.close();
  }
  await ctx.close();
}
await b.close();
console.log(bad ? `${bad} failed` : 'all passed');
process.exit(bad ? 1 : 0);
