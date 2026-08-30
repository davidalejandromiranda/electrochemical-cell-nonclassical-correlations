"""Load the released EIS exports and reproduce the manuscript data figures.

The functions in this module never modify the Excel exports and never save figure
files unless a caller explicitly chooses to do so. Plot-specific point limits are
the display selections used by the historical analysis notebook; the complete
acquired series remain available in ``data/``.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from collections.abc import Mapping
from math import pi
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator
import numpy as np
import pandas as pd

from scr.figure_styles import FIGURE_STYLES


MICRO = 1e6
BODE_FREQUENCY_LIMITS = (0.1, 1.0e6)
DUMMY_RESONANCE = FIGURE_STYLES["figure_7"]["bode"]["dummy_resonance"]
REQUIRED_COLUMNS = (
    "Index",
    "C' (F)",
    "C'' (F)",
    "Frequency (Hz)",
    "Z' (Ω)",
    "-Z'' (Ω)",
    "Z (Ω)",
    "-Phase (°)",
    "Time (s)",
)

EXPECTED_EXPORTS = {
    "Main_Fig4/R 10kOhm - C 1microFarad.xlsx": (60, 1.0e5, 0.1),
    "Main_Fig4/R 10kOhm.xlsx": (60, 1.0e5, 0.1),
    "Main_Fig4/R 1kOhm - C 1microFarad.xlsx": (60, 1.0e5, 0.1),
    "Main_Fig4/R 1kOhm.xlsx": (60, 1.0e5, 0.1),
    "Main_Fig4/R 3kOhm - C 1microFarad.xlsx": (60, 1.0e5, 0.1),
    "Main_Fig4/R 3kOhm.xlsx": (60, 1.0e5, 0.1),
    "Main_Fig4/R 47kOhm.xlsx": (60, 1.0e5, 0.1),
    "Main_Fig4/Sin protoboard.xlsx": (60, 1.0e5, 0.1),
    "Main_Fig5/Configuration1_Bar1WE.xlsx": (80, 1.0e6, 0.1),
    "Main_Fig5/Configuration1_Bar2WE.xlsx": (80, 1.0e6, 0.1),
    "Main_Fig5/Configuration2.xlsx": (80, 1.0e6, 0.1),
    "Main_Fig6-7/Configuration 1.xlsx": (80, 1.0e6, 0.1),
    "Main_Fig6-7/Configuration 2 + dummy on CE.xlsx": (80, 1.0e6, 0.1),
    "Main_Fig6-7/Configuration 3 + dummy on CE.xlsx": (80, 1.0e6, 0.1),
    "Main_Fig6-7/Configuration 3.xlsx": (80, 1.0e6, 0.1),
    "Supplementary_Fig1/Configuration1.xlsx": (80, 1.0e6, 0.1),
    "Supplementary_Fig1/Configuration3.xlsx": (80, 1.0e6, 0.1),
    "Supplementary_Fig2/Configuration1.xlsx": (80, 1.0e6, 0.1),
    "Supplementary_Fig2/Configuration3.xlsx": (80, 1.0e6, 0.1),
    "Supplementary_Fig3/Configuration1.xlsx": (80, 1.0e6, 0.1),
    "Supplementary_Fig3/Configuration3.xlsx": (80, 1.0e6, 0.1),
    "Supplementary_Fig4/Configuration1.xlsx": (80, 1.0e6, 0.1),
    "Supplementary_Fig4/Configuration3.xlsx": (80, 1.0e6, 0.1),
}



def _deep_merge(base: dict, updates: Mapping | None) -> dict:
    result = deepcopy(base)
    if updates is None:
        return result
    for key, value in updates.items():
        if isinstance(value, Mapping) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


STYLE_ALIASES = {"configuration_1_vs_3": "figure_6"}


def figure_style(style_name: str, overrides: Mapping | None = None) -> dict:
    """Return a mutable copy of a figure style from ``scr.figure_styles``."""
    resolved_name = STYLE_ALIASES.get(style_name, style_name)
    if resolved_name not in FIGURE_STYLES:
        available = ", ".join(sorted(FIGURE_STYLES))
        raise KeyError(f"Unknown style {style_name!r}; available styles: {available}")
    return _deep_merge(FIGURE_STYLES[resolved_name], overrides)


def _scatter_kwargs(series_style: Mapping, *, label: str | None = None) -> dict:
    keys = ("color", "marker", "s", "alpha", "edgecolors", "facecolors", "linewidths")
    kwargs = {key: series_style[key] for key in keys if key in series_style}
    marker = kwargs.get("marker")
    marker_fill = series_style.get("marker_fill", series_style.get("fill", False))
    unfillable_markers = {"x", "+", "1", "2", "3", "4", "|", "_"}
    if marker_fill is False and marker not in unfillable_markers:
        kwargs.setdefault("facecolors", "none")
        if "color" in kwargs:
            kwargs.setdefault("edgecolors", kwargs["color"])
    kwargs["label"] = series_style.get("label") if label is None else label
    return kwargs


def _line_kwargs(series_style: Mapping, *, label: str | None = None) -> dict:
    keys = ("color", "linestyle", "linewidth", "alpha")
    kwargs = {key: series_style[key] for key in keys if key in series_style}
    if series_style.get("show_line") is True and kwargs.get("linestyle") in (None, "", "None", "none"):
        kwargs["linestyle"] = "-"
    kwargs["label"] = series_style.get("label") if label is None else label
    return kwargs


def _style_has_line(series_style: Mapping) -> bool:
    if series_style.get("show") is False:
        return False
    if series_style.get("show_line") is False:
        return False
    if series_style.get("show_line") is True:
        return True
    linestyle = series_style.get("linestyle")
    return linestyle not in (None, "", "None", "none")


def _style_has_marker(series_style: Mapping) -> bool:
    if series_style.get("show") is False:
        return False
    return series_style.get("show_marker", True) is not False


def _plot_line(axis, x, y, series_style: Mapping, *, label: str | None = None):
    if _style_has_line(series_style):
        return axis.plot(x, y, **_line_kwargs(series_style, label=label))
    return None


def _plot_points(axis, x, y, series_style: Mapping, *, label: str | None = None):
    _plot_line(axis, x, y, series_style, label="_nolegend_")
    if _style_has_marker(series_style):
        return axis.scatter(x, y, **_scatter_kwargs(series_style, label=label))
    return None


def _apply_legend(axis, legend_style: Mapping) -> None:
    if legend_style.get("show", True):
        axis.legend(**legend_style.get("kwargs", {}))


def _apply_axis_title(axis, title: str | None, **kwargs) -> None:
    if title:
        axis.set_title(title, **kwargs)


def _capacitance_axes(figsize: tuple[float, float], dpi: int, panel_box_aspect: float):
    figure = plt.figure(figsize=figsize, dpi=dpi)
    nyquist_width = 0.38
    bode_width = 0.38
    nyquist_height = nyquist_width * figsize[0] * panel_box_aspect / figsize[1]
    bode_height = nyquist_height * 0.45
    bottom = 0.16
    left = 0.07
    gap = 0.05
    vertical_gap = nyquist_height * 0.10
    bode_left = left + nyquist_width + gap
    nyquist_axis = figure.add_axes([left, bottom, nyquist_width, nyquist_height])
    bode_real_axis = figure.add_axes(
        [bode_left, bottom + bode_height + vertical_gap, bode_width, bode_height]
    )
    bode_imag_axis = figure.add_axes([bode_left, bottom, bode_width, bode_height], sharex=bode_real_axis)
    return figure, nyquist_axis, bode_real_axis, bode_imag_axis


def _format_bode_axis(axis, bode_style: Mapping, ylabel: str, *, xlabel: bool = False) -> None:
    if xlabel:
        axis.set_xlabel("Frequency [Hz]")
    axis.set_ylabel(ylabel, labelpad=8)
    axis.yaxis.set_label_position("right")
    axis.yaxis.tick_right()
    axis.set_xscale("log")
    axis.set_xlim(*bode_style.get("x_limits", BODE_FREQUENCY_LIMITS))
    if "y_limits" in bode_style:
        axis.set_ylim(*bode_style["y_limits"])
    if "y_step" in bode_style:
        axis.yaxis.set_major_locator(MultipleLocator(bode_style["y_step"]))


def _format_bode_axes(real_axis, imaginary_axis, bode_style: Mapping) -> None:
    _format_bode_axis(real_axis, bode_style, r"C' [$\mu F$]")
    _format_bode_axis(imaginary_axis, bode_style, r"C'' [$\mu F$]", xlabel=True)
    plt.setp(real_axis.get_xticklabels(), visible=False)
    _plot_dummy_resonance(imaginary_axis, bode_style.get("dummy_resonance", {}))


def _dummy_resonance_frequency(resonance_style: Mapping) -> float:
    resistance = float(
        resonance_style.get(
            "parallel_resistance_ohm",
            resonance_style.get("resistance_ohm", DUMMY_RESONANCE["parallel_resistance_ohm"]),
        )
    )
    capacitance = float(resonance_style.get("capacitance_f", DUMMY_RESONANCE["capacitance_f"]))
    return 1.0 / (2.0 * pi * resistance * capacitance)


def _plot_dummy_resonance(axis, resonance_style: Mapping) -> None:
    if not resonance_style.get("show", False):
        return
    frequency = _dummy_resonance_frequency(resonance_style)
    keys = ("color", "linestyle", "linewidth", "alpha")
    line_kwargs = {key: resonance_style[key] for key in keys if key in resonance_style}
    line_kwargs["label"] = resonance_style.get("label", DUMMY_RESONANCE["label"])
    axis.axvline(frequency, **line_kwargs)
    if resonance_style.get("annotate", False):
        axis.annotate(
            resonance_style.get("annotation", DUMMY_RESONANCE["annotation"]),
            xy=(frequency, 0.96),
            xycoords=("data", "axes fraction"),
            xytext=(4, 0),
            textcoords="offset points",
            rotation=90,
            va="top",
            ha="left",
            fontsize=resonance_style.get("fontsize", 8),
            color=resonance_style.get("color", "black"),
        )


def _plot_capacitance_panels(
    nyquist_axis,
    bode_real_axis,
    bode_imaginary_axis,
    frequency,
    capacitance_real,
    capacitance_imaginary,
    series_style: Mapping,
):
    _plot_points(nyquist_axis, capacitance_real * MICRO, capacitance_imaginary * MICRO, series_style)
    _plot_points(bode_real_axis, frequency, capacitance_real * MICRO, series_style)
    _plot_points(bode_imaginary_axis, frequency, capacitance_imaginary * MICRO, series_style)


def _plot_capacitance_bode(
    bode_real_axis,
    bode_imaginary_axis,
    frequency,
    capacitance_real,
    capacitance_imaginary,
    series_style: Mapping,
):
    _plot_points(bode_real_axis, frequency, capacitance_real * MICRO, series_style)
    _plot_points(bode_imaginary_axis, frequency, capacitance_imaginary * MICRO, series_style)


def read_eis_export(path: str | Path) -> pd.DataFrame:
    """Read and validate one released Excel export without changing it."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Missing EIS export: {path}")

    frame = pd.read_excel(path, sheet_name="Sheet1")
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"{path} is missing required columns: {missing}")

    frame = frame.loc[:, REQUIRED_COLUMNS].copy()
    for column in REQUIRED_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    if frame.isna().any().any():
        raise ValueError(f"{path} contains missing values")

    frequency = frame["Frequency (Hz)"].to_numpy(dtype=float)
    if len(frequency) < 2 or not np.all(np.diff(frequency) < 0):
        raise ValueError(f"{path} frequencies are not strictly descending")
    return frame


