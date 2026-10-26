#!/usr/bin/env python3
"""Plan the next manuscript release from pull-request release labels.

Every pull request carries exactly one of release:major, release:minor,
release:patch or release:none; README.md ("Release procedure") defines when
each applies. A push to main releases the highest bump among the pull requests merged since
the latest vMAJOR.MINOR.PATCH tag; a pull request plans the tag it would
receive if merged next. Runs from .github/workflows/release.yml and writes
`tag` (empty when nothing is released) and `tagged` (HEAD already carries
that tag, so only the Zenodo deposit remains) to GITHUB_OUTPUT.
"""

from __future__ import annotations

import enum
import json
import os
import re
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path

TAG_PATTERN = re.compile(r"v(\d+)\.(\d+)\.(\d+)")
LABEL_PREFIX = "release:"
MAIN_BRANCH = "main"


class Bump(enum.IntEnum):
    NONE = 0
    PATCH = 1
    MINOR = 2
    MAJOR = 3


class ReleaseLabelError(ValueError):
    pass


def bump_from_labels(labels: Iterable[str]) -> Bump:
    release_labels = [label for label in labels if label.startswith(LABEL_PREFIX)]
    if len(release_labels) != 1:
        raise ReleaseLabelError(
            f"expected exactly one of {', '.join(LABEL_PREFIX + b.name.lower() for b in Bump)}; "
            f"found {release_labels or 'none'}")
    name = release_labels[0].removeprefix(LABEL_PREFIX).upper()
    if name not in Bump.__members__:
        raise ReleaseLabelError(f"unknown release label: {release_labels[0]}")
    return Bump[name]


def bump_for_pulls(label_sets: Iterable[Iterable[str]]) -> Bump:
    return max((bump_from_labels(labels) for labels in label_sets), default=Bump.NONE)


def _version(tag: str) -> tuple[int, int, int]:
    match = TAG_PATTERN.fullmatch(tag)
    if match is None:
        raise ValueError(f"release tag must have the form vMAJOR.MINOR.PATCH: {tag}")
    major, minor, patch = map(int, match.groups())
    return major, minor, patch


def latest_tag(tags: Iterable[str]) -> str:
    releases = [tag for tag in tags if TAG_PATTERN.fullmatch(tag)]
    if not releases:
        raise ValueError("no vMAJOR.MINOR.PATCH tag to release from")
    return max(releases, key=_version)


def next_tag(tag: str, bump: Bump) -> str:
    major, minor, patch = _version(tag)
    if bump is Bump.MAJOR:
        return f"v{major + 1}.0.0"
    if bump is Bump.MINOR:
        return f"v{major}.{minor + 1}.0"
    if bump is Bump.PATCH:
        return f"v{major}.{minor}.{patch + 1}"
    raise ValueError("Bump.NONE produces no release tag")


def _git(*args: str) -> list[str]:
    return subprocess.check_output(["git", *args], text=True).split()


def gh_api(path: str):
    return json.loads(subprocess.check_output(["gh", "api", path], text=True))


def latest_release_tag() -> str:
    return latest_tag(_git("tag", "--list", "v*"))


def pull_labels(pull: dict) -> list[str]:
    return [label["name"] for label in pull["labels"]]


def _merged_pull(repository: str, commit: str) -> dict | None:
    pulls = gh_api(f"repos/{repository}/commits/{commit}/pulls")
    merged = [pull for pull in pulls if pull.get("merged_at") and pull["base"]["ref"] == MAIN_BRANCH]
    return merged[0] if merged else None


def release_pulls(repository: str, since: str, until: str = "HEAD") -> dict[int, dict]:
    """The pull requests that merged the commits on main in since..until, keyed by number."""
    pulls = {}
    for commit in _git("rev-list", f"{since}..{until}"):
        pull = _merged_pull(repository, commit)
        if pull is None:
            print(f"::warning::{commit} reached {MAIN_BRANCH} without a pull request; "
                  "it does not affect the version or the release notes")
            continue
        pulls[pull["number"]] = pull
    return pulls


def _push_bump(repository: str, since: str) -> Bump:
    pulls = release_pulls(repository, since)
    for number, pull in pulls.items():
        try:
            bump_from_labels(pull_labels(pull))
        except ReleaseLabelError as exc:
            raise ReleaseLabelError(f"pull request #{number}: {exc}; label it and re-run") from exc
    return bump_for_pulls(pull_labels(pull) for pull in pulls.values())


def plan() -> dict[str, str]:
    event_name = os.environ["GITHUB_EVENT_NAME"]
    current = latest_release_tag()
    if event_name == "pull_request":
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
        bump = bump_from_labels(label["name"] for label in event["pull_request"]["labels"])
    elif event_name == "push":
        head_tags = [tag for tag in _git("tag", "--points-at", "HEAD", "--list", "v*") if TAG_PATTERN.fullmatch(tag)]
        if head_tags:
            return {"tag": latest_tag(head_tags), "tagged": "true"}
        bump = _push_bump(os.environ["GITHUB_REPOSITORY"], current)
    else:
        raise ValueError(f"unsupported event: {event_name}")
    tag = next_tag(current, bump) if bump is not Bump.NONE else ""
    return {"tag": tag, "tagged": "false"}


def main() -> None:
    try:
        outputs = plan()
    except (ReleaseLabelError, ValueError) as exc:
        sys.exit(f"::error::{exc}")
    summary = f"release plan: {outputs['tag'] or 'no release'}"
    print(summary)
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.writelines(f"{key}={value}\n" for key, value in outputs.items())


if __name__ == "__main__":
    main()
