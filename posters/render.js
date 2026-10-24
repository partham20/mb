// Exports every poster SVG to print files: export/NN-name.pdf (A3, vector text)
// and export/NN-name.png (3508 x 4961 px = A3 at 300 dpi).
// Run from this folder:  node render.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const dir = __dirname;
  const out = path.join(dir, 'export');
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  // 297 mm = 1122.5 CSS px; scale 3.125 gives 300 dpi
  const page = await browser.newPage({ viewport: { width: 1123, height: 1588 }, deviceScaleFactor: 3.125 });
  for (const file of fs.readdirSync(dir).filter(f => /^\d\d-.*\.svg$/.test(f)).sort()) {
    const base = file.replace(/\.svg$/, '');
    await page.goto('file://' + path.join(dir, file));
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(out, base + '.png') });
    await page.pdf({ path: path.join(out, base + '.pdf'), width: '297mm', height: '420mm', printBackground: true, pageRanges: '1' });
    console.log('exported', base);
  }
  await browser.close();
})();