def _export(data_root: str | Path, relative_path: str) -> pd.DataFrame:
    return read_eis_export(Path(data_root) / Path(relative_path))


def _capacitance(frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Return potentiostat-exported capacitance components without recalculation."""
    return (
        frame["C' (F)"].to_numpy(dtype=float),
        frame["C'' (F)"].to_numpy(dtype=float),
    )


def _frequency(frame: pd.DataFrame) -> np.ndarray:
    return frame["Frequency (Hz)"].to_numpy(dtype=float)


def _impedance(frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    return (
        frame["Z' (Ω)"].to_numpy(dtype=float),
        frame["-Z'' (Ω)"].to_numpy(dtype=float),
    )


def _assert_same_frequency(*frames: pd.DataFrame) -> None:
    reference = frames[0]["Frequency (Hz)"].to_numpy(dtype=float)
    for frame in frames[1:]:
        candidate = frame["Frequency (Hz)"].to_numpy(dtype=float)
        if reference.shape != candidate.shape or not np.allclose(reference, candidate):
            raise ValueError("Frequency grids differ for inputs used in one calculation")


def sha256_file(path: str | Path) -> str:
    """Return the SHA-256 digest of a file."""
    digest = sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_raw_hashes(data_root: str | Path, manifest_path: str | Path) -> pd.DataFrame:
    """Verify all released exports against the recorded SHA-256 manifest."""
    data_root = Path(data_root)
    manifest = pd.read_csv(manifest_path)
    required = {"relative_path", "sha256"}
    if not required.issubset(manifest.columns):
        raise ValueError(f"Hash manifest must contain columns {sorted(required)}")

    rows = []
    for record in manifest.itertuples(index=False):
        path = data_root / Path(record.relative_path)
        actual = sha256_file(path)
        expected = str(record.sha256).lower()
        rows.append(
            {
                "relative_path": record.relative_path,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "matches": actual == expected,
            }
        )
    result = pd.DataFrame(rows)
    if len(result) != len(EXPECTED_EXPORTS) or not result["matches"].all():
        raise ValueError("Raw-data hash verification failed")
    return result


def validate_raw_dataset(data_root: str | Path) -> pd.DataFrame:
    """Validate file coverage, rows, columns, and acquired frequency ranges."""
    data_root = Path(data_root)
    found = {
        path.relative_to(data_root).as_posix()
        for path in data_root.rglob("*.xlsx")
    }
    expected = set(EXPECTED_EXPORTS)
    if found != expected:
        raise ValueError(
            f"Unexpected raw-data coverage; missing={sorted(expected - found)}, "
            f"extra={sorted(found - expected)}"
        )

    summaries = []
    for relative_path, (expected_rows, expected_max, expected_min) in EXPECTED_EXPORTS.items():
        frame = _export(data_root, relative_path)
        frequency = frame["Frequency (Hz)"].to_numpy(dtype=float)
        if len(frame) != expected_rows:
            raise ValueError(f"{relative_path}: expected {expected_rows} rows, found {len(frame)}")
        if not np.isclose(frequency[0], expected_max) or not np.isclose(frequency[-1], expected_min):
            raise ValueError(f"{relative_path}: unexpected frequency range")
        summaries.append(
            {
                "relative_path": relative_path,
                "rows": len(frame),
                "frequency_max_hz": frequency[0],
                "frequency_min_hz": frequency[-1],
            }
        )
    return pd.DataFrame(summaries)


def plot_figure_4(data_root: str | Path = "data", style: Mapping | None = None) -> Figure:
    """Reproduce main Figure 4: potentiostat/dummy-cell validation."""
    figure_style_config = figure_style("figure_4", style)
    series_styles = figure_style_config["series"]
    specifications = [
        ("Sin protoboard.xlsx", "without_network"),
        ("R 1kOhm.xlsx", "r_1k"),
        ("R 1kOhm - C 1microFarad.xlsx", "r_1k_c_1uf"),
        ("R 3kOhm.xlsx", "r_3k"),
        ("R 3kOhm - C 1microFarad.xlsx", "r_3k_c_1uf"),
        ("R 10kOhm.xlsx", "r_10k"),
        ("R 10kOhm - C 1microFarad.xlsx", "r_10k_c_1uf"),
        ("R 47kOhm.xlsx", "r_47k"),
    ]
    datasets = []
    for filename, style_key in specifications:
        real, imaginary = _impedance(_export(data_root, f"Main_Fig4/{filename}"))
        datasets.append((real, imaginary, series_styles[style_key]))

    figure = plt.figure(figsize=(12, 10), dpi=100)
    positions = [
        [0.06, 0.68, 0.18, 0.18], [0.29, 0.68, 0.18, 0.18],
        [0.52, 0.68, 0.18, 0.18], [0.75, 0.68, 0.18, 0.18],
        [0.06, 0.52, 0.18, 0.18], [0.29, 0.52, 0.18, 0.18],
        [0.52, 0.52, 0.18, 0.18], [0.75, 0.52, 0.18, 0.18],
    ]
    axes = []
    for position, (real, imaginary, series_style) in zip(positions, datasets):
        axis = figure.add_axes(position)
        axes.append(axis)
        _plot_points(axis, real, imaginary, series_style)
        _apply_axis_title(axis, series_style.get("title"), fontsize=9)
        axis.set_xlim(101, 1091)
        axis.set_xticks([101, 1091])
        axis.set_aspect("equal")
    for axis in axes[4:]:
        axis.set_xlabel(r"Z' [$\Omega$]")
    for axis in (axes[0], axes[4]):
        axis.set_ylabel(r"Z'' [$\Omega$]")

    main_axis = figure.add_axes([0.22, 0.17, 0.53, 0.32])
    first_real = datasets[0][0]
    offset = 0.003 * (max(first_real) - min(first_real))
    angles = np.linspace(0, 2 * np.pi, 8, endpoint=False)
    dx = offset * np.cos(angles)
    dy = offset * np.sin(angles)

    r_inf = 101.0
    delta_r = 990.0
    theta = np.linspace(0, np.pi, 500)
    center = r_inf + delta_r / 2
    radius = delta_r / 2
    main_axis.plot(
        center + radius * np.cos(theta),
        radius * np.sin(theta),
        **_line_kwargs(figure_style_config["model"]),
    )

    point_count = min(len(real) for real, *_ in datasets)
    for point_index in range(point_count):
        for data_index in ((point_index + index) % 8 for index in range(8)):
            real, imaginary, series_style = datasets[data_index]
            _plot_points(
                main_axis,
                real[point_index] + dx[data_index],
                imaginary[point_index] + dy[data_index],
                series_style,
                label=series_style["label"] if point_index == 0 else "_nolegend_",
            )

    main_axis.set_xlabel(r"Z' [$\Omega$]")
    main_axis.set_ylabel(r"Z'' [$\Omega$]")
    main_axis.set_xlim(0, 1200)
    main_axis.set_xticks([0, 101, 200, 400, 600, 800, 1000, 1091, 1200])
    main_axis.set_aspect("equal")
    _apply_axis_title(main_axis, figure_style_config.get("title"))
    _apply_legend(main_axis, figure_style_config["legend"])
    return figure


def plot_figure_5(data_root: str | Path = "data", style: Mapping | None = None) -> Figure:
    """Reproduce main Figure 5: measured and calculated two-electrode response."""
    figure_style_config = figure_style("figure_5", style)
    series_styles = figure_style_config["series"]
    bar_1 = _export(data_root, "Main_Fig5/Configuration1_Bar1WE.xlsx")
    bar_2 = _export(data_root, "Main_Fig5/Configuration1_Bar2WE.xlsx")
    configuration_2 = _export(data_root, "Main_Fig5/Configuration2.xlsx")
    _assert_same_frequency(bar_1, bar_2, configuration_2)
    frequency = _frequency(configuration_2)
    real_1, imaginary_1 = _capacitance(bar_1)
    real_2, imaginary_2 = _capacitance(bar_2)
    measured_real, measured_imaginary = _capacitance(configuration_2)
    capacitance_1 = real_1 - 1j * imaginary_1
    capacitance_2 = real_2 - 1j * imaginary_2
    equivalent = capacitance_1 * capacitance_2 / (capacitance_1 + capacitance_2)

    display_slice = slice(None, 78)
    figure, nyquist_axis, bode_real_axis, bode_imaginary_axis = _capacitance_axes(
        (10, 3.7), 120, figure_style_config.get("panel_box_aspect", 0.65)
    )
    _plot_capacitance_panels(
        nyquist_axis,
        bode_real_axis,
        bode_imaginary_axis,
        frequency[display_slice],
        measured_real[display_slice],
        measured_imaginary[display_slice],
        series_styles["configuration_2"],
    )
    _plot_points(
        nyquist_axis,
        equivalent.real[display_slice] * MICRO,
        -equivalent.imag[display_slice] * MICRO,
        series_styles["c_eq_points"],
    )
    _plot_points(
        bode_real_axis,
        frequency[display_slice],
        equivalent.real[display_slice] * MICRO,
        series_styles["c_eq_points"],
    )
    _plot_points(
        bode_imaginary_axis,
        frequency[display_slice],
        -equivalent.imag[display_slice] * MICRO,
        series_styles["c_eq_points"],
    )
    _plot_line(
        nyquist_axis,
        equivalent.real[display_slice] * MICRO,
        -equivalent.imag[display_slice] * MICRO,
        series_styles["c_eq_line"],
    )
    _plot_line(
        bode_real_axis,
        frequency[display_slice],
        equivalent.real[display_slice] * MICRO,
        series_styles["c_eq_line"],
    )
    _plot_line(
        bode_imaginary_axis,
        frequency[display_slice],
        -equivalent.imag[display_slice] * MICRO,
        series_styles["c_eq_line"],
    )
    _format_capacitance_axis(nyquist_axis, (-0.05, 2.6), (-0.05, 0.8), 0.5, 0.5)
    _format_bode_axes(bode_real_axis, bode_imaginary_axis, figure_style_config["bode"])
    _apply_axis_title(nyquist_axis, figure_style_config.get("title"))
    _apply_axis_title(bode_real_axis, figure_style_config["bode"].get("title"))
    _apply_legend(nyquist_axis, figure_style_config["legend"])
    _apply_legend(bode_real_axis, figure_style_config["bode"]["legend"])
    return figure


def plot_figure_6(data_root: str | Path = "data", style: Mapping | None = None) -> Figure:
    """Reproduce main Figure 6: Configuration 1 versus Configuration 3."""
    figure_style_config = figure_style("configuration_1_vs_3", style)
    series_styles = figure_style_config["series"]
    configuration_1_frame = _export(data_root, "Main_Fig6-7/Configuration 1.xlsx")
    configuration_3_frame = _export(data_root, "Main_Fig6-7/Configuration 3.xlsx")
    configuration_1 = _capacitance(configuration_1_frame)
    configuration_3 = _capacitance(configuration_3_frame)
    configuration_1_slice = slice(None, 67)
    configuration_3_slice = slice(None, 66)
    figure, nyquist_axis, bode_real_axis, bode_imaginary_axis = _capacitance_axes(
        (10, 3.7), 140, figure_style_config.get("panel_box_aspect", 0.65)
    )
    _plot_capacitance_panels(
        nyquist_axis,
        bode_real_axis,
        bode_imaginary_axis,
        _frequency(configuration_1_frame)[configuration_1_slice],
        configuration_1[0][configuration_1_slice],
        configuration_1[1][configuration_1_slice],
        series_styles["configuration_1"],
    )
    _plot_capacitance_panels(
        nyquist_axis,
        bode_real_axis,
        bode_imaginary_axis,
        _frequency(configuration_3_frame)[configuration_3_slice],
        configuration_3[0][configuration_3_slice],
        configuration_3[1][configuration_3_slice],
        series_styles["configuration_3"],
    )
    _format_capacitance_axis(nyquist_axis, (-0.01, 1.8), (-0.01, 0.6), 0.25, 0.25)
    _format_bode_axes(bode_real_axis, bode_imaginary_axis, figure_style_config["bode"])
    _apply_axis_title(nyquist_axis, figure_style_config.get("title"))
    _apply_axis_title(bode_real_axis, figure_style_config["bode"].get("title"))
    _apply_legend(nyquist_axis, figure_style_config["legend"])
    _apply_legend(bode_real_axis, figure_style_config["bode"]["legend"])
    return figure


def plot_figure_7(data_root: str | Path = "data", style: Mapping | None = None) -> Figure:
    """Reproduce main Figure 7: passive dummy-cell control."""
    figure_style_config = figure_style("figure_7", style)
    series_styles = figure_style_config["series"]
    configuration_3_dummy_frame = _export(data_root, "Main_Fig6-7/Configuration 3 + dummy on CE.xlsx")
    configuration_3_frame = _export(data_root, "Main_Fig6-7/Configuration 3.xlsx")
    configuration_2_dummy_frame = _export(data_root, "Main_Fig6-7/Configuration 2 + dummy on CE.xlsx")
    configuration_3_dummy = _capacitance(configuration_3_dummy_frame)
    configuration_3 = _capacitance(configuration_3_frame)
    configuration_2_dummy = _capacitance(configuration_2_dummy_frame)
    configuration_3_dummy_slice = slice(None, 67)
    configuration_3_slice = slice(None, 66)
    configuration_2_dummy_slice = slice(None, 69)
    figure, nyquist_axis, bode_real_axis, bode_imaginary_axis = _capacitance_axes(
        (10, 3.7), 140, figure_style_config.get("panel_box_aspect", 0.65)
    )
    _plot_capacitance_panels(
        nyquist_axis,
        bode_real_axis,
        bode_imaginary_axis,
        _frequency(configuration_3_dummy_frame)[configuration_3_dummy_slice],
        configuration_3_dummy[0][configuration_3_dummy_slice],
        configuration_3_dummy[1][configuration_3_dummy_slice],
        series_styles["configuration_3_dummy"],
    )
    _plot_capacitance_panels(
        nyquist_axis,
        bode_real_axis,
        bode_imaginary_axis,
        _frequency(configuration_3_frame)[configuration_3_slice],
        configuration_3[0][configuration_3_slice],
        configuration_3[1][configuration_3_slice],
        series_styles["configuration_3"],
    )
    _plot_capacitance_panels(
        nyquist_axis,
        bode_real_axis,
        bode_imaginary_axis,
        _frequency(configuration_2_dummy_frame)[configuration_2_dummy_slice],
        configuration_2_dummy[0][configuration_2_dummy_slice],
        configuration_2_dummy[1][configuration_2_dummy_slice],
        series_styles["configuration_2_dummy"],
    )
    configuration_1_style = series_styles.get("configuration_1_pt_ce", {})
    if configuration_1_style.get("show", False):
        configuration_1_frame = _export(data_root, "Main_Fig6-7/Configuration 1.xlsx")
        configuration_1 = _capacitance(configuration_1_frame)
        configuration_1_slice = slice(None, 67)
        _plot_capacitance_panels(
            nyquist_axis,
            bode_real_axis,
            bode_imaginary_axis,
            _frequency(configuration_1_frame)[configuration_1_slice],
            configuration_1[0][configuration_1_slice],
            configuration_1[1][configuration_1_slice],
            configuration_1_style,
        )
    _format_capacitance_axis(nyquist_axis, (-0.01, 0.75), (-0.01, 0.25), 0.25, 0.25)
    _format_bode_axes(bode_real_axis, bode_imaginary_axis, figure_style_config["bode"])
    _apply_axis_title(nyquist_axis, figure_style_config.get("title"))
    _apply_axis_title(bode_real_axis, figure_style_config["bode"].get("title"))
    _apply_legend(nyquist_axis, figure_style_config["legend"])
    _apply_legend(bode_real_axis, figure_style_config["bode"]["legend"])
    return figure


def _format_capacitance_axis(axis, x_limits, y_limits, x_step, y_step) -> None:
    axis.set_xlabel(r"C' [$\mu F$]")
    axis.set_ylabel(r"C'' [$\mu F$]")
    axis.set_xlim(*x_limits)
    axis.set_ylim(*y_limits)
    axis.xaxis.set_major_locator(MultipleLocator(x_step))
    axis.yaxis.set_major_locator(MultipleLocator(y_step))


def _plot_supplementary_pair(
    data_root: str | Path,
    folder: str,
    green_points: int | None,
    red_points: int | None,
    x_limits: tuple[float, float],
    y_limits: tuple[float, float],
    x_step: float,
    y_step: float,
    style: Mapping | None = None,
) -> Figure:
    figure_style_config = figure_style("supplementary_pair", style)
    series_styles = figure_style_config["series"]
    green_frame = _export(data_root, f"{folder}/Configuration1.xlsx")
    red_frame = _export(data_root, f"{folder}/Configuration3.xlsx")
    green = _capacitance(green_frame)
    red = _capacitance(red_frame)
    green_slice = slice(None, green_points)
    red_slice = slice(None, red_points)
    figure, nyquist_axis, bode_real_axis, bode_imaginary_axis = _capacitance_axes(
        (10, 3.7), 120, figure_style_config.get("panel_box_aspect", 0.65)
    )
    _plot_capacitance_panels(
        nyquist_axis,
        bode_real_axis,
        bode_imaginary_axis,
        _frequency(green_frame)[green_slice],
        green[0][green_slice],
        green[1][green_slice],
        series_styles["configuration_1"],
    )
    _plot_capacitance_panels(
        nyquist_axis,
        bode_real_axis,
        bode_imaginary_axis,
        _frequency(red_frame)[red_slice],
        red[0][red_slice],
        red[1][red_slice],
        series_styles["configuration_3"],
    )
    _format_capacitance_axis(nyquist_axis, x_limits, y_limits, x_step, y_step)
    _format_bode_axes(bode_real_axis, bode_imaginary_axis, figure_style_config["bode"])
    _apply_axis_title(nyquist_axis, figure_style_config.get("title"))
    _apply_axis_title(bode_real_axis, figure_style_config["bode"].get("title"))
    _apply_legend(nyquist_axis, figure_style_config["legend"])
    _apply_legend(bode_real_axis, figure_style_config["bode"]["legend"])
    return figure


def plot_supplementary_figure_1(data_root: str | Path = "data", style: Mapping | None = None) -> Figure:
    return _plot_supplementary_pair(
        data_root, "Supplementary_Fig1", 71, 73,
        (-0.05, 7.0), (-0.05, 2.2), 1.0, 1.0,
        style,
    )


def plot_supplementary_figure_2(data_root: str | Path = "data", style: Mapping | None = None) -> Figure:
    return _plot_supplementary_pair(
        data_root, "Supplementary_Fig2", 70, 70,
        (-0.03, 2.5), (-0.03, 0.8), 0.5, 0.5,
        style,
    )


def plot_supplementary_figure_3(data_root: str | Path = "data", style: Mapping | None = None) -> Figure:
    return _plot_supplementary_pair(
        data_root, "Supplementary_Fig3", None, None,
        (-0.3, 25.0), (-0.3, 12.0), 5.0, 5.0,
        style,
    )


def plot_supplementary_figure_4(data_root: str | Path = "data", style: Mapping | None = None) -> Figure:
    return _plot_supplementary_pair(
        data_root, "Supplementary_Fig4", 65, 75,
        (-0.2e-6, 6.5), (-0.1e-6, 3.0), 1.0, 1.0,
        style,
    )


FIGURE_FUNCTIONS = {
    "Figure 4": plot_figure_4,
    "Figure 5": plot_figure_5,
    "Figure 6": plot_figure_6,
    "Figure 7": plot_figure_7,
    "Figure S1": plot_supplementary_figure_1,
    "Figure S2": plot_supplementary_figure_2,
    "Figure S3": plot_supplementary_figure_3,
    "Figure S4": plot_supplementary_figure_4,
}
