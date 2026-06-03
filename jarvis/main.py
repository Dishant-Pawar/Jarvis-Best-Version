import sys
import os
from PyQt6.QtWidgets import QApplication
from jarvis.utils.logger import logger
from jarvis.core.assistant import Assistant
from jarvis.ui.floating_panel import FloatingPanel

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global hook to log unhandled exceptions and prevent silent crashes."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Unhandled exception occurred!", exc_info=(exc_type, exc_value, exc_traceback))

def main():
    logger.info("==========================================")
    logger.info("Initializing J.A.R.V.I.S. Desktop Assistant")
    logger.info("==========================================")
    
    # Set sys.excepthook to capture crashes in log files
    sys.excepthook = handle_exception

    # Create the PyQt6 application
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("JARVIS")
    app.setApplicationDisplayName("JARVIS Assistant")
    app.setOrganizationName("AI-Automation")

    # Instantiate the Brain (Assistant Core)
    assistant = Assistant()
    
    # Instantiate the Face (Floating Panel Window)
    ui_panel = FloatingPanel(assistant)
    
    # Show the Panel
    ui_panel.show()
    logger.info("Floating panel interface loaded and displayed.")

    # Start the assistant background threads
    assistant.start()
    
    # Execute application
    exit_code = app.exec()
    
    # Cleanup on shutdown
    logger.info("Application exiting, stopping background services...")
    assistant.stop()
    logger.info("Shutdown completed.")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
