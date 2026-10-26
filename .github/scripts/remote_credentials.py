"""Keep the GitHub token out of the git remote that a Claude review can read.

claude-code-action writes its GitHub token into the ``origin`` URL of the
checkout before Claude starts, where any tool that reads the checkout can see
it. ``strip`` rewrites the remote without credentials; the shared review
settings run it as a session-start hook, before Claude acts. ``check`` fails
the job when the remote still carries credentials after the review, which means
the hook did not run; it never prints the URL.

Usage: ``remote_credentials.py strip|check``, run inside the checkout.
"""
from __future__ import annotations

import argparse
import subprocess
from urllib.parse import urlsplit, urlunsplit

REMOTE = 'origin'


def remote_url() -> str:
    return subprocess.run(
        ['git', 'remote', 'get-url', REMOTE], capture_output=True, text=True, check=True
    ).stdout.strip()


def without_credentials(url: str) -> str:
    parts = urlsplit(url)
    if parts.username is None and parts.password is None:
        return url
    host = parts.netloc.rpartition('@')[2]
    return urlunsplit(parts._replace(netloc=host))


def strip() -> int:
    url = remote_url()
    plain = without_credentials(url)
    if plain != url:
        subprocess.run(['git', 'remote', 'set-url', REMOTE, plain], check=True)
    return 0


def check() -> int:
    url = remote_url()
    if without_credentials(url) != url:
        print(f'::error::The {REMOTE} remote still carried credentials after the review, so Claude could read the job token.')
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('mode', choices=['strip', 'check'])
    return {'strip': strip, 'check': check}[parser.parse_args().mode]()


if __name__ == '__main__':
    raise SystemExit(main())
