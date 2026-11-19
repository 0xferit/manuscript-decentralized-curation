#!/usr/bin/env python3
"""Publish a verified release PDF as a new version of its paper's Zenodo concept record.

The parent paper deposits from .github/workflows/publish-zenodo.yml, either on
release.published or called by .github/workflows/release.yml after a merge to
main. Replaces Zenodo's default GitHub-integration deposit (which the webhook
must be turned off for) with a clean PDF-only deposit under the existing
concept DOI. Its metadata comes from .zenodo.json, and the release manifest
binds its PDF to the checked-out commit. When the release carries
deposit-notes.html, written by release_notes.py, its contents become the
version's notes.

The public-goods companion (--paper companion) deposits under its own concept
record. The checkout must be at its public-goods-vMAJOR.MINOR.PATCH tag:
projects/rpgf/companion-paper/zenodo-metadata.json there is the deposit
metadata, and the PDF must match the SHA-256 that the tagged verification
record holds for the version.

Every release check runs before any network request. Use --verify-only for
the credential-free check, --write-manifest to bind a freshly rendered parent
PDF to the checked-out commit, --draft-only to stop at an unpublished draft and
print it for review, and --publish-draft ID to publish that draft once the
review confirms it.
"""

from __future__ import annotations

import argparse
import enum
import hashlib
import http.client
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from http import HTTPStatus
from pathlib import Path

from release_notes import DEPOSIT_NOTES_PATH
from release_version import TAG_PATTERN

API = "https://zenodo.org/api"
PARENT_CONCEPT_RECID = "20543760"
COMPANION_CONCEPT_RECID = "23354211"
PARENT_PDF_PATH = Path("outputs/paper.pdf")
PARENT_META_PATH = Path(".zenodo.json")
MANIFEST_PATH = Path("outputs/manifest.json")
COMPANION_TAG_PATTERN = re.compile(r"public-goods-v(\d+\.\d+\.\d+)")
COMPANION_PDF_PATH = "outputs/decentralized-curation-public-goods-v{version}.pdf"
COMPANION_SOURCES = Path("projects/rpgf/companion-paper")
COMPANION_META_PATH = COMPANION_SOURCES / "zenodo-metadata.json"
COMPANION_VERIFICATION_PATH = COMPANION_SOURCES / "verification-results.json"
HTTP_TIMEOUT = 60
DEPOSITION_PAGE_SIZE = 100
REPEATABLE_METHODS = frozenset({"GET", "PUT", "DELETE"})
TRANSIENT_HTTP_STATUSES = frozenset({
    HTTPStatus.TOO_MANY_REQUESTS, HTTPStatus.INTERNAL_SERVER_ERROR, HTTPStatus.BAD_GATEWAY,
    HTTPStatus.SERVICE_UNAVAILABLE, HTTPStatus.GATEWAY_TIMEOUT,
})
RETRY_DELAYS_SECONDS = (10, 30, 60)


class Paper(enum.Enum):
    PARENT = "parent"
    COMPANION = "companion"


@dataclass(frozen=True)
class Release:
    """A reviewed PDF and its complete deposit metadata, verified against the release tag."""

    concept_recid: str
    version: str
    pdf_path: Path
    pdf_bytes: bytes
    metadata: dict


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        sys.exit(f"missing required environment variable: {name}")
    return value


def _req(method: str, url: str, *, token: str, body=None, content_type: str | None = None):
    headers = {"Authorization": f"Bearer {token}"}
    data: bytes | None = None
    if body is not None:
        if content_type is None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        else:
            data = body
            headers["Content-Type"] = content_type
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    retry_delays = RETRY_DELAYS_SECONDS if method in REPEATABLE_METHODS else ()
    for attempt in range(len(retry_delays) + 1):
        try:
            with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
                return _decode(method, url, response.read())
        except urllib.error.HTTPError as exc:
            with exc:
                detail = exc.read().decode('utf-8', errors='replace')
            removed_by_earlier_attempt = method == "DELETE" and exc.code == HTTPStatus.NOT_FOUND and attempt > 0
            if removed_by_earlier_attempt:
                return {}
            failure = f"HTTP {exc.code} on {method} {url}: {detail}"
            transient = exc.code in TRANSIENT_HTTP_STATUSES
        except (OSError, http.client.HTTPException) as exc:
            failure = f"network error on {method} {url}: {getattr(exc, 'reason', exc)!r}"
            transient = True
        if not transient or attempt == len(retry_delays):
            sys.exit(failure)
        print(f"[zenodo] {failure}; retrying in {retry_delays[attempt]} s")
        time.sleep(retry_delays[attempt])


