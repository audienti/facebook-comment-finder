#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


FIRST_PERSON_RE = re.compile(r"\b(i|we|my|our|me|us)\b", re.IGNORECASE)
SECOND_PERSON_RE = re.compile(r"\b(you|your|yours)\b", re.IGNORECASE)
REQUEST_RE = re.compile(
    r"\b(looking for|recommend|recommendation|what are you using|need help|struggling|any advice|anyone using|need a tool|what would you use)\b",
    re.IGNORECASE,
)
PAIN_RE = re.compile(
    r"\b(broken|manual|slow|friction|painful|stuck|vendor|renewal|delay|outage|risk|approval|support|hard to|hard when|messy)\b",
    re.IGNORECASE,
)
STRATEGIC_RE = re.compile(
    r"\b(evaluating|shortlist|compare|comparison|budget|planning|migration|transition|governance|decisioning|first customers|go to market|pipeline|positioning|end-of-quarter)\b",
    re.IGNORECASE,
)
HARD_PROMO_RE = re.compile(
    r"\b(dm me|book a call|book a demo|free trial|use my code|telegram|whatsapp)\b",
    re.IGNORECASE,
)
PROMO_RE = re.compile(
    r"\b(launching|launched|join my|join us|waitlist|free doc|free guide|template|download the guide)\b",
    re.IGNORECASE,
)
AI_SLOP_RE = re.compile(
    r"\b(10x|game changer|vibe coded|vibecoded|agentic|unlock|revolutionize|disrupt|guru|five prompts|7 prompts|top 5 tools|top 10 tools)\b",
    re.IGNORECASE,
)
BUSINESS_CONTEXT_RE = re.compile(
    r"\b(founder|startup|saas|b2b|sales|sdr|revops|marketing|growth|pipeline|procurement|vendor|supplier|renewal|qbr|operations|it\b|cio|director|vp|credit|aml|underwriting|bank|fintech|compliance|risk|data center|colocation|buyers|customers)\b",
    re.IGNORECASE,
)
BUSINESS_ROLE_RE = re.compile(
    r"\b(founder|co-founder|ceo|cfo|coo|cto|cmo|cpo|ciso|cio|vp|vice president|director|head of|lead|manager|procurement|purchasing|operations|sourcing|supply chain|infrastructure|it\b|risk|aml|credit|compliance|sales|marketing|revops)\b",
    re.IGNORECASE,
)
WORD_RE = re.compile(r"[a-z0-9']+")


def load_items(path: str | None) -> list[dict]:
    if path:
        payload = Path(path).read_text()
    else:
        payload = sys.stdin.read()
    data = json.loads(payload or "[]")
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array of Apify dataset items.")
    return [item for item in data if isinstance(item, dict)]


def pick(*values):
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return None


def clean_text(value) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def normalize_text(text: str) -> str:
    return clean_text(text).lower()


def is_substantive_text(text: str) -> bool:
    normalized = normalize_text(text)
    if len(WORD_RE.findall(normalized)) >= 6:
        return True
    return bool(REQUEST_RE.search(normalized) or PAIN_RE.search(normalized) or STRATEGIC_RE.search(normalized))


def speaker_perspective(text: str) -> str:
    normalized = normalize_text(text)
    if FIRST_PERSON_RE.search(normalized):
        return "first_person_self_report"
    if SECOND_PERSON_RE.search(normalized):
        return "second_person_advice"
    return "other"


def extract_author(item: dict) -> dict:
    user = item.get("user") or {}
    if not isinstance(user, dict):
        user = {}
    return {
        "handle": clean_text(pick(item.get("pageName"), user.get("name"))) or None,
        "name": clean_text(pick(user.get("name"), item.get("pageName"))) or None,
        "bio": clean_text(pick(item.get("pageName"), user.get("name"), item.get("inputUrl"))) or None,
    }


