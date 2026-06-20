#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


ALNUM_RE = re.compile(r"[a-z0-9]")
WORD_RE = re.compile(r"[a-z0-9']+")
FIRST_PERSON_RE = re.compile(
    r"\b(i|i'm|im|i’ve|i've|me|my|mine|myself|we|we're|were|weve|we've|our|ours|us)\b"
)
SECOND_PERSON_RE = re.compile(r"\b(you|your|yours|u)\b")
QUESTION_STARTS = (
    "how ",
    "what ",
    "why ",
    "where ",
    "when ",
    "which ",
    "who ",
    "does ",
    "do ",
    "did ",
    "is ",
    "are ",
    "can ",
    "could ",
    "should ",
    "would ",
    "anyone ",
    "worth ",
    "will ",
)
PROBLEM_PATTERNS = (
    "need",
    "looking for",
    "struggling",
    "stuck",
    "can't",
    "cannot",
    "hard",
    "problem",
    "issue",
    "pain",
    "confused",
    "overwhelmed",
    "trying to",
    "don't know",
    "do not know",
    "not sure",
    "unclear",
    "friction",
    "difficult",
)
RECOMMENDATION_PATTERNS = (
    "recommend",
    "recommendation",
    "what do you use",
    "what are you using",
    "which tool",
    "any tool",
    "tool for",
    "anyone know",
    "advice",
    "help",
    "worth it",
    "how do you",
    "how to",
)
SELF_PROMO_PATTERNS = (
    "dm me",
    "check my",
    "link in bio",
    "follow me",
    "follow for more",
    "contact us",
    "book a call",
    "telegram",
    "whatsapp",
    "http://",
    "https://",
    "www.",
    ".com",
)
LOW_SIGNAL_PATTERNS = (
    "love this",
    "great insights",
    "great post",
    "so true",
    "well said",
    "nice",
    "niceee",
    "wow",
    "lets go",
    "let's go",
    "amazing",
    "incredible",
    "fire",
    "will be there",
)


def load_items(path: str | None) -> list[dict]:
    if path:
        payload = Path(path).read_text()
    else:
        payload = sys.stdin.read()
    data = json.loads(payload or "[]")
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array of Apify dataset items.")
    return [item for item in data if isinstance(item, dict)]


def clean_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        value = json.dumps(value, sort_keys=True)
    return str(value).strip()


def pick(*values):
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return None


