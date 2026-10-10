// node render.mjs <pasta-com-cena.js> <saida.mp4|--quadros t1,t2,...> [--fps 30] [--dur N] [--palco longo]
// Mesmo método do eventosextremospub: página 1080x1920, quadro a quadro, render(t) → screenshot → ffmpeg.
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const aqui = path.dirname(fileURLToPath(import.meta.url));
const [, , pasta, saida, ...resto] = process.argv;
const opt = k => { const i = resto.indexOf(k); return i >= 0 ? resto[i + 1] : null; };
const fps = Number(opt('--fps') || 30);

// --palco longo → motor/longo.html (16:9, cenas do explicavideo v2) lendo <pasta>/cena-longo.js
const LONGO = opt('--palco') === 'longo';
const [W, H] = LONGO ? [1920, 1080] : [1080, 1920];
const html = fs.readFileSync(path.join(aqui, LONGO ? 'longo.html' : 'palco.html'), 'utf8')
  .replace('<head>', `<head><base href="file://${aqui}/">`)
  .replace('src="cena.js"', `src="file://${path.resolve(pasta, LONGO ? 'cena-longo.js' : 'cena.js')}"`);
const tmp = path.resolve(pasta, LONGO ? '.longo.html' : '.palco.html');
fs.writeFileSync(tmp, html);

const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
const page = await browser.newPage({ viewport: { width: W, height: H } });
page.on('pageerror', e => console.error('pageerror', e.message));
await page.goto('file://' + tmp);
await page.waitForFunction(() => window.pronto && window.render, null, { timeout: 60000 });
await page.evaluate(() => window.pronto);
const dur = Number(opt('--dur') || await page.evaluate(() => window.CENA.duracao));

if (saida === '--quadros') {
  const ts = (opt('--quadros') || resto[0]).split(',').map(Number);
  for (const t of ts) {
    await page.evaluate(t => window.render(t), t);
    const f = path.resolve(pasta, `q_${String(t).replace('.', '_')}.jpg`);
    await page.screenshot({ path: f, type: 'jpeg', quality: 85 });
    console.log(f);
  }
} else {
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', saida], { stdio: ['pipe', 'inherit', 'inherit'] });
  const n = Math.round(dur * fps); const t0 = Date.now();
  for (let i = 0; i < n; i++) {
    await page.evaluate(t => window.render(t), i / fps);
    const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 60 === 0) process.stderr.write(`\r${i}/${n} ${((Date.now() - t0) / 1000 / (i + 1)).toFixed(2)}s/quadro `);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  console.error(`\nok ${saida}`);
}
await browser.close();
fs.unlinkSync(tmp);
