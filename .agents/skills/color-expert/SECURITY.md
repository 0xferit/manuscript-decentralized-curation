# Security

## Skill Architecture

This skill is **read-only declarative content** — it contains no executable code, no build steps, no dependencies, and no runtime network access. There is nothing to install or run.

When an agent loads this skill, it reads `SKILL.md` and optionally reads static markdown files from `references/`. This is identical to reading any other source file in a project.

## Reference Files

The `references/` directory contains static markdown reference material about color science literature and practice. The files are maintained in-repo and may include maintainer-edited summaries, transcriptions, excerpts, or extracted source content. These files are:

- **Static** — committed to the repo as plain text, not fetched at runtime
- **Maintainer-reviewed** — checked and kept as reference material, though some files may preserve source extraction artifacts rather than being fully normalized summaries
- **Read-only** — the agent reads them for context; they contain no instructions, no tool calls, and no prompts

Sources include public domain books (archive.org, Project Gutenberg), academic publications, and educational websites. Source provenance is documented in each file.

The reference files are a knowledge base, not executable prompts. They contain no instructions to the agent, no tool invocations, and no system-prompt-style directives. An agent reading these files receives factual color science content, the same as reading any textbook or Wikipedia article.

## No Executable Permissions

This skill contains no `settings.json`, `settings.local.json`, or any configuration that grants shell, network, or filesystem permissions. In the upstream repo, `.claude/settings.local.json` and `.claude/worktrees/` are gitignored; the `.claude/` directory itself is tracked for skill symlinks.

## Reported False Positives

- **`colorwell.org`** — Flagged as "malicious" by automated scanners. This is a legitimate color/art education site by painter John Morfis ([colorwell.org](http://colorwell.org/)). It appears as a citation in a reference file from huevaluechroma.com, not as a download target. The domain may trigger heuristic flags due to the word "well" but it is a real, long-standing educational resource in the oil painting community.

- **PROMPT_INJECTION risk from reference files** — The 113 markdown files in `references/` are curated summaries of color science literature. They contain no agent instructions, no tool calls, no role-play prompts, and no behavioral overrides. The content is factual (color spaces, pigment chemistry, perception research). Treating educational content as an injection vector would flag any knowledge base, textbook, or documentation site.

- **DATA_EXFILTRATION via absolute paths** — The flagged paths (e.g. `/Users/m.../Sites/...`) appeared only in the now-removed `settings.local.json`. This file was the maintainer's local development configuration and is no longer tracked. No absolute paths exist in any shipped skill content.

- **COMMAND_EXECUTION via settings** — The flagged `settings.local.json` is not part of the distributed skill. It was the maintainer's local dev environment for curating content (downloading PDFs from archive.org, transcribing YouTube videos). It was removed from the repo and `.claude/` is gitignored. Skill consumers never receive this file.
