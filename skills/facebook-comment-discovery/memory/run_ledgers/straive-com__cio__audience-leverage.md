# straive-com__cio__audience-leverage__run-ledger

- Last updated: 2026-06-18
- Offer: https://www.straive.com/
- ICP: CIO
- Strategy: audience_leverage
- Platform: Facebook

## Measurement contract

- Optimize goodput, not visibility.
- `external substantive discussion` means the thread has real audience detail,
  direct questions, or first-person problem language.
- `goodput opportunity` means the thread is worth engaging after spam,
  low-signal chatter, and self-promo suppression.

## Runs

| Date | Query count | Seed count | Scraped threads | External substantive discussion | Goodput opportunities | Posted engagement | Primary failure mode | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-06-18 | 0 | 5 | 0 | 0 | 0 | 0 | no_accessible_comments | page-led posts pass found 5 Straive posts, but every follow-on comments pull returned `no_items`; stop spending on this page cluster until the seed source changes |

## Current goodput rules

- Treat `no_items` rows as a real seed failure, not as thin discussion.
- Do not pay for comment pulls on company-page blog promo unless the post already shows visible public discussion.
- Facebook only stays viable here if seeded from community or operator pages with accessible comments.

## Next tuning move

- shift from the Straive page to community pages, conference pages, or operator-led public threads
- keep Facebook in a low-priority lane until it proves accessible comment surfaces
