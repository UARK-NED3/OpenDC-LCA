"""Install bundled example scenarios into a user-selected directory."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path


def install_examples(output_dir: str | Path) -> list[Path]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    resource_dir = files("opendc_lca").joinpath("example_data")
    installed = []
    for name in (
        "air-cooled.json",
        "direct-to-chip.json",
        "single-phase-immersion.json",
        "reliability-direct-to-chip.json",
        "performance-map-direct-to-chip.csv",
        "uncertainty-direct-to-chip.json",
    ):
        target = destination / name
        if target.exists():
            raise FileExistsError(f"Refusing to replace existing example: {target}")
        target.write_bytes(resource_dir.joinpath(name).read_bytes())
        installed.append(target)
    return installed
