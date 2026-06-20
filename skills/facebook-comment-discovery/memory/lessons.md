# Facebook Signal Discovery Lessons

## Active rules

- Treat page choice as the primary lever and comments as the intent layer.
- Prefer page-led or post-led comment collection over open keyword search.
- Use open search only to discover or refresh seeds. Do not treat it as the
  final signal layer.
- Drop creator self-comments by default.
- Up-rank first-person questions, recommendation asks, and workflow confusion.
- Down-rank praise spam, emoji-only comments, and fandom chatter.
- Only surface hits by default when they are a direct question or a
  first-person pain signal.
- Goodput is the optimization target. Visibility-only threads do not count as
  success.
- Suppress threads with fewer than three external substantive comments or zero
  actionable comments after filtering.
- Record winning and losing seeds in `seed_packs/` for each offer and ICP.
- Do not reuse the same reply angle inside the same page cluster too
  quickly.

## Lessons log

- 2026-06-17
  - Facebook open search is useful for seed discovery, but it is too noisy to
    trust as a final signal layer.
  - Semantically relevant pages can still fail on volume. Keep them out of
    the curated pack until they produce repeat external discussion.
- Add dated lessons below as live runs accumulate.
