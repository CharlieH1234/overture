// Read the public stats of every video on a TikTok profile.
//
// Usage:
//   node content-engine/scripts/tiktok_profile_stats.js <profile url> <out dir>
//
// Opens the profile in headless Chromium (through the session's proxy),
// scrolls it, & records TikTok's own /api/post/item_list/ responses. Writes
// <out dir>/videos.json: [{ id, url, desc, createTime, isPhoto, slideCount,
// views, likes, comments, saves, shares, cover }] (cover is TikTok's cover URL)
// & downloads each cover to <out dir>/covers/<id>.jpg.
//
// Needs www.tiktok.com & TikTok's CDN hosts allowed in the cloud environment.
// Only public numbers are read; no login.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const [url, out] = process.argv.slice(2);
  if (!url || !out) { console.error('usage: tiktok_profile_stats.js <profile url> <out dir>'); process.exit(2); }
  fs.mkdirSync(path.join(out, 'covers'), { recursive: true });
  const b = await chromium.launch({ proxy: process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined });
  const ctx = await b.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 }, locale: 'en-GB', ignoreHTTPSErrors: false,
  });
  const p = await ctx.newPage();
  const items = new Map(); let hasMore = true; let sawApi = false;
  p.on('response', async r => {
    if (!r.url().includes('/api/post/item_list/')) return;
    sawApi = true;
    try { const j = await r.json(); (j.itemList || []).forEach(it => items.set(it.id, it)); hasMore = !!j.hasMore; } catch (e) {}
  });
  await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await p.waitForTimeout(8000);
  // The first page of videos can also be embedded in the HTML
  try {
    const raw = await p.$eval('#__UNIVERSAL_DATA_FOR_REHYDRATION__', el => el.textContent);
    const j = JSON.parse(raw); const scope = j.__DEFAULT_SCOPE__ || {};
    const list = scope['webapp.user-detail']?.itemList || [];
    list.forEach(it => it?.id && items.set(it.id, it));
  } catch (e) {}
  let still = 0, last = 0;
  for (let i = 0; i < 80 && (hasMore || items.size === 0); i++) {
    await p.mouse.wheel(0, 5000); await p.waitForTimeout(1800);
    if (items.size === last) { if (++still > 8) break; } else { still = 0; last = items.size; }
  }
  const handle = (url.match(/@([^/?]+)/) || [])[1] || '';
  const videos = [...items.values()].map(it => {
    const s = it.statsV2 || it.stats || {};
    const n = v => (v === undefined || v === null ? null : Number(v));
    const isPhoto = !!it.imagePost;
    return {
      id: it.id, url: `https://www.tiktok.com/@${handle}/${isPhoto ? 'photo' : 'video'}/${it.id}`,
      desc: it.desc || '', createTime: it.createTime ? new Date(it.createTime * 1000).toISOString() : null,
      isPhoto, slideCount: isPhoto ? (it.imagePost.images || []).length : null,
      views: n(s.playCount), likes: n(s.diggCount), comments: n(s.commentCount), saves: n(s.collectCount), shares: n(s.shareCount),
      cover: (isPhoto ? it.imagePost?.cover?.imageURL?.urlList?.[0] : null) || it.video?.cover || it.video?.originCover || null,
    };
  });
  for (const v of videos) {
    if (!v.cover) continue;
    try {
      const r = await ctx.request.get(v.cover, { timeout: 30000 });
      if (r.ok()) fs.writeFileSync(path.join(out, 'covers', v.id + '.jpg'), await r.body());
    } catch (e) {}
  }
  fs.writeFileSync(path.join(out, 'videos.json'), JSON.stringify(videos, null, 1));
  console.log(JSON.stringify({ videos: videos.length, sawApi, hasMore }));
  await b.close();
})();
