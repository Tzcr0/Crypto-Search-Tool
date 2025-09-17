"""
Main entry point for Phantom Detector.
Initializes and runs the complete trading intelligence platform.
"""

import asyncio
import signal
import sys
import threading
import time
from typing import NoReturn

from config.settings import config
from utils.logging_config import logger, setup_logging
from data_ingestion.mock_data import mock_generator
from signal_processing.algorithms import signal_processor
from phantom_oracle.oracle import phantom_oracle
from dashboard_ui.app import phantom_dashboard


class PhantomDetectorApp:
    """
    Main application class for Phantom Detector.
    Orchestrates all components of the trading intelligence platform.
    """
    
    def __init__(self):
        """Initialize the Phantom Detector application."""
        self.is_running = False
        self.data_thread: threading.Thread = None
        self.loop: asyncio.AbstractEventLoop = None
        
        # Setup logging
        self.logger = setup_logging("PhantomDetector")
        
        self.logger.info("=" * 60)
        self.logger.info("🔮 PHANTOM DETECTOR - Trading Intelligence Platform")
        self.logger.info(f"Version: {config.VERSION}")
        self.logger.info(f"Mode: {'DEBUG' if config.DEBUG else 'PRODUCTION'}")
        self.logger.info("=" * 60)
    
    def start(self) -> None:
        """Start the complete Phantom Detector system."""
        try:
            self.logger.info("Starting Phantom Detector system...")
            
            # Validate configuration
            self._validate_config()
            
            # Setup signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            # Start data ingestion in background thread
            self._start_data_ingestion()
            
            # Wait a moment for data to start flowing
            time.sleep(2)
            
            # Start the dashboard (blocking call)
            self.logger.info("Starting web dashboard...")
            phantom_dashboard.run(
                host=config.DASH_HOST,
                port=config.DASH_PORT,
                debug=config.DASH_DEBUG
            )
            
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
            self.shutdown()
        except Exception as e:
            self.logger.error(f"Fatal error starting application: {e}")
            self.shutdown()
            sys.exit(1)
    
    def _validate_config(self) -> None:
        """Validate application configuration."""
        self.logger.info("Validating configuration...")
        
        # Check required settings
        required_settings = ['DASH_HOST', 'DASH_PORT', 'APP_NAME']
        for setting in required_settings:
            if not hasattr(config, setting):
                raise ValueError(f"Missing required configuration: {setting}")
        
        # Log configuration
        self.logger.info(f"Dashboard will run on: http://{config.DASH_HOST}:{config.DASH_PORT}")
        self.logger.info(f"Mock data enabled: {config.MOCK_DATA_ENABLED}")
        self.logger.info(f"Price update interval: {config.PRICE_UPDATE_INTERVAL}s")
        self.logger.info(f"Log level: {config.LOG_LEVEL}")
        
        self.logger.info("✅ Configuration validated successfully")
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}")
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        if hasattr(signal, 'SIGBREAK'):  # Windows
            signal.signal(signal.SIGBREAK, signal_handler)
    
    def _start_data_ingestion(self) -> None:
        """Start the data ingestion system in a background thread."""
        self.logger.info("Starting data ingestion system...")
        
        def run_async_data():
            """Run the async data ingestion loop."""
            try:
                # Create new event loop for this thread
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
                
                # Start the mock data generator
                self.loop.run_until_complete(mock_generator.start_price_stream())
                
            except Exception as e:
                self.logger.error(f"Error in data ingestion thread: {e}")
            finally:
                if self.loop:
                    self.loop.close()
        
        self.data_thread = threading.Thread(target=run_async_data, daemon=True)
        self.data_thread.start()
        self.is_running = True
        
        self.logger.info("✅ Data ingestion system started")
    
    def shutdown(self) -> None:
        """Shutdown the Phantom Detector system gracefully."""
        if not self.is_running:
            return
        
        self.logger.info("Shutting down Phantom Detector system...")
        
        try:
            # Stop data ingestion
            if mock_generator.is_running:
                mock_generator.stop_stream()
                self.logger.info("✅ Data ingestion stopped")
            
            # Stop event loop
            if self.loop and not self.loop.is_closed():
                self.loop.call_soon_threadsafe(self.loop.stop)
            
            # Wait for data thread to finish
            if self.data_thread and self.data_thread.is_alive():
                self.data_thread.join(timeout=5)
                
            self.is_running = False
            self.logger.info("✅ Phantom Detector shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def get_system_status(self) -> dict:
        """Get the current system status."""
        return {
            "app_running": self.is_running,
            "data_ingestion_running": mock_generator.is_running,
            "current_price": mock_generator.get_current_price(),
            "total_subscribers": len(mock_generator.subscribers),
            "config": {
                "version": config.VERSION,
                "debug": config.DEBUG,
                "mock_data": config.MOCK_DATA_ENABLED,
                "dashboard_url": f"http://{config.DASH_HOST}:{config.DASH_PORT}"
            }
        }


def print_startup_banner() -> None:
    """Print the application startup banner."""
    banner = f"""
    
    ╔══════════════════════════════════════════════════════╗
    ║                                                      ║
    ║              🔮 PHANTOM DETECTOR 🔮                  ║
    ║                                                      ║
    ║        Next-Gen Trading Intelligence Platform        ║
    ║                                                      ║
    ║  📈 Real-time Market Analysis                        ║
    ║  🚨 Spoofing & Manipulation Detection               ║
    ║  🐋 Whale Movement Tracking                         ║
    ║  🧠 AI-Powered Trade Recommendations                ║
    ║  📊 Smart Money Theory Analysis                      ║
    ║                                                      ║
    ║  Version: {config.VERSION:<8} | Mode: {'DEBUG' if config.DEBUG else 'PROD':<12}    ║
    ║                                                      ║
    ╚══════════════════════════════════════════════════════╝
    
    🌐 Dashboard: http://{config.DASH_HOST}:{config.DASH_PORT}
    📊 Status: Mock Data Mode (No Live APIs)
    🔧 Ready for Development & Testing
    
    ⚠️  DISCLAIMER: For educational purposes only. 
       Not financial advice. Trade responsibly.
    
    """
    print(banner)


def main() -> NoReturn:
    """Main entry point."""
    # Print startup banner
    print_startup_banner()
    
    # Create and start the application
    app = PhantomDetectorApp()
    
    try:
        # Start the system
        app.start()
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Thanks for using Phantom Detector!")
    except Exception as e:
        logger.error(f"Application crashed: {e}")
        sys.exit(1)
    finally:
        app.shutdown()


if __name__ == "__main__":
    main()