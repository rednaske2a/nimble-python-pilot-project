
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget, QMessageBox,
    QStatusBar, QSplitter, QApplication, QFileDialog
)
from PySide6.QtCore import Qt, QSettings, QTimer, QSize, QPoint, QEvent
from PySide6.QtGui import QColor, QPalette, QAction, QIcon, QDragEnterEvent, QDropEvent

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
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        
        # Initialize logger
        self.logger = get_logger(__name__)
        
        try:
            # Store config manager
            self.config_manager = config_manager
            self.config = self.config_manager.config
            
            # Update logger level based on config
            setup_logger(self.config.get("log_level", "info"))
            
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
            
            # Load window state
            self.load_window_state()
            
            # Enable drag and drop
            self.setAcceptDrops(True)
            
        except Exception as e:
            self.logger.error(f"Error initializing main window: {e}")
            QMessageBox.critical(self, "Initialization Error", 
                               f"An error occurred during application initialization: {str(e)}\n\n"
                               "The application may not function correctly.")
    
    def init_components(self):
        """Initialize application components"""
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
        
        # Initialize refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(10000)  # 10 seconds
    
    def init_ui(self):
        """Initialize UI components"""
        # Set up central widget with main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create splitter widget for resizable panels
        self.splitter = QSplitter(Qt.Horizontal)
        
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
        
        # Set up splitter with tab widget
        self.splitter.addWidget(self.tab_widget)
        
        # Add splitter to main layout
        main_layout.addWidget(self.splitter)
        
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
        
        # Create actions
        self.create_actions()
        
        # Apply theme to window
        self.apply_theme()
    
    def create_actions(self):
        """Create menu actions"""
        # File menu actions
        self.scan_action = QAction("Scan for Models", self)
        self.scan_action.triggered.connect(self.scan_for_models)
        
        self.export_action = QAction("Export Database", self)
        self.export_action.triggered.connect(self.export_database)
        
        self.import_action = QAction("Import Database", self)
        self.import_action.triggered.connect(self.import_database)
        
        # Create menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self.scan_action)
        file_menu.addSeparator()
        file_menu.addAction(self.export_action)
        file_menu.addAction(self.import_action)
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menu_bar.addMenu("View")
        
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_data)
        view_menu.addAction(refresh_action)
        
        view_menu.addSeparator()
        
        # Theme submenu
        theme_menu = view_menu.addMenu("Theme")
        
        # Add theme actions
        for theme_id, theme_data in APP_THEMES.items():
            theme_action = QAction(theme_data["name"], self)
            theme_action.setCheckable(True)
            theme_action.setChecked(theme_id == self.current_theme_id)
            theme_action.setData(theme_id)
            theme_action.triggered.connect(self.on_theme_action)
            theme_menu.addAction(theme_action)
    
    def connect_signals(self):
        """Connect signals and slots"""
        # Download queue signals
        self.download_queue.queue_updated.connect(self.update_queue_status)
        self.download_queue.download_started.connect(self.start_download_from_queue)
        self.download_queue.task_updated.connect(self.update_download_task)
        
        # Settings signals
        self.settings_tab.settings_saved.connect(self.on_settings_saved)
        
        # Timer signal
        self.refresh_timer.timeout.connect(self.on_refresh_timer)
        
        # Tab widget signals
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
    
    def load_data(self):
        """Load application data"""
        # Start refresh timer
        self.refresh_timer.start()
        
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
            QMenuBar {{
                background-color: {self.theme["window"]};
                color: {self.theme["text"]};
            }}
            QMenuBar::item {{
                background-color: {self.theme["window"]};
                color: {self.theme["text"]};
            }}
            QMenuBar::item:selected {{
                background-color: {self.theme["card_hover"]};
            }}
            QMenu {{
                background-color: {self.theme["card"]};
                color: {self.theme["text"]};
                border: 1px solid {self.theme["border"]};
            }}
            QMenu::item:selected {{
                background-color: {self.theme["accent"]};
                color: white;
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
        
        # Update theme for splitter
        self.splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {self.theme['border']};
            }}
            QSplitter::handle:hover {{
                background-color: {self.theme['accent']};
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
    
    def on_theme_action(self):
        """Handle theme selection from menu"""
        action = self.sender()
        if action:
            theme_id = action.data()
            self.change_theme(theme_id)
            
            # Update checked status of theme actions
            for theme_action in self.findChildren(QAction):
                if hasattr(theme_action, 'data') and theme_action.data() in APP_THEMES:
                    theme_action.setChecked(theme_action.data() == theme_id)
    
    def on_settings_saved(self):
        """Handle settings saved event"""
        # Reload configuration
        self.config = self.config_manager.config
        
        # Update UI
        self.gallery_tab.refresh_gallery()
        
        # If comfy_path was changed, refresh models
        new_comfy_path = self.config.get("comfy_path")
        if new_comfy_path:
            self.storage_manager = StorageManager(new_comfy_path)
            self.storage_tab.set_storage_manager(self.storage_manager)
            self.scan_for_models()
            self.storage_tab.refresh_storage_analysis()
        
        self.status_bar.showMessage("Settings saved successfully", 3000)
    
    def scan_for_models(self):
        """Scan for existing models in ComfyUI directory"""
        comfy_path = self.config.get("comfy_path", "")
        if not comfy_path:
            self.logger.warning("ComfyUI path not set, skipping model scan")
            QMessageBox.warning(self, "ComfyUI Path Missing", 
                              "Please set your ComfyUI path in Settings before scanning for models.")
            return
        
        comfy_dir = Path(comfy_path)
        if not comfy_dir.exists():
            self.logger.error(f"ComfyUI directory not found: {comfy_path}")
            QMessageBox.warning(self, "Directory Not Found", 
                              f"ComfyUI directory not found: {comfy_path}\n\n"
                              "Please check your settings.")
            return
        
        self.logger.info("Scanning for models...")
        self.status_bar.showMessage("Scanning for models...", 0)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        
        try:
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
            self.status_bar.showMessage(f"Scan complete. Found {len(models)} models.", 5000)
        except Exception as e:
            self.logger.error(f"Error during model scan: {str(e)}")
            QMessageBox.critical(self, "Scan Error", 
                               f"An error occurred during model scan: {str(e)}")
        finally:
            QApplication.restoreOverrideCursor()
    
    def export_database(self):
        """Export database to JSON file"""
        export_path, _ = QFileDialog.getSaveFileName(
            self, "Export Database", 
            str(Path.home()), "JSON Files (*.json)"
        )
        
        if export_path:
            try:
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(self.models_db.models, f, indent=2)
                self.status_bar.showMessage(f"Database exported successfully to {export_path}", 5000)
            except Exception as e:
                self.logger.error(f"Error exporting database: {str(e)}")
                QMessageBox.critical(self, "Export Error", 
                                   f"An error occurred during database export: {str(e)}")
    
    def import_database(self):
        """Import database from JSON file"""
        import_path, _ = QFileDialog.getOpenFileName(
            self, "Import Database", 
            str(Path.home()), "JSON Files (*.json)"
        )
        
        if import_path:
            try:
                with open(import_path, 'r', encoding='utf-8') as f:
                    imported_models = json.load(f)
                
                if not isinstance(imported_models, dict):
                    raise ValueError("Invalid database format")
                
                # Ask for confirmation
                count = len(imported_models)
                reply = QMessageBox.question(self, "Import Database",
                                          f"Import {count} models?\n\n"
                                          "This will merge with your existing database.",
                                          QMessageBox.Yes | QMessageBox.No)
                
                if reply == QMessageBox.Yes:
                    # Merge with existing database
                    for model_id, model_data in imported_models.items():
                        self.models_db.models[model_id] = model_data
                    
                    # Save database
                    self.models_db.save()
                    
                    # Refresh gallery
                    self.gallery_tab.refresh_gallery()
                    
                    self.status_bar.showMessage(f"Imported {count} models successfully", 5000)
            except Exception as e:
                self.logger.error(f"Error importing database: {str(e)}")
                QMessageBox.critical(self, "Import Error", 
                                   f"An error occurred during database import: {str(e)}")
    
    def update_queue_status(self, queue_size):
        """Update queue status label"""
        self.download_tab.set_queue_status(queue_size)
        
        # Update window title to show queue size
        if queue_size > 0:
            self.setWindowTitle(f"Civitai Model Manager ({queue_size} in queue)")
        else:
            self.setWindowTitle("Civitai Model Manager")
    
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
            self.storage_tab.refresh_storage_analysis()
            
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
        added_count = self.download_queue.add_urls(urls)
        
        # Start processing queue if not already processing
        if added_count > 0 and self.download_manager.get_active_downloads_count() == 0:
            self.process_next_download()
        
        if added_count > 0:
            self.download_tab.log(f"Added {added_count} URLs to download queue", "info")
    
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
    
    def refresh_data(self):
        """Refresh application data"""
        self.gallery_tab.refresh_gallery()
        self.storage_tab.refresh_storage_analysis()
        self.status_bar.showMessage("Data refreshed", 3000)
    
    def on_refresh_timer(self):
        """Handle refresh timer event"""
        # Update task durations in download queue
        for task in self.download_queue.get_all_tasks():
            if task.status in [DOWNLOAD_STATUS["QUEUED"], DOWNLOAD_STATUS["DOWNLOADING"]]:
                self.download_queue.task_updated.emit(task)
    
    def on_tab_changed(self, index):
        """Handle tab changed event"""
        # Load data for the newly selected tab
        if index == 1:  # Gallery tab
            self.gallery_tab.refresh_gallery()
        elif index == 2:  # Storage tab
            self.storage_tab.refresh_storage_analysis()
    
    def load_window_state(self):
        """Load window position, size and state from settings"""
        settings = QSettings("CivitaiManager", "MainWindow")
        
        if settings.contains("geometry"):
            self.restoreGeometry(settings.value("geometry"))
        
        if settings.contains("windowState"):
            self.restoreState(settings.value("windowState"))
        
        # Restore splitter state
        if settings.contains("splitterState"):
            self.splitter.restoreState(settings.value("splitterState"))
    
    def save_window_state(self):
        """Save window position, size and state to settings"""
        settings = QSettings("CivitaiManager", "MainWindow")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.setValue("splitterState", self.splitter.saveState())
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event for drag-n-drop URL import"""
        if event.mimeData().hasText():
            text = event.mimeData().text()
            if "civitai.com/models" in text:
                event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event for drag-n-drop URL import"""
        urls = []
        text = event.mimeData().text()
        
        # Extract Civitai URLs
        import re
        url_pattern = r'https?://civitai\.com/models/\S+'
        found_urls = re.findall(url_pattern, text)
        
        if found_urls:
            self.start_batch_download(found_urls)
            event.acceptProposedAction()
            
            # Switch to download tab
            self.tab_widget.setCurrentIndex(0)
    
    def closeEvent(self, event):
        """Handle application close event"""
        # Save config and database
        self.config_manager.save()
        self.models_db.save()
        
        # Cancel active downloads
        for url in list(self.download_manager.active_downloads.keys()):
            self.download_manager.cancel_download(url)
        
        # Save window state
        self.save_window_state()
        
        event.accept()
