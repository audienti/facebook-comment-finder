#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse


SKILL_DIR = Path(__file__).resolve().parent.parent
MEMORY_DIR = SKILL_DIR / "memory"
DOMAIN_DIR = MEMORY_DIR / "domains"
URL_DIR = MEMORY_DIR / "urls"
ICP_DIR = MEMORY_DIR / "icps"
SEED_PACK_DIR = MEMORY_DIR / "seed_packs"
RUN_LEDGER_DIR = MEMORY_DIR / "run_ledgers"
COMMENT_DIR = MEMORY_DIR / "comments"
TEMPLATE_DIR = MEMORY_DIR / "templates"
DOMAIN_TEMPLATE = TEMPLATE_DIR / "domain-note-template.md"
URL_TEMPLATE = TEMPLATE_DIR / "url-note-template.md"
ICP_TEMPLATE = TEMPLATE_DIR / "icp-note-template.md"
SEED_PACK_TEMPLATE = TEMPLATE_DIR / "seed-pack-template.md"
RUN_LEDGER_TEMPLATE = TEMPLATE_DIR / "run-ledger-template.md"
COMMENT_TEMPLATE = TEMPLATE_DIR / "comment-note-template.md"


def normalize_host(host: str) -> str:
    host = host.lower().strip()
    if host.startswith("www."):
        host = host[4:]
    return host


def host_slug(host: str) -> str:
    return normalize_host(host).replace(".", "-")


def path_slug(path: str) -> str:
    trimmed = path.strip().strip("/")
    if not trimmed:
        return ""
    return trimmed.replace("/", "--")


def slugify(value: str) -> str:
    cleaned = value.lower().strip()
    slug_chars = []
    last_was_dash = False
    for char in cleaned:
        if char.isalnum():
            slug_chars.append(char)
            last_was_dash = False
        elif not last_was_dash:
            slug_chars.append("-")
            last_was_dash = True
    slug = "".join(slug_chars).strip("-")
    return slug or "general"


def strategy_slug(strategy: str) -> str:
    return slugify(strategy)


def strategy_alias_slugs(strategy: str | None) -> list[str]:
    if not strategy:
        return []
    slug = strategy_slug(strategy)
    visibility_family = {
        "visibility-leverage",
        "audience-leverage",
        "referral-channel",
        "market-learning",
    }
    if slug not in visibility_family:
        return [slug]

    ordered = []
    for candidate in (
        slug,
        "visibility-leverage",
        "audience-leverage",
        "referral-channel",
        "market-learning",
    ):
        if candidate not in ordered:
            ordered.append(candidate)
    return ordered


def surface_family_slug(surface_family: str) -> str:
    return slugify(surface_family)


