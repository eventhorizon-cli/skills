# Native SVG animation

Use SVG as both the editable source and the default deliverable. Open it directly in a browser; HTML is not required. The [starter](../assets/svg-animation/scene.svg) illustrates one request moving through a processing stage. Its timings are examples, not an architecture contract.

## Structure and style

- Use the SVG namespace, explicit dimensions, a stable landscape `viewBox`, and an opaque white background. Start around 1000–1200 logical units wide; vectors do not need a 4K coordinate system for sharp output.
- Put styles and animation elements inside the SVG. Avoid scripts, event-handler attributes, external fonts/styles/images, `foreignObject`, and runtime HTML dependencies so the animation can work in an image context. Use native shapes and text, not embedded raster frames.
- Include a `<title>` and `<desc>` with an accessible name/description. Prefer system sans-serif fonts with CJK fallbacks. Use separate files for each language and preserve geometry and timing.
- Start with 18–20 unit component labels and 15–16 unit annotations. Explicitly position multiline `<tspan>` elements. Inspect readability at the destination width; reducing detail is preferable to tiny text.
- Use restrained semantic colors: blue for requests/dispatch, purple for processing, green for completion, gray for inactive paths, red for failures. Include a text or shape cue. Keep connectors away from labels; avoid decorative shadows and gradients.

## Timeline

Write down the actual events and the states between them before authoring keyframes. Use a shared cycle duration; the starter records it as `data-duration="8"` and uses `dur="8s"` on each animation. Keep those values synchronized when changing the cycle.

- Use `<animateTransform>` for movement, `<animate>` for progress or opacity, and `calcMode="discrete"` to select state labels, narration, and counter values. CSS keyframes are also suitable when deterministic seeking and image-context playback are verified.
- Compute normalized `keyTimes` from the event times. Keep movement, membership, labels, and counters consistent with the same event table; independently written timelines can drift.
- To change text, provide the relevant text states and switch their visibility at the corresponding boundaries. Do not depend on JS assigning `textContent` after embedding.
- Give base attributes a meaningful first state and make every repeated animation share the same cycle. Inspect both sides of each event and the cycle boundary, including a second cycle.
- Use internal CSS `@media (prefers-reduced-motion: reduce)` to show a meaningful static group and hide the animated group. SMIL does not automatically stop when reduced motion is requested. The static group must communicate a coherent state on its own.
- Motion must not invent collection waits, ordering guarantees, persistent storage, worker threads, or other behavior absent from the design. Distinguish illustrative timing from measured execution.

## Verification

Parse the XML and check the namespace, viewBox, unique IDs, local references, animation values/keyTimes, cycle duration, accessible labels, and reduced-motion still. Structural validity does not prove visual correctness.

Open the actual SVG in a browser and inspect idle, busy, and complete states at the intended document width. For SMIL, deterministic inspection can use the browser's SVG API:

```js
const scene = document.documentElement;
scene.pauseAnimations();
scene.setCurrentTime(4);
```

For CSS animations, pause each animation from `document.getAnimations()` and set its `currentTime` in milliseconds instead. The inspection method must match the animation mechanism; the SMIL API does not seek CSS animations.

Check that visible requests agree with counters, execution states, and narration. Inspect long translated labels, arrow endpoints, clipping, stationary text, and loop reset. Test an actual `<img src="scene.svg">` with autonomous playback as well: a script-enabled standalone SVG can conceal image-context problems. Test the reduced-motion still in both contexts. Page-level media emulation may not reach an SVG image; if it does not, record that limitation instead of claiming the image's reduced-motion behavior is verified. Confirm the target publishing platform separately before claiming its animation support.

Temporary preview pages and screenshots may be used for inspection without becoming deliverables. Do not add HTML, PNG, or GIF files to the project just to verify SVG. If raster backups are explicitly requested or required by repository instructions, generate and inspect them as separate outputs.

## GIF, when requested

The adjacent [export.json](../assets/svg-animation/export.json) captures the SMIL starter directly. Its seek hook pauses the SVG time container before setting the requested time, and `reducedMotion: "no-preference"` selects the animated group during export. Adapt the duration and semantic checkpoints to the actual SVG. See [GIF export](gif-export.md) for setup and commands.