def normalize_text(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(pattern in text for pattern in patterns)


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def is_emoji_only(text: str) -> bool:
    compact = re.sub(r"\s+", "", text or "")
    return bool(compact) and not ALNUM_RE.search(compact)


def detect_direct_question(text: str, normalized_text: str) -> bool:
    return "?" in text or normalized_text.startswith(QUESTION_STARTS)


def speaker_perspective(
    is_direct_question: bool,
    has_first_person: bool,
    normalized_text: str,
) -> str:
    if is_direct_question:
        return "direct_question"
    if has_first_person:
        return "first_person_self_report"
    if SECOND_PERSON_RE.search(normalized_text):
        return "second_person_advice"
    if word_count(normalized_text) <= 6:
        return "generic_reaction"
    return "other"


def comment_type(
    is_self_promo: bool,
    is_direct_question: bool,
    has_recommendation_intent: bool,
    has_problem_signal: bool,
    is_low_signal: bool,
) -> str:
    if is_self_promo:
        return "self_promo"
    if is_direct_question:
        return "question"
    if has_recommendation_intent:
        return "recommendation_ask"
    if has_problem_signal:
        return "pain_or_problem"
    if is_low_signal:
        return "generic_reaction"
    return "discussion"


def extract_page_handle(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(url)
    path = (parsed.path or "").strip("/")
    if not path:
        return None
    first = path.split("/", 1)[0]
    if first in {"posts", "reel", "watch", "photo"}:
        return None
    return first


def build_comment_id(item: dict) -> str:
    parts = [
        str(pick(item.get("date"), "")),
        str(pick(item.get("profileName"), "")),
        str(pick(item.get("text"), ""))[:80],
    ]
    return "::".join(parts)


def normalize_comment(item: dict) -> dict:
    post_url = pick(item.get("facebookUrl"), item.get("inputUrl"), item.get("commentUrl"))
    seed_page_url = pick(item.get("inputUrl"), item.get("facebookUrl"))
    creator_handle = pick(
        extract_page_handle(seed_page_url),
        extract_page_handle(item.get("facebookUrl")),
        item.get("pageName"),
    )
    creator_name = pick(item.get("pageName"), creator_handle)
    commenter_handle = item.get("profileName")
    text = str(item.get("text") or "").strip()
    normalized_text = normalize_text(text)
    is_direct_question = detect_direct_question(text, normalized_text)
    has_first_person = bool(FIRST_PERSON_RE.search(normalized_text))
    has_problem_signal = contains_any(normalized_text, PROBLEM_PATTERNS)
    has_recommendation_intent = contains_any(normalized_text, RECOMMENDATION_PATTERNS)
    emoji_only = is_emoji_only(text)
    is_self_promo = contains_any(normalized_text, SELF_PROMO_PATTERNS)
    low_signal_phrase = contains_any(normalized_text, LOW_SIGNAL_PATTERNS)
    is_low_signal = emoji_only or (
        low_signal_phrase and not is_direct_question and not has_problem_signal
    )
    is_substantive = bool(
        is_direct_question
        or has_problem_signal
        or has_recommendation_intent
        or word_count(normalized_text) >= 8
    )
    creator_identity = normalize_text(str(pick(creator_name, creator_handle) or ""))
    commenter_identity = normalize_text(str(commenter_handle or ""))
    is_creator_self_comment = bool(
        creator_identity
        and commenter_identity
        and creator_identity == commenter_identity
    )
    is_first_person_pain = has_first_person and (
        has_problem_signal or has_recommendation_intent or is_direct_question
    )

    exclusion_reasons = []
    if is_creator_self_comment:
        exclusion_reasons.append("creator_self_comment")
    if is_self_promo:
        exclusion_reasons.append("self_promotional")
    if emoji_only:
        exclusion_reasons.append("emoji_only")
    if is_low_signal and not emoji_only:
        exclusion_reasons.append("generic_low_signal")
    if not is_substantive:
        exclusion_reasons.append("not_substantive")
    if not (is_direct_question or is_first_person_pain):
        exclusion_reasons.append("not_direct_question_or_first_person_pain")

    signal_flags = []
    if is_direct_question:
        signal_flags.append("direct_question")
    if has_first_person:
        signal_flags.append("first_person")
    if has_problem_signal:
        signal_flags.append("problem_signal")
    if has_recommendation_intent:
        signal_flags.append("recommendation_intent")
    if is_substantive:
        signal_flags.append("substantive")

    keep_by_default = not exclusion_reasons

    return {
        "id": build_comment_id(item),
        "postUrl": post_url,
        "postId": pick(item.get("facebookId"), item.get("postId")),
        "creatorHandle": creator_handle,
        "creatorName": creator_name,
        "seedProfileUrl": seed_page_url,
        "caption": item.get("postTitle"),
        "hashtags": [],
        "commentText": text,
        "createdAt": item.get("date"),
        "commenterHandle": commenter_handle,
        "commenterProfilePicUrl": item.get("profilePicture"),
        "commentUrl": item.get("commentUrl"),
        "commenterProfileId": item.get("profileId"),
        "replyCount": item.get("commentsCount"),
        "likeCount": item.get("likesCount"),
        "analysis": {
            "speakerPerspective": speaker_perspective(
                is_direct_question=is_direct_question,
                has_first_person=has_first_person,
                normalized_text=normalized_text,
            ),
            "commentType": comment_type(
                is_self_promo=is_self_promo,
                is_direct_question=is_direct_question,
                has_recommendation_intent=has_recommendation_intent,
                has_problem_signal=has_problem_signal,
                is_low_signal=is_low_signal,
            ),
            "wordCount": word_count(normalized_text),
            "isCreatorSelfComment": is_creator_self_comment,
            "isExternalComment": not is_creator_self_comment,
            "isDirectQuestion": is_direct_question,
            "hasFirstPerson": has_first_person,
            "hasProblemSignal": has_problem_signal,
            "hasRecommendationIntent": has_recommendation_intent,
            "isEmojiOnly": emoji_only,
            "isLowSignal": is_low_signal,
            "isSelfPromotional": is_self_promo,
            "isSubstantive": is_substantive,
            "isFirstPersonPain": is_first_person_pain,
            "keepByDefault": keep_by_default,
            "isGoodputCandidate": keep_by_default,
            "signalFlags": signal_flags,
            "exclusionReasons": exclusion_reasons,
        },
    }


def is_error_row(item: dict) -> bool:
    return bool(pick(item.get("error"), item.get("errorDescription")))


def comment_signature(comment: dict) -> str:
    return "::".join(
        [
            str(comment.get("postUrl") or ""),
            str(comment.get("commenterHandle") or "").lower(),
            normalize_text(str(comment.get("commentText") or "")),
        ]
    )


def ratio(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator / denominator, 4)


def classify_post_outcome(
    *,
    kept_comment_count: int,
    external_substantive_comment_count: int,
) -> str:
    if kept_comment_count > 0:
        return "direct_buyer"
    if external_substantive_comment_count > 0:
        return "visibility_leverage"
    return "discard"


def choose_post_action(
    *,
    commercial_path: str,
    kept_comment_count: int,
    external_substantive_comment_count: int,
    min_external_substantive_comments: int,
) -> str:
    if commercial_path == "discard" or kept_comment_count == 0:
        return "discard"
    return "engage_now"


def build_tuning_diagnostics(summary: dict, seed_counts: dict[str, int]) -> dict:
    total_items = int(summary.get("totalItems", 0))
    post_count = int(summary.get("postCount", 0))
    attempted_seed_count = int(summary.get("attemptedSeedCount", 0))
    accessible_seed_count = int(summary.get("accessibleSeedCount", 0))
    seed_error_count = int(summary.get("seedErrorCount", 0))
    goodput_thread_count = int(summary.get("goodputOpportunityCount", 0))
    external_comment_count = int(summary.get("externalCommentCount", 0))
    external_substantive_count = int(summary.get("externalSubstantiveCommentCount", 0))
    kept_comment_count = int(summary.get("keptCommentCount", 0))
    creator_self_comment_count = int(summary.get("creatorSelfCommentCount", 0))
    low_signal_comment_count = int(summary.get("lowSignalCommentCount", 0))
    self_promotional_comment_count = int(summary.get("selfPromotionalCommentCount", 0))
    direct_question_count = int(summary.get("directQuestionCount", 0))
    first_person_pain_count = int(summary.get("firstPersonPainCount", 0))
    seed_count = attempted_seed_count or len(seed_counts)

    actionable_signal_count = direct_question_count + first_person_pain_count
    visibility_only_comment_count = max(0, external_substantive_count - kept_comment_count)
    rates = {
        "goodputThreadRate": ratio(goodput_thread_count, post_count),
        "externalSubstantiveRate": ratio(external_substantive_count, external_comment_count),
        "goodputCommentRate": ratio(kept_comment_count, external_substantive_count),
        "lowSignalRate": ratio(low_signal_comment_count, total_items),
        "selfCommentRate": ratio(creator_self_comment_count, total_items),
        "selfPromotionalRate": ratio(self_promotional_comment_count, total_items),
        "commentsPerSeed": ratio(total_items, seed_count),
        "goodputSignalsPerSeed": ratio(actionable_signal_count, seed_count),
        "visibilityOnlyRate": ratio(visibility_only_comment_count, external_substantive_count),
    }

    if goodput_thread_count > 0:
        primary_failure_mode = "productive"
        spend_decision = "continue_with_known_good_pages"
        next_actions = [
            "Expand from the viable page cluster before testing new searches.",
            "Log the winning page or post cluster in the seed pack and keep engaging where the audience stays relevant.",
        ]
    elif attempted_seed_count > 0 and seed_error_count == attempted_seed_count:
        primary_failure_mode = "no_accessible_comments"
        spend_decision = "change_seed_source_or_access_mode"
        next_actions = [
            "Do not retry the same public post URLs. They are returning inaccessible or empty comment surfaces.",
            "Prefer new public pages or public posts with visible discussion before paying for another comments pass.",
        ]
    elif total_items == 0:
        primary_failure_mode = "no_comment_volume"
        spend_decision = "pause_and_change_seed_source"
        next_actions = [
            "Do not burn more comment runs on the same seeds.",
            "Refresh the seed pack with new page clusters before another comments pass.",
        ]
    elif creator_self_comment_count >= max(1, round(total_items * 0.4)):
        primary_failure_mode = "creator_self_comment_dominance"
        spend_decision = "retune_to_external_discussion_pages"
        next_actions = [
            "Avoid pages where the creator carries the thread with pinned or promotional self-comments.",
            "Prefer pages whose audiences ask follow-up questions or talk about implementation.",
        ]
    elif external_substantive_count < int(summary.get("minExternalSubstantiveComments", 3)):
        primary_failure_mode = "thin_discussion"
        spend_decision = "switch_to_higher-discussion-pages"
        next_actions = [
            "Keep the theme, but swap the seed source to pages with denser external comment sections.",
            "Do not lower the thread threshold until a better page cluster has been tested.",
        ]
    elif kept_comment_count == 0 and external_substantive_count > 0:
        primary_failure_mode = "visibility_without_goodput"
        spend_decision = "change_lane_or_profile_family"
        next_actions = [
            "Do not count this as success. The thread has visibility but no credible engagement opportunity.",
            "Retune toward recommendation asks, offer-testing questions, or implementation confusion rather than broad community chatter.",
        ]
    elif low_signal_comment_count >= max(3, round(total_items * 0.35)):
        primary_failure_mode = "low_signal_audience"
        spend_decision = "avoid_this_page_cluster"
        next_actions = [
            "Mark this page cluster as noisy in the seed pack.",
            "Shift toward operators or educators whose audiences ask real process questions.",
        ]
    else:
        primary_failure_mode = "seed_mismatch"
        spend_decision = "retune_seeds_before_more_spend"
        next_actions = [
            "The theme may be right, but these pages are not producing buying-adjacent discussion.",
            "Refresh the seed pack before another comment scrape.",
        ]

    stop_loss_triggered = goodput_thread_count == 0 and (
        seed_count >= 1 or total_items >= 15 or external_substantive_count >= 6
    )

    if stop_loss_triggered and primary_failure_mode != "productive":
        next_actions.append(
            "Stop spending on more passes from the same lane until the seed pack or lane changes."
        )

    return {
        "seedCount": seed_count,
        "goodputCommentCount": kept_comment_count,
        "goodputThreadCount": goodput_thread_count,
        "attemptedSeedCount": attempted_seed_count,
        "accessibleSeedCount": accessible_seed_count,
        "seedErrorCount": seed_error_count,
        "visibilityOnlyCommentCount": visibility_only_comment_count,
        "primaryFailureMode": primary_failure_mode,
        "spendDecision": spend_decision,
        "stopLossTriggered": stop_loss_triggered,
        "rates": rates,
        "nextActions": next_actions,
    }


def build_run_ledger(summary: dict, tuning: dict) -> dict:
    query_count = 0
    seed_count = tuning["seedCount"]
    scraped_thread_count = summary["postCount"]
    external_discussion_count = summary["externalSubstantiveThreadCount"]
    goodput_thread_count = tuning["goodputThreadCount"]
    goodput_comment_count = tuning["goodputCommentCount"]
    return {
        "queryCount": query_count,
        "seedCount": seed_count,
        "scrapedThreadCount": scraped_thread_count,
        "externalSubstantiveDiscussionCount": external_discussion_count,
        "goodputOpportunityCount": goodput_thread_count,
        "goodputCommentCount": goodput_comment_count,
        "postedEngagementCount": 0,
        "primaryFailureMode": tuning["primaryFailureMode"],
        "markdownRow": (
            "| YYYY-MM-DD | "
            f"{query_count} | {seed_count} | {scraped_thread_count} | {external_discussion_count} | "
            f"{goodput_thread_count} | 0 | {tuning['primaryFailureMode']} | "
            f"goodput comments={goodput_comment_count}; replace with live notes |"
        ),
    }


def normalize(items: list[dict], min_external_substantive_comments: int = 3) -> dict:
    posts: dict[str, dict] = {}
    attempted_seed_counts = Counter()
    error_rows = []
    valid_items = []

    for item in items:
        attempted_seed = str(
            pick(item.get("inputUrl"), item.get("facebookUrl"), item.get("commentUrl"), "unknown")
        )
        attempted_seed_counts[attempted_seed] += 1
        if is_error_row(item):
            error_rows.append(
                {
                    "inputUrl": attempted_seed,
                    "error": clean_text(item.get("error")) or None,
                    "errorDescription": clean_text(item.get("errorDescription")) or None,
                }
            )
            continue
        valid_items.append(item)

    seed_counts = Counter(attempted_seed_counts)

    for item in valid_items:
        normalized = normalize_comment(item)
        post_url = normalized["postUrl"] or "unknown"

        post_entry = posts.setdefault(
            post_url,
            {
                "postUrl": normalized["postUrl"],
                "postId": normalized["postId"],
                "creatorHandle": normalized["creatorHandle"],
                "creatorName": normalized["creatorName"],
                "seedProfileUrl": normalized["seedProfileUrl"],
                "caption": normalized["caption"],
                "hashtags": normalized["hashtags"],
                "comments": [],
            },
        )
        post_entry["comments"].append(normalized)

    grouped_posts = []
    unique_commenters = set()
    dropped_duplicate_count = 0
    viable_post_count = 0
    external_comment_count = 0
    external_substantive_count = 0
    kept_comment_count = 0
    creator_self_comment_count = 0
    low_signal_count = 0
    self_promo_count = 0
    direct_question_count = 0
    first_person_pain_count = 0
    visibility_only_comment_count = 0

    for post in posts.values():
        raw_comments = sorted(
            post["comments"],
            key=lambda comment: str(comment.get("createdAt") or ""),
        )
        comments = []
        seen_signatures = set()
        for comment in raw_comments:
            signature = comment_signature(comment)
            if signature in seen_signatures:
                dropped_duplicate_count += 1
                continue
            seen_signatures.add(signature)
            comments.append(comment)

        kept_comments = []
        for comment in comments:
            handle = comment.get("commenterHandle")
            if handle:
                unique_commenters.add(handle)
            analysis = comment.get("analysis") or {}
            if analysis.get("isExternalComment"):
                external_comment_count += 1
            if analysis.get("isCreatorSelfComment"):
                creator_self_comment_count += 1
            if analysis.get("isLowSignal"):
                low_signal_count += 1
            if analysis.get("isSelfPromotional"):
                self_promo_count += 1
            if analysis.get("isDirectQuestion"):
                direct_question_count += 1
            if analysis.get("isFirstPersonPain"):
                first_person_pain_count += 1
            is_external_substantive = bool(
                analysis.get("isExternalComment")
                and analysis.get("isSubstantive")
                and not analysis.get("isLowSignal")
                and not analysis.get("isSelfPromotional")
            )
            if is_external_substantive:
                external_substantive_count += 1
            if analysis.get("keepByDefault"):
                kept_comment_count += 1
                kept_comments.append(comment)
            elif is_external_substantive:
                visibility_only_comment_count += 1

        post_external_comment_count = sum(
            1 for comment in comments if (comment.get("analysis") or {}).get("isExternalComment")
        )
        post_external_substantive_count = sum(
            1
            for comment in comments
            if (
                (comment.get("analysis") or {}).get("isExternalComment")
                and (comment.get("analysis") or {}).get("isSubstantive")
                and not (comment.get("analysis") or {}).get("isLowSignal")
                and not (comment.get("analysis") or {}).get("isSelfPromotional")
            )
        )
        commercial_path = classify_post_outcome(
            kept_comment_count=len(kept_comments),
            external_substantive_comment_count=post_external_substantive_count,
        )
        action_type = choose_post_action(
            commercial_path=commercial_path,
            kept_comment_count=len(kept_comments),
            external_substantive_comment_count=post_external_substantive_count,
            min_external_substantive_comments=min_external_substantive_comments,
        )
        passes_thread_threshold = action_type != "discard"
        if passes_thread_threshold:
            viable_post_count += 1
        suppression_reasons = []
        if action_type == "discard" and post_external_substantive_count < min_external_substantive_comments:
            suppression_reasons.append("thin_external_substantive_thread")
        if action_type == "discard" and not kept_comments:
            suppression_reasons.append("no_direct_question_or_first_person_pain")
        grouped_posts.append(
            {
                **post,
                "commentCount": len(comments),
                "droppedDuplicateCount": len(raw_comments) - len(comments),
                "externalCommentCount": post_external_comment_count,
                "externalSubstantiveCommentCount": post_external_substantive_count,
                "keptCommentCount": len(kept_comments),
                "commercialClass": commercial_path,
                "actionType": action_type,
                "passesThreadThreshold": passes_thread_threshold,
                "suppressionReasons": suppression_reasons,
                "keptComments": kept_comments,
                "comments": comments,
            }
        )

    grouped_posts.sort(key=lambda post: post["commentCount"], reverse=True)

    seed_count_map = dict(seed_counts)

    summary = {
        "totalRawItems": len(items),
        "totalItems": sum(post["commentCount"] for post in grouped_posts),
        "attemptedSeedCount": len(attempted_seed_counts),
        "accessibleSeedCount": len(grouped_posts),
        "seedErrorCount": len(error_rows),
        "seedErrorReasons": dict(
            Counter((row["error"] or row["errorDescription"] or "unknown_error") for row in error_rows)
        ),
        "droppedDuplicateCount": dropped_duplicate_count,
        "postCount": len(grouped_posts),
        "viablePostCount": viable_post_count,
        "externalSubstantiveThreadCount": sum(
            1 for post in grouped_posts if post["externalSubstantiveCommentCount"] > 0
        ),
        "suppressedPostCount": sum(1 for post in grouped_posts if post["actionType"] == "discard"),
        "uniqueCommenters": len(unique_commenters),
        "externalCommentCount": external_comment_count,
        "externalSubstantiveCommentCount": external_substantive_count,
        "keptCommentCount": kept_comment_count,
        "goodputCommentCount": kept_comment_count,
        "creatorSelfCommentCount": creator_self_comment_count,
        "lowSignalCommentCount": low_signal_count,
        "selfPromotionalCommentCount": self_promo_count,
        "directQuestionCount": direct_question_count,
        "firstPersonPainCount": first_person_pain_count,
        "visibilityOnlyCommentCount": visibility_only_comment_count,
        "minExternalSubstantiveComments": min_external_substantive_comments,
        "seedCounts": seed_count_map,
        "goodputOpportunityCount": sum(1 for post in grouped_posts if post["actionType"] == "engage_now"),
        "directBuyerCount": sum(
            1
            for post in grouped_posts
            if post["commercialClass"] == "direct_buyer" and post["actionType"] == "engage_now"
        ),
        "visibilityLeverageCount": sum(
            1
            for post in grouped_posts
            if post["commercialClass"] == "visibility_leverage" and post["actionType"] == "engage_now"
        ),
        "engageNowCount": sum(1 for post in grouped_posts if post["actionType"] == "engage_now"),
        "deepenNowCount": 0,
        "discardCount": sum(1 for post in grouped_posts if post["actionType"] == "discard"),
    }

    tuning = build_tuning_diagnostics(summary, seed_count_map)

    return {
        "summary": summary,
        "tuning": tuning,
        "runLedger": build_run_ledger(summary, tuning),
        "posts": grouped_posts,
        "viablePosts": [post for post in grouped_posts if post["passesThreadThreshold"]],
        "seedErrors": error_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Group Apify Facebook comment dataset items into posts plus normalized comments."
    )
    parser.add_argument(
        "--input",
        help="Path to a JSON file containing dataset items. Reads stdin when omitted.",
    )
    parser.add_argument(
        "--min-external-substantive-comments",
        type=int,
        default=3,
        help="Minimum external substantive comments required for a thread to stay reviewable.",
    )
    args = parser.parse_args()

    items = load_items(args.input)
    print(
        json.dumps(
            normalize(items, min_external_substantive_comments=args.min_external_substantive_comments),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
