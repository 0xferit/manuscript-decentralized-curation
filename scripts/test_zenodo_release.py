from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / '.github/scripts/publish_to_zenodo.py'
SPEC = importlib.util.spec_from_file_location('zenodo_release', SCRIPT)
publisher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(publisher)


class Response(io.BytesIO):
    def __init__(self, payload):
        super().__init__(json.dumps(payload).encode())


class ZenodoReleaseTests(unittest.TestCase):
    def setUp(self):
        directory = self.enterContext(tempfile.TemporaryDirectory())
        self.enterContext(contextlib.chdir(directory))
        self.root = Path(directory)
        subprocess.run(['git', 'init', '-q'], check=True)
        Path('paper.qmd').write_text('Reviewed manuscript\n')
        subprocess.run(['git', 'add', 'paper.qmd'], check=True)
        tree = subprocess.check_output(['git', 'write-tree'], text=True).strip()
        self.commit = subprocess.check_output(
            ['git', '-c', 'user.name=Release Test', '-c', 'user.email=test@example.org',
             'commit-tree', tree], input='test fixture\n', text=True,
        ).strip()
        subprocess.run(['git', 'update-ref', 'HEAD', self.commit], check=True)
        Path('outputs').mkdir()
        self.pdf = b'%PDF-1.7\nreviewed bytes\n%%EOF\n'
        Path('outputs/paper.pdf').write_bytes(self.pdf)
        self.manifest = {
            'release_version': 'v1.1.0', 'source_commit': self.commit,
            'manuscript_sha256': hashlib.sha256(Path('paper.qmd').read_bytes()).hexdigest(),
            'reviewed_pdf_sha256': hashlib.sha256(self.pdf).hexdigest(),
        }
        self.write_manifest()
        Path('.zenodo.json').write_text(json.dumps({
            'title': 'Reviewed title', 'creators': [{'name': 'Author'}],
            'description': 'Reviewed description', 'keywords': ['curation'],
        }))
        self.enterContext(patch.dict(os.environ, {
            'RELEASE_TAG': 'v1.1.0', 'ZENODO_TOKEN': 'test-token',
            'RELEASE_PUBLISHED_AT': '2026-10-11T13:00:00Z',
        }))
        self.requests = []
        self.queue = []
        self.enterContext(patch('urllib.request.urlopen', side_effect=self.http))
        self.enterContext(contextlib.redirect_stdout(io.StringIO()))

    def write_manifest(self):
        Path('outputs/manifest.json').write_text(json.dumps(self.manifest))

    def http(self, request, timeout):
        self.requests.append(request)
        if not self.queue:
            self.fail(f'Unexpected HTTP request: {request.method} {request.full_url}')
        payload = self.queue.pop(0)
        if isinstance(payload, Exception):
            raise payload
        return Response(payload)

    def latest(self, version='1.0.4', files=None):
        return {'hits': {'hits': [{
            'id': 42, 'conceptrecid': publisher.CONCEPT_RECID,
            'metadata': {'version': version, 'title': 'Reviewed title',
                                 'description': 'Reviewed description',
                                 'creators': [{'name': 'Author'}], 'keywords': ['curation']},
            'files': files if files is not None else [],
        }]}}

    def publication_queue(self, checksum=None):
        return [
            self.latest(), [],
            {'links': {'latest_draft': publisher.API + '/deposit/depositions/43'}},
            {'id': 43, 'conceptrecid': publisher.CONCEPT_RECID, 'submitted': False,
             'links': {'bucket': publisher.API + '/files/bucket'},
             'files': [{'filename': 'old.pdf', 'links': {'self': publisher.API + '/old-file'}}]},
            {}, {'checksum': checksum or 'md5:' + hashlib.md5(self.pdf).hexdigest(), 'size': len(self.pdf)},
            {}, {'doi': '10.5281/zenodo.43', 'links': {'html': 'https://zenodo.org/records/43'},
                 'submitted': True, 'conceptrecid': publisher.CONCEPT_RECID,
                 'metadata': {'version': '1.1.0'}},
        ]

    def test_verified_asset_requires_no_network_or_token(self):
        os.environ.pop('ZENODO_TOKEN')
        publisher.main(verify_only=True)
        self.assertEqual(self.requests, [])

    def test_rejects_mismatched_artifact_bindings_before_network(self):
        for key in self.manifest:
            with self.subTest(key=key):
                original = self.manifest[key]
                self.manifest[key] = 'incorrect'
                self.write_manifest()
                with self.assertRaises(SystemExit):
                    publisher.main()
                self.manifest[key] = original
        self.assertEqual(self.requests, [])

    def test_missing_pdf_fails_before_network(self):
        Path('outputs/paper.pdf').unlink()
        with self.assertRaises(SystemExit):
            publisher.main()
        self.assertEqual(self.requests, [])

    def test_invalid_manifest_fails_before_network(self):
        Path('outputs/manifest.json').write_text('{')
        with self.assertRaisesRegex(SystemExit, 'invalid release JSON'):
            publisher.main()
        self.assertEqual(self.requests, [])

    def test_uploads_exact_reviewed_bytes_then_publishes(self):
        self.queue = self.publication_queue()
        publisher.main()
        uploads = [r for r in self.requests if r.full_url.endswith('/paper.pdf')]
        self.assertEqual([r.data for r in uploads], [self.pdf])
        self.assertTrue(self.requests[-1].full_url.endswith('/actions/publish'))
        metadata = json.loads(self.requests[-2].data)['metadata']
        self.assertEqual(metadata['description'], 'Reviewed description')
        self.assertEqual(metadata['version'], '1.1.0')
        self.assertEqual(metadata['publication_date'], '2026-10-11')
        self.assertEqual(self.queue, [])

    def test_checksum_failure_never_publishes(self):
        self.queue = self.publication_queue('md5:incorrect')
        with self.assertRaises(SystemExit):
            publisher.main()
        self.assertFalse(any(r.full_url.endswith('/actions/publish') for r in self.requests))

    def test_wrong_draft_concept_is_untouched(self):
        self.queue = self.publication_queue()
        self.queue[3]['conceptrecid'] = 'other'
        with self.assertRaises(SystemExit):
            publisher.main()
        self.assertFalse(any(r.method in ('PUT', 'DELETE') for r in self.requests))

    def test_unconfirmed_publication_does_not_report_success(self):
        self.queue = self.publication_queue()
        self.queue[-1]['submitted'] = False
        with self.assertRaisesRegex(SystemExit, 'publication not confirmed'):
            publisher.main()

    def test_existing_human_draft_is_untouched(self):
        self.queue = [self.latest(), [{'id': 99, 'conceptrecid': publisher.CONCEPT_RECID,
                                      'submitted': False}]]
        with self.assertRaises(SystemExit):
            publisher.main()
        self.assertTrue(all(r.method == 'GET' for r in self.requests))

    def test_checks_later_deposition_pages_before_creating_draft(self):
        self.queue = [self.latest(),
                      [{'id': 42, 'conceptrecid': publisher.CONCEPT_RECID, 'submitted': True}],
                      [{'id': 99, 'conceptrecid': publisher.CONCEPT_RECID, 'submitted': False}]]
        with self.assertRaises(SystemExit):
            publisher.main()
        self.assertEqual(len(self.requests), 3)
        self.assertIn('page=2', self.requests[-1].full_url)
        self.assertTrue(all(r.method == 'GET' for r in self.requests))

    def test_matching_published_version_is_noop(self):
        files = [{'key': 'paper.pdf', 'checksum': 'md5:' + hashlib.md5(self.pdf).hexdigest()}]
        self.queue = [self.latest('1.1.0', files)]
        publisher.main()
        self.assertEqual(len(self.requests), 1)
        self.assertEqual(self.requests[0].method, 'GET')

    def test_conflicting_published_version_is_untouched(self):
        self.queue = [self.latest('1.1.0', [{'key': 'paper.pdf', 'checksum': 'md5:other'}])]
        with self.assertRaises(SystemExit):
            publisher.main()
        self.assertTrue(all(r.method == 'GET' for r in self.requests))

    def test_older_release_never_creates_deposit(self):
        self.queue = [self.latest('1.2.0')]
        with self.assertRaises(SystemExit):
            publisher.main()
        self.assertEqual(len(self.requests), 1)

    def test_no_record_never_creates_deposit(self):
        self.queue = [{'hits': {'hits': []}}]
        with self.assertRaises(SystemExit):
            publisher.main()
        self.assertEqual(len(self.requests), 1)

    def test_wrong_published_concept_never_creates_deposit(self):
        response = self.latest()
        response['hits']['hits'][0]['conceptrecid'] = 'other'
        self.queue = [response]
        with self.assertRaises(SystemExit):
            publisher.main()
        self.assertEqual(len(self.requests), 1)

    def test_authorization_failure_never_creates_deposit(self):
        self.queue = [urllib.error.HTTPError(publisher.API, 401, 'Unauthorized', {}, io.BytesIO(b'denied'))]
        with self.assertRaisesRegex(SystemExit, 'HTTP 401'):
            publisher.main()
        self.assertEqual(len(self.requests), 1)


if __name__ == '__main__':
    unittest.main()
