from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / '.github/scripts/review_fetch_domains.py'
SPEC = importlib.util.spec_from_file_location('review_fetch_domains', SCRIPT)
domains = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(domains)


class ReviewFetchDomainsTests(unittest.TestCase):
    def setUp(self):
        self.directory = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def rules(self, bibliography, allow):
        bibliography_path = self.directory / 'references.bib'
        settings_path = self.directory / 'settings.json'
        bibliography_path.write_text(bibliography, encoding='utf-8')
        settings_path.write_text(json.dumps({'permissions': {'allow': allow}}), encoding='utf-8')
        return domains.fetch_rules(bibliography_path, settings_path)

    def test_cited_hosts_and_configured_domains_are_allowed(self):
        bibliography = (
            '@misc{a, url = {https://blog.ethereum.org/2014/03/28/post}}\n'
            '@misc{b, howpublished = {\\url{HTTP://Medium.com:443/@user/post}}}\n'
            '@misc{c, url = {https://blog.ethereum.org/2015/01/28/other}}\n'
        )
        allow = ['WebFetch(domain:doi.org)', 'Bash(make render)', 'WebFetch(domain:api.crossref.org)']
        self.assertEqual(self.rules(bibliography, allow), [
            'WebFetch(domain:api.crossref.org)',
            'WebFetch(domain:blog.ethereum.org)',
            'WebFetch(domain:doi.org)',
            'WebFetch(domain:medium.com)',
        ])

    def test_only_plain_host_names_become_rules(self):
        bibliography = (
            '@misc{a, note = {mirrored at example.org}}\n'
            '@misc{b, url = {https://evil.example),Bash(curl:*)/x}}\n'
        )
        self.assertEqual(self.rules(bibliography, ['WebFetch(domain:*)']), [])


if __name__ == '__main__':
    unittest.main()
