---
name: render-benchmark-charts
description: Generate SVG benchmark charts from measured CSV data, separate comparison scenarios, and visually review rendered output. Use for benchmark plots and concise README presentations; keep rendering automation in this skill rather than the target project.
---

# Benchmark charts

Keep the project focused on its deliverables: measured data, generated charts, and documentation.
Use this skill's scripts or a temporary workspace for rendering automation and environment setup.
Do not add plotting dependencies to the project's runtime or build dependencies.
The default chart font stack matches the technical-diagram skill: `Arial, PingFang SC, Microsoft YaHei, sans-serif`.
Use local system fonts for this stack; do not copy proprietary system font files into a project or skill. A requested
open font may still be supplied through `font_files` with its license.
Verify the actual font faces used in the rendered SVG, not only the configured fallback stack. Register a local CJK
face explicitly when needed; an available Latin font may otherwise supply unintended CJK fallback glyphs.

## Compare the measured workloads

- Identify the actual APIs, commit mode, concurrency, capacity mode, units, and timed operation before plotting.
- Prefer comparisons of equivalent interfaces as the primary result. Show a synchronous reference separately
  when comparing asynchronous APIs; do not imply that the reference performs the same work.
- A parameter that does not affect one implementation must not appear to control its performance. Use a
  consistently selected fixed baseline for that implementation, explain the selection, and retain the raw data.
- Measure independent optimizations against the same baseline before attributing their gains. Keep combined
  results distinct; do not add percentage improvements together.
- Split charts when capacity or concurrency changes the question. Keep shared axis ranges where that aids
  comparison. Choose the x-axis deliberately: `linear` preserves numeric distance (so 1, 10, 50, and 100
  naturally cluster before 1000), `log` shows orders of magnitude (so 50 and 100 are closer), and `categorical`
  gives discrete configurations equal spacing. Categorical spacing is visual only; its line slope is not a numeric rate.
  Label logarithmic axes explicitly and preserve meaningful intermediate parameter values.
- Use the recorded means and reported uncertainty. Do not invent missing measurements, smooth away failures,
  or describe a microbenchmark as an end-to-end throughput guarantee.

## Render

Use standard plotting tools rather than writing SVG paths manually. SVG is an output format, not a requirement
to author vector markup. PNG is also suitable when requested; preserve vector output for repository charts when
that is the requested deliverable.

Give multiline labels comfortable leading (roughly 1.4–1.5 line spacing) and separate legend rows clearly
(Matplotlib `labelspacing` around 1.0–1.2 is a useful starting point). Line spacing is distinct from the blank space
between title, subtitle, legend, and plot: increasing block margins does not fix cramped text rows. Check wrapped
axis labels, translated text, and multi-row legends at the intended display size; reserve enough room to avoid
clipping without shrinking the plot or type. Position subtitles from the rendered title bounds, rather than using
independent fixed vertical coordinates. Scale block gaps with the relevant font size: start with 0.3× subtitle size
after the title, 0.7× subtitle size before the legend, and 1× legend size before the plot. Position each block from
the preceding block's measured bounds, so font changes and wrapped lines preserve this hierarchy without excess whitespace.
Keep related charts consistent.

Check for curves hidden by later series when measured values nearly overlap. Do not shift measurements to separate
lines. Either use distinguishable line/marker styles or, when the values support it, show one representative curve
with a combined legend (for example, `Auto/Manual Commit · nearly equal`). Identify which measurements are plotted
in the footnote and retain the complete data. Use `equivalent_filters` with an explicit relative tolerance to verify
every merged value before rendering; if any exceeds that tolerance, show separate curves. A renderer overlap warning
requires review at the intended display size; a single crossing is not a hidden series.

Align legend entries horizontally across columns: entries in the same row must have matching heights and aligned
text baselines. Prefer concise single-line labels; do not wrap a qualifier onto a second line while its neighboring
entry stays on one line. If wrapping is necessary, use a consistent line count and measured row height across that
row, or reduce the column count. Verify left/right alignment in the rendered image; increasing overall legend
spacing does not fix unequal entry heights. Put longer workload explanations in nearby prose.

Trim unused space above the data after allowing for error bars and value labels; roughly 10–15% linear headroom is
a useful starting point. Keep bar axes anchored at zero. Share limits when that helps comparison, but do not leave
large empty upper ranges merely to reuse one limit across unrelated scenarios. Check log-axis headroom separately.

The renderer supports grouped `bar` series for categorical API comparisons. Keep bar charts separate from curve or
baseline series, use a linear y-axis starting at zero, and identify categories through tick labels or the legend.

For allocation comparisons, state the work represented by one operation and normalize the reported units consistently.
Distinguish allocated bytes from peak/live memory, and do not reuse time uncertainty as allocation error bars.

The reusable renderer accepts normalized numeric CSV columns and a task-specific JSON configuration:

```bash
python scripts/render_benchmark_charts.py --csv /path/results.csv --config /tmp/chart-config.json --output /path/charts
```

Read [the configuration reference](references/chart-config.md) when using the renderer. Put task-specific filters,
labels, dimensions, and scenario choices in a temporary configuration rather than hard-coding a repository into
the skill. Install `matplotlib` in a temporary Python environment if needed; the renderer uses a noninteractive
backend. Keep generated figures deterministic where practical, including SVG IDs and creation metadata.

## Verify visually

Render each delivered SVG to a bitmap with an actual SVG renderer and inspect it through an available vision/image
tool. XML validation and a successful save do not constitute visual review. Check legends, units, axis scaling,
labels, annotation collisions, clipping, baseline meanings, and agreement with the measured data. Correct issues
and render again before delivery. Inspect individual charts or small contact sheets at a readable scale; a dense
thumbnail grid alone cannot verify typography. Confirm parameter-independent references are horizontal at the selected
measurement, including any uncertainty band, rather than joining unrelated repeated measurements.

One option is `resvg-py` in a temporary environment:

```python
from pathlib import Path
import resvg_py
Path("/tmp/chart.png").write_bytes(resvg_py.svg_to_bytes(svg_path="/path/chart.svg", dpi=96))
```

Keep README presentation brief: explain the comparison, show the relevant charts, and link to details containing
the reproducible configuration, complete data, and limitations. Follow the repository's language and terminology
rules. Report what was measured and visually checked without claiming checks that were not performed.
