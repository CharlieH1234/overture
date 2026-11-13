#!/usr/bin/env python3
"""Send a post's slide photos through Telegram and download Telegram's re-encoded copies.

Usage:
  python3 -I telegram_compress.py <post_dir>

Reads <post_dir>/slide1.jpg, slide2.jpg, ... (text-free photos), sends each to the
bot chat as a photo, then downloads Telegram's re-encoded JPEG as
<post_dir>/slide<N>_tg.jpg. This strips the AI-generation metadata and gives a
phone-style JPEG, the same step the Palace engine uses (tiktok-app-marketing
skill, "Telegram Metadata Wipe"). Only the *_tg.jpg files go on to Postiz.

Needs the environment variables TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID (set in
the cloud environment's settings by the operator, the same values as Memory
Palace) and api.telegram.org reachable. The token is never printed.

There is no local fallback: if Telegram can't be reached or a credential is
missing, the script stops with an error, and nothing should be uploaded.
"""
import json
import os
import ssl
import sys
import urllib.request
import uuid

CA = '/root/.ccr/ca-bundle.crt'


def ctx():
    return ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()


def die(msg):
    print('ERROR: ' + msg, file=sys.stderr)
    sys.exit(1)


def send_photo(token, chat_id, path, caption):
    boundary = uuid.uuid4().hex
    parts = []
    for name, value in (('chat_id', chat_id), ('caption', caption)):
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    with open(path, 'rb') as f:
        data = f.read()
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="photo"; filename="{os.path.basename(path)}"\r\n'
                 'Content-Type: image/jpeg\r\n\r\n'.encode() + data + b'\r\n')
    parts.append(f'--{boundary}--\r\n'.encode())
    req = urllib.request.Request(f'https://api.telegram.org/bot{token}/sendPhoto', data=b''.join(parts),
                                 headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
    with urllib.request.urlopen(req, timeout=120, context=ctx()) as r:
        res = json.load(r)
    if not res.get('ok'):
        die(f'sendPhoto failed for {os.path.basename(path)}: {res.get("description")}')
    # Telegram returns several sizes; the last is the largest
    return res['result']['photo'][-1]['file_id']


def download(token, file_id, out_path):
    with urllib.request.urlopen(f'https://api.telegram.org/bot{token}/getFile?file_id={file_id}', timeout=60, context=ctx()) as r:
        res = json.load(r)
    if not res.get('ok'):
        die(f'getFile failed: {res.get("description")}')
    with urllib.request.urlopen(f'https://api.telegram.org/file/bot{token}/{res["result"]["file_path"]}', timeout=120, context=ctx()) as r:
        data = r.read()
    with open(out_path, 'wb') as f:
        f.write(data)
    return len(data)


def main():
    if len(sys.argv) != 2:
        die('usage: telegram_compress.py <post_dir>')
    post_dir = sys.argv[1]
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip()
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '').strip()
    if not token or not chat_id:
        die('TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in the environment')
    slides = sorted((f for f in os.listdir(post_dir) if f.startswith('slide') and f.endswith('.jpg') and '_' not in f),
                    key=lambda f: int(f[5:-4]))
    if not slides:
        die(f'no slide<N>.jpg files in {post_dir}')
    label = os.path.basename(os.path.normpath(post_dir))
    for name in slides:
        n = name[5:-4]
        try:
            file_id = send_photo(token, chat_id, os.path.join(post_dir, name), f'{label} slide {n}')
            size = download(token, file_id, os.path.join(post_dir, f'slide{n}_tg.jpg'))
        except urllib.error.HTTPError as e:
            die(f'Telegram returned HTTP {e.code} for slide {n}')
        except urllib.error.URLError as e:
            die(f'Telegram could not be reached for slide {n}: {e.reason}')
        print(f'slide {n}: sent and downloaded ({size} bytes)')


if __name__ == '__main__':
    main()
