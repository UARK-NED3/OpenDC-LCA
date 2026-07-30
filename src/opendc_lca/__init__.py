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
]
__version__ = "0.6.0"
