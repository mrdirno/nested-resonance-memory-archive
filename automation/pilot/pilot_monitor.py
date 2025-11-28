"""
Cycle 2451: Pilot Monitor (Gate 79)
Role: The Pilot Monitor
Responsibility: Monitor Pilot Health on macOS.

Phase 61 (Digital Terraforming) Standards:
- Structured Logging
- Type Safety
- Robust Error Handling
"""

import sys
import platform
import time
import os
import logging
import signal
from typing import NoReturn

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("PILOT_MONITOR")

class PilotMonitor:
    """
    Monitors the health and status of the Pilot Node (macOS).
    
    Attributes:
        interval (int): Heartbeat interval in seconds.
        running (bool): Control flag for the main loop.
    """

    def __init__(self, interval: int = 3600):
        """
        Initialize the Pilot Monitor.

        Args:
            interval (int): Time in seconds between heartbeats. Default 3600.
        """
        self.interval = interval
        self.running = True
        self._setup_signal_handlers()

    def _setup_signal_handlers(self) -> None:
        """Register signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def check_identity(self) -> None:
        """
        Verify that the script is running on the correct node (macOS).
        
        Raises:
            SystemExit: If running on a non-Darwin system.
        """
        system = platform.system()
        if system != "Darwin":
            logger.critical(f"⛔ IDENTITY MISMATCH: Pilot Monitor must run on macOS. Detected: {system}")
            sys.exit(1)
        logger.info(f"✅ IDENTITY VERIFIED: Host is {system} (Pilot Node).")

    def heartbeat(self) -> None:
        """Perform a single heartbeat check."""
        logger.info("💓 HEARTBEAT: System Nominal.")
        # Future: Check for incoming messages from Guardian or MOG directives.

    def shutdown(self, signum, frame) -> None:
        """Handle shutdown signals."""
        logger.info("🛑 SHUTDOWN SIGNAL RECEIVED. Terminating...")
        self.running = False

    def run(self) -> None:
        """
        Main execution loop.
        """
        self.check_identity()
        logger.info(f"🚀 PILOT MONITOR ONLINE. Interval: {self.interval}s")

        try:
            while self.running:
                self.heartbeat()
                # Use a shorter sleep loop to respond to shutdown signals faster
                for _ in range(self.interval):
                    if not self.running:
                        break
                    time.sleep(1)
        except Exception as e:
            logger.error(f"💥 CRITICAL ERROR: {e}", exc_info=True)
            sys.exit(1)
        
        logger.info("👋 Pilot Monitor Offline.")

if __name__ == "__main__":
    interval = 60
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
        except ValueError:
            logger.warning(f"Invalid interval argument '{sys.argv[1]}'. Using default {interval}s.")
    
    monitor = PilotMonitor(interval=interval)
    monitor.run()
