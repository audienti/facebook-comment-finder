# Skill Memory

This folder stores reusable tuning learned from live runs.

Use it so the skill does not rediscover the same drift patterns, seed surfaces,
and goodput failures every time.

## Memory Types

- `lessons.md`
  Use for cross-run rules that should shape all future executions of the skill.
  This is the closest match to Recursive Drift's self-improvement loop.

- `domains/`
  Use when the tuning is reusable across the whole company or domain.

- `urls/`
  Use when the tuning is specific to one page, wedge, or path.

- `icps/`
  Use when the tuning depends on a specific buyer lens for a specific offer.

- `seed_packs/`
  Use to promote the queries, pages, profiles, authors, creator clusters,
  communities, or thread shapes that repeatedly produce goodput.
  Query-led search is seed discovery until a query or surface proves it can
  keep producing useful opportunities.

- `run_ledgers/`
  Use to record the shared funnel for every run:
  `query -> seeds -> scraped threads -> external substantive discussion -> goodput opportunities -> posted engagement`
  This is the measurement layer. Visibility-only hits do not count as success.

- `comments/`
  Use to track public replies or comments already posted, the angle used, the
  thread or author, and the follow-up state for conversations we have already
  entered.
  This is the stateful memory layer that prevents repeating the same angle and
  creates the only revisit queue that matters: conversations where we already
  posted.

- `strategy`
  Strategy is not a separate folder. It is a suffix on the operational memory
  key for `seed_packs/`, `run_ledgers/`, and `comments/`.
  Example strategies:
  `direct_buyer`, `visibility_leverage`.
  Strategy answers `why is this commercially worth engaging`.

- `surface_family`
  Surface family is also not a separate folder. It is another suffix on the
  same operational key after the strategy suffix.
  Example surface families:
  `buyer_authored`, `competitor_audience`, `creator_audience`,
  `community_audience`, `partner_audience`.
  Surface family answers `whose authored surface or audience produced this
  signal`.

Use `strategy` and `surface_family` together so one offer plus ICP can keep
distinct tuned motions like:

- direct buyer discovery on buyer-authored surfaces
- visibility leverage on competitor audiences
- visibility leverage on creator audiences
- visibility leverage on partner or influencer surfaces

A full run can and often should combine multiple operational notes in parallel,
not choose only one.

Default bundle:

- base direct-demand track: `direct_buyer + buyer_authored`
- additive surface tracks: `visibility_leverage` plus
  `creator_audience`, `competitor_audience`,
  `community_audience`, or `partner_audience`

Run `resolve_memory.py` once per track and keep the notes side by side in the
same report. Surface tracking should extend the direct pain or topic pass, not
replace it.

## Naming

- Domain note:
  Lowercase host with dots replaced by dashes.
  Example: `actico.com` -> `domains/actico-com.md`

- URL note:
  Start with the normalized host, then `__`, then the path with leading and
  trailing slashes removed and remaining slashes replaced by `--`.
  Example: `https://audienti.com/exo` -> `urls/audienti-com__exo.md`

- ICP note:
  Start with the normalized host, include the path when present, then append
  `__<icp-slug>`.
  Example:
  `https://audienti.com/exo` + `AI startup founders` ->
  `icps/audienti-com__exo__ai-startup-founders.md`

If a URL has no path or only `/`, use only the domain note.

- Seed-pack, run-ledger, and comment notes:
  Use the same base as the URL or domain note.
  If an ICP is present, append `__<icp-slug>`.
  If a strategy is present, append `__<strategy-slug>`.
  If a surface family is present, append `__<surface-family-slug>` after the
  strategy slug.

Examples:

- `audienti-com__exo__ai-startup-founders__direct-buyer__buyer-authored.md`
- `audienti-com__exo__ai-startup-founders__visibility-leverage__competitor-audience.md`
- `audienti-com__exo__ai-startup-founders__visibility-leverage__creator-audience.md`

## Helper Scripts

Use:

```bash
python3 scripts/resolve_memory.py \
  --url "https://example.com/path" \
  --icp "AI startup founders" \
  --strategy "visibility_leverage" \
  --surface-family "competitor_audience" \
  --scaffold
```

The resolver:

- normalizes the host and path
- computes the domain, URL, and optional ICP note paths
- computes the strategy- and surface-specific seed-pack, run-ledger, and
  comment note paths
- creates missing notes from templates when `--scaffold` is passed
- prints a JSON payload the agent can use directly

## What To Record

Each note should capture:

- offer or domain summary
- ICP framing that actually helped
- winning query or seed patterns
- losing query or seed patterns
- productive surfaces, communities, or creator clusters
- noisy surfaces or content types
- exclusion cues and slop cues
- open questions or next tests

`icps/` notes should capture:

- the exact buyer lens used
- which queries or surface types worked for that lens
- which role or persona patterns were false positives
- what should be up-ranked or down-ranked for future scoring

`seed_packs/` notes should capture:

- which query families graduated into reusable seeds
- which accounts, pages, creators, communities, or author clusters keep
  surfacing good threads
- which surface families were productive for this strategy
- what must be true before a seed is promoted again

`run_ledgers/` notes should capture:

- query count
- seed count
- scraped thread count
- external substantive discussion count
- goodput opportunity count
- posted engagement count
- primary failure mode
- strategy used
- surface family used
- next tuning move

`comments/` notes should capture:

- thread or post URL
- author or handle
- whether we engaged at the surface or comment level
- strategy
- surface family
- comment angle used
- status such as `drafted`, `posted`, `awaiting_reply`, `needs_response`, or `closed`
- outcome signals such as replies, likes, or follow-up interest
- what not to repeat next time

`lessons.md` should capture:

- what happened
- the rule that should persist
- a short active-rules list distilled from past entries

## Operating Rule

These notes are priors, not truth.

If fresh live results contradict a note, update the note.
