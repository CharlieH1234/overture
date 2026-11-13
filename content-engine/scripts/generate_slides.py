#!/usr/bin/env python3
"""Generate text-free TikTok slide photos for one Overture engine post.

Usage:
  python3 -I generate_slides.py <prompts.json> <out_dir>

prompts.json:
  {"model": "gpt-image-1.5",
   "base": "shared description used for every slide (person, room, camera, light)",
   "slides": ["slide 1 changes", "slide 2 changes", ...]}

For each slide it asks the OpenAI Images API for a 1024x1536 image, then
centre-crops it to 9:16 and resizes it to 1080x1920 (an upscale of about 1.25x),
writing <out_dir>/slide<N>.jpg. Raw API images are kept as slide<N>_raw.png.
Slides that already exist are skipped, so a failed run can be re-run.

The request is streamed: in the cloud environment the proxy drops non-streamed
requests that take longer than about 30 seconds, and high-quality images take longer.
The API key is added by the environment's proxy, so the Authorization header
here is a placeholder.
"""
import base64
import concurrent.futures as cf
import json
import os
import ssl
import sys
import urllib.error
import urllib.request

from PIL import Image

API = 'https://api.openai.com/v1/images/generations'
CA = '/root/.ccr/ca-bundle.crt'
W, H = 1080, 1920


def generate(model, prompt, raw_path):
    body = json.dumps({'model': model, 'prompt': prompt, 'size': '1024x1536', 'quality': 'high',
                       'n': 1, 'stream': True, 'partial_images': 2}).encode()
    req = urllib.request.Request(API, data=body, headers={
        'Content-Type': 'application/json', 'Authorization': 'Bearer proxy-injected'})
    ctx = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
    final = None
    with urllib.request.urlopen(req, timeout=300, context=ctx) as r:
        for line in r:
            line = line.decode().strip()
            if not line.startswith('data:'):
                continue
            ev = json.loads(line[5:])
            if ev.get('type') == 'image_generation.completed':
                final = ev['b64_json']
            elif 'error' in ev:
                raise RuntimeError(str(ev['error'])[:300])
    if not final:
        raise RuntimeError('no completed image in the stream')
    with open(raw_path, 'wb') as f:
        f.write(base64.b64decode(final))


def finish(raw_path, out_path):
    im = Image.open(raw_path).convert('RGB')
    w, h = im.size
    cw = min(w, round(h * 9 / 16))
    ch = min(h, round(cw * 16 / 9))
    left, top = (w - cw) // 2, (h - ch) // 2
    im = im.crop((left, top, left + cw, top + ch)).resize((W, H), Image.LANCZOS)
    im.save(out_path, 'JPEG', quality=90, optimize=True, progressive=True)


def one(model, base, i, extra, out_dir):
    raw = os.path.join(out_dir, f'slide{i}_raw.png')
    out = os.path.join(out_dir, f'slide{i}.jpg')
    if os.path.exists(out):
        return f'slide {i}: already done'
    try:
        if not (os.path.exists(raw) and os.path.getsize(raw) > 10000):
            generate(model, base + '\n\n' + extra, raw)
        finish(raw, out)
        return f'slide {i}: ok'
    except urllib.error.HTTPError as e:
        return f'slide {i}: HTTP {e.code} {e.read()[:300]!r}'
    except Exception as e:  # report and carry on with the other slides
        return f'slide {i}: {e}'


def main():
    prompts = json.load(open(sys.argv[1]))
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    model = prompts.get('model', 'gpt-image-1.5')
    with cf.ThreadPoolExecutor(3) as ex:
        jobs = [ex.submit(one, model, prompts['base'], i + 1, s, out_dir) for i, s in enumerate(prompts['slides'])]
        for j in jobs:
            print(j.result(), flush=True)


if __name__ == '__main__':
    main()
