from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / '.github/scripts/install_review_skills.py'
SPEC = importlib.util.spec_from_file_location('install_review_skills', SCRIPT)
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)

BODY = '# Skill\n\nallowed-tools: in the body is prose, not a grant.\n'


class InstallReviewSkillsTests(unittest.TestCase):
    def setUp(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.sources = root / 'sources'
        self.destination = root / 'skills'

    def skill(self, name, frontmatter):
        directory = self.sources / name
        (directory / 'references').mkdir(parents=True)
        (directory / 'SKILL.md').write_text(f'---\n{frontmatter}---\n{BODY}', encoding='utf-8')
        (directory / 'references' / 'rules.md').write_text('rules\n', encoding='utf-8')
        return directory

    def installed(self, name):
        return (self.destination / name / 'SKILL.md').read_text(encoding='utf-8')

    def test_every_form_of_tool_grant_is_removed(self):
        forms = {
            'inline': ('allowed-tools: Read Write Edit Bash WebSearch WebFetch\ndescription: d\n', 'description: d\n'),
            'flow-list': ('allowed-tools: [Read, Grep, Glob, Bash, Agent]\ncontext: inherit\n', 'context: inherit\n'),
            'block-list': ('allowed-tools:\n  - Read\n  - Bash\ndescription: d\n', 'description: d\n'),
            'unindented-block-list': ('allowed-tools:\n- Read\ndescription: d\n', 'description: d\n'),
            'last-key': ('allowed-tools:\n  - WebFetch\n', ''),
        }
        sources = [self.skill(name, f'name: {name}\n{granted}') for name, (granted, _) in forms.items()]
        installer.install(sources, self.destination)
        for name, (_, kept) in forms.items():
            with self.subTest(name=name):
                self.assertEqual(self.installed(name), f'---\nname: {name}\n{kept}---\n{BODY}')

    def test_other_frontmatter_and_skill_files_are_kept(self):
        frontmatter = 'name: peer-review\nlicense: MIT\nmetadata:\n    version: "2.2"\n'
        installer.install([self.skill('peer-review', frontmatter)], self.destination)
        self.assertEqual(self.installed('peer-review'), f'---\n{frontmatter}---\n{BODY}')
        self.assertTrue((self.destination / 'peer-review' / 'references' / 'rules.md').is_file())

    def test_unterminated_frontmatter_is_refused_by_name(self):
        source = self.skill('unterminated', '')
        (source / 'SKILL.md').write_text('---\nname: unterminated\nbody\n', encoding='utf-8')
        with self.assertRaisesRegex(SystemExit, 'unterminated.*frontmatter'):
            installer.install([source], self.destination)

    def test_license_is_copied_into_each_installed_skill(self):
        license_file = self.sources / 'LICENSE.md'
        sources = [self.skill('one', 'name: one\n'), self.skill('two', 'name: two\n')]
        license_file.write_text('MIT License\n', encoding='utf-8')
        installer.install(sources, self.destination, license_file=license_file)
        for name in ('one', 'two'):
            self.assertEqual((self.destination / name / 'LICENSE.md').read_text(encoding='utf-8'), 'MIT License\n')

    def test_unrecognised_tool_grant_is_refused(self):
        source = self.skill('quoted', 'name: quoted\n"allowed-tools": [Bash]\n')
        with self.assertRaisesRegex(SystemExit, 'quoted'):
            installer.install([source], self.destination)
        self.assertFalse((self.destination / 'quoted').exists())


if __name__ == '__main__':
    unittest.main()
