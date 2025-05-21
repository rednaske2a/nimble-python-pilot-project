#!/usr/bin/env python3
import sys
from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.utils.logger import setup_logger

if __name__ == "__main__":
    # Set up logging
    logger = setup_logger()
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Set application info
    app.setApplicationName("Civitai Model Manager")
    app.setApplicationVersion("2.0")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())