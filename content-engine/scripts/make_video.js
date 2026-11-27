// Turn a post's slides + their text into one 9:16 MP4 slideshow.
//
// Usage:
//   node content-engine/scripts/make_video.js <post.json> <slides dir> <out.mp4> [secondsPerSlide] [fadeSeconds]
//
// post.json: { "overlays": [{ "text", "style", "y", "size", "width", "lineHeight", "card" }, ...] }  (the post doc's overlays)
// slides dir: slide1.jpg, slide2.jpg, ... (the text-free 1080x1920 slides, in order)
//
// Each slide is drawn with its text exactly as the engine page draws it (the .sl/.ov CSS below is a copy of
// index.html's; keep the two in step), screenshotted at 1080x1920 with Playwright, then ffmpeg joins the frames
// with a cross-dissolve ("fade" xfade). Defaults: 2.5 s of each slide on screen + a 0.5 s dissolve.
// Output: H.264 (yuv420p, 30 fps, faststart) with a silent AAC track, all metadata stripped (-map_metadata -1).
// Also writes <out>.jpg (first frame, 270x480) for the page's poster image.
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const CSS = `
html,body{margin:0;background:#000}
.sl{position:relative;display:block;width:1080px;height:1920px;container-type:inline-size;overflow:hidden}
.sl img{width:100%;height:100%;object-fit:cover;display:block}
.ov{position:absolute;left:50%;transform:translate(-50%,-50%);text-align:center;white-space:pre-line;color:#fff;overflow-wrap:break-word}
.ov.serif,.ov.serif-bold{font-family:Georgia,"Times New Roman",serif;text-shadow:0 .4cqw 2cqw rgba(0,0,0,.75)}
.ov.serif-bold{font-weight:700}
.ov.tiktok{font-family:"Segoe UI","Helvetica Neue",Arial,sans-serif;font-weight:700;text-shadow:0 .5cqw 2.4cqw rgba(0,0,0,.75)}
.ov.outline{font-family:Arial,sans-serif;font-weight:700;-webkit-text-stroke:1.4cqw rgba(0,0,0,.85);paint-order:stroke fill}
.ov-card{position:absolute;left:0;right:0;bottom:0;background:#F6EEDF;color:#3B2A1A;padding:4cqw 7cqw;text-align:center;font:italic 4.2cqw/1.3 Georgia,serif}
.ov-card .b{font-style:normal;font-size:3.2cqw;color:#6B5840;margin-top:2cqw}`;
const OV_WIDTH = { outline: 0.8, tiktok: 0.82, serif: 0.72, 'serif-bold': 0.8 };
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

function overlay(o) {
  if (!o) return '';
  const st = OV_WIDTH[o.style] ? o.style : 'outline';
  const text = o.text ? `<div class="ov ${st}" style="top:${(o.y ?? 0.4) * 100}%;width:${(o.width || OV_WIDTH[st]) * 100}%;font-size:${(o.size || 0.065) * 100}cqw;line-height:${o.lineHeight || 1.25}">${esc(o.text)}</div>` : '';
  const card = o.card ? `<div class="ov-card" style="top:${o.card.top * 100}%">${esc(o.card.title || '')}${o.card.body ? `<div class="b">${esc(o.card.body)}</div>` : ''}</div>` : '';
  return card + text;
}

(async () => {
  const [postFile, slidesDir, out, perArg, fadeArg] = process.argv.slice(2);
  if (!postFile || !slidesDir || !out) { console.error('usage: make_video.js <post.json> <slides dir> <out.mp4> [secondsPerSlide] [fadeSeconds]'); process.exit(2); }
  const per = Number(perArg || 2.5), fade = Number(fadeArg || 0.5);
  const post = JSON.parse(fs.readFileSync(postFile, 'utf8'));
  const slides = fs.readdirSync(slidesDir).filter(f => /^slide\d+\.jpg$/.test(f)).sort((a, b) => parseInt(a.slice(5)) - parseInt(b.slice(5)));
  if (!slides.length) { console.error('no slide<N>.jpg files in ' + slidesDir); process.exit(1); }
  const work = fs.mkdtempSync(path.join(path.dirname(path.resolve(out)), '.frames-'));
  const b = await chromium.launch();
  const page = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  const frames = [];
  for (const [i, f] of slides.entries()) {
    const img = 'data:image/jpeg;base64,' + fs.readFileSync(path.join(slidesDir, f)).toString('base64');
    await page.setContent(`<!doctype html><meta charset="utf-8"><style>${CSS}</style><span class="sl"><img src="${img}">${overlay(post.overlays?.[i])}</span>`);
    await page.waitForLoadState('load'); await page.evaluate(() => document.fonts.ready);
    const fr = path.join(work, `f${i + 1}.png`);
    await page.locator('.sl').screenshot({ path: fr });
    frames.push(fr);
  }
  await b.close();

  // Each input is shown per+fade seconds; consecutive inputs overlap by `fade` (the dissolve), so each slide
  // holds about `per` seconds on its own. Offsets: k*per for the k-th transition.
  const hold = per + fade, args = ['-y', '-v', 'error'];
  frames.forEach(fr => args.push('-loop', '1', '-t', String(hold), '-framerate', '30', '-i', fr));
  const total = frames.length * per + fade;
  args.push('-f', 'lavfi', '-t', String(total), '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100');
  let chain = frames.map((_, i) => `[${i}:v]scale=1080:1920,setsar=1,format=yuv420p,fps=30[v${i}]`).join(';');
  let last = 'v0';
  for (let k = 1; k < frames.length; k++) {
    chain += `;[${last}][v${k}]xfade=transition=fade:duration=${fade}:offset=${(k * per).toFixed(3)}[x${k}]`;
    last = `x${k}`;
  }
  args.push('-filter_complex', chain, '-map', `[${last}]`, '-map', `${frames.length}:a`,
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', '30',
    '-c:a', 'aac', '-b:a', '96k', '-shortest', '-movflags', '+faststart', '-map_metadata', '-1', '-fflags', '+bitexact', out);
  execFileSync('ffmpeg', args, { stdio: 'inherit' });
  execFileSync('ffmpeg', ['-y', '-v', 'error', '-i', frames[0], '-vf', 'scale=270:480', '-q:v', '4', out.replace(/\.mp4$/, '') + '.jpg']);
  fs.rmSync(work, { recursive: true, force: true });
  const dur = execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out]).toString().trim();
  console.log(JSON.stringify({ out, slides: frames.length, seconds: Number(Number(dur).toFixed(2)), bytes: fs.statSync(out).size }));
})().catch(e => { console.error(e.message || e); process.exit(1); });
