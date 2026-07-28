"""OpenDC-LCA public API."""

from .engine import analyze, compare
from .io import load_scenario
from .models import Scenario, ValidationError

__all__ = ["Scenario", "ValidationError", "analyze", "compare", "load_scenario"]
__version__ = "0.1.0"
