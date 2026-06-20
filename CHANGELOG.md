# Changelog

## 0.1.3 - 2026-06-20

- Hardened the post-level visibility gate to discard engagement-bait and hard
  self-promotional Facebook posts before they count as goodput.
- Added a self-check that proves a real visibility surface stays in while bait
  gets dropped.

## 0.1.2 - 2026-06-20

- Added a post-level Facebook page normalizer so `visibility_leverage` runs
  can keep strong page posts without forcing a comments pass first.
- Updated the skill, README, and actor notes to treat page-led posts as valid
  final surfaces for audience-leverage work.

## 0.1.1 - 2026-06-20

- Renamed the user-facing plugin surface to Facebook Signal Finder.
- Tightened the published contract to `raw surfaces -> engage_now -> discard`.
- Kept Facebook specific retrieval honest: page-led and post-led first, open
  search only for seed discovery.

## 0.1.0 - 2026-06-16

Initial release.

- Added a standalone `facebook-comment-discovery` skill under
  `skills/facebook-comment-discovery/`.
- Set the v1 retrieval path to Apify-backed Facebook comment discovery using
  page-led and post-led collection.
- Added a normalizer script so Facebook comment datasets can be grouped into
  posts plus comments before scoring.
- Added Facebook-specific filtering rules for creator self-comments,
  low-signal reactions, public-page noise, and self-promo.
- Added skill-local memory scaffolding for global lessons plus domain-, URL-,
  and ICP-specific tuning.
