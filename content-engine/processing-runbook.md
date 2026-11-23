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

Sources: the `overture-content-engine` skill (brief, personas, catalogue,
guardrails; synced 18 Nov 2026) and the "Overture — Homepage Copy" doc
(https://claude.ai/artifact/LoDqu9MLPJmU7RrgeK6FTL). Where this runbook and the
skill differ, this runbook wins: Charlie chose (18 Nov) to keep slide text out of
the images and to keep his caption rules.

- **One line:** an iPhone alarm that wakes you to a classical piece, then plays
  live classical radio with one tap. "Mornings deserve better than a beeping alarm."
  "Wake in two movements."
- **Who it's for:** UK professional, 25 to 40, who wakes or commutes to classical
  radio & wants it without the box by the bed.
- **Voice:** premium, warm, brief, a little witty. British spelling. No
  exclamation marks. Never "game-changer". At most one musical pun per hook.
- **Always write "&" instead of "and"** in everything posted: hooks (`cover`),
  slide text (`overlays`), TikTok titles and captions, with no exceptions.
  Internal fields (`notes`, `style`, `subject`, image prompts) don't need it.
- **Proof points that can be claimed:** rings on the Lock Screen even in Silent or
  Focus; gentle fade-in; the piece keeps playing if a station can't be reached;
  timers that end in music; no account or login; 3-day free trial.

**Personas** (label every post with one in `persona`):

| Persona | Job, in their words |
| --- | --- |
| Radio-loyal professional (primary) | "Keep my classical radio, lose the box by the bed." |
| Romantic aesthete | "Romanticise my morning." |
| Dark-winter-mornings riser (Oct–Feb) | "Make 6:30 in the dark less grim." |
| Parents | "Give me a calm minute before the chaos." |
| Sensitive wakers | "Wake me without the jolt." |
| Student (university, 18+ only) | "Get me into study mode." |
| Traveller | "My usual wake-up, wherever I sleep." |
| Lapsed listener | "Bring classical back into my day." |
| Bedtime listener | Tease as "coming soon" only, once Charlie confirms wording |

Not targeted: heavy sleepers who need a loud alarm; digital-detox seekers.

**Pieces in the app** (the only pieces a post may feature; use these names
exactly): Prelude in C Major (Bach) · Symphony No. 5 in C Minor (Beethoven) ·
Minuet for String Quartet (Boccherini) · Pomp and Circumstance March No. 1 in D
(Elgar) · Gymnopédie No. 1 (Satie) · The Marriage of Figaro (Mozart) · Flight of
the Bumblebee (Rimsky-Korsakov) · Rosamunde Quartet (Schubert) · Arabesque No. 1
(Debussy) · Clair de Lune (Debussy) · Morning Mood (Grieg) · Pavane for a Dead
Princess (Ravel) · The Swan (Saint-Saëns) · Waltz of the Flowers, Nutcracker
(Tchaikovsky) · Moonlight Sonata (Beethoven) · Miserere (Allegri) · Chinese
Dance, March & Overture Part 1, Nutcracker (Tchaikovsky) · Ride of the Valkyries
(Wagner). Festive season only: O Christmas Tree · O Come, All Ye Faithful ·
Silent Night · Carol of the Bells. A reference post built on another piece can
lend its format, but the post uses a piece from this list.

**Live radio, UK:** only Classic FM, BBC Radio 3 & Magic Classical. Posts may name
these three; never mention or show any other station; no station logos as
graphics.

## Guardrails (check every hook, slide & caption)

- **The radio needs a tap.** Never show or say that live radio plays as the alarm
  or starts by itself. The alarm plays a piece; the radio is one tap away.
- **Claims:** music *can help* ("can help lower stress", "wake without the jolt",
  "helps you focus"). Never a percentage, "proven", "clinically", "guaranteed",
  the Mozart effect, or treating ADHD, insomnia, anxiety disorders or SAD.
- **Story hooks are allowed:** made-up "someone told me / my friend said / my
  dad…" anecdotes are fine as storytelling (Charlie's decision, 18 Nov). Keep
  the person unnamed or generic (never a real, named person), & the music
  claims inside the story still follow the Claims rule above.
- **No fabricated social proof:** no made-up reviews, ratings, user counts or
  stats. Numbers become `[NUMBER]` for Charlie.
- **No performer, orchestra or recording names** unless Charlie confirms the licence.
- **Imagery:** original or AI-generated only; nothing from films or TV; no real
  named venues. Never generate the app's interface with an image model.
- **Copy formats, never claims:** a reference's health claims & hashtags don't carry over.
- **Label AI images:** Postiz's TikTok draft mode can't set the AI-generated
  label, so tell Charlie to switch it on in TikTok before publishing.
- **One slideshow per account per day,** never two of the same format on one day.
- If a format only works by breaking a guardrail, drop the format.

## App screens

Real screenshots come from the Overture Screenshots Figma file
(https://www.figma.com/design/syHqZFA4ClUDvQee3Mff4Z/Overture-Screenshots, page
`0:1`). Export them fresh each session they're needed (Figma `get_screenshot`,
maxDimension 2400), index what each shows, and never reuse old exports without
checking. Never paint over text in a screenshot.

- **Where:** at most one app slide per post, on slide 3 or later (never slide 1).
  It's the one place the slide text can name Overture, naturally, e.g. "found an
  alarm that plays Grieg instead of a beep" over the alarm list. The caption still
  never names Overture.
- **Which:** an "Homescreen alarm set NN" frame showing the post's own piece
  (frames exist for Arabesque No. 1, The Marriage of Figaro, Pomp & Circumstance,
  Minuet for String Quartet, Prelude in C Major, Flight of the Bumblebee), the
  ringing lock screen, or the live radio screens. Not the "Appstore screenshots"
  frames: they read as ads.
- **Ask Charlie first** before using a screen that shows a station logo or a
  performer's name.
- Figma's MCP calls are limited on Charlie's Starter plan. If a call is refused,
  stop and tell Charlie; don't fall back to old exports.

## Proven formats (Figma library, H-160 to H-176)

Charlie's 17 reference slideshows are hooks H-160 to H-176 (collection "Figma
slideshows"); each has its slide text, stats & an Overture angle in `note`.
Different accounts & no view counts, so treat these as patterns, not proof.
When an idea doesn't come from a specific hook, start from one of these:

1. **"Just listen" reveal** (H-172, H-173, H-176; also H-170, H-171, H-174).
   Biggest reach (H-172: 533K likes). Plain colour cards: "\"it's just an
   alarm\"" → "Shut Up" → "JUST LISTEN", then an AI painting with a title card
   for one piece (composer in script, piece in serif); optional app slide after.
   The piece must be the post's sound: tell Charlie which piece to pick in
   TikTok, because Postiz drafts go up without music.
2. **Gentle protocol list** (H-168, H-164, H-160). Most saves (H-168: 0.72
   saves per like). First-person or "formula" hook about waking up, numbered
   named rules with real detail per slide over dimmed moody photos or dark
   cards, the app as a "bonus tip" near the end.
3. **Aesthetic one-line list** (H-166, H-169). One lowercase line per slide over
   letterboxed lifestyle photos; the app is one item mid-list ("my fave alarm").

Skip as main formats: numbered series cards without a hook (H-175), the
competitor listicle (H-165, too little data).

## Test week 24–29 Nov (3 posts a day)

Charlie's call (23 Nov): 18 test posts, P-028 to P-045, 3 a day at 07:30, 16:30
& 21:00, each tagged `experiment` (`id`, `name`, `question`, `format`,
`hookType`). For this week the "one slideshow per account per day" rule is
relaxed; still never put two posts of the same format back to back. Every
post uses a different piece from the app's catalogue (the two series posts
list four each).

