# Renderer configuration

The input is a CSV with numeric measurement columns. Normalize units before rendering; the renderer does not guess
whether a number is nanoseconds, microseconds, milliseconds, throughput, or memory. Match axis labels to those units.
CSV filter values are matched as text, case-sensitively. Use string values when their formatting matters.

Example configuration:

```json
{
  "x_column": "BatchSize",
  "y_column": "Mean_us",
  "error_column": "Error_us",
  "x_values": [1, 10, 50, 100, 1000],
  "x_label": "BatchSize (discrete configuration)",
  "y_label": "Mean elapsed time (µs, log scale)",
  "font_family": ["Arial", "PingFang SC", "Microsoft YaHei", "sans-serif"],
  "x_scale": "categorical",
  "y_scale": "log",
  "y_limits": [10, 6000],
  "y_ticks": [10, 20, 50, 100, 200, 500, 1000, 2000, 5000],
  "subtitle": "Same message count and capacity configuration · lower is better",
  "footnote": "The reference API does not use the batch-size parameter.",
  "series": [
    {
      "label": "Candidate async API",
      "filters": {"Method": "Candidate"},
      "kind": "curve",
      "color": "#2459b8"
    },
    {
      "label": "Reference async API",
      "filters": {"Method": "Reference"},
      "kind": "baseline",
      "baseline_x": 1,
      "color": "#b56313",
      "style": "--"
    }
  ],
  "charts": [
    {"filename": "one-reader.svg", "title": "1 reader", "filters": {"Consumers": "1"}},
    {"filename": "many-readers.svg", "title": "12 readers", "filters": {"Consumers": "12"}}
  ]
}
```

Each chart combines its filters with each series' filters. A curve requires exactly one matching measurement at each
configured x value. A baseline requires exactly one at `baseline_x`; it is drawn horizontally. Ambiguous or missing
measurements fail instead of selecting an arbitrary row. Series retain their configured legend order.
Set `annotate` to `false` on a curve or bar series when nearby values would make point labels overlap; it defaults to
`true`.

Use `kind: "bar"` for grouped categorical comparisons such as APIs with no numeric x-axis. Bar series cannot be
mixed with curves or baselines in one chart and require a linear y-axis. Set `x_tick_labels` when the numeric x values
are only category positions; `x_tick_rotation` is an optional numeric rotation in degrees.
Set `legend_columns` when a long legend should wrap at a specific number of columns; it defaults to three columns.

`error_column`, limits, and y ticks are optional. The x scale is `linear`, `log`, or `categorical`; the y scale is
`linear` or `log`. Use `categorical` when the x values are a small set of discrete configurations (for example, batch
sizes) and equal visual spacing is clearer than implying numeric distance. Use `linear` or `log` when the x-axis
magnitude itself is the quantity being compared. Log data and error bounds must be positive. Errors must be finite and
nonnegative. The chart uses the supplied error magnitude without interpreting its confidence level; explain the source's
definition in the accompanying benchmark details. Set optional `font_family` to a family name or ordered array of
locally available families. The default is `["Arial", "PingFang SC", "Microsoft YaHei", "sans-serif"]`, matching the
technical-diagram skill. Use optional `font_files` to register local font files before rendering (for example, a
locally extracted PingFang SC face); do not bundle proprietary system fonts. Open fonts may be supplied this way when
their license permits redistribution.

Choose limits after inspecting all scenarios so points and uncertainty are visible. Visual review remains necessary,
especially when labels are long, baselines overlap, or changing axis ranges makes comparisons difficult.

A curve may explicitly represent other measured series with `equivalent_filters` (an array of filter objects) and
`equivalence_relative_tolerance` (a required number from 0 inclusive to 1 exclusive). At every x value, each peer must
match exactly one row under the chart filters; its plotted y value must differ from the representative by at most
`tolerance × max(abs(representative), abs(peer))`. Both zeros match. No missing rows or larger differences are hidden.
For example, add `"equivalent_filters": [{"Method": "ManualCommit"}]` and
`"equivalence_relative_tolerance": 0.005` to an AutoCommit curve to check a 0.5% display tolerance. This is a chart
presentation check, not a statistical equivalence claim. Keep complete measurements and explain the combined legend
and chosen representative in the footnote. The renderer also warns when at least 80% of two curves' points are within
two display pixels with identical line and marker styles; inspect these warnings rather than relying on color alone.

Omit `color` to use the default series palette in series order; an explicit color overrides that default.
