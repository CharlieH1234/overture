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
  tone, a soft call to action ("Set your first alarm tonight." or similar), then
  3 to 5 relevant hashtags. Under 2,200 characters.
- Keep `cover` and `title` exactly as saved when `locked.cover` / `locked.title`
  is true.
- For "Reimagine caption", take a different angle from the current caption.

## Reimagine slides

Not set up for Overture yet: there is no slide builder or photo source for this
account. Set `reimagine.slides` to `error` with
"Slide building isn't set up for Overture yet" and tell the operator.

## Approve 2

No Overture TikTok channel is configured (`CHANNELS` is empty in the page), so
the button is disabled. If a request arrives anyway, set `schedule.status` to
`error` with "No Overture channel is set up yet".

## Check views

Read the post's public TikTok page and record `stats`
(`views, likes, comments, saves, shares, checkedAt, url`). Write `error` if the
page can't be read, and say why.
