import time
from pathlib import Path
from typing import Dict, List, Any, Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget, QMessageBox,
    QStatusBar
)
from PySide6.QtGui import QColor, QPalette

from src.constants import APP_THEMES, DOWNLOAD_STATUS
from src.core.download_manager import DownloadManager, DownloadQueue
from src.core.storage_manager import StorageManager
from src.db.models_db import ModelsDatabase
from src.models.model_info import ModelInfo
from src.ui.tabs.download_tab import DownloadTab
from src.ui.tabs.gallery_tab import GalleryTab
from src.ui.tabs.settings_tab import SettingsTab
from src.ui.tabs.storage_tab import StorageTab
from src.utils.config_manager import ConfigManager
from src.utils.logger import get_logger, setup_logger

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize logger
        self.logger = get_logger()
        
        try:
            # Set window properties
            self.setWindowTitle("Civitai Model Manager")
            self.setMinimumSize(1200, 800)
            
            # Initialize components
            self.init_components()
            
            # Initialize UI
            self.init_ui()
            
            # Connect signals
            self.connect_signals()
            
            # Load data
            self.load_data()
            
        except Exception as e:
            self.logger.error(f"Error initializing main window: {e}")
            QMessageBox.critical(self, "Initialization Error", 
                               f"An error occurred during application initialization: {str(e)}\n\n"
                               "The application may not function correctly.")
    
    def init_components(self):
        """Initialize application components"""
        # Load configuration
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        
        # Update logger level based on config
        setup_logger(self.config.get("log_level", "info"))
        
        # Set current theme
        self.current_theme_id = self.config.get("theme", "dark")
        self.theme = APP_THEMES.get(self.current_theme_id, APP_THEMES["dark"])
        
        # Initialize managers
        self.models_db = ModelsDatabase()
        
        comfy_path = self.config.get("comfy_path", "")
        self.storage_manager = StorageManager(comfy_path)
        
        # Initialize download components
        self.download_queue = DownloadQueue(self)
        self.download_manager = DownloadManager(self.config)
    
    def init_ui(self):
        """Initialize UI components"""
        # Set up central widget with main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create tab widget for main sections
        self.tab_widget = QTabWidget()
        self.apply_theme_to_tabs()
        
        # Create tabs
        self.download_tab = DownloadTab(self.theme, self)
        self.gallery_tab = GalleryTab(self.theme, self)
        self.storage_tab = StorageTab(self.theme, self)
        self.settings_tab = SettingsTab(self.theme, self)
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.download_tab, "Download")
        self.tab_widget.addTab(self.gallery_tab, "Gallery")
        self.tab_widget.addTab(self.storage_tab, "Storage")
        self.tab_widget.addTab(self.settings_tab, "Settings")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {self.theme['window']};
                color: {self.theme['text']};
                border-top: 1px solid {self.theme['border']};
            }}
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Apply theme to window
        self.apply_theme()
    
    def connect_signals(self):
        """Connect signals and slots"""
        # Download queue signals
        self.download_queue.queue_updated.connect(self.update_queue_status)
        self.download_queue.download_started.connect(self.start_download_from_queue)
        self.download_queue.task_updated.connect(self.update_download_task)
        
        # Settings signals
        self.settings_tab.settings_saved.connect(self.on_settings_saved)
        self.settings_tab.theme_changed.connect(self.change_theme)
    
    def load_data(self):
        """Load application data"""
        # Scan for existing models if comfy_path is set
        if self.config.get("comfy_path"):
            self.scan_for_models()
        
        # Refresh gallery
        self.gallery_tab.refresh_gallery()
        
        # Refresh storage analysis
        self.storage_tab.refresh_storage_analysis()
    
    def apply_theme(self):
        """Apply the current theme to the application"""
        # Set application palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(self.theme["window"]))
        palette.setColor(QPalette.WindowText, QColor(self.theme["text"]))
        palette.setColor(QPalette.Base, QColor(self.theme["background"]))
        palette.setColor(QPalette.AlternateBase, QColor(self.theme["card"]))
        palette.setColor(QPalette.ToolTipBase, QColor(self.theme["card"]))
        palette.setColor(QPalette.ToolTipText, QColor(self.theme["text"]))
        palette.setColor(QPalette.Text, QColor(self.theme["text"]))
        palette.setColor(QPalette.Button, QColor(self.theme["card"]))
        palette.setColor(QPalette.ButtonText, QColor(self.theme["text"]))
        palette.setColor(QPalette.BrightText, QColor(self.theme["text"]))
        palette.setColor(QPalette.Link, QColor(self.theme["accent"]))
        palette.setColor(QPalette.Highlight, QColor(self.theme["accent"]))
        palette.setColor(QPalette.HighlightedText, QColor("white"))
        
        self.setPalette(palette)
        
        # Set stylesheet for the main window
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.theme["window"]};
                color: {self.theme["text"]};
            }}
            QWidget {{
                background-color: {self.theme["window"]};
                color: {self.theme["text"]};
            }}
            QScrollBar:vertical {{
                border: none;
                background: {self.theme["background"]};
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.theme["border"]};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: {self.theme["background"]};
                height: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: {self.theme["border"]};
                min-width: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: none;
                background: none;
                width: 0px;
            }}
            QToolTip {{
                background-color: {self.theme["card"]};
                color: {self.theme["text"]};
                border: 1px solid {self.theme["border"]};
                padding: 4px;
            }}
        """)
        
        # Update theme for tab widget
        self.apply_theme_to_tabs()
        
        # Update status bar
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {self.theme['window']};
                color: {self.theme['text']};
                border-top: 1px solid {self.theme['border']};
            }}
        """)
    
    def apply_theme_to_tabs(self):
        """Apply theme to tab widget"""
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {self.theme['border']};
                background-color: {self.theme['window']};
            }}
            QTabBar::tab {{
                background-color: {self.theme['card']};
                color: {self.theme['text']};
                border: 1px solid {self.theme['border']};
                border-bottom-color: {self.theme['border']};
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 8ex;
                padding: 8px 12px;
            }}
            QTabBar::tab:selected, QTabBar::tab:hover {{
                background-color: {self.theme['card_hover']};
            }}
            QTabBar::tab:selected {{
                border-bottom-color: {self.theme['window']};
            }}
        """)
    
    def change_theme(self, theme_id):
        """Change the application theme"""
        if theme_id in APP_THEMES:
            self.current_theme_id = theme_id
            self.theme = APP_THEMES[theme_id]
            
            # Update theme for all components
            self.apply_theme()
            
            # Update theme for specific tabs
            self.download_tab.set_theme(self.theme)
            self.gallery_tab.set_theme(self.theme)
            self.storage_tab.set_theme(self.theme)
            self.settings_tab.set_theme(self.theme)
            
            # Update config
            self.config["theme"] = theme_id
            self.config_manager.save()
            
            self.status_bar.showMessage(f"Theme changed to {self.theme['name']}", 3000)
    
    def on_settings_saved(self):
        """Handle settings saved event"""
        # Reload configuration
        self.config = self.config_manager.config
        
        # Update UI
        self.gallery_tab.refresh_gallery()
        self.storage_tab.refresh_storage_analysis()
        
        # If comfy_path was changed, refresh models
        if self.config.get("comfy_path"):
            self.storage_manager = StorageManager(self.config.get("comfy_path"))
            self.scan_for_models()
        
        self.status_bar.showMessage("Settings saved successfully", 3000)
    
    def scan_for_models(self):
        """Scan for existing models in ComfyUI directory"""
        comfy_path = self.config.get("comfy_path", "")
        if not comfy_path:
            self.logger.warning("ComfyUI path not set, skipping model scan")
            return
        
        comfy_dir = Path(comfy_path)
        if not comfy_dir.exists():
            self.logger.error(f"ComfyUI directory not found: {comfy_path}")
            return
        
        self.logger.info("Scanning for models...")
        self.status_bar.showMessage("Scanning for models...", 3000)
        
        # Scan for models
        models = self.storage_manager.scan_models()
        
        # Update models database
        for model_data in models:
            if "id" in model_data:
                model_id = str(model_data["id"])
                self.models_db.models[model_id] = model_data
        
        # Save database
        self.models_db.save()
        
        # Refresh gallery
        self.gallery_tab.refresh_gallery()
        
        self.logger.info(f"Scan complete. Found {len(models)} models.")
        self.status_bar.showMessage(f"Scan complete. Found {len(models)} models.", 3000)
    
    def update_queue_status(self, queue_size):
        """Update queue status label"""
        self.download_tab.set_queue_status(queue_size)
    
    def update_download_task(self, task):
        """Update the download task in the queue widget"""
        self.download_tab.update_download_task(task)
    
    def start_download_from_queue(self, url):
        """Start a download from the queue"""
        self.start_download(url)
    
    def start_download(self, url):
        """Start downloading a model"""
        self.download_manager.start_download(
            url,
            self.download_progress_callback,
            self.download_completed_callback
        )
    
    def download_progress_callback(self, log_message, model_progress, image_progress, status):
        """Callback for download progress updates"""
        if log_message:
            self.download_tab.log(log_message, status)
        
        # Find the URL for this task
        url = None
        for task_url, worker in self.download_manager.active_downloads.items():
            if worker.is_alive():
                url = task_url
                break
        
        if url:
            # Update task progress
            progress_update = {}
            if model_progress >= 0:
                progress_update["model_progress"] = model_progress
            if image_progress >= 0:
                progress_update["image_progress"] = image_progress
            
            if progress_update:
                self.download_queue.update_task(url, **progress_update)
    
    def download_completed_callback(self, success, message, model_info):
        """Callback for download completion"""
        # Find the URL for this task
        url = None
        for task_url in list(self.download_manager.active_downloads.keys()):
            if task_url not in self.download_manager.active_downloads:  # Check if already removed
                continue
            
            worker = self.download_manager.active_downloads[task_url]
            if not worker.is_alive():
                url = task_url
                del self.download_manager.active_downloads[task_url]
                break
        
        if success and model_info:
            # Add model to database
            self.models_db.add_model(model_info)
            
            # Save database
            self.models_db.save()
            
            # Refresh gallery
            self.gallery_tab.refresh_gallery()
            
            self.download_tab.log(message, "success")
            
            # Update task status
            if url:
                self.download_queue.complete_task(url, True, model_info=model_info)
        else:
            self.download_tab.log(f"Download failed: {message}", "error")
            
            # Update task status
            if url:
                self.download_queue.complete_task(url, False, message=message)
        
        # Process next in queue
        self.process_next_download()
    
    def process_next_download(self):
        """Process the next download in the queue"""
        # Wait a bit before starting the next download
        time.sleep(0.5)
        
        if not self.download_queue.is_empty():
            url = self.download_queue.get_next_url()
            if url:
                self.start_download(url)
    
    def start_batch_download(self, urls):
        """Start batch download of models"""
        if not urls:
            QMessageBox.warning(self, "No URLs", "Please enter at least one Civitai model URL.")
            return
        
        # Check if ComfyUI path is set
        if not self.config.get("comfy_path"):
            QMessageBox.warning(self, "ComfyUI Path Not Set", 
                              "Please set your ComfyUI path in Settings before downloading models.")
            self.tab_widget.setCurrentIndex(3)  # Switch to settings tab
            return
        
        # Add URLs to queue
        self.download_queue.add_urls(urls)
        
        # Start processing queue if not already processing
        if not self.download_queue.is_empty() and not self.download_manager.active_downloads:
            self.process_next_download()
        
        self.download_tab.log(f"Added {len(urls)} URLs to download queue", "info")
    
    def cancel_download(self, url):
        """Cancel a download"""
        if self.download_manager.cancel_download(url):
            self.download_queue.cancel_task(url)
            self.download_tab.log(f"Download cancelled: {url}", "warning")
    
    def clear_download_queue(self):
        """Clear the download queue"""
        # Cancel all active downloads
        for url in list(self.download_manager.active_downloads.keys()):
            self.download_manager.cancel_download(url)
            self.download_queue.cancel_task(url)
        
        # Clear queue
        self.download_queue.clear()
        
        self.download_tab.log("Download queue cleared", "info")
    
    def closeEvent(self, event):
        """Handle application close event"""
        # Save config and database
        self.config_manager.save()
        self.models_db.save()
        
        # Cancel active downloads
        for url in list(self.download_manager.active_downloads.keys()):
            self.download_manager.cancel_download(url)
        
        event.accept()