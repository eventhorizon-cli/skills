#!/usr/bin/env python3
"""Run lightweight, dependency-free checks on authored SVG diagrams.

The validator intentionally checks the parts of an SVG that are easy to get
wrong in documentation diagrams: canvas metadata, a visible white canvas,
text placement, marker references, and accidentally duplicated paths.  It is
not a renderer and cannot replace visual inspection of the final image.
"""

from __future__ import annotations

import argparse
import math
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
NUMBER_RE = re.compile(NUMBER)
TOKEN_RE = re.compile(rf"[A-Za-z]|{NUMBER}")
URL_RE = re.compile(r"url\(\s*[\"']?#([^\s)\"']+)[\"']?\s*\)")
WHITE_VALUES = {
    "white",
    "#fff",
    "#ffffff",
    "rgb(255,255,255)",
    "rgb(255, 255, 255)",
}
NORMALIZED_WHITE_VALUES = {re.sub(r"\s+", "", item) for item in WHITE_VALUES}


def local_name(tag: str) -> str:
    """Return an XML tag's local name, ignoring an optional namespace."""

    return tag.rsplit("}", 1)[-1]


def parse_numbers(value: str | None) -> list[float] | None:
    if value is None:
        return None
    numbers: list[float] = []
    position = 0
    while position < len(value):
        while position < len(value) and value[position] in " ,\t\r\n":
            position += 1
        if position == len(value):
            break
        match = NUMBER_RE.match(value, position)
        if match is None:
            return None
        try:
            number = float(match.group(0))
        except ValueError:
            return None
        if not math.isfinite(number):
            return None
        numbers.append(number)
        position = match.end()
        if position < len(value) and value[position] == "%":
            position += 1
    return numbers


def parse_scalar(value: str | None) -> float | None:
    numbers = parse_numbers(value)
    if numbers is None or len(numbers) != 1:
        return None
    return numbers[0]


def style_value(element: ET.Element, name: str) -> str | None:
    direct = element.attrib.get(name)
    if direct is not None:
        return direct.strip()
    style = element.attrib.get("style", "")
    for declaration in style.split(";"):
        if ":" not in declaration:
            continue
        key, value = declaration.split(":", 1)
        if key.strip().lower() == name:
            return value.strip()
    return None


def is_white(value: str | None) -> bool:
    if value is None:
        return False
    normalized = re.sub(r"\s+", "", value.strip().lower())
    return normalized in NORMALIZED_WHITE_VALUES


def is_visible(element: ET.Element) -> bool:
    """Return false for elements explicitly made fully transparent."""

    for attribute in ("opacity", "fill-opacity"):
        value = parse_scalar(style_value(element, attribute))
        if value is not None and value <= 0:
            return False
    return True


def element_label(element: ET.Element, fallback: str) -> str:
    identifier = element.attrib.get("id")
    return f"#{identifier}" if identifier else fallback


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    message: str
    node: str | None = None


class SvgValidator:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.issues: list[Issue] = []

    def issue(self, severity: str, code: str, message: str, node: str | None = None) -> None:
        self.issues.append(Issue(severity, code, message, node))

    def validate(self) -> list[Issue]:
        if not self.path.is_file():
            self.issue("error", "file", "file does not exist")
            return self.issues

        try:
            tree = ET.parse(self.path)
        except (ET.ParseError, OSError) as exc:
            self.issue("error", "xml", f"cannot parse SVG: {exc}")
            return self.issues

        root = tree.getroot()
        if local_name(root.tag) != "svg":
            self.issue("error", "root", f"root element must be <svg>, got <{local_name(root.tag)}>")
            return self.issues

        self.check_ids(root)
        view_box = self.check_canvas(root)
        self.check_background(root, view_box)
        self.check_text_coordinates(root)
        self.check_markers(root)
        self.check_duplicate_paths(root)
        return self.issues

    def check_ids(self, root: ET.Element) -> None:
        seen: dict[str, int] = {}
        for element in root.iter():
            identifier = element.attrib.get("id")
            if not identifier:
                continue
            seen[identifier] = seen.get(identifier, 0) + 1
        for identifier, count in seen.items():
            if count > 1:
                self.issue("error", "duplicate-id", f"id '{identifier}' occurs {count} times")

    def check_canvas(self, root: ET.Element) -> tuple[float, float, float, float] | None:
        raw_view_box = root.attrib.get("viewBox")
        values = parse_numbers(raw_view_box)
        if raw_view_box is None:
            self.issue("error", "viewbox-missing", "root <svg> must declare a viewBox")
            view_box = None
        elif values is None or len(values) != 4:
            self.issue("error", "viewbox-invalid", "viewBox must contain exactly four numbers")
            view_box = None
        elif values[2] <= 0 or values[3] <= 0 or not all(math.isfinite(value) for value in values):
            self.issue("error", "viewbox-invalid", "viewBox width and height must be finite and positive")
            view_box = None
        else:
            view_box = (values[0], values[1], values[2], values[3])

        for dimension in ("width", "height"):
            value = root.attrib.get(dimension)
            if value is None:
                self.issue("warning", "dimension-missing", f"root <svg> has no explicit {dimension}")
            elif parse_scalar(value) is None:
                self.issue("warning", "dimension-invalid", f"root {dimension} is not a simple numeric length: {value!r}")
        return view_box

    def check_background(self, root: ET.Element, view_box: tuple[float, float, float, float] | None) -> None:
        if view_box is None:
            return
        if is_white(style_value(root, "background-color")) and is_visible(root):
            return
        vx, vy, vw, vh = view_box
        parent_map = {child: parent for parent in root.iter() for child in parent}
        for index, element in enumerate(root.iter()):
            if (
                local_name(element.tag) != "rect"
                or not is_white(style_value(element, "fill"))
                or not is_visible(element)
            ):
                continue
            ancestor = parent_map.get(element)
            while ancestor is not None:
                if local_name(ancestor.tag) == "defs":
                    break
                ancestor = parent_map.get(ancestor)
            else:
                ancestor = None
            if ancestor is not None:
                continue
            x = parse_scalar(element.attrib.get("x"))
            y = parse_scalar(element.attrib.get("y"))
            width = parse_scalar(element.attrib.get("width"))
            height = parse_scalar(element.attrib.get("height"))
            if x is None:
                x = 0.0
            if y is None:
                y = 0.0
            if width is None or height is None:
                continue
            if x <= vx and y <= vy and x + width >= vx + vw and y + height >= vy + vh:
                return
            self.issue(
                "warning",
                "background-too-small",
                "white background rect does not cover the full viewBox",
                element_label(element, f"rect[{index}]"),
            )
        self.issue("warning", "background-missing", "no explicit white rect covers the full viewBox")

    def check_text_coordinates(self, root: ET.Element) -> None:
        for index, element in enumerate(root.iter()):
            if local_name(element.tag) != "text":
                continue
            label = element_label(element, f"text[{index}]")
            has_transform = bool(element.attrib.get("transform"))
            x = element.attrib.get("x")
            y = element.attrib.get("y")
            if not has_transform and (x is None or y is None):
                self.issue("warning", "text-position", "text should declare both x and y coordinates (or a transform)", label)
                continue
            if x is not None and parse_numbers(x) is None:
                self.issue("error", "text-position", f"text x is not numeric: {x!r}", label)
            if y is not None and parse_numbers(y) is None:
                self.issue("error", "text-position", f"text y is not numeric: {y!r}", label)

    def check_markers(self, root: ET.Element) -> None:
        marker_ids = {element.attrib["id"] for element in root.iter() if local_name(element.tag) == "marker" and "id" in element.attrib}
        references: list[tuple[str, str, str]] = []
        marker_attributes = ("marker-start", "marker-mid", "marker-end")
        for index, element in enumerate(root.iter()):
            label = element_label(element, f"{local_name(element.tag)}[{index}]")
            for attribute in marker_attributes:
                value = style_value(element, attribute)
                if value:
                    references.extend((label, attribute, marker_id) for marker_id in URL_RE.findall(value))
        for label, attribute, marker_id in references:
            if marker_id not in marker_ids:
                self.issue("error", "marker-missing", f"{attribute} references undefined marker '{marker_id}'", label)

    def check_duplicate_paths(self, root: ET.Element) -> None:
        parent_map = {child: parent for parent in root.iter() for child in parent}
        paths: dict[tuple[tuple[str, ...], str], list[str]] = defaultdict(list)
        for index, element in enumerate(root.iter()):
            if local_name(element.tag) != "path" or not element.attrib.get("d"):
                continue
            ancestor = parent_map.get(element)
            in_defs = False
            while ancestor is not None:
                if local_name(ancestor.tag) in {"defs", "marker", "clipPath", "mask", "pattern"}:
                    in_defs = True
                    break
                ancestor = parent_map.get(ancestor)
            if in_defs:
                continue
            tokens = tuple(TOKEN_RE.findall(element.attrib["d"]))
            key = (tokens, element.attrib.get("transform", ""))
            paths[key].append(element_label(element, f"path[{index}]"))
        for labels in paths.values():
            if len(labels) > 1:
                self.issue("warning", "duplicate-path", f"same path geometry appears {len(labels)} times: {', '.join(labels)}")


def validate_paths(paths: Iterable[Path], strict: bool) -> int:
    total_errors = 0
    total_warnings = 0
    files = list(paths)
    for path in files:
        validator = SvgValidator(path)
        issues = validator.validate()
        errors = sum(issue.severity == "error" for issue in issues)
        warnings = sum(issue.severity == "warning" for issue in issues)
        total_errors += errors
        total_warnings += warnings
        for issue in issues:
            location = f" ({issue.node})" if issue.node else ""
            print(f"{path}: {issue.severity.upper()} [{issue.code}]{location}: {issue.message}")
        if not issues:
            print(f"{path}: OK")

    print(f"Validated {len(files)} SVG file(s): {total_errors} error(s), {total_warnings} warning(s)")
    return 1 if total_errors or (strict and total_warnings) else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate authored SVG diagrams without third-party dependencies.")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("svg", nargs="+", type=Path, help="SVG files to validate")
    args = parser.parse_args(argv)
    return validate_paths(args.svg, args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
