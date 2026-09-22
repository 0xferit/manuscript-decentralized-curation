#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]


class PublishedNavigationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for relative in (
            'scripts/check_repo_invariants.py',
            '_quarto.yml',
            'truth-post/blueprint/index.qmd',
            'rpgf/design/index.qmd',
        ):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPOSITORY / relative, target)
        for relative in (
            'paper.qmd', 'references.bib', 'truth-post/index.qmd', 'rpgf/index.qmd',
            'projects/truth-post/blueprint.md', 'projects/rpgf/design.md',
        ):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('', encoding='utf-8')

    def check(self, text: str, source: str = 'paper.qmd') -> subprocess.CompletedProcess[str]:
        (self.root / source).write_text(text, encoding='utf-8')
        return subprocess.run(
            [sys.executable, str(self.root / 'scripts/check_repo_invariants.py')],
            capture_output=True, text=True, check=False,
        )

    def test_rejects_source_navigation_targets(self) -> None:
        for text, line in (
            ('[Blueprint](truth-post/blueprint/index.qmd#open-questions)', 1),
            ('[Blueprint](<truth-post/blueprint/index.qmd?view=all#open-questions>)', 1),
            ('[Blueprint][policy]\n\n[policy]: truth-post/blueprint/index.qmd#scope', 3),
            ('<a href="truth-post/blueprint/index.qmd?view=all#scope">Blueprint</a>', 1),
        ):
            with self.subTest(text=text):
                result = self.check(text)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn(f'paper.qmd:{line}:', result.stderr)
                self.assertIn('index.qmd', result.stderr)

    def test_rejects_nested_list_navigation(self) -> None:
        for text in (
            '- Parent\n    - [Broken](paper.qmd#scope)\n',
            '- Parent\n\n    [Continuation](paper.qmd)\n',
        ):
            with self.subTest(text=text):
                result = self.check(text)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn('paper.qmd', result.stderr)

    def test_rejects_multiline_html_navigation(self) -> None:
        result = self.check('<a\n    href="paper.qmd">Broken</a>')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('paper.qmd:1:', result.stderr)

    def test_reads_only_actual_html_href_attribute(self) -> None:
        result = self.check('<a data-href="paper.qmd" href="index.html">Valid</a>')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_reports_malformed_destination_without_traceback(self) -> None:
        result = self.check('[Invalid](https://[broken/paper.qmd)')
        self.assertEqual(result.returncode, 1)
        self.assertIn('paper.qmd:1: invalid navigation target', result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_ignores_indented_code_in_list(self) -> None:
        result = self.check('- Parent\n\n      [Code example](paper.qmd)\n')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_inline_code_does_not_change_html_indentation_context(self) -> None:
        result = self.check('`<a href="example">`\n\n    [Example](paper.qmd)\n')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_commented_fence_does_not_hide_following_navigation(self) -> None:
        result = self.check('<!--\n```\n-->\n[Paper](paper.qmd)\n')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('paper.qmd:4:', result.stderr)

    def test_checks_anchor_indented_inside_html_block(self) -> None:
        result = self.check('<div>\n    <a href="paper.qmd">Paper</a>\n</div>')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('paper.qmd:2:', result.stderr)

    def test_ignores_html_pre_and_code_examples(self) -> None:
        result = self.check('<pre><code>[Example](paper.qmd)</code></pre>')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_checks_canonical_included_content(self) -> None:
        result = self.check('[Paper](../../paper.qmd)', 'projects/rpgf/design.md')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('projects/rpgf/design.md:1:', result.stderr)

    def test_ignores_unpublished_project_notes(self) -> None:
        result = self.check('[Source](../paper.qmd)', 'projects/README.md')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_accepts_routes_external_sources_and_non_links(self) -> None:
        text = '''[Blueprint](truth-post/blueprint/index.html?view=all#scope)
[Root route](/truth-post/blueprint/#scope)
[Local section](#scope)
[Source](https://github.com/example/repo/blob/main/paper.qmd)
[Remote](//example.org/paper.qmd)
Plain paper.qmd and `paper.qmd` are filenames.
`[example](paper.qmd)`
```markdown
[example](paper.qmd)
```
~~~html
<a href="paper.qmd">example</a>
~~~
    [indented code](paper.qmd)
<!-- [comment](paper.qmd) -->
'''
        result = self.check(text)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Repo invariants OK', result.stdout)


if __name__ == '__main__':
    unittest.main()
