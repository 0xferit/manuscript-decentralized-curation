"""Render a Claude Code Action run as a job-summary section.

The action keeps every message of a run in the JSON array it exposes as its
``execution_file`` output, but its job log states only how many tool calls
were denied. A review that found problems and could not post them therefore
looks like a clean one. This script lists the denied tool calls with their
inputs and quotes Claude's final message.

Usage: ``summarize_claude_run.py [EXECUTION_FILE]``. The Markdown goes to
stdout; the workflow appends it to ``$GITHUB_STEP_SUMMARY``. An empty or
missing path is the normal case when the action skipped the run.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HEADING = '## Review outcome'
INPUT_PREVIEW_CHARS = 600
CODE_INDENT = '    '


def summarize(execution_file: str) -> str:
    if not execution_file or not Path(execution_file).is_file():
        return (
            f'{HEADING}\n\nNo execution log. The review did not run; a pull request '
            'that edits this workflow is the usual reason.\n'
        )
    messages = json.loads(Path(execution_file).read_text(encoding='utf-8'))
    result = next((m for m in messages if isinstance(m, dict) and m.get('type') == 'result'), None)
    if result is None:
        return (
            f'{HEADING}\n\nThe log holds {len(messages)} messages and no result: '
            'the run ended before Claude reported one.\n'
        )
    return '\n'.join([HEADING, '', *outcome_lines(result), '', *denial_lines(result), '', *final_message_lines(result), ''])


def outcome_lines(result: dict) -> list[str]:
    denials = result.get('permission_denials') or []
    noun = 'denied tool call' if len(denials) == 1 else 'denied tool calls'
    lines = [f"Outcome `{result.get('subtype', 'unknown')}` after {result.get('num_turns', '?')} turns; {len(denials)} {noun}."]
    if result.get('is_error'):
        errors = '; '.join(str(error) for error in result.get('errors') or []) or 'no detail given'
        lines.append(f'Claude reported an error: {errors}')
    return lines


def denial_lines(result: dict) -> list[str]:
    denials = result.get('permission_denials') or []
    if not denials:
        return ['No tool call was denied.']
    lines = ['### Denied tool calls', '']
    for denial in denials:
        tool_input = json.dumps(denial.get('tool_input'), ensure_ascii=False, sort_keys=True)
        lines.append(f"{CODE_INDENT}{denial.get('tool_name', '?')}  {tool_input[:INPUT_PREVIEW_CHARS]}")
    return lines


def final_message_lines(result: dict) -> list[str]:
    text = str(result.get('result') or '').strip()
    if not text:
        return ['Claude returned no final text.']
    return ['### Final message', '', *(f'> {line}'.rstrip() for line in text.splitlines())]


def main(argv: list[str]) -> int:
    execution_file = argv[1] if len(argv) > 1 else ''
    sys.stdout.write(summarize(execution_file))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
