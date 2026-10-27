#!/usr/bin/env python3
"""Apply the manuscript's publication-figure typography policy to SVG outputs.

The figure caption carries the figure title.  Figure 1 (the workflow graphic)
retains its in-figure title; all other SVG figures omit one.  This postprocess
is deliberately run after the analysis scripts so regenerating results does
not restore inconsistent typography.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "paper" / "figures"
WORKFLOW = "figure0_opendc_lca_workflow.svg"

TITLE = re.compile(r"\s*<text\b[^>]*\bclass=\"title\"[^>]*>.*?</text>\s*", re.DOTALL)
FONT_FAMILY = re.compile(r"font-family:[^;}]+")


def replace_class_size(svg: str, class_name: str, size: str) -> str:
    pattern = re.compile(
        rf"(\.{re.escape(class_name)}\{{[^}}]*?font-size:)[0-9.]+px",
    )
    return pattern.sub(rf"\g<1>{size}px", svg)


def normalize(path: Path) -> None:
    svg = path.read_text(encoding="utf-8")
    svg = FONT_FAMILY.sub("font-family:Arial,sans-serif", svg)
    if path.name != WORKFLOW:
        svg = TITLE.sub("\n", svg, count=1)

    # Minimum readable type at one-column manuscript width.  Each SVG keeps
    # its own geometry; this only scales text into the space freed by titles.
    for class_name, size in (("axis", "17"), ("label", "16"), ("note", "14"), ("small", "14")):
        svg = replace_class_size(svg, class_name, size)

    if path.name == WORKFLOW:
        for class_name, size in (
            ("title", "30"), ("subtitle", "18"), ("section", "20"),
            ("cardtitle", "17"), ("body", "15"), ("small", "14"),
            ("number", "29"), ("step", "16"),
        ):
            svg = replace_class_size(svg, class_name, size)
        svg = re.sub(r"font-size:12px", "font-size:14px", svg)
        svg = re.sub(r"font-size:17px", "font-size:18px", svg)
    else:
        # Several early figures use only a default text size rather than the
        # axis/label/note classes.  Raise it consistently where present.
        svg = re.sub(r"fill:#17212b;font-size:15px", "fill:#17212b;font-size:17px", svg)
        svg = re.sub(r"fill:#17212b;font-size:16px", "fill:#17212b;font-size:18px", svg)

    path.write_text(svg, encoding="utf-8")


def main() -> None:
    for path in sorted(FIGURES.glob("*.svg")):
        normalize(path)
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
