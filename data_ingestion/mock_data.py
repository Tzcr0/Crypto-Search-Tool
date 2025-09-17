"""
Mock data generator for Phantom Detector.
Simulates real-time WebSocket/REST trading data for development and testing.
"""

import asyncio
import random
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Callable

# Try to import numpy, fallback to random if not available
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    # Create a simple fallback for numpy functions
    class MockNumpy:
        @staticmethod
        def random():
            class MockRandom:
                @staticmethod
                def normal(mean=0, std=1):
                    return random.gauss(mean, std)
                @staticmethod
                def uniform(low=0, high=1):
                    return random.uniform(low, high)
            return MockRandom()
        @staticmethod
        def mean(values):
            return sum(values) / len(values) if values else 0
        @staticmethod
        def abs(value):
            return abs(value)
    np = MockNumpy()

from config.settings import config
from utils.logging_config import logger
from utils.helpers import get_timestamp


class MockDataGenerator:
    """
    Mock data generator that simulates real-time trading data streams.
    
    This class generates realistic price movements, volume patterns, and market events
    to simulate what would come from real exchange APIs.
    """
    
    def __init__(self):
        """Initialize the mock data generator."""
        self.config = config.get_mock_data_config()
        self.current_price = self.config["initial_price"]
        self.is_running = False
        self.subscribers: List[Callable] = []
        self.price_history: List[Dict[str, Any]] = []
        self.volume_history: List[Dict[str, Any]] = []
        
        # Market state variables
        self.trend_direction = random.choice([-1, 1])  # -1 bearish, 1 bullish
        self.trend_strength = random.uniform(0.1, 0.8)
        self.market_session = "regular"  # regular, volatile, consolidation
        
        logger.info("MockDataGenerator initialized")
    
    def subscribe(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Subscribe to real-time data updates.
        
        Args:
            callback: Function to call with new data
        """
        self.subscribers.append(callback)
        logger.info(f"New subscriber added. Total subscribers: {len(self.subscribers)}")
    
    def unsubscribe(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Unsubscribe from data updates.
        
        Args:
            callback: Function to remove from subscribers
        """
        if callback in self.subscribers:
            self.subscribers.remove(callback)
            logger.info(f"Subscriber removed. Total subscribers: {len(self.subscribers)}")
    
    def _generate_price_tick(self) -> Dict[str, Any]:
        """
        Generate a single price tick with realistic market behavior.
        
        Returns:
            Dictionary containing price tick data
        """
        # Generate price movement based on current trend and volatility
        base_volatility = self.config["volatility"]
        
        # Adjust volatility based on market session
        if self.market_session == "volatile":
            volatility = base_volatility * 2.0
        elif self.market_session == "consolidation":
            volatility = base_volatility * 0.3
        else:
            volatility = base_volatility
        
        # Generate price change with trend bias
        trend_factor = self.trend_direction * self.trend_strength * 0.001
        random_factor = np.random.normal(0, volatility)
        price_change = trend_factor + random_factor
        
        # Update price
        new_price = self.current_price * (1 + price_change)
        new_price = max(new_price, 1000)  # Minimum price floor
        
        # Generate volume (higher volume during volatile periods)
        base_volume = random.uniform(*self.config["volume_range"])
        if abs(price_change) > volatility:  # High price movement
            volume_multiplier = random.uniform(1.5, 3.0)
        else:
            volume_multiplier = random.uniform(0.8, 1.2)
        
        volume = base_volume * volume_multiplier
        
        # Calculate price change metrics
        price_change_abs = new_price - self.current_price
        price_change_pct = (price_change_abs / self.current_price) * 100
        
        tick_data = {
            "timestamp": get_timestamp(),
            "datetime": datetime.now(timezone.utc).isoformat(),
            "symbol": "BTCUSD",
            "price": round(new_price, 2),
            "volume": round(volume, 2),
            "price_change": round(price_change_abs, 2),
            "price_change_pct": round(price_change_pct, 4),
            "bid": round(new_price * 0.9995, 2),  # Slight bid-ask spread
            "ask": round(new_price * 1.0005, 2),
            "high_24h": round(new_price * random.uniform(1.02, 1.08), 2),
            "low_24h": round(new_price * random.uniform(0.92, 0.98), 2),
            "volume_24h": round(random.uniform(50000, 200000), 2),
            "market_session": self.market_session,
            "trend_direction": self.trend_direction,
            "trend_strength": round(self.trend_strength, 3)
        }
        
        self.current_price = new_price
        return tick_data
    
    def _generate_trade_event(self) -> Dict[str, Any]:
        """
        Generate individual trade events.
        
        Returns:
            Dictionary containing trade event data
        """
        trade_size = random.uniform(0.01, 50.0)  # BTC amount
        trade_price = self.current_price * random.uniform(0.999, 1.001)  # Small price variation
        side = random.choice(["buy", "sell"])
        
        # Generate whale trades occasionally
        if random.random() < 0.05:  # 5% chance of whale trade
            trade_size = random.uniform(100, 1000)
            logger.info(f"Generated whale trade: {trade_size:.2f} BTC")
        
        # Generate suspicious trades for spoofing detection
        is_suspicious = random.random() < 0.02  # 2% chance
        if is_suspicious:
            # Large order that might be spoofing
            trade_size = random.uniform(500, 2000)
            trade_price = self.current_price * random.uniform(0.98, 1.02)
        
        return {
            "timestamp": get_timestamp(),
            "datetime": datetime.now(timezone.utc).isoformat(),
            "trade_id": f"trade_{int(time.time() * 1000)}_{random.randint(1000, 9999)}",
            "symbol": "BTCUSD",
            "side": side,
            "size": round(trade_size, 6),
            "price": round(trade_price, 2),
            "value": round(trade_size * trade_price, 2),
            "is_whale": trade_size >= 100,
            "is_suspicious": is_suspicious,
            "exchange": "mock_exchange"
        }
    
    def _update_market_conditions(self) -> None:
        """Update market trend and session conditions periodically."""
        # Change trend direction occasionally
        if random.random() < 0.1:  # 10% chance
            self.trend_direction *= -1
            logger.info(f"Trend direction changed to {'bullish' if self.trend_direction > 0 else 'bearish'}")
        
        # Adjust trend strength
        if random.random() < 0.2:  # 20% chance
            self.trend_strength = random.uniform(0.1, 0.8)
        
        # Change market session
        if random.random() < 0.05:  # 5% chance
            old_session = self.market_session
            self.market_session = random.choice(["regular", "volatile", "consolidation"])
            if old_session != self.market_session:
                logger.info(f"Market session changed from {old_session} to {self.market_session}")
    
    async def start_price_stream(self) -> None:
        """
        Start the continuous price data stream.
        
        This coroutine generates price ticks at regular intervals and notifies subscribers.
        """
        self.is_running = True
        logger.info("Starting mock price stream")
        
        while self.is_running:
            try:
                # Generate price tick
                tick_data = self._generate_price_tick()
                self.price_history.append(tick_data)
                
                # Keep only last 1000 ticks in memory
                if len(self.price_history) > 1000:
                    self.price_history.pop(0)
                
                # Generate trade events (multiple trades per tick)
                num_trades = random.randint(1, 5)
                trade_events = [self._generate_trade_event() for _ in range(num_trades)]
                
                # Combine data for subscribers
                market_data = {
                    "type": "market_update",
                    "tick": tick_data,
                    "trades": trade_events,
                    "timestamp": get_timestamp()
                }
                
                # Notify all subscribers
                for callback in self.subscribers:
                    try:
                        callback(market_data)
                    except Exception as e:
                        logger.error(f"Error in subscriber callback: {e}")
                
                # Update market conditions periodically
                self._update_market_conditions()
                
                # Wait for next tick
                await asyncio.sleep(self.config["price_update_interval"])
                
            except Exception as e:
                logger.error(f"Error in price stream: {e}")
                await asyncio.sleep(1)  # Brief pause before retry
    
    def stop_stream(self) -> None:
        """Stop the price data stream."""
        self.is_running = False
        logger.info("Mock price stream stopped")
    
    def get_historical_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get historical price data.
        
        Args:
            limit: Number of historical records to return
        
        Returns:
            List of historical price data
        """
        return self.price_history[-limit:] if self.price_history else []
    
    def get_current_price(self) -> float:
        """Get the current price."""
        return self.current_price
    
    def generate_historical_ohlcv(
        self,
        days: int = 30,
        interval: str = "1h"
    ) -> List[Dict[str, Any]]:
        """
        Generate historical OHLCV data for backtesting.
        
        Args:
            days: Number of days of historical data
            interval: Time interval (1m, 5m, 15m, 1h, 4h, 1d)
        
        Returns:
            List of OHLCV candles
        """
        # Convert interval to minutes
        interval_minutes = {
            "1m": 1, "5m": 5, "15m": 15, "30m": 30,
            "1h": 60, "4h": 240, "1d": 1440
        }.get(interval, 60)
        
        total_candles = (days * 1440) // interval_minutes
        
        # Generate price forecast based on interval using simple random walk
        if interval == "1h":
            price_change_range = (-0.02, 0.02)  # ±2%
        elif interval == "4h":
            price_change_range = (-0.05, 0.05)  # ±5%
        elif interval == "1d":
            price_change_range = (-0.10, 0.10)  # ±10%
        else:  # Default for shorter intervals
            price_change_range = (-0.01, 0.01)  # ±1%
        
        prices = []
        current_price = self.config["initial_price"]
        for i in range(total_candles * 4):
            change = random.uniform(*price_change_range)
            current_price *= (1 + change)
            prices.append(current_price)
        
        ohlcv_data = []
        start_time = time.time() - (days * 86400)  # Go back 'days' from now
        
        for i in range(total_candles):
            # Get 4 prices for this candle
            candle_start_idx = i * 4
            candle_prices = prices[candle_start_idx:candle_start_idx + 4]
            
            open_price = candle_prices[0]
            high_price = max(candle_prices)
            low_price = min(candle_prices)
            close_price = candle_prices[-1]
            
            # Generate realistic volume
            base_volume = random.uniform(1000, 10000)
            volatility_factor = (high_price - low_price) / open_price
            volume = base_volume * (1 + volatility_factor * 10)
            
            candle_time = start_time + (i * interval_minutes * 60)
            
            ohlcv_data.append({
                "timestamp": candle_time,
                "datetime": datetime.fromtimestamp(candle_time, timezone.utc).isoformat(),
                "symbol": "BTCUSD",
                "interval": interval,
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": round(volume, 2)
            })
        
        return ohlcv_data


# Global mock data generator instance
mock_generator = MockDataGenerator()