# Explicit GIF export

Use this workflow only when the user explicitly requests GIF. Default SVG delivery does not require frame capture, Pillow, or a GIF encoder. Keep rendering dependencies in the skill cache, outside the target project.

## Setup

```sh
python3 -m venv ~/.cache/codex/render-technical-animations/venv
~/.cache/codex/render-technical-animations/venv/bin/pip install -r ~/.codex/skills/render-technical-animations/scripts/requirements.txt
~/.cache/codex/render-technical-animations/venv/bin/python -m playwright install chromium --only-shell
```

Prefer Playwright's matching Chromium headless shell. Use `--browser /path/to/chrome` for another installed executable. The renderer bounds browser/transport shutdown waits and replaces the destination only after encoding and validation succeed.

## Native SVG input

Use the [SVG export config](../assets/svg-animation/export.json) as a starting point. Adapt the duration and checkpoints to the actual scene. There is no HTML intermediate:

```sh
~/.cache/codex/render-technical-animations/venv/bin/python \
  ~/.codex/skills/render-technical-animations/scripts/render_animation.py \
  --source path/to/scene.svg --config path/to/export.json \
  --output path/to/animation.gif
```

The SMIL seek hook calls `pauseAnimations()` and `setCurrentTime(seconds)` on the root SVG. For CSS animation, replace the hook with one that pauses and seeks the CSS animations. The configured seek operation must control every animation in the captured region.

## Existing HTML input

The [HTML starter config](../assets/technical-animation/export.json) and existing seekable HTML sources remain supported:

```sh
~/.cache/codex/render-technical-animations/venv/bin/python \
  ~/.codex/skills/render-technical-animations/scripts/render_animation.py \
  --source path/to/index.html --config path/to/export.json \
  --output path/to/animation.gif --query lang=en
```

HTML's `seek` hook must pause playback and reconstruct the complete state from time. Repeat with the appropriate language query only for languages the scene supports. Separate SVG language files are passed as separate sources instead.

## Configuration and checks

Inspect unfamiliar configs before running them: `ready`, `seek`, and checkpoint `evaluate` contain executable JavaScript.

- `width` and `height` set the CSS viewport; `selector` chooses exactly one export region. Keep its dimensions fixed throughout playback.
- `scale` controls pixel density (default 2, greater than 0 and at most 4). Optional positive integer `outputWidth` requests a physical pixel width such as `3840`, preserving logical layout and aspect ratio. The renderer derives the required density from the region; at most one pixel of browser rounding is allowed.
- `duration` and `fps` define frame times. FPS must divide 100 for GIF centisecond delays; 20 is a useful starting point. Capture excludes the endpoint to avoid duplicating the first frame at the loop boundary.
- `reducedMotion` is `reduce` by default for existing HTML players. Set `no-preference` when capturing an SVG whose reduced-motion mode shows a still. The seek hook still has to stop autonomous playback.
- `ready`, optional `css`, and `seek` prepare the source and render each requested time. Screenshot latency must not advance the scene.
- `checkpoints` validate meaningful states before capture. Check visible identities, membership, counters, and completion where applicable, not only that the page loaded. Encoding validates fixed dimensions, total duration, and infinite looping before replacing the destination.

Render at the required density; do not upscale low-resolution screenshots. Quantize full-resolution frames, inspect decoded GIF frames at the intended display width, and check stationary regions for palette flicker. Report actual dimensions and file size. Run large exports sequentially when memory is limited. Keep only requested outputs in the project and use its documentation image-path convention.
