# Apify Facebook Actor Notes

Use this file to verify the live actor schemas before running Facebook comment
discovery.

These notes were grounded against live `apify` CLI checks on 2026-06-18 plus
sample runs in this workspace.

## Primary Actors

### 1. Page-Led Post Discovery

Actor:

```text
apify/facebook-posts-scraper
```

Purpose:

- scrape recent posts from one or more public Facebook pages
- find candidate posts with visible discussion before paying for comment pulls

Verify schema:

```bash
apify actors info apify/facebook-posts-scraper --input
```

Key input fields observed live:

- `startUrls`
- `resultsLimit`
- `captionText`
- `onlyPostsNewerThan`
- `onlyPostsOlderThan`

Page-led default:

```json
{
  "startUrls": [
    {
      "url": "https://www.facebook.com/examplepage/"
    }
  ],
  "resultsLimit": 5,
  "onlyPostsNewerThan": "30 days"
}
```

Observed live output shape:

- `url`
- `text`
- `time`
- `comments`
- `likes`
- `pageName`
- `user.name`
- `user.profileUrl`
- `facebookUrl`

Notes from the live checks:

- The maintained posts actor targets public pages, not personal profiles.
- A sample run on 2026-06-18 against `https://www.facebook.com/humansofnewyork/`
  succeeded and returned public reel or post URLs plus engagement counts.
- Use this actor to shortlist posts worth a second comments pass, or return
  them directly as visibility-leverage surfaces when the root post is already
  strong.

Typical call flow:

```bash
apify call apify/facebook-posts-scraper --input-file posts-input.json --silent --json
apify datasets get-items <datasetId> > posts.json
```

### 2. Post-Led Comment Collection

Actor:

```text
apify/facebook-comments-scraper
```

Purpose:

- scrape comments from known public Facebook post URLs
- use after a page-led post shortlist or when exact post URLs are already
  known

Verify schema:

```bash
apify actors info apify/facebook-comments-scraper --input
```

Key input fields observed live:

- `startUrls`
- `resultsLimit`
- `includeNestedComments`
- `viewOption`
- `onlyCommentsNewerThan`

Default:

```json
{
  "startUrls": [
    {
      "url": "https://www.facebook.com/examplepage/posts/EXAMPLE/"
    }
  ],
  "resultsLimit": 50,
  "includeNestedComments": false,
  "viewOption": "RANKED_UNFILTERED"
}
```

Observed live output shape:

- `facebookUrl`
- `commentUrl`
- `commentId`
- `date`
- `text`
- `profileName`
- `profilePicture`
- `likesCount`
- `commentsCount`
- `postTitle`
- `inputUrl`

Notes from the live checks:

- A sample run on 2026-06-18 against the maintained prefill post succeeded and
  returned flat comment rows with the source post URL attached.
- The actor is good for grouping comments back to the same public post.
- Nested replies can be useful later, but default to `false` until the top
  level is proven productive.

Typical call flow:

```bash
apify call apify/facebook-comments-scraper --input-file comments-input.json --silent --json
apify datasets get-items <datasetId> > comments.json
python3 scripts/normalize_apify_comment_results.py --input comments.json
```

## Search Strategy Implications

- Default to seeded public pages, not open search.
- Use the posts actor to shortlist discussion-worthy posts before the comments
  actor.
- Treat open web search as seed refresh only.
- Expect Facebook to skew more toward `audience_leverage`,
  `market_learning`, or `referral_channel` than clean direct-buyer signal.
