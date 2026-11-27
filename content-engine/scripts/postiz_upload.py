#!/usr/bin/env python3
"""Upload a post's Telegram-processed slides to the Postiz media library.

Usage:
  python3 -I postiz_upload.py <post_dir>            # photo post: slide<N>_tg.jpg
  python3 -I postiz_upload.py <post_dir> --video    # video post: video_tg.mp4

Uploads <post_dir>/slide1_tg.jpg, slide2_tg.jpg, ... (the copies made by
telegram_compress.py; plain slide<N>.jpg files are never uploaded) to
POST https://api.postiz.com/public/v1/upload, in slide order, and prints one JSON
line: [{"id": ..., "path": ...}, ...]. It also writes that list to
<post_dir>/postiz_media.json. The paths are then used as attachments when the
post is scheduled with the Postiz MCP tool.

Needs the Postiz public API key in the environment variable POSTIZ_API_KEY (set
by the operator in the cloud environment's settings) and api.postiz.com
reachable. Postiz expects the raw key in the Authorization header, with no
prefix. The key is never printed. Each slide is one API call; Postiz Cloud
allows about 30 calls an hour.
"""
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
import uuid

CA = '/root/.ccr/ca-bundle.crt'
URL = 'https://api.postiz.com/public/v1/upload'


def die(msg):
    print('ERROR: ' + msg, file=sys.stderr)
    sys.exit(1)


def upload(key, path, ctype='image/jpeg'):
    boundary = uuid.uuid4().hex
    with open(path, 'rb') as f:
        data = f.read()
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{os.path.basename(path)}"\r\n'
            f'Content-Type: {ctype}\r\n\r\n').encode() + data + f'\r\n--{boundary}--\r\n'.encode()
    req = urllib.request.Request(URL, data=body, headers={
        'Authorization': key, 'Content-Type': f'multipart/form-data; boundary={boundary}'})
    ctx = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=300, context=ctx) as r:
        res = json.load(r)
    if not res.get('id') or not res.get('path'):
        die(f'unexpected upload response for {os.path.basename(path)}: {json.dumps(res)[:200]}')
    return {'id': res['id'], 'path': res['path']}


def main():
    if len(sys.argv) not in (2, 3) or (len(sys.argv) == 3 and sys.argv[2] != '--video'):
        die('usage: postiz_upload.py <post_dir> [--video]')
    post_dir, video = sys.argv[1], len(sys.argv) == 3
    key = os.environ.get('POSTIZ_API_KEY', '').strip()
    if not key:
        die('POSTIZ_API_KEY must be set in the environment')
    if video:
        files = ['video_tg.mp4'] if os.path.exists(os.path.join(post_dir, 'video_tg.mp4')) else []
        if not files:
            die(f'no video_tg.mp4 in {post_dir}: run telegram_video.py first')
    else:
        files = sorted((f for f in os.listdir(post_dir) if f.startswith('slide') and f.endswith('_tg.jpg')),
                       key=lambda f: int(f[5:].split('_')[0]))
        if not files:
            die(f'no slide<N>_tg.jpg files in {post_dir}: run telegram_compress.py first')
    media = []
    for name in files:
        try:
            media.append(upload(key, os.path.join(post_dir, name), 'video/mp4' if video else 'image/jpeg'))
        except urllib.error.HTTPError as e:
            hint = ' (rate limit: about 30 calls an hour)' if e.code == 429 else ' (check POSTIZ_API_KEY)' if e.code in (401, 403) else ''
            die(f'Postiz returned HTTP {e.code} for {name}{hint}')
        except urllib.error.URLError as e:
            die(f'Postiz could not be reached for {name}: {e.reason}')
    with open(os.path.join(post_dir, 'postiz_media.json'), 'w') as f:
        json.dump(media, f)
    print(json.dumps(media))


if __name__ == '__main__':
    main()
