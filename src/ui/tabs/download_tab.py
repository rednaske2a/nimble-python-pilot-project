
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel, 
    QPushButton, QTextEdit, QLineEdit, QSpinBox, QFrame
)
from PySide6.QtCore import Qt, Signal, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

from src.ui.components.download_queue_widget import DownloadQueueWidget
from src.ui.components.log_widget import LogWidget
from src.models.download_task import DownloadTask

class DownloadTab(QWidget):
    """Tab for download management"""
    
    add_urls_requested = Signal(list)  # urls
    
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.parent_window = parent
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        
        # Create splitter for main content and queue
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Create left panel with log and input
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Log widget
        self.log_widget = LogWidget(self.theme)
        
        # URL input section
        url_section = self.create_url_input_section()
        
        left_layout.addWidget(self.log_widget, 3)
        left_layout.addWidget(url_section, 1)
        
        # Create right panel with queue
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Queue widget
        self.queue_widget = DownloadQueueWidget(self.theme)
        self.queue_widget.cancel_requested.connect(self.cancel_download)
        self.queue_widget.clear_requested.connect(self.clear_queue)
        
        right_layout.addWidget(self.queue_widget)
        
        # Add panels to splitter
        self.splitter.addWidget(left_panel)
        self.splitter.addWidget(right_panel)
        
        # Set initial sizes
        self.splitter.setSizes([int(self.width() * 0.6), int(self.width() * 0.4)])
        
        layout.addWidget(self.splitter)
    
    def create_url_input_section(self):
        """Create URL input section with validation"""
        section = QFrame()
        section.setFrameShape(QFrame.StyledPanel)
        section.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme['card']};
                border-radius: 8px;
                border: 1px solid {self.theme['border']};
            }}
        """)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("Add Models to Download Queue")
        title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {self.theme['text']};
        """)
        
        # URL input
        url_layout = QVBoxLayout()
        url_label = QLabel("CivitAI URLs (one per line)")
        url_label.setStyleSheet(f"color: {self.theme['text_secondary']};")
        
        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText("https://civitai.com/models/...")
        self.url_input.setMinimumHeight(80)
        self.url_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.theme['input_bg']};
                color: {self.theme['text']};
                border: 1px solid {self.theme['border']};
                border-radius: 4px;
                padding: 5px;
            }}
        """)
        
        # Example URL
        example_label = QLabel("Example: https://civitai.com/models/1234/cool-model")
        example_label.setStyleSheet(f"color: {self.theme['text_secondary']}; font-style: italic; font-size: 11px;")
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(example_label)
        
        # Options row
        options_layout = QHBoxLayout()
        
        max_images_label = QLabel("Max Images:")
        max_images_label.setStyleSheet(f"color: {self.theme['text_secondary']};")
        
        self.max_images_input = QSpinBox()
        self.max_images_input.setRange(1, 100)
        self.max_images_input.setValue(9)
        self.max_images_input.setStyleSheet(f"""
            QSpinBox {{
                background-color: {self.theme['input_bg']};
                color: {self.theme['text']};
                border: 1px solid {self.theme['border']};
                border-radius: 4px;
                padding: 5px;
                min-width: 60px;
            }}
        """)
        
        options_layout.addWidget(max_images_label)
        options_layout.addWidget(self.max_images_input)
        options_layout.addStretch()
        
        # Add button
        self.add_button = QPushButton("Add to Queue")
        self.add_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme['accent']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.theme['accent_hover']};
            }}
            QPushButton:pressed {{
                background-color: {self.theme['accent']};
            }}
        """)
        self.add_button.clicked.connect(self.add_urls)
        
        options_layout.addWidget(self.add_button)
        
        layout.addWidget(title)
        layout.addLayout(url_layout)
        layout.addLayout(options_layout)
        
        return section
    
    def add_urls(self):
        """Process URLs from input and add to queue"""
        text = self.url_input.toPlainText().strip()
        if not text:
            return
        
        # Update max images in config
        self.parent_window.config["top_image_count"] = self.max_images_input.value()
        
        # Extract URLs
        import re
        url_pattern = r'https?://civitai\.com/models/\S+'
        urls = []
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if re.match(url_pattern, line):
                urls.append(line)
            else:
                self.log(f"Invalid URL format: {line}", "error")
        
        if urls:
            # Start download
            self.parent_window.start_batch_download(urls)
            
            # Clear input
            self.url_input.clear()
    
    def set_theme(self, theme):
        """Update the theme"""
        self.theme = theme
        
        # Update log widget theme
        self.log_widget.set_theme(theme)
        
        # Update queue widget theme
        self.queue_widget.set_theme(theme)
        
        # Update URL input section
        self.url_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.theme['input_bg']};
                color: {self.theme['text']};
                border: 1px solid {self.theme['border']};
                border-radius: 4px;
                padding: 5px;
            }}
        """)
        
        self.max_images_input.setStyleSheet(f"""
            QSpinBox {{
                background-color: {self.theme['input_bg']};
                color: {self.theme['text']};
                border: 1px solid {self.theme['border']};
                border-radius: 4px;
                padding: 5px;
                min-width: 60px;
            }}
        """)
        
        self.add_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme['accent']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.theme['accent_hover']};
            }}
            QPushButton:pressed {{
                background-color: {self.theme['accent']};
            }}
        """)
        
        # Update frame
        for frame in self.findChildren(QFrame):
            frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.theme['card']};
                    border-radius: 8px;
                    border: 1px solid {self.theme['border']};
                }}
            """)
        
        # Update labels
        for label in self.findChildren(QLabel):
            if "font-size: 16px" in label.styleSheet():
                label.setStyleSheet(f"""
                    font-size: 16px;
                    font-weight: bold;
                    color: {self.theme['text']};
                """)
            elif "font-style: italic" in label.styleSheet():
                label.setStyleSheet(f"color: {self.theme['text_secondary']}; font-style: italic; font-size: 11px;")
            else:
                label.setStyleSheet(f"color: {self.theme['text_secondary']};")
    
    def log(self, message, level="info"):
        """Add a message to the log"""
        self.log_widget.add_message(message, level)
    
    def update_download_task(self, task):
        """Update the download task in the queue widget"""
        self.queue_widget.update_task(task)
    
    def set_queue_status(self, queue_size):
        """Update queue status and update queue widget"""
        all_tasks = self.parent_window.download_queue.get_all_tasks()
        self.queue_widget.update_tasks(all_tasks)
    
    def cancel_download(self, url):
        """Signal to cancel a download"""
        self.parent_window.cancel_download(url)
    
    def clear_queue(self):
        """Signal to clear the download queue"""
        self.parent_window.clear_download_queue()
