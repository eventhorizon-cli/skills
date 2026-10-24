#!/usr/bin/env python3
"""Check local image references in Markdown documents.

The checker intentionally handles the two forms commonly used in technical
documentation: Markdown image syntax and HTML ``img`` tags. Remote URLs,
data URLs, and fragment-only references are left to the publishing platform.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit


MARKDOWN_IMAGE = re.compile(
    r"!\[[^\]]*\]\(\s*(?:<(?P<bracketed>[^>]+)>|(?P<plain>[^\s)]+))"
    r"(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)",
    re.MULTILINE,
)
IMG_TAG = re.compile(r"<img\b[^>]*>", re.IGNORECASE | re.MULTILINE)
IMG_SRC = re.compile(
    r"\bsrc\s*=\s*(?:"
    r"(?P<double>\"[^\"]*\")|"
    r"(?P<single>'[^']*')|"
    r"(?P<bare>[^\s>]+)"
    r")",
    re.IGNORECASE,
)
FENCED_CODE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,}).*$", re.MULTILINE)
INLINE_CODE = re.compile(r"(?P<ticks>`+)(?P<body>[^`\n]*?)(?P=ticks)")


@dataclass(frozen=True)
class Reference:
    source: str
    offset: int
    line: int
    kind: str
    target: str


def _mask_fenced_code(markdown: str) -> str:
    """Replace fenced code contents with spaces while retaining line breaks."""

    matches = list(FENCED_CODE.finditer(markdown))
    if not matches:
        return markdown

    masked = list(markdown)
    index = 0
    while index < len(matches):
        opening = matches[index]
        closing = None
        marker = opening.group(1)[0]
        marker_length = len(opening.group(1))
        for candidate in matches[index + 1 :]:
            candidate_marker = candidate.group(1)
            if candidate_marker[0] == marker and len(candidate_marker) >= marker_length:
                closing = candidate
                break
        end = closing.end() if closing else len(markdown)
        for position in range(opening.start(), end):
            if masked[position] != "\n":
                masked[position] = " "
        if closing is None:
            break
        index = matches.index(closing) + 1
    return "".join(masked)


def _line_number(markdown: str, offset: int) -> int:
    return markdown.count("\n", 0, offset) + 1


def _mask_inline_code(markdown: str) -> str:
    """Replace inline code spans with spaces while retaining line structure."""

    masked = list(markdown)
    for match in INLINE_CODE.finditer(markdown):
        for position in range(match.start(), match.end()):
            if masked[position] != "\n":
                masked[position] = " "
    return "".join(masked)


def _extract_references(source: str, markdown: str) -> list[Reference]:
    masked = _mask_inline_code(_mask_fenced_code(markdown))
    references: list[Reference] = []
    for match in MARKDOWN_IMAGE.finditer(masked):
        target = match.group("bracketed") or match.group("plain")
        assert target is not None
        references.append(
            Reference(
                source, match.start(), _line_number(markdown, match.start()), "Markdown", target
            )
        )
    for tag in IMG_TAG.finditer(masked):
        source_match = IMG_SRC.search(tag.group(0))
        if source_match is None:
            continue
        target = next(value for value in source_match.groups() if value is not None)
        if target[:1] in {'"', "'"}:
            target = target[1:-1]
        references.append(
            Reference(
                source, tag.start(), _line_number(markdown, tag.start()), "HTML img", target
            )
        )
    return sorted(references, key=lambda reference: reference.offset)


def _is_external(target: str) -> bool:
    parsed = urlsplit(target)
    return (
        not target
        or target.startswith("#")
        or target.startswith("//")
        or bool(parsed.scheme)
    )


def _resolve_target(markdown_path: Path, target: str) -> Path | None:
    target = html.unescape(target).strip()
    if _is_external(target):
        return None
    parsed = urlsplit(target)
    decoded_path = unquote(parsed.path)
    if not decoded_path:
        return None
    return (markdown_path.parent / decoded_path).resolve()


def _markdown_files(inputs: list[str]) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    errors: list[str] = []
    for value in inputs:
        path = Path(value)
        if path.is_dir():
            files.extend(sorted(item for item in path.rglob("*.md") if item.is_file()))
        elif path.is_file():
            files.append(path)
        else:
            errors.append(f"error: Markdown file or directory does not exist: {value}")
    return files, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check local Markdown and HTML image references."
    )
    parser.add_argument("markdown", nargs="+", help="Markdown files or directories to check")
    args = parser.parse_args(argv)

    files, errors = _markdown_files(args.markdown)
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 2

    missing = 0
    checked = 0
    skipped = 0
    for markdown_path in files:
        try:
            content = markdown_path.read_text(encoding="utf-8")
        except OSError as error:
            print(f"error: cannot read {markdown_path}: {error}", file=sys.stderr)
            return 2
        references = _extract_references(str(markdown_path), content)
        for reference in references:
            target = html.unescape(reference.target).strip()
            resolved = _resolve_target(markdown_path, target)
            if resolved is None:
                skipped += 1
                continue
            checked += 1
            if resolved.is_file():
                print(f"OK      {reference.source}:{reference.line} {reference.kind} -> {target}")
            else:
                missing += 1
                print(
                    f"MISSING {reference.source}:{reference.line} {reference.kind} -> "
                    f"{target} (resolved: {resolved})"
                )

    print(f"Checked {checked} local image reference(s); skipped {skipped} external reference(s).")
    if missing:
        print(f"Found {missing} missing local image reference(s).", file=sys.stderr)
        return 1
    print("All local image references exist.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
