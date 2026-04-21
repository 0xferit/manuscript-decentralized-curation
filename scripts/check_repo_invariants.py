#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_WRAPPER_INCLUDES = {
    Path("truth-post/blueprint/index.qmd"): "{{< include ../../projects/truth-post/blueprint.md >}}",
    Path("rpgf/design/index.qmd"): "{{< include ../../projects/rpgf/design.md >}}",
}

EXPECTED_RENDER_INPUTS = (
    "paper.qmd",
    "truth-post/index.qmd",
    "truth-post/blueprint/index.qmd",
    "rpgf/index.qmd",
    "rpgf/design/index.qmd",
)

NON_BIB_CROSSREF_PREFIXES = (
    "fig-",
    "tbl-",
    "sec-",
    "eq-",
    "lem-",
    "thm-",
    "def-",
    "cor-",
    "exm-",
    "lst-",
    "alg-",
    "app-",
)

BIB_ENTRY_PATTERN = re.compile(r"@\w+\{([^,\s]+),")
CITATION_PATTERN = re.compile(r"(?<![A-Za-z0-9_:-])@([A-Za-z0-9][A-Za-z0-9:_-]*)")


def read_text(path: Path) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def source_paths() -> tuple[Path, ...]:
    return (
        Path("paper.qmd"),
        *sorted(path.relative_to(ROOT) for path in (ROOT / "projects").rglob("*.md")),
        *sorted(path.relative_to(ROOT) for path in (ROOT / "truth-post").rglob("*.qmd")),
        *sorted(path.relative_to(ROOT) for path in (ROOT / "rpgf").rglob("*.qmd")),
    )


def load_bib_keys() -> set[str]:
    bib_text = read_text(Path("references.bib"))
    return set(BIB_ENTRY_PATTERN.findall(bib_text))


def extract_citations(text: str) -> set[str]:
    keys = set(CITATION_PATTERN.findall(text))
    return {
        key
        for key in keys
        if not key.startswith(NON_BIB_CROSSREF_PREFIXES)
    }


def check_wrapper_routes(errors: list[str]) -> None:
    for relative_path, expected_include in EXPECTED_WRAPPER_INCLUDES.items():
        text = read_text(relative_path)
        if expected_include not in text:
            errors.append(
                f"{relative_path}: missing canonical include `{expected_include}`"
            )


def check_quarto_render_list(errors: list[str]) -> None:
    quarto_text = read_text(Path("_quarto.yml"))
    for relative_path in EXPECTED_RENDER_INPUTS:
        quoted = f'- "{relative_path}"'
        if quoted not in quarto_text:
            errors.append(
                f"_quarto.yml: missing project render entry for `{relative_path}`"
            )


def check_citations(errors: list[str]) -> None:
    known_keys = load_bib_keys()
    for relative_path in source_paths():
        cited_keys = extract_citations(read_text(relative_path))
        missing = sorted(key for key in cited_keys if key not in known_keys)
        if missing:
            errors.append(
                f"{relative_path}: missing BibTeX entries for {', '.join(missing)}"
            )


def main() -> int:
    errors: list[str] = []
    check_wrapper_routes(errors)
    check_quarto_render_list(errors)
    check_citations(errors)

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("Repo invariants OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
