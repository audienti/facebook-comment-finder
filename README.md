# Facebook Signal Finder

Facebook Signal Finder is a Codex and Claude Code plugin for turning an offer
into real Facebook posts and comment threads worth engaging now for buyer
signal or audience visibility.

It is built for comment-first discovery on public Facebook surfaces. The
strongest motion is usually:

1. start from known-good public pages
2. scrape recent posts
3. shortlist posts with real discussion
4. scrape comments from those post URLs
5. normalize for goodput instead of raw reach

## What the plugin provides

- A `facebook-comment-discovery` skill under
  `skills/facebook-comment-discovery/`
- Facebook-specific actor notes under `references/`
- Skill-local memory for domain notes, URL notes, ICP notes,
  strategy-specific seed packs, run ledgers, and comment logs
- A helper script to resolve and scaffold note paths
- A helper script to normalize Apify Facebook comment datasets into grouped
  post plus comment shapes
- Codex marketplace metadata at `.codex-plugin/plugin.json`
- Claude Code marketplace metadata at `.claude-plugin/plugin.json`

## Best for

- finding visibility-leverage threads on public Facebook
  pages
- spotting recommendation asks and workflow pain in comments
- separating creator or page relevance from commenter intent
- testing which page clusters repeatedly produce goodput
- building a disciplined goodput ledger instead of counting vanity chatter

## What it does

The plugin adds a research skill that:

- reads an offer URL or short offer summary
- turns the offer into comment-level signal patterns
- prefers page-led post discovery over blind keyword search
- uses `apify/facebook-posts-scraper` to find recent public posts on seeded
  pages
- uses `apify/facebook-comments-scraper` to extract comments from shortlisted
  public post URLs
- ranks comments by commercial signal and engagement value
- drops creator self-comments, low-signal reactions, and self-promo by default
- keeps surfaced hits focused on direct questions and first-person pain
- suppresses thin threads with fewer than three external substantive comments
- classifies kept hits into `direct_buyer`, `visibility_leverage`, or `discard`
- keeps only the `engage_now` set and discards the rest
- drafts casual, thread-aware public reply angles when useful

## Retrieval contract

- The returned queue is `raw surfaces -> engage_now -> discard`.
- There is no watch bucket or maybe-later bucket in the published contract.
- On Facebook, the real motion is page-led or post-led retrieval plus comment
  scoring, not blind open search.

## Runtime requirements

This plugin ships a skill. It does not bundle its own MCP server or app
connector.

### Required

- Codex plugin support with skill loading enabled
- `python3` for the bundled helper scripts
- an authenticated local `apify` CLI session or an Apify tool surface in the
  current run

### What happens without them

- without Apify tooling, the plugin can still build the offer summary, seed
  strategy, ranking framework, and likely page hypotheses
- without live Facebook scraping, it should say that live discovery is blocked
  instead of pretending the run happened

## How it works

1. Read skill-local memory notes for the domain, URL, ICP, seed pack, run
   ledger, and comment log.
2. Reuse curated page clusters and losing seeds before inventing new search
   terms.
3. Break the offer into comment-level signal patterns such as recommendation
   asks, workflow confusion, first-person need, and implementation friction.
4. Build seed page and seed post hypotheses.
5. Run `apify/facebook-posts-scraper` on known public page URLs to collect
   recent posts.
6. Shortlist posts with visible discussion, then run
   `apify/facebook-comments-scraper` on those post URLs.
7. Normalize the comment dataset into grouped posts plus comment rows with
   thread viability, self-comment exclusion, and keep or suppress decisions.
8. Rank comments, penalize vanity chatter, and split the kept set into
   commercial outcomes plus action types.
9. Draft thread-aware replies or follow-up angles when asked.

## Usage

Example prompts:

- Find Facebook signal for `https://audienti.com/exo` and show the best posts and comments.
- Turn this offer into Facebook seed pages, findings, and reply angles.
- Find real Facebook comments where this ICP is asking for help with the problem.
- Run Facebook industry search and engagement for this offer and tell me what I should write.

## Repository layout

```text
.codex-plugin/plugin.json
.claude-plugin/plugin.json
skills/facebook-comment-discovery/SKILL.md
skills/facebook-comment-discovery/assets/finding-template.md
skills/facebook-comment-discovery/references/apify-facebook-actors.md
skills/facebook-comment-discovery/references/comment-modes.md
skills/facebook-comment-discovery/references/comment-signal-framework.md
skills/facebook-comment-discovery/references/facebook-engagement-rubric.md
skills/facebook-comment-discovery/scripts/normalize_apify_comment_results.py
skills/facebook-comment-discovery/scripts/resolve_memory.py
skills/facebook-comment-discovery/memory/README.md
skills/facebook-comment-discovery/memory/lessons.md
skills/facebook-comment-discovery/memory/domains/
skills/facebook-comment-discovery/memory/icps/
skills/facebook-comment-discovery/memory/run_ledgers/
skills/facebook-comment-discovery/memory/seed_packs/
skills/facebook-comment-discovery/memory/urls/
skills/facebook-comment-discovery/memory/comments/
skills/facebook-comment-discovery/memory/templates/
```

## Validation

```bash
python3 /Users/williamflanagan/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
python3 /Users/williamflanagan/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/facebook-comment-discovery
python3 skills/facebook-comment-discovery/scripts/resolve_memory.py --url https://example.com --icp "AI startup founders" --strategy "visibility_leverage"
python3 skills/facebook-comment-discovery/scripts/normalize_apify_comment_results.py --input sample.json
```

## License

Copyright (c) 2026 OMALab, Inc. All rights reserved.

## Marketplace source

Marketplace entries can reference this repository:

```text
https://github.com/audienti/facebook-comment-finder.git
```
