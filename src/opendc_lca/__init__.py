"""OpenDC-LCA public API."""

from .engine import analyze, compare, sensitivity
from .audit import audit
from .report import generate_experimental_report, generate_report
from .io import load_scenario
from .models import Scenario, ValidationError
from .performance import (
    HourlyPerformanceResult,
    InterpolatedPerformance,
    PerformancePoint,
    PerformanceSummary,
    apply_performance,
    integrate_hourly_performance,
    interpolate_performance,
    measurement_comparative_claim_allowed,
    load_performance_map,
    summarize_performance,
)
from .uncertainty import MonteCarloResult, ParameterDistribution, monte_carlo
from .api import (
    analyze_practitioner_study,
    analyze_scenario,
    audit_scenario,
    new_practitioner_study,
    practitioner_capabilities,
    prepare_practitioner_study,
    summarize_performance_csv,
    validate_scenario,
)
from .practitioner import write_practitioner_report
from .benchmark import (
    package_benchmark_release,
    validate_benchmark_manifest,
    validate_review_record,
)
from .interoperability import (
    InventoryExchange,
    InventoryProcess,
    export_scenario_openlca_jsonld,
    install_brightway_database,
    read_openlca_jsonld,
    to_brightway_data,
    write_brightway_json,
)

__all__ = [
    "Scenario", "ValidationError", "analyze", "compare", "load_scenario",
    "sensitivity",
    "audit",
    "generate_report",
    "generate_experimental_report",
    "PerformancePoint", "PerformanceSummary", "InterpolatedPerformance",
    "HourlyPerformanceResult", "apply_performance", "interpolate_performance",
    "integrate_hourly_performance",
    "measurement_comparative_claim_allowed",
    "load_performance_map", "summarize_performance",
    "MonteCarloResult", "ParameterDistribution", "monte_carlo",
    "analyze_scenario", "audit_scenario", "summarize_performance_csv",
    "validate_scenario", "practitioner_capabilities",
    "new_practitioner_study", "prepare_practitioner_study",
    "analyze_practitioner_study", "write_practitioner_report",
    "InventoryExchange", "InventoryProcess", "read_openlca_jsonld",
    "export_scenario_openlca_jsonld", "to_brightway_data",
    "write_brightway_json", "install_brightway_database",
    "validate_benchmark_manifest", "validate_review_record",
    "package_benchmark_release",
]
__version__ = "1.1.0"
