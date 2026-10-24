# Benchmark Charts

[简体中文](render-benchmark-charts.zh-CN.md) · [Repository README](../README.md) · [Skill instructions](../skills/render-benchmark-charts/SKILL.md)

Use `render-benchmark-charts` to turn measured CSV results into SVG charts, separate comparison scenarios, and visually review the rendered output before presenting it in a README or report.

## What to provide

- The measured CSV with numeric columns and normalized units, including reported uncertainty when available.
- The APIs, timed operation, commit mode, concurrency, and capacity settings represented by each measurement.
- The comparisons to show, output directory, language, and intended display size.

The skill keeps complete measurements and uses a temporary JSON configuration for filters, labels, axis scales, and scenarios. See the [configuration reference](../skills/render-benchmark-charts/references/chart-config.md) for the schema and an example. Curves, fixed baselines, and grouped bars are supported; bars use a separate chart with a linear y-axis starting at zero.

## Outputs and dependencies

The bundled renderer produces SVG files. Keep the raw CSV and reproducible configuration with the benchmark details; keep README presentation brief.

Use Python with `matplotlib` in a temporary environment. Visual review also needs an SVG rasterizer, such as `resvg-py`, and an image viewer. Keep rendering dependencies outside the target project's runtime and build dependencies. Fonts come from the local system; verify the faces actually used, including CJK glyphs, and preserve any supplied font's license.

```bash
python <skill-dir>/scripts/render_benchmark_charts.py \
  --csv /path/results.csv \
  --config /tmp/chart-config.json \
  --output /path/charts
```

## Example

```text
Use $render-benchmark-charts to plot benchmark/results.csv as SVG charts.
Compare the asynchronous APIs under matching workload settings and show
the synchronous reference separately. Keep the original measurements,
use the recorded units and uncertainty, and visually review every chart.
Keep rendering scripts and environment setup outside the target project.
```

## Checks and failures

Missing or ambiguous measurements fail rather than selecting arbitrary rows. A fixed baseline uses the measurement selected by `baseline_x` and stays horizontal, including its uncertainty band. When combining nearly equal curves, set `equivalent_filters` and an explicit relative tolerance; inspect overlap warnings at the intended display size.

Rasterize each delivered SVG and inspect labels, legends, units, axis scaling, clipping, and agreement with the data. A successful save or XML check alone does not complete visual review. If rendering or visual review is unavailable, report the unfinished check. Use recorded measurements and keep microbenchmark conclusions within the measured workload.
