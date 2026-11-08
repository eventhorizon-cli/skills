# Technical Animations

[简体中文](render-technical-animations.zh-CN.md) · [Repository README](../README.md) · [Skill instructions](../skills/render-technical-animations/SKILL.md)

Use `render-technical-animations` to explain architecture, request flow, concurrency, and state transitions with self-contained animated SVGs for READMEs and technical documentation. Use `draw-technical-diagrams` when a static diagram is sufficient.

## What to provide

- The relevant code or design, including request ownership, execution limits, completion, and ordering guarantees.
- The sequence of events to explain and any behavior the diagram must not imply.
- The output location, language, intended display size, and a suitable playback duration.
- Whether you need interactive controls or explicitly want a GIF.

The agent should establish an event timeline before drawing. Requests, execution slots, counters, and explanatory text must agree at each transition. Illustrative timing must not imply measured performance.

## Outputs and dependencies

The default deliverable is a native animated SVG: the same file is editable source and embeddable output. It uses vector elements and CSS or SMIL animation, without JavaScript, external resources, or embedded bitmap frames. Include an accessible description and a static state for reduced-motion viewing. See the [SVG reference](../skills/render-technical-animations/references/svg-animation.md) and [starter SVG](../skills/render-technical-animations/assets/svg-animation/scene.svg).

HTML is optional for pause, seek, speed, or parameter controls; it is not required as an intermediate step. The skill includes an [HTML starter](../skills/render-technical-animations/assets/technical-animation/index.html) and [player API](../skills/render-technical-animations/references/player-api.md).

GIF is exported only when explicitly requested. The bundled Python renderer uses Playwright and Pillow and can render either a seekable SVG or HTML scene. Follow the [GIF export reference](../skills/render-technical-animations/references/gif-export.md) for environment setup, configuration, and commands. Keep rendering dependencies and caches outside the target project.

Do not automatically create PNG or GIF companions for an SVG. Follow any explicit user request or repository requirement for additional formats.

## Example

```text
Use $render-technical-animations to explain the request batching flow in this repository.
Show two execution slots and a batch limit of four. Take queued requests immediately
when a slot is available; do not imply that the system waits for a full batch.
Output separate English and Chinese SVGs under docs/assets, with a readable loop speed.
Add a step-by-step explanation below each README image.
```

Use this example only when these batching rules match the implementation. Separate language versions should share geometry and timing while translating all visible labels.

## Checks and failures

Check XML, identifiers, timing ranges, and local references, then inspect rendered states around meaningful transitions and the loop boundary. Check labels, clipping, overlaps, counters, and request ownership at the intended README size. Test actual playback through an image element as well as direct SVG viewing. XML validation and a static screenshot do not establish animation correctness.

Check the reduced-motion state and explain any unverified behavior. Browser emulation of reduced motion may not propagate into SVGs embedded as images. Local browser playback also does not establish support on GitHub, NuGet, or a publishing platform; report the context actually tested. If rendering or visual inspection is unavailable, report the incomplete check.
