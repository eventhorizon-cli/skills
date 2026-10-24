#!/usr/bin/env python3
"""Validate the repository layout and metadata for Agent Skills.

The validator intentionally performs local, deterministic checks only.  It is
usable from a checkout (``python scripts/validate-skills.py``) or against an
isolated fixture with ``--root``.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple
from urllib.parse import unquote, urlsplit


try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised in a dependency-free checkout
    print(
        "error: missing dependency PyYAML; install dependencies with "
        "python -m pip install -r requirements-dev.txt",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc

try:
    from markdown_it import MarkdownIt
except ImportError as exc:  # pragma: no cover - exercised in a dependency-free checkout
    print(
        "error: missing dependency markdown-it-py; install dependencies with "
        "python -m pip install -r requirements-dev.txt",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_SUFFIXES = {".md", ".markdown"}
EXCLUDED_DIRS = {".git", ".hg", ".svn", ".venv", "venv", "node_modules", "__pycache__"}
REMOTE_SCHEMES = {"http", "https", "mailto", "tel", "data", "javascript"}
KNOWN_INTERFACE_FIELDS = {"display_name", "short_description", "default_prompt"}
SHORT_DESCRIPTION_MAX = 64
SKILL_NAME_MAX = 64
SKILL_DESCRIPTION_MAX = 1024


class DiagnosticCollector:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.messages: List[str] = []

    def relative(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self.root).as_posix()
        except ValueError:
            return str(path)

    def add(self, path: Path, line: int, message: str) -> None:
        self.messages.append(f"{self.relative(path)}:{max(1, line)}: {message}")

    def error(self, message: str) -> None:
        self.messages.append(message)


def line_for_yaml_error(exc: yaml.YAMLError) -> int:
    mark = getattr(exc, "problem_mark", None)
    return int(getattr(mark, "line", 0)) + 1 if mark is not None else 1


def read_text(path: Path, diagnostics: DiagnosticCollector) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        diagnostics.add(path, 1, f"must be valid UTF-8 ({exc})")
    except OSError as exc:
        diagnostics.add(path, 1, f"cannot read file ({exc})")
    return None


def parse_frontmatter(
    path: Path, text: str, diagnostics: DiagnosticCollector
) -> Optional[Mapping[str, Any]]:
    lines = text.splitlines()
    if not lines or lines[0].lstrip("\ufeff") != "---":
        diagnostics.add(path, 1, "must start with YAML frontmatter delimiter '---'")
        return None

    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() in {"---", "..."}:
            end = index
            break
    if end is None:
        diagnostics.add(path, 1, "YAML frontmatter is not closed")
        return None

    raw = "\n".join(lines[1:end])
    try:
        metadata = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        diagnostics.add(path, line_for_yaml_error(exc) + 1, f"invalid YAML frontmatter ({exc})")
        return None

    if not isinstance(metadata, Mapping):
        diagnostics.add(path, 1, "YAML frontmatter must be a mapping")
        return None
    return metadata


def validate_skill(skill_dir: Path, diagnostics: DiagnosticCollector) -> None:
    if not SKILL_NAME_RE.fullmatch(skill_dir.name):
        diagnostics.add(
            skill_dir,
            1,
            "skill directory name must contain lowercase letters, digits, and hyphens only",
        )

    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        diagnostics.add(skill_file, 1, "missing required SKILL.md")
    else:
        text = read_text(skill_file, diagnostics)
        if text is not None:
            metadata = parse_frontmatter(skill_file, text, diagnostics)
            if metadata is not None:
                name = metadata.get("name")
                description = metadata.get("description")
                if not isinstance(name, str) or not name.strip():
                    diagnostics.add(skill_file, 1, "frontmatter field 'name' must be a non-empty string")
                else:
                    if name != skill_dir.name:
                        diagnostics.add(
                            skill_file,
                            1,
                            f"frontmatter name {name!r} must match directory {skill_dir.name!r}",
                        )
                    if len(name) > SKILL_NAME_MAX:
                        diagnostics.add(
                            skill_file,
                            1,
                            f"frontmatter field 'name' must be at most {SKILL_NAME_MAX} characters",
                        )
                if not isinstance(description, str) or not description.strip():
                    diagnostics.add(
                        skill_file,
                        1,
                        "frontmatter field 'description' must be a non-empty string",
                    )
                elif len(description) > SKILL_DESCRIPTION_MAX:
                    diagnostics.add(
                        skill_file,
                        1,
                        f"frontmatter field 'description' must be at most {SKILL_DESCRIPTION_MAX} characters",
                    )

    openai_file = skill_dir / "agents" / "openai.yaml"
    if openai_file.is_file():
        validate_openai_metadata(openai_file, diagnostics)


def validate_openai_metadata(path: Path, diagnostics: DiagnosticCollector) -> None:
    text = read_text(path, diagnostics)
    if text is None:
        return
    try:
        metadata = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        diagnostics.add(path, line_for_yaml_error(exc), f"invalid YAML ({exc})")
        return

    if not isinstance(metadata, Mapping):
        diagnostics.add(path, 1, "must contain a YAML mapping")
        return
    if "interface" not in metadata:
        return
    interface = metadata["interface"]
    if not isinstance(interface, Mapping):
        diagnostics.add(path, 1, "'interface' must be a mapping when present")
        return
    skill_name = path.parents[1].name
    for field in KNOWN_INTERFACE_FIELDS:
        if field in interface and (not isinstance(interface[field], str) or not interface[field].strip()):
            diagnostics.add(path, 1, f"interface field {field!r} must be a non-empty string")
    short_description = interface.get("short_description")
    if isinstance(short_description, str) and len(short_description) > SHORT_DESCRIPTION_MAX:
        diagnostics.add(
            path,
            1,
            f"interface field 'short_description' must be at most {SHORT_DESCRIPTION_MAX} characters",
        )
    default_prompt = interface.get("default_prompt")
    if isinstance(default_prompt, str) and default_prompt.strip() and f"${skill_name}" not in default_prompt:
        diagnostics.add(
            path,
            1,
            f"interface field 'default_prompt' must mention ${skill_name}",
        )


def slugify_heading(text: str) -> str:
    # This follows GitHub's useful common case while retaining Unicode letters
    # and digits for headings in languages other than English.
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", "-", text)


class HtmlAnchorCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: Set[str] = set()
        self.links: List[Tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        values = dict(attrs)
        for key in ("id", "name"):
            value = values.get(key)
            if value:
                self.anchors.add(value)
        for key in ("href", "src"):
            value = values.get(key)
            if value:
                self.links.append((key, value))


class HtmlTextCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: List[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def token_attr(token: Any, name: str) -> Optional[str]:
    value = token.attrGet(name)
    return value if isinstance(value, str) else None


def collect_html(content: str, line: int) -> Tuple[List[Tuple[str, int]], Set[str]]:
    collector = HtmlAnchorCollector()
    collector.feed(content)
    collector.close()
    return [(value, line) for _, value in collector.links], collector.anchors


def rendered_heading_text(token: Any) -> str:
    parts: List[str] = []
    for child in token.children or []:
        if child.type in {"text", "code_inline", "softbreak", "hardbreak"}:
            parts.append(child.content)
        elif child.type == "image":
            parts.append(child.content)
        elif child.type == "html_inline":
            collector = HtmlTextCollector()
            collector.feed(child.content)
            collector.close()
            parts.extend(collector.parts)
    return "".join(parts)


def iter_markdown_links(
    path: Path, text: str
) -> Tuple[List[Tuple[str, int]], Set[str]]:
    markdown = MarkdownIt("commonmark", {"html": True})
    tokens = markdown.parse(text)
    links: List[Tuple[str, int]] = []
    anchors: Set[str] = set()
    seen_heading_slugs: Dict[str, int] = defaultdict(int)

    for token in tokens:
        if token.type == "inline" and token.children:
            line = (token.map[0] + 1) if token.map else 1
            for child in token.children:
                if child.type == "link_open":
                    href = token_attr(child, "href")
                    if href:
                        links.append((href, line))
                elif child.type == "image":
                    src = token_attr(child, "src")
                    if src:
                        links.append((src, line))
                elif child.type == "html_inline":
                    html_links, html_anchors = collect_html(child.content, line)
                    links.extend(html_links)
                    anchors.update(html_anchors)
        elif token.type == "html_block":
            html_links, html_anchors = collect_html(token.content, (token.map[0] + 1) if token.map else 1)
            links.extend(html_links)
            anchors.update(html_anchors)

    for index, token in enumerate(tokens):
        if token.type != "heading_open":
            continue
        if index + 1 >= len(tokens) or tokens[index + 1].type != "inline":
            continue
        heading = rendered_heading_text(tokens[index + 1])
        base = slugify_heading(heading)
        if not base:
            continue
        occurrence = seen_heading_slugs[base]
        seen_heading_slugs[base] += 1
        anchors.add(base if occurrence == 0 else f"{base}-{occurrence}")

    return links, anchors


def is_remote_link(destination: str) -> bool:
    parsed = urlsplit(destination)
    return parsed.scheme.lower() in REMOTE_SCHEMES or destination.startswith("//")


def resolve_local_target(root: Path, source: Path, destination: str) -> Tuple[Optional[Path], str]:
    parsed = urlsplit(destination)
    path_part = unquote(parsed.path)
    fragment = unquote(parsed.fragment)
    if path_part.startswith("/"):
        target = root / path_part.lstrip("/")
    else:
        target = source.parent / path_part
    return target.resolve(), fragment


def validate_markdown_links(
    root: Path, markdown_files: Iterable[Path], diagnostics: DiagnosticCollector
) -> None:
    anchor_cache: Dict[Path, Set[str]] = {}
    root_resolved = root.resolve()
    for path in markdown_files:
        text = read_text(path, diagnostics)
        if text is None:
            continue
        try:
            links, own_anchors = iter_markdown_links(path, text)
        except Exception as exc:
            diagnostics.add(path, 1, f"Markdown parsing failed ({exc})")
            continue
        anchor_cache[path.resolve()] = own_anchors
        for destination, line in links:
            if is_remote_link(destination):
                continue
            target, fragment = resolve_local_target(root, path, destination)
            try:
                target.relative_to(root_resolved)
            except ValueError:
                diagnostics.add(path, line, f"local link escapes repository: {destination!r}")
                continue
            if not target.exists():
                diagnostics.add(path, line, f"broken local link: {destination!r}")
                continue
            if fragment and target.suffix.lower() in MARKDOWN_SUFFIXES:
                if target not in anchor_cache:
                    target_text = read_text(target, diagnostics)
                    if target_text is None:
                        continue
                    try:
                        _, target_anchors = iter_markdown_links(target, target_text)
                    except Exception as exc:
                        diagnostics.add(target, 1, f"Markdown parsing failed ({exc})")
                        continue
                    anchor_cache[target] = target_anchors
                if fragment not in anchor_cache[target]:
                    diagnostics.add(path, line, f"broken Markdown anchor: {destination!r}")


def iter_files(root: Path, suffix: str) -> Iterable[Path]:
    for path in root.rglob(f"*{suffix}"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.is_file():
            yield path


def validate_json(root: Path, diagnostics: DiagnosticCollector) -> None:
    for path in iter_files(root, ".json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError as exc:
            diagnostics.add(path, 1, f"must be valid UTF-8 ({exc})")
        except json.JSONDecodeError as exc:
            diagnostics.add(path, exc.lineno, f"invalid JSON ({exc.msg})")
        except OSError as exc:
            diagnostics.add(path, 1, f"cannot read file ({exc})")


def validate_yaml(root: Path, diagnostics: DiagnosticCollector) -> None:
    for suffix in (".yaml", ".yml"):
        for path in iter_files(root, suffix):
            try:
                text = path.read_text(encoding="utf-8")
                list(yaml.safe_load_all(text))
            except UnicodeDecodeError as exc:
                diagnostics.add(path, 1, f"must be valid UTF-8 ({exc})")
            except yaml.YAMLError as exc:
                diagnostics.add(path, line_for_yaml_error(exc), f"invalid YAML ({exc})")
            except OSError as exc:
                diagnostics.add(path, 1, f"cannot read file ({exc})")


def validate_python(root: Path, diagnostics: DiagnosticCollector) -> None:
    for path in iter_files(root, ".py"):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except UnicodeDecodeError as exc:
            diagnostics.add(path, 1, f"must be valid UTF-8 ({exc})")
        except SyntaxError as exc:
            diagnostics.add(path, exc.lineno or 1, f"invalid Python syntax ({exc.msg})")
        except OSError as exc:
            diagnostics.add(path, 1, f"cannot read file ({exc})")


def validate_shell(root: Path, diagnostics: DiagnosticCollector) -> None:
    for path in iter_files(root, ".sh"):
        try:
            result = subprocess.run(
                ["bash", "-n", str(path)],
                cwd=str(root),
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            diagnostics.add(path, 1, "cannot run bash -n: bash is not installed")
            continue
        if result.returncode != 0:
            detail = (result.stderr.strip() or result.stdout.strip() or "syntax check failed").splitlines()[0]
            match = re.search(r": line (\d+):", detail)
            line = int(match.group(1)) if match else 1
            diagnostics.add(path, line, f"invalid shell syntax ({detail})")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        help="repository root to validate (defaults to the parent of this script's directory)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    script_root = Path(__file__).resolve().parent.parent
    root = (args.root or script_root).resolve()
    diagnostics = DiagnosticCollector(root)
    if not root.is_dir():
        print(f"error: repository root does not exist: {root}", file=sys.stderr)
        return 2

    skills_root = root / "skills"
    if not skills_root.is_dir():
        diagnostics.add(skills_root, 1, "missing required skills/ directory")
    else:
        skill_dirs = sorted(path for path in skills_root.iterdir() if path.is_dir() and not path.name.startswith("."))
        if not skill_dirs:
            diagnostics.add(skills_root, 1, "skills/ must contain at least one skill directory")
        for skill_dir in skill_dirs:
            validate_skill(skill_dir, diagnostics)

    markdown_files = sorted(iter_files(root, ".md"))
    validate_markdown_links(root, markdown_files, diagnostics)
    validate_json(root, diagnostics)
    validate_yaml(root, diagnostics)
    validate_python(root, diagnostics)
    validate_shell(root, diagnostics)

    if diagnostics.messages:
        for message in diagnostics.messages:
            print(f"error: {message}", file=sys.stderr)
        print(f"Validation failed with {len(diagnostics.messages)} error(s).", file=sys.stderr)
        return 1
    print(f"Validation passed: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