def _decode(method: str, url: str, raw: bytes):
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        sys.exit(f"non-JSON response from {method} {url}: {raw[:200]!r}")


def _commit_of(revision: str) -> str:
    resolved = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{revision}^{{commit}}"],
                              capture_output=True, text=True)
    if resolved.returncode != 0:
        sys.exit(f"git cannot resolve {revision} to a commit")
    return resolved.stdout.strip()


def _require_pdf(pdf_bytes: bytes) -> None:
    if not pdf_bytes.startswith(b"%PDF-"):
        sys.exit("reviewed asset is not a PDF")


def release_manifest(tag: str, pdf_bytes: bytes) -> dict[str, str]:
    return {
        "release_version": tag,
        "source_commit": _commit_of("HEAD"),
        "manuscript_sha256": hashlib.sha256(Path("paper.qmd").read_bytes()).hexdigest(),
        "reviewed_pdf_sha256": hashlib.sha256(pdf_bytes).hexdigest(),
    }


def write_manifest() -> None:
    tag = _require_env("RELEASE_TAG")
    manifest = release_manifest(tag, PARENT_PDF_PATH.read_bytes())
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"[release] wrote {MANIFEST_PATH} for {tag} at {manifest['source_commit']}")


def verify_parent_release(tag: str) -> Release:
    if not TAG_PATTERN.fullmatch(tag):
        sys.exit("release tag must have the form vMAJOR.MINOR.PATCH")
    version = tag.removeprefix("v")
    try:
        pdf_bytes = PARENT_PDF_PATH.read_bytes()
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        base_meta = json.loads(PARENT_META_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit("missing reviewed PDF, release manifest, or .zenodo.json")
    except json.JSONDecodeError as exc:
        sys.exit(f"invalid release JSON: {exc.msg} at line {exc.lineno} col {exc.colno}")
    notes = DEPOSIT_NOTES_PATH.read_text(encoding="utf-8") if DEPOSIT_NOTES_PATH.exists() else None
    expected = release_manifest(tag, pdf_bytes)
    for key, value in expected.items():
        if manifest.get(key) != value:
            sys.exit(f"release manifest mismatch: {key}")
    _require_pdf(pdf_bytes)
    print(f"[release] verified {tag} at {expected['source_commit']}: sha256={expected['reviewed_pdf_sha256']}")
    metadata = {
        "upload_type": base_meta.get("upload_type", "publication"),
        "publication_type": base_meta.get("publication_type", "preprint"),
        "title": base_meta["title"],
        "creators": base_meta["creators"],
        "description": base_meta["description"],
        "access_right": base_meta.get("access_right", "open"),
        "license": base_meta.get("license", "CC-BY-4.0").lower(),
        "keywords": base_meta.get("keywords", []),
        "version": version,
        "publication_date": datetime.fromisoformat(_require_env("RELEASE_PUBLISHED_AT")).date().isoformat(),
    }
    if notes is not None:
        metadata["notes"] = notes
    return Release(PARENT_CONCEPT_RECID, version, PARENT_PDF_PATH, pdf_bytes, metadata)


def verify_companion_release(tag: str) -> Release:
    tag_match = COMPANION_TAG_PATTERN.fullmatch(tag)
    if not tag_match:
        sys.exit("companion release tag must have the form public-goods-vMAJOR.MINOR.PATCH")
    version = tag_match.group(1)
    head = _commit_of("HEAD")
    if head != _commit_of(tag):
        sys.exit(f"the checkout is not at {tag}, whose sources describe the deposit")
    pdf_path = Path(COMPANION_PDF_PATH.format(version=version))
    try:
        pdf_bytes = pdf_path.read_bytes()
        metadata = json.loads(COMPANION_META_PATH.read_text(encoding="utf-8"))
        verification = json.loads(COMPANION_VERIFICATION_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        sys.exit(f"missing {exc.filename}")
    except json.JSONDecodeError as exc:
        sys.exit(f"invalid release JSON: {exc.msg} at line {exc.lineno} col {exc.colno}")
    if metadata.get("version") != version:
        sys.exit(f"{COMPANION_META_PATH} describes version {metadata.get('version')}, not {version}")
    release_record = "release_" + version.replace(".", "_")
    recorded_sha256 = verification.get(release_record, {}).get("checks", {}).get("pdf_sha256")
    pdf_sha256 = hashlib.sha256(pdf_bytes).hexdigest()
    if pdf_sha256 != recorded_sha256:
        sys.exit(f"{pdf_path.name} has SHA-256 {pdf_sha256}, but {COMPANION_VERIFICATION_PATH} "
                 f"records {recorded_sha256} for {release_record}")
    _require_pdf(pdf_bytes)
    print(f"[release] verified {tag} at {head}: sha256={pdf_sha256}")
    return Release(COMPANION_CONCEPT_RECID, version, pdf_path, pdf_bytes, metadata)


def _create_draft(release: Release, token: str) -> int | None:
    """Build an unpublished version holding only the reviewed PDF and metadata.

    Returns None when Zenodo already publishes this version with the reviewed PDF and metadata.
    """
    pdf_checksum = "md5:" + hashlib.md5(release.pdf_bytes).hexdigest()
    search = _req(
        "GET",
        f"{API}/records?q=conceptrecid:{release.concept_recid}&sort=mostrecent&size=1&all_versions=true",
        token=token,
    )
    hits = search.get("hits", {}).get("hits") or []
    if not hits:
        sys.exit(f"No record found for conceptrecid={release.concept_recid}")
    latest_id = hits[0]["id"]
    latest = hits[0]
    if str(latest.get("conceptrecid")) != release.concept_recid:
        sys.exit("published record does not belong to the expected concept")
    latest_version = latest["metadata"].get("version", "").removeprefix("v")
    print(f"[zenodo] latest published version: id={latest_id} version={latest_version}")
    if latest_version == release.version:
        files = latest.get("files", [])
        same_file = (len(files) == 1 and files[0].get("key") == release.pdf_path.name
                     and files[0].get("checksum") == pdf_checksum)
        same_metadata = all(latest["metadata"].get(key) == release.metadata[key]
                            for key in ("title", "description", "keywords"))
        same_authors = [author.get("name") for author in latest["metadata"].get("creators", [])] == [
            author["name"] for author in release.metadata["creators"]]
        if not (same_file and same_metadata and same_authors):
            sys.exit("version already published with different content; inspect Zenodo before proceeding")
        print(f"[zenodo] already published and matches reviewed release: id={latest_id}")
        return None
    if not re.fullmatch(r"\d+\.\d+\.\d+", latest_version) or tuple(map(int, latest_version.split("."))) >= tuple(map(int, release.version.split("."))):
        sys.exit("requested version must be newer than the latest published version")

    page = 1
    while True:
        depositions = _req(
            "GET", f"{API}/deposit/depositions?q=conceptrecid:{release.concept_recid}"
            f"&all_versions=true&allversions=true&size={DEPOSITION_PAGE_SIZE}&page={page}",
            token=token,
        )
        if not isinstance(depositions, list):
            sys.exit("unexpected deposition search response; inspect Zenodo before retrying")
        if not depositions:
            break
        for deposition in depositions:
            if str(deposition.get("conceptrecid")) != release.concept_recid or deposition.get("submitted") is not True:
                sys.exit("an unpublished Zenodo draft may already exist; inspect it before retrying")
        page += 1

    newversion = _req(
        "POST",
        f"{API}/deposit/depositions/{latest_id}/actions/newversion",
        token=token,
    )
    draft_url = newversion["links"]["latest_draft"]
    draft = _req("GET", draft_url, token=token)
    if str(draft.get("conceptrecid")) != release.concept_recid or draft.get("submitted") is not False:
        sys.exit("new draft does not belong to the expected unpublished concept")
    draft_id = draft["id"]
    bucket = draft["links"]["bucket"]
    print(f"[zenodo] new draft: id={draft_id}")

    for existing in draft.get("files") or []:
        _req("DELETE", existing["links"]["self"], token=token)
        print(f"[zenodo] removed carryover file: {existing.get('filename')}")

    uploaded = _req(
        "PUT",
        f"{bucket}/{release.pdf_path.name}",
        token=token,
        body=release.pdf_bytes,
        content_type="application/octet-stream",
    )
    if uploaded.get("checksum") != pdf_checksum or uploaded.get("size") != len(release.pdf_bytes):
        sys.exit("uploaded PDF checksum or size mismatch; draft left unpublished for inspection")
    print(f"[zenodo] uploaded {release.pdf_path.name} ({len(release.pdf_bytes)} bytes)")
    draft_files = [entry.get("filename") for entry in _req("GET", draft_url, token=token).get("files") or []]
    if draft_files != [release.pdf_path.name]:
        sys.exit(f"draft holds {draft_files}, not only {release.pdf_path.name}; draft left unpublished for inspection")

    _req("PUT", f"{API}/deposit/depositions/{draft_id}", token=token, body={"metadata": release.metadata})
    print(f"[zenodo] metadata set: version={release.version} date={release.metadata['publication_date']}")
    return draft_id


def _confirm_draft(release: Release, draft: dict) -> None:
    """Exit unless the draft is an unpublished version of the release's concept holding only its reviewed PDF."""
    draft_metadata = draft.get("metadata", {})
    observed = {
        "concept record": str(draft.get("conceptrecid")),
        "publication state": draft.get("submitted"),
        "files": [(entry.get("filename"), entry.get("checksum")) for entry in draft.get("files") or []],
        "version": draft_metadata.get("version"),
        "title": draft_metadata.get("title"),
    }
    expected = {
        "concept record": release.concept_recid,
        "publication state": False,
        "files": [(release.pdf_path.name, hashlib.md5(release.pdf_bytes).hexdigest())],
        "version": release.version,
        "title": release.metadata["title"],
    }
    differences = [field for field in expected if observed[field] != expected[field]]
    if differences:
        sys.exit(f"draft {draft.get('id')} differs from the reviewed release in {', '.join(differences)}; "
                 "it stays unpublished for inspection")


def _print_draft(draft: dict) -> None:
    draft_metadata = draft.get("metadata", {})
    print(f"[zenodo] draft ready for review: id={draft['id']} url={draft.get('links', {}).get('html')}")
    print(f"[zenodo]   concept record: {draft.get('conceptrecid')}")
    print(f"[zenodo]   reserved DOI: {draft_metadata.get('prereserve_doi', {}).get('doi')}")
    print(f"[zenodo]   version: {draft_metadata.get('version')}")
    print(f"[zenodo]   publication date: {draft_metadata.get('publication_date')}")
    print(f"[zenodo]   title: {draft_metadata.get('title')}")
    for related in draft_metadata.get("related_identifiers") or []:
        print(f"[zenodo]   {related.get('relation')}: {related.get('identifier')}")
    for entry in draft.get("files") or []:
        print(f"[zenodo]   file: {entry.get('filename')} md5={entry.get('checksum')}")
    print(f"[zenodo] after review, publish it with --publish-draft {draft['id']}")


def _publish(release: Release, draft_id: int, token: str) -> None:
    published = _req("POST", f"{API}/deposit/depositions/{draft_id}/actions/publish", token=token)
    if (published.get("submitted") is not True
            or str(published.get("conceptrecid")) != release.concept_recid
            or published.get("metadata", {}).get("version") != release.version):
        sys.exit(f"publication not confirmed for draft {draft_id}; inspect Zenodo before retrying")
    doi = published.get("doi") or published.get("metadata", {}).get("doi")
    html = published.get("links", {}).get("html")
    conceptdoi = published.get("conceptdoi") or published.get("metadata", {}).get("conceptdoi")
    print(f"[zenodo] published: doi={doi} concept_doi={conceptdoi} url={html}")


def main(paper: Paper = Paper.PARENT, *, verify_only: bool = False, draft_only: bool = False,
         publish_draft: int | None = None) -> None:
    tag = _require_env("RELEASE_TAG")
    release = verify_parent_release(tag) if paper is Paper.PARENT else verify_companion_release(tag)
    if verify_only:
        return

    token = _require_env("ZENODO_TOKEN")
    if publish_draft is not None:
        _confirm_draft(release, _req("GET", f"{API}/deposit/depositions/{publish_draft}", token=token))
        _publish(release, publish_draft, token)
        return
    draft_id = _create_draft(release, token)
    if draft_id is None:
        return
    if draft_only:
        draft = _req("GET", f"{API}/deposit/depositions/{draft_id}", token=token)
        _confirm_draft(release, draft)
        _print_draft(draft)
        return
    _publish(release, draft_id, token)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper", choices=[paper.value for paper in Paper], default=Paper.PARENT.value)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--verify-only", action="store_true")
    mode.add_argument("--write-manifest", action="store_true")
    mode.add_argument("--draft-only", action="store_true")
    mode.add_argument("--publish-draft", type=int, metavar="ID")
    args = parser.parse_args()
    paper = Paper(args.paper)
    if args.write_manifest and paper is not Paper.PARENT:
        parser.error("--write-manifest binds the parent's rendered PDF only")
    if args.write_manifest:
        write_manifest()
    else:
        main(paper, verify_only=args.verify_only, draft_only=args.draft_only, publish_draft=args.publish_draft)
