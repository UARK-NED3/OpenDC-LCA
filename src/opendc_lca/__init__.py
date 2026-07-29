"""OpenDC-LCA public API."""

from .engine import analyze, compare, sensitivity
from .audit import audit
from .report import generate_experimental_report, generate_report
from .io import load_scenario
from .models import Scenario, ValidationError
from .performance import (
    PerformancePoint,
    PerformanceSummary,
    apply_performance,
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
    "PerformancePoint", "PerformanceSummary", "apply_performance",
    "load_performance_map", "summarize_performance",
    "MonteCarloResult", "ParameterDistribution", "monte_carlo",
]
__version__ = "0.3.0"
