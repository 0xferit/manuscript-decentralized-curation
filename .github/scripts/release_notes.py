#!/usr/bin/env python3
"""Write the notes of a manuscript release, including stacked pull requests.

A release holds the pull requests that release_version.py counts for its
version, the ones merged into main since the latest tag. Each of those also
carries the pull requests merged into its head branch before it merged, so a
stack of pull requests reaches main through one merge. The GitHub release lists
every pull request in GitHub's generated-notes format, with stacked ones
indented under the pull request that carried them. The Zenodo deposit's notes
list only changes to the published paper: pull requests not labelled
release:none.

Runs from .github/workflows/release.yml once a release is planned. A push
writes outputs/release-notes.md and outputs/deposit-notes.html; a pull request
into main appends the notes its merge would publish to the job summary.
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode

from release_version import (MAIN_BRANCH, Bump, ReleaseLabelError, bump_from_labels, gh_api, latest_release_tag,
                             pull_labels, release_pulls)

RELEASE_NOTES_PATH = Path("outputs/release-notes.md")
DEPOSIT_NOTES_PATH = Path("outputs/deposit-notes.html")
PAGE_SIZE = 100
NESTED_LIST_INDENT = "  "
CONVENTIONAL_PREFIX = re.compile(r"[a-z]+(?:\([^)]*\))*!?: ")


@dataclass(frozen=True)
class Change:
    pull: dict
    stacked: tuple[Change, ...] = ()


def _merge_order(pull: dict) -> tuple[bool, str]:
    return pull.get("merged_at") is None, pull.get("merged_at") or ""


def _pulls_into(repository: str, branch: str) -> list[dict]:
    pulls, page = [], 1
    while True:
        query = urlencode({"state": "closed", "base": branch, "per_page": PAGE_SIZE, "page": page})
        batch = gh_api(f"repos/{repository}/pulls?{query}")
        pulls.extend(batch)
        if len(batch) < PAGE_SIZE:
            return pulls
        page += 1


def _contains(repository: str, head_sha: str, commit: str) -> bool:
    comparison = gh_api(f"repos/{repository}/compare/{commit}...{head_sha}?per_page=1")
    return comparison["behind_by"] == 0


def _stacked(repository: str, pull: dict, seen: set[int]) -> tuple[Change, ...]:
    head = pull["head"]
    if (head.get("repo") or {}).get("full_name") != repository:
        return ()
    stacked = []
    for candidate in sorted(_pulls_into(repository, head["ref"]), key=_merge_order):
        merged_into_this_pull = (candidate.get("merged_at") and candidate["number"] not in seen
                                 and _contains(repository, head["sha"], candidate["merge_commit_sha"]))
        if merged_into_this_pull:
            seen.add(candidate["number"])
            stacked.append(Change(candidate, _stacked(repository, candidate, seen)))
    return tuple(stacked)


def release_changes(repository: str, pulls: Iterable[dict]) -> tuple[Change, ...]:
    """The release's pull requests in merge order, each with the pull requests stacked into it.

    A pull request merged into another's head branch counts only when its merge
    commit is in the history that pull request merged, which excludes ones merged
    after it and ones into an earlier branch of the same name."""
    ordered = sorted(pulls, key=_merge_order)
    seen = {pull["number"] for pull in ordered}
    return tuple(Change(pull, _stacked(repository, pull, seen)) for pull in ordered)


def _github_lines(changes: Iterable[Change], depth: int = 0) -> Iterator[str]:
    for change in changes:
        pull = change.pull
        yield f"{NESTED_LIST_INDENT * depth}* {pull['title']} by @{pull['user']['login']} in {pull['html_url']}"
        yield from _github_lines(change.stacked, depth + 1)


def github_notes(repository: str, changes: Iterable[Change], previous_tag: str, tag: str) -> str:
    return "\n".join([
        "## What's Changed", *_github_lines(changes), "",
        f"**Full Changelog**: https://github.com/{repository}/compare/{previous_tag}...{tag}", "",
    ])


def _all(changes: Iterable[Change]) -> Iterator[dict]:
    for change in changes:
        yield change.pull
        yield from _all(change.stacked)


def _changes_paper(pull: dict) -> bool:
    try:
        return bump_from_labels(pull_labels(pull)) is not Bump.NONE
    except ReleaseLabelError as exc:
        raise ReleaseLabelError(f"pull request #{pull['number']}: {exc}; label it and re-run") from exc


def _plain_title(title: str) -> str:
    prefix = CONVENTIONAL_PREFIX.match(title)
    plain = title[prefix.end():] if prefix else title
    return plain[:1].upper() + plain[1:]


def deposit_notes(changes: Iterable[Change], previous_tag: str) -> str:
    items = [f'<li>{html.escape(_plain_title(pull["title"]))} '
             f'(<a href="{html.escape(pull["html_url"])}">#{pull["number"]}</a>)</li>'
             for pull in _all(changes) if _changes_paper(pull)]
    return "\n".join([f"<p>Changes since {previous_tag}:</p>", "<ul>", *items, "</ul>", ""])


def write_notes() -> None:
    repository = os.environ["GITHUB_REPOSITORY"]
    tag = os.environ["RELEASE_TAG"]
    previous_tag = latest_release_tag()
    event_name = os.environ["GITHUB_EVENT_NAME"]
    if event_name == "push":
        changes = release_changes(repository, release_pulls(repository, previous_tag).values())
        RELEASE_NOTES_PATH.parent.mkdir(parents=True, exist_ok=True)
        RELEASE_NOTES_PATH.write_text(github_notes(repository, changes, previous_tag, tag), encoding="utf-8")
        DEPOSIT_NOTES_PATH.write_text(deposit_notes(changes, previous_tag), encoding="utf-8")
        print(f"[release] wrote {RELEASE_NOTES_PATH} and {DEPOSIT_NOTES_PATH} for {tag}")
    elif event_name == "pull_request":
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
        pull = event["pull_request"]
        if pull["base"]["ref"] != MAIN_BRANCH:
            print(f"[release] no notes preview: #{pull['number']} merges into {pull['base']['ref']}, not {MAIN_BRANCH}")
            return
        main_tip = "HEAD^1"
        changes = release_changes(repository, [*release_pulls(repository, previous_tag, main_tip).values(), pull])
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as summary:
            summary.write(f"### Release notes this merge would publish as {tag}\n\n"
                          f"{github_notes(repository, changes, previous_tag, tag)}\n"
                          f"### Zenodo notes\n\n```html\n{deposit_notes(changes, previous_tag)}```\n")
    else:
        raise ValueError(f"unsupported event: {event_name}")


def main() -> None:
    try:
        write_notes()
    except (ReleaseLabelError, ValueError) as exc:
        sys.exit(f"::error::{exc}")


if __name__ == "__main__":
    main()
