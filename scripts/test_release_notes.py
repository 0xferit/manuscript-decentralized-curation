from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.github/scripts'))
notes = importlib.import_module('release_notes')

REPOSITORY = 'owner/paper'


def pull(number, title, label, merged_at, head_ref=None, base_ref='main', head_repo=REPOSITORY):
    return {
        'number': number, 'title': title, 'user': {'login': 'author'},
        'html_url': f'https://github.com/{REPOSITORY}/pull/{number}',
        'labels': [{'name': label}], 'merged_at': merged_at,
        'merge_commit_sha': f'merge-{number}' if merged_at else None,
        'head': {'ref': head_ref or f'branch-{number}', 'sha': f'head-{number}',
                 'repo': {'full_name': head_repo}},
        'base': {'ref': base_ref},
    }


class StackTests(unittest.TestCase):
    """A stack: #193 merges into main carrying #194 and #195, which carry #197 and #196."""

    def setUp(self):
        self.ci = pull(192, 'ci: strip the job token', 'release:none', '2026-10-26T06:21:00Z')
        self.base = pull(193, 'docs: evaluate the median', 'release:minor', '2026-10-27T09:00:00Z',
                         head_ref='docs/aggregation')
        self.into_branch = {
            'docs/aggregation': [
                pull(195, 'docs(companion): state no intervention power', 'release:none',
                     '2026-10-27T08:10:00Z', head_ref='docs/intervention', base_ref='docs/aggregation'),
                pull(194, 'docs: name migration as the backstop', 'release:minor',
                     '2026-10-27T08:00:00Z', head_ref='docs/migration', base_ref='docs/aggregation'),
                pull(150, 'docs: an older pull request into a reused branch name', 'release:minor',
                     '2026-09-01T00:00:00Z', base_ref='docs/aggregation'),
                pull(151, 'docs: closed without merging', 'release:minor', None,
                     base_ref='docs/aggregation'),
            ],
            'docs/migration': [
                pull(197, 'docs: define trustless & cite <Trust Models>', 'release:minor',
                     '2026-10-27T07:00:00Z', base_ref='docs/migration'),
            ],
            'docs/intervention': [
                pull(196, 'docs(companion): state the court commitment', 'release:none',
                     '2026-10-27T07:30:00Z', base_ref='docs/intervention'),
            ],
        }
        self.outside_history = {'merge-150'}
        self.enterContext(patch.object(notes, 'gh_api', side_effect=self.api))

    def api(self, path):
        url = urlsplit(path)
        if url.path == f'repos/{REPOSITORY}/pulls':
            query = parse_qs(url.query)
            self.assertEqual(query['state'], ['closed'])
            if query['page'] != ['1']:
                return []
            return self.into_branch.get(query['base'][0], [])
        compared = url.path.removeprefix(f'repos/{REPOSITORY}/compare/')
        commit, _, _head = compared.partition('...')
        return {'behind_by': 1 if commit in self.outside_history else 0}

    def changes(self):
        return notes.release_changes(REPOSITORY, [self.base, self.ci])

    def test_stacked_pull_requests_nest_under_the_pull_request_that_carried_them(self):
        def numbers(changes):
            return [(change.pull['number'], numbers(change.stacked)) for change in changes]

        self.assertEqual(numbers(self.changes()),
                         [(192, []), (193, [(194, [(197, [])]), (195, [(196, [])])])])

    def test_a_pull_request_outside_its_parents_merged_history_is_left_out(self):
        self.outside_history.add('merge-197')
        stacked = {change.pull['number']: change.stacked for change in self.changes()[1].stacked}
        self.assertEqual(stacked[194], ())

    def test_github_notes_indent_stacked_pull_requests_under_their_parent(self):
        url = f'https://github.com/{REPOSITORY}/pull'
        self.assertEqual(notes.github_notes(REPOSITORY, self.changes(), 'v1.3.2', 'v1.4.0'), '\n'.join([
            "## What's Changed",
            f'* ci: strip the job token by @author in {url}/192',
            f'* docs: evaluate the median by @author in {url}/193',
            f'  * docs: name migration as the backstop by @author in {url}/194',
            f'    * docs: define trustless & cite <Trust Models> by @author in {url}/197',
            f'  * docs(companion): state no intervention power by @author in {url}/195',
            f'    * docs(companion): state the court commitment by @author in {url}/196',
            '',
            f'**Full Changelog**: https://github.com/{REPOSITORY}/compare/v1.3.2...v1.4.0',
            '',
        ]))

    def test_deposit_notes_list_only_changes_to_the_published_paper(self):
        url = f'https://github.com/{REPOSITORY}/pull'
        self.assertEqual(notes.deposit_notes(self.changes(), 'v1.3.2'), '\n'.join([
            '<p>Changes since v1.3.2:</p>',
            '<ul>',
            f'<li>Evaluate the median (<a href="{url}/193">#193</a>)</li>',
            f'<li>Name migration as the backstop (<a href="{url}/194">#194</a>)</li>',
            f'<li>Define trustless &amp; cite &lt;Trust Models&gt; (<a href="{url}/197">#197</a>)</li>',
            '</ul>',
            '',
        ]))

    def test_a_stacked_pull_request_without_a_release_label_blocks_the_notes(self):
        self.into_branch['docs/migration'][0]['labels'] = []
        with self.assertRaisesRegex(notes.ReleaseLabelError, '#197'):
            notes.deposit_notes(self.changes(), 'v1.3.2')


if __name__ == '__main__':
    unittest.main()
