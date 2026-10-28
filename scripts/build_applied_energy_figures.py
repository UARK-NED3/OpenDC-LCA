#!/usr/bin/env python3
"""Rebuild the four Applied Energy CAS data figures as vector PDFs.

The figures are redrawn from the committed result tables in
``results/applied-energy`` so that no raw provider download is required. Each
panel reproduces the released numerical relationships only; nothing here is an
independently measured or common-method lifecycle result.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "applied-energy"
OUTPUT = ROOT / "paper" / "applied_energy_cas_overleaf"

# Released Microsoft/WSP electricity anchors and the released-workbook
# cold-plate/single-phase numerical crossover.
LOW_ANCHOR = 6.13302490385571
HIGH_ANCHOR = 524.893385656191
CROSSOVER = 96.70396926805036

AIR = "#374151"
BLUE = "#0072B2"
GREEN = "#009E73"
ORANGE = "#D55E00"
PURPLE = "#7C3AED"
GREY_DOT = "#9CA3AF"
BAR_GREY = "#94A3B8"
GRID = "#D1D5DB"
BAND = "#EFF6FB"

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 9,
        "axes.edgecolor": "#6B7280",
        "axes.linewidth": 0.8,
        "xtick.color": "#374151",
        "ytick.color": "#374151",
        "pdf.fonttype": 42,
    }
)


def read(name: str) -> list[dict[str, str]]:
    with open(RESULTS / name, encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def response_lines() -> dict[str, tuple[float, float]]:
    """Return slope and zero-intensity total intercept per cooling archetype.

    The slope is the released two-endpoint use-phase response. The intercept
    adds the released embodied burden, which does not vary with electricity
    intensity.
    """
    embodied: dict[str, float] = {}
    for row in read("table16_historical_cooling_results.csv"):
        embodied.setdefault(
            row["technology"], float(row["embodied_kgco2e_per_vcore_year"])
        )
    lines = {}
    for row in read("table31_implied_electricity_response.csv"):
        technology = row["technology"]
        lines[technology] = (
            float(row["implied_electricity_response_mwh_per_vcore_year"]),
            float(row["implied_zero_intensity_intercept_kgco2e_per_vcore_year"])
            + embodied[technology],
        )
    return lines


def figure_released_response_context() -> None:
    """Figure 2: released response lines and the eGRID electricity context."""
    lines = response_lines()
    display = (
        ("Air-cooled", "Air cooling", AIR),
        ("Cold plate", "Cold plate", BLUE),
        ("One-phase", "Single-phase immersion", GREEN),
        ("Two-phase", "Two-phase immersion", ORANGE),
    )
    intensities = [
        float(row["co2e_kg_per_mwh"])
        for row in read("table14_egrid_historical_state_factors.csv")
    ]
    xmax = 1000.0

    figure, (upper, lower) = plt.subplots(
        2,
        1,
        figsize=(6.35, 6.15),
        sharex=True,
        gridspec_kw={"height_ratios": [1.35, 1.0], "hspace": 0.08},
    )

    for axes in (upper, lower):
        axes.axvspan(LOW_ANCHOR, HIGH_ANCHOR, color=BAND, zorder=0)
        for anchor in (LOW_ANCHOR, HIGH_ANCHOR):
            axes.axvline(
                anchor,
                color="#6B7280",
                linestyle=(0, (5, 4)),
                linewidth=0.9,
                zorder=1,
            )
        axes.axvline(
            CROSSOVER, color=GREEN, linestyle=(0, (6, 4)), linewidth=1.5, zorder=2
        )
        axes.set_xlim(0, xmax)
        axes.spines["top"].set_visible(False)
        axes.spines["right"].set_visible(False)
        axes.yaxis.grid(True, color=GRID, linewidth=0.6)
        axes.set_axisbelow(True)

    for key, label, color in display:
        slope, intercept = lines[key]
        for start, stop, style in (
            (0.0, LOW_ANCHOR, (0, (6, 3))),
            (LOW_ANCHOR, HIGH_ANCHOR, "solid"),
            (HIGH_ANCHOR, xmax, (0, (6, 3))),
        ):
            upper.plot(
                [start, stop],
                [intercept + slope * start, intercept + slope * stop],
                color=color,
                linestyle=style,
                linewidth=1.9,
                label=label if style == "solid" else None,
                zorder=4,
            )
        for anchor in (LOW_ANCHOR, HIGH_ANCHOR):
            upper.plot(
                anchor,
                intercept + slope * anchor,
                marker="o",
                markersize=3.4,
                color=color,
                zorder=5,
            )

    upper.set_ylim(0, 60)
    upper.set_ylabel("Released-model climate impact\n(kg CO$_2$e/Vcore-year)")
    upper.text(
        -0.135, 1.005, "(a)", transform=upper.transAxes, fontsize=10, va="bottom"
    )
    upper.text(
        430.0, 56.8, "Interpolation", ha="center", fontsize=8.5, color="#374151"
    )
    upper.text(
        (HIGH_ANCHOR + xmax) / 2,
        56.8,
        "Extrapolation",
        ha="center",
        fontsize=8.5,
        color="#374151",
    )
    upper.text(
        CROSSOVER + 13,
        12.5,
        f"CP/1-P equality: {CROSSOVER:.1f}",
        rotation=90,
        fontsize=8,
        color=GREEN,
        va="bottom",
    )
    upper.legend(
        loc="upper left",
        bbox_to_anchor=(0.015, 0.99),
        frameon=True,
        framealpha=1.0,
        fontsize=8.5,
    )

    # Inset: the cold-plate minus single-phase difference. On the 0-60 axis of
    # panel (a) the two released lines are indistinguishable, so the equality
    # at 96.70 cannot be read off the response lines themselves.
    cold_plate_slope, cold_plate_intercept = lines["Cold plate"]
    single_slope, single_intercept = lines["One-phase"]
    inset = upper.inset_axes([0.525, 0.075, 0.435, 0.355])
    endpoints = [0.0, 250.0]
    inset.plot(
        endpoints,
        [
            (cold_plate_intercept - single_intercept)
            + (cold_plate_slope - single_slope) * value
            for value in endpoints
        ],
        color="#111827",
        linewidth=1.4,
    )
    inset.axhline(0, color="#6B7280", linewidth=0.8)
    inset.axvline(CROSSOVER, color=GREEN, linestyle=(0, (4, 3)), linewidth=1.2)
    inset.plot(CROSSOVER, 0, marker="o", markersize=4, color=GREEN, zorder=5)
    inset.text(
        CROSSOVER + 9, -0.082, f"{CROSSOVER:.2f}", fontsize=7, color=GREEN
    )
    inset.text(14, 0.062, "single-phase lower", fontsize=6.5, color="#4B5563")
    inset.text(142, -0.102, "cold plate lower", fontsize=6.5, color="#4B5563")
    inset.set_xlim(0, 250)
    inset.set_ylim(-0.14, 0.2)
    inset.set_title(
        "Cold plate minus single-phase (kg CO$_2$e/Vcore-year)",
        fontsize=7,
        pad=3,
    )
    inset.tick_params(labelsize=6.5, length=2.5, pad=1.5)
    inset.set_yticks([-0.1, 0.0, 0.1])
    inset.set_xticks([0, 100, 200])
    for side in ("top", "right"):
        inset.spines[side].set_visible(False)
    inset.set_facecolor("white")

    lower.hist(
        intensities,
        bins=[value * 25.0 for value in range(41)],
        color=BAR_GREY,
        edgecolor="white",
        linewidth=0.5,
        zorder=3,
    )
    lower.set_ylabel("State-year count")
    lower.set_xlabel(
        "Harmonized eGRID state/DC electricity carbon intensity "
        "(kg CO$_2$e/MWh)"
    )
    lower.text(
        -0.135, 1.005, "(b)", transform=lower.transAxes, fontsize=10, va="bottom"
    )

    figure.subplots_adjust(left=0.135, right=0.975, top=0.955, bottom=0.085)
    figure.savefig(OUTPUT / "figure2_released_response_context.pdf")
    plt.close(figure)


def figure_historical_grid_transition() -> None:
    """Figure 3: harmonized eGRID state/DC rates for nine releases."""
    states = read("table14_egrid_historical_state_factors.csv")
    national = read("table15_egrid_historical_national_factors.csv")
    years = sorted({int(row["year"]) for row in states})

    figure, axes = plt.subplots(figsize=(8.0, 4.51))
    axes.set_xlim(0, 1030)
    axes.set_xticks([0, 200, 400, 600, 800, 1000])
    for tick in (0, 200, 400, 600, 800, 1000):
        axes.axvline(tick, color="#E5E7EB", linewidth=0.7, zorder=0)
    for year in years:
        axes.axhline(year, color="#F3F4F6", linewidth=0.8, zorder=0)

    below = [
        (float(row["co2e_kg_per_mwh"]), int(row["year"]))
        for row in states
        if float(row["co2e_kg_per_mwh"]) < CROSSOVER
    ]
    above = [
        (float(row["co2e_kg_per_mwh"]), int(row["year"]))
        for row in states
        if float(row["co2e_kg_per_mwh"]) >= CROSSOVER
    ]
    axes.scatter(
        [point[0] for point in above],
        [point[1] for point in above],
        s=14,
        color=GREY_DOT,
        alpha=0.72,
        linewidths=0,
        zorder=2,
    )
    axes.scatter(
        [point[0] for point in below],
        [point[1] for point in below],
        s=14,
        color=BLUE,
        alpha=0.85,
        linewidths=0,
        zorder=3,
    )
    aggregate = sorted(
        (
            int(row["year"]),
            float(row["generation_weighted_co2e_kg_per_mwh"]),
        )
        for row in national
    )
    for (year, value), (next_year, next_value) in zip(aggregate, aggregate[1:]):
        # eGRID publishes no 2013, 2015, or 2017 release, so a segment
        # spanning more than one year bridges an unobserved year.
        bridged = next_year - year > 1
        axes.plot(
            [value, next_value],
            [year, next_year],
            color=ORANGE,
            linewidth=2.6,
            linestyle=(0, (2.6, 2.0)) if bridged else "solid",
            solid_capstyle="round",
            zorder=4,
        )
    axes.scatter(
        [value for _, value in aggregate],
        [year for year, _ in aggregate],
        s=26,
        color=ORANGE,
        linewidths=0,
        zorder=5,
    )
    axes.axvline(
        CROSSOVER, color=PURPLE, linestyle=(0, (6, 4)), linewidth=1.4, zorder=5
    )
    axes.text(
        CROSSOVER + 8,
        min(years) - 0.85,
        f"Cold plate/single-phase crossover: {CROSSOVER:.1f}",
        fontsize=8.5,
        color="#374151",
        va="center",
    )

    axes.set_yticks(years)
    axes.set_yticklabels([str(year) for year in years])
    # True time spacing: the 2012-2018 releases are two years apart and
    # the 2018-2023 releases one year apart.
    axes.set_ylim(max(years) + 0.6, min(years) - 1.3)
    axes.set_ylabel("eGRID release year")
    axes.set_xlabel("State total-output electricity intensity (kg CO$_2$e/MWh)")
    for side in ("top", "right"):
        axes.spines[side].set_visible(False)
    axes.set_axisbelow(True)

    figure.subplots_adjust(left=0.085, right=0.985, top=0.975, bottom=0.125)
    figure.savefig(OUTPUT / "figure6_historical_grid_transition.pdf")
    plt.close(figure)


def figure_lifecycle_electricity() -> None:
    """Figure 4: partial linked-system factors for FERC regions and the U.S."""
    rows = sorted(
        (
            row
            for row in read("table28_lifecycle_electricity_factors.csv")
            if row["region_level"] in {"FERC", "US"}
        ),
        key=lambda row: float(row["lifecycle_ar5_gwp100_kgco2e_per_mwh"]),
        reverse=True,
    )
    names = [row["region_name"] for row in rows]
    direct = [
        float(row["direct_generation_ar5_gwp100_kgco2e_per_mwh"]) for row in rows
    ]
    upstream = [
        float(row["upstream_infrastructure_ar5_gwp100_kgco2e_per_mwh"])
        for row in rows
    ]
    index = list(range(len(rows)))

    figure, axes = plt.subplots(figsize=(8.0, 5.467))
    axes.barh(index, direct, height=0.56, color=BLUE, zorder=3)
    axes.barh(index, upstream, left=direct, height=0.56, color=ORANGE, zorder=3)
    for place, (first, second) in enumerate(zip(direct, upstream)):
        axes.text(
            first + second + 7,
            place,
            f"{first + second:.1f}",
            va="center",
            fontsize=8.5,
        )

    axes.axvline(
        CROSSOVER, color=GREEN, linestyle=(0, (7, 4)), linewidth=1.6, zorder=4
    )
    axes.axvline(
        HIGH_ANCHOR, color=PURPLE, linestyle=(0, (2, 3)), linewidth=1.6, zorder=4
    )
    axes.text(
        CROSSOVER + 6,
        len(rows) - 0.3,
        f"CP/1-P crossover: {CROSSOVER:.1f}",
        fontsize=8.5,
        color=GREEN,
        va="center",
    )
    axes.text(
        HIGH_ANCHOR - 6,
        len(rows) - 0.3,
        f"Released high numerical anchor: {HIGH_ANCHOR:.1f}",
        fontsize=8.5,
        color=PURPLE,
        va="center",
        ha="right",
    )

    axes.set_yticks(index)
    axes.set_yticklabels(names)
    axes.set_ylim(-0.75, len(rows) - 0.05)
    axes.set_xlim(0, 600)
    axes.set_xticks([0, 100, 200, 300, 400, 500, 600])
    axes.set_xlabel("IPCC AR5 GWP100 (kg CO$_2$e/MWh delivered at user)")
    axes.xaxis.grid(True, color="#E5E7EB", linewidth=0.7)
    axes.set_axisbelow(True)
    for side in ("top", "right", "left"):
        axes.spines[side].set_visible(False)
    axes.tick_params(axis="y", length=0)
    axes.legend(
        handles=[
            Patch(facecolor=BLUE, label="generation processes"),
            Patch(facecolor=ORANGE, label="upstream and infrastructure"),
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.09),
        ncol=2,
        frameon=False,
        fontsize=8.5,
    )

    figure.subplots_adjust(left=0.135, right=0.975, top=0.965, bottom=0.145)
    figure.savefig(OUTPUT / "figure10_lifecycle_electricity.pdf")
    plt.close(figure)


def figure_standardized_robustness() -> None:
    """Figure 5: deterministic equal-width first-rank certificates."""
    rows = read("table29_standardized_rank_robustness.csv")
    order = (
        "grid only",
        "use phase only",
        "embodied only",
        "service equivalence only",
        "all four equal-width",
    )
    national = {
        row["active_assumption_blocks"]: row
        for row in rows
        if row["region_level"] == "US"
    }

    figure, (left, right) = plt.subplots(
        1, 2, figsize=(8.0, 4.8), gridspec_kw={"wspace": 0.4}
    )

    axis_max = 25.0
    for index, block in enumerate(order):
        value = national[block]["critical_equal_half_width_pct"]
        if value == "":
            # No reversal was found anywhere in the tested nonnegative range,
            # so the bar is open-ended rather than equal to the axis maximum.
            left.barh(
                index,
                axis_max,
                height=0.55,
                facecolor="white",
                edgecolor=BLUE,
                linewidth=1.1,
                hatch="////",
                zorder=3,
            )
            left.annotate(
                "",
                xy=(axis_max + 2.1, index),
                xytext=(axis_max, index),
                annotation_clip=False,
                arrowprops={"arrowstyle": "-|>", "color": BLUE, "linewidth": 1.1},
            )
            left.text(
                axis_max / 2,
                index,
                "no reversal through 99.999%",
                va="center",
                ha="center",
                fontsize=7.6,
                color=BLUE,
                zorder=4,
                bbox={
                    "facecolor": "white",
                    "edgecolor": "none",
                    "pad": 1.6,
                },
            )
        else:
            numeric = float(value)
            left.barh(index, numeric, height=0.55, color=BLUE, zorder=3)
            left.text(
                numeric + 0.5, index, f"{numeric:.2f}%", va="center", fontsize=8.5
            )

    left.set_yticks(range(len(order)))
    left.set_yticklabels([block[0].upper() + block[1:] for block in order])
    left.set_ylim(len(order) - 0.45, -0.55)
    left.set_xlim(0, axis_max + 2.6)
    left.set_xticks([0, 5, 10, 15, 20, 25])
    left.set_xticklabels([f"{tick}%" for tick in (0, 5, 10, 15, 20, 25)])
    left.set_xlabel("Critical half-width, $h$")
    left.xaxis.grid(True, color="#E5E7EB", linewidth=0.7)
    left.set_axisbelow(True)
    for side in ("top", "right", "left"):
        left.spines[side].set_visible(False)
    left.tick_params(axis="y", length=0)
    left.legend(
        handles=[
            Patch(facecolor=BLUE, label="finite critical half-width"),
            Patch(
                facecolor="white",
                edgecolor=BLUE,
                hatch="////",
                label="open-ended: no reversal in the tested range",
            ),
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.135),
        ncol=1,
        frameon=False,
        fontsize=7.8,
        handlelength=1.9,
        handleheight=1.2,
    )
    left.text(-0.36, 1.02, "(a)", transform=left.transAxes, fontsize=10)

    colors = {"BA": BLUE, "FERC": ORANGE, "US": GREEN}
    for level, label in (("BA", "BA"), ("FERC", "FERC"), ("US", "U.S.")):
        points = [
            (
                float(row["lifecycle_ar5_gwp100_kgco2e_per_mwh"]),
                float(row["critical_equal_half_width_pct"]),
            )
            for row in rows
            if row["active_assumption_blocks"] == "all four equal-width"
            and row["region_level"] == level
        ]
        right.scatter(
            [point[0] for point in points],
            [point[1] for point in points],
            s=18,
            color=colors[level],
            alpha=0.85,
            linewidths=0,
            label=label,
            zorder=3,
        )
    right.set_xlim(0, 1030)
    right.set_xticks([0, 200, 400, 600, 800, 1000])
    right.set_ylim(1.0, 1.6)
    right.set_yticks([1.0, 1.2, 1.4, 1.6])
    right.set_yticklabels(["1.0%", "1.2%", "1.4%", "1.6%"])
    right.set_xlabel("Lifecycle electricity factor (kg CO$_2$e/MWh)")
    right.set_ylabel("Critical half-width, $h$")
    right.grid(True, color="#E5E7EB", linewidth=0.7)
    right.set_axisbelow(True)
    for side in ("top", "right"):
        right.spines[side].set_visible(False)
    right.legend(loc="upper right", frameon=True, framealpha=1.0, fontsize=8)
    right.text(-0.22, 1.02, "(b)", transform=right.transAxes, fontsize=10)

    figure.subplots_adjust(left=0.18, right=0.975, top=0.94, bottom=0.215)
    figure.savefig(OUTPUT / "figure11_standardized_robustness.pdf")
    plt.close(figure)


def main() -> None:
    figure_released_response_context()
    figure_historical_grid_transition()
    figure_lifecycle_electricity()
    figure_standardized_robustness()
    print(f"Wrote four vector figure PDFs to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
