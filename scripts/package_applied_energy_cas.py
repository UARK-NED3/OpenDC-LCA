#!/usr/bin/env python3
"""Create the flat, self-contained Applied Energy CAS source archive.

The archive contents are derived from the LaTeX sources rather than from a
directory sweep. Figures come from ``\\includegraphics`` and data files from the
derived-table names cited in the text, so local build output cannot leak into
the archive and a renamed or missing dependency fails the build instead of
shipping silently.
"""

from __future__ import annotations

import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "paper" / "applied_energy_cas_overleaf"
DESTINATION = ROOT / "paper" / "OpenDC-LCA_Applied_Energy_CAS_Overleaf.zip"

# Documents and Elsevier template files that are always shipped.
SOURCES = (
    "main.tex",
    "supplement.tex",
    "highlights.tex",
    "cover_letter_draft.tex",
)
SUPPORT = (
    "cas-sc.cls",
    "cas-common.sty",
    "cas-model2-names.bst",
    "cas-email.jpeg",
    "README",
    "SUBMISSION_ACTIONS.md",
)
# Derived tables carried for reviewer traceability that no sentence cites by
# name. Everything else in the archive is resolved from the sources.
EXTRA_DATA = (
    "table19_server_inventory_stress_test.csv",
    "table20_method_comparison.csv",
    "table35_transferability_evidence_map.csv",
)

GRAPHICS = re.compile(r"\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}")
DERIVED_TABLE = re.compile(r"table\d+(?:\\?_[A-Za-z0-9]+)+\.csv")


def declared_files() -> list[str]:
    """Resolve every file the archive must contain, in a stable order."""
    figures: set[str] = set()
    tables: set[str] = set()
    for name in SOURCES:
        text = (PROJECT / name).read_text(encoding="utf-8")
        figures.update(GRAPHICS.findall(text))
        tables.update(
            match.group(0).replace("\\_", "_")
            for match in DERIVED_TABLE.finditer(text)
        )
    tables.update(EXTRA_DATA)
    return [*SOURCES, *SUPPORT, *sorted(figures), *sorted(tables)]


def main() -> None:
    declared = declared_files()
    missing = [name for name in declared if not (PROJECT / name).is_file()]
    if missing:
        raise FileNotFoundError(
            "Declared files are absent from "
            f"{PROJECT.relative_to(ROOT)}: {', '.join(sorted(missing))}"
        )

    carried = {
        path.name
        for path in PROJECT.iterdir()
        if path.is_file()
        and path.suffix
        in {".csv", ".pdf", ".png", ".tex", ".jpeg", ".cls", ".sty", ".bst"}
    }
    # Build output is expected to stay behind; anything else is worth a look.
    generated = {"main.pdf", "supplement.pdf", "cover_letter_draft.pdf"}
    orphans = sorted(carried - set(declared) - generated)
    if orphans:
        print("Note: present but not shipped: " + ", ".join(orphans))

    with ZipFile(DESTINATION, "w", compression=ZIP_DEFLATED) as archive:
        for name in declared:
            archive.write(PROJECT / name, name)
    print(f"Wrote {DESTINATION.relative_to(ROOT)} with {len(declared)} flat files")


if __name__ == "__main__":
    main()
