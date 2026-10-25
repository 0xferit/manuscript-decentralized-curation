from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / '.github/scripts/release_version.py'
SPEC = importlib.util.spec_from_file_location('release_version', SCRIPT)
planner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(planner)
Bump = planner.Bump


class NextTagTests(unittest.TestCase):
    def test_each_bump_resets_the_lower_components(self):
        self.assertEqual(planner.next_tag('v1.3.7', Bump.PATCH), 'v1.3.8')
        self.assertEqual(planner.next_tag('v1.3.7', Bump.MINOR), 'v1.4.0')
        self.assertEqual(planner.next_tag('v1.3.7', Bump.MAJOR), 'v2.0.0')

    def test_latest_tag_orders_numerically_and_ignores_other_release_lines(self):
        tags = ['v1.9.0', 'v1.10.0', 'public-goods-v9.0.0', 'v1.2.0']
        self.assertEqual(planner.latest_tag(tags), 'v1.10.0')


class LabelTests(unittest.TestCase):
    def test_one_release_label_names_the_bump_and_other_labels_are_ignored(self):
        self.assertIs(planner.bump_from_labels(['dependencies', 'release:minor']), Bump.MINOR)

    def test_a_pull_request_needs_exactly_one_release_label(self):
        for labels in ([], ['dependencies'], ['release:patch', 'release:major'], ['release:huge']):
            with self.subTest(labels=labels), self.assertRaises(planner.ReleaseLabelError):
                planner.bump_from_labels(labels)

    def test_a_push_releases_the_highest_bump_among_its_pull_requests(self):
        pulls = [['release:patch'], ['release:none'], ['release:major'], ['release:minor']]
        self.assertIs(planner.bump_for_pulls(pulls), Bump.MAJOR)
        self.assertIs(planner.bump_for_pulls([['release:none'], ['release:none']]), Bump.NONE)

    def test_an_unlabelled_merged_pull_request_blocks_the_release(self):
        with self.assertRaises(planner.ReleaseLabelError):
            planner.bump_for_pulls([['release:major'], []])


if __name__ == '__main__':
    unittest.main()
