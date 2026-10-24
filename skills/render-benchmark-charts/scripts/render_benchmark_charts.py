"""Render configurable benchmark charts from CSV measurements."""

import argparse
import csv
import json
import math
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator


DEFAULT_COLORS = ["#2459b8", "#b56313", "#697586", "#2f855a", "#9f3a38"]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, type=Path, help="Benchmark CSV file")
    parser.add_argument("--config", required=True, type=Path, help="Chart configuration JSON file")
    parser.add_argument("--output", required=True, type=Path, help="Directory for rendered SVG files")
    return parser.parse_args()


def fail(message):
    raise ValueError(message)


def stringify(value):
    if isinstance(value, bool):
        return "True" if value else "False"
    if value is None:
        return "None"
    return str(value)


def require_string(config, name):
    value = config.get(name)
    if not isinstance(value, str) or not value:
        fail(f"{name} must be a non-empty string")
    return value


def require_list(config, name):
    value = config.get(name)
    if not isinstance(value, list) or not value:
        fail(f"{name} must be a non-empty array")
    return value


def validate_config(config):
    if not isinstance(config, dict):
        fail("config must be a JSON object")

    for name in ("x_column", "y_column", "x_label", "y_label", "x_scale", "y_scale", "subtitle", "footnote"):
        require_string(config, name)
    if config["x_scale"] not in ("linear", "log", "categorical"):
        fail("x_scale must be linear, log, or categorical")
    if config["y_scale"] not in ("linear", "log"):
        fail("y_scale must be linear or log")
    if "error_column" in config and config["error_column"] is not None:
        require_string(config, "error_column")
    if "font_family" in config:
        font_family = config["font_family"]
        if isinstance(font_family, str):
            if not font_family:
                fail("font_family must be a non-empty string or array")
        elif (
            not isinstance(font_family, list)
            or not font_family
            or any(not isinstance(item, str) or not item for item in font_family)
        ):
            fail("font_family must be a non-empty string or array of strings")
    if "font_files" in config:
        font_files = config["font_files"]
        if (
            not isinstance(font_files, list)
            or any(not isinstance(item, str) or not item for item in font_files)
        ):
            fail("font_files must be an array of non-empty strings")

    x_values = require_list(config, "x_values")
    if len({stringify(value) for value in x_values}) != len(x_values):
        fail("x_values must not contain duplicate stringified values")
    if "x_tick_labels" in config:
        labels = config["x_tick_labels"]
        if (
            not isinstance(labels, list)
            or len(labels) != len(x_values)
            or any(not isinstance(item, str) or not item for item in labels)
        ):
            fail("x_tick_labels must be an array of non-empty strings matching x_values")
    if "x_tick_rotation" in config and not isinstance(config["x_tick_rotation"], (int, float)):
        fail("x_tick_rotation must be numeric")
    if "show_x_axis_labels" in config and not isinstance(config["show_x_axis_labels"], bool):
        fail("show_x_axis_labels must be boolean")
    if "legend_columns" in config and (
        not isinstance(config["legend_columns"], int) or config["legend_columns"] < 1
    ):
        fail("legend_columns must be a positive integer")

    series = require_list(config, "series")
    kinds = {item.get("kind") for item in series if isinstance(item, dict)}
    if "bar" in kinds and len(kinds) > 1:
        fail("bar series cannot be mixed with curve or baseline series")
    for index, item in enumerate(series):
        if not isinstance(item, dict):
            fail(f"series[{index}] must be an object")
        require_string(item, "label")
        kind = require_string(item, "kind")
        if kind not in ("curve", "baseline", "bar"):
            fail(f"series[{index}].kind must be curve, baseline, or bar")
        if "color" in item and (not isinstance(item["color"], str) or not item["color"]):
            fail(f"series[{index}].color must be a non-empty string")
        filters = item.get("filters", {})
        if not isinstance(filters, dict):
            fail(f"series[{index}].filters must be an object")
        if kind == "baseline" and "baseline_x" not in item:
            fail(f"series[{index}] baseline requires baseline_x")
        if "style" in item and not isinstance(item["style"], str):
            fail(f"series[{index}].style must be a string")
        if "equivalent_filters" in item:
            peers = item["equivalent_filters"]
            if kind != "curve" or not isinstance(peers, list) or not peers or any(
                not isinstance(peer, dict) or not peer for peer in peers
            ):
                fail(f"series[{index}].equivalent_filters requires a curve and non-empty filter objects")
            tolerance = parse_number(item.get("equivalence_relative_tolerance"), "equivalence_relative_tolerance")
            if not 0 <= tolerance < 1:
                fail("equivalence_relative_tolerance must be >= 0 and < 1")

    charts = require_list(config, "charts")
    for index, chart in enumerate(charts):
        if not isinstance(chart, dict):
            fail(f"charts[{index}] must be an object")
        filename = require_string(chart, "filename")
        chart_path = Path(filename)
        if chart_path.is_absolute() or chart_path.name != filename or chart_path.suffix.lower() != ".svg":
            fail(f"charts[{index}].filename must be a plain .svg filename")
        require_string(chart, "title")
        filters = chart.get("filters", {})
        if not isinstance(filters, dict):
            fail(f"charts[{index}].filters must be an object")

    for name in ("x_limits", "y_limits", "y_ticks"):
        if name in config:
            values = config[name]
            if not isinstance(values, list) or not values:
                fail(f"{name} must be a non-empty array")
            if name.endswith("limits") and len(values) != 2:
                fail(f"{name} must contain exactly two values")
    return config


