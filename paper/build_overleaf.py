#!/usr/bin/env python3
"""Build a self-contained Elsevier/Overleaf manuscript from MANUSCRIPT.md."""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "MANUSCRIPT.md"
SUPPLEMENT_SOURCE = ROOT / "SUPPLEMENTARY_INFORMATION.md"
OUT = ROOT / "overleaf"
FIGURES = OUT / "figures"


def protect_inline(text: str) -> str:
    text = (
        text.replace("−", "-")
        .replace("—", "---")
        .replace("–", "--")
        .replace("“", "``")
        .replace("”", "''")
        .replace("’", "'")
        .replace("⁻¹⁴", "$^{-14}$")
        .replace("⁻¹", "$^{-1}$")
        .replace("⁻⁴", "$^{-4}$")
        .replace("³", "$^{3}$")
        .replace("±", r"$\pm$")
    )
    tokens: list[str] = []

    def hold(value: str) -> str:
        tokens.append(value)
        return f"@@TOKEN{len(tokens)-1}@@"

    def citation(value: str) -> str:
        numbers: list[int] = []
        for part in value.replace(" ", "").split(","):
            if "-" in part:
                first, last = (int(x) for x in part.split("-", 1))
                numbers.extend(range(first, last + 1))
            else:
                numbers.append(int(part))
        return r"\cite{" + ",".join(f"ref{x}" for x in numbers) + "}"

    text = re.sub(
        r"\[([0-9][0-9,\- ]*)\]",
        lambda m: hold(citation(m.group(1))),
        text,
    )
    text = re.sub(r"`([^`]+)`", lambda m: hold(r"\texttt{" + escape(m.group(1)) + "}"), text)
    text = re.sub(r"\\\((.+?)\\\)", lambda m: hold("$" + m.group(1) + "$"), text)
    text = re.sub(r"(?<!\\)\$([^$]+)\$", lambda m: hold("$" + m.group(1) + "$"), text)
    text = re.sub(
        r"https?://[^\s)]+",
        lambda m: hold(r"\url{" + m.group(0).rstrip(".,") + "}")
        + m.group(0)[len(m.group(0).rstrip(".,")) :],
        text,
    )
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\\textit{\1}", text)
    for index, token in enumerate(tokens):
        text = text.replace(f"@@TOKEN{index}@@", token)
    return text


def escape(text: str) -> str:
    replacements = {
        "\\": "@@BS@@",
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.replace("@@BS@@", r"\textbackslash{}")


def table_latex(rows: list[list[str]], caption: str) -> str:
    columns = len(rows[0])

    def cell(value: str) -> str:
        return (
            protect_inline(value)
            .replace("/", r"/\allowbreak{}")
            .replace("-", r"-\allowbreak{}")
        )

    if columns == 4 and rows[0][0] != "Envelope":
        ragged = r">{\raggedright\arraybackslash}"
        spec = (
            ragged
            + r"p{0.18\textwidth}"
            + ragged
            + r"p{0.23\textwidth}"
            + ragged
            + r"p{0.34\textwidth}"
            + ragged
            + r"p{0.16\textwidth}"
        )
        header = " & ".join(cell(value) for value in rows[0]) + r" \\"
        output = [
            r"{\footnotesize",
            r"\setlength{\tabcolsep}{3pt}",
            r"\begin{longtable}{" + spec + "}",
            r"\caption{" + protect_inline(caption) + r"}\\",
            r"\toprule",
            header,
            r"\midrule",
            r"\endfirsthead",
            r"\caption[]{" + protect_inline(caption) + r" (continued)}\\",
            r"\toprule",
            header,
            r"\midrule",
            r"\endhead",
            r"\midrule",
            r"\multicolumn{4}{r}{Continued on next page}\\",
            r"\endfoot",
            r"\bottomrule",
            r"\endlastfoot",
        ]
        for row in rows[2:]:
            output.append(" & ".join(cell(value) for value in row) + r" \\")
            output.append(r"\addlinespace[2pt]")
        output += [r"\end{longtable}", r"}", ""]
        return "\n".join(output)

    if columns == 4:
        ragged = r">{\raggedright\arraybackslash}"
        spec = (
            ragged
            + r"p{0.15\linewidth}"
            + ragged
            + r"p{0.39\linewidth}"
            + ragged
            + r"p{0.18\linewidth}"
            + ragged
            + r"p{0.18\linewidth}"
        )
        font_size = r"\small"
        tab_space = "3pt"
        table_begin = [r"\begin{table}[!htbp]"]
        table_end = [r"\end{table}"]
        width = r"\textwidth"
    else:
        spec = "l" + "X" * (columns - 1)
        font_size = r"\small"
        tab_space = "3pt"
        table_begin = [r"\begin{table*}[htbp]"]
        table_end = [r"\end{table*}"]
        width = r"\textwidth"
    output = table_begin + [
        r"\centering",
        r"\caption{" + protect_inline(caption) + "}",
        font_size,
        rf"\setlength{{\tabcolsep}}{{{tab_space}}}",
        r"\begin{tabularx}{" + width + "}{" + spec + "}",
        r"\toprule",
        " & ".join(cell(value) for value in rows[0]) + r" \\",
        r"\midrule",
    ]
    for row in rows[2:]:
        output.append(
            " & ".join(cell(value) for value in row) + r" \\"
        )
    output += [r"\bottomrule", r"\end{tabularx}"] + table_end + [""]
    return "\n".join(output)


def longtable_latex(rows: list[list[str]], caption: str) -> str:
    """Render a three-column audit table that can continue across pages."""
    if len(rows[0]) != 3:
        raise ValueError("The supplementary long-table layout expects three columns")

    def cell(value: str) -> str:
        match = re.fullmatch(r"`([^`]+)`", value.strip())
        if match:
            return r"\path{" + match.group(1) + "}"
        return protect_inline(value)

    header = " & ".join(cell(value) for value in rows[0]) + r" \\"
    output = [
        r"{\small",
        r"\setlength{\tabcolsep}{4pt}",
        r"\begin{longtable}{>{\raggedright\arraybackslash}p{0.38\textwidth}"
        r">{\raggedright\arraybackslash}p{0.27\textwidth}"
        r">{\raggedright\arraybackslash}p{0.27\textwidth}}",
        r"\caption{" + protect_inline(caption) + r"}\\",
        r"\toprule",
        header,
        r"\midrule",
        r"\endfirsthead",
        r"\caption[]{"
        + protect_inline(caption)
        + r" (continued)}\\",
        r"\toprule",
        header,
        r"\midrule",
        r"\endhead",
        r"\midrule",
        r"\multicolumn{3}{r}{Continued on next page}\\",
        r"\endfoot",
        r"\bottomrule",
        r"\endlastfoot",
    ]
    for row in rows[2:]:
        output.append(" & ".join(cell(value) for value in row) + r" \\")
    output += [r"\end{longtable}", r"}", ""]
    return "\n".join(output)


def convert_figures() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    source_text = SOURCE.read_text(encoding="utf-8")
    if SUPPLEMENT_SOURCE.exists():
        source_text += "\n" + SUPPLEMENT_SOURCE.read_text(encoding="utf-8")
    used = set(re.findall(r"\]\(figures/([^)]+\.svg)\)", source_text))
    for filename in used:
        source = ROOT / "figures" / filename
        target = FIGURES / f"{source.stem}.pdf"
        if shutil.which("rsvg-convert"):
            subprocess.run(
                ["rsvg-convert", "-f", "pdf", "-o", str(target), str(source)],
                check=True,
            )
        else:
            with tempfile.TemporaryDirectory(prefix="opendc-svg-") as temporary:
                png = Path(temporary) / f"{source.stem}.png"
                render_svg_with_browser(source, png, width=2400)
                from PIL import Image

                with Image.open(png) as rendered:
                    rendered.convert("RGB").save(
                        target, "PDF", resolution=300.0
                    )


def render_svg_with_browser(source: Path, target: Path, *, width: int) -> None:
    """Rasterize an SVG with an installed Chromium browser."""
    browser = next(
        (
            candidate
            for candidate in (
                Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
                Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
                Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
            )
            if candidate.is_file()
        ),
        None,
    )
    if browser is None:
        raise RuntimeError("Figure conversion requires rsvg-convert or Chromium")
    root = ET.parse(source).getroot()
    view_box = root.attrib.get("viewBox", "").split()
    if len(view_box) == 4:
        source_width, source_height = float(view_box[2]), float(view_box[3])
    else:
        source_width = float(root.attrib["width"])
        source_height = float(root.attrib["height"])
    scale = width / source_width
    css_width = round(source_width)
    css_height = round(source_height)
    with tempfile.TemporaryDirectory(prefix="opendc-browser-") as temporary:
        subprocess.run(
            [
                str(browser),
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--no-first-run",
                f"--force-device-scale-factor={scale}",
                f"--user-data-dir={Path(temporary) / 'profile'}",
                f"--window-size={css_width},{css_height}",
                f"--screenshot={target}",
                source.resolve().as_uri(),
            ],
            check=True,
            timeout=60,
        )
        for _ in range(300):
            if target.is_file() and target.stat().st_size:
                break
            time.sleep(0.1)
        else:
            raise RuntimeError(f"Browser did not render {source.name}")


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    convert_figures()
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    title = lines[0][2:]
    output = [
        r"\documentclass[review,12pt]{elsarticle}",
        r"\usepackage{amsmath,amssymb}",
        r"\usepackage{booktabs,tabularx,array,longtable}",
        r"\usepackage{graphicx,float,pdflscape}",
        r"\usepackage{siunitx}",
        r"\usepackage{url,hyperref}",
        r"\hypersetup{hidelinks}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage[utf8]{inputenc}",
        r"\setlength{\emergencystretch}{3em}",
        r"\journal{Applied Energy}",
        r"\begin{document}",
        r"\begin{frontmatter}",
        r"\title{" + protect_inline(title) + "}",
        r"\author[uark,hfa]{Braden Stevens}",
        r"\author[uark,hfa]{Pengjiang Xiang}",
        r"\author[ahpcc]{Pawel Wolinski}",
        r"\author[its]{Charles Dwyer}",
        r"\author[ornl]{Yimin Chen}",
        r"\author[uark]{Darin Nutter}",
        r"\author[uark]{Han Hu\corref{cor1}}",
        r"\ead{hanhu@uark.edu}",
        r"\address[uark]{Department of Mechanical Engineering, University of Arkansas, Fayetteville, AR 72701, U.S.}",
        r"\address[ahpcc]{Arkansas High Performance Computing Center, University of Arkansas, Fayetteville, AR 72701, U.S.}",
        r"\address[its]{IT Services, University of Arkansas, Fayetteville, AR 72701, U.S.}",
        r"\address[ornl]{Building Technologies Research and Integration Center, Oak Ridge National Laboratory, Oak Ridge, TN 37830, U.S.}",
        r"\address[hfa]{Harrison French \& Associates Ltd., Bentonville, AR 72712, U.S.}",
        r"\cortext[cor1]{Corresponding author}",
    ]
    index = next(i for i, line in enumerate(lines) if line.strip() == "## Abstract") + 1
    in_abstract = True
    in_refs = False
    paragraph: list[str] = []
    pending_caption = ""
    list_kind = ""

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            output.append(protect_inline(" ".join(part.strip() for part in paragraph)))
            output.append("")
            paragraph = []

    def close_list() -> None:
        nonlocal list_kind
        if list_kind:
            output.append(r"\end{" + list_kind + "}")
            output.append("")
            list_kind = ""

    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if in_refs:
            break
        if not stripped:
            flush_paragraph()
            close_list()
            index += 1
            continue
        if stripped.startswith("**Keywords**"):
            flush_paragraph()
            if in_abstract:
                output.append(r"\end{abstract}")
            keywords = re.sub(r"^\*\*Keywords\*\*\s*", "", stripped)
            keyword_latex = r" \sep ".join(
                protect_inline(keyword.strip()) for keyword in keywords.split(",")
            )
            output += [
                r"\begin{keyword}",
                keyword_latex,
                r"\end{keyword}",
                r"\end{frontmatter}",
                "",
            ]
            in_abstract = False
            index += 1
            continue
        if in_abstract:
            if not any(line == r"\begin{abstract}" for line in output):
                output.append(r"\begin{abstract}")
            paragraph.append(raw)
            index += 1
            continue
        if stripped == "## References":
            flush_paragraph()
            close_list()
            in_refs = True
            index += 1
            break
        if stripped.startswith("## "):
            flush_paragraph()
            close_list()
            heading = re.sub(r"^\d+\.\s*", "", stripped[3:])
            output.append(r"\section{" + protect_inline(heading) + "}")
            index += 1
            continue
        if stripped.startswith("### "):
            flush_paragraph()
            close_list()
            if stripped.startswith("### 4.10."):
                index += 1
                while index < len(lines) and not lines[index].strip().startswith("## "):
                    index += 1
                continue
            heading = re.sub(r"^\d+(?:\.\d+)*\.\s*", "", stripped[4:])
            output.append(r"\subsection{" + protect_inline(heading) + "}")
            index += 1
            continue
        if stripped.startswith("!["):
            flush_paragraph()
            match = re.match(r"!\[(.*)\]\(figures/(.*)\.svg\)", stripped)
            if match:
                caption, name = match.groups()
                caption = re.sub(r"^Figure \d+\.\s*", "", caption)
                output += [
                    r"\begin{figure}[!htbp]",
                    r"\centering",
                    rf"\includegraphics[width=0.98\linewidth]{{figures/{name}.pdf}}",
                    r"\caption{" + protect_inline(caption) + "}",
                    r"\label{fig:" + name.replace("_", "-") + "}",
                    r"\end{figure}",
                    "",
                ]
            index += 1
            continue
        if stripped == r"\[":
            flush_paragraph()
            close_list()
            equation = [raw]
            index += 1
            while index < len(lines):
                equation.append(lines[index])
                if lines[index].strip() == r"\]":
                    break
                index += 1
            output.extend(equation)
            output.append("")
            index += 1
            continue
        if stripped.startswith("**Table "):
            flush_paragraph()
            pending_caption = stripped.strip("*")
            pending_caption = re.sub(r"^Table \d+\.\s*", "", pending_caption)
            index += 1
            continue
        if stripped.startswith("|"):
            flush_paragraph()
            close_list()
            rows = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append(
                    [cell.strip() for cell in lines[index].strip().strip("|").split("|")]
                )
                index += 1
            output.append(table_latex(rows, pending_caption or "Summary table"))
            pending_caption = ""
            continue
        numbered = re.match(r"^\d+\.\s+(.*)", stripped)
        bullet = re.match(r"^-\s+(.*)", stripped)
        if numbered or bullet:
            flush_paragraph()
            wanted = "enumerate" if numbered else "itemize"
            if list_kind != wanted:
                close_list()
                output.append(r"\begin{" + wanted + "}")
                list_kind = wanted
            output.append(r"\item " + protect_inline((numbered or bullet).group(1)))
            index += 1
            continue
        paragraph.append(raw)
        index += 1

    flush_paragraph()
    close_list()

    references: list[str] = []
    current = ""
    for raw in lines[index:]:
        stripped = raw.strip()
        match = re.match(r"^\d+\.\s+(.*)", stripped)
        if match:
            if current:
                references.append(current)
            current = match.group(1)
        elif stripped:
            current += " " + stripped
    if current:
        references.append(current)
    output += [r"\begin{thebibliography}{99}"]
    for number, reference in enumerate(references, 1):
        output.append(rf"\bibitem{{ref{number}}} " + protect_inline(reference))
    output += [r"\end{thebibliography}", r"\end{document}", ""]
    (OUT / "main.tex").write_text("\n".join(output), encoding="utf-8")
    shutil.copy2(ROOT / "SUBMISSION_ACTIONS.md", OUT)
    for name in (
        "table15_egrid_historical_national_factors.csv",
        "table19_server_inventory_stress_test.csv",
        "table20_method_comparison.csv",
        "table21_anchor_extrapolation_diagnostic.csv",
        "table22_boundary_mismatch_stress.csv",
        "table23_joint_assumption_stress.csv",
        "table24_functional_unit_sensitivity.csv",
        "table25_priority_index_sensitivity.csv",
        "table26_stress_structure_sensitivity.csv",
        "table27_stress_convergence.csv",
        "table28_lifecycle_electricity_factors.csv",
        "table29_standardized_rank_robustness.csv",
        "table30_released_endpoint_method_audit.csv",
        "table31_implied_electricity_response.csv",
        "table32_national_lifecycle_cutoffs.csv",
        "table33_residual_electricity_factors.csv",
        "table34_boavizta_server_inclusion.csv",
        "table35_transferability_evidence_map.csv",
    ):
        shutil.copy2(ROOT / "tables" / name, OUT)


def build_supplement() -> None:
    """Convert the lightweight Markdown supplement to a standalone TeX file."""
    lines = SUPPLEMENT_SOURCE.read_text(encoding="utf-8").splitlines()
    output = [
        r"\documentclass[review,12pt]{elsarticle}",
        r"\usepackage{booktabs,tabularx,array,longtable,graphicx,float,pdflscape,url,hyperref}",
        r"\hypersetup{hidelinks}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage[utf8]{inputenc}",
        r"\setlength{\emergencystretch}{3em}",
        r"\renewcommand{\thesection}{S\arabic{section}}",
        r"\renewcommand{\thefigure}{S\arabic{figure}}",
        r"\renewcommand{\thetable}{S\arabic{table}}",
        r"\begin{document}",
        r"\begin{frontmatter}",
        r"\title{" + protect_inline(lines[0][2:]) + "}",
        r"\author[uark,hfa]{Braden Stevens}",
        r"\author[uark,hfa]{Pengjiang Xiang}",
        r"\author[ahpcc]{Pawel Wolinski}",
        r"\author[its]{Charles Dwyer}",
        r"\author[ornl]{Yimin Chen}",
        r"\author[uark]{Darin Nutter}",
        r"\author[uark]{Han Hu}",
        r"\address[uark]{Department of Mechanical Engineering, University of Arkansas, Fayetteville, AR 72701, U.S.}",
        r"\address[ahpcc]{Arkansas High Performance Computing Center, University of Arkansas, Fayetteville, AR 72701, U.S.}",
        r"\address[its]{IT Services, University of Arkansas, Fayetteville, AR 72701, U.S.}",
        r"\address[ornl]{Building Technologies Research and Integration Center, Oak Ridge National Laboratory, Oak Ridge, TN 37830, U.S.}",
        r"\address[hfa]{Harrison French \& Associates Ltd., Bentonville, AR 72712, U.S.}",
        r"\end{frontmatter}",
        "",
    ]
    index = 1
    paragraph: list[str] = []
    list_open = False
    in_code = False

    def flush() -> None:
        nonlocal paragraph
        if paragraph:
            output.append(protect_inline(" ".join(x.strip() for x in paragraph)))
            output.append("")
            paragraph = []

    def close_list() -> None:
        nonlocal list_open
        if list_open:
            output.extend([r"\end{itemize}", ""])
            list_open = False

    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if stripped.startswith("```"):
            flush()
            close_list()
            if in_code:
                output.extend([r"\end{verbatim}", ""])
            else:
                output.append(r"\begin{verbatim}")
            in_code = not in_code
            index += 1
            continue
        if in_code:
            output.append(raw)
            index += 1
            continue
        if not stripped:
            flush()
            close_list()
            index += 1
            continue
        if stripped.startswith("## "):
            flush()
            close_list()
            heading = re.sub(r"^S\d+\.\s*", "", stripped[3:])
            output.append(r"\section{" + protect_inline(heading) + "}")
            index += 1
            continue
        if stripped.startswith("!["):
            flush()
            close_list()
            match = re.match(r"!\[(.*)\]\(figures/(.*)\.svg\)", stripped)
            if match:
                caption, name = match.groups()
                caption = re.sub(
                    r"^Supplementary Figure S\d+\.\s*", "", caption
                )
                output += [
                    r"\begin{figure}[H]",
                    r"\centering",
                    rf"\includegraphics[width=0.96\linewidth]{{figures/{name}.pdf}}",
                    r"\caption{" + protect_inline(caption) + "}",
                    r"\end{figure}",
                    "",
                ]
            index += 1
            continue
        if stripped.startswith("|"):
            flush()
            close_list()
            rows = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append(
                    [
                        cell.strip()
                        for cell in lines[index].strip().strip("|").split("|")
                    ]
                )
                index += 1
            output.append(longtable_latex(rows, "Supplementary result map"))
            continue
        if stripped.startswith("- "):
            flush()
            if not list_open:
                output.append(r"\begin{itemize}")
                list_open = True
            output.append(r"\item " + protect_inline(stripped[2:]))
            index += 1
            continue
        numbered = re.match(r"^\d+\.\s+(.*)", stripped)
        if numbered:
            flush()
            if not list_open:
                output.append(r"\begin{itemize}")
                list_open = True
            output.append(r"\item " + protect_inline(numbered.group(1)))
            index += 1
            continue
        paragraph.append(raw)
        index += 1

    flush()
    close_list()
    output.extend([r"\end{document}", ""])
    (OUT / "supplement.tex").write_text("\n".join(output), encoding="utf-8")


if __name__ == "__main__":
    build()
    build_supplement()
    print(OUT)
