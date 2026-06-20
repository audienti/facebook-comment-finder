#!/usr/bin/env python3
from __future__ import annotations

from normalize_apify_search_results import normalize


def main() -> None:
    good = {
        "postId": "1",
        "url": "https://facebook.com/good",
        "text": "The worst end-of-quarter sales rep behavior I have seen yet",
        "pageName": "SaaStr",
        "user": {"name": "SaaStr"},
        "likes": 2,
        "shares": 1,
        "topReactionsCount": 2,
        "time": "2026-06-20T12:22:37.000Z",
    }
    bad = {
        "postId": "2",
        "url": "https://facebook.com/bad",
        "text": "top 10 tools to unlock 10x growth instantly",
        "pageName": "Growth Wizard",
        "user": {"name": "Growth Wizard"},
        "likes": 99,
        "shares": 12,
        "topReactionsCount": 100,
        "time": "2026-06-20T12:22:37.000Z",
    }
    bait = {
        "postId": "3",
        "url": "https://facebook.com/bait",
        "text": "Follow our page for daily growth hacks. Comment GUIDE and we'll send it.",
        "pageName": "Growth Wizard",
        "user": {"name": "Growth Wizard"},
        "likes": 40,
        "shares": 8,
        "topReactionsCount": 42,
        "time": "2026-06-20T12:22:37.000Z",
    }
    result = normalize([good, bad, bait])
    posts = {post["id"]: post for post in result["posts"]}
    assert posts["1"]["analysis"]["actionType"] == "engage_now"
    assert posts["2"]["analysis"]["actionType"] == "discard"
    assert posts["3"]["analysis"]["actionType"] == "discard"


if __name__ == "__main__":
    main()
