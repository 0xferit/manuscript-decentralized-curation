from __future__ import annotations

import contextlib
import hashlib
import http.client
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / '.github/scripts'
sys.path.insert(0, str(SCRIPTS))
SCRIPT = SCRIPTS / 'publish_to_zenodo.py'
SPEC = importlib.util.spec_from_file_location('zenodo_release', SCRIPT)
publisher = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = publisher
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
        self.commit = self.commit_index()
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
        self.sleeps = []
        self.enterContext(patch('time.sleep', side_effect=self.sleeps.append))
        self.enterContext(contextlib.redirect_stdout(io.StringIO()))

    def commit_index(self, *parents):
        tree = subprocess.check_output(['git', 'write-tree'], text=True).strip()
        parent_args = [arg for parent in parents for arg in ('-p', parent)]
        commit = subprocess.check_output(
            ['git', '-c', 'user.name=Release Test', '-c', 'user.email=test@example.org',
             'commit-tree', tree, *parent_args], input='test fixture\n', text=True,
        ).strip()
        subprocess.run(['git', 'update-ref', 'HEAD', commit], check=True)
        return commit

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
            'id': 42, 'conceptrecid': publisher.PARENT_CONCEPT_RECID,
            'metadata': {'version': version, 'title': 'Reviewed title',
                                 'description': 'Reviewed description',
                                 'creators': [{'name': 'Author'}], 'keywords': ['curation']},
            'files': files if files is not None else [],
        }]}}

    def publication_queue(self, checksum=None, deletion=({},), draft_files=('paper.pdf',)):
        return [
            self.latest(), [],
            {'links': {'latest_draft': publisher.API + '/deposit/depositions/43'}},
            {'id': 43, 'conceptrecid': publisher.PARENT_CONCEPT_RECID, 'submitted': False,
             'links': {'bucket': publisher.API + '/files/bucket'},
             'files': [{'filename': 'old.pdf', 'links': {'self': publisher.API + '/old-file'}}]},
            *deletion,
            {'checksum': checksum or 'md5:' + hashlib.md5(self.pdf).hexdigest(), 'size': len(self.pdf)},
            {'files': [{'filename': name} for name in draft_files]},
            {}, {'doi': '10.5281/zenodo.43', 'links': {'html': 'https://zenodo.org/records/43'},
                 'submitted': True, 'conceptrecid': publisher.PARENT_CONCEPT_RECID,
                 'metadata': {'version': '1.1.0'}},
        ]

    def test_verified_asset_requires_no_network_or_token(self):
        os.environ.pop('ZENODO_TOKEN')
        publisher.main(verify_only=True)
        self.assertEqual(self.requests, [])

    def test_written_manifest_passes_verification(self):
        Path('outputs/manifest.json').unlink()
        publisher.write_manifest()
        publisher.main(verify_only=True)
        self.assertEqual(json.loads(Path('outputs/manifest.json').read_text()), self.manifest)

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

    def test_release_notes_asset_becomes_the_deposit_notes(self):
        Path('outputs/deposit-notes.html').write_text('<ul><li>Changed rule</li></ul>\n')
        self.queue = self.publication_queue()
        publisher.main()
        metadata = json.loads(self.requests[-2].data)['metadata']
        self.assertEqual(metadata['notes'], '<ul><li>Changed rule</li></ul>\n')

    def test_notes_do_not_decide_whether_a_published_version_matches(self):
        Path('outputs/deposit-notes.html').write_text('<ul><li>Changed rule</li></ul>\n')
        files = [{'key': 'paper.pdf', 'checksum': 'md5:' + hashlib.md5(self.pdf).hexdigest()}]
        self.queue = [self.latest('1.1.0', files)]
        publisher.main()
        self.assertEqual(len(self.requests), 1)

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
        self.queue = [self.latest(), [{'id': 99, 'conceptrecid': publisher.PARENT_CONCEPT_RECID,
                                      'submitted': False}]]
        with self.assertRaises(SystemExit):
            publisher.main()
        self.assertTrue(all(r.method == 'GET' for r in self.requests))

    def test_checks_later_deposition_pages_before_creating_draft(self):
        self.queue = [self.latest(),
                      [{'id': 42, 'conceptrecid': publisher.PARENT_CONCEPT_RECID, 'submitted': True}],
                      [{'id': 99, 'conceptrecid': publisher.PARENT_CONCEPT_RECID, 'submitted': False}]]
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

    def server_error(self, code=500):
        return urllib.error.HTTPError(publisher.API, code, 'Server Error', {}, io.BytesIO(b'busy'))

    def test_transient_error_on_a_repeatable_request_is_retried(self):
        self.queue = [self.server_error(503), *self.publication_queue()]
        publisher.main()
        self.assertEqual([r.method for r in self.requests[:2]], ['GET', 'GET'])
        self.assertEqual(len(self.sleeps), 1)
        self.assertTrue(self.requests[-1].full_url.endswith('/actions/publish'))

    def not_found(self):
        return urllib.error.HTTPError(publisher.API, 404, 'Not Found', {}, io.BytesIO(b''))

    def test_carryover_file_gone_on_retry_counts_as_removed(self):
        self.queue = self.publication_queue(deletion=(self.server_error(), self.not_found()))
        publisher.main()
        self.assertEqual([r.method for r in self.requests].count('DELETE'), 2)
        self.assertTrue(self.requests[-1].full_url.endswith('/actions/publish'))

    def test_missing_file_on_first_delete_is_not_assumed_removed(self):
        self.queue = self.publication_queue(deletion=(self.not_found(),))
        with self.assertRaisesRegex(SystemExit, 'HTTP 404'):
            publisher.main()

    def test_dropped_connection_on_a_repeatable_request_is_retried(self):
        for dropped in (ConnectionResetError('reset by peer'), http.client.IncompleteRead(b'')):
            with self.subTest(dropped=type(dropped).__name__):
                self.requests.clear()
                self.queue = [dropped, *self.publication_queue()]
                publisher.main()
                self.assertTrue(self.requests[-1].full_url.endswith('/actions/publish'))

    def test_draft_holding_another_file_is_never_published(self):
        self.queue = self.publication_queue(draft_files=('old.pdf', 'paper.pdf'))
        with self.assertRaisesRegex(SystemExit, 'old.pdf'):
            publisher.main()
        self.assertFalse(any(r.full_url.endswith('/actions/publish') for r in self.requests))

    def test_publish_request_is_never_retried(self):
        queue = self.publication_queue()
        queue[-1] = self.server_error()
        self.queue = queue
        with self.assertRaisesRegex(SystemExit, 'HTTP 500'):
            publisher.main()
        self.assertEqual(sum(r.full_url.endswith('/actions/publish') for r in self.requests), 1)
        self.assertEqual(self.sleeps, [])

    def test_persistent_server_error_gives_up_after_bounded_retries(self):
        self.queue = [self.server_error() for _ in range(len(publisher.RETRY_DELAYS_SECONDS) + 1)]
        with self.assertRaisesRegex(SystemExit, 'HTTP 500'):
            publisher.main()
        self.assertEqual(len(self.requests), len(publisher.RETRY_DELAYS_SECONDS) + 1)
        self.assertEqual(self.sleeps, list(publisher.RETRY_DELAYS_SECONDS))

    COMPANION_TAG = 'public-goods-v0.3.0'

    def companion_release(self, *, recorded_pdf=None, metadata_version='0.3.0'):
        sources = Path('projects/rpgf/companion-paper')
        sources.mkdir(parents=True, exist_ok=True)
        self.companion_metadata = {
            'upload_type': 'publication', 'publication_type': 'preprint', 'title': 'Companion title',
            'creators': [{'name': 'Author', 'orcid': '0009-0004-1449-9348'}],
            'description': 'Companion description', 'access_right': 'open', 'license': 'CC-BY-4.0',
            'keywords': ['public goods'], 'version': metadata_version, 'publication_date': '2026-11-20',
            'related_identifiers': [{'relation': 'cites', 'identifier': '10.5281/zenodo.23636842',
                                     'scheme': 'doi'}],
        }
        (sources / 'zenodo-metadata.json').write_text(json.dumps(self.companion_metadata))
        recorded = hashlib.sha256(recorded_pdf or self.pdf).hexdigest()
        (sources / 'verification-results.json').write_text(
            json.dumps({'release_0_3_0': {'checks': {'pdf_sha256': recorded}}}))
        self.companion_pdf = Path('outputs/decentralized-curation-public-goods-v0.3.0.pdf')
        self.companion_pdf.write_bytes(self.pdf)
        subprocess.run(['git', 'add', str(sources)], check=True)
        commit = self.commit_index('HEAD')
        subprocess.run(['git', 'update-ref', f'refs/tags/{self.COMPANION_TAG}', commit], check=True)
        os.environ['RELEASE_TAG'] = self.COMPANION_TAG

    def companion_draft(self):
        return {
            'id': 77, 'conceptrecid': publisher.COMPANION_CONCEPT_RECID, 'submitted': False,
            'files': [{'filename': self.companion_pdf.name, 'checksum': hashlib.md5(self.pdf).hexdigest()}],
            'metadata': {'title': 'Companion title', 'version': '0.3.0', 'publication_date': '2026-11-20',
                         'prereserve_doi': {'doi': '10.5281/zenodo.77'}},
            'links': {'html': 'https://zenodo.org/deposit/77'},
        }

    def companion_draft_queue(self):
        return [
            {'hits': {'hits': [{'id': 70, 'conceptrecid': publisher.COMPANION_CONCEPT_RECID,
                                'metadata': {'version': '0.2.0'}, 'files': []}]}},
            [],
            {'links': {'latest_draft': publisher.API + '/deposit/depositions/77'}},
            {'id': 77, 'conceptrecid': publisher.COMPANION_CONCEPT_RECID, 'submitted': False,
             'links': {'bucket': publisher.API + '/files/companion-bucket'},
             'files': [{'filename': 'decentralized-curation-public-goods-v0.2.0.pdf',
                        'links': {'self': publisher.API + '/old-file'}}]},
            {},
            {'checksum': 'md5:' + hashlib.md5(self.pdf).hexdigest(), 'size': len(self.pdf)},
            {'files': [{'filename': self.companion_pdf.name}]},
            {},
            self.companion_draft(),
        ]

    def test_companion_draft_carries_its_tagged_metadata_and_never_the_parent_record(self):
        self.companion_release()
        self.queue = self.companion_draft_queue()
        publisher.main(publisher.Paper.COMPANION, draft_only=True)
        self.assertEqual(self.queue, [])
        self.assertIn(f'conceptrecid:{publisher.COMPANION_CONCEPT_RECID}', self.requests[0].full_url)
        self.assertFalse(any(publisher.PARENT_CONCEPT_RECID in r.full_url for r in self.requests))
        upload = next(r for r in self.requests if r.full_url.endswith('/' + self.companion_pdf.name))
        self.assertEqual(upload.data, self.pdf)
        metadata_update = next(r for r in self.requests
                               if r.method == 'PUT' and r.full_url.endswith('/deposit/depositions/77'))
        self.assertEqual(json.loads(metadata_update.data)['metadata'], self.companion_metadata)
        self.assertFalse(any(r.full_url.endswith('/actions/publish') for r in self.requests))

    def test_companion_release_unlike_its_tagged_record_fails_before_network(self):
        cases = {
            'records': {'recorded_pdf': b'%PDF-1.7\nanother render\n%%EOF\n'},
            'describes version 0.2.0': {'metadata_version': '0.2.0'},
        }
        for reason, fixture in cases.items():
            with self.subTest(reason):
                self.companion_release(**fixture)
                with self.assertRaisesRegex(SystemExit, reason):
                    publisher.main(publisher.Paper.COMPANION, draft_only=True)
        with self.subTest('checkout past the tag'):
            self.companion_release()
            self.commit_index('HEAD')
            with self.assertRaisesRegex(SystemExit, f'not at {self.COMPANION_TAG}'):
                publisher.main(publisher.Paper.COMPANION, draft_only=True)
        self.assertEqual(self.requests, [])

    def test_publish_draft_refuses_a_draft_unlike_the_release(self):
        self.companion_release()
        draft = self.companion_draft()
        variants = {
            'another file': {'files': [*draft['files'], {'filename': 'old.pdf', 'checksum': '0' * 32}]},
            'other bytes': {'files': [{'filename': self.companion_pdf.name, 'checksum': 'f' * 32}]},
            'other version': {'metadata': draft['metadata'] | {'version': '0.2.0'}},
            'other title': {'metadata': draft['metadata'] | {'title': 'Previous title'}},
            'other concept': {'conceptrecid': publisher.PARENT_CONCEPT_RECID},
            'already published': {'submitted': True},
        }
        for name, change in variants.items():
            with self.subTest(name):
                self.queue = [draft | change]
                with self.assertRaisesRegex(SystemExit, 'differs from the reviewed release'):
                    publisher.main(publisher.Paper.COMPANION, publish_draft=77)
        self.assertTrue(all(r.method == 'GET' for r in self.requests))

    def test_publish_draft_publishes_the_confirmed_draft(self):
        self.companion_release()
        self.queue = [self.companion_draft(),
                      {'submitted': True, 'conceptrecid': publisher.COMPANION_CONCEPT_RECID,
                       'doi': '10.5281/zenodo.77', 'metadata': {'version': '0.3.0'},
                       'links': {'html': 'https://zenodo.org/records/77'}}]
        publisher.main(publisher.Paper.COMPANION, publish_draft=77)
        self.assertEqual([(r.method, r.full_url) for r in self.requests], [
            ('GET', publisher.API + '/deposit/depositions/77'),
            ('POST', publisher.API + '/deposit/depositions/77/actions/publish'),
        ])

    def test_command_line_verifies_a_companion_release(self):
        self.companion_release()
        result = subprocess.run([sys.executable, str(SCRIPT), '--paper', 'companion', '--verify-only'],
                                capture_output=True, text=True, env=os.environ | {'ZENODO_TOKEN': ''})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f'verified {self.COMPANION_TAG}', result.stdout)


if __name__ == '__main__':
    unittest.main()
