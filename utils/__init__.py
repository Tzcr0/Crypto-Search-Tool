"""
Utilities package for Phantom Detector.
"""

from .logging_config import setup_logging, logger
from .helpers import (
    get_timestamp,
    get_iso_timestamp,
    format_currency,
    format_percentage,
    calculate_price_change,
    generate_random_walk,
    moving_average,
    detect_outliers,
    safe_divide,
    clamp,
    exponential_moving_average
)

__all__ = [
    "setup_logging",
    "logger", 
    "get_timestamp",
    "get_iso_timestamp",
    "format_currency",
    "format_percentage",
    "calculate_price_change",
    "generate_random_walk",
    "moving_average",
    "detect_outliers",
    "safe_divide",
    "clamp",
    "exponential_moving_average"
]