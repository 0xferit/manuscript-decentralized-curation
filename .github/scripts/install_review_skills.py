"""Install skills for the CI paper review without their tool grants.

A skill's ``allowed-tools`` frontmatter pre-approves those tools while the
skill is active, which in a headless run is the rest of the run. The paper
review grants tools only through its workflow's ``--allowedTools``, so each
installed copy drops the key. A manifest that still names ``allowed-tools``
in its frontmatter after that, in a form this script does not remove, stops
the installation before the skill is copied.

Usage: ``install_review_skills.py DESTINATION SKILL_DIR... [--license FILE]``.
``--license`` copies a licence file into every installed skill, for skills
copied from a third-party repository.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

MANIFEST = 'SKILL.md'
FRONTMATTER_DELIMITER = '---\n'
TOOL_GRANT_KEY = 'allowed-tools'
YAML_CONTINUATION_PREFIXES = (' ', '\t', '-')


def without_tool_grant(frontmatter: list[str]) -> list[str]:
    kept = []
    inside_grant = False
    for line in frontmatter:
        continues_previous_key = line.startswith(YAML_CONTINUATION_PREFIXES)
        inside_grant = line.startswith(f'{TOOL_GRANT_KEY}:') or (inside_grant and continues_previous_key)
        if not inside_grant:
            kept.append(line)
    return kept


def manifest_without_tool_grant(skill: Path) -> str:
    lines = (skill / MANIFEST).read_text(encoding='utf-8').splitlines(keepends=True)
    if not lines or lines[0] != FRONTMATTER_DELIMITER:
        sys.exit(f'{skill / MANIFEST}: does not start with YAML frontmatter')
    end = lines.index(FRONTMATTER_DELIMITER, 1)
    frontmatter = without_tool_grant(lines[1:end])
    if any(TOOL_GRANT_KEY in line for line in frontmatter):
        sys.exit(f'{skill / MANIFEST}: names {TOOL_GRANT_KEY} in a form this installer does not remove')
    return ''.join([lines[0], *frontmatter, *lines[end:]])


def install(skills: list[Path], destination: Path, license_file: Path | None = None) -> None:
    for skill in skills:
        manifest = manifest_without_tool_grant(skill)
        installed = destination / skill.name
        shutil.copytree(skill, installed)
        (installed / MANIFEST).write_text(manifest, encoding='utf-8')
        if license_file is not None:
            shutil.copyfile(license_file, installed / license_file.name)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('destination', type=Path)
    parser.add_argument('skills', type=Path, nargs='+')
    parser.add_argument('--license', type=Path, dest='license_file')
    arguments = parser.parse_args(argv[1:])
    install(arguments.skills, arguments.destination, arguments.license_file)
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
