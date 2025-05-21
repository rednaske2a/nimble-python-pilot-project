from typing import Dict
import re
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QSplitter, QScrollArea, QGridLayout, QFormLayout,
    QMessageBox, QWidget, QApplication
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap, QDesktopServices

from src.utils.formatting import format_size
from src.ui.components.image_viewer import ImageViewer

class ModelDetailDialog(QDialog):
    """Dialog for displaying detailed model information"""
    
    def __init__(self, model_data: Dict, theme: Dict, parent=None):
        super().__init__(parent)
        self.model_data = model_data
        self.theme = theme
        self.parent = parent
        self.setWindowTitle(f"Model Details: {model_data.get('name', 'Unknown')}")
        self.setMinimumSize(1000, 700)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header with model name and type
        header_layout = QHBoxLayout()
        
        # Model thumbnail
        thumbnail_path = self.model_data.get("thumbnail", "")
        if thumbnail_path and Path(thumbnail_path).exists():
            thumbnail = QLabel()
            pixmap = QPixmap(thumbnail_path)
            thumbnail.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            thumbnail.setFixedSize(80, 80)
            thumbnail.setStyleSheet(f"border-radius: 8px; background-color: {self.theme['background']};")
            header_layout.addWidget(thumbnail)
        
        # Model info
        info_layout = QVBoxLayout()
        
        name_label = QLabel(self.model_data.get("name", "Unknown"))
        name_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {self.theme['text']};")
        
        type_base_layout = QHBoxLayout()
        type_label = QLabel(f"Type: {self.model_data.get('type', 'Unknown')}")
        type_label.setStyleSheet(f"font-size: 14px; color: {self.theme['text_secondary']};")
        
        base_label = QLabel(f"Base Model: {self.model_data.get('base_model', 'Unknown')}")
        base_label.setStyleSheet(f"font-size: 14px; color: {self.theme['text_secondary']};")
        
        type_base_layout.addWidget(type_label)
        type_base_layout.addWidget(base_label)
        type_base_layout.addStretch()
        
        info_layout.addWidget(name_label)
        info_layout.addLayout(type_base_layout)
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        # External link button
        url = self.model_data.get("url", "")
        if url:
            open_url_btn = QPushButton("Open on Civitai")
            open_url_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.theme['accent']};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: {self.theme['accent_hover']};
                }}
            """)
            open_url_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
            header_layout.addWidget(open_url_btn)
        
        layout.addLayout(header_layout)
        
        # Divider
        divider = QLabel()
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background-color: {self.theme['border']};")
        layout.addWidget(divider)
        
        # Main content
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left side - metadata and tags
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Description
        description_group = self.create_styled_group_box("Description")
        description_layout = QVBoxLayout(description_group)
        
        description_scroll = QScrollArea()
        description_scroll.setWidgetResizable(True)
        description_scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {self.theme['input_bg']};
                border: 1px solid {self.theme['input_border']};
                border-radius: 4px;
            }}
        """)
        
        description_content = QLabel(self.model_data.get("description", "No description available"))
        description_content.setWordWrap(True)
        description_content.setStyleSheet(f"color: {self.theme['text']}; padding: 10px;")
        description_content.setTextFormat(Qt.PlainText)
        
        description_scroll.setWidget(description_content)
        description_scroll.setMaximumHeight(150)
        
        description_layout.addWidget(description_scroll)
        
        # Tags
        tags_group = self.create_styled_group_box("Activation Tags")
        tags_layout = QVBoxLayout(tags_group)
        
        tags_scroll = QScrollArea()
        tags_scroll.setWidgetResizable(True)
        tags_scroll.setStyleSheet("border: none; background-color: transparent;")
        
        tags_widget = QWidget()
        tags_flow = QGridLayout(tags_widget)
        tags_flow.setContentsMargins(5, 5, 5, 5)
        tags_flow.setSpacing(8)
        
        tags = self.model_data.get("tags", [])
        row, col = 0, 0
        max_cols = 3
        
        for tag in tags:
            tag_btn = QPushButton(tag)
            tag_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.theme['accent']};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 10px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: {self.theme['accent_hover']};
                }}
            """)
            tag_btn.clicked.connect(lambda _, t=tag: self.copy_to_clipboard(t))
            tag_btn.setToolTip("Click to copy")
            
            tags_flow.addWidget(tag_btn, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        if not tags:
            no_tags = QLabel("No tags available")
            no_tags.setStyleSheet(f"color: {self.theme['text_tertiary']}; padding: 10px;")
            no_tags.setAlignment(Qt.AlignCenter)
            tags_flow.addWidget(no_tags, 0, 0, 1, max_cols)
        
        tags_scroll.setWidget(tags_widget)
        tags_layout.addWidget(tags_scroll)
        
        # Metadata
        metadata_group = self.create_styled_group_box("Metadata")
        metadata_layout = QFormLayout(metadata_group)
        
        # Download date
        date_value = QLabel(self.model_data.get("download_date", "Unknown"))
        date_value.setStyleSheet(f"color: {self.theme['text']};")
        
        # Size
        size_bytes = self.model_data.get("size", 0)
        size_str = format_size(size_bytes)
        size_value = QLabel(size_str)
        size_value.setStyleSheet(f"color: {self.theme['text']};")
        
        # NSFW status
        nsfw_value = QLabel("Yes" if self.model_data.get("nsfw", False) else "No")
        nsfw_value.setStyleSheet(f"color: {self.theme['text']};")
        
        # Creator
        creator_value = QLabel(self.model_data.get("creator", "Unknown"))
        creator_value.setStyleSheet(f"color: {self.theme['text']};")
        
        # Version
        version_value = QLabel(self.model_data.get("version_name", "Unknown"))
        version_value.setStyleSheet(f"color: {self.theme['text']};")
        
        metadata_layout.addRow("Downloaded:", date_value)
        metadata_layout.addRow("Size:", size_value)
        metadata_layout.addRow("NSFW:", nsfw_value)
        metadata_layout.addRow("Creator:", creator_value)
        metadata_layout.addRow("Version:", version_value)
        
        left_layout.addWidget(description_group)
        left_layout.addWidget(tags_group)
        left_layout.addWidget(metadata_group)
        left_layout.addStretch()
        
        # Right side - image viewer
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.image_viewer = ImageViewer(self.theme)
        
        right_layout.addWidget(self.image_viewer)
        
        # Add panels to splitter
        content_splitter.addWidget(left_panel)
        content_splitter.addWidget(right_panel)
        content_splitter.setStretchFactor(0, 1)
        content_splitter.setStretchFactor(1, 2)
        
        layout.addWidget(content_splitter)
        
        # Buttons
        button_layout = QHBoxLayout()
        open_folder_btn = QPushButton("Open Folder")
        open_folder_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme['accent']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {self.theme['accent_hover']};
            }}
        """)
        open_folder_btn.clicked.connect(self.open_model_folder)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme['text_tertiary']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {self.theme['text_secondary']};
            }}
        """)
        close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(open_folder_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Load images
        self.load_images()
    
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
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.show_message(f"'{text}' copied to clipboard")
    
    def show_message(self, message):
        """Show a temporary message in the status bar"""
        if self.parent and hasattr(self.parent, "status_bar"):
            self.parent.status_bar.showMessage(message, 3000)
    
    def get_model_folder_path(self):
        """Get the model folder path"""
        model_type = self.model_data.get("type", "Other")
        base_model = self.model_data.get("base_model", "unknown")
        name = self.model_data.get("name", "")
        
        if not name:
            return None
            
        # Sanitize model name for folder name
        safe_name = re.sub(r'[^A-Za-z0-9_.-]', '_', name)
        
        # Get ComfyUI path from parent
        if not self.parent or not hasattr(self.parent, "config"):
            return None
            
        comfy_path = Path(self.parent.config.get("comfy_path", ""))
        if not comfy_path.exists():
            return None
            
        # Determine model folder
        from src.constants import MODEL_TYPES
        model_type_folder = MODEL_TYPES.get(model_type, MODEL_TYPES["Other"])
        
        return comfy_path / model_type_folder / base_model / safe_name
    
    def open_model_folder(self):
        """Open the model folder in file explorer"""
        folder_path = self.get_model_folder_path()
        if folder_path and folder_path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder_path)))
        else:
            QMessageBox.warning(self, "Error", "Model folder not found")
    
    def load_images(self):
        """Load images for the model"""
        folder_path = self.get_model_folder_path()
        if not folder_path:
            return
            
        images_folder = folder_path / "images"
        if not images_folder.exists():
            return
            
        # Load images from the folder
        images = []
        for img_file in images_folder.glob("*"):
            if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp', '.mp4', '.webm', '.avi', '.mov']:
                # Try to load metadata from the model's metadata.json
                metadata_path = folder_path / "metadata.json"
                if metadata_path.exists():
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            import json
                            metadata = json.load(f)
                            
                        # Find matching image in metadata
                        if "images" in metadata:
                            for img_data in metadata["images"]:
                                if "local_path" in img_data and Path(img_data["local_path"]).name == img_file.name:
                                    images.append(img_data)
                                    break
                            else:
                                # If not found, add basic info
                                images.append({
                                    "local_path": str(img_file),
                                    "meta": {}
                                })
                        else:
                            # No images in metadata, add basic info
                            images.append({
                                "local_path": str(img_file),
                                "meta": {}
                            })
                    except Exception:
                        # If metadata loading fails, add basic info
                        images.append({
                            "local_path": str(img_file),
                            "meta": {}
                        })
                else:
                    # No metadata file, add basic info
                    images.append({
                        "local_path": str(img_file),
                        "meta": {}
                    })
        
        # Set images in the viewer
        self.image_viewer.set_images(images)