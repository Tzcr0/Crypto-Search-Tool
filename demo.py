#!/usr/bin/env python3
"""
Demo script for Phantom Detector - shows core functionality without full dashboard.
This script demonstrates the trading intelligence platform capabilities using mock data.
"""

import time
import asyncio
from datetime import datetime

from config.settings import config
from utils.logging_config import logger, setup_logging
from data_ingestion.mock_data import mock_generator
from signal_processing.algorithms import signal_processor
from phantom_oracle.oracle import phantom_oracle


def print_banner():
    """Print demo banner."""
    print("\n" + "="*70)
    print("🔮 PHANTOM DETECTOR - DEMO MODE")
    print("Next-Gen Trading Intelligence Platform")
    print("="*70)
    print(f"📅 Demo Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💻 Version: {config.VERSION}")
    print(f"📊 Mode: Mock Data Simulation")
    print("="*70 + "\n")


def demonstrate_data_generation():
    """Demonstrate mock data generation capabilities."""
    print("🔄 DEMONSTRATING DATA GENERATION")
    print("-" * 40)
    
    # Show current price
    current_price = mock_generator.get_current_price()
    print(f"💰 Current BTC Price: ${current_price:,.2f}")
    
    # Generate historical data
    print("📈 Generating historical OHLCV data...")
    historical = mock_generator.generate_historical_ohlcv(days=1, interval="1h")
    print(f"✅ Generated {len(historical)} hourly candles")
    
    # Show sample candle
    if historical:
        sample = historical[-1]
        print(f"📊 Latest Candle: O: ${sample['open']:.2f} | H: ${sample['high']:.2f} | L: ${sample['low']:.2f} | C: ${sample['close']:.2f}")
    
    # Generate mock tick data
    print("🎲 Generating mock market tick...")
    tick_data = mock_generator._generate_price_tick()
    print(f"📈 Price: ${tick_data['price']:.2f} | Volume: {tick_data['volume']:.2f} | Change: {tick_data['price_change_pct']:.2f}%")
    
    # Generate trade events
    trades = [mock_generator._generate_trade_event() for _ in range(3)]
    print(f"💱 Generated {len(trades)} trade events")
    for i, trade in enumerate(trades, 1):
        side_emoji = "🟢" if trade['side'] == 'buy' else "🔴"
        whale_indicator = " 🐋" if trade.get('is_whale') else ""
        print(f"  {i}. {side_emoji} {trade['side'].upper()} {trade['size']:.4f} BTC @ ${trade['price']:.2f}{whale_indicator}")
    
    print()


def demonstrate_signal_processing():
    """Demonstrate signal processing capabilities."""
    print("🚨 DEMONSTRATING SIGNAL PROCESSING")
    print("-" * 40)
    
    # Create mock market data
    tick_data = mock_generator._generate_price_tick()
    trade_events = [mock_generator._generate_trade_event() for _ in range(5)]
    
    # Add some whale and suspicious trades for demo
    whale_trade = {
        **mock_generator._generate_trade_event(),
        'size': 150.0,  # Large trade
        'value': 150.0 * tick_data['price'],
        'is_whale': True
    }
    
    suspicious_trade = {
        **mock_generator._generate_trade_event(),
        'size': 500.0,
        'is_suspicious': True,
        'value': 500.0 * tick_data['price']
    }
    
    trade_events.extend([whale_trade, suspicious_trade])
    
    market_data = {
        "type": "market_update",
        "tick": tick_data,
        "trades": trade_events,
        "timestamp": time.time()
    }
    
    # Process signals
    print("🔍 Processing market signals...")
    signals = signal_processor.process_market_data(market_data)
    
    # Display results
    print(f"🎯 Market State: {signals['market_state']}")
    print(f"📊 Current Price: ${signals['price']:.2f}")
    print(f"📈 Volume: {signals['volume']:.2f}")
    
    # Show spoofing alerts
    spoofing_alerts = signals['spoofing']
    if spoofing_alerts:
        print(f"⚠️  Spoofing Alerts: {len(spoofing_alerts)}")
        for alert in spoofing_alerts:
            print(f"   • {alert['description']} (Confidence: {alert['confidence']:.1%})")
    else:
        print("✅ No spoofing detected")
    
    # Show whale alerts
    whale_alerts = signals['whales']
    if whale_alerts:
        print(f"🐋 Whale Alerts: {len(whale_alerts)}")
        for alert in whale_alerts:
            print(f"   • {alert['description']} (Impact: {alert['market_impact']})")
    else:
        print("📊 No whale activity detected")
    
    # Show market structure signals
    smt_signals = signals['market_structure']
    if smt_signals:
        print(f"📈 Market Structure Signals: {len(smt_signals)}")
        for signal in smt_signals:
            print(f"   • {signal['type']}: {signal['description']}")
    else:
        print("📊 No significant market structure changes")
    
    print()


def demonstrate_oracle_analysis():
    """Demonstrate Oracle AI analysis capabilities."""
    print("🔮 DEMONSTRATING ORACLE ANALYSIS")
    print("-" * 40)
    
    # Get Oracle status
    status = phantom_oracle.get_oracle_status()
    print(f"🤖 Oracle Status: {status['status']}")
    print(f"📊 Model Version: {status['oracle_version']}")
    print(f"🎯 Model Accuracy: {status['model_accuracy']:.1%}")
    
    # Generate trend summary
    print("\n📈 TREND ANALYSIS:")
    summary = phantom_oracle.summarize_trends("1h")
    print(f"   {summary}")
    
    # Generate market forecast
    print("\n🔮 MARKET FORECAST:")
    forecast = phantom_oracle.get_market_forecast("24h")
    if 'primary_target' in forecast:
        print(f"   📊 24h Target: ${forecast['primary_target']:,.0f}")
        print(f"   🎯 Confidence: {forecast['confidence']:.1%}")
        
        # Show scenarios
        scenarios = forecast.get('scenarios', [])
        for scenario in scenarios:
            emoji = "🟢" if scenario['scenario'] == 'bullish' else "🔴" if scenario['scenario'] == 'bearish' else "⚪"
            print(f"   {emoji} {scenario['scenario'].title()}: {scenario['probability']:.1%} - ${scenario['price_target']:,.0f}")
    
    # Generate trade recommendations
    print("\n💡 TRADE RECOMMENDATIONS:")
    mock_signals = {'spoofing': [], 'whales': [], 'market_structure': [], 'narrative': []}
    current_price = mock_generator.get_current_price()
    recommendations = phantom_oracle.recommend_trades(current_price, mock_signals, 10000)
    
    if recommendations:
        for rec in recommendations:
            action_emoji = "🟢" if rec['action'] == 'buy' else "🔴" if rec['action'] == 'sell' else "⏸️"
            print(f"   {action_emoji} {rec['action'].upper()} {rec.get('asset', 'BTCUSD')}")
            print(f"      💰 Entry: ${rec.get('entry_price', 0):,.2f}")
            print(f"      🎯 Confidence: {rec.get('confidence', 0):.1%}")
            print(f"      📝 Reason: {rec.get('reasoning', 'N/A')}")
    else:
        print("   ⏳ No recommendations at this time (waiting for clearer signals)")
    
    print()


def demonstrate_integration():
    """Demonstrate how all components work together."""
    print("🔗 DEMONSTRATING SYSTEM INTEGRATION")
    print("-" * 40)
    
    print("🔄 Simulating real-time data flow...")
    
    # Simulate 5 market updates
    for i in range(5):
        print(f"\n📊 Market Update #{i+1}")
        
        # Generate market data
        tick_data = mock_generator._generate_price_tick()
        trade_events = [mock_generator._generate_trade_event() for _ in range(3)]
        
        market_data = {
            "tick": tick_data,
            "trades": trade_events
        }
        
        # Process through signal processor
        signals = signal_processor.process_market_data(market_data)
        
        # Show key metrics
        price = signals['price']
        change = tick_data.get('price_change_pct', 0)
        change_emoji = "📈" if change >= 0 else "📉"
        
        print(f"   {change_emoji} Price: ${price:.2f} ({change:+.2f}%)")
        
        # Check for alerts
        total_alerts = (len(signals['spoofing']) + 
                       len(signals['whales']) + 
                       len(signals['market_structure']) + 
                       len(signals['narrative']))
        
        if total_alerts > 0:
            print(f"   🚨 Alerts: {total_alerts} new signals detected")
        else:
            print("   ✅ No alerts")
        
        # Brief pause to simulate real-time
        time.sleep(0.5)
    
    print("\n✅ Integration demonstration complete!")
    print()


def main():
    """Run the complete demonstration."""
    # Setup logging
    logger = setup_logging("PhantomDetectorDemo")
    
    try:
        print_banner()
        
        print("🎯 PHANTOM DETECTOR CAPABILITIES DEMONSTRATION")
        print("This demo showcases all core features using mock data simulation.\n")
        
        # Run demonstrations
        demonstrate_data_generation()
        input("Press Enter to continue to Signal Processing demo...")
        
        demonstrate_signal_processing()
        input("Press Enter to continue to Oracle Analysis demo...")
        
        demonstrate_oracle_analysis()
        input("Press Enter to continue to System Integration demo...")
        
        demonstrate_integration()
        
        # Final summary
        print("🎉 DEMONSTRATION COMPLETE!")
        print("-" * 40)
        print("✅ All core components successfully demonstrated:")
        print("   📊 Mock Data Generation")
        print("   🚨 Signal Processing & Alert Systems")
        print("   🐋 Whale Tracking")
        print("   🔮 AI Oracle Analysis & Recommendations")
        print("   🔗 Real-time System Integration")
        print()
        print("🚀 Ready for dashboard deployment!")
        print(f"   Run: python main.py")
        print(f"   Then visit: http://{config.DASH_HOST}:{config.DASH_PORT}")
        print()
        print("⚠️  Remember: This is MOCK DATA for development/demo purposes only.")
        print("   Real trading requires integration with live exchange APIs.")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user. Goodbye!")
    except Exception as e:
        logger.error(f"Demo error: {e}")
        print(f"\n❌ Demo error: {e}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()