// Exports poster SVGs to print files: export/NN-name.pdf (A3, vector text)
// and export/NN-name.png (A3 at 300 dpi, portrait or landscape from the SVG's size).
// Run from this folder:
//   node render.js                      all posters, PDF + PNG
//   node render.js --png 07 08          only posters 07 and 08, PNG only
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const args = process.argv.slice(2);
  const pngOnly = args.includes('--png');
  const only = args.filter(a => /^\d\d$/.test(a));
  const dir = __dirname;
  const out = path.join(dir, 'export');
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const files = fs.readdirSync(dir).filter(f => /^\d\d-.*\.svg$/.test(f)).sort()
    .filter(f => !only.length || only.includes(f.slice(0, 2)));
  for (const file of files) {
    const base = file.replace(/\.svg$/, '');
    const landscape = /width="420mm"/.test(fs.readFileSync(path.join(dir, file), 'utf8').slice(0, 400000));
    const [w, h] = landscape ? [420, 297] : [297, 420];
    // 1 mm = 3.7795 CSS px; scale 3.125 gives 300 dpi
    const page = await browser.newPage({
      viewport: { width: Math.ceil(w * 3.7795), height: Math.ceil(h * 3.7795) }, deviceScaleFactor: 3.125 });
    await page.goto('file://' + path.join(dir, file));
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(out, base + '.png') });
    if (!pngOnly) {
      await page.pdf({ path: path.join(out, base + '.pdf'), width: w + 'mm', height: h + 'mm', printBackground: true, pageRanges: '1' });
    }
    await page.close();
    console.log('exported', base);
  }
  await browser.close();
})();
