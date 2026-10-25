// Renders intro.html frame by frame, then muxes it with intro-audio.wav into an MP4.
//   node render.js                 full 12 s video -> out/intro-1080x1920.mp4
//   node render.js --stills 1 3 5  PNG stills at those seconds -> out/still-<t>.png
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const FPS = 30, DURATION = 12;

(async () => {
  const args = process.argv.slice(2);
  const out = path.join(__dirname, 'out');
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(__dirname, 'intro.html'));
  await page.evaluate(() => document.fonts.ready);

  if (args[0] === '--stills') {
    for (const s of args.slice(1)) {
      await page.evaluate(t => setTime(t), +s);
      await page.screenshot({ path: path.join(out, `still-${s}.png`) });
    }
  } else {
    const frames = path.join(out, 'frames');
    fs.rmSync(frames, { recursive: true, force: true });
    fs.mkdirSync(frames);
    for (let i = 0; i < FPS * DURATION; i++) {
      await page.evaluate(t => setTime(t), i / FPS);
      await page.screenshot({ path: path.join(frames, String(i).padStart(4, '0') + '.jpg'), type: 'jpeg', quality: 95 });
    }
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(frames, '%04d.jpg'),
      '-i', path.join(__dirname, 'intro-audio.wav'), '-c:v', 'libx264', '-preset', 'slow', '-crf', '16',
      '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart',
      path.join(out, 'intro-1080x1920.mp4')]);
    fs.rmSync(frames, { recursive: true, force: true });
    console.log('wrote out/intro-1080x1920.mp4');
  }
  await browser.close();
})();