def extract_metrics(item: dict) -> dict:
    return {
        "likeCount": int(pick(item.get("likes"), item.get("topReactionsCount"), 0) or 0),
        "commentCount": int(pick(item.get("comments"), 0) or 0),
        "shareCount": int(pick(item.get("shares"), 0) or 0),
    }


def audience_activity(metrics: dict) -> bool:
    return bool(metrics["commentCount"] >= 1 or metrics["shareCount"] >= 1 or metrics["likeCount"] >= 1)


def classify_surface(
    *,
    substantive_text: bool,
    business_surface: bool,
    root_operator_signal: bool,
    ai_slop: bool,
) -> str:
    if not substantive_text or not business_surface or ai_slop:
        return "discard"
    if root_operator_signal:
        return "direct_buyer"
    return "visibility_leverage"


def choose_action_type(
    *,
    commercial_path: str,
    audience_backed: bool,
    root_operator_signal: bool,
) -> str:
    if commercial_path == "discard":
        return "discard"
    if commercial_path == "direct_buyer":
        return "engage_now"
    if audience_backed or root_operator_signal:
        return "engage_now"
    return "discard"


def failure_mode(flags: dict) -> str:
    if flags["isAiSlopLikely"]:
        return "ai_slop_or_hot_take"
    if not flags["businessSurface"]:
        return "not_a_business_surface"
    if not flags["audienceBacked"] and not flags["rootOperatorSignal"]:
        return "thin_surface"
    return "goodput_candidate"


def normalize_item(item: dict) -> dict:
    text = clean_text(item.get("text"))
    author = extract_author(item)
    metrics = extract_metrics(item)
    perspective = speaker_perspective(text)
    request_signal = bool(REQUEST_RE.search(text))
    pain_signal = bool(PAIN_RE.search(text))
    strategic_signal = bool(STRATEGIC_RE.search(text))
    hard_promo = bool(HARD_PROMO_RE.search(text))
    promo = bool(PROMO_RE.search(text))
    ai_slop = bool(AI_SLOP_RE.search(text))
    substantive_text = is_substantive_text(text)
    author_business_role = bool(BUSINESS_ROLE_RE.search(clean_text(author.get("bio"))))
    business_context = bool(BUSINESS_CONTEXT_RE.search(text))
    business_surface = business_context or author_business_role
    root_operator_signal = bool(
        substantive_text
        and business_surface
        and not hard_promo
        and (
            request_signal
            or strategic_signal
            or (perspective == "first_person_self_report" and pain_signal)
        )
    )
    audience_backed = audience_activity(metrics)
    commercial_path = classify_surface(
        substantive_text=substantive_text,
        business_surface=business_surface,
        root_operator_signal=root_operator_signal,
        ai_slop=ai_slop,
    )
    action_type = choose_action_type(
        commercial_path=commercial_path,
        audience_backed=audience_backed,
        root_operator_signal=root_operator_signal,
    )
    return {
        "id": clean_text(pick(item.get("postId"), item.get("feedbackId"))) or None,
        "url": clean_text(pick(item.get("url"), item.get("topLevelUrl"))) or None,
        "text": text,
        "createdAt": clean_text(pick(item.get("time"), item.get("timestamp"))) or None,
        "author": author,
        "metrics": metrics,
        "analysis": {
            "speakerPerspectiveHint": perspective,
            "requestSignal": request_signal,
            "painSignal": pain_signal,
            "strategicSignal": strategic_signal,
            "isPromotional": promo,
            "isHardPromotional": hard_promo,
            "isAiSlopLikely": ai_slop,
            "businessSurface": business_surface,
            "audienceBacked": audience_backed,
            "rootOperatorSignal": root_operator_signal,
            "commercialClass": commercial_path,
            "actionType": action_type,
            "goodputCandidate": action_type == "engage_now",
            "primaryFailureMode": failure_mode(
                {
                    "isAiSlopLikely": ai_slop,
                    "businessSurface": business_surface,
                    "audienceBacked": audience_backed,
                    "rootOperatorSignal": root_operator_signal,
                }
            ),
        },
        "raw": item,
    }


