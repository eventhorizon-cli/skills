---
name: draw-technical-diagrams
description: Create and revise technical flowcharts, system architecture diagrams, component diagrams, and data-flow diagrams from prose, code, or an existing sketch. Use when asked to draw a flowchart or architecture diagram, convert Mermaid to a white-background PNG/SVG, embed a diagram in technical documentation, or fix a diagram that is too tall, too wide, clipped, blank, or overlapping.
---

# Draw Technical Diagrams

Create clear, visually compelling technical diagrams, preferring directly authored SVG for control over layout, typography, and routing. Choose the visual form that communicates the subject most naturally; do not force every concept into a conventional flowchart. Mermaid is an optional logical model or rendering tool when it better fits the request. Favor beauty, expressive clarity, and semantic accuracy together over a repetitive box-and-arrow style.

## Choose the work mode

Choose one mode before changing a diagram:

- **Faithful redraw** applies when an existing image, screenshot, or hand-drawn sketch is the source of truth. Inspect the source at full size, record its nodes, edges, labels, grouping, and approximate geometry, then reproduce that structure as editable SVG. Preserve the original image unless the user explicitly asks to replace it. Do not redesign the topology or rename labels as part of vectorization.
- **Semantic-first creation** applies when there is no existing image to preserve. Extract a small diagram contract from the source material before drawing: node names and ownership, directed edges, branch conditions, timing or waiting states, and any event that must not be implied as a write. Use that contract to choose the layout and review the final SVG or Mermaid source.

Do not silently switch between these modes. If an existing diagram is ambiguous, preserve the observable structure and call out the uncertainty instead of inventing a new relationship.

## Workflow

