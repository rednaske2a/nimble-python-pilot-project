from typing import Dict

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect

from pathlib import Path

from src.utils.formatting import format_size

class ModelCard(QWidget):
    """Widget for displaying a model card in the gallery"""
    
    clicked = Signal(dict)
    delete_requested = Signal(dict)
    update_requested = Signal(dict)
    favorite_toggled = Signal(dict, bool)
    
    def __init__(self, model_data: Dict, theme: Dict, parent=None):
        super().__init__(parent)
        self.model_data = model_data
        self.theme = theme
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Card frame
        self.setObjectName("modelCard")
        self.apply_theme()
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(self.theme["shadow"]))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        # Thumbnail container with overlay for NSFW
        thumbnail_container = QWidget()
        thumbnail_container.setFixedSize(200, 200)
        thumbnail_layout = QVBoxLayout(thumbnail_container)
        thumbnail_layout.setContentsMargins(0, 0, 0, 0)
        
        # Thumbnail
        thumbnail_path = self.model_data.get("thumbnail", "")
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(200, 200)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.theme["background"]}; 
                color: {self.theme["text_secondary"]}; 
                border-radius: 8px;
                border: 1px solid {self.theme["border"]};
            }}
        """)
        
        if thumbnail_path and Path(thumbnail_path).exists():
            pixmap = QPixmap(thumbnail_path)
            self.thumbnail_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # Default thumbnail
            self.thumbnail_label.setText("No Image")
            
        thumbnail_layout.addWidget(self.thumbnail_label)
        
        # NSFW overlay if needed
        if self.model_data.get("nsfw", False):
            nsfw_overlay = QLabel("NSFW")
            nsfw_overlay.setAlignment(Qt.AlignCenter)
            nsfw_overlay.setStyleSheet("""
                QLabel {
                    background-color: rgba(255, 0, 0, 0.7);
                    color: white;
                    font-weight: bold;
                    border-radius: 4px;
                    padding: 2px 6px;
                }
            """)
            nsfw_overlay.setFixedSize(60, 24)
            
            # Position in top-right corner
            nsfw_overlay.setParent(thumbnail_container)
            nsfw_overlay.move(thumbnail_container.width() - nsfw_overlay.width() - 5, 5)
            nsfw_overlay.show()
        
        layout.addWidget(thumbnail_container, alignment=Qt.AlignCenter)
        
        # Favorite button
        favorite_layout = QHBoxLayout()
        favorite_layout.setContentsMargins(0, 0, 0, 0)
        
        self.favorite_btn = QPushButton()
        self.favorite_btn.setCheckable(True)
        self.favorite_btn.setChecked(self.model_data.get("favorite", False))
        self.update_favorite_button()
        self.favorite_btn.clicked.connect(self.toggle_favorite)
        self.favorite_btn.setFixedSize(30, 30)
        
        # Model name
        name_label = QLabel(self.model_data.get("name", "Unknown"))
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {self.theme['text']};")
        
        favorite_layout.addWidget(self.favorite_btn)
        favorite_layout.addWidget(name_label)
        favorite_layout.addStretch()
        
        layout.addLayout(favorite_layout)
        
        # Base model
        base_model = QLabel(f"Base: {self.model_data.get('base_model', 'Unknown')}")
        base_model.setAlignment(Qt.AlignCenter)
        base_model.setStyleSheet(f"font-size: 12px; color: {self.theme['text_secondary']};")
        layout.addWidget(base_model)
        
        # Type
        type_label = QLabel(self.model_data.get("type", "Unknown"))
        type_label.setAlignment(Qt.AlignCenter)
        type_label.setStyleSheet(f"font-size: 12px; color: {self.theme['text_tertiary']};")
        layout.addWidget(type_label)
        
        # Creator
        creator = self.model_data.get("creator", "Unknown")
        if creator:
            creator_label = QLabel(f"By: {creator}")
            creator_label.setAlignment(Qt.AlignCenter)
            creator_label.setStyleSheet(f"font-size: 12px; color: {self.theme['text_secondary']};")
            layout.addWidget(creator_label)
        
        # Size
        size_bytes = self.model_data.get("size", 0)
        size_str = format_size(size_bytes)
        size_label = QLabel(size_str)
        size_label.setAlignment(Qt.AlignCenter)
        size_label.setStyleSheet(f"font-size: 11px; color: {self.theme['text_tertiary']};")
        layout.addWidget(size_label)
        
        # Tags preview (first 3 tags)
        tags = self.model_data.get("tags", [])
        if tags:
            tags_preview = tags[:3]
            tags_text = ", ".join(tags_preview)
            if len(tags) > 3:
                tags_text += f" +{len(tags) - 3} more"
                
            tags_label = QLabel(tags_text)
            tags_label.setAlignment(Qt.AlignCenter)
            tags_label.setWordWrap(True)
            tags_label.setStyleSheet(f"font-size: 11px; color: {self.theme['text_tertiary']}; font-style: italic;")
            layout.addWidget(tags_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        update_btn = QPushButton("Update")
        update_btn.setToolTip("Check for updates")
        update_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme['accent']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                background-color: {self.theme['accent_hover']};
            }}
        """)
        update_btn.clicked.connect(lambda: self.update_requested.emit(self.model_data))
        
        delete_btn = QPushButton("Delete")
        delete_btn.setToolTip("Delete this model")
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme['danger']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                background-color: {self.theme['danger_hover']};
            }}
        """)
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.model_data))
        
        button_layout.addWidget(update_btn)
        button_layout.addWidget(delete_btn)
        layout.addLayout(button_layout)
        
        self.setFixedSize(240, 400)
    
    def apply_theme(self):
        """Apply the current theme to the widget"""
        self.setStyleSheet(f"""
            #modelCard {{
                background-color: {self.theme["card"]};
                border-radius: 12px;
                border: 1px solid {self.theme["border"]};
            }}
            #modelCard:hover {{
                border: 1px solid {self.theme["border_hover"]};
                background-color: {self.theme["card_hover"]};
            }}
        """)
    
    def set_theme(self, theme):
        """Update the theme"""
        self.theme = theme
        self.apply_theme()
        self.update_favorite_button()
        
        # Update child widgets
        for child in self.findChildren(QLabel):
            if "font-weight: bold" in child.styleSheet():
                child.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {self.theme['text']};")
            elif "By:" in child.text():
                child.setStyleSheet(f"font-size: 12px; color: {self.theme['text_secondary']};")
            elif "Base:" in child.text():
                child.setStyleSheet(f"font-size: 12px; color: {self.theme['text_secondary']};")
            elif "font-style: italic" in child.styleSheet():
                child.setStyleSheet(f"font-size: 11px; color: {self.theme['text_tertiary']}; font-style: italic;")
            elif child.text() in self.model_data.get("type", ""):
                child.setStyleSheet(f"font-size: 12px; color: {self.theme['text_tertiary']};")
            elif format_size(self.model_data.get("size", 0)) == child.text():
                child.setStyleSheet(f"font-size: 11px; color: {self.theme['text_tertiary']};")
            else:
                child.setStyleSheet(f"color: {self.theme['text']};")
                
        # Update thumbnail label
        self.thumbnail_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.theme["background"]}; 
                color: {self.theme["text_secondary"]}; 
                border-radius: 8px;
                border: 1px solid {self.theme["border"]};
            }}
        """)
        
        # Update buttons
        for child in self.findChildren(QPushButton):
            if child == self.favorite_btn:
                self.update_favorite_button()
            elif "Delete" in child.text():
                child.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.theme['danger']};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                    }}
                    QPushButton:hover {{
                        background-color: {self.theme['danger_hover']};
                    }}
                """)
            else:
                child.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.theme['accent']};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                    }}
                    QPushButton:hover {{
                        background-color: {self.theme['accent_hover']};
                    }}
                """)
    
    def update_favorite_button(self):
        """Update the favorite button appearance"""
        if self.favorite_btn.isChecked():
            self.favorite_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: gold;
                    font-size: 18px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    color: #ffcc00;
                }
            """)
            self.favorite_btn.setText("★")
        else:
            self.favorite_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    color: {self.theme['text_tertiary']};
                    font-size: 18px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    color: {self.theme['text_secondary']};
                }}
            """)
            self.favorite_btn.setText("☆")
    
    def toggle_favorite(self):
        """Toggle favorite status"""
        is_favorite = self.favorite_btn.isChecked()
        self.update_favorite_button()
        self.favorite_toggled.emit(self.model_data, is_favorite)
    
    def mousePressEvent(self, event):
        """Handle mouse press event"""
        self.clicked.emit(self.model_data)
        super().mousePressEvent(event)