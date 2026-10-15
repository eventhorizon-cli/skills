---
name: draw-technical-diagrams
description: Create and revise technical flowcharts, system architecture diagrams, component diagrams, and data-flow diagrams from prose, code, or an existing sketch. Use when asked to draw a flowchart or architecture diagram, convert Mermaid to a white-background PNG/SVG, embed a diagram in technical documentation, or fix a diagram that is too tall, too wide, clipped, blank, or overlapping.
---

# Draw Technical Diagrams

Create readable technical diagrams with Mermaid or directly authored SVG, choosing the tool that produces the clearest result. Prefer restrained, documentation-oriented visuals over decorative illustrations.

## Workflow

1. Inspect the source material and destination document. Preserve component names, directions, protocol boundaries, and control/data-path distinctions.
2. Choose the smallest diagram type that explains the relationship and assess whether Mermaid suits its layout and the available environment (see **Choose Mermaid or SVG**):
   - Use a flowchart for architecture, components, message paths, and operational flows.
   - Use a sequence diagram only when request order or timing is the main point.
   - Split unrelated concerns into separate diagrams instead of crowding one image.
3. Read [layout-patterns.md](references/layout-patterns.md) when selecting layout, styling architecture roles, or fixing an awkward render.
4. Write a `.mmd` source for Mermaid, or an explicit `.svg` for direct SVG, next to the output image unless the user requests a temporary artifact.
5. Render Mermaid with `scripts/render-mermaid.sh`; render directly authored SVG as described under **Direct SVG**.
6. Inspect dimensions and open the output image. If Mermaid's layout or visual quality is poor, switch directly to SVG. Inspect and revise the final render until labels, arrows, and groups are readable without clipping or overlap.
7. Embed the image with a relative path when editing a local Markdown document.

## Choose Mermaid or SVG

- Use Mermaid for standard flows and sequences when automatic layout can express the relationships clearly.
- Consider the runtime as well as the layout. If Node.js is unavailable and no working Mermaid renderer is already available, start directly with SVG. If Node.js is available, a single lightweight Mermaid render attempt is reasonable; a normal first-use `npx` download is acceptable when network access permits. A known environment blocker does not need another trial.
- If the attempt is blocked by a missing browser, failed dependency download, incompatible runtime, or sandbox restrictions, switch directly to SVG. Do not make installing a toolchain, repeated retries, or requesting elevated execution a prerequisite for finishing the diagram. Troubleshoot Mermaid setup when the user explicitly requests it or requires Mermaid rendering.
- Start directly with SVG when the diagram needs precise placement, fixed alignment, custom shapes, dense cross-group connections, or controlled routing that Mermaid is unlikely to handle cleanly. No Mermaid trial is required.
- If a Mermaid render has poor balance, an unsuitable aspect ratio, overlapping or cramped labels, confusing crossings, or arrows that appear to terminate on group borders, switch directly to SVG. Do not require multiple Mermaid revision rounds or add invisible nodes and fragile ordering constraints to force the layout.
- Respect an explicit user requirement for Mermaid source or a particular format. If SVG supplies the visual layout, retain any requested Mermaid source as the logical model.

## Layout Rules

