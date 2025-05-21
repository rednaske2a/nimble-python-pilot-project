
#!/usr/bin/env python3
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings, Qt

from src.ui.main_window import MainWindow
from src.utils.logger import setup_logger
from src.utils.config_manager import ConfigManager

if __name__ == "__main__":
    # Set up logging
    logger = setup_logger()
    
    # Load configuration
    config = ConfigManager()
    
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Set application info
    app.setApplicationName("Civitai Model Manager")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("CivitaiManager")
    app.setOrganizationDomain("civitaimanager.org")
    
    # Create main window
    main_window = MainWindow(config)
    main_window.show()
    
    sys.exit(app.exec())
