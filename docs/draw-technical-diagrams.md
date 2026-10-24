# Technical Diagrams

[简体中文](draw-technical-diagrams.zh-CN.md) · [Repository README](../README.md) · [Skill instructions](../skills/draw-technical-diagrams/SKILL.md)

Use `draw-technical-diagrams` to create or revise flowcharts, system architecture diagrams, component diagrams, and data-flow diagrams from prose, code, or an existing sketch.

## What to provide

- For an existing image, screenshot, or sketch, say that it is the source of truth. The result should be a faithful redraw that preserves observable nodes, labels, groups, edges, and approximate geometry.
- For a new diagram, describe the components, ownership boundaries, directed relationships, branch conditions, timing or waiting states, and events that must remain distinct.
- State the desired output format, target document or article width, and whether the editable source should be delivered.

The skill distinguishes faithful redraw from semantic-first creation. See the [skill instructions](../skills/draw-technical-diagrams/SKILL.md) for the execution rules and layout guidance.

## Outputs and dependencies

The editable source is `.mmd` for Mermaid or `.svg` for a directly authored layout. Mermaid can produce PNG, SVG, or PDF. When a directly authored SVG has relationships Mermaid can express faithfully, the skill also keeps a companion `.mmd` logical model.

| Path | Requirements |
| --- | --- |
| Mermaid | Bash, Node.js/`npx`, and headless Chrome/Chromium; the first render may download the pinned Mermaid CLI |
| Direct SVG | No Mermaid runtime; an SVG viewer or renderer is needed for visual review and PNG export |

Mermaid rendering uses [`render-mermaid.sh`](../skills/draw-technical-diagrams/scripts/render-mermaid.sh). If Mermaid cannot run in the environment or its result is unsuitable, the skill can use direct SVG and report any unavailable preview or export.

## Examples

For a new flow:

```text
Use $draw-technical-diagrams to draw this order flow:

Submit order -> validate -> save to database -> return success.
Return an error when validation fails.

Export a white-background PNG and keep the editable source.
```

For an architecture diagram:

```text
Read the current project and draw its system architecture.
Separate the API, application service, message broker, consumer, and database
into their ownership boundaries. Show request and registration paths clearly.
Keep the editable source and export a white-background PNG for an article.
```

## Checks and failures

Run the bundled structural checks before visual review:

```bash
python3 <skill-dir>/scripts/validate-svg.py diagram.svg --strict
python3 <skill-dir>/scripts/check-markdown-diagrams.py README.md
```

The checks catch malformed or structurally unsafe SVG and broken local Markdown or HTML image links. They do not replace opening the rendered image: inspect clipping, text overlap, arrow endpoints, branch readability, and the final aspect ratio. If a viewer or rasterizer is unavailable, report the preview or export as unverified.

When a Mermaid dependency, browser, or download is blocked, switch to direct SVG rather than making environment setup a prerequisite. When Mermaid renders poorly, revise the SVG layout directly and preserve any requested logical source.