- Default architecture and data-flow diagrams to left-to-right reading (`LR` in Mermaid).
- Use top-to-bottom reading (`TB` in Mermaid) only for short, naturally vertical processes or explicitly portrait output.
- Prefer blog diagrams between roughly `1.4:1` and `3:1`. Allow up to `4.5:1` when parallel paths remain clearer in one band; otherwise split or regroup the graph. Reject a portrait result whose height exceeds `1.35` times its width unless portrait was requested.
- Keep labels short. Break long labels with `<br/>` in Mermaid or positioned `<tspan>` elements in SVG rather than widening every node.
- Use groups (`subgraph` in Mermaid) for real ownership or deployment boundaries, not as decorative containers.
- Use solid arrows for primary requests or data flow and dashed arrows for discovery, registration, heartbeats, or other control-plane traffic.
- Avoid crossing arrows. Duplicate a stateless gateway node when doing so materially improves two separate paths, and label the duplicate consistently.
- Treat subgraphs as visual boundaries, not flow endpoints. Every semantic edge must terminate on a concrete node inside the boundary; an arrow that appears to stop at a subgraph border is a failed layout.
- Keep branch ownership visible. Success, failure, timeout, and cancellation edges must visibly originate from the node that makes or observes that result, rather than from a nearby gateway or an ambiguous point on a container.
- Separate terminal paths from recovery paths. A success edge must reach an explicit terminal or acknowledged state and must not visually merge into retry or recovery flow before that distinction is shown.
- Do not draw the absence of an event as if it were a write operation. For example, represent a missing ACK with a note or waiting state, not an arrow that implies a failure record was written.
- Route cross-section edges around section titles, node labels, and edge labels. Curves are acceptable when they make the source and destination clearer, but they must not cross unrelated nodes or text.
- In sequence diagrams, keep meaningful intermediate lifelines visible. When a horizontal message label crosses one or more of them, give the label an opaque white backing or a sufficiently wide white text halo so the lifelines do not pass through the glyphs. This is a readability treatment for message labels, not a substitute for routing a real flowchart edge around unrelated content.
- Do not add a title inside the image when the surrounding document already supplies a caption or heading.

## Visual Style

- Render on a white background.
- For Mermaid, use the shared configuration in `assets/mermaid.config.json`; apply the same palette and typography to directly authored SVG.
- Use a quiet multi-color semantic palette: green for clients, blue for gateways, gray for core services, yellow for storage, purple for handlers, and red only for failures.
- Avoid gradients, shadows, ornamental shapes, and excessive rounded corners.
- Keep edge labels and node text at a readable size after the image is scaled to the target document width.
- Size every node from its rendered text and its shape's safe content area, not from a fixed default or the outer bounding box alone. Curves, angled sides, icons, headers, and other internal geometry reduce the space available for labels.
- Multi-line labels need visible padding on all sides after rendering. Increase the node dimensions before reducing the font size when the content area feels cramped.

## Render Mermaid

Run:

```bash
<skill-dir>/scripts/render-mermaid.sh input.mmd output.png
```

Optional arguments set logical width and render scale:

```bash
<skill-dir>/scripts/render-mermaid.sh input.mmd output.png 2000 4
```

Supported Mermaid CLI outputs are PNG, SVG, and PDF. PNG defaults to `4×` rendering for high-resolution publishing. Prefer PNG for blogs and general publishing, and keep or additionally export SVG when the destination supports vectors and maximum scalability matters.

The script pins Mermaid CLI `11.12.0`. Its first invocation can require a package download. With Node.js available, try it once if the current environment permits; if downloading dependencies or launching headless Chrome is blocked, follow the SVG path instead of automatically requesting elevated execution. Use an available trusted SVG renderer and verify its output.

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
- Sequence-diagram message labels that cross intermediate lifelines have an opaque white backing or white halo, and the retained lifelines remain understandable on either side of the label.
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

## Direct SVG

Author the layout directly in SVG when selected upfront, when the environment cannot run Mermaid, or when Mermaid's result is poor. Exporting Mermaid's existing layout as SVG does not fix its layout problems.

- Use a stable `viewBox`, an explicit white background, and explicit node and label positions. Size nodes around their text and safe content areas.
- Give every path an explicit start point, end point, and non-overlapping route. Place arrowheads on the intended node boundary and keep lines clear of unrelated labels and group headings.
- Keep the `.svg` as the editable visual source. Preserve an existing `.mmd` as the logical model when switching from Mermaid; do not create one solely to accompany a diagram authored directly in SVG unless requested.
- Deliver SVG when the destination supports it or the user requests it. When PNG is needed, rasterize the SVG with an available trusted renderer on a white background at sufficient resolution for the destination.
- Direct SVG authoring does not need Node.js, Mermaid CLI, or headless Chrome, but visual inspection and PNG export still need a working SVG viewer or renderer. If none is available, keep the SVG source and clearly report the unverified preview or unavailable export; do not claim verification or substitute SVG for an explicitly required PNG without explaining the limitation.
- Visually inspect the final SVG or its rasterized preview, and any delivered PNG, using the same verification checks above. Valid SVG syntax alone is not sufficient.