def parse_target(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    if not parsed.scheme:
        parsed = urlparse(f"https://{url}")
    if not parsed.netloc:
        raise ValueError(f"Could not parse host from URL: {url}")
    return normalize_host(parsed.netloc), parsed.path or "/"


def build_operational_key(base: str, *parts: str | None) -> str:
    suffixes = [part for part in parts if part]
    if not suffixes:
        return base
    return "__".join([base, *suffixes])


def resolve_operational_key(
    memory_base: str,
    icp_key: str | None,
    strategy_keys: list[str],
    surface_family_key: str | None,
) -> tuple[str, str]:
    candidates = strategy_keys or [None]
    operational_candidates = [
        (strategy_key, build_operational_key(memory_base, icp_key, strategy_key, surface_family_key))
        for strategy_key in candidates
    ]

    for strategy_key, operational_key in operational_candidates:
        if (
            (SEED_PACK_DIR / f"{operational_key}.md").exists()
            or (RUN_LEDGER_DIR / f"{operational_key}.md").exists()
            or (COMMENT_DIR / f"{operational_key}.md").exists()
        ):
            return strategy_key or "", operational_key

    primary_strategy_key, primary_operational_key = operational_candidates[0]
    return primary_strategy_key or "", primary_operational_key


def write_from_template(target: Path, template: Path, title: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    content = template.read_text()
    content = content.replace("# example-com__comment", f"# {title}")
    content = content.replace("# example-com__path", f"# {title}")
    content = content.replace("# example-com__icp", f"# {title}")
    content = content.replace("# example-com__seed-pack", f"# {title}")
    content = content.replace("# example-com__run-ledger", f"# {title}")
    content = content.replace("# example-com", f"# {title}")
    target.write_text(content)


def resolve_paths(
    url: str,
    icp: str | None = None,
    strategy: str | None = None,
    surface_family: str | None = None,
) -> dict:
    host, path = parse_target(url)
    host_key = host_slug(host)
    path_key = path_slug(path)

    domain_note = DOMAIN_DIR / f"{host_key}.md"
    url_note = None
    if path_key:
        url_note = URL_DIR / f"{host_key}__{path_key}.md"

    icp_key = slugify(icp) if icp else None
    strategy_keys = strategy_alias_slugs(strategy)
    strategy_key = strategy_keys[0] if strategy_keys else None
    surface_family_key = surface_family_slug(surface_family) if surface_family else None

    icp_note = None
    if icp_key:
        icp_base = f"{host_key}__{path_key}" if path_key else host_key
        icp_note = ICP_DIR / f"{icp_base}__{icp_key}.md"

    memory_base = f"{host_key}__{path_key}" if path_key else host_key
    resolved_strategy_key, operational_key = resolve_operational_key(
        memory_base,
        icp_key,
        strategy_keys,
        surface_family_key,
    )
    strategy_key = resolved_strategy_key or strategy_key
    seed_pack_note = SEED_PACK_DIR / f"{operational_key}.md"
    run_ledger_note = RUN_LEDGER_DIR / f"{operational_key}.md"
    comment_note = COMMENT_DIR / f"{operational_key}.md"

    return {
        "input_url": url,
        "input_icp": icp,
        "input_strategy": strategy,
        "input_surface_family": surface_family,
        "normalized_host": host,
        "normalized_path": path,
        "domain_key": host_key,
        "url_key": f"{host_key}__{path_key}" if path_key else None,
        "icp_key": icp_key,
        "strategy_key": strategy_key,
        "strategy_alias_keys": strategy_keys,
        "surface_family_key": surface_family_key,
        "seed_pack_key": operational_key,
        "run_ledger_key": operational_key,
        "comment_key": operational_key,
        "domain_note": str(domain_note),
        "url_note": str(url_note) if url_note else None,
        "icp_note": str(icp_note) if icp_note else None,
        "seed_pack_note": str(seed_pack_note),
        "run_ledger_note": str(run_ledger_note),
        "comment_note": str(comment_note),
        "domain_exists": domain_note.exists(),
        "url_exists": url_note.exists() if url_note else None,
        "icp_exists": icp_note.exists() if icp_note else None,
        "seed_pack_exists": seed_pack_note.exists(),
        "run_ledger_exists": run_ledger_note.exists(),
        "comment_exists": comment_note.exists(),
    }


def scaffold(paths: dict) -> dict:
    created = []

    domain_note = Path(paths["domain_note"])
    if not domain_note.exists():
        write_from_template(domain_note, DOMAIN_TEMPLATE, paths["domain_key"])
        created.append(str(domain_note))
        paths["domain_exists"] = True

    if paths["url_note"]:
        url_note = Path(paths["url_note"])
        if not url_note.exists():
            write_from_template(url_note, URL_TEMPLATE, paths["url_key"])
            created.append(str(url_note))
            paths["url_exists"] = True

    if paths["icp_note"]:
        icp_note = Path(paths["icp_note"])
        if not icp_note.exists():
            write_from_template(icp_note, ICP_TEMPLATE, paths["icp_key"])
            created.append(str(icp_note))
            paths["icp_exists"] = True

    seed_pack_note = Path(paths["seed_pack_note"])
    if not seed_pack_note.exists():
        write_from_template(seed_pack_note, SEED_PACK_TEMPLATE, paths["seed_pack_key"])
        created.append(str(seed_pack_note))
        paths["seed_pack_exists"] = True

    run_ledger_note = Path(paths["run_ledger_note"])
    if not run_ledger_note.exists():
        write_from_template(run_ledger_note, RUN_LEDGER_TEMPLATE, paths["run_ledger_key"])
        created.append(str(run_ledger_note))
        paths["run_ledger_exists"] = True

    comment_note = Path(paths["comment_note"])
    if not comment_note.exists():
        write_from_template(comment_note, COMMENT_TEMPLATE, paths["comment_key"])
        created.append(str(comment_note))
        paths["comment_exists"] = True

    paths["created"] = created
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resolve and optionally scaffold skill memory notes for a URL."
    )
    parser.add_argument("--url", required=True, help="Offer URL or host/path to resolve.")
    parser.add_argument("--icp", help="Optional ICP or buyer lens to resolve to an ICP-specific note.")
    parser.add_argument(
        "--strategy",
        help="Optional strategy lane such as direct_buyer or visibility_leverage. Legacy labels like audience_leverage or referral_channel still resolve for existing memory.",
    )
    parser.add_argument(
        "--surface-family",
        help="Optional source surface such as buyer_authored, competitor_audience, creator_audience, community_audience, or partner_audience.",
    )
    parser.add_argument("--scaffold", action="store_true", help="Create missing note files from templates.")
    args = parser.parse_args()

    paths = resolve_paths(
        args.url,
        icp=args.icp,
        strategy=args.strategy,
        surface_family=args.surface_family,
    )
    if args.scaffold:
        paths = scaffold(paths)
    else:
        paths["created"] = []

    print(json.dumps(paths, indent=2))


if __name__ == "__main__":
    main()
