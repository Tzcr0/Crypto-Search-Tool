"""
Basic import tests for Phantom Detector.
Ensures all modules can be imported correctly.
"""

import pytest
import sys
import importlib
from typing import List


class TestImports:
    """Test that all modules can be imported successfully."""
    
    def test_config_imports(self):
        """Test config module imports."""
        try:
            from config import config, Config
            assert config is not None
            assert Config is not None
            assert hasattr(config, 'APP_NAME')
            assert hasattr(config, 'VERSION')
        except ImportError as e:
            pytest.fail(f"Failed to import config: {e}")
    
    def test_utils_imports(self):
        """Test utils module imports."""
        try:
            from utils import logger, setup_logging
            from utils.helpers import (
                get_timestamp, format_currency, format_percentage,
                calculate_price_change, generate_random_walk
            )
            assert logger is not None
            assert setup_logging is not None
            assert get_timestamp is not None
            assert format_currency is not None
        except ImportError as e:
            pytest.fail(f"Failed to import utils: {e}")
    
    def test_data_ingestion_imports(self):
        """Test data ingestion module imports."""
        try:
            from data_ingestion import MockDataGenerator, mock_generator
            assert MockDataGenerator is not None
            assert mock_generator is not None
            assert hasattr(mock_generator, 'subscribe')
            assert hasattr(mock_generator, 'get_current_price')
        except ImportError as e:
            pytest.fail(f"Failed to import data_ingestion: {e}")
    
    def test_signal_processing_imports(self):
        """Test signal processing module imports."""
        try:
            from signal_processing import SignalProcessor, signal_processor
            assert SignalProcessor is not None
            assert signal_processor is not None
            assert hasattr(signal_processor, 'detect_spoofing')
            assert hasattr(signal_processor, 'track_whales')
            assert hasattr(signal_processor, 'analyze_market_structure')
        except ImportError as e:
            pytest.fail(f"Failed to import signal_processing: {e}")
    
    def test_phantom_oracle_imports(self):
        """Test phantom oracle module imports."""
        try:
            from phantom_oracle import PhantomOracle, phantom_oracle
            assert PhantomOracle is not None
            assert phantom_oracle is not None
            assert hasattr(phantom_oracle, 'analyze_market_state')
            assert hasattr(phantom_oracle, 'summarize_trends')
            assert hasattr(phantom_oracle, 'recommend_trades')
        except ImportError as e:
            pytest.fail(f"Failed to import phantom_oracle: {e}")
    
    def test_dashboard_ui_imports(self):
        """Test dashboard UI module imports."""
        try:
            from dashboard_ui import PhantomDashboard, phantom_dashboard
            assert PhantomDashboard is not None
            assert phantom_dashboard is not None
            assert hasattr(phantom_dashboard, 'app')
            assert hasattr(phantom_dashboard, 'run')
        except ImportError as e:
            pytest.fail(f"Failed to import dashboard_ui: {e}")
    
    def test_main_import(self):
        """Test main module import."""
        try:
            import main
            assert hasattr(main, 'PhantomDetectorApp')
            assert hasattr(main, 'main')
        except ImportError as e:
            pytest.fail(f"Failed to import main: {e}")


class TestModuleFunctionality:
    """Test basic functionality of key modules."""
    
    def test_config_values(self):
        """Test that config has expected values."""
        from config import config
        
        assert config.APP_NAME == "Phantom Detector"
        assert config.VERSION == "1.0.0"
        assert isinstance(config.DASH_PORT, int)
        assert config.DASH_PORT > 0
        assert config.MOCK_DATA_ENABLED is True
        
    def test_utils_functions(self):
        """Test utility functions work correctly."""
        from utils.helpers import (
            get_timestamp, format_currency, format_percentage,
            calculate_price_change
        )
        
        # Test timestamp
        timestamp = get_timestamp()
        assert isinstance(timestamp, float)
        assert timestamp > 0
        
        # Test currency formatting
        formatted = format_currency(1234.56)
        assert "$1.23K USD" in formatted
        
        # Test percentage formatting
        pct = format_percentage(0.1234)
        assert "12.34%" == pct
        
        # Test price change calculation
        change = calculate_price_change(110.0, 100.0)
        assert change["absolute"] == 10.0
        assert change["percentage"] == 0.1
    
    def test_mock_data_generator_basic(self):
        """Test mock data generator basic functionality."""
        from data_ingestion import mock_generator
        
        # Test initial state
        assert not mock_generator.is_running
        assert mock_generator.get_current_price() > 0
        
        # Test historical data generation
        historical = mock_generator.generate_historical_ohlcv(days=1)
        assert len(historical) > 0
        assert all("open" in candle for candle in historical)
        assert all("close" in candle for candle in historical)
        assert all("volume" in candle for candle in historical)
    
    def test_signal_processor_basic(self):
        """Test signal processor basic functionality."""
        from signal_processing import signal_processor
        
        # Test empty signals
        empty_signals = signal_processor._empty_signals()
        assert "timestamp" in empty_signals
        assert "spoofing" in empty_signals
        assert "whales" in empty_signals
        
        # Test recent alerts (should be empty initially)
        alerts = signal_processor.get_recent_alerts("all", 10)
        assert isinstance(alerts, list)
    
    def test_phantom_oracle_basic(self):
        """Test phantom oracle basic functionality."""
        from phantom_oracle import phantom_oracle
        
        # Test status
        status = phantom_oracle.get_oracle_status()
        assert "timestamp" in status
        assert "oracle_version" in status
        assert status["status"] == "active"
        
        # Test trend summary
        summary = phantom_oracle.summarize_trends()
        assert isinstance(summary, str)
        assert len(summary) > 0
        
        # Test market forecast
        forecast = phantom_oracle.get_market_forecast("1h")
        assert "timestamp" in forecast
        assert "scenarios" in forecast


class TestDependencies:
    """Test that required dependencies are available."""
    
    def test_required_packages(self):
        """Test that all required packages can be imported."""
        required_packages = [
            "plotly",
            "dash", 
            "pandas",
            "numpy",
            "requests"
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                importlib.import_module(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            pytest.fail(f"Missing required packages: {missing_packages}")
    
    def test_python_version(self):
        """Test that Python version is compatible."""
        assert sys.version_info >= (3, 8), "Python 3.8+ required"


if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__, "-v"])