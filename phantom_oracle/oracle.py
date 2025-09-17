"""
Phantom Oracle - AI/ML Analysis Engine for Phantom Detector.
Provides intelligent trend analysis and trade recommendations.
"""

import time
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple

# Try to import numpy, provide fallback if not available
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
                def uniform(low=0, high=1):
                    import random
                    return random.uniform(low, high)
            return MockRandom()
        @staticmethod
        def mean(values):
            return sum(values) / len(values) if values else 0
    np = MockNumpy()

from config.settings import config
from utils.logging_config import logger
from utils.helpers import get_timestamp, format_currency, format_percentage


class PhantomOracle:
    """
    AI-powered analysis engine that provides intelligent market insights,
    trend analysis, and trade recommendations based on processed signals.
    """
    
    def __init__(self):
        """Initialize the Phantom Oracle."""
        self.config = config.get_oracle_config()
        self.analysis_history: List[Dict[str, Any]] = []
        self.recommendations: List[Dict[str, Any]] = []
        self.last_recommendation_time = 0
        self.market_sentiment = "neutral"  # bullish, bearish, neutral
        self.confidence_score = 0.5
        
        # ML model state (simulated)
        self.model_version = "1.0.0-mock"
        self.training_samples = 0
        self.model_accuracy = 0.73  # Simulated accuracy
        
        logger.info("PhantomOracle initialized")
    
    def analyze_market_state(
        self,
        price_data: List[Dict[str, Any]],
        signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive market state analysis.
        
        Args:
            price_data: Recent price history
            signals: Current market signals
        
        Returns:
            Comprehensive market analysis
        """
        try:
            analysis = {
                "timestamp": get_timestamp(),
                "datetime": datetime.now(timezone.utc).isoformat(),
                "oracle_version": self.model_version,
                "market_sentiment": self._analyze_sentiment(signals),
                "trend_analysis": self._analyze_trends(price_data),
                "volatility_analysis": self._analyze_volatility(price_data),
                "momentum_analysis": self._analyze_momentum(price_data),
                "risk_assessment": self._assess_risk(signals),
                "manipulation_score": self._calculate_manipulation_score(signals),
                "whale_impact": self._analyze_whale_impact(signals),
                "confidence_score": self._calculate_confidence(signals),
                "key_insights": self._generate_insights(price_data, signals),
                "next_analysis": get_timestamp() + 300  # Next analysis in 5 minutes
            }
            
            self.analysis_history.append(analysis)
            
            # Keep only last 100 analyses
            if len(self.analysis_history) > 100:
                self.analysis_history.pop(0)
            
            logger.info(f"Market analysis completed - Sentiment: {analysis['market_sentiment']}, "
                       f"Confidence: {analysis['confidence_score']:.2f}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in market analysis: {e}")
            return self._empty_analysis()
    
    def summarize_trends(self, timeframe: str = "1h") -> str:
        """
        Generate a human-readable trend summary.
        
        Args:
            timeframe: Analysis timeframe (1h, 4h, 1d)
        
        Returns:
            Formatted trend summary
        """
        try:
            if not self.analysis_history:
                return "Insufficient data for trend analysis."
            
            latest_analysis = self.analysis_history[-1]
            sentiment = latest_analysis.get("market_sentiment", "neutral")
            confidence = latest_analysis.get("confidence_score", 0.5)
            trend = latest_analysis.get("trend_analysis", {})
            volatility = latest_analysis.get("volatility_analysis", {})
            
            # Generate dynamic summary based on current conditions
            summary_parts = []
            
            # Sentiment summary
            if sentiment == "bullish":
                summary_parts.append(f"🟢 Market shows BULLISH sentiment (confidence: {confidence:.1%})")
            elif sentiment == "bearish":
                summary_parts.append(f"🔴 Market shows BEARISH sentiment (confidence: {confidence:.1%})")
            else:
                summary_parts.append(f"🟡 Market sentiment is NEUTRAL (confidence: {confidence:.1%})")
            
            # Trend summary
            trend_direction = trend.get("direction", "sideways")
            trend_strength = trend.get("strength", 0.5)
            
            if trend_direction != "sideways":
                summary_parts.append(f"📈 {trend_direction.upper()} trend detected with {trend_strength:.1%} strength")
            else:
                summary_parts.append("📊 Market is consolidating in sideways movement")
            
            # Volatility summary
            vol_level = volatility.get("level", "normal")
            if vol_level == "high":
                summary_parts.append("⚡ HIGH volatility - Expect significant price swings")
            elif vol_level == "low":
                summary_parts.append("😴 LOW volatility - Market is relatively calm")
            else:
                summary_parts.append("🌊 NORMAL volatility levels")
            
            # Risk assessment
            risk_level = latest_analysis.get("risk_assessment", {}).get("level", "medium")
            summary_parts.append(f"⚠️  Current risk level: {risk_level.upper()}")
            
            # Key insights
            insights = latest_analysis.get("key_insights", [])
            if insights:
                summary_parts.append(f"💡 Key insight: {insights[0]}")
            
            return " | ".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error generating trend summary: {e}")
            return "Error generating trend analysis. Please try again."
    
    def recommend_trades(
        self,
        current_price: float,
        signals: Dict[str, Any],
        portfolio_balance: float = 10000.0
    ) -> List[Dict[str, Any]]:
        """
        Generate AI-powered trade recommendations.
        
        Args:
            current_price: Current market price
            signals: Current market signals
            portfolio_balance: Available portfolio balance
        
        Returns:
            List of trade recommendations
        """
        recommendations = []
        current_time = get_timestamp()
        
        try:
            # Check cooldown period
            if current_time - self.last_recommendation_time < self.config["recommendation_cooldown"]:
                logger.info("Recommendation cooldown active")
                return recommendations
            
            # Analyze current market conditions
            market_analysis = self._quick_market_analysis(signals)
            
            # Only generate recommendations if confidence is high enough
            if market_analysis["confidence"] < self.config["confidence_threshold"]:
                logger.info(f"Confidence too low for recommendations: {market_analysis['confidence']:.2f}")
                return recommendations
            
            # Generate recommendations based on market conditions
            if market_analysis["sentiment"] == "bullish":
                recommendations.extend(self._generate_bullish_recommendations(
                    current_price, portfolio_balance, market_analysis
                ))
            elif market_analysis["sentiment"] == "bearish":
                recommendations.extend(self._generate_bearish_recommendations(
                    current_price, portfolio_balance, market_analysis
                ))
            else:
                recommendations.extend(self._generate_neutral_recommendations(
                    current_price, portfolio_balance, market_analysis
                ))
            
            # Add recommendations to history
            for rec in recommendations:
                self.recommendations.append(rec)
            
            # Keep only last 50 recommendations
            if len(self.recommendations) > 50:
                self.recommendations = self.recommendations[-50:]
            
            self.last_recommendation_time = current_time
            
            if recommendations:
                logger.info(f"Generated {len(recommendations)} trade recommendations")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating trade recommendations: {e}")
            return []
    
    def evaluate_trade_performance(self, executed_trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate the performance of executed trades against recommendations.
        
        Args:
            executed_trades: List of executed trades
        
        Returns:
            Performance evaluation metrics
        """
        try:
            if not executed_trades or not self.recommendations:
                return {"status": "insufficient_data"}
            
            # Simulate performance analysis
            total_trades = len(executed_trades)
            profitable_trades = sum(1 for trade in executed_trades 
                                  if trade.get("profit_loss", 0) > 0)
            
            win_rate = profitable_trades / total_trades if total_trades > 0 else 0
            total_pnl = sum(trade.get("profit_loss", 0) for trade in executed_trades)
            avg_trade_pnl = total_pnl / total_trades if total_trades > 0 else 0
            
            # Calculate recommendation accuracy (simulated)
            recommendation_accuracy = min(0.95, self.model_accuracy + random.uniform(-0.1, 0.1))
            
            performance = {
                "timestamp": get_timestamp(),
                "datetime": datetime.now(timezone.utc).isoformat(),
                "evaluation_period": "1d",  # 1 day evaluation
                "total_trades": total_trades,
                "profitable_trades": profitable_trades,
                "losing_trades": total_trades - profitable_trades,
                "win_rate": round(win_rate * 100, 1),
                "total_pnl": round(total_pnl, 2),
                "average_trade_pnl": round(avg_trade_pnl, 2),
                "recommendation_accuracy": round(recommendation_accuracy * 100, 1),
                "oracle_performance": "good" if win_rate > 0.6 else "needs_improvement",
                "suggestions": self._generate_performance_suggestions(win_rate, total_pnl)
            }
            
            logger.info(f"Trade performance evaluated: {win_rate:.1%} win rate, "
                       f"${total_pnl:.2f} total PnL")
            
            return performance
            
        except Exception as e:
            logger.error(f"Error evaluating trade performance: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_market_forecast(self, timeframe: str = "24h") -> Dict[str, Any]:
        """
        Generate market forecast using AI models.
        
        Args:
            timeframe: Forecast timeframe (1h, 4h, 24h, 1w)
        
        Returns:
            Market forecast with price targets and probabilities
        """
        try:
            current_time = get_timestamp()
            
            # Simulate AI model prediction
            base_price = 50000  # Base BTC price for simulation
            
            # Generate price forecast based on timeframe
            if timeframe == "1h":
                price_change_range = (-0.02, 0.02)  # ±2%
                confidence_base = 0.75
            elif timeframe == "4h":
                price_change_range = (-0.05, 0.05)  # ±5%
                confidence_base = 0.65
            elif timeframe == "24h":
                price_change_range = (-0.10, 0.10)  # ±10%
                confidence_base = 0.55
            else:  # 1w
                price_change_range = (-0.20, 0.20)  # ±20%
                confidence_base = 0.45
            
            # Generate forecast scenarios
            price_change = random.uniform(*price_change_range)
            target_price = base_price * (1 + price_change)
            
            # Generate multiple scenarios
            scenarios = [
                {
                    "scenario": "bullish",
                    "probability": 0.3 + random.uniform(-0.1, 0.1),
                    "price_target": target_price * random.uniform(1.02, 1.08),
                    "description": "Strong upward momentum with institutional buying"
                },
                {
                    "scenario": "neutral",
                    "probability": 0.4 + random.uniform(-0.1, 0.1),
                    "price_target": target_price * random.uniform(0.98, 1.02),
                    "description": "Sideways movement with consolidation"
                },
                {
                    "scenario": "bearish",
                    "probability": 0.3 + random.uniform(-0.1, 0.1),
                    "price_target": target_price * random.uniform(0.92, 0.98),
                    "description": "Downward pressure from profit-taking"
                }
            ]
            
            # Normalize probabilities
            total_prob = sum(s["probability"] for s in scenarios)
            for scenario in scenarios:
                scenario["probability"] = scenario["probability"] / total_prob
            
            forecast = {
                "timestamp": current_time,
                "datetime": datetime.now(timezone.utc).isoformat(),
                "timeframe": timeframe,
                "model_version": self.model_version,
                "base_price": base_price,
                "primary_target": round(target_price, 2),
                "confidence": confidence_base + random.uniform(-0.1, 0.1),
                "scenarios": scenarios,
                "key_factors": [
                    "Market structure analysis",
                    "Whale movement patterns",
                    "Social sentiment trends",
                    "Technical indicator confluence"
                ],
                "risk_factors": [
                    "High volatility environment",
                    "Regulatory uncertainty",
                    "Macro economic factors"
                ],
                "next_update": current_time + 3600  # Next update in 1 hour
            }
            
            logger.info(f"Market forecast generated for {timeframe}: "
                       f"${target_price:.0f} target with {forecast['confidence']:.1%} confidence")
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error generating market forecast: {e}")
            return {"status": "error", "message": str(e)}
    
    def _analyze_sentiment(self, signals: Dict[str, Any]) -> str:
        """Analyze overall market sentiment from signals."""
        bullish_factors = 0
        bearish_factors = 0
        
        # Analyze spoofing signals
        spoofing_alerts = signals.get("spoofing", [])
        if spoofing_alerts:
            bearish_factors += len(spoofing_alerts)
        
        # Analyze whale signals
        whale_alerts = signals.get("whales", [])
        for whale in whale_alerts:
            if whale.get("side") == "buy":
                bullish_factors += 1
            else:
                bearish_factors += 1
        
        # Analyze market structure
        smt_signals = signals.get("market_structure", [])
        for signal in smt_signals:
            if signal.get("type") == "structure_break":
                if signal.get("direction") == "bullish":
                    bullish_factors += 2
                else:
                    bearish_factors += 2
        
        # Analyze narrative signals
        narrative_signals = signals.get("narrative", [])
        for signal in narrative_signals:
            sentiment_score = signal.get("sentiment_score", 0)
            if sentiment_score > 0.5:
                bullish_factors += 1
            elif sentiment_score < -0.5:
                bearish_factors += 1
        
        # Determine overall sentiment
        if bullish_factors > bearish_factors * 1.2:
            return "bullish"
        elif bearish_factors > bullish_factors * 1.2:
            return "bearish"
        else:
            return "neutral"
    
    def _analyze_trends(self, price_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze price trends."""
        if len(price_data) < 10:
            return {"direction": "sideways", "strength": 0.5}
        
        prices = [item.get("price", 0) for item in price_data[-20:]]
        
        # Calculate trend using linear regression simulation
        recent_change = (prices[-1] - prices[0]) / prices[0]
        
        if recent_change > 0.02:
            direction = "bullish"
        elif recent_change < -0.02:
            direction = "bearish"
        else:
            direction = "sideways"
        
        strength = min(abs(recent_change) * 10, 1.0)
        
        return {
            "direction": direction,
            "strength": round(strength, 2),
            "price_change": round(recent_change * 100, 2)
        }
    
    def _analyze_volatility(self, price_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze market volatility."""
        if len(price_data) < 10:
            return {"level": "normal", "value": 0.02}
        
        prices = [item.get("price", 0) for item in price_data[-20:]]
        
        # Calculate price volatility
        price_changes = [abs(prices[i] - prices[i-1]) / prices[i-1] 
                        for i in range(1, len(prices))]
        avg_volatility = np.mean(price_changes)
        
        if avg_volatility > 0.03:
            level = "high"
        elif avg_volatility < 0.01:
            level = "low"
        else:
            level = "normal"
        
        return {
            "level": level,
            "value": round(avg_volatility, 4),
            "percentile": round(avg_volatility * 100, 2)
        }
    
    def _analyze_momentum(self, price_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze price momentum."""
        if len(price_data) < 15:
            return {"strength": "weak", "direction": "neutral"}
        
        prices = [item.get("price", 0) for item in price_data[-15:]]
        
        # Simple momentum calculation
        short_term = np.mean(prices[-5:])
        long_term = np.mean(prices[-15:-5])
        
        momentum = (short_term - long_term) / long_term
        
        if momentum > 0.01:
            direction = "bullish"
            strength = "strong" if momentum > 0.03 else "moderate"
        elif momentum < -0.01:
            direction = "bearish"
            strength = "strong" if momentum < -0.03 else "moderate"
        else:
            direction = "neutral"
            strength = "weak"
        
        return {
            "strength": strength,
            "direction": direction,
            "value": round(momentum * 100, 2)
        }
    
    def _assess_risk(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Assess current market risk."""
        risk_score = 0.5  # Base risk
        
        # Increase risk for spoofing activity
        spoofing_count = len(signals.get("spoofing", []))
        risk_score += spoofing_count * 0.1
        
        # Increase risk for whale activity
        whale_count = len(signals.get("whales", []))
        risk_score += whale_count * 0.05
        
        # Clamp risk score
        risk_score = min(risk_score, 1.0)
        
        if risk_score > 0.7:
            level = "high"
        elif risk_score > 0.4:
            level = "medium"
        else:
            level = "low"
        
        return {
            "level": level,
            "score": round(risk_score, 2),
            "factors": self._identify_risk_factors(signals)
        }
    
    def _calculate_manipulation_score(self, signals: Dict[str, Any]) -> float:
        """Calculate market manipulation probability score."""
        manipulation_score = 0.0
        
        # Spoofing signals increase manipulation score
        spoofing_alerts = signals.get("spoofing", [])
        manipulation_score += len(spoofing_alerts) * 0.3
        
        # High whale activity might indicate manipulation
        whale_alerts = signals.get("whales", [])
        if len(whale_alerts) > 3:
            manipulation_score += 0.2
        
        return min(manipulation_score, 1.0)
    
    def _analyze_whale_impact(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze whale impact on market."""
        whale_alerts = signals.get("whales", [])
        
        if not whale_alerts:
            return {"impact": "minimal", "direction": "neutral"}
        
        total_value = sum(whale.get("value", 0) for whale in whale_alerts)
        buy_value = sum(whale.get("value", 0) for whale in whale_alerts 
                       if whale.get("side") == "buy")
        sell_value = total_value - buy_value
        
        if buy_value > sell_value * 1.5:
            direction = "bullish"
        elif sell_value > buy_value * 1.5:
            direction = "bearish"
        else:
            direction = "neutral"
        
        if total_value > 50_000_000:  # $50M+
            impact = "high"
        elif total_value > 10_000_000:  # $10M+
            impact = "medium"
        else:
            impact = "low"
        
        return {
            "impact": impact,
            "direction": direction,
            "total_value": total_value,
            "buy_sell_ratio": round(buy_value / max(sell_value, 1), 2)
        }
    
    def _calculate_confidence(self, signals: Dict[str, Any]) -> float:
        """Calculate overall analysis confidence."""
        base_confidence = 0.6
        
        # More signals = higher confidence
        total_signals = (
            len(signals.get("spoofing", [])) +
            len(signals.get("whales", [])) +
            len(signals.get("market_structure", [])) +
            len(signals.get("narrative", []))
        )
        
        signal_boost = min(total_signals * 0.05, 0.3)
        
        return min(base_confidence + signal_boost, 0.95)
    
    def _generate_insights(
        self,
        price_data: List[Dict[str, Any]],
        signals: Dict[str, Any]
    ) -> List[str]:
        """Generate key market insights."""
        insights = []
        
        # Price-based insights
        if price_data:
            current_price = price_data[-1].get("price", 0)
            if len(price_data) > 1:
                price_change = (current_price - price_data[-2].get("price", 0)) / price_data[-2].get("price", 1)
                if abs(price_change) > 0.02:
                    insights.append(f"Significant price movement: {price_change*100:.1f}%")
        
        # Signal-based insights
        spoofing_count = len(signals.get("spoofing", []))
        if spoofing_count > 0:
            insights.append(f"Market manipulation detected: {spoofing_count} spoofing alerts")
        
        whale_count = len(signals.get("whales", []))
        if whale_count > 2:
            insights.append(f"High whale activity: {whale_count} large transactions detected")
        
        # Add random market insights
        random_insights = [
            "Technical indicators showing divergence",
            "Social sentiment aligning with price action",
            "Market structure suggests potential reversal",
            "Volume profile indicates strong support/resistance",
            "Institutional flow patterns detected"
        ]
        
        if len(insights) < 3:
            insights.extend(random.sample(random_insights, 3 - len(insights)))
        
        return insights[:3]  # Return top 3 insights
    
    def _quick_market_analysis(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Quick market analysis for recommendations."""
        return {
            "sentiment": self._analyze_sentiment(signals),
            "confidence": self._calculate_confidence(signals),
            "manipulation_risk": self._calculate_manipulation_score(signals),
            "whale_direction": self._analyze_whale_impact(signals).get("direction", "neutral")
        }
    
    def _generate_bullish_recommendations(
        self,
        current_price: float,
        balance: float,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate bullish trade recommendations."""
        recommendations = []
        
        # Long position recommendation
        position_size = min(balance * 0.1, 5000)  # Max $5k position
        
        rec = {
            "id": f"rec_{int(time.time() * 1000)}",
            "timestamp": get_timestamp(),
            "datetime": datetime.now(timezone.utc).isoformat(),
            "type": "long",
            "action": "buy",
            "asset": "BTCUSD",
            "entry_price": current_price,
            "position_size": position_size,
            "quantity": position_size / current_price,
            "stop_loss": current_price * 0.95,  # 5% stop loss
            "take_profit": current_price * 1.08,  # 8% take profit
            "confidence": analysis["confidence"],
            "risk_level": "medium",
            "reasoning": "Bullish market sentiment with strong momentum indicators",
            "expected_return": "5-8%",
            "time_horizon": "1-3 days",
            "oracle_score": random.uniform(0.7, 0.9)
        }
        
        recommendations.append(rec)
        return recommendations
    
    def _generate_bearish_recommendations(
        self,
        current_price: float,
        balance: float,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate bearish trade recommendations."""
        recommendations = []
        
        # Short position recommendation (simulated)
        position_size = min(balance * 0.08, 3000)  # Smaller position for shorts
        
        rec = {
            "id": f"rec_{int(time.time() * 1000)}",
            "timestamp": get_timestamp(),
            "datetime": datetime.now(timezone.utc).isoformat(),
            "type": "short",
            "action": "sell",
            "asset": "BTCUSD",
            "entry_price": current_price,
            "position_size": position_size,
            "quantity": position_size / current_price,
            "stop_loss": current_price * 1.05,  # 5% stop loss
            "take_profit": current_price * 0.92,  # 8% take profit
            "confidence": analysis["confidence"],
            "risk_level": "high",
            "reasoning": "Bearish sentiment with potential downward pressure",
            "expected_return": "5-8%",
            "time_horizon": "1-2 days",
            "oracle_score": random.uniform(0.6, 0.8)
        }
        
        recommendations.append(rec)
        return recommendations
    
    def _generate_neutral_recommendations(
        self,
        current_price: float,
        balance: float,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate neutral market recommendations."""
        recommendations = []
        
        # Range trading recommendation
        position_size = min(balance * 0.05, 2000)  # Conservative position
        
        rec = {
            "id": f"rec_{int(time.time() * 1000)}",
            "timestamp": get_timestamp(),
            "datetime": datetime.now(timezone.utc).isoformat(),
            "type": "range",
            "action": "wait",
            "asset": "BTCUSD",
            "entry_price": current_price,
            "position_size": position_size,
            "confidence": analysis["confidence"],
            "risk_level": "low",
            "reasoning": "Neutral market conditions suggest range-bound trading",
            "recommendation": "Wait for clearer directional signals",
            "support_level": current_price * 0.97,
            "resistance_level": current_price * 1.03,
            "oracle_score": random.uniform(0.5, 0.7)
        }
        
        recommendations.append(rec)
        return recommendations
    
    def _generate_performance_suggestions(self, win_rate: float, total_pnl: float) -> List[str]:
        """Generate performance improvement suggestions."""
        suggestions = []
        
        if win_rate < 0.5:
            suggestions.append("Consider tightening risk management parameters")
            suggestions.append("Review entry criteria for trade recommendations")
        
        if total_pnl < 0:
            suggestions.append("Reduce position sizes until performance improves")
            suggestions.append("Focus on higher confidence signals only")
        
        if win_rate > 0.7:
            suggestions.append("Consider increasing position sizes gradually")
            suggestions.append("Excellent performance - maintain current strategy")
        
        return suggestions
    
    def _identify_risk_factors(self, signals: Dict[str, Any]) -> List[str]:
        """Identify current market risk factors."""
        factors = []
        
        if signals.get("spoofing"):
            factors.append("Market manipulation detected")
        
        if len(signals.get("whales", [])) > 3:
            factors.append("High whale activity")
        
        if signals.get("market_state") == "volatile":
            factors.append("Increased volatility")
        
        # Add some standard risk factors
        standard_factors = [
            "Regulatory uncertainty",
            "Macro economic factors",
            "Technical resistance levels"
        ]
        
        factors.extend(random.sample(standard_factors, 2))
        
        return factors[:5]  # Return top 5 factors
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure."""
        return {
            "timestamp": get_timestamp(),
            "status": "error",
            "market_sentiment": "unknown",
            "confidence_score": 0.0
        }
    
    def get_oracle_status(self) -> Dict[str, Any]:
        """Get current oracle status and performance metrics."""
        return {
            "timestamp": get_timestamp(),
            "oracle_version": self.model_version,
            "status": "active",
            "model_accuracy": self.model_accuracy,
            "training_samples": self.training_samples,
            "total_analyses": len(self.analysis_history),
            "total_recommendations": len(self.recommendations),
            "last_analysis": self.analysis_history[-1]["timestamp"] if self.analysis_history else None,
            "last_recommendation": self.last_recommendation_time,
            "next_recommendation_available": self.last_recommendation_time + self.config["recommendation_cooldown"]
        }


# Global oracle instance
phantom_oracle = PhantomOracle()