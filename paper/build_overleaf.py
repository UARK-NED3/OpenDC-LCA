#!/usr/bin/env python3
"""Build a self-contained Elsevier/Overleaf manuscript from MANUSCRIPT.md."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "MANUSCRIPT.md"
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
    )
    tokens: list[str] = []

    def hold(value: str) -> str:
        tokens.append(value)
        return f"@@TOKEN{len(tokens)-1}@@"

    text = re.sub(
        r"\[(\d+(?:,\d+)*)\]",
        lambda m: hold(
            r"\cite{" + ",".join(f"ref{x}" for x in m.group(1).split(",")) + "}"
        ),
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
    if columns == 5:
        ragged = r">{\raggedright\arraybackslash}"
        spec = (
            ragged
            + r"p{0.16\textwidth}"
            + ragged
            + "X"
            + ragged
            + r"p{0.12\textwidth}"
            + ragged
            + r"p{0.12\textwidth}"
            + ragged
            + r"p{0.14\textwidth}"
        )
        font_size = r"\scriptsize"
        tab_space = "2pt"
    else:
        spec = "l" + "X" * (columns - 1)
        font_size = r"\small"
        tab_space = "3pt"
    output = [
        r"\begin{table*}[htbp]",
        r"\centering",
        r"\caption{" + protect_inline(caption) + "}",
        font_size,
        rf"\setlength{{\tabcolsep}}{{{tab_space}}}",
        r"\begin{tabularx}{\textwidth}{" + spec + "}",
        r"\toprule",
        " & ".join(protect_inline(value) for value in rows[0]) + r" \\",
        r"\midrule",
    ]
    for row in rows[2:]:
        output.append(
            " & ".join(protect_inline(value) for value in row) + r" \\"
        )
    output += [r"\bottomrule", r"\end{tabularx}", r"\end{table*}", ""]
    return "\n".join(output)


def convert_figures() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    used = set(re.findall(r"\]\(figures/([^)]+\.svg)\)", SOURCE.read_text()))
    for filename in used:
        source = ROOT / "figures" / filename
        target = FIGURES / f"{source.stem}.pdf"
        subprocess.run(
            ["rsvg-convert", "-f", "pdf", "-o", str(target), str(source)],
            check=True,
        )


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    convert_figures()
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    title = lines[0][2:]
    output = [
        r"\documentclass[review,12pt]{elsarticle}",
        r"\usepackage{amsmath,amssymb}",
        r"\usepackage{booktabs,tabularx,array,longtable}",
        r"\usepackage{graphicx,float}",
        r"\usepackage{siunitx}",
        r"\usepackage{url,hyperref}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage[utf8]{inputenc}",
        r"\setlength{\emergencystretch}{3em}",
        r"\journal{Applied Energy}",
        r"\begin{document}",
        r"\begin{frontmatter}",
        r"\title{" + protect_inline(title) + "}",
        r"\author[uark]{Han Hu\corref{cor1}}",
        r"\ead{Corresponding author email to be confirmed}",
        r"\author[uark]{Darin W. Nutter}",
        r"\address[uark]{Department of Mechanical Engineering, University of Arkansas, Fayetteville, Arkansas, USA}",
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
        if stripped.startswith("**Keywords:**"):
            flush_paragraph()
            if in_abstract:
                output.append(r"\end{abstract}")
            keywords = stripped.split(":", 1)[1].strip()
            output += [
                r"\begin{keyword}",
                protect_inline(keywords.replace(";", r" \sep ")),
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
                    r"\begin{figure*}[htbp]",
                    r"\centering",
                    rf"\includegraphics[width=0.96\textwidth]{{figures/{name}.pdf}}",
                    r"\caption{" + protect_inline(caption) + "}",
                    r"\label{fig:" + name.replace("_", "-") + "}",
                    r"\end{figure*}",
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
    shutil.copy2(ROOT / "tables" / "table15_egrid_historical_national_factors.csv", OUT)
    shutil.copy2(ROOT / "tables" / "table19_server_inventory_stress_test.csv", OUT)
    shutil.copy2(ROOT / "tables" / "table20_method_comparison.csv", OUT)


if __name__ == "__main__":
    build()
    print(OUT)