def load_csv(path):
    with path.open(newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None:
            fail(f"CSV has no header: {path}")
        rows = list(reader)
    return reader.fieldnames, rows


def matching_rows(rows, filters):
    expected = {str(key): stringify(value) for key, value in filters.items()}
    return [row for row in rows if all(row.get(key) == value for key, value in expected.items())]


def parse_number(value, name):
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        fail(f"{name} must be numeric: {value!r}")
        raise error
    if not math.isfinite(number):
        fail(f"{name} must be finite: {value!r}")
    return number


def selected_measurement(rows, config, chart_filters, series, x_value=None):
    filters = dict(chart_filters)
    filters.update(series.get("filters", {}))
    filtered = matching_rows(rows, filters)
    x_column = config["x_column"]
    if x_value is not None:
        expected_x = stringify(x_value)
        filtered = [row for row in filtered if row.get(x_column) == expected_x]
    kind = series["kind"]
    if len(filtered) != 1:
        location = f" at {x_column}={stringify(x_value)}" if x_value is not None else ""
        fail(
            f"Expected exactly one {kind} row for {series['label']!r}{location}; "
            f"found {len(filtered)} after filters"
        )
    return filtered[0]


def measurement(row, config, series):
    x = parse_number(row[config["x_column"]], config["x_column"])
    y = parse_number(row[config["y_column"]], config["y_column"])
    error_column = config.get("error_column")
    error = None
    if error_column:
        error = parse_number(row[error_column], error_column)
        if error < 0:
            fail(f"{error_column} must be non-negative: {error}")
    return x, y, error


def validate_axis_value(value, name, scale):
    number = parse_number(value, name)
    if scale == "log" and number <= 0:
        fail(f"{name} must be positive for a log axis: {number}")
    return number


def error_band(mean, error, scale, name):
    if error is None:
        return None
    lower = mean - error
    upper = mean + error
    if not math.isfinite(lower) or not math.isfinite(upper):
        fail(f"{name} error band must be finite")
    if scale == "log" and lower <= 0:
        fail(f"{name} error band must remain positive for a log axis: {lower}")
    return lower


def validate_limits(config, name, scale):
    if name not in config:
        return None
    limits = config[name]
    values = [validate_axis_value(value, name, scale) for value in limits]
    if values[0] >= values[1]:
        fail(f"{name} lower bound must be less than upper bound")
    return values


def format_tick(value, _position):
    if value == int(value):
        return f"{int(value):,}"
    return f"{value:g}"


def annotation_offset(axis, figure, x, y, baseline_ranges, text):
    """Choose a pixel-safe vertical offset that avoids baseline bands."""
    x_pixel, y_pixel = axis.transData.transform((x, y))
    figure_width, _ = figure.canvas.get_width_height()
    axis_box = axis.bbox
    half_width = max(8, len(text) * 3.2)
    half_height = 7
    point_to_pixel = figure.dpi / 72
    candidates = [(0, 10), (0, -15), (0, 20), (0, -25), (0, 30), (0, -35)]

    def is_safe(x_offset, y_offset):
        candidate_x = x_pixel + x_offset * point_to_pixel
        candidate_y = y_pixel + y_offset * point_to_pixel
        if candidate_x - half_width < 1 or candidate_x + half_width > figure_width - 1:
            return False
        if candidate_y - half_height < axis_box.y0 + 1 or candidate_y + half_height > axis_box.y1 - 1:
            return False
        for lower, upper in baseline_ranges:
            lower_pixel = axis.transData.transform((x, lower))[1]
            upper_pixel = axis.transData.transform((x, upper))[1]
            band_low = min(lower_pixel, upper_pixel) - half_height - 2
            band_high = max(lower_pixel, upper_pixel) + half_height + 2
            if candidate_y + half_height >= band_low and candidate_y - half_height <= band_high:
                return False
        return True

    for candidate in candidates:
        if is_safe(*candidate):
            return candidate
    desired_y = y_pixel + (-15 if y_pixel > (axis_box.y0 + axis_box.y1) / 2 else 10) * point_to_pixel
    clamped_y = min(max(desired_y, axis_box.y0 + half_height + 1), axis_box.y1 - half_height - 1)
    clamped_x = min(max(x_pixel, half_width + 1), figure_width - half_width - 1)
    return ((clamped_x - x_pixel) / point_to_pixel, (clamped_y - y_pixel) / point_to_pixel)



def check_equivalent_measurement(rows, config, series, x_value, representative):
    """Validate explicitly merged series against every recorded plotted value."""
    for filters in series.get("equivalent_filters", []):
        peer = dict(series, filters=filters)
        row = selected_measurement(rows, config, {}, peer, x_value)
        _, other, _ = measurement(row, config, peer)
        scale = max(abs(representative), abs(other))
        tolerance = series["equivalence_relative_tolerance"]
        if abs(representative - other) > tolerance * scale:
            fail(
                f"Merged series {series['label']!r} differs beyond {tolerance:.1%} "
                f"at {config['x_column']}={x_value}: {representative:g} versus {other:g}; "
                "show separate curves instead"
            )


def warn_obscured_curves(axis, curves):
    """Catch sustained overlap at the rendered scale, rather than a crossing."""
    for index, (earlier_label, earlier) in enumerate(curves):
        points = axis.transData.transform(earlier.get_xydata())
        if len(points) < 2:
            continue
        for later_label, later in curves[index + 1:]:
            other = axis.transData.transform(later.get_xydata())
            if len(other) != len(points):
                continue
            close = sum(abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 2 for a, b in zip(points, other))
            if (close / len(points) >= 0.8
                and earlier.get_linestyle() == later.get_linestyle()
                and earlier.get_marker() == later.get_marker()):
                warnings.warn(
                    f"Curves {earlier_label!r} and {later_label!r} nearly overlap "
                    "with identical line/marker styles; distinguish them or explicitly merge "
                    "them with equivalent_filters and explain the representative in the legend/footnote.",
                    UserWarning,
                    stacklevel=2,
                )


def render_chart(rows, config, chart, output):
    x_column = config["x_column"]
    x_values = config["x_values"]
    if config["x_scale"] == "categorical":
        # Discrete configuration values get equal visual spacing; their numeric
        # magnitude is not a claim about the distance between workloads.
        x_numbers = list(range(len(x_values)))
    else:
        x_numbers = [validate_axis_value(value, x_column, config["x_scale"]) for value in x_values]
    y_limits = validate_limits(config, "y_limits", config["y_scale"])
    x_limits = validate_limits(config, "x_limits", "linear" if config["x_scale"] == "categorical" else config["x_scale"])
    y_ticks = None
    if "y_ticks" in config:
        y_ticks = [validate_axis_value(value, "y_ticks", config["y_scale"]) for value in config["y_ticks"]]

    chart_rows = matching_rows(rows, chart.get("filters", {}))
    if not chart_rows:
        fail(f"Chart {chart['filename']!r} filters matched no rows")

    fig, axis = plt.subplots(figsize=(9.4, 5.2), facecolor="white")
    fig.subplots_adjust(left=0.115, right=0.975, bottom=0.18, top=0.70)
    figure_height_pt = fig.get_figheight() * 72
    title_fontsize, subtitle_fontsize, legend_fontsize = 17, 10, 8
    title_text = fig.suptitle(
        chart["title"], x=0.115, y=1 - 0.7 * title_fontsize / figure_height_pt, ha="left",
        fontsize=title_fontsize, fontweight="bold", linespacing=1.5, color="#172b4d",
    )
    subtitle_text = fig.text(
        0.115, 0, config["subtitle"], va="top", fontsize=subtitle_fontsize, linespacing=1.5, color="#475467",
    )
    annotations = []
    baseline_ranges = []
    curves = []
    bar_series = [series for series in config["series"] if series["kind"] == "bar"]
    if bar_series and config["y_scale"] == "log":
        fail("bar series require a linear y_scale")

    for index, series in enumerate(config["series"]):
        color = series.get("color") or DEFAULT_COLORS[index % len(DEFAULT_COLORS)]
        style = series.get("style", "-")
        if series["kind"] == "bar":
            bar_index = bar_series.index(series)
            bar_width = 0.8 / len(bar_series)
            measurements = [
                measurement(selected_measurement(chart_rows, config, {}, series, x_value), config, series)
                for x_value in x_values
            ]
            means = [item[1] for item in measurements]
            errors = [item[2] for item in measurements]
            positions = [
                x + (bar_index - (len(bar_series) - 1) / 2) * bar_width
                for x in x_numbers
            ]
            yerr = errors if all(error is not None for error in errors) else None
            axis.bar(
                positions,
                means,
                width=bar_width * 0.9,
                yerr=yerr,
                error_kw={"capsize": 3} if yerr is not None else None,
                color=color,
                alpha=0.9,
                label=series["label"],
                zorder=3,
            )
            if series.get("annotate", True):
                annotations.extend((x, mean, f"{mean:,.1f}", color) for x, mean in zip(positions, means))
        elif series["kind"] == "curve":
            measurements = []
            for x_value in x_values:
                row = selected_measurement(chart_rows, config, {}, series, x_value)
                item = measurement(row, config, series)
                check_equivalent_measurement(chart_rows, config, series, x_value, item[1])
                measurements.append(item)
            means = [item[1] for item in measurements]
            errors = [item[2] for item in measurements]
            if config["x_scale"] == "log" and any(x <= 0 for x in x_numbers):
                fail(f"{x_column} must be positive for a log axis")
            if config["y_scale"] == "log" and any(y <= 0 for y in means):
                fail(f"{config['y_column']} must be positive for a log axis")
            yerr = errors if all(error is not None for error in errors) else None
            plotted = axis.errorbar(
                x_numbers,
                means,
                yerr=yerr,
                color=color,
                linewidth=2.5,
                linestyle=style,
                marker="o",
                markersize=6,
                capsize=3 if yerr is not None else 0,
                label=series["label"],
                zorder=3,
            )
            curves.append((series["label"], plotted.lines[0]))
            if yerr is not None:
                lower = [error_band(y, error, config["y_scale"], config["y_column"]) for y, error in zip(means, errors)]
                axis.fill_between(
                    x_numbers,
                    lower,
                    [y + error for y, error in zip(means, errors)],
                    color=color,
                    alpha=0.07,
                    linewidth=0,
                    zorder=1,
                )
            if series.get("annotate", True):
                annotations.extend((x, mean, f"{mean:,.1f}", color) for x, mean in zip(x_numbers, means))
        else:
            baseline_x = series["baseline_x"]
            row = selected_measurement(chart_rows, config, {}, series, baseline_x)
            x, mean, error = measurement(row, config, series)
            if config["x_scale"] == "log" and x <= 0:
                fail(f"{x_column} must be positive for a log axis")
            if config["y_scale"] == "log" and mean <= 0:
                fail(f"{config['y_column']} must be positive for a log axis")
            if error is not None:
                lower = error_band(mean, error, config["y_scale"], config["y_column"])
                axis.axhspan(lower, mean + error, color=color, alpha=0.07, linewidth=0, zorder=1)
            else:
                lower = mean
            baseline_ranges.append((lower, mean + error if error is not None else mean))
            axis.axhline(mean, color=color, linewidth=2, linestyle=style, label=series["label"], zorder=2)

    if config["x_scale"] != "categorical":
        axis.set_xscale(config["x_scale"])
    axis.set_yscale(config["y_scale"])
    if x_limits is not None:
        axis.set_xlim(x_limits)
    if y_limits is not None:
        axis.set_ylim(y_limits)
    if config.get("show_x_axis_labels", True):
        axis.xaxis.set_major_locator(FixedLocator(x_numbers))
        axis.xaxis.set_minor_locator(NullLocator())
        if config["x_scale"] == "categorical":
            tick_labels = config.get("x_tick_labels", [stringify(value) for value in x_values])
            axis.xaxis.set_major_formatter(
                FuncFormatter(
                    lambda value, _position, tick_labels=tick_labels: tick_labels[int(round(value))]
                    if 0 <= int(round(value)) < len(tick_labels)
                    else ""
                )
            )
        else:
            axis.xaxis.set_major_formatter(FuncFormatter(format_tick))
    else:
        axis.set_xticks([])
    if y_ticks is not None:
        axis.yaxis.set_major_locator(FixedLocator(y_ticks))
    axis.yaxis.set_minor_locator(NullLocator())
    axis.yaxis.set_major_formatter(FuncFormatter(format_tick))
    if config.get("show_x_axis_labels", True):
        axis.set_xlabel(config["x_label"], labelpad=9, fontsize=10)
    axis.set_ylabel(config["y_label"], labelpad=10, fontsize=10)
    axis.tick_params(axis="both", labelsize=9, length=0, pad=6, colors="#344054")
    for label in axis.get_xticklabels() + axis.get_yticklabels():
        label.set_linespacing(1.5)
    if "x_tick_rotation" in config:
        plt.setp(axis.get_xticklabels(), rotation=config["x_tick_rotation"], ha="right")
    axis.grid(axis="y", color="#e4e7ec", linewidth=0.8)
    axis.set_axisbelow(True)
    for side in ("top", "right"):
        axis.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        axis.spines[side].set_color("#d0d5dd")

    # Anchor header blocks to measured text bounds, including CJK and wrapped lines.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    def bottom_in_figure(artist):
        return artist.get_window_extent(renderer).transformed(fig.transFigure.inverted()).y0

    subtitle_text.set_position((0.115, bottom_in_figure(title_text) - 0.3 * subtitle_fontsize / figure_height_pt))
    legend_top = bottom_in_figure(subtitle_text) - 0.7 * subtitle_fontsize / figure_height_pt

    handles, labels = axis.get_legend_handles_labels()
    legend = fig.legend(
        handles,
        labels,
        ncol=config.get("legend_columns", min(len(handles), 3)),
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(0.115, legend_top),
        borderaxespad=0,
        borderpad=0,
        fontsize=legend_fontsize,
        labelspacing=1.15,
        columnspacing=1.2,
        handlelength=2.0,
    )
    for label in legend.get_texts():
        label.set_linespacing(1.5)
    plot_top = bottom_in_figure(legend) - legend_fontsize / figure_height_pt
    if plot_top <= 0.18:
        fail("Title, subtitle, and legend leave no room for the plot")
    axis.set_position([0.115, 0.18, 0.86, plot_top - 0.18])

    fig.canvas.draw()
    warn_obscured_curves(axis, curves)
    for x, mean, text, color in annotations:
        offset = annotation_offset(axis, fig, x, mean, baseline_ranges, text)
        axis.annotate(
            text,
            (x, mean),
            xytext=offset,
            textcoords="offset points",
            ha="center",
            fontsize=9,
            color=color,
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 1, "alpha": 0.9},
        )

    fig.text(0.115, 0.025, config["footnote"], fontsize=9, linespacing=1.5, color="#667085")
    title = chart["title"]
    svg_path = output / chart["filename"]
    fig.savefig(
        svg_path,
        format="svg",
        metadata={"Date": None, "Title": title},
    )
    # Matplotlib emits trailing spaces on wrapped path commands. Normalize the
    # generated artifact so repository whitespace checks remain deterministic.
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n",
        encoding="utf-8",
    )
    plt.close(fig)


def main():
    args = parse_args()
    with args.config.open() as source:
        config = validate_config(json.load(source))
    fieldnames, rows = load_csv(args.csv)
    required_columns = {config["x_column"], config["y_column"]}
    if config.get("error_column"):
        required_columns.add(config["error_column"])
    missing = sorted(required_columns - set(fieldnames))
    if missing:
        fail(f"CSV is missing columns: {', '.join(missing)}")
    args.output.mkdir(parents=True, exist_ok=True)
    # Register fonts explicitly supplied by the rendering environment. The
    # default family stack matches the technical-diagram skill and lets each
    # platform resolve its local CJK fallback.
    for filename in config.get("font_files", []):
        path = Path(filename)
        if not path.is_file():
            fail(f"font_files entry does not exist: {filename}")
        font_manager.fontManager.addfont(str(path))
    font_family = config.get(
        "font_family", ["Arial", "PingFang SC", "Microsoft YaHei", "sans-serif"]
    )
    if isinstance(font_family, str):
        font_family = [font_family]
    # Keep the declared order while omitting unavailable named faces. This
    # avoids repeated findfont warnings on machines without Microsoft YaHei;
    # the final generic family remains the platform fallback.
    resolved_families = []
    for family in font_family:
        if family in ("sans-serif", "serif", "monospace"):
            resolved_families.append(family)
            continue
        try:
            font_manager.findfont(family, fallback_to_default=False)
        except ValueError:
            continue
        resolved_families.append(family)
    if not resolved_families:
        fail("font_family has no available family or generic fallback")
    plt.rcParams.update(
        {
            "font.family": resolved_families,
            "font.size": 9,
            "svg.hashsalt": "benchmark-charts",
        }
    )
    for chart in config["charts"]:
        render_chart(rows, config, chart, args.output)


if __name__ == "__main__":
    main()
