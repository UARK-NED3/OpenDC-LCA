"""Dependency-free reproducible reports and SVG figures."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path

from .engine import Result, analyze, sensitivity
from .models import Scenario

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

## Results

{_results_table(results)}

![Normalized impact comparison](impact-comparison.svg)

![Annual GHG contribution analysis](ghg-contributions.svg)

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
