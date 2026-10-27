#!/usr/bin/env python3
"""Create the upload-ready Overleaf source archive from the generated project."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "paper" / "overleaf"
DESTINATION = ROOT / "paper" / "OpenDC-LCA_Applied_Energy_Overleaf.zip"
EXCLUDED_SUFFIXES = {".aux", ".fdb_latexmk", ".fls", ".log", ".out", ".spl"}
EXCLUDED_NAMES = {
    "main.pdf",
    "supplement.pdf",
    "OpenDC-LCA_manuscript_final_review.pdf",
    "OpenDC-LCA_manuscript_YC_revision.pdf",
}


def main() -> None:
    if not (PROJECT / "main.tex").is_file() or not (PROJECT / "supplement.tex").is_file():
        raise FileNotFoundError("Build the Overleaf source before packaging it")
    files = sorted(
        path
        for path in PROJECT.rglob("*")
        if path.is_file()
        and path.suffix not in EXCLUDED_SUFFIXES
        and path.name not in EXCLUDED_NAMES
    )
    with ZipFile(DESTINATION, "w", compression=ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(PROJECT).as_posix())
    print(f"Wrote {DESTINATION.relative_to(ROOT)} with {len(files)} files")


if __name__ == "__main__":
    main()
