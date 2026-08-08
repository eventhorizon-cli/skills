---
name: draw-technical-diagrams
description: Create and revise technical flowcharts, system architecture diagrams, component diagrams, and data-flow diagrams from prose, code, or an existing sketch. Use when asked to draw a flowchart or architecture diagram, convert Mermaid to a white-background PNG/SVG, embed a diagram in technical documentation, or fix a diagram that is too tall, too wide, clipped, blank, or overlapping.
---

# Draw Technical Diagrams

Create readable technical diagrams as Mermaid source plus a rendered image. Prefer restrained, documentation-oriented visuals over decorative illustrations.

## Workflow

1. Inspect the source material and destination document. Preserve component names, directions, protocol boundaries, and control/data-path distinctions.
2. Choose the smallest diagram type that explains the relationship:
   - Use `flowchart` for architecture, components, message paths, and operational flows.
   - Use `sequenceDiagram` only when request order or timing is the main point.
   - Split unrelated concerns into separate diagrams instead of crowding one image.
3. Read [layout-patterns.md](references/layout-patterns.md) when selecting layout, styling architecture roles, or fixing an awkward render.
4. Write a `.mmd` source file next to the output image unless the user requests a temporary artifact.
5. Render with `scripts/render-mermaid.sh`.
6. Inspect dimensions and open the output image. Revise and re-render until labels, arrows, and groups are readable without clipping or overlap.
7. Embed the image with a relative path when editing a local Markdown document.

## Layout Rules

- Default architecture and data-flow diagrams to `LR`.
- Use `TB` only for short, naturally vertical processes or explicitly portrait output.
- Prefer blog diagrams between roughly `1.4:1` and `3:1`. Allow up to `4.5:1` when parallel paths remain clearer in one band; otherwise split or regroup the graph. Reject a portrait result whose height exceeds `1.35` times its width unless portrait was requested.
- Keep labels short. Break long labels with `<br/>` rather than widening every node.
- Use subgraphs for real ownership or deployment boundaries, not as decorative containers.
- Use solid arrows for primary requests or data flow and dashed arrows for discovery, registration, heartbeats, or other control-plane traffic.
- Avoid crossing arrows. Duplicate a stateless gateway node when doing so materially improves two separate paths, and label the duplicate consistently.
- Treat subgraphs as visual boundaries, not flow endpoints. Every semantic edge must terminate on a concrete node inside the boundary; an arrow that appears to stop at a subgraph border is a failed layout.
- Keep branch ownership visible. Success, failure, timeout, and cancellation edges must visibly originate from the node that makes or observes that result, rather than from a nearby gateway or an ambiguous point on a container.
- Separate terminal paths from recovery paths. A success edge must reach an explicit terminal or acknowledged state and must not visually merge into retry or recovery flow before that distinction is shown.
- Do not draw the absence of an event as if it were a write operation. For example, represent a missing ACK with a note or waiting state, not an arrow that implies a failure record was written.
- Route cross-section edges around section titles, node labels, and edge labels. Curves are acceptable when they make the source and destination clearer, but they must not cross unrelated nodes or text.
- Do not add a title inside the image when the surrounding document already supplies a caption or heading.

## Visual Style

- Render on a white background.
- Use the shared configuration in `assets/mermaid.config.json`.
- Use a quiet multi-color semantic palette: green for clients, blue for gateways, gray for core services, yellow for storage, purple for handlers, and red only for failures.
- Avoid gradients, shadows, ornamental shapes, and excessive rounded corners.
- Keep edge labels and node text at a readable size after the image is scaled to the target document width.
- Size every node from its rendered text and its shape's safe content area, not from a fixed default or the outer bounding box alone. Curves, angled sides, icons, headers, and other internal geometry reduce the space available for labels.
- Multi-line labels need visible padding on all sides after rendering. Increase the node dimensions before reducing the font size when the content area feels cramped.

## Render

Run:

```bash
<skill-dir>/scripts/render-mermaid.sh input.mmd output.png
```

Optional arguments set logical width and render scale:

```bash
<skill-dir>/scripts/render-mermaid.sh input.mmd output.png 2000 4
```

Supported Mermaid CLI outputs are PNG, SVG, and PDF. PNG defaults to `4×` rendering for high-resolution publishing. Prefer PNG for blogs and general publishing, and keep or additionally export SVG when the destination supports vectors and maximum scalability matters.

The script pins Mermaid CLI `11.12.0`. Its first invocation can require package download and network approval. If headless Chrome is blocked by the execution sandbox, request permission to rerun the same render command outside the sandbox; do not silently switch to an unverified renderer.

## Verify

Check dimensions with an available native tool:

```bash
sips -g pixelWidth -g pixelHeight output.png
```

or:

```bash
identify output.png
```

Then visually inspect the actual image, preferably with `view_image`. Confirm all of the following:

- The canvas is not blank and the background is white.
- No node, label, arrowhead, or border is clipped.
- Text does not overlap arrows or adjacent nodes.
- No node border, curve, angled edge, icon, divider, or decorative geometry crosses, touches, underlines, or passes behind its own label.
- Multi-line labels have balanced top and bottom padding at normal article width; a technically non-overlapping but visually cramped node still fails verification.
- Every arrow visibly starts at its intended source node and its arrowhead visibly lands on the intended destination node, not on a section border or empty space.
- Decision branches remain distinguishable from source to destination; labels such as success, failure, timeout, and retry cannot be mistaken for a neighboring edge.
- Container borders and section headings do not interrupt, hide, or appear to terminate a line.
- The rendered routing matches the intended semantics. In particular, success does not flow into retry, and timeout/no-response is not depicted as an explicit response or write.
- The reading direction is obvious without explanatory prose inside the image.
- The aspect ratio is appropriate for both desktop and mobile article widths.
- The image mode has no unwanted transparency when PNG was requested for publishing.

Do not report completion until the rendered file, not only the Mermaid syntax, has passed these checks.

## Fallback

If Mermaid cannot produce a balanced layout after two focused revisions, or if it repeatedly attaches cross-subgraph edges to container borders, create an explicit SVG with a stable `viewBox`. Give every path an explicit start point, end point, and non-overlapping route, then rasterize it to a white-background PNG using an available trusted renderer.

Preserve the `.mmd` file as the machine-readable record of logical relationships, keep the explicit `.svg` as the stable visual layout source, and publish the rendered `.png`. Apply the same source/destination, label-overlap, background, clipping, and aspect-ratio checks to the final PNG.
