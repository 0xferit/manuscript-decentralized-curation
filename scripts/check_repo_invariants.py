#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

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

INCLUDE_PATTERN = re.compile(
    r"""\{\{<\s*include\s+("[^"]+"|'[^']+'|[^\s>]+)\s*>}}"""
)
LINK_DESTINATION = r'(?:<([^>\n]+)>|([^\s)]+))'
INLINE_LINK_PATTERN = re.compile(r'(?<!!)\[[^\]\n]*\]\(\s*' + LINK_DESTINATION)
REFERENCE_LINK_PATTERN = re.compile(r'^ {0,3}\[[^\]\n]+\]:\s*' + LINK_DESTINATION, re.MULTILINE)
MARKDOWN_CODE_INDENT = 4
LIST_ITEM_PATTERN = re.compile(r"^ *(?:[-+*]|\d+[.)]) +")
ANCHOR_OPEN_PATTERN = re.compile(r"<a(?:\s|>|$)", re.IGNORECASE)
ANCHOR_CLOSE_PATTERN = re.compile(r"</a\s*>", re.IGNORECASE)
FENCE_PATTERN = re.compile(r'^ {0,3}(`{3,}|~{3,})')
NON_NAVIGATION_PATTERN = re.compile(
    r"<!--[\s\S]*?-->|<(?P<code_tag>pre|code)\b[^>]*>[\s\S]*?</(?P=code_tag)\s*>"
    r"|(?<!`)(?P<ticks>`+)(?!`)[\s\S]*?(?<!`)(?P=ticks)(?!`)",
    re.IGNORECASE,
)
HTML_BLOCK_TAGS = {
    "div", "section", "article", "aside", "nav", "main", "header", "footer",
    "figure", "figcaption", "details", "summary", "table", "thead", "tbody",
    "tfoot", "tr", "td", "th", "ul", "ol", "li", "dl", "dt", "dd",
    "blockquote", "p", "form", "fieldset",
}


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


class HTMLNavigationParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.destinations: list[tuple[int, str]] = []
        self.open_blocks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in HTML_BLOCK_TAGS:
            self.open_blocks.append(tag)
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value is not None:
                    self.destinations.append((self.getpos()[0], value))

    def handle_endtag(self, tag: str) -> None:
        if self.open_blocks and tag == self.open_blocks[-1]:
            self.open_blocks.pop()


def navigation_text(text: str) -> str:
    text = NON_NAVIGATION_PATTERN.sub(
        lambda match: re.sub(r"[^\n]", " ", match.group()), text
    )
    lines = []
    html_context = HTMLNavigationParser()
    fence = None
    list_content_indents: list[int] = []
    inside_anchor = False
    for line in text.splitlines(keepends=True):
        expanded = line.expandtabs(MARKDOWN_CODE_INDENT)
        indent = len(expanded) - len(expanded.lstrip())
        if line.strip() and fence is None:
            while list_content_indents and indent < list_content_indents[-1]:
                list_content_indents.pop()
        content_indent = list_content_indents[-1] if list_content_indents else 0
        marker = FENCE_PATTERN.match(expanded[content_indent:])
        inside_fence = fence is not None
        if marker:
            run = marker.group(1)
            if fence is None:
                fence = run
            elif run[0] == fence[0] and len(run) >= len(fence) and not expanded[content_indent + marker.end():].strip():
                fence = None
        indented_code = (
            indent >= content_indent + MARKDOWN_CODE_INDENT
            and not inside_anchor
            and not html_context.open_blocks
        )
        if inside_fence or marker or indented_code:
            line = re.sub(r"[^\n]", " ", line)
        else:
            html_context.feed(line)
            item = LIST_ITEM_PATTERN.match(expanded)
            if item:
                list_content_indents.append(item.end())
            if ANCHOR_OPEN_PATTERN.search(line):
                inside_anchor = True
            if ANCHOR_CLOSE_PATTERN.search(line):
                inside_anchor = False
        lines.append(line)
    return "".join(lines)


def published_source_paths() -> tuple[Path, ...]:
    pending = [Path(path) for path in EXPECTED_RENDER_INPUTS]
    visited = set()
    while pending:
        path = pending.pop()
        if path in visited or not (ROOT / path).is_file():
            continue
        visited.add(path)
        for match in INCLUDE_PATTERN.finditer(navigation_text(read_text(path))):
            target = (ROOT / path.parent / match.group(1).strip('\'"')).resolve()
            if target.is_relative_to(ROOT):
                pending.append(target.relative_to(ROOT))
    return tuple(sorted(visited))


def check_published_navigation(errors: list[str]) -> None:
    for relative_path in published_source_paths():
        text = navigation_text(read_text(relative_path))
        parser = HTMLNavigationParser()
        parser.feed(text)
        destinations = parser.destinations
        for pattern in (INLINE_LINK_PATTERN, REFERENCE_LINK_PATTERN):
            for match in pattern.finditer(text):
                destination = unescape(next(group for group in match.groups() if group is not None))
                destinations.append((text.count("\n", 0, match.start()) + 1, destination))
        for line, destination in destinations:
            try:
                target = urlsplit(destination)
            except ValueError as error:
                errors.append(f"{relative_path}:{line}: invalid navigation target `{destination}`: {error}")
                continue
            if target.scheme or target.netloc or not unquote(target.path).lower().endswith(".qmd"):
                continue
            errors.append(
                f"{relative_path}:{line}: local navigation target `{destination}` uses a .qmd source; "
                "link to its published HTML route instead"
            )


def main() -> int:
    errors: list[str] = []
    check_wrapper_routes(errors)
    check_quarto_render_list(errors)
    check_citations(errors)
    check_published_navigation(errors)

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("Repo invariants OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
