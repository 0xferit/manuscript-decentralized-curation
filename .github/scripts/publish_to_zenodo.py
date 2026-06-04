#!/usr/bin/env python3
"""Publish outputs/paper.pdf as a new version of the Zenodo concept record.

Runs from .github/workflows/publish-zenodo.yml on release.published. Replaces
Zenodo's default GitHub-integration deposit (which the webhook must be turned
off for) with a clean PDF-only deposit under the existing concept DOI.

Reads metadata from .zenodo.json (single source of truth for deposit
metadata) and augments it with the release tag and today's date.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

API = "https://zenodo.org/api"
CONCEPT_RECID = "20543760"
PDF_PATH = Path("outputs/paper.pdf")
META_PATH = Path(".zenodo.json")
HTTP_TIMEOUT = 60


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
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        sys.exit(f"HTTP {exc.code} on {method} {url}: {exc.read().decode('utf-8', errors='replace')}")
    except urllib.error.URLError as exc:
        sys.exit(f"network error on {method} {url}: {exc.reason}")
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        sys.exit(f"non-JSON response from {method} {url}: {raw[:200]!r}")


def main() -> None:
    token = _require_env("ZENODO_TOKEN")
    tag = _require_env("RELEASE_TAG")
    version = tag.removeprefix("v")

    if not PDF_PATH.exists():
        sys.exit(f"PDF missing at {PDF_PATH}; render must run before publish step")
    try:
        base_meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"missing required metadata file: {META_PATH}")
    except json.JSONDecodeError as exc:
        sys.exit(f"invalid JSON in {META_PATH}: {exc.msg} at line {exc.lineno} col {exc.colno}")

    search = _req(
        "GET",
        f"{API}/records?q=conceptrecid:{CONCEPT_RECID}&sort=mostrecent&size=1&all_versions=true",
        token=token,
    )
    hits = search.get("hits", {}).get("hits") or []
    if not hits:
        sys.exit(f"No record found for conceptrecid={CONCEPT_RECID}")
    latest_id = hits[0]["id"]
    print(f"[zenodo] latest published version: id={latest_id} version={hits[0]['metadata'].get('version')}")

    newversion = _req(
        "POST",
        f"{API}/deposit/depositions/{latest_id}/actions/newversion",
        token=token,
    )
    draft_url = newversion["links"]["latest_draft"]
    draft = _req("GET", draft_url, token=token)
    draft_id = draft["id"]
    bucket = draft["links"]["bucket"]
    print(f"[zenodo] new draft: id={draft_id}")

    for existing in draft.get("files") or []:
        _req("DELETE", existing["links"]["self"], token=token)
        print(f"[zenodo] removed carryover file: {existing.get('filename')}")

    pdf_bytes = PDF_PATH.read_bytes()
    _req(
        "PUT",
        f"{bucket}/paper.pdf",
        token=token,
        body=pdf_bytes,
        content_type="application/octet-stream",
    )
    print(f"[zenodo] uploaded paper.pdf ({len(pdf_bytes)} bytes)")

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
        "publication_date": date.today().isoformat(),
    }
    _req("PUT", f"{API}/deposit/depositions/{draft_id}", token=token, body={"metadata": metadata})
    print(f"[zenodo] metadata set: version={version} date={metadata['publication_date']}")

    published = _req("POST", f"{API}/deposit/depositions/{draft_id}/actions/publish", token=token)
    doi = published.get("doi") or published.get("metadata", {}).get("doi")
    html = published.get("links", {}).get("html")
    conceptdoi = published.get("conceptdoi") or published.get("metadata", {}).get("conceptdoi")
    print(f"[zenodo] published: doi={doi} concept_doi={conceptdoi} url={html}")


if __name__ == "__main__":
    main()