1. Inspect the source material and destination document. Preserve component names, directions, protocol boundaries, and control/data-path distinctions.
2. Select **Faithful redraw** or **Semantic-first creation**, then write down the topology contract before drawing. For a new diagram, keep the contract in a short adjacent note or an optional `.mmd` logical model so later edits can be checked against it.
3. Choose the visual form that best explains the concept and plan its SVG layout (see **Choose Mermaid or SVG**). Consider timelines, annotated state transitions, memory/reference maps, layered views, comparisons, sequences, and flowcharts as appropriate; combine visual forms when this improves comprehension. Use visual hierarchy, grouping, typography, and color to make the graphic attractive and immediately understandable. Split unrelated concerns instead of crowding one image.
4. Read [layout-patterns.md](references/layout-patterns.md) when selecting layout, styling architecture roles, or fixing an awkward render.
5. Write an editable `.svg` next to the output image unless the user requests a temporary artifact. A companion `.mmd` is optional unless the user explicitly requests Mermaid or it substantially aids review of the topology.
6. Render Mermaid with `scripts/render-mermaid.sh`; render directly authored SVG as described under **Direct SVG**.
7. Run the static checks in [Static checks](#static-checks) before visual review.
8. Inspect dimensions and open the output image. If Mermaid's layout or visual quality is poor, switch directly to SVG. Inspect and revise the final render until labels, arrows, and groups are readable without clipping or overlap.
9. Run the Markdown image-link check when embedding the image in documentation, then embed it with a relative path.

## Choose Mermaid or SVG

- Start directly with SVG by default, including standard flows and sequences, so labels, spacing, routing, and visual hierarchy can be designed for the actual content. No Mermaid trial is required.
- Use Mermaid as an optional logical record, or as a rendering tool when automatic layout better serves a simple diagram or the user requests it. An `.mmd` logical record is not a substitute for reviewing the SVG topology.
- If a Mermaid render has poor balance, an unsuitable aspect ratio, overlapping or cramped labels, confusing crossings, or arrows that appear to terminate on group borders, switch directly to SVG. Do not require multiple Mermaid revision rounds or add invisible nodes and fragile ordering constraints to force the layout.
- Respect an explicit user requirement for Mermaid source or a particular format. If SVG supplies the visual layout, retain any requested Mermaid source as the logical model.

## Layout Rules

- Prefer left-to-right reading for architecture and data-flow diagrams when it fits the material; choose another arrangement when it communicates the structure more clearly or creates a better-balanced graphic.
- Use top-to-bottom reading (`TB` in Mermaid) only for short, naturally vertical processes or explicitly portrait output.
- Prefer blog diagrams between roughly `1.4:1` and `3:1`. Allow up to `4.5:1` when parallel paths remain clearer in one band; otherwise split or regroup the graph. Reject a portrait result whose height exceeds `1.35` times its width unless portrait was requested.
- Keep labels short. Break long labels with `<br/>` in Mermaid or positioned `<tspan>` elements in SVG rather than widening every node.
- Use groups (`subgraph` in Mermaid) for real ownership or deployment boundaries, not as decorative containers.
- Use solid arrows for primary requests or data flow and dashed arrows for discovery, registration, heartbeats, or other control-plane traffic.
- Avoid crossing arrows. Duplicate a stateless gateway node when doing so materially improves two separate paths, and label the duplicate consistently.
- Choose straight lines, curves, arcs, or a combination according to the relationship and visual composition. Use smooth curves proactively when they improve the reading flow, grouping, or routing; do not constrain SVG diagrams to orthogonal connectors. Keep arrow direction and endpoints unambiguous, and avoid decorative curves that obscure relationships.
- Treat subgraphs as visual boundaries, not flow endpoints. Every semantic edge must terminate on a concrete node inside the boundary; an arrow that appears to stop at a subgraph border is a failed layout.
- Keep branch ownership visible. Success, failure, timeout, and cancellation edges must visibly originate from the node that makes or observes that result, rather than from a nearby gateway or an ambiguous point on a container.
- Separate terminal paths from recovery paths. A success edge must reach an explicit terminal or acknowledged state and must not visually merge into retry or recovery flow before that distinction is shown.
- Do not draw the absence of an event as if it were a write operation. For example, represent a missing ACK with a note or waiting state, not an arrow that implies a failure record was written.
- Route cross-section edges around section titles, node labels, and edge labels. Curves must not cross unrelated nodes or text.
- In sequence diagrams, keep meaningful intermediate lifelines visible. When a horizontal message label crosses one or more of them, give the label an opaque white backing or a sufficiently wide white text halo so the lifelines do not pass through the glyphs. This is a readability treatment for message labels, not a substitute for routing a real flowchart edge around unrelated content.
- Do not add a title inside the image when the surrounding document already supplies a caption or heading.

## Visual Style

- Render on a white background.
- For Mermaid, use the shared configuration in `assets/mermaid.config.json`; apply the same palette and typography to directly authored SVG.
- Use a quiet multi-color semantic palette: green for clients, blue for gateways, gray for core services, yellow for storage, purple for handlers, and red only for failures.
- Avoid visual effects or ornamental shapes that compete with meaning; use visual styling deliberately to improve hierarchy, clarity, and aesthetic quality.
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

Supported Mermaid CLI outputs are PNG, SVG, and PDF. PNG defaults to `4×` rendering for high-resolution publishing. Prefer SVG when the destination supports it; export PNG when the destination requires or benefits from a raster image.

The script pins Mermaid CLI `11.12.0`. Its first invocation can require a package download. If the environment cannot download dependencies or launch headless Chrome, switch to direct SVG or another available trusted renderer and report that the preview could not be rendered. Do not make an environment-specific install or elevated execution a prerequisite for finishing the diagram.

## Static checks

Use the bundled checks before opening the rendered image:

```bash
python3 <skill-dir>/scripts/validate-svg.py diagram.svg --strict
python3 <skill-dir>/scripts/check-markdown-diagrams.py README.md
```

`validate-svg.py` catches malformed SVG, missing viewBox or white background, text without a stable position, unresolved markers, and accidental duplicate path geometry. `check-markdown-diagrams.py` catches broken local Markdown and HTML image links. These checks are fast structural gates; they do not replace visual inspection of routing, spacing, or semantic meaning.

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
- Inspect every rendered image at its intended article width and at full size, following every connector, arrowhead, lifeline, divider, and grid line past every text label. Any line crossing, touching, underlining, or passing behind unrelated text is a defect even when the SVG passes structural validation. Reposition the label or reroute the line, then render and inspect the corrected image again; use an opaque label backing only when it preserves a clear, unambiguous connection. Do not infer visual cleanliness from a thumbnail or a successful render.
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

Do not report completion until the rendered file, not only the Mermaid syntax, has passed these checks. If no SVG viewer or rasterizer is available, report the unverified preview explicitly instead of claiming visual verification.

## Direct SVG

Author the layout directly in SVG by default. Exporting Mermaid's existing layout as SVG does not fix its layout problems.

- Use a stable `viewBox`, an explicit white background, and explicit node and label positions. Size nodes around their text and safe content areas.
- Give every path an explicit start point, end point, and non-overlapping route. Place arrowheads on the intended node boundary and keep lines clear of unrelated labels and group headings.
- Keep the `.svg` as the editable visual source. Preserve an existing `.mmd` as a logical model when switching from Mermaid. Create a companion `.mmd` only when requested or when it materially helps review the relationships.
- Deliver SVG when the destination supports it or the user requests it. When PNG is needed, rasterize the SVG with an available trusted renderer on a white background at sufficient resolution for the destination.
- Visually inspect the final SVG or its rasterized preview, and any delivered PNG, using the same verification checks above. Valid SVG syntax or a passing static check alone is not sufficient.

## Bilingual diagrams

When both English and Simplified Chinese are requested, keep the two sources isomorphic: the same node identifiers, edge directions, branch conditions, and visual positions must appear in both versions. Translate labels and explanatory notes only. Run the static SVG and Markdown checks for both language variants.
