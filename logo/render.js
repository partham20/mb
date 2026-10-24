// Renders every logo SVG in svg/ to png/ at its own size x2 (transparent where the SVG has no background).
// Run from this folder:  node render.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const src = path.join(__dirname, 'svg');
  const out = path.join(__dirname, 'png');
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  for (const file of fs.readdirSync(src).filter(f => f.endsWith('.svg')).sort()) {
    const svg = fs.readFileSync(path.join(src, file), 'utf8');
    const [, w, h] = svg.match(/width="(\d+)" height="(\d+)"/);
    const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 2 });
    await page.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
    await page.locator('svg').screenshot({ path: path.join(out, file.replace('.svg', '.png')), omitBackground: true });
    await page.close();
    console.log('rendered', file);
  }
  await browser.close();
})();
