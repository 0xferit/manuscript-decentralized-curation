"""Print the WebFetch rules for the CI paper review, comma-separated.

The review may fetch from the host of every URL cited in ``references.bib``
and from each domain ``.claude/settings.json`` allows WebFetch to reach, and
from nothing else, so fetched text cannot send data to an arbitrary host. Only
plain host names become rules: the list is spliced into ``--allowedTools``,
and a crafted URL must not be able to add another tool grant to it.

Usage: ``review_fetch_domains.py``, run from the repository root.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BIBLIOGRAPHY = Path('references.bib')
SETTINGS = Path('.claude/settings.json')
URL_HOST = re.compile(r'https?://([^/\s{}:?#]+)', re.IGNORECASE)
WEBFETCH_DOMAIN_RULE = re.compile(r'WebFetch\(domain:(.+)\)')
HOST_NAME = re.compile(r'[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)+')


def fetch_rules(bibliography: Path, settings: Path) -> list[str]:
    cited = URL_HOST.findall(bibliography.read_text(encoding='utf-8'))
    allowed = json.loads(settings.read_text(encoding='utf-8'))['permissions']['allow']
    configured = [match.group(1) for rule in allowed if (match := WEBFETCH_DOMAIN_RULE.fullmatch(rule))]
    hosts = {host.lower() for host in cited + configured}
    return [f'WebFetch(domain:{host})' for host in sorted(hosts) if HOST_NAME.fullmatch(host)]


def main(argv: list[str]) -> int:
    print(','.join(fetch_rules(BIBLIOGRAPHY, SETTINGS)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
