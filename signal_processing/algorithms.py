"""
Signal processing algorithms for Phantom Detector.
Core detection algorithms for spoofing, whale tracking, and market structure analysis.
"""

import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple

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
                @staticmethod
                def uniform(low=0, high=1):
                    import random
                    return random.uniform(low, high)
            return MockRandom()
        @staticmethod
        def mean(values):
            return sum(values) / len(values) if values else 0
        @staticmethod
        def abs(value):
            return abs(value)
        @staticmethod
        def choice(values):
            import random
            return random.choice(values)
    np = MockNumpy()

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from config.settings import config
from utils.logging_config import logger
from utils.helpers import (
    get_timestamp, 
    moving_average, 
    detect_outliers,
    exponential_moving_average,
    safe_divide
)


class SignalProcessor:
    """
    Main signal processing class that analyzes market data for various patterns and anomalies.
    """
    
    def __init__(self):
        """Initialize the signal processor."""
        self.config = config.get_signal_config()
        self.price_buffer: List[Dict[str, Any]] = []
        self.trade_buffer: List[Dict[str, Any]] = []
        self.spoofing_alerts: List[Dict[str, Any]] = []
        self.whale_alerts: List[Dict[str, Any]] = []
        self.smt_signals: List[Dict[str, Any]] = []
        self.narrative_signals: List[Dict[str, Any]] = []
        
        # State tracking
        self.last_narrative_update = 0
        self.market_structure_state = "neutral"  # bullish, bearish, neutral
        
        logger.info("SignalProcessor initialized")
    
    def process_market_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming market data and generate signals.
        
        Args:
            market_data: Market data from data ingestion
        
        Returns:
            Dictionary containing all generated signals
        """
        try:
            # Extract tick and trade data
            tick_data = market_data.get("tick", {})
            trade_events = market_data.get("trades", [])
            
            # Update internal buffers
            self._update_buffers(tick_data, trade_events)
            
            # Generate signals
            spoofing_signals = self.detect_spoofing(trade_events)
            whale_signals = self.track_whales(trade_events)
            smt_signals = self.analyze_market_structure()
            narrative_signals = self.process_narrative_signals()
            
            # Compile all signals
            all_signals = {
                "timestamp": get_timestamp(),
                "spoofing": spoofing_signals,
                "whales": whale_signals,
                "market_structure": smt_signals,
                "narrative": narrative_signals,
                "market_state": self.market_structure_state,
                "price": tick_data.get("price", 0),
                "volume": tick_data.get("volume", 0)
            }
            
            return all_signals
            
        except Exception as e:
            logger.error(f"Error processing market data: {e}")
            return self._empty_signals()
    
    def detect_spoofing(self, trade_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect potential market manipulation and spoofing activities.
        
        This algorithm looks for:
        - Large orders that are quickly canceled
        - Unusual price movements followed by reversals
        - Abnormal order book patterns
        
        Args:
            trade_events: List of recent trade events
        
        Returns:
            List of spoofing alerts
        """
        spoofing_alerts = []
        
        try:
            # Check for suspicious trades in current batch
            for trade in trade_events:
                if trade.get("is_suspicious", False):
                    
                    # Analyze price impact
                    current_price = trade.get("price", 0)
                    recent_prices = [t.get("price", 0) for t in self.price_buffer[-10:]]
                    
                    if recent_prices:
                        avg_recent_price = np.mean(recent_prices)
                        price_deviation = abs(current_price - avg_recent_price) / avg_recent_price
                        
                        # Check if price deviation exceeds threshold
                        if price_deviation > self.config["spoofing_threshold"]:
                            alert = {
                                "id": f"spoof_{int(time.time() * 1000)}",
                                "timestamp": get_timestamp(),
                                "datetime": datetime.now(timezone.utc).isoformat(),
                                "type": "potential_spoofing",
                                "severity": "high" if price_deviation > 0.25 else "medium",
                                "trade_id": trade.get("trade_id", "unknown"),
                                "price": current_price,
                                "size": trade.get("size", 0),
                                "value": trade.get("value", 0),
                                "price_deviation": round(price_deviation * 100, 2),
                                "description": f"Large order detected with {price_deviation*100:.1f}% price deviation",
                                "confidence": min(0.95, price_deviation * 2)  # Higher deviation = higher confidence
                            }
                            
                            spoofing_alerts.append(alert)
                            self.spoofing_alerts.append(alert)
                            
                            logger.warning(f"Spoofing alert: {alert['description']}")
            
            # Check for order imbalance patterns
            if len(self.trade_buffer) > 20:
                recent_trades = self.trade_buffer[-20:]
                buy_volume = sum(t.get("size", 0) for t in recent_trades if t.get("side") == "buy")
                sell_volume = sum(t.get("size", 0) for t in recent_trades if t.get("side") == "sell")
                
                total_volume = buy_volume + sell_volume
                if total_volume > 0:
                    imbalance = abs(buy_volume - sell_volume) / total_volume
                    
                    # Significant imbalance might indicate manipulation
                    if imbalance > 0.8:  # 80% imbalance
                        alert = {
                            "id": f"imbalance_{int(time.time() * 1000)}",
                            "timestamp": get_timestamp(),
                            "datetime": datetime.now(timezone.utc).isoformat(),
                            "type": "order_imbalance",
                            "severity": "medium",
                            "buy_volume": round(buy_volume, 2),
                            "sell_volume": round(sell_volume, 2),
                            "imbalance_ratio": round(imbalance * 100, 1),
                            "description": f"Significant order imbalance detected: {imbalance*100:.1f}%",
                            "confidence": min(0.8, imbalance)
                        }
                        
                        spoofing_alerts.append(alert)
                        logger.info(f"Order imbalance detected: {imbalance*100:.1f}%")
            
        except Exception as e:
            logger.error(f"Error in spoofing detection: {e}")
        
        return spoofing_alerts
    
    def track_whales(self, trade_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Track large transactions and whale movements.
        
        Args:
            trade_events: List of recent trade events
        
        Returns:
            List of whale alerts
        """
        whale_alerts = []
        
        try:
            for trade in trade_events:
                trade_value = trade.get("value", 0)
                
                # Check if trade exceeds whale threshold
                if trade_value > self.config["whale_threshold"]:
                    
                    # Classify whale type based on trade characteristics
                    whale_type = self._classify_whale_trade(trade)
                    
                    alert = {
                        "id": f"whale_{int(time.time() * 1000)}",
                        "timestamp": get_timestamp(),
                        "datetime": datetime.now(timezone.utc).isoformat(),
                        "type": "whale_activity",
                        "whale_type": whale_type,
                        "severity": self._get_whale_severity(trade_value),
                        "trade_id": trade.get("trade_id", "unknown"),
                        "side": trade.get("side", "unknown"),
                        "size": trade.get("size", 0),
                        "price": trade.get("price", 0),
                        "value": trade_value,
                        "exchange": trade.get("exchange", "unknown"),
                        "description": f"Whale {trade.get('side', 'trade')}: ${trade_value:,.0f} ({trade.get('size', 0):.2f} BTC)",
                        "market_impact": self._estimate_market_impact(trade_value),
                        "confidence": 0.9  # High confidence for whale detection
                    }
                    
                    whale_alerts.append(alert)
                    self.whale_alerts.append(alert)
                    
                    logger.info(f"Whale alert: {alert['description']}")
            
        except Exception as e:
            logger.error(f"Error in whale tracking: {e}")
        
        return whale_alerts
    
    def analyze_market_structure(self) -> List[Dict[str, Any]]:
        """
        Analyze market structure using Smart Money Theory (SMT) concepts.
        
        Returns:
            List of market structure signals
        """
        smt_signals = []
        
        try:
            if len(self.price_buffer) < self.config["smt_lookback"]:
                return smt_signals
            
            # Get recent price data
            recent_data = self.price_buffer[-self.config["smt_lookback"]:]
            prices = [item.get("price", 0) for item in recent_data]
            volumes = [item.get("volume", 0) for item in recent_data]
            
            # Calculate technical indicators
            price_ma = moving_average(prices, 10)
            volume_ma = moving_average(volumes, 10)
            
            current_price = prices[-1]
            current_volume = volumes[-1]
            
            # Detect market structure breaks
            structure_break = self._detect_structure_break(prices)
            if structure_break:
                signal = {
                    "id": f"smt_{int(time.time() * 1000)}",
                    "timestamp": get_timestamp(),
                    "datetime": datetime.now(timezone.utc).isoformat(),
                    "type": "structure_break",
                    "direction": structure_break["direction"],
                    "strength": structure_break["strength"],
                    "price": current_price,
                    "description": f"Market structure break: {structure_break['direction']} momentum",
                    "confidence": structure_break["confidence"]
                }
                smt_signals.append(signal)
                self.market_structure_state = structure_break["direction"]
            
            # Detect liquidity grabs
            liquidity_grab = self._detect_liquidity_grab(prices, volumes)
            if liquidity_grab:
                signal = {
                    "id": f"liquidity_{int(time.time() * 1000)}",
                    "timestamp": get_timestamp(),
                    "datetime": datetime.now(timezone.utc).isoformat(),
                    "type": "liquidity_grab",
                    "direction": liquidity_grab["direction"],
                    "price": current_price,
                    "volume": current_volume,
                    "description": f"Liquidity grab detected: {liquidity_grab['direction']}",
                    "confidence": liquidity_grab["confidence"]
                }
                smt_signals.append(signal)
            
            # Detect order blocks
            order_block = self._detect_order_block(prices, volumes)
            if order_block:
                signal = {
                    "id": f"orderblock_{int(time.time() * 1000)}",
                    "timestamp": get_timestamp(),
                    "datetime": datetime.now(timezone.utc).isoformat(),
                    "type": "order_block",
                    "zone_type": order_block["type"],  # bullish/bearish
                    "price_zone": order_block["price_zone"],
                    "strength": order_block["strength"],
                    "description": f"Order block identified: {order_block['type']} zone",
                    "confidence": order_block["confidence"]
                }
                smt_signals.append(signal)
            
        except Exception as e:
            logger.error(f"Error in market structure analysis: {e}")
        
        return smt_signals
    
    def process_narrative_signals(self) -> List[Dict[str, Any]]:
        """
        Process narrative and sentiment-based signals.
        
        Returns:
            List of narrative signals
        """
        narrative_signals = []
        current_time = get_timestamp()
        
        try:
            # Only update narrative signals periodically
            if current_time - self.last_narrative_update < self.config["narrative_interval"]:
                return narrative_signals
            
            self.last_narrative_update = current_time
            
            # Simulate news sentiment analysis
            import random
            sentiment_score = random.uniform(-1, 1)  # -1 bearish, +1 bullish
            
            # Generate narrative based on sentiment
            if abs(sentiment_score) > 0.6:  # Strong sentiment
                narrative_type = "bullish_news" if sentiment_score > 0 else "bearish_news"
                
                signal = {
                    "id": f"narrative_{int(time.time() * 1000)}",
                    "timestamp": current_time,
                    "datetime": datetime.now(timezone.utc).isoformat(),
                    "type": narrative_type,
                    "sentiment_score": round(sentiment_score, 2),
                    "strength": "strong" if abs(sentiment_score) > 0.8 else "moderate",
                    "source": "mock_sentiment_analysis",
                    "description": self._generate_narrative_description(sentiment_score),
                    "confidence": abs(sentiment_score)
                }
                
                narrative_signals.append(signal)
                self.narrative_signals.append(signal)
                
                logger.info(f"Narrative signal: {signal['description']}")
            
            # Simulate social media trends
            social_trend = self._simulate_social_trend()
            if social_trend:
                narrative_signals.append(social_trend)
                self.narrative_signals.append(social_trend)
            
        except Exception as e:
            logger.error(f"Error in narrative processing: {e}")
        
        return narrative_signals
    
    def _update_buffers(self, tick_data: Dict[str, Any], trade_events: List[Dict[str, Any]]) -> None:
        """Update internal data buffers."""
        if tick_data:
            self.price_buffer.append(tick_data)
            # Keep only last 100 price points
            if len(self.price_buffer) > 100:
                self.price_buffer.pop(0)
        
        self.trade_buffer.extend(trade_events)
        # Keep only last 200 trades
        if len(self.trade_buffer) > 200:
            self.trade_buffer = self.trade_buffer[-200:]
    
    def _classify_whale_trade(self, trade: Dict[str, Any]) -> str:
        """Classify the type of whale trade."""
        trade_value = trade.get("value", 0)
        
        if trade_value > 10_000_000:  # $10M+
            return "mega_whale"
        elif trade_value > 5_000_000:  # $5M+
            return "large_whale"
        else:
            return "whale"
    
    def _get_whale_severity(self, trade_value: float) -> str:
        """Get severity level for whale trade."""
        if trade_value > 10_000_000:
            return "critical"
        elif trade_value > 5_000_000:
            return "high"
        else:
            return "medium"
    
    def _estimate_market_impact(self, trade_value: float) -> str:
        """Estimate potential market impact of whale trade."""
        if trade_value > 20_000_000:
            return "very_high"
        elif trade_value > 10_000_000:
            return "high"
        elif trade_value > 5_000_000:
            return "medium"
        else:
            return "low"
    
    def _detect_structure_break(self, prices: List[float]) -> Optional[Dict[str, Any]]:
        """Detect market structure breaks."""
        if len(prices) < 20:
            return None
        
        # Simple structure break detection using price momentum
        recent_momentum = (prices[-1] - prices[-10]) / prices[-10]
        
        if abs(recent_momentum) > 0.03:  # 3% momentum
            direction = "bullish" if recent_momentum > 0 else "bearish"
            strength = min(abs(recent_momentum) * 10, 1.0)
            confidence = min(abs(recent_momentum) * 5, 0.9)
            
            return {
                "direction": direction,
                "strength": round(strength, 2),
                "confidence": round(confidence, 2)
            }
        
        return None
    
    def _detect_liquidity_grab(self, prices: List[float], volumes: List[float]) -> Optional[Dict[str, Any]]:
        """Detect liquidity grab patterns."""
        if len(prices) < 10 or len(volumes) < 10:
            return None
        
        # Check for sudden volume spike with price reversal
        current_volume = volumes[-1]
        avg_volume = np.mean(volumes[-10:-1])
        
        if current_volume > avg_volume * 2:  # Volume spike
            price_change = (prices[-1] - prices[-2]) / prices[-2]
            
            if abs(price_change) > 0.01:  # 1% price movement
                direction = "bullish" if price_change > 0 else "bearish"
                confidence = min(current_volume / avg_volume * 0.1, 0.8)
                
                return {
                    "direction": direction,
                    "confidence": round(confidence, 2)
                }
        
        return None
    
    def _detect_order_block(self, prices: List[float], volumes: List[float]) -> Optional[Dict[str, Any]]:
        """Detect order block formations."""
        if len(prices) < 15:
            return None
        
        # Simplified order block detection
        recent_high = max(prices[-10:])
        recent_low = min(prices[-10:])
        current_price = prices[-1]
        
        # Check if we're near a significant level
        high_distance = abs(current_price - recent_high) / recent_high
        low_distance = abs(current_price - recent_low) / recent_low
        
        if high_distance < 0.005:  # Near recent high
            return {
                "type": "bearish",
                "price_zone": (recent_high * 0.999, recent_high * 1.001),
                "strength": "strong",
                "confidence": 0.7
            }
        elif low_distance < 0.005:  # Near recent low
            return {
                "type": "bullish", 
                "price_zone": (recent_low * 0.999, recent_low * 1.001),
                "strength": "strong",
                "confidence": 0.7
            }
        
        return None
    
    def _generate_narrative_description(self, sentiment_score: float) -> str:
        """Generate narrative description based on sentiment."""
        if sentiment_score > 0.8:
            return "Extremely bullish market sentiment detected"
        elif sentiment_score > 0.6:
            return "Strong bullish sentiment in social media and news"
        elif sentiment_score < -0.8:
            return "Extremely bearish market sentiment detected"
        elif sentiment_score < -0.6:
            return "Strong bearish sentiment in social media and news"
        else:
            return "Neutral market sentiment"
    
    def _simulate_social_trend(self) -> Optional[Dict[str, Any]]:
        """Simulate social media trend detection."""
        import random
        if random.random() < 0.1:  # 10% chance of social trend
            trend_strength = random.uniform(0.5, 1.0)
            trend_type = random.choice(["viral_tweet", "reddit_trend", "telegram_signal"])
            
            return {
                "id": f"social_{int(time.time() * 1000)}",
                "timestamp": get_timestamp(),
                "datetime": datetime.now(timezone.utc).isoformat(),
                "type": trend_type,
                "strength": round(trend_strength, 2),
                "source": "social_media_analysis",
                "description": f"Social media trend detected: {trend_type}",
                "confidence": trend_strength * 0.6  # Lower confidence for social signals
            }
        
        return None
    
    def _empty_signals(self) -> Dict[str, Any]:
        """Return empty signals structure."""
        return {
            "timestamp": get_timestamp(),
            "spoofing": [],
            "whales": [],
            "market_structure": [],
            "narrative": [],
            "market_state": "neutral",
            "price": 0,
            "volume": 0
        }
    
    def get_recent_alerts(self, alert_type: str = "all", limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent alerts of specified type.
        
        Args:
            alert_type: Type of alerts to retrieve (spoofing, whales, smt, narrative, all)
            limit: Maximum number of alerts to return
        
        Returns:
            List of recent alerts
        """
        if alert_type == "spoofing":
            return self.spoofing_alerts[-limit:]
        elif alert_type == "whales":
            return self.whale_alerts[-limit:]
        elif alert_type == "smt":
            return self.smt_signals[-limit:]
        elif alert_type == "narrative":
            return self.narrative_signals[-limit:]
        else:
            # Return all alerts sorted by timestamp
            all_alerts = (
                self.spoofing_alerts + 
                self.whale_alerts + 
                self.smt_signals + 
                self.narrative_signals
            )
            return sorted(all_alerts, key=lambda x: x.get("timestamp", 0))[-limit:]


# Global signal processor instance
signal_processor = SignalProcessor()