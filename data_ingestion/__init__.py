"""
Data ingestion package for Phantom Detector.
Handles mock data generation and future live API integration.
"""

from .mock_data import MockDataGenerator, mock_generator

__all__ = ["MockDataGenerator", "mock_generator"]