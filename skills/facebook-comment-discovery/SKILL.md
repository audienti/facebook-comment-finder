---
name: facebook-comment-discovery
description: Use when the user asks to find Facebook signal, page-audience signal, public reply opportunities, or recurring brand-building threads for an offer, product, or ICP.
---

# Facebook Signal Discovery

Convert an offer into ranked Facebook comment threads that reveal real
audience intent, pain, and engagement opportunities.

The objective is `goodput`: credible, target-adjacent engagement opportunities
per run. Do not optimize for raw reach, broad chatter, or creator visibility
alone.

## Use This Skill To Produce

- A compact summary of the offer, ICP, and likely audience language
- A seed strategy across public pages, public post URLs, and weak fallback
  search ideas
- Reusable strategy-specific seed-pack memory for each offer plus ICP
- One or more bounded Apify runs
- Ranked comments with signal strength, fit, audience context, and a reply
  angle
- A track split across base direct-demand retrieval and additive
  visibility-leverage retrieval
- An outcome split across `direct_buyer`, `visibility_leverage`, or `discard`
- A surface split across `buyer_authored`, `competitor_audience`,
  `creator_audience`, `community_audience`, or `partner_audience`

## Inputs

- Prefer an offer URL. If absent, use a short offer description.
- Optional: ICP, seed pages, known post URLs, excluded page types, time
  window, spend cap, or whether to include nested replies.

## Rules

- Inspect skill-local memory under `memory/domains/`, `memory/urls/`,
  `memory/icps/`, `memory/seed_packs/`, `memory/run_ledgers/`, and
  `memory/comments/`.
- Review `memory/lessons.md` first for global cross-run rules.
- Treat this as industry search and engagement. `direct_buyer` is one lane,
  not the whole system.
- Never let competitor, influencer, partner, or adjacent-offer surface
  tracking replace direct pain, topic, symptom, or recommendation retrieval.
- A full run should usually keep one base direct-demand track such as
  `direct_buyer + buyer_authored`, then add one or more visibility-leverage
  tracks such as `visibility_leverage + creator_audience` or
  `visibility_leverage + competitor_audience`.
- Separate `strategy` from `surface_family`.
- Strategy answers `why this is worth engaging commercially`.
- Surface family answers `whose authored surface or audience produced the
  signal`.
- Use `buyer_authored` for direct operator or buyer surfaces and the other
  surface families for competitor, creator, community, or partner audiences.
- The top-level question is not `is this a relevant page`. The top-level
  question is `is this comment predictive that this person or audience would
  care about what we sell`.
- On Facebook, page choice matters more than keyword cleverness.
- Default to page-led post discovery for `visibility_leverage`, then deepen
  into comments only when buyer-intent evidence matters.
- Use open search only as a weak fallback for finding likely public pages or
  public posts.
- When the strategy is `visibility_leverage`, prefer
  seeded named competitors, creators, consultants, communities, or partners
  before refreshing through open search.
- Search for first-person pain, recommendation asks, tool questions, workflow
  confusion, and aspiration gaps, not just category keywords.
- Separate `page fit` from `commenter fit`. The page can be low direct buyer
  fit while the commenters are useful.
- First-person self-report and direct questions are usually the strongest
  comment-level signals.
- Drop creator self-comments by default.
- Keep hits by default only when they are direct questions or first-person
  pain signals after low-signal and self-promo filters.
- Public Facebook comment sections are often noisy. Be stricter than you would
  be on LinkedIn or Reddit.
- Suppress threads with fewer than three external substantive comments or zero
  actionable comments after filtering.
- Public replies can look thirsty in big creator threads. Use them only when
  the comment clearly invites a useful answer.
- The returned queue is `raw surfaces -> engage_now -> discard`.
- There is no watch bucket or maybe-later bucket in the published contract.
  If it is not worth engaging now, discard it.
- Replies should sound like a practitioner: casual, concrete, and useful.
- Avoid em dashes, semicolons, and colon-heavy phrasing in drafted replies.
- Verify the live Actor schema before running the scraper.
- Prefer the Apify tool surface when it is available. Otherwise use the local
  authenticated `apify` CLI.
- Use the result template in `assets/finding-template.md`.

## Workflow

1. Inspect memory.
   - Read `memory/lessons.md` first.
   - Resolve the base direct-demand track first.
   - Then resolve additive surface tracks one by one so buyer-authored pain
     priors and audience-surface priors stay separate.
   - Run
     `python3 scripts/resolve_memory.py --url "<offer_url>" --icp "<icp>" --strategy "<strategy>" --surface-family "<surface_family>" --scaffold`
     when a URL is available.
   - Reuse curated seed packs and review the matching run ledger before
     burning new spend.

2. Read the offer.
   - Open the URL or inspect the provided summary.
   - Extract: ICP, promised outcome, broken alternatives, costly symptoms,
     urgency triggers, named tools, and adjacent creator or educator
     ecosystems.

3. Translate the offer into comment-level signal primitives.
   - Build 3-6 concrete situations that would make a commenter ask for help,
     expose pain, or request recommendations.
   - Build the phrases people would write when they are stuck, shopping, or
     comparing.
   - If an ICP is given, extract observable proxies such as title words,
     industry clues, business clues, self-description clues, and urgency
     triggers.
   - Use `references/comment-signal-framework.md`.

4. Build the seed strategy.
   - Start from `memory/seed_packs/` when a matching offer plus ICP pack
     exists.
   - Build the retrieval stack in this order:
   - base direct-demand track: comment-level pain, topic, recommendation, and
     workflow-friction retrieval from likely buyer-authored or buyer-adjacent
     surfaces
   - additive visibility-leverage tracks: competitors, influencers, consultants,
     communities, partners, or adjacent offers speaking to the same audience
   - Do not drop the base direct-demand track just because a surface track
     exists.
   - Build a surface map before refreshing seeds:
   - `buyer_authored`: buyers or operators showing their own situation
   - `competitor_audience`: competitor pages with overlapping buyer audiences
   - `creator_audience`: educators, creators, consultants, or advisors
   - `community_audience`: groups, media pages, or adjacent communities
   - `partner_audience`: implementation, tooling, or service partners
   - If the motion is `visibility_leverage`, start from
     named surface seeds first and only then widen into search refresh.
   - Prefer seeded public pages first:
   - operators teaching the workflow
   - niche vendors with audiences that ask tool questions
   - adjacent communities or educators
   - category pages where practical questions show up in comments
   - Use post-led seeds when the user already has specific public Facebook
     post URLs.
   - Use open search only to refresh the seed map when strong page seeds are
     missing.

5. Choose the collection shape.
   - Page-led default:
   - actor: `apify/facebook-posts-scraper`
   - `startUrls=[{"url":"https://www.facebook.com/examplepage/"}]`
   - `resultsLimit=3` to `10`
   - optional `onlyPostsNewerThan="30 days"` when freshness matters
   - Post-led comments:
   - actor: `apify/facebook-comments-scraper`
   - `startUrls=[{"url":"https://www.facebook.com/.../posts/..."}]`
   - `resultsLimit=20` to `100`
   - `includeNestedComments=false` by default
   - `viewOption="RANKED_UNFILTERED"` or `"RECENT_ACTIVITY"`
   - Search-led fallback:
   - use web search only to discover likely pages or post URLs

6. Run the Actors.
   - Verify schemas against `references/apify-facebook-actors.md`.
   - If page-led:
   - run `apify/facebook-posts-scraper`
   - inspect returned posts
   - normalize with
     `python3 scripts/normalize_apify_search_results.py --input <dataset.json>`
   - rerun `apify/facebook-comments-scraper` on the best post URLs only when
     a second-stage comment pass is justified
   - If post-led:
   - go directly to `apify/facebook-comments-scraper`
   - Save actor input JSON locally.
   - Save dataset items locally.
   - Normalize with
     `python3 scripts/normalize_apify_comment_results.py --input <dataset.json> --min-external-substantive-comments 3`
   - If live Facebook scraping is blocked, say so plainly and stop instead of
     pretending the run happened.

7. Rank and filter.
   - Start with hard exclusions:
   - creator self-comments
   - praise with no problem signal
   - emoji-only or one-word reactions
   - social-only chatter
   - self-promotional comments
   - threads with fewer than three external substantive comments
   - Then classify each surviving comment on:
   - `comment type`
   - `speaker perspective`
   - `commercial class`
   - `repeat status`
   - Then score each surviving comment on:
   - offer relevance
   - comment-level ICP fit
   - buyer likelihood
   - first-person specificity
   - recommendation or evaluation intent
   - workflow pain
   - urgency
   - page-audience relevance
   - engagement opportunity

8. Present the findings.
   - Use the structure in `assets/finding-template.md`.
   - State whether the run was page-led, post-led, or search-refreshed.
   - Show the seed pages or seed posts used.
   - Show whether those seeds came from a curated seed pack or from a fresh
     search-refresh pass.
   - Report the outcome split clearly so direct-buyer and visibility-leverage do
     not get blended together.
   - Report the track split clearly so direct pain/topic opportunities stay
     separate from competitor, influencer, and audience-surface opportunities.
   - Report the surface split clearly so buyer-authored, competitor, creator,
     community, and partner motions do not get blended together.
   - Call out how many threads were suppressed for being thin, noisy, or
     self-comment heavy.
   - Include the page context, commenter context, comment text, why it is
     predictive, the surface family, the repeat status, the action type,
     and a suggested reply or follow-up angle.

9. Write back the tuning.
   - Record winning and losing seeds in the strategy- and surface-specific
     seed pack.
   - Record the shared goodput funnel in the run ledger.
   - Record drafted or posted replies in the comment log.
   - If the channel keeps failing for the same strategy, say so and demote it
     honestly instead of inflating success.