def build_run_ledger(summary: dict) -> dict:
    surface_count = summary["scrapedThreadCount"]
    goodput_count = summary["goodputOpportunityCount"]
    visibility_only_count = summary["visibilityOnlyCount"]
    return {
        "queryCount": 0,
        "seedCount": 0,
        "scrapedThreadCount": surface_count,
        "externalSubstantiveDiscussionCount": summary["audienceBackedCount"],
        "goodputOpportunityCount": goodput_count,
        "postedEngagementCount": 0,
        "visibilityOnlyCount": visibility_only_count,
        "primaryFailureMode": summary["primaryFailureMode"],
        "markdownRow": (
            "| YYYY-MM-DD | "
            f"0 | 0 | {surface_count} | {summary['audienceBackedCount']} | "
            f"{goodput_count} | 0 | {summary['primaryFailureMode']} | replace with live notes |"
        ),
    }


def normalize(items: list[dict]) -> dict:
    seen = set()
    posts = []
    duplicates = 0

    for item in items:
        normalized = normalize_item(item)
        key = normalized["id"] or normalized["url"] or normalized["text"]
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        posts.append(normalized)

    posts.sort(
        key=lambda item: (
            1 if item["analysis"]["actionType"] == "engage_now" else 0,
            item["metrics"]["shareCount"],
            item["metrics"]["likeCount"],
            item["metrics"]["commentCount"],
        ),
        reverse=True,
    )

    failure_counts = Counter(item["analysis"]["primaryFailureMode"] for item in posts)
    summary = {
        "rawSurfaceCount": len(items),
        "duplicateCount": duplicates,
        "scrapedThreadCount": len(posts),
        "marketRelevantSurfaceCount": sum(1 for post in posts if post["analysis"]["businessSurface"]),
        "audienceBackedCount": sum(1 for post in posts if post["analysis"]["audienceBacked"]),
        "goodputOpportunityCount": sum(1 for post in posts if post["analysis"]["goodputCandidate"]),
        "directBuyerCount": sum(
            1
            for post in posts
            if post["analysis"]["commercialClass"] == "direct_buyer"
            and post["analysis"]["actionType"] == "engage_now"
        ),
        "visibilityLeverageCount": sum(
            1
            for post in posts
            if post["analysis"]["commercialClass"] == "visibility_leverage"
            and post["analysis"]["actionType"] == "engage_now"
        ),
        "engageNowCount": sum(1 for post in posts if post["analysis"]["actionType"] == "engage_now"),
        "deepenNowCount": 0,
        "discardCount": sum(1 for post in posts if post["analysis"]["actionType"] == "discard"),
        "visibilityOnlyCount": sum(
            1 for post in posts if post["analysis"]["commercialClass"] == "visibility_leverage"
        ),
        "primaryFailureMode": (
            failure_counts.most_common(1)[0][0]
            if failure_counts
            else ("goodput_present" if posts else "no_results")
        ),
    }
    tuning = {
        "primaryFailureMode": summary["primaryFailureMode"],
        "stopLossTriggered": summary["goodputOpportunityCount"] == 0,
        "spendDecision": (
            "engage_and_track_replies"
            if summary["goodputOpportunityCount"] > 0
            else "retune_pages_or_seed_sources"
        ),
    }
    return {
        "summary": summary,
        "tuning": tuning,
        "runLedger": build_run_ledger(summary),
        "posts": posts,
        "viablePosts": [post for post in posts if post["analysis"]["actionType"] == "engage_now"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize Facebook page post datasets into post-level goodput analysis."
    )
    parser.add_argument(
        "--input",
        help="Path to a JSON file containing dataset items. Reads stdin when omitted.",
    )
    args = parser.parse_args()

    items = load_items(args.input)
    print(json.dumps(normalize(items), indent=2))


if __name__ == "__main__":
    main()
