---
name: render-technical-animations
description: Create or revise technical architecture, request-flow, concurrency, and state-transition animations as self-contained animated SVGs for READMEs and documentation. SVG is the default deliverable; export GIF only when the user explicitly requests it. Supports optional HTML playback controls and deterministic GIF rendering. Use for technical explanatory animations; use a static diagram workflow when no animation is needed.
---

# Render Technical Animations

Create readable technical animations whose states match the system being explained. Default to a self-contained animated `.svg`: it is both the editable source and the deliverable. Do not generate GIFs unless the user explicitly asks for GIF. HTML is optional for interactive demonstrations, not a required intermediate for SVG.

Keep rendering tools and dependencies in this skill or its cache. Keep requested assets and any reusable scene sources in the target repository; inspection screenshots and disposable exports belong in temporary storage.

## Default: animated SVG

1. Read the relevant code/design and destination document. Establish names, ownership, event triggers, concurrency limits, and completion semantics. Distinguish illustrative timing from real waits or ordering guarantees.
2. Read [SVG authoring and verification](references/svg-animation.md). Start from [scene.svg](assets/svg-animation/scene.svg) when useful, or adapt an existing SVG. Replace example nodes, transitions, narration, and timing with the actual scenario.
3. Author native SVG geometry and internal CSS/SMIL animation directly. Use one explicit cycle and synchronize movement, states, counters, and narration. Include a stable `viewBox`, a white background, accessible labels, and a meaningful reduced-motion still. SVGs embedded as images must work without scripts, external resources, or HTML layout.
4. Translate visible and accessible labels for requested languages into separate SVGs with the same geometry and timeline. Inspect busy scenes and long labels at the intended document width. Keep arrows clear of text.
5. Validate XML, IDs, references, and timing; then inspect the SVG in a browser at meaningful timestamps and across the loop boundary. Also load it as an `<img>` and check actual playback and reduced-motion behavior. Fix clipping, overlap, and mismatched states before delivery. Embed the SVG using the destination's image-path convention.

The SVG is the output; there is no mandatory HTML page, screenshot-to-vector conversion, or frame encoder. Do not put bitmap frames inside an SVG to simulate vector animation. Do not automatically create PNG or GIF companions; honor explicit requests and applicable repository requirements.

## Optional: HTML interaction

When the user asks for pause/replay controls, seeking, speed changes, language switching, or parameter exploration, retain or create an HTML demonstration. Read [HTML style](references/html-style.md) and [the player API](references/player-api.md); the [HTML starter](assets/technical-animation/) remains available.

For an existing HTML/JS scene, preserve its design and derive a native SVG timeline when SVG is requested. Serializing the current SVG DOM produces one state, not the JS-driven animation. Keep any HTML and SVG versions consistent with the same scenario contract. Project sources must not depend on the user's global skill directory.

## Optional: explicitly requested GIF

Only follow [GIF export](references/gif-export.md) when the user explicitly requests GIF. The renderer can capture either a native SVG or a seekable HTML scene; SVG-to-GIF needs no HTML intermediate. A platform limitation alone is not a request to generate GIF: explain the constraint and keep the requested scope.

For SVG delivery, report the `viewBox` and file size. For GIF, report actual pixel dimensions and file size. Describe any unverified rendering or destination-platform behavior accurately; browser playback alone does not establish that a publishing platform preserves SVG animation.
