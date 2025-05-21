from typing import Dict, List, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QPlainTextEdit,
    QGroupBox, QSplitter, QFrame
)
from PySide6.QtCore import Qt

from src.ui.components.download_queue_widget import DownloadQueueWidget
from src.ui.components.log_widget import LogWidget
from src.models.download_task import DownloadTask

class DownloadTab(QWidget):
    """Download tab for downloading models from Civitai"""
    
    def __init__(self, theme: Dict, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        
        # App title and version
        title_layout = QHBoxLayout()
        app_title = QLabel("Civitai Model Manager")
        app_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {self.theme['text']};")
        app_version = QLabel("v2.0")
        app_version.setStyleSheet(f"font-size: 12px; color: {self.theme['text_tertiary']};")
        title_layout.addWidget(app_title)
        title_layout.addWidget(app_version, alignment=Qt.AlignBottom)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet(f"background-color: {self.theme['border']};")
        layout.addWidget(divider)
        
        # Split view for URL input and queue
        splitter = QSplitter(Qt.Vertical)
        
        # URL input section
        url_widget = QWidget()
        url_layout = QVBoxLayout(url_widget)
        
        url_group = self.create_styled_group_box("Download Model")
        url_inner_layout = QVBoxLayout(url_group)
        
        url_label = QLabel("Model URLs (one per line):")
        url_label.setStyleSheet(f"color: {self.theme['text']};")
        self.url_input = QPlainTextEdit()
        self.url_input.setPlaceholderText("Paste Civitai model URLs here, one per line...")
        self.url_input.setMinimumHeight(150)
        self.url_input.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {self.theme['input_bg']};
                color: {self.theme['text']};
                border: 1px solid {self.theme['input_border']};
                border-radius: 4px;
                padding: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
            }}
        """)
        
        button_layout = QHBoxLayout()
        
        self.download_btn = QPushButton("Download All")
        self.download_btn.setStyleSheet(self.get_primary_button_style())
        self.download_btn.clicked.connect(self.start_batch_download)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setStyleSheet(self.get_secondary_button_style())
        self.clear_btn.clicked.connect(lambda: self.url_input.clear())
        
        button_layout.addWidget(self.download_btn)
        button_layout.addWidget(self.clear_btn)
        
        url_inner_layout.addWidget(url_label)
        url_inner_layout.addWidget(self.url_input)
        url_inner_layout.addLayout(button_layout)
        
        # Queue status
        self.queue_status_label = QLabel("Queue: 0")
        self.queue_status_label.setStyleSheet(f"font-size: 14px; color: {self.theme['text_secondary']};")
        url_inner_layout.addWidget(self.queue_status_label)
        
        url_layout.addWidget(url_group)
        
        
        # --- Create a horizontal splitter for queue and log ---
        queue_log_splitter = QSplitter(Qt.Horizontal)

        # Left: Download Queue Section
        queue_widget = QWidget()
        queue_layout = QVBoxLayout(queue_widget)

        queue_group = self.create_styled_group_box("Download Queue")
        queue_inner_layout = QVBoxLayout(queue_group)
        self.download_queue_widget = DownloadQueueWidget(self.theme)
        queue_inner_layout.addWidget(self.download_queue_widget)
        queue_layout.addWidget(queue_group)

        queue_log_splitter.addWidget(queue_widget)

        # Right: Log Output Section
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)

        log_group = self.create_styled_group_box("Download Log")
        log_group_layout = QVBoxLayout(log_group)
        self.log_widget = LogWidget(self.theme)
        self.log_widget.setMinimumHeight(200)
        log_group_layout.addWidget(self.log_widget)
        log_layout.addWidget(log_group)

        queue_log_splitter.addWidget(log_widget)
        queue_log_splitter.setSizes([600, 400])  # Optional: Set initial sizes

        # Add the horizontal splitter to the main layout
        layout.addWidget(url_widget)
        layout.addWidget(queue_log_splitter, 1)  # Stretch to fill space
    
    def create_styled_group_box(self, title):
        """Create a styled group box"""
        group = QGroupBox(title)
        group.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                margin-top: 1ex;
                font-weight: bold;
                color: {self.theme['text']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        return group
    
    def get_primary_button_style(self):
        """Get style for primary buttons"""
        return f"""
            QPushButton {{
                background-color: {self.theme['accent']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.theme['accent_hover']};
            }}
            QPushButton:pressed {{
                background-color: {self.theme['accent_pressed']};
            }}
        """
    
    def get_secondary_button_style(self):
        """Get style for secondary buttons"""
        return f"""
            QPushButton {{
                background-color: {self.theme['text_tertiary']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {self.theme['text_secondary']};
            }}
        """
    
    def set_theme(self, theme):
        """Update the theme"""
        self.theme = theme
        
        # Update UI styles
        self.queue_status_label.setStyleSheet(f"font-size: 14px; color: {self.theme['text_secondary']};")
        self.url_input.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {self.theme['input_bg']};
                color: {self.theme['text']};
                border: 1px solid {self.theme['input_border']};
                border-radius: 4px;
                padding: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
            }}
        """)
        
        self.download_btn.setStyleSheet(self.get_primary_button_style())
        self.clear_btn.setStyleSheet(self.get_secondary_button_style())
        
        # Update child widgets
        self.download_queue_widget.set_theme(self.theme)
        self.log_widget.set_theme(self.theme)
        
        # Update group boxes
        for child in self.findChildren(QGroupBox):
            child.setStyleSheet(f"""
                QGroupBox {{
                    border: 1px solid {self.theme['border']};
                    border-radius: 8px;
                    margin-top: 1ex;
                    font-weight: bold;
                    color: {self.theme['text']};
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }}
            """)
    
    def log(self, message, status="info"):
        """Add a log message"""
        self.log_widget.add_log(message, status)
    
    def set_queue_status(self, queue_size):
        """Update queue status label"""
        self.queue_status_label.setText(f"Queue: {queue_size}")
    
    def update_download_task(self, task: DownloadTask):
        """Update a download task"""
        self.download_queue_widget.update_task(task)
    
    def start_batch_download(self):
        """Start batch download of models"""
        urls = self.url_input.toPlainText().strip().split("\n")
        urls = [url.strip() for url in urls if url.strip()]
        
        # Pass to parent window for processing
        parent = self.parent
        if hasattr(parent, "start_batch_download"):
            parent.start_batch_download(urls)