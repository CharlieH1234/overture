# Overture Content Engine: processing runbook

How Claude handles a request sent from the Overture Content Engine page
(https://claude.ai/artifact/ADkmgmkyuGFWa2sj3JAqiS). Requests arrive as a comment
sent to Claude that starts `Overture engine request:`. If the page could not
notify Claude, the operator types a short version in chat instead, such as
"reimagine P-003".

All data lives in the page's database, read and written with the ArtifactData
tool on the URL above:

- `hooks/<id>`: the hook library. `text` is the hook, `orig` the original post's
  stats, `note` what we know about it, `thumb` its cover image.
- `posts/<id>`: one per planned post. `stage` is `idea`, `review`, `scheduled`
  or `posted`. `hookId` points at the hook it copies.

Always read the document first and pass its `version` as `if_version` when you
write. Write progress to the request's status field so the page shows it:
`queued` (set by the page), then `working` with a short `detail`, then `done`,
or `error` with an `error` the operator can act on.

## What Overture is

Source: the "Overture — Homepage Copy & Claude Design Prompts" doc
(https://claude.ai/artifact/LoDqu9MLPJmU7RrgeK6FTL). Re-read it if it may have changed.

- The classical music alarm for iPhone and iPad.
- The idea is the two-movement morning. Movement I: a short extract of a real
  classical recording fades in. Movement II: live classical radio plays on, one tap away.
- Core promise: "Mornings deserve better than a beep."
- Pieces named in the app copy: Grieg's Morning Mood, Debussy's Clair de Lune,
  Bach's Prelude in C Major, Satie, Mozart, Ravel. Only name a piece as being
  in Overture if it is in that list; anything else, write "check it's in the app".
- Proof points that can be claimed: rings on the Lock Screen even in Silent or
  Focus (AlarmKit); gentle fade-in; the track keeps playing if a station can't be
  reached; timers that end in music; no account or login; 3-day free trial.
- Likely audience (inferred, not tested): people who already like classical
  music or classical radio mornings; people who hate harsh alarms; nappers.
- Tone: warm, unhurried, a little witty. At most one musical pun per hook.
  Not loud or shouty.

The ICP and jobs to be done are not set yet. When they are, add them here and
use them to choose the angle.

## Reimagine hook

Triggered by **Add: Ideas** on a hook (which creates the idea post) or by
**Reimagine hook** on an idea card. Status field: `posts/<id>.reimagine.hook`.

1. Read the post and its hook (`hookId`). Look at the hook's thumbnail
   (`thumb`, a file published with the page; read it with the Artifact tool's
   `read` and `path`) so the style brief matches what the original looks like.
2. Work out the pattern that made the original work: the sentence shape, the
   promise, the emotion, the format (POV, "if you…", list, reaction, deadpan
   caption). Name it in one line.
3. Write the Overture version of the slide-1 hook:
   - Keep the original's pattern and rhythm. Swap in Overture's world: waking
     to a classical piece, mornings without a beep, the radio playing on.
   - One hook, at most about 20 words, in the original's casing style.
   - No health or medical claims (dopamine, cortisol, anxiety cures, healing),
     even if the original made one. Borrow the format, not the claim.
   - No made-up stats, studies, reviews or ratings.
   - Name a real piece and composer only from the list above.
   - If `locked.cover` is true, the operator wrote the headline: keep `cover`
     exactly as it is and only refresh the other fields.
4. Write these fields on the post:
   - `cover`: the new hook.
   - `subject`: the piece and composer the post features, e.g.
     "Morning Mood (Grieg)".
   - `style`: `{ medium, palette, text }` describing the original's look to copy,
     e.g. medium "letterboxed concert footage", palette "black bands, warm stage
     light", text "white sans-serif, two centred lines above the footage".
   - `pinterest`: 5 to 6 search terms for finding a photo like the original's.
   - `notes`: start with `Pattern: …` (step 2) and `Why for Overture: …` (one line).
     Keep the existing evidence after them.
   - `reimagine.hook`: `{ status: "done", doneAt: <ISO time> }`.
5. Reply to the comment that sent the request with one line: the new hook and
   the post reference.

If the hook is flagged, or its only appeal is a claim we can't make, still write
a version that keeps the format, and say in `notes` what was dropped.

## Create caption / Reimagine caption

Status field: `posts/<id>.reimagine.caption`.

- `title`: TikTok title, at most 90 characters.
- `caption`: starts with the title line, then 2 to 4 short lines in Overture's
  tone, then the tagline, then the hashtags. Under 2,200 characters.
  - **Never mention Overture** (or "the app", "this alarm app", features, the
    trial or how it works). The caption is about the feeling, the mood of the
    piece, and the result: how the morning feels when you wake to it.
  - **End with the tagline on its own line:** "Mornings deserve better than a beep."
  - **Hashtags, in this order:** `#classicalmusic #alarm #wakeup #<composer>`,
    where the last is the featured composer's surname in lowercase
    (`#grieg`, `#mozart`, `#debussy`, `#bach`, `#satie`). Only those four.
- Keep `cover` and `title` exactly as saved when `locked.cover` / `locked.title`
  is true.
- For "Reimagine caption", take a different angle from the current caption.

## Reimagine slides

Builds the post's text-free photos and the text that goes on them, the same way
as the Palace engine. Status field: `posts/<id>.reimagine.slides`.

Needs the OpenAI key saved on the cloud environment (network secret for
api.openai.com). If a request fails with `insufficient_quota` /
`credit_balance_exhausted`, set `error` to "The OpenAI account has no credits" and
tell the operator; don't retry.

1. Read the post: `cover`, `subject`, `style`, `notes`, and the original
   hook's thumbnail, to match its look.
2. Plan 3 slides (unless the operator asks for another number):
   - Slide 1: the hook (`cover`).
   - Slide 2: the turn or payoff that continues the joke or story.
   - Slide 3: the Overture close, e.g. "mornings deserve better / than a beep",
     then "Overture: the classical / music alarm". No "link in bio" claims we
     can't back.
   For "Reimagine slides" on a post that already has slides, change the
   composition (camera angle, moment, framing) and keep the same look.
3. Write `prompts.json` for `content-engine/scripts/generate_slides.py`:
   - `base`: one shared description used for every slide: who, where, camera
     position, light, "iPhone photo", "natural phone camera quality", and
     "No text, no words, no logos, no visible phone screen". Lock the person,
     room and angle so the slides look like one shoot.
   - `slides`: only what changes per slide (expression, moment, light).
   - `model`: `gpt-image-1.5` unless the operator picks another.
   - Leave plain space in the upper-middle of the frame, where the text goes.
4. Run `python3 -I content-engine/scripts/generate_slides.py prompts.json <dir>`.
   It writes `slide1.jpg…` at exactly 1080 × 1920 (9:16; generated at
   1024 × 1536 and upscaled about 1.25x after the crop).
5. Look at every slide. Regenerate any with garbled text, extra fingers, a
   different person or room, or anything in the top 10% / bottom 20% that
   matters. Delete its `slide<N>.jpg` and `slide<N>_raw.png` and re-run.
6. Publish them with the page as `img/<post id>-<N>.jpg` (Artifact publish of
   `content-engine/index.html` with `files`; existing files are kept).
7. Write on the post:
   - `slides`: `["img/<post id>-1.jpg", …]`
   - `overlays`: one per slide, `{ text, style, y, size }`. `text` uses `\n`
     breaks, 4 to 6 words a line, no emoji. `style` is `outline` (TikTok-style
     white text with black outline, the default), `tiktok`, `serif` or
     `serif-bold`, matching the original. `y` is the text's centre as a share of
     the height, between 0.15 and 0.7 (keep out of the top 10% and bottom 20%).
     `size` is a share of the width, about 0.06.
   - `slidePrompts`: the prompts.json used, so the slides can be remade.
   - `blocker`: "" once the slides are built.
   - `reimagine.slides`: `{ status: "done", doneAt, detail: "<one line on the composition>" }`.
8. Reply to the comment with one line on what was built.

The text is never baked into the photos: it's added in the TikTok app from the
"Slide text to add in TikTok" list. Before anything goes to Postiz, the photos
still go through the Telegram metadata step (see Approve 2).

## Approve 2

No Overture TikTok channel is configured (`CHANNELS` is empty in the page), so
the button is disabled. If a request arrives anyway, set `schedule.status` to
`error` with "No Overture channel is set up yet".

## Check views

Read the post's public TikTok page and record `stats`
(`views, likes, comments, saves, shares, checkedAt, url`). Write `error` if the
page can't be read, and say why.
