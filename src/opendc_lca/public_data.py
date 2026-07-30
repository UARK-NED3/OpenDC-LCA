"""Adapters for public datasets used by OpenDC-LCA examples.

The adapters deliberately read provider-native exports without redistributing
the raw databases.  They return small, auditable records suitable for derived
tables and screening analyses.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
import re
from statistics import fmean
from typing import Iterable
from xml.etree import ElementTree as ET
from zipfile import ZipFile


@dataclass(frozen=True)
class TmyClimateSummary:
    station_id: str
    station_name: str
    latitude: float
    longitude: float
    elevation_m: float
    record_start_year: int
    record_end_year: int
    hours: int
    mean_dry_bulb_c: float
    minimum_dry_bulb_c: float
    maximum_dry_bulb_c: float
    mean_relative_humidity_pct: float
    cooling_degree_hours_18c: float
    hours_above_30c: int
    hours_below_5c: int
    missing_value_counts: dict[str, int]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class OekobaudatFactor:
    uuid: str
    name: str
    module: str
    geography: str
    dataset_type: str
    reference_year: int
    reference_unit: str
    gwp_total_kgco2e: float
    nonrenewable_primary_energy_mj: float
    renewable_primary_energy_mj: float
    freshwater_m3: float
    url: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class GladProcess:
    archive: str
    uuid: str
    name: str
    description: str
    category: str
    geography: str
    process_type: str
    valid_from: str
    valid_until: str
    owner: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class EgridStateFactor:
    data_year: int
    state: str
    state_abbreviation: str
    co2e_kg_per_mwh: float
    source_field: str

    @property
    def co2e_kg_per_kwh(self) -> float:
        return self.co2e_kg_per_mwh / 1000.0

    def as_dict(self) -> dict[str, object]:
        result = asdict(self)
        result["co2e_kg_per_kwh"] = self.co2e_kg_per_kwh
        return result


def summarize_noaa_tmy(
    csv_path: str | Path, metadata_path: str | Path
) -> TmyClimateSummary:
    """Summarize an NCEI TMY CSV while treating -999 as missing."""
    with Path(metadata_path).open(encoding="utf-8-sig", newline="") as stream:
        metadata = {
            row[0]: row[1]
            for row in csv.reader(stream)
            if len(row) >= 2
        }
    with Path(csv_path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        provider_header = next(reader)
        provider_values = next(reader)
        fields = next(reader)
        provider = dict(zip(provider_header, provider_values))
        rows = [dict(zip(fields, row)) for row in reader]

    temperatures: list[float] = []
    humidities: list[float] = []
    missing: dict[str, int] = {}
    for row in rows:
        for field, raw_value in row.items():
            if raw_value.strip() == "-999.0":
                missing[field] = missing.get(field, 0) + 1
        temperature = float(row["Temperature"])
        if temperature != -999.0:
            temperatures.append(temperature)
        humidity = float(row["Relative Humidity"])
        if humidity != -999.0:
            humidities.append(humidity)
    if not temperatures:
        raise ValueError("TMY file has no valid dry-bulb temperatures")

    return TmyClimateSummary(
        station_id=provider["Location ID"],
        station_name=provider["Location Name"],
        latitude=float(provider["Latitude"]),
        longitude=float(provider["Longitude"]),
        elevation_m=float(metadata["Elevation (m)"]),
        record_start_year=int(provider["Data Start Year"]),
        record_end_year=int(provider["Data End Year"]),
        hours=len(rows),
        mean_dry_bulb_c=fmean(temperatures),
        minimum_dry_bulb_c=min(temperatures),
        maximum_dry_bulb_c=max(temperatures),
        mean_relative_humidity_pct=fmean(humidities),
        cooling_degree_hours_18c=sum(max(value - 18.0, 0.0) for value in temperatures),
        hours_above_30c=sum(value > 30.0 for value in temperatures),
        hours_below_5c=sum(value < 5.0 for value in temperatures),
        missing_value_counts=dict(sorted(missing.items())),
    )


def load_oekobaudat_factors(
    csv_path: str | Path,
    uuids: Iterable[str],
    *,
    module: str = "A1-A3",
) -> list[OekobaudatFactor]:
    """Load selected EN 15804+A2 indicators from an ÖKOBAUDAT CSV export."""
    requested = set(uuids)
    found: dict[str, OekobaudatFactor] = {}
    with Path(csv_path).open(
        encoding="utf-8-sig", errors="replace", newline=""
    ) as stream:
        for row in csv.DictReader(stream, delimiter=";"):
            uuid = row["UUID"]
            if uuid not in requested or row["Modul"] != module:
                continue
            found[uuid] = OekobaudatFactor(
                uuid=uuid,
                name=row["Name (en)"] or row["Name (de)"],
                module=module,
                geography=row["Laenderkennung"],
                dataset_type=row["Typ"],
                reference_year=int(row["Referenzjahr"]),
                reference_unit=row["Bezugseinheit"],
                gwp_total_kgco2e=float(row["GWPtotal (A2)"]),
                nonrenewable_primary_energy_mj=float(row["PENRT"]),
                renewable_primary_energy_mj=float(row["PERT"]),
                freshwater_m3=float(row["FW"]),
                url=row["URL"],
            )
    missing = requested - found.keys()
    if missing:
        raise KeyError(f"ÖKOBAUDAT UUIDs not found in module {module}: {sorted(missing)}")
    return [found[uuid] for uuid in sorted(found)]


def inspect_glad_jsonld(zip_path: str | Path) -> GladProcess:
    """Read the root process metadata from a GLAD/openLCA JSON-LD package."""
    path = Path(zip_path)
    uuid = path.name.split("_", 1)[0]
    with ZipFile(path) as archive:
        process = json.loads(archive.read(f"processes/{uuid}.json"))
    documentation = process.get("processDocumentation", {})
    owner = documentation.get("dataSetOwner") or {}
    location = process.get("location") or {}
    return GladProcess(
        archive=path.name,
        uuid=uuid,
        name=process.get("name", ""),
        description=process.get("description", ""),
        category=process.get("category", ""),
        geography=location.get("name", ""),
        process_type=process.get("processType", ""),
        valid_from=documentation.get("validFrom", ""),
        valid_until=documentation.get("validUntil", ""),
        owner=owner.get("name", ""),
    )


def _xlsx_shared_strings(archive: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    namespace = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    return [
        "".join(text.text or "" for text in item.findall(".//x:t", namespace))
        for item in root.findall("x:si", namespace)
    ]


def _xlsx_sheet_path(archive: ZipFile, sheet_name: str) -> str:
    main = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    relationship_id = None
    for sheet in workbook.findall(f".//{{{main}}}sheet"):
        if sheet.attrib.get("name") == sheet_name:
            relationship_id = sheet.attrib[f"{{{rel}}}id"]
            break
    if relationship_id is None:
        raise KeyError(f"Worksheet not found: {sheet_name}")
    relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    for item in relationships:
        if item.attrib.get("Id") == relationship_id:
            target = item.attrib["Target"].lstrip("/")
            return target if target.startswith("xl/") else f"xl/{target}"
    raise KeyError(f"Worksheet relationship not found: {sheet_name}")


def _column_number(cell_reference: str) -> int:
    letters = re.match(r"[A-Z]+", cell_reference)
    if not letters:
        raise ValueError(f"Invalid cell reference: {cell_reference}")
    result = 0
    for character in letters.group(0):
        result = result * 26 + ord(character) - ord("A") + 1
    return result


def load_egrid_state_factor(
    xlsx_path: str | Path, state_abbreviation: str
) -> EgridStateFactor:
    """Read eGRID's state total-output CO2e rate using only the Python stdlib."""
    namespace = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    with ZipFile(xlsx_path) as archive:
        shared = _xlsx_shared_strings(archive)
        path = _xlsx_sheet_path(archive, "ST23")
        root = ET.fromstring(archive.read(path))
    parsed_rows: list[dict[int, object]] = []
    for row in root.findall(f".//{{{namespace}}}row"):
        values: dict[int, object] = {}
        for cell in row.findall(f"{{{namespace}}}c"):
            reference = cell.attrib["r"]
            value_node = cell.find(f"{{{namespace}}}v")
            if value_node is None:
                continue
            raw = value_node.text or ""
            if cell.attrib.get("t") == "s":
                value: object = shared[int(raw)]
            else:
                try:
                    value = float(raw)
                except ValueError:
                    value = raw
            values[_column_number(reference)] = value
        parsed_rows.append(values)
    if len(parsed_rows) < 3:
        raise ValueError("eGRID ST23 worksheet is incomplete")
    field_codes = {
        column: str(value) for column, value in parsed_rows[1].items()
    }
    columns = {code: column for column, code in field_codes.items()}
    required = {"YEAR", "PSTATABB", "STC2ERTA"}
    if not required.issubset(columns):
        raise ValueError(f"eGRID ST23 fields missing: {sorted(required - columns.keys())}")
    for row in parsed_rows[2:]:
        if row.get(columns["PSTATABB"]) == state_abbreviation:
            return EgridStateFactor(
                data_year=int(float(row[columns["YEAR"]])),
                state="Arkansas" if state_abbreviation == "AR" else state_abbreviation,
                state_abbreviation=state_abbreviation,
                co2e_kg_per_mwh=float(row[columns["STC2ERTA"]]),
                source_field="ST23!STC2ERTA",
            )
    raise KeyError(f"State not found in eGRID ST23: {state_abbreviation}")


def operational_ghg_per_it_mwh(
    egrid_factor: EgridStateFactor, pue: float
) -> float:
    """Location-based operational GHG per delivered IT MWh."""
    if pue < 1:
        raise ValueError("PUE cannot be less than 1")
    return egrid_factor.co2e_kg_per_mwh * pue
