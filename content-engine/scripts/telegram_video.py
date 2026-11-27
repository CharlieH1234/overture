#!/usr/bin/env python3
"""Send a post's slideshow video through Telegram and download the copy Telegram keeps.

Usage:
  python3 -I telegram_video.py <post_dir>

Sends <post_dir>/video.mp4 (made by make_video.js) to the bot chat with sendVideo
and downloads the file Telegram stores as <post_dir>/video_tg.mp4; only that copy
goes on to Postiz (postiz_upload.py --video). make_video.js already strips all
metadata with ffmpeg; this is the same Telegram pass the photo posts get.
Telegram's Bot API can only hand back files up to 20 MB, so the video must be
smaller than that (a 3 to 8 slide video is usually 1 to 5 MB).

Same bot and chat as telegram_compress.py: Memorypalace_slides_bot (or
TELEGRAM_BOT_TOKEN) and TELEGRAM_CHAT_ID in the environment. The token is never
printed. No local fallback: if Telegram fails, nothing should be uploaded.
"""
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
import uuid

CA = '/root/.ccr/ca-bundle.crt'
LIMIT = 20 * 1024 * 1024


def ctx():
    return ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()


def die(msg):
    print('ERROR: ' + msg, file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) != 2:
        die('usage: telegram_video.py <post_dir>')
    post_dir = sys.argv[1]
    token = (os.environ.get('TELEGRAM_BOT_TOKEN') or os.environ.get('Memorypalace_slides_bot') or '').strip()
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '').strip()
    if not token or not chat_id:
        die('Set Memorypalace_slides_bot (or TELEGRAM_BOT_TOKEN) and TELEGRAM_CHAT_ID in the environment')
    src = os.path.join(post_dir, 'video.mp4')
    if not os.path.exists(src):
        die(f'no video.mp4 in {post_dir}: run make_video.js first')
    if os.path.getsize(src) >= LIMIT:
        die('video.mp4 is 20 MB or more: Telegram bots cannot download it back')
    label = os.path.basename(os.path.normpath(post_dir))
    boundary = uuid.uuid4().hex
    parts = [f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
             for k, v in (('chat_id', chat_id), ('caption', f'{label} video'), ('supports_streaming', 'true'))]
    with open(src, 'rb') as f:
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="video"; filename="video.mp4"\r\n'
                     'Content-Type: video/mp4\r\n\r\n'.encode() + f.read() + b'\r\n')
    parts.append(f'--{boundary}--\r\n'.encode())
    try:
        req = urllib.request.Request(f'https://api.telegram.org/bot{token}/sendVideo', data=b''.join(parts),
                                     headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
        with urllib.request.urlopen(req, timeout=300, context=ctx()) as r:
            res = json.load(r)
        if not res.get('ok'):
            die(f'sendVideo failed: {res.get("description")}')
        msg = res['result']
        file_id = (msg.get('video') or msg.get('document') or {}).get('file_id')
        if not file_id:
            die('Telegram did not return the video')
        with urllib.request.urlopen(f'https://api.telegram.org/bot{token}/getFile?file_id={file_id}', timeout=60, context=ctx()) as r:
            res = json.load(r)
        if not res.get('ok'):
            die(f'getFile failed: {res.get("description")}')
        with urllib.request.urlopen(f'https://api.telegram.org/file/bot{token}/{res["result"]["file_path"]}', timeout=300, context=ctx()) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        die(f'Telegram returned HTTP {e.code}')
    except urllib.error.URLError as e:
        die(f'Telegram could not be reached: {e.reason}')
    with open(os.path.join(post_dir, 'video_tg.mp4'), 'wb') as f:
        f.write(data)
    print(f'video: sent and downloaded ({len(data)} bytes)')


if __name__ == '__main__':
    main()
