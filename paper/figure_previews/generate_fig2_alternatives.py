"""Generate non-production alternatives for the revised main-text Figure 2.

All curves are linear reconstructions of released Microsoft/WSP GHG endpoints.
They are numerical screening relationships, not measured cooling performance or
replacement electricity LCA models.  The script reads only derived tables that
are already retained in the manuscript package.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "paper" / "tables"
OUT = Path(__file__).resolve().parent
LOW_ANCHOR = 6.13302490385571
HIGH_ANCHOR = 524.893385656191
CROSSOVER = 96.70396924389829
COLORS = {
    "Air-cooled": "#4D5766",
    "Cold plate": "#0072B2",
    "One-phase": "#009E73",
    "Two-phase": "#D55E00",
}
LABELS = {
    "Air-cooled": "Air cooling",
    "Cold plate": "Cold plate",
    "One-phase": "Single-phase immersion",
    "Two-phase": "Two-phase immersion",
}
ORDER = ["Air-cooled", "Cold plate", "One-phase", "Two-phase"]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def fit_lines() -> dict[str, np.poly1d]:
    rows = read_rows(TABLES / "table16_historical_cooling_results.csv")
    lines: dict[str, np.poly1d] = {}
    for technology in ORDER:
        subset = [row for row in rows if row["technology"] == technology]
        x = np.array([float(row["co2e_kg_per_mwh"]) for row in subset])
        y = np.array([float(row["total_kgco2e_per_vcore_year"]) for row in subset])
        lines[technology] = np.poly1d(np.polyfit(x, y, 1))
    return lines


def style() -> None:
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 10.5,
            "axes.labelsize": 11,
            "axes.titlesize": 11,
            "legend.fontsize": 9.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def anchors(ax: plt.Axes, y_top: float, *, label: bool = True) -> None:
    ax.axvspan(LOW_ANCHOR, HIGH_ANCHOR, color="#D9EAF7", alpha=0.42, zorder=0)
    ax.axvline(LOW_ANCHOR, color="#6B7280", lw=1.0, ls="--", zorder=1)
    ax.axvline(HIGH_ANCHOR, color="#6B7280", lw=1.0, ls="--", zorder=1)
    ax.axvline(CROSSOVER, color="#009E73", lw=1.3, ls=(0, (4, 3)), zorder=1)
    if label:
        ax.text(
            330,
            y_top,
            "Released numerical anchor interval",
            ha="center",
            va="bottom",
            color="#475569",
        )
        ax.text(
            CROSSOVER + 10,
            y_top * 0.90,
            "CP/1-P equality\n96.7 kg CO$_2$e/MWh",
            ha="left",
            va="top",
            color="#007F67",
        )


def draw_lines(ax: plt.Axes, lines: dict[str, np.poly1d]) -> None:
    x_inside = np.linspace(LOW_ANCHOR, HIGH_ANCHOR, 240)
    x_outside_left = np.linspace(0, LOW_ANCHOR, 30)
    x_outside_right = np.linspace(HIGH_ANCHOR, 1000, 240)
    for technology in ORDER:
        line = lines[technology]
        ax.plot(x_inside, line(x_inside), color=COLORS[technology], lw=2.4, label=LABELS[technology])
        ax.plot(x_outside_left, line(x_outside_left), color=COLORS[technology], lw=1.4, ls="--")
        ax.plot(x_outside_right, line(x_outside_right), color=COLORS[technology], lw=1.4, ls="--")
        ax.scatter(
            [LOW_ANCHOR, HIGH_ANCHOR],
            [line(LOW_ANCHOR), line(HIGH_ANCHOR)],
            color=COLORS[technology], edgecolor="white", linewidth=0.7, s=28, zorder=4,
        )


def option_a(lines: dict[str, np.poly1d]) -> None:
    fig, ax = plt.subplots(figsize=(8.3, 4.8), constrained_layout=True)
    draw_lines(ax, lines)
    anchors(ax, 58.0)
    ax.set(xlim=(0, 1000), ylim=(0, 62), xlabel="Electricity carbon intensity (kg CO$_2$e/MWh)", ylabel="Released-model climate impact (kg CO$_2$e/Vcore-year)")
    ax.grid(axis="y", color="#D1D5DB", lw=0.7)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=2, frameon=True, facecolor="white", edgecolor="#9CA3AF")
    ax.text(805, 7.0, "Solid: interpolation\nDashed: extrapolation", ha="center", va="bottom", color="#4B5563")
    fig.savefig(OUT / "fig2_option_a_response_lines.png", dpi=240)
    plt.close(fig)


def option_b(lines: dict[str, np.poly1d]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.1, 4.55), gridspec_kw={"width_ratios": [1.35, 1]}, constrained_layout=True)
    ax, diff_ax = axes
    draw_lines(ax, lines)
    anchors(ax, 57.5, label=False)
    ax.set(xlim=(0, 850), ylim=(0, 60), xlabel="Electricity carbon intensity (kg CO$_2$e/MWh)", ylabel="Released-model climate impact\n(kg CO$_2$e/Vcore-year)")
    ax.grid(axis="y", color="#D1D5DB", lw=0.7)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.17), ncol=2, frameon=True, facecolor="white", edgecolor="#9CA3AF")
    ax.text(410, 56.8, "Shading: released anchor interval", ha="center", color="#475569")

    x = np.linspace(0, 850, 500)
    difference = lines["One-phase"](x) - lines["Cold plate"](x)
    diff_ax.axhline(0, color="#374151", lw=0.9)
    diff_ax.axvspan(LOW_ANCHOR, HIGH_ANCHOR, color="#D9EAF7", alpha=0.42, zorder=0)
    diff_ax.plot(x, difference, color="#6D28D9", lw=2.3)
    diff_ax.axvline(CROSSOVER, color="#009E73", lw=1.3, ls=(0, (4, 3)))
    diff_ax.scatter([LOW_ANCHOR, HIGH_ANCHOR], [lines["One-phase"](LOW_ANCHOR) - lines["Cold plate"](LOW_ANCHOR), lines["One-phase"](HIGH_ANCHOR) - lines["Cold plate"](HIGH_ANCHOR)], color="#6D28D9", edgecolor="white", linewidth=0.7, s=28, zorder=4)
    diff_ax.set(xlim=(0, 850), ylim=(-2.1, 2.1), xlabel="Electricity carbon intensity\n(kg CO$_2$e/MWh)", ylabel="Single-phase minus cold-plate impact\n(kg CO$_2$e/Vcore-year)")
    diff_ax.grid(axis="y", color="#D1D5DB", lw=0.7)
    diff_ax.text(CROSSOVER + 15, 1.88, "Equal at 96.7", color="#007F67")
    diff_ax.text(500, 1.22, "Positive: cold plate lower", ha="center", color="#4B5563")
    diff_ax.text(500, -1.46, "Negative: single-phase lower", ha="center", color="#4B5563")
    fig.savefig(OUT / "fig2_option_b_crossover_explained.png", dpi=240)
    plt.close(fig)


def option_c(lines: dict[str, np.poly1d]) -> None:
    state_rows = read_rows(TABLES / "table14_egrid_historical_state_factors.csv")
    values = np.array([float(row["co2e_kg_per_mwh"]) for row in state_rows])
    fig, axes = plt.subplots(2, 1, figsize=(6.35, 6.15), height_ratios=[1.45, 1], constrained_layout=True)
    ax, hist_ax = axes
    draw_lines(ax, lines)
    anchors(ax, 57.3, label=False)
    ax.set(xlim=(0, 1000), ylim=(0, 60), ylabel="Released-model climate impact\n(kg CO$_2$e/Vcore-year)")
    ax.grid(axis="y", color="#D1D5DB", lw=0.7)
    ax.legend(ncol=1, loc="lower right", frameon=True, facecolor="white", edgecolor="#9CA3AF", framealpha=1.0)
    ax.text(CROSSOVER + 10, 52.4, "CP/1-P equality: 96.7", color="#007F67", fontsize=10)
    ax.text(240, 59.0, "Interpolation", ha="center", va="top", color="black", fontsize=10)
    ax.text(760, 59.0, "Extrapolation", ha="center", va="top", color="black", fontsize=10)
    ax.text(-0.075, 1.025, "(a)", transform=ax.transAxes, ha="left", va="bottom", fontsize=11, clip_on=False)

    bins = np.arange(0, 1025, 25)
    hist_ax.hist(values, bins=bins, color="#94A3B8", edgecolor="white", linewidth=0.5)
    hist_ax.axvspan(LOW_ANCHOR, HIGH_ANCHOR, color="#D9EAF7", alpha=0.42, zorder=0)
    hist_ax.axvline(LOW_ANCHOR, color="#6B7280", lw=1.0, ls="--")
    hist_ax.axvline(HIGH_ANCHOR, color="#6B7280", lw=1.0, ls="--")
    hist_ax.axvline(CROSSOVER, color="#009E73", lw=1.3, ls=(0, (4, 3)))
    hist_ax.set(xlim=(0, 1000), xlabel="Harmonized eGRID state/DC electricity carbon intensity (kg CO$_2$e/MWh)", ylabel="State-year count")
    hist_ax.text(-0.075, 1.025, "(b)", transform=hist_ax.transAxes, ha="left", va="bottom", fontsize=11, clip_on=False)
    for axis in axes:
        for spine in axis.spines.values():
            spine.set_visible(True)
            spine.set_color("#374151")
            spine.set_linewidth(0.9)
    fig.savefig(OUT / "fig2_option_c_response_and_context.png", dpi=240)
    fig.savefig(OUT / "fig2_option_c_response_and_context.pdf")
    plt.close(fig)


def main() -> None:
    style()
    lines = fit_lines()
    option_a(lines)
    option_b(lines)
    option_c(lines)


if __name__ == "__main__":
    main()
