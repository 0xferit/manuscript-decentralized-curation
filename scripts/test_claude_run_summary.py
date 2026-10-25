from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / '.github/scripts/summarize_claude_run.py'
SPEC = importlib.util.spec_from_file_location('summarize_claude_run', SCRIPT)
summarizer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(summarizer)


def result_message(**overrides):
    message = {
        'type': 'result',
        'subtype': 'success',
        'is_error': False,
        'num_turns': 9,
        'result': 'No issues found.',
        'permission_denials': [],
    }
    message.update(overrides)
    return message


class ClaudeRunSummaryTests(unittest.TestCase):
    def setUp(self):
        self.directory = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def write_log(self, messages):
        path = self.directory / 'claude-execution-output.json'
        path.write_text(json.dumps(messages), encoding='utf-8')
        return str(path)

    def test_missing_log_reports_that_the_review_did_not_run(self):
        for execution_file in ('', str(self.directory / 'absent.json')):
            with self.subTest(execution_file=execution_file):
                summary = summarizer.summarize(execution_file)
                self.assertIn('did not run', summary)
                self.assertNotIn('denied', summary)

    def test_log_without_result_reports_an_early_end(self):
        path = self.write_log([{'type': 'system', 'subtype': 'init'}, {'type': 'assistant', 'message': {}}])
        summary = summarizer.summarize(path)
        self.assertIn('2 messages', summary)
        self.assertIn('no result', summary)

    def test_clean_run_states_that_nothing_was_denied(self):
        path = self.write_log([{'type': 'system', 'subtype': 'init'}, result_message()])
        summary = summarizer.summarize(path)
        self.assertIn('`success` after 9 turns', summary)
        self.assertIn('No tool call was denied.', summary)
        self.assertIn('> No issues found.', summary)

    def test_denied_calls_are_listed_with_their_inputs(self):
        denials = [
            {'tool_name': 'Bash', 'tool_use_id': 'toolu_1', 'tool_input': {'command': 'gh pr comment 175 --body-file /tmp/review.md'}},
            {'tool_name': 'mcp__github_inline_comment__create_inline_comment', 'tool_use_id': 'toolu_2', 'tool_input': {'path': 'paper.qmd', 'line': 3}},
        ]
        path = self.write_log([result_message(result='Two findings.\n\nThe first one.', permission_denials=denials)])
        summary = summarizer.summarize(path)
        self.assertIn('2 denied tool calls', summary)
        self.assertIn('    Bash  {"command": "gh pr comment 175 --body-file /tmp/review.md"}', summary)
        self.assertIn('    mcp__github_inline_comment__create_inline_comment  {"line": 3, "path": "paper.qmd"}', summary)
        self.assertIn('> Two findings.\n>\n> The first one.', summary)

    def test_long_inputs_are_cut_to_the_preview_length(self):
        command = 'x' * (summarizer.INPUT_PREVIEW_CHARS * 2)
        path = self.write_log([result_message(permission_denials=[{'tool_name': 'Bash', 'tool_input': {'command': command}}])])
        summary = summarizer.summarize(path)
        longest_line = max(summary.splitlines(), key=len)
        self.assertEqual(len(longest_line), len('    Bash  ') + summarizer.INPUT_PREVIEW_CHARS)
        self.assertIn('1 denied tool call.', summary)

    def test_error_results_are_flagged(self):
        path = self.write_log([result_message(subtype='error_during_execution', is_error=True, result='', errors=['out of usage'])])
        summary = summarizer.summarize(path)
        self.assertIn('`error_during_execution`', summary)
        self.assertIn('Claude reported an error: out of usage', summary)
        self.assertIn('Claude returned no final text.', summary)

    def test_command_line_accepts_the_empty_path_the_workflow_passes_when_the_action_skipped(self):
        completed = subprocess.run([sys.executable, '-I', str(SCRIPT), ''], capture_output=True, text=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(completed.stdout.startswith('## Review outcome'), completed.stdout)
        self.assertIn('did not run', completed.stdout)


if __name__ == '__main__':
    unittest.main()
