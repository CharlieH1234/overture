#!/usr/bin/env python3
"""Send a scheduled post's slide text to Telegram, one message per slide.

Usage:
  python3 -I telegram_slide_text.py <post.json>

post.json: {"ref": "P-033", "title": "...", "scheduleAt": "2026-11-27T12:00:00Z",
            "overlays": [{"text": "slide 1 text"}, {"text": "slide 2 text"}, ...]}

TikTok's posting API (and so Postiz) has no field for per-slide text, so the
text still has to be added in the TikTok app. To save copying it out of the
draft's description, this sends a short header, then each slide's text as its
own message containing nothing else: long-press, Copy, paste onto the slide.
The caption isn't sent for photo posts: Approve 2 puts it in the draft's
description. For a video post ("video": true in post.json, with "caption"),
the text is already in the video and TikTok drops the description of video
drafts, so it sends the header and then the caption instead.

Uses the same bot and chat as telegram_compress.py: the token from the
environment variable Memorypalace_slides_bot (or TELEGRAM_BOT_TOKEN) and the
chat from TELEGRAM_CHAT_ID. The token is never printed.
"""
import datetime
import json
import os
import ssl
import sys
import urllib.parse
import urllib.request

CA = '/root/.ccr/ca-bundle.crt'


def ctx():
    return ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()


def die(msg):
    print('ERROR: ' + msg, file=sys.stderr)
    sys.exit(1)


def send(token, chat_id, text):
    body = urllib.parse.urlencode({'chat_id': chat_id, 'text': text, 'disable_notification': 'true'}).encode()
    req = urllib.request.Request(f'https://api.telegram.org/bot{token}/sendMessage', data=body)
    try:
        with urllib.request.urlopen(req, timeout=60, context=ctx()) as r:
            res = json.load(r)
    except Exception as e:  # never echo the URL, it holds the token
        die(f'sendMessage failed: {type(e).__name__}')
    if not res.get('ok'):
        die(f'sendMessage failed: {res.get("description")}')


def main():
    if len(sys.argv) != 2:
        die('usage: telegram_slide_text.py <post.json>')
    token = os.environ.get('Memorypalace_slides_bot') or os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        die('Memorypalace_slides_bot (or TELEGRAM_BOT_TOKEN) and TELEGRAM_CHAT_ID must be set')
    post = json.load(open(sys.argv[1]))
    video = bool(post.get('video'))
    slides = [o.get('text', '').strip() for o in post.get('overlays') or []]
    if video and not (post.get('caption') or '').strip():
        die('a video post needs its caption in post.json')
    if not video and not any(slides):
        die('the post has no slide text')
    when = ''
    if post.get('scheduleAt'):
        at = datetime.datetime.fromisoformat(post['scheduleAt'].replace('Z', '+00:00'))
        when = f' · lands {at.strftime("%a %d %b %H:%M")} UTC'
    header = f'{post.get("ref", "")}{when} · ' + ('video' if video else f'{len(slides)} slides')
    if post.get('title'):
        header += f'\n{post["title"]}'
    header += '\nCaption follows: paste it into the TikTok draft.' if video else '\nSlide text follows, one message per slide.'
    send(token, chat_id, header)
    if video:
        send(token, chat_id, post['caption'].strip())
        print('sent 2 messages')
        return
    n = 1
    for i, text in enumerate(slides, 1):
        if not text:
            continue
        send(token, chat_id, text)
        n += 1
    print(f'sent {n} messages')


if __name__ == '__main__':
    main()
