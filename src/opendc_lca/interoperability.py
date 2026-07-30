"""openLCA JSON-LD and Brightway interoperability.

The adapters preserve inventory exchanges and provenance. They do not convert
LCIA methods or silently turn LCIA results into elementary flows.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Iterable
from uuid import NAMESPACE_URL, uuid5
from zipfile import ZIP_DEFLATED, ZipFile

from .models import Scenario, ValidationError


@dataclass(frozen=True)
class InventoryExchange:
    internal_id: int
    flow_id: str
    flow_name: str
    flow_type: str
    amount: float
    unit: str
    is_input: bool
    is_reference: bool
    default_provider_id: str | None = None
    description: str = ""

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class InventoryProcess:
    id: str
    name: str
    description: str
    category: str
    process_type: str
    location: str
    version: str
    exchanges: tuple[InventoryExchange, ...]
    source_format: str = "openlca-json-ld"

    def as_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["exchanges"] = [exchange.as_dict() for exchange in self.exchanges]
        return data


def _load_exchange(raw: dict[str, Any]) -> InventoryExchange:
    flow = raw.get("flow") or {}
    unit = raw.get("unit") or {}
    provider = raw.get("defaultProvider") or {}
    try:
        amount = float(raw["amount"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValidationError("openLCA exchange amount must be numeric") from exc
    flow_id = str(flow.get("@id", "")).strip()
    if not flow_id:
        raise ValidationError("openLCA exchange is missing flow @id")
    return InventoryExchange(
        internal_id=int(raw.get("internalId", 0)),
        flow_id=flow_id,
        flow_name=str(flow.get("name", "")),
        flow_type=str(flow.get("flowType", "")),
        amount=amount,
        unit=str(unit.get("name") or flow.get("refUnit") or ""),
        is_input=bool(raw.get("isInput")),
        is_reference=bool(raw.get("isQuantitativeReference")),
        default_provider_id=(
            str(provider["@id"]) if provider.get("@id") else None
        ),
        description=str(raw.get("description", "")),
    )


def _load_process(raw: dict[str, Any]) -> InventoryProcess:
    if raw.get("@type") != "Process" or not raw.get("@id"):
        raise ValidationError("JSON-LD object is not an openLCA Process")
    location = raw.get("location") or {}
    return InventoryProcess(
        id=str(raw["@id"]),
        name=str(raw.get("name", "")),
        description=str(raw.get("description", "")),
        category=str(raw.get("category", "")),
        process_type=str(raw.get("processType", "")),
        location=str(location.get("name") or location.get("@id") or ""),
        version=str(raw.get("version", "")),
        exchanges=tuple(
            _load_exchange(exchange) for exchange in raw.get("exchanges", [])
        ),
    )


def read_openlca_jsonld(
    source: str | Path,
    *,
    process_ids: Iterable[str] | None = None,
) -> list[InventoryProcess]:
    """Read complete process exchanges from an openLCA JSON-LD archive/folder."""
    path = Path(source)
    requested = set(process_ids or ())
    processes: list[InventoryProcess] = []
    if path.is_dir():
        files = sorted((path / "processes").glob("*.json"))
        for file in files:
            raw = json.loads(file.read_text(encoding="utf-8"))
            if not requested or raw.get("@id") in requested:
                processes.append(_load_process(raw))
    else:
        if path.suffix.lower() not in {".zip", ".jsonld"}:
            if path.suffix.lower() == ".zolca":
                raise ValidationError(
                    ".zolca is an openLCA database backup, not JSON-LD. "
                    "Open it in openLCA and export JSON-LD for portable exchange."
                )
            raise ValidationError("Expected an openLCA JSON-LD ZIP or folder")
        with ZipFile(path) as archive:
            names = sorted(
                name for name in archive.namelist()
                if name.startswith("processes/") and name.endswith(".json")
            )
            for name in names:
                raw = json.loads(archive.read(name))
                if not requested or raw.get("@id") in requested:
                    processes.append(_load_process(raw))
    if requested:
        missing = requested - {process.id for process in processes}
        if missing:
            raise ValidationError(
                "Requested openLCA process IDs not found: "
                + ", ".join(sorted(missing))
            )
    if not processes:
        raise ValidationError("No openLCA processes were found")
    return processes


def to_brightway_data(
    processes: Iterable[InventoryProcess],
    *,
    database_name: str,
) -> dict[tuple[str, str], dict[str, Any]]:
    """Convert openLCA process records to data accepted by bw2data.Database.write."""
    process_list = list(processes)
    process_ids = {process.id for process in process_list}
    output: dict[tuple[str, str], dict[str, Any]] = {}
    for process in process_list:
        exchanges: list[dict[str, Any]] = []
        for exchange in process.exchanges:
            if exchange.is_reference:
                kind = "production"
                target = (database_name, process.id)
            elif exchange.flow_type == "ELEMENTARY_FLOW":
                kind = "biosphere"
                target = ("biosphere3", exchange.flow_id)
            else:
                kind = "technosphere"
                provider = exchange.default_provider_id or exchange.flow_id
                target = (
                    database_name if provider in process_ids else database_name,
                    provider,
                )
            exchanges.append({
                "input": target,
                "amount": exchange.amount,
                "type": kind,
                "name": exchange.flow_name,
                "unit": exchange.unit,
                "comment": exchange.description,
                "opendc_lca_flow_id": exchange.flow_id,
            })
        reference = next(
            (item for item in process.exchanges if item.is_reference),
            None,
        )
        output[(database_name, process.id)] = {
            "name": process.name,
            "reference product": (
                reference.flow_name if reference else process.name
            ),
            "unit": reference.unit if reference else "unit",
            "location": process.location or "GLO",
            "database": database_name,
            "code": process.id,
            "type": "process",
            "comment": process.description,
            "classifications": [("openLCA category", process.category)],
            "exchanges": exchanges,
            "opendc_lca_source_format": process.source_format,
        }
    return output


def write_brightway_json(
    processes: Iterable[InventoryProcess],
    destination: str | Path,
    *,
    database_name: str,
) -> Path:
    """Write a portable JSON representation of Brightway database-write data."""
    data = to_brightway_data(processes, database_name=database_name)
    serializable = [
        {"key": list(key), "dataset": value}
        for key, value in sorted(data.items())
    ]
    path = Path(destination)
    path.write_text(json.dumps({
        "format": "brightway-database-write-v1",
        "database": database_name,
        "datasets": serializable,
    }, indent=2), encoding="utf-8")
    return path


def install_brightway_database(
    processes: Iterable[InventoryProcess],
    *,
    database_name: str,
    overwrite: bool = False,
) -> int:
    """Install into the active Brightway project when bw2data is available."""
    try:
        from bw2data import Database, databases  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Brightway is optional. Install bw2data in the target environment "
            "or use write_brightway_json for a dependency-free export."
        ) from exc
    if database_name in databases and not overwrite:
        raise FileExistsError(
            f"Brightway database already exists: {database_name}"
        )
    data = to_brightway_data(processes, database_name=database_name)
    Database(database_name).write(data)
    return len(data)


def _stable_id(label: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"opendc-lca:{label}"))


def export_scenario_openlca_jsonld(
    scenario: Scenario,
    destination: str | Path,
) -> Path:
    """Export an annual foreground process for linking in openLCA.

    Impact factors remain documented in the OpenDC-LCA scenario; this export
    contains physical foreground exchanges only and intentionally omits LCIA
    results.
    """
    path = Path(destination)
    process_id = _stable_id(scenario.source_digest_sha256 or scenario.name)
    process_name = f"OpenDC-LCA annual operation - {scenario.name}"
    flows = [
        ("reference", "IT service, delivered electricity", "PRODUCT_FLOW", "MWh"),
        ("electricity", "Electricity, facility", "PRODUCT_FLOW", "kWh"),
        ("water", "Water, cooling consumption", "ELEMENTARY_FLOW", "L"),
    ]
    flow_records: dict[str, dict[str, Any]] = {}
    for key, name, flow_type, unit in flows:
        flow_id = _stable_id(f"{process_id}:{key}")
        flow_records[key] = {
            "@type": "Flow",
            "@id": flow_id,
            "name": name,
            "flowType": flow_type,
            "refUnit": unit,
        }
    annual_it_kwh = (
        scenario.it_capacity_kw * scenario.capacity_factor * 8760
    )
    exchanges = [
        {
            "@type": "Exchange",
            "internalId": 1,
            "amount": annual_it_kwh / 1000,
            "isInput": False,
            "isQuantitativeReference": True,
            "flow": flow_records["reference"],
            "unit": {"@type": "Unit", "@id": _stable_id("unit:MWh"), "name": "MWh"},
        },
        {
            "@type": "Exchange",
            "internalId": 2,
            "amount": annual_it_kwh * scenario.pue,
            "isInput": True,
            "flow": flow_records["electricity"],
            "unit": {"@type": "Unit", "@id": _stable_id("unit:kWh"), "name": "kWh"},
        },
        {
            "@type": "Exchange",
            "internalId": 3,
            "amount": annual_it_kwh * scenario.onsite_water_l_per_kwh_it,
            "isInput": True,
            "flow": flow_records["water"],
            "unit": {"@type": "Unit", "@id": _stable_id("unit:L"), "name": "L"},
        },
    ]
    for index, component in enumerate(scenario.components, start=10):
        key = f"component-{index}"
        flow_id = _stable_id(f"{process_id}:{key}")
        record = {
            "@type": "Flow",
            "@id": flow_id,
            "name": component.name,
            "flowType": "PRODUCT_FLOW",
            "refUnit": "Item(s)",
        }
        flow_records[key] = record
        exchanges.append({
            "@type": "Exchange",
            "internalId": index,
            "amount": component.quantity,
            "isInput": True,
            "description": (
                "Foreground quantity; lifecycle factors remain in the "
                "OpenDC-LCA scenario."
            ),
            "flow": record,
            "unit": {
                "@type": "Unit",
                "@id": _stable_id("unit:items"),
                "name": "Item(s)",
            },
        })
    process = {
        "@type": "Process",
        "@id": process_id,
        "name": process_name,
        "description": (
            "OpenDC-LCA foreground export. Link inputs to compatible background "
            "providers and select LCIA methods in openLCA."
        ),
        "category": "OpenDC-LCA/Data center cooling",
        "version": "01.00.000",
        "processType": "UNIT_PROCESS",
        "location": {"@type": "Location", "name": "unspecified"},
        "processDocumentation": {
            "inventoryMethodDescription": (
                "Physical foreground exchanges exported by OpenDC-LCA."
            ),
            "modelingConstantsDescription": (
                f"Scenario digest: {scenario.source_digest_sha256}"
            ),
        },
        "exchanges": exchanges,
    }
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr("openlca.json", json.dumps({
            "@type": "Library",
            "name": "OpenDC-LCA foreground export",
            "version": "1.1.0",
        }, indent=2))
        archive.writestr(
            f"processes/{process_id}.json",
            json.dumps(process, indent=2),
        )
        for record in flow_records.values():
            archive.writestr(
                f"flows/{record['@id']}.json",
                json.dumps(record, indent=2),
            )
    return path
