"""OpenDC-LCA public API."""

from .engine import analyze, compare, sensitivity
from .io import load_scenario
from .models import Scenario, ValidationError

__all__ = [
    "Scenario", "ValidationError", "analyze", "compare", "load_scenario",
    "sensitivity",
]
__version__ = "0.2.0"
