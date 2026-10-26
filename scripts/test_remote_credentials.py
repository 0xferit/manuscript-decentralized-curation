from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / '.github/scripts/remote_credentials.py'
TOKEN = 'ghs_exampleToken0123456789'
ACTION_REMOTE = f'https://x-access-token:{TOKEN}@github.com/owner/repo.git'
PLAIN_REMOTE = 'https://github.com/owner/repo.git'


class RemoteCredentialsTests(unittest.TestCase):
    def setUp(self):
        self.repository = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.git('init', '--quiet')
        self.git('remote', 'add', 'origin', ACTION_REMOTE)

    def git(self, *arguments):
        return subprocess.run(['git', *arguments], cwd=self.repository, capture_output=True, text=True, check=True).stdout.strip()

    def run_script(self, mode):
        return subprocess.run([sys.executable, str(SCRIPT), mode], cwd=self.repository, capture_output=True, text=True)

    def test_strip_removes_the_token_the_review_action_writes(self):
        self.assertEqual(self.run_script('strip').returncode, 0)
        self.assertEqual(self.git('config', '--get', 'remote.origin.url'), PLAIN_REMOTE)

    def test_check_fails_without_echoing_the_token_until_it_is_stripped(self):
        refused = self.run_script('check')
        self.assertEqual(refused.returncode, 1)
        self.assertNotIn(TOKEN, refused.stdout + refused.stderr)
        self.run_script('strip')
        self.assertEqual(self.run_script('check').returncode, 0)


if __name__ == '__main__':
    unittest.main()
