"""
Configuration module for Phantom Detector.
Centralized settings management for the trading intelligence platform.
"""

import os
from typing import Dict, Any

# Try to load environment variables if dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Continue without dotenv if not available
    pass


class Config:
    """Centralized configuration class for Phantom Detector."""
    
    # Application Settings
    APP_NAME = "Phantom Detector"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Dashboard Settings
    DASH_HOST = os.getenv("DASH_HOST", "127.0.0.1")
    DASH_PORT = int(os.getenv("DASH_PORT", "8050"))
    DASH_DEBUG = DEBUG
    
    # Mock Data Settings
    MOCK_DATA_ENABLED = True  # TODO: Set to False when integrating live APIs
    PRICE_UPDATE_INTERVAL = 1.0  # seconds
    INITIAL_PRICE = 50000.0  # Starting BTC price
    PRICE_VOLATILITY = 0.02  # 2% volatility
    VOLUME_RANGE = (100, 10000)  # Min/Max volume per update
    
    # Signal Processing Settings
    SPOOFING_THRESHOLD = 0.15  # 15% price movement threshold
    WHALE_THRESHOLD = 1000000  # $1M threshold for whale detection
    SMT_LOOKBACK_PERIODS = 20  # Periods for market structure analysis
    NARRATIVE_UPDATE_INTERVAL = 300  # seconds (5 minutes)
    
    # Oracle Settings
    ORACLE_CONFIDENCE_THRESHOLD = 0.7  # 70% confidence minimum
    RECOMMENDATION_COOLDOWN = 3600  # 1 hour between recommendations
    
    # Logging Settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "logs/phantom_detector.log"
    LOG_MAX_BYTES = 10_000_000  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Future API Settings (TODO: Implement when ready)
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
    BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY", "")
    COINBASE_API_KEY = os.getenv("COINBASE_API_KEY", "")
    COINBASE_SECRET_KEY = os.getenv("COINBASE_SECRET_KEY", "")
    
    @classmethod
    def get_mock_data_config(cls) -> Dict[str, Any]:
        """Get mock data generation configuration."""
        return {
            "price_update_interval": cls.PRICE_UPDATE_INTERVAL,
            "initial_price": cls.INITIAL_PRICE,
            "volatility": cls.PRICE_VOLATILITY,
            "volume_range": cls.VOLUME_RANGE,
        }
    
    @classmethod
    def get_signal_config(cls) -> Dict[str, Any]:
        """Get signal processing configuration."""
        return {
            "spoofing_threshold": cls.SPOOFING_THRESHOLD,
            "whale_threshold": cls.WHALE_THRESHOLD,
            "smt_lookback": cls.SMT_LOOKBACK_PERIODS,
            "narrative_interval": cls.NARRATIVE_UPDATE_INTERVAL,
        }
    
    @classmethod
    def get_oracle_config(cls) -> Dict[str, Any]:
        """Get oracle configuration."""
        return {
            "confidence_threshold": cls.ORACLE_CONFIDENCE_THRESHOLD,
            "recommendation_cooldown": cls.RECOMMENDATION_COOLDOWN,
        }
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode."""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"


# Global config instance
config = Config()