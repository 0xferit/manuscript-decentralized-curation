#!/usr/bin/env python3
"""Publish the verified GitHub release PDF to the Zenodo concept record.

Runs from .github/workflows/publish-zenodo.yml, either on release.published or
called by .github/workflows/release.yml after a merge to main. Replaces
Zenodo's default GitHub-integration deposit (which the webhook must be turned
off for) with a clean PDF-only deposit under the existing concept DOI.

Reads metadata from .zenodo.json and verifies the release manifest before
any network request. Use --verify-only for the credential-free check and
--write-manifest to bind a freshly rendered PDF to the checked-out commit.
"""

from __future__ import annotations

import argparse
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
from datetime import datetime
from http import HTTPStatus
from pathlib import Path

from release_version import TAG_PATTERN

API = "https://zenodo.org/api"
CONCEPT_RECID = "20543760"
PDF_PATH = Path("outputs/paper.pdf")
META_PATH = Path(".zenodo.json")
MANIFEST_PATH = Path("outputs/manifest.json")
HTTP_TIMEOUT = 60
DEPOSITION_PAGE_SIZE = 100
REPEATABLE_METHODS = frozenset({"GET", "PUT", "DELETE"})
TRANSIENT_HTTP_STATUSES = frozenset({
    HTTPStatus.TOO_MANY_REQUESTS, HTTPStatus.INTERNAL_SERVER_ERROR, HTTPStatus.BAD_GATEWAY,
    HTTPStatus.SERVICE_UNAVAILABLE, HTTPStatus.GATEWAY_TIMEOUT,
})
RETRY_DELAYS_SECONDS = (10, 30, 60)


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


def release_manifest(tag: str, pdf_bytes: bytes) -> dict[str, str]:
    return {
        "release_version": tag,
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "manuscript_sha256": hashlib.sha256(Path("paper.qmd").read_bytes()).hexdigest(),
        "reviewed_pdf_sha256": hashlib.sha256(pdf_bytes).hexdigest(),
    }


def write_manifest() -> None:
    tag = _require_env("RELEASE_TAG")
    manifest = release_manifest(tag, PDF_PATH.read_bytes())
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"[release] wrote {MANIFEST_PATH} for {tag} at {manifest['source_commit']}")


