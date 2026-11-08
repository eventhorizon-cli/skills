# HTML animation style

Use `assets/technical-animation/` when an interactive HTML demonstration is requested. The default documentation deliverable is a native animated SVG; see [SVG authoring](svg-animation.md). Adapt existing HTML animations to their surrounding documentation rather than imposing this layout on every source.

## Page and export layout

- Use self-contained HTML, CSS, JavaScript, and inline SVG with local files; no build or CDN dependency.
- Put the title and introductory explanation outside `.demo`, the export region. Avoid repeating the README heading inside the GIF.
- Within `.demo`, place compact scenario context above the SVG, optional state counters below it, then a short explanation of the current step. Group controls at the bottom and mark them with `data-export-hide`.
- Use a stable landscape scene, usually 1000–1200 CSS pixels wide. The starter has an 1100-wide SVG viewBox. Reserve narration height for the longest language so export bounds remain fixed.
- At narrow widths, wrap controls and allow the SVG region to scroll horizontally instead of making technical labels unreadably small. Check the final GIF separately at its intended document width.

## Typography and color

- Default to white backgrounds, system sans-serif fonts with CJK fallbacks, and tabular or monospace numbers for identifiers and counters.
- Use dark text (`#243447`) and readable secondary text (`#526579`). Start with 18–20 px component labels, 15–16 px annotations, and 14 px context labels at the default layout width. Reduce detail before reducing important labels below these sizes.
- Use restrained semantic colors: blue for requests or dispatch, purple for processing, green for completion, gray for inactive paths, red for failures. Adapt colors to actual roles, and include a text or shape cue.
- Prefer solid connectors, modest corner rounding, and no decorative shadows or gradients. Keep arrow labels clear of lines and progress indicators.

## Motion and technical meaning

- Establish component ownership, admission and execution boundaries, concurrency limits, triggers, and terminal outcomes before drawing. Match names to source code and design documents.
- Derive positions, states, counters, and narration from one explicit time value. Seeking backward must reconstruct the same state; do not increment simulation counters on each frame.
- Motion illustrates a real transition. Do not imply collection timers, ordering guarantees, persistence, or new worker threads merely to make something move.
- Use varied arrivals or concurrent work when these explain the requested behavior. Allow time to read a state without unnecessarily long completion pauses.
- Keep timing in the scene's render function. Avoid autonomous CSS transitions/animations, random arrivals, and network-dependent state unless the seek operation explicitly controls them.

## Readability checks

Inspect the busiest scene, long translated labels, narrow-page controls, and the loop boundary. Check counters against visible entities. Inspect decoded GIF frames as well as HTML: palette conversion and insufficient pixel density can degrade otherwise clear source text.

Start at 2× density. For a 4K-wide export, use `outputWidth: 3840`, preserving logical layout and aspect ratio. Do not stretch the scene or enlarge a low-resolution screenshot. Report the resulting dimensions and file size.