- A (hook test, Landscape), B (format test, hook "the perfect classical
  alarm?"), C (piece test, Quad), D (rebuttal repeat, Block colour), E
  (series test).
- New formats: **Sunrise photo** (no person) & **App screenshot** (B6: a real
  "Homescreen alarm set" frame on slide 1, a one-off exception to the app-slide
  rule; hook & caption still don't name Overture; never AI-generate the app).
- Build slides in the post's `experiment.format`, not a new one. Read stats at
  48 hours & compare within each experiment; because the pieces differ, look
  for patterns across several posts rather than single winners.

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
   - Never mention Overture (or "this app") in the hook.
   - Follow the Guardrails above. In particular: borrow the format, never the
     original's claim; no made-up stats, studies, reviews or ratings.
     "Someone told me" / "my dad…" story hooks are fine (unnamed, made-up
     people only).
   - Feature one piece from "Pieces in the app", named exactly as listed.
   - Pick the persona it speaks to and save it as `persona`.
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

- `title`: TikTok title, at most 90 characters. **A short, engaging mini-hook
  that is different from the slide-1 hook (`cover`)**, never a copy of it.
  Usually 3 to 8 words, may end with one fitting emoji. Example: hook "your 7am
  alarm doesn't have to be a shock. it can be grieg." → title "calmest way to
  start the day 🌅".
- `caption`: **doesn't repeat the title or the hook.** It starts straight into
  the body (e.g. "Grieg's Morning Mood opens with one quiet flute…"), 2 to 4
  short lines in Overture's tone, then the tagline, then the hashtags. Under
  2,200 characters.
  - **Never mention Overture** (or "the app", "this alarm app", features, the
    trial or how it works). The caption is about the feeling, the mood of the
    piece, and the result: how the morning feels when you wake to it.
  - **End with the tagline on its own line:** "Mornings deserve better than a
    beeping alarm." (changed from "…than a beep." on 18 Nov; on a closing
    slide it's "mornings deserve better\nthan a beeping alarm")
  - **Hashtags, in this order:** `#classicalmusic #alarm #wakeup #<composer>`,
    where the last is the featured composer's surname in lowercase
    (`#grieg`, `#mozart`, `#debussy`, `#bach`, `#satie`), then **one rotating
    fifth tag** that fits the post. Exactly five, never more (Charlie's
    decision, 18 Nov; 2025-26 posts in the hook library mostly use exactly 5):
    - routine & list posts: `#morningroutine`
    - alarm-sound reveals ("just listen", "it's just an alarm"): `#alarmclock`
    - painting or moody posts: `#darkacademia`
    - piano pieces: `#piano`
    - a famous piece: its own tag, e.g. `#clairdelune`, `#morningmood`
      (one word, lowercase, no spaces or punctuation)
    Never `#fyp`, `#foryou`, `#viral`, `#777`, `#lucky` or other filler: in the
    hook library they made no difference to views, & they don't fit the voice.
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
2. Plan 3 slides, or 4 with an app slide (unless the operator asks otherwise):
   - Slide 1: the hook (`cover`). Never an app screen or the Overture name.
   - Slide 2: the turn or payoff that continues the joke or story.
   - Optional app slide (slide 3, before the close): a real screenshot from the
     Overture Screenshots Figma file (see "App screens"), ideally the alarm list
     showing this post's piece. This is the only slide whose text may name
     Overture, and only naturally, e.g. "found an alarm that plays grieg / instead
     of a beep" or "overture: grieg at 6:30, / radio one tap away". No sales line,
     no price, never implying the radio starts by itself.
   - Last slide: the close, ending on the tagline "mornings deserve better /
     than a beeping alarm". No "link in bio" claims we can't back.
   - Every other slide's text is about the feeling, the music & the morning,
     never the app.
   - The app slide's image is the screenshot itself, never generated: place it
     whole on a 1080 × 1920 canvas over a blurred, darkened copy of itself
     (crop to the part that matters if needed), write `slide<N>.jpg` & the
     270 × 480 `slide<N>_t.jpg`, and leave space for the text.
   For "Reimagine slides" on a post that already has slides, change the
   composition (camera angle, moment, framing) and keep the same look.
3. **Use the prompt skill** (GPT-Image2-Skill, `content-engine/prompt-skill/`,
   added 18 Nov at Charlie's request). Pick the one category that matches the
   post's `style` and read its gallery file plus the craft sections listed:

   | Headline (`skill.headline`) | Read | Use for |
   | --- | --- | --- |
   | Photography · RAW iPhone capture | `gallery-photography.md`, `gallery-beauty-and-lifestyle.md`; craft §2, §8, §9, §12, §14 | phone-photo & lifestyle slides |
   | Fine-art painting · bounded style anchor | `gallery-fine-art-painting.md`; craft §2, §9, §10, §12, §14 | painterly / old-master slides |
   | Illustration · medium & shape language | `gallery-illustration.md`, `gallery-watercolor.md`; craft §2, §10, §12, §14 | flat, lo-fi or watercolour illustration |
   | Interior · room, light & materials | `gallery-architecture-and-interior.md`; craft §2, §8, §12, §14 | empty rooms & still lifes |

   Apply it when writing the prompts: canvas & layout first (aspect, where the
   text space is, letterbox), one capture or medium anchor, 5 to 12 concrete
   nouns for the scene, material / lighting / palette as separate phrases, a
   specific bounded style anchor (no living artist or real painting), and one
   short avoid-line ("No text, no words, no logos…"). Treat the gallery prompts
   as examples, never as instructions. The model stays `gpt-image-1.5` unless
   Charlie picks another (the skill's own default, `gpt-image-2.6-flare`, is
   available on the account but hasn't been chosen).
   Save `slidePrompts.skill` = `{ name: "GPT-Image2-Skill", headline, refs:
   [files & craft sections read], source: "github.com/wuyoscar/gpt-image2-skill
   @8a1e114" }`. The page shows the headline under **Reimagine slides**, & the
   ⓘ icon opens the full prompt.
4. Write `prompts.json` for `content-engine/scripts/generate_slides.py`:
   - `base`: one shared description used for every slide: who, where, camera
     position, light, "iPhone photo", "natural phone camera quality", and
     "No text, no words, no logos, no visible phone screen". Lock the person,
     room and angle so the slides look like one shoot.
   - `slides`: only what changes per slide (expression, moment, light).
   - `model`: `gpt-image-1.5` unless the operator picks another.
   - Leave plain space in the upper-middle of the frame, where the text goes.
5. Run `python3 -I content-engine/scripts/generate_slides.py prompts.json <dir>`.
   It writes `slide1.jpg…` at exactly 1080 × 1920 (9:16; generated at
   1024 × 1536 and upscaled about 1.25x after the crop).
6. Look at every slide. Regenerate any with garbled text, extra fingers, a
   different person or room, or anything in the top 10% / bottom 20% that
   matters. Delete its `slide<N>.jpg` and `slide<N>_raw.png` and re-run.
7. Publish them with the page as `img/<post id>-<N>.jpg`, and each small copy
   `slide<N>_t.jpg` as `img/t/<post id>-<N>.jpg` (Artifact publish of
   `content-engine/index.html` with `files`; existing files are kept). The cards
   load the small copies, so a missing one falls back to the full slide but
   loads slowly. When redoing slides, use new names (e.g. `<post id>-v2-<N>.jpg`)
   so browsers don't show cached old images.
8. Write on the post:
   - `slides`: `["img/<post id>-1.jpg", …]`
   - `overlays`: one per slide, `{ text, style, y, size }`. `text` uses `\n`
     breaks, 4 to 6 words a line, no emoji. `style` is `outline` (TikTok-style
     white text with black outline, the default), `tiktok`, `serif` or
     `serif-bold`, matching the original. `y` is the text's centre as a share of
     the height, between 0.15 and 0.7 (keep out of the top 10% and bottom 20%).
     `size` is a share of the width, about 0.06.
   - `slidePrompts`: the prompts.json used, with its `skill` block, so the
     slides can be remade & the page can show the prompt.
   - `blocker`: "" once the slides are built.
   - `reimagine.slides`: `{ status: "done", doneAt, detail: "<one line on the composition>" }`.
9. Reply to the comment with one line on what was built.

The text is never baked into the photos: it's added in the TikTok app from the
"Slide text to add in TikTok" list. Before anything goes to Postiz, the photos
still go through the Telegram metadata step (see Approve 2).

## Reimagine with edits

The **Reimagine with edits** button on an idea card lets Charlie say how to
redo the slides, hook or caption ("no alarm clock on slide 2", "make slide 1
brighter"). The request arrives as "reimagine the <kind> of P-NNN … with these
edits from me: "<direction>"", & the direction is also saved as
`posts/<id>.reimagine.<kind>.direction`.

- Follow the matching section (Reimagine slides / hook / caption), but the
  direction wins over the defaults there: e.g. keep the current composition if
  it only asks to remove one object, or keep the hook if it only asks for a
  different piece. Guardrails still apply; if a direction would break one, do
  the rest & say in the reply what you left out & why.
- For slides, redo only the slides the direction is about & keep the others
  (same names for kept slides, new `-vN-` names for changed ones). Put the
  direction into the prompts as concrete instructions & avoid-lines, not as
  quoted text.
- Keep `direction` on the status when you set it to `done`, so the card shows
  what was asked. Reply with one line on what changed.

## Approve 2

Channel: **Overture.alarm.app** (Postiz TikTok, integration id
`cmwf7nvfk014kms076xqd8f1m`). Approve 2 writes `schedule` on the post with that
`integrationId`, the send time and `step: "queued"`.

Write each step to `schedule.step` (and a short `schedule.detail`) as you go, so
the Scheduled tab shows progress. On any failure set `schedule.status: "error"`
with a plain `schedule.error` and stop.

1. **telegram** (mandatory, no fallback). Put the post's slides in a folder as
   `slide1.jpg…` (from the page's `img/<post id>-<N>.jpg`, read with the
   Artifact tool), then run
   `python3 -I content-engine/scripts/telegram_compress.py <folder>`.
   It sends each photo to the Memory Palace bot chat and downloads Telegram's
   re-encoded copy as `slide<N>_tg.jpg`. It reads the bot token from the
   environment variable `Memorypalace_slides_bot` (the Memory Palace slides
   bot) and the chat from `TELEGRAM_CHAT_ID`, both set in the cloud
   environment's settings, and needs `api.telegram.org` allowed (it is). If either variable is missing, or Telegram can't
   be reached, set `error` to "Telegram step can't run: <reason>" and don't
   upload. Never substitute local compression.
2. **download**: check every `slide<N>_tg.jpg` exists and opens.
3. **upload**: run `python3 -I content-engine/scripts/postiz_upload.py <folder>`.
   It uploads only the `slide<N>_tg.jpg` files, in order, to the Postiz media
   library and prints `[{id, path}, …]` (also saved as `postiz_media.json`). It
   needs `POSTIZ_API_KEY` in the environment (the operator sets it in the cloud
   environment's settings) and `api.postiz.com` allowed (it is). Save the list on
   the post as `postizMedia` (the paths). On HTTP 401/403 set `error` to
   "Postiz rejected the API key"; on 429 "Postiz rate limit, try again in an hour".
4. **schedule**: with the Postiz MCP tool `integrationSchedulePostTool`:
   - `integrationId`: the channel above; `isPremium: false`; `shortLink: false`;
     `type: "schedule"`; `date`: `schedule.at` (UTC).
   - `postsAndComments`: one item, `attachments` = the uploaded paths in slide
     order, `content` = all the text the operator needs, in three labelled
     sections so it can be copied in one go, each line wrapped in `<p>…</p>`
     (blank lines become `<p></p>`):
     ```
     SLIDE TEXT TO ADD:
     Slide 1:
     <slide 1 text, one line per line break>
     Slide 2:
     <slide 2 text>
     Slide 3:
     <slide 3 text>

     TITLE:
     <the post's title>

     CAPTION:
     <the post's caption, ending with the tagline & hashtags>
     ```
     Slide text comes from `overlays[].text` (empty lines inside a slide's text
     are kept). Escape `&` as `&amp;` in the HTML.
     This whole block becomes the TikTok draft's description, so the operator
     copies the slide text out, then replaces the description with the CAPTION
     section before publishing.
   - `settings`: `title` = the post's `title`, `content_posting_method: "UPLOAD"`,
     and the required fields `privacy_level: "SELF_ONLY"`, `duet: false`,
     `stitch: false`, `comment: true`, `autoAddMusic: "no"`,
     `brand_content_toggle: false`, `brand_organic_toggle: false` (TikTok ignores
     these in UPLOAD mode).
   UPLOAD sends the photos to the TikTok app inbox as a draft at that time. The
   operator adds each slide's text and a sound and publishes within 24 hours, or
   TikTok discards it. Never use DIRECT_POST unless the operator asks.
   Then write `schedule.status: "sent"`, `postizId`, `previewUrl` (from the
   tool's result), `sentAt`, and `step: "schedule"`.

## Analysis (TikTok stats & ranking)

Triggered by **Check TikTok stats** on the Analysis tab. Status & results live in
`analysis/tiktok`: `{ status, detail, error, checkedAt, account, channel, posts, note }`.

1. Set `status: "working"` with a short `detail`.
2. Account totals: run `node content-engine/scripts/tiktok_profile_stats.js
   https://www.tiktok.com/@overture.alarm.app <dir>` or read the profile page's
   header; save `account: { followers, following, likes, videos }`. (From this
   cloud browser TikTok returns the profile header but an empty video list, so
   per-video numbers come from Postiz. Don't try to get round TikTok's bot
   checks.)
3. Channel totals: Postiz `integrationAnalyticsTool` on the channel, 30 days →
   `channel: { days: 30, views, likes, comments, shares }`.
4. Per post: for every post with `schedule.postizId`, call Postiz
   `postAnalyticsTool` (30 days). Linked posts give views, likes, comments &
   shares; write them to `posts[]` (`{ ref, postId, postizId, views, likes,
   comments, shares, saves: null, linked: true, previewUrl }`) & also to that
   post's `stats` so its card shows them. Posts Postiz hasn't linked to their
   TikTok video come back with an error: list them with `views: null,
   linked: false` so the tab tells Charlie to link them in Postiz.
5. **Screenshots from Charlie** (the profile grid with view counts): crop each
   tile to `analysis-img/vNN.jpg` (publish with the page) & save every video in
   `videos[]` as `{ n, hook, views, likes, comments, shares, saves, thumb, ref,
   postId, pinned, piece, source }`, matching engine posts by their hook text
   (`ref`/`postId`; null for videos posted outside the engine) & merging the
   Postiz likes/comments/shares where linked. When `videos` exists the tab
   ranks the whole account from it.
6. Tag every video with a `format` (shown as a chip & summarised in the
   "By format" table): **Quad composition** (2–4 panels in one frame),
   **Landscape** (a scenic view, photo or painting), **Bedroom scene** (a bed,
   a sleeper or a morning bedroom), **Block colour** (a plain colour card with
   one line), **Profile pic** (face-to-camera selfie), **App promo** (shows the
   app or a download prompt), **Painted scene** (a classical painting of
   people indoors). Add a new format to `formats` only if none fits.
   Also tag a `hookType`: **Perfect alarm label** ("the perfect classical
   alarm?"), **Rebuttal** (a quoted put-down the music answers), **Transformation
   story** ("I changed my alarm & now…"), **How-to / formula**, **Series pick**
   ("…you need as your alarm, Part N"), **POV moment** ("when my alarm goes
   off…", "the fact I wake up to this"), **Swap (not a beep)** (names the piece
   as the beep's replacement). Definitions live in `hookTypes`.
7. Saves aren't available through Postiz: keep `saves: null` unless Charlie
   gives the numbers (TikTok Studio shows them).
8. Write a one-line `note` on what was & wasn't covered, set `status: "done"`,
   `checkedAt`, & reply to the comment with the top post & how many were ranked.

## Check views

Read the post's public TikTok page and record `stats`
(`views, likes, comments, saves, shares, checkedAt, url`). Write `error` if the
page can't be read, and say why.