def main(*, verify_only: bool = False) -> None:
    tag = _require_env("RELEASE_TAG")
    if not TAG_PATTERN.fullmatch(tag):
        sys.exit("release tag must have the form vMAJOR.MINOR.PATCH")
    version = tag.removeprefix("v")
    try:
        pdf_bytes = PDF_PATH.read_bytes()
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        base_meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit("missing reviewed PDF, release manifest, or .zenodo.json")
    except json.JSONDecodeError as exc:
        sys.exit(f"invalid release JSON: {exc.msg} at line {exc.lineno} col {exc.colno}")
    expected = release_manifest(tag, pdf_bytes)
    commit = expected["source_commit"]
    for key, value in expected.items():
        if manifest.get(key) != value:
            sys.exit(f"release manifest mismatch: {key}")
    if not pdf_bytes.startswith(b"%PDF-"):
        sys.exit("reviewed asset is not a PDF")
    print(f"[release] verified {tag} at {commit}: sha256={expected['reviewed_pdf_sha256']}")
    if verify_only:
        return

    token = _require_env("ZENODO_TOKEN")
    publication_date = datetime.fromisoformat(_require_env("RELEASE_PUBLISHED_AT")).date().isoformat()
    pdf_checksum = "md5:" + hashlib.md5(pdf_bytes).hexdigest()

    search = _req(
        "GET",
        f"{API}/records?q=conceptrecid:{CONCEPT_RECID}&sort=mostrecent&size=1&all_versions=true",
        token=token,
    )
    hits = search.get("hits", {}).get("hits") or []
    if not hits:
        sys.exit(f"No record found for conceptrecid={CONCEPT_RECID}")
    latest_id = hits[0]["id"]
    latest = hits[0]
    if str(latest.get("conceptrecid")) != CONCEPT_RECID:
        sys.exit("published record does not belong to the expected concept")
    latest_version = latest["metadata"].get("version", "").removeprefix("v")
    print(f"[zenodo] latest published version: id={latest_id} version={latest_version}")
    if latest_version == version:
        files = latest.get("files", [])
        same_file = len(files) == 1 and files[0].get("key") == PDF_PATH.name and files[0].get("checksum") == pdf_checksum
        same_metadata = all(latest["metadata"].get(key) == base_meta[key]
                            for key in ("title", "description", "keywords"))
        same_authors = [author.get("name") for author in latest["metadata"].get("creators", [])] == [
            author["name"] for author in base_meta["creators"]]
        if not (same_file and same_metadata and same_authors):
            sys.exit("version already published with different content; inspect Zenodo before proceeding")
        print(f"[zenodo] already published and matches reviewed release: id={latest_id}")
        return
    if not re.fullmatch(r"\d+\.\d+\.\d+", latest_version) or tuple(map(int, latest_version.split("."))) >= tuple(map(int, version.split("."))):
        sys.exit("requested version must be newer than the latest published version")

    page = 1
    while True:
        depositions = _req(
            "GET", f"{API}/deposit/depositions?q=conceptrecid:{CONCEPT_RECID}"
            f"&all_versions=true&allversions=true&size={DEPOSITION_PAGE_SIZE}&page={page}",
            token=token,
        )
        if not isinstance(depositions, list):
            sys.exit("unexpected deposition search response; inspect Zenodo before retrying")
        if not depositions:
            break
        for deposition in depositions:
            if str(deposition.get("conceptrecid")) != CONCEPT_RECID or deposition.get("submitted") is not True:
                sys.exit("an unpublished Zenodo draft may already exist; inspect it before retrying")
        page += 1

    newversion = _req(
        "POST",
        f"{API}/deposit/depositions/{latest_id}/actions/newversion",
        token=token,
    )
    draft_url = newversion["links"]["latest_draft"]
    draft = _req("GET", draft_url, token=token)
    if str(draft.get("conceptrecid")) != CONCEPT_RECID or draft.get("submitted") is not False:
        sys.exit("new draft does not belong to the expected unpublished concept")
    draft_id = draft["id"]
    bucket = draft["links"]["bucket"]
    print(f"[zenodo] new draft: id={draft_id}")

    for existing in draft.get("files") or []:
        _req("DELETE", existing["links"]["self"], token=token)
        print(f"[zenodo] removed carryover file: {existing.get('filename')}")

    uploaded = _req(
        "PUT",
        f"{bucket}/{PDF_PATH.name}",
        token=token,
        body=pdf_bytes,
        content_type="application/octet-stream",
    )
    if uploaded.get("checksum") != pdf_checksum or uploaded.get("size") != len(pdf_bytes):
        sys.exit("uploaded PDF checksum or size mismatch; draft left unpublished for inspection")
    print(f"[zenodo] uploaded {PDF_PATH.name} ({len(pdf_bytes)} bytes)")
    draft_files = [entry.get("filename") for entry in _req("GET", draft_url, token=token).get("files") or []]
    if draft_files != [PDF_PATH.name]:
        sys.exit(f"draft holds {draft_files}, not only {PDF_PATH.name}; draft left unpublished for inspection")

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
        "publication_date": publication_date,
    }
    _req("PUT", f"{API}/deposit/depositions/{draft_id}", token=token, body={"metadata": metadata})
    print(f"[zenodo] metadata set: version={version} date={metadata['publication_date']}")

    published = _req("POST", f"{API}/deposit/depositions/{draft_id}/actions/publish", token=token)
    if (published.get("submitted") is not True
            or str(published.get("conceptrecid")) != CONCEPT_RECID
            or published.get("metadata", {}).get("version") != version):
        sys.exit(f"publication not confirmed for draft {draft_id}; inspect Zenodo before retrying")
    doi = published.get("doi") or published.get("metadata", {}).get("doi")
    html = published.get("links", {}).get("html")
    conceptdoi = published.get("conceptdoi") or published.get("metadata", {}).get("conceptdoi")
    print(f"[zenodo] published: doi={doi} concept_doi={conceptdoi} url={html}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--verify-only", action="store_true")
    mode.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()
    if args.write_manifest:
        write_manifest()
    else:
        main(verify_only=args.verify_only)
