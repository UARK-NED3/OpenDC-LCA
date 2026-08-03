"""Dependency-free reproducible reports and SVG figures."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path

from .engine import Result, analyze, sensitivity
from .models import Scenario
from .performance import PerformancePoint, PerformanceSummary
from .uncertainty import MonteCarloResult

COLORS = ("#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00")


def _svg_text(x: float, y: float, text: str, **attrs: object) -> str:
    attributes = " ".join(
        f'{key.replace("_", "-")}="{escape(str(value))}"'
        for key, value in attrs.items()
    )
    return f'<text x="{x}" y="{y}" {attributes}>{escape(text)}</text>'


def impact_comparison_svg(results: list[Result]) -> str:
    """Grouped normalized-impact chart with actual-value labels."""
    width, height = 1320, 600
    metrics = (
        ("GHG", "kg CO₂e / IT MWh", lambda r: r.per_it_mwh.ghg_kgco2e),
        ("Primary energy", "MJ / IT MWh", lambda r: r.per_it_mwh.primary_energy_mj),
        ("Blue water", "L / IT MWh", lambda r: r.per_it_mwh.blue_water_l),
    )
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        _svg_text(
            40, 42, "Illustrative cooling comparison — not decision-grade",
            font_size=24, font_weight="bold", fill="#222",
        ),
        _svg_text(
            40, 68,
            "Bar lengths are normalized within each metric; labels show actual values.",
            font_size=14, fill="#555",
        ),
    ]
    panel_width = 390
    chart_top, chart_height = 150, 295
    for metric_index, (title, unit, getter) in enumerate(metrics):
        x0 = 40 + metric_index * 420
        values = [getter(result) for result in results]
        maximum = max(values) or 1
        elements.append(_svg_text(
            x0, 102, title, font_size=18, font_weight="bold", fill="#222"
        ))
        elements.append(_svg_text(x0, 122, unit, font_size=12, fill="#555"))
        bar_width = min(74, (panel_width - 30) / max(1, len(results)) - 18)
        gap = (panel_width - 20) / max(1, len(results))
        for index, (result, value) in enumerate(zip(results, values)):
            bar_height = chart_height * value / maximum
            x = x0 + 10 + index * gap
            y = chart_top + chart_height - bar_height
            elements.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" '
                f'height="{bar_height:.1f}" fill="{COLORS[index % len(COLORS)]}"/>'
            )
            elements.append(_svg_text(
                x + bar_width / 2, y - 7, f"{value:,.1f}",
                font_size=11, text_anchor="middle", fill="#222",
            ))
            label = result.cooling_architecture.replace("-", " ")
            elements.append(_svg_text(
                x + bar_width / 2, chart_top + chart_height + 22, label,
                font_size=11, text_anchor="middle", fill="#222",
            ))
        elements.append(
            f'<line x1="{x0}" y1="{chart_top + chart_height}" '
            f'x2="{x0 + panel_width}" y2="{chart_top + chart_height}" '
            'stroke="#444" stroke-width="1"/>'
        )
    elements.extend([
        _svg_text(
            40, 535,
            "Synthetic example factors demonstrate software behavior only.",
            font_size=16, font_weight="bold", fill="#A33",
        ),
        _svg_text(
            40, 560,
            "Replace with reviewed foreground data, background inventories, "
            "and quantified uncertainty before interpretation.",
            font_size=13, fill="#555",
        ),
        "</svg>",
    ])
    return "\n".join(elements)


def ghg_contributions_svg(results: list[Result]) -> str:
    """Stacked annual GHG contribution chart."""
    width, height = 980, 520
    contribution_names = list(results[0].contributions)
    totals = [result.annual_impacts.ghg_kgco2e for result in results]
    maximum = max(totals) or 1
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        _svg_text(
            40, 42, "Annual GHG contribution analysis — illustrative",
            font_size=24, font_weight="bold", fill="#222",
        ),
        _svg_text(
            40, 68,
            "Absolute scale intentionally reveals electricity dominance in these synthetic scenarios.",
            font_size=14, fill="#555",
        ),
    ]
    chart_left, chart_top, chart_width = 250, 90, 650
    bar_height, row_gap = 62, 105
    for row, result in enumerate(results):
        y = chart_top + row * row_gap
        elements.append(_svg_text(
            235, y + 35, result.cooling_architecture.replace("-", " "),
            font_size=14, text_anchor="end", fill="#222",
        ))
        x = chart_left
        for index, name in enumerate(contribution_names):
            value = result.contributions[name].ghg_kgco2e
            segment_width = chart_width * max(0, value) / maximum
            if segment_width:
                elements.append(
                    f'<rect x="{x:.1f}" y="{y}" width="{segment_width:.1f}" '
                    f'height="{bar_height}" fill="{COLORS[index % len(COLORS)]}"/>'
                )
            x += segment_width
        elements.append(_svg_text(
            min(x + 8, 930), y + 35, f"{result.annual_impacts.ghg_kgco2e:,.0f}",
            font_size=12, fill="#222",
        ))
    legend_y = 430
    for index, name in enumerate(contribution_names):
        x = 40 + index * 185
        elements.append(
            f'<rect x="{x}" y="{legend_y}" width="15" height="15" '
            f'fill="{COLORS[index % len(COLORS)]}"/>'
        )
        elements.append(_svg_text(
            x + 21, legend_y + 13, name.replace("_", " "),
            font_size=11, fill="#222",
        ))
    elements.append("</svg>")
    return "\n".join(elements)


def _results_table(results: list[Result]) -> str:
    lines = [
        "| Scenario | Architecture | kg CO₂e/IT MWh | MJ/IT MWh | "
        "L blue water/IT MWh |",
        "|---|---|---:|---:|---:|",
    ]
    for result in results:
        lines.append(
            f"| {result.scenario} | {result.cooling_architecture} | "
            f"{result.per_it_mwh.ghg_kgco2e:.3f} | "
            f"{result.per_it_mwh.primary_energy_mj:.3f} | "
            f"{result.per_it_mwh.blue_water_l:.3f} |"
        )
    return "\n".join(lines)


def _reliability_table(results: list[Result]) -> str:
    lines = [
        "| Scenario | Component | Model | Adjusted life (yr) | "
        "Expected failures | Downtime (h/yr) | Unserved IT exposure (kWh/yr) |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for result in results:
        for record in result.reliability:
            lines.append(
                f"| {result.scenario} | {record.component} | {record.model} | "
                f"{record.adjusted_characteristic_life_years:.3f} | "
                f"{record.expected_failures:.3f} | "
                f"{record.annual_downtime_hours:.3f} | "
                f"{record.annual_unserved_it_kwh:.3f} |"
            )
    if len(lines) == 2:
        return ""
    return """## Reliability and replacement expectations

The following values are expected counts from the declared renewal model. They
are exposure indicators, not a facility-availability prediction; redundancy,
common-cause failures, repair queues, and workload migration are outside the
current model.

""" + "\n".join(lines)


def generate_report(
    scenarios: list[Scenario], output_dir: str | Path
) -> dict[str, Path]:
    """Write deterministic JSON, Markdown, and SVG report artifacts."""
    if len(scenarios) < 2:
        raise ValueError("A comparison report requires at least two scenarios")
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    results = [analyze(scenario) for scenario in scenarios]
    json_path = destination / "results.json"
    impact_path = destination / "impact-comparison.svg"
    contribution_path = destination / "ghg-contributions.svg"
    report_path = destination / "REPORT.md"
    json_path.write_text(
        json.dumps([result.as_dict() for result in results], indent=2) + "\n",
        encoding="utf-8",
    )
    impact_path.write_text(impact_comparison_svg(results) + "\n", encoding="utf-8")
    contribution_path.write_text(
        ghg_contributions_svg(results) + "\n", encoding="utf-8"
    )
    sensitivity_rows = []
    for scenario in scenarios:
        ranked = sensitivity(scenario)
        if ranked:
            item = ranked[0]
            sensitivity_rows.append(
                f"| {scenario.name} | `{item.parameter}` | {item.elasticity:.3f} |"
            )
    markdown = f"""# Representative OpenDC-LCA screening results

> **Illustrative, not decision-grade.** The bundled scenarios use synthetic
> factors to demonstrate calculation, provenance, audit, sensitivity, and
> reporting behavior. They must not be used to select a cooling technology.

## Model

Annual IT electricity:

$$E_{{IT}} = P_{{IT}}\\,CF\\,(8,760\\ \\mathrm{{h\\,yr^{{-1}}}})$$

Annual facility electricity:

$$E_{{facility}} = E_{{IT}}\\,PUE$$

Discrete annualized component inventory:

$$q_{{annual}} =
\\frac{{q\\,\\lceil L_{{facility}}/L_{{component}}\\rceil}}{{L_{{facility}}}}$$

Annual coolant production includes the initial charge amortized over the
facility life plus annual replacement of losses:

$$m_{{fluid,annual}} =
\\frac{{m_{{initial}}}}{{L_{{facility}}}} + m_{{initial}}f_{{loss}}$$

Losses are treated as direct releases and replaced to maintain a constant
operating charge. The remaining initial charge is treated at facility end of
life; released mass is not counted again in end-of-life treatment:

$$I_{{fluid}} = m_{{fluid,annual}}I_{{production}} +
\\frac{{m_{{initial}}}}{{L_{{facility}}}}I_{{EOL}}, \\qquad
GHG_{{direct}} = m_{{initial}}f_{{loss}}GWP_{{direct}}$$

## Results

{_results_table(results)}

![Normalized impact comparison](impact-comparison.svg)

![Annual GHG contribution analysis](ghg-contributions.svg)

{_reliability_table(results)}

## Leading local GHG sensitivities

| Scenario | Highest-ranked parameter | Elasticity |
|---|---|---:|
{chr(10).join(sensitivity_rows)}

Elasticity is a local one-at-a-time screening measure, not a substitute for
Monte Carlo or global sensitivity analysis.

## Reproducibility

- Model version: `{results[0].model_version}`
- Scenario SHA-256 digests and complete contribution results:
  [`results.json`](results.json)
- Inputs: bundled files from `examples/`
- Functional unit: one MWh delivered to IT equipment
- Comparative assertion: false

## Interpretation boundary

The numerical ordering shown here is an artifact of synthetic assumptions.
Publication-quality results require reviewed inventories, canonical impact
methods, quantified uncertainty, consistent system models, and critical review
as specified in `docs/BENCHMARK_PROTOCOL.md`.
"""
    report_path.write_text(markdown, encoding="utf-8")
    return {
        "report": report_path,
        "results": json_path,
        "impact_figure": impact_path,
        "contribution_figure": contribution_path,
    }


def performance_curve_svg(points: list[PerformancePoint]) -> str:
    """Plot measured partial PUE against IT load."""
    width, height = 760, 500
    left, top, chart_width, chart_height = 90, 90, 600, 310
    max_load = max(point.it_load_kw for point in points)
    pue_values = [point.partial_pue for point in points]
    low_pue = min(1.0, min(pue_values))
    high_pue = max(pue_values) * 1.02
    coordinates = []
    for point in sorted(points, key=lambda item: item.it_load_kw):
        x = left + chart_width * point.it_load_kw / max_load
        y = top + chart_height * (
            1 - (point.partial_pue - low_pue) / (high_pue - low_pue)
        )
        coordinates.append((x, y, point))
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        _svg_text(
            40, 42, "Synthetic laboratory performance map",
            font_size=24, font_weight="bold", fill="#222",
        ),
        _svg_text(
            40, 68, "Partial PUE includes recorded cooling-system parasitics.",
            font_size=14, fill="#555",
        ),
        f'<line x1="{left}" y1="{top + chart_height}" '
        f'x2="{left + chart_width}" y2="{top + chart_height}" stroke="#444"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" '
        f'y2="{top + chart_height}" stroke="#444"/>',
        '<polyline points="'
        + " ".join(f"{x:.1f},{y:.1f}" for x, y, _ in coordinates)
        + '" fill="none" stroke="#0072B2" stroke-width="3"/>',
    ]
    for x, y, point in coordinates:
        elements.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="#D55E00"/>'
        )
        elements.append(_svg_text(
            x, y - 12, f"{point.partial_pue:.3f}",
            font_size=12, text_anchor="middle", fill="#222",
        ))
    elements.extend([
        _svg_text(
            left + chart_width / 2, 455, "IT load (kW)",
            font_size=14, text_anchor="middle", fill="#222",
        ),
        _svg_text(
            25, top + chart_height / 2, "Partial PUE",
            font_size=14, text_anchor="middle", fill="#222",
            transform=f"rotate(-90 25 {top + chart_height / 2})",
        ),
        _svg_text(left, 425, "0", font_size=12, text_anchor="middle", fill="#555"),
        _svg_text(
            left + chart_width, 425, f"{max_load:,.0f}",
            font_size=12, text_anchor="middle", fill="#555",
        ),
        _svg_text(
            40, 485, "Illustrative data only — not a validated experiment.",
            font_size=13, font_weight="bold", fill="#A33",
        ),
        "</svg>",
    ])
    return "\n".join(elements)


def uncertainty_intervals_svg(result: MonteCarloResult) -> str:
    """Three-panel p05–p95 uncertainty interval figure."""
    width, height = 1320, 380
    metrics = (
        ("GHG", "kg CO₂e / IT MWh", result.ghg_kgco2e_per_it_mwh),
        (
            "Primary energy",
            "MJ / IT MWh",
            result.primary_energy_mj_per_it_mwh,
        ),
        ("Blue water", "L / IT MWh", result.blue_water_l_per_it_mwh),
    )
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        _svg_text(
            40, 42, "Monte Carlo screening intervals — illustrative",
            font_size=24, font_weight="bold", fill="#222",
        ),
        _svg_text(
            40, 68,
            f"{result.samples:,} seeded samples; whiskers show p05–p95 and dots show p50.",
            font_size=14, fill="#555",
        ),
    ]
    for index, (title, unit, values) in enumerate(metrics):
        x0 = 50 + index * 430
        line_left, line_right, y = x0, x0 + 340, 205
        p05, p50, p95 = values["p05"], values["p50"], values["p95"]
        span = p95 - p05 or 1
        median_x = line_left + (p50 - p05) / span * (line_right - line_left)
        elements.extend([
            _svg_text(x0, 125, title, font_size=19, font_weight="bold", fill="#222"),
            _svg_text(x0, 148, unit, font_size=12, fill="#555"),
            f'<line x1="{line_left}" y1="{y}" x2="{line_right}" y2="{y}" '
            'stroke="#0072B2" stroke-width="8" stroke-linecap="round"/>',
            f'<line x1="{line_left}" y1="{y - 12}" x2="{line_left}" '
            f'y2="{y + 12}" stroke="#222" stroke-width="2"/>',
            f'<line x1="{line_right}" y1="{y - 12}" x2="{line_right}" '
            f'y2="{y + 12}" stroke="#222" stroke-width="2"/>',
            f'<circle cx="{median_x:.1f}" cy="{y}" r="8" fill="#D55E00"/>',
            _svg_text(
                line_left, 242, f"p05 {p05:,.1f}",
                font_size=12, text_anchor="start", fill="#222",
            ),
            _svg_text(
                median_x, 270, f"p50 {p50:,.1f}",
                font_size=12, text_anchor="middle", fill="#222",
            ),
            _svg_text(
                line_right, 242, f"p95 {p95:,.1f}",
                font_size=12, text_anchor="end", fill="#222",
            ),
        ])
    elements.extend([
        _svg_text(
            40, 335,
            "Independent input sampling; correlations and model-form uncertainty are not represented.",
            font_size=13, fill="#555",
        ),
        "</svg>",
    ])
    return "\n".join(elements)


def generate_experimental_report(
    summary: PerformanceSummary,
    points: list[PerformancePoint],
    uncertainty: MonteCarloResult,
    output_dir: str | Path,
) -> dict[str, Path]:
    """Write a representative Phase 2 performance and uncertainty report."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    performance_path = destination / "performance-map.svg"
    uncertainty_path = destination / "uncertainty-intervals.svg"
    results_path = destination / "results.json"
    report_path = destination / "REPORT.md"
    performance_path.write_text(
        performance_curve_svg(points) + "\n", encoding="utf-8"
    )
    uncertainty_path.write_text(
        uncertainty_intervals_svg(uncertainty) + "\n", encoding="utf-8"
    )
    payload = {
        "model_version": uncertainty.model_version,
        "performance_summary": summary.as_dict(),
        "uncertainty": uncertainty.as_dict(),
    }
    results_path.write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    ghg = uncertainty.ghg_kgco2e_per_it_mwh
    report_path.write_text(
        f"""# OpenDC-LCA v0.3 experimental workflow

> **Synthetic demonstration—not decision-grade.** This report shows how
> laboratory performance points and input distributions enter the LCA workflow.

## Performance-map reduction

For observation $i$ with duration $t_i$, the measured cooling-only partial PUE is:

$$PUE = 1 + \\frac{{\\sum_i P_{{cooling,i}}t_i}}
{{\\sum_i P_{{IT,i}}t_i}}$$

The {summary.point_count} points represent {summary.total_duration_hours:.1f} h
and produce:

- measured cooling-only partial PUE: **{summary.measured_pue:.4f}**
- on-site water: **{summary.onsite_water_l_per_kwh_it:.4f} L/kWh IT**
- cooling COP: **{summary.cooling_cop:.3f}**

![Performance map](performance-map.svg)

## Uncertainty propagation

The seeded Monte Carlo analysis used {uncertainty.samples:,} samples. GHG
screening results are **{ghg['p50']:.1f} kg CO₂e/IT MWh** at p50, with a
p05–p95 interval of **{ghg['p05']:.1f}–{ghg['p95']:.1f}**.

![Uncertainty intervals](uncertainty-intervals.svg)

Inputs are sampled independently. Correlation, model-form uncertainty, and
experimental systematic error require additional analysis before comparative
interpretation. Complete machine-readable results are in
[`results.json`](results.json).
""",
        encoding="utf-8",
    )
    return {
        "report": report_path,
        "results": results_path,
        "performance_figure": performance_path,
        "uncertainty_figure": uncertainty_path,
    }
