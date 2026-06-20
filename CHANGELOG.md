# Changelog

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
