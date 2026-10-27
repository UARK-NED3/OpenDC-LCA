#!/usr/bin/env python3
"""Build or verify the checksum ledger for locally held provider files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from opendc_lca.provenance import (  # noqa: E402
    build_file_manifest,
    verify_manifest_records,
    write_file_manifest,
)

SOURCE_ROOT = ROOT / "private-data" / "incoming"
MANIFEST = ROOT / "data" / "derived" / "source-file-manifest.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the existing manifest rather than rewriting it.",
    )
    parser.add_argument(
        "--skip-hashes",
        action="store_true",
        help="In --check mode, verify path and byte count but not SHA-256.",
    )
    args = parser.parse_args()

    if not SOURCE_ROOT.is_dir():
        raise SystemExit(
            "No local provider archive was found at private-data/incoming. "
            "Clone-only installations can still run the package examples, but "
            "cannot rebuild the paper evidence package."
        )

    if args.check:
        records = json.loads(MANIFEST.read_text(encoding="utf-8"))
        local_files = sorted(
            path for path in SOURCE_ROOT.rglob("*") if path.is_file()
        )
        errors = verify_manifest_records(
            records,
            root=ROOT,
            required_paths=local_files,
            verify_hashes=not args.skip_hashes,
        )
        recorded = {str(record["local_path"]) for record in records}
        local = {path.relative_to(ROOT).as_posix() for path in local_files}
        errors.extend(
            f"manifest path no longer exists: {path}"
            for path in sorted(recorded - local)
        )
        if errors:
            raise SystemExit("\n".join(errors))
        print(
            f"Verified {len(records)} provider files in "
            f"{MANIFEST.relative_to(ROOT)}"
        )
        return

    records = build_file_manifest(SOURCE_ROOT, root=ROOT)
    write_file_manifest(MANIFEST, records)
    print(
        f"Wrote {len(records)} provider-file records to "
        f"{MANIFEST.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
