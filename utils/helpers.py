"""
Helper utilities for Phantom Detector.
Common functions used across the application.
"""

import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Union

# Try to import external dependencies, provide fallbacks if not available
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    class MockNumpy:
        @staticmethod 
        def random():
            class MockRandom:
                @staticmethod
                def normal(mean=0, std=1):
                    import random
                    return random.gauss(mean, std)
            return MockRandom()
        @staticmethod
        def mean(values):
            return sum(values) / len(values) if values else 0
    np = MockNumpy()

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    # Simple pandas Series mock
    class MockSeries:
        def __init__(self, data):
            self.data = list(data)
        def rolling(self, window):
            return MockRolling(self.data, window)
        def mean(self):
            return sum(self.data) / len(self.data) if self.data else 0
        def std(self):
            if len(self.data) < 2:
                return 0
            mean_val = self.mean()
            variance = sum((x - mean_val) ** 2 for x in self.data) / len(self.data)
            return variance ** 0.5
        def fillna(self, method='bfill'):
            return self
        def tolist(self):
            return self.data
    
    class MockRolling:
        def __init__(self, data, window):
            self.data = data
            self.window = window
        def mean(self):
            if len(self.data) < self.window:
                return MockSeries(self.data)
            result = []
            for i in range(len(self.data)):
                if i < self.window - 1:
                    result.append(self.data[i])
                else:
                    window_data = self.data[i-self.window+1:i+1]
                    result.append(sum(window_data) / len(window_data))
            return MockSeries(result)
    
    class MockPandas:
        @staticmethod
        def Series(data):
            return MockSeries(data)
    pd = MockPandas()


def get_timestamp() -> float:
    """Get current Unix timestamp."""
    return time.time()


def get_iso_timestamp() -> str:
    """Get current ISO format timestamp."""
    return datetime.now(timezone.utc).isoformat()


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format currency amount for display.
    
    Args:
        amount: Currency amount
        currency: Currency symbol
    
    Returns:
        Formatted currency string
    """
    if amount >= 1_000_000:
        return f"${amount/1_000_000:.2f}M {currency}"
    elif amount >= 1_000:
        return f"${amount/1_000:.2f}K {currency}"
    else:
        return f"${amount:.2f} {currency}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format percentage for display.
    
    Args:
        value: Percentage value (0.05 = 5%)
        decimals: Number of decimal places
    
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def calculate_price_change(current: float, previous: float) -> Dict[str, float]:
    """
    Calculate price change metrics.
    
    Args:
        current: Current price
        previous: Previous price
    
    Returns:
        Dictionary with absolute and percentage changes
    """
    absolute_change = current - previous
    percentage_change = (absolute_change / previous) if previous != 0 else 0
    
    return {
        "absolute": absolute_change,
        "percentage": percentage_change,
        "current": current,
        "previous": previous
    }


def generate_random_walk(
    start_value: float,
    steps: int,
    volatility: float = 0.02,
    trend: float = 0.0
) -> List[float]:
    """
    Generate random walk data for price simulation.
    
    Args:
        start_value: Starting value
        steps: Number of steps
        volatility: Volatility factor
        trend: Trend factor (positive = upward trend)
    
    Returns:
        List of generated values
    """
    values = [start_value]
    current = start_value
    
    for _ in range(steps - 1):
        # Random walk with trend and volatility
        change = np.random.normal(trend, volatility)
        current *= (1 + change)
        values.append(current)
    
    return values


def moving_average(data: List[float], window: int) -> List[float]:
    """
    Calculate moving average.
    
    Args:
        data: Input data
        window: Window size
    
    Returns:
        Moving average values
    """
    if len(data) < window:
        return data.copy()
    
    df = pd.Series(data)
    ma = df.rolling(window=window).mean()
    return ma.fillna(method='bfill').tolist()


def detect_outliers(data: List[float], threshold: float = 2.0) -> List[bool]:
    """
    Detect outliers using z-score method.
    
    Args:
        data: Input data
        threshold: Z-score threshold
    
    Returns:
        Boolean list indicating outliers
    """
    if len(data) < 3:
        return [False] * len(data)
    
    df = pd.Series(data)
    z_scores = np.abs((df - df.mean()) / df.std())
    return (z_scores > threshold).tolist()


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero
    
    Returns:
        Division result or default value
    """
    return numerator / denominator if denominator != 0 else default


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp value between min and max.
    
    Args:
        value: Input value
        min_val: Minimum value
        max_val: Maximum value
    
    Returns:
        Clamped value
    """
    return max(min_val, min(value, max_val))


def exponential_moving_average(
    data: List[float],
    alpha: float = 0.1
) -> List[float]:
    """
    Calculate exponential moving average.
    
    Args:
        data: Input data
        alpha: Smoothing factor (0 < alpha < 1)
    
    Returns:
        EMA values
    """
    if not data:
        return []
    
    ema = [data[0]]
    for value in data[1:]:
        ema_value = alpha * value + (1 - alpha) * ema[-1]
        ema.append(ema_value)
    
    return ema