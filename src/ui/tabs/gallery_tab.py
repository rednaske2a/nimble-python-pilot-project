from typing import Dict, List, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout, QDialog
)
from PySide6.QtCore import Qt

from src.ui.components.filter_panel import FilterPanel
from src.ui.components.model_card import ModelCard
from src.ui.components.storage_info_widget import StorageInfoWidget
from src.ui.dialogs.model_detail_dialog import ModelDetailDialog

class GalleryTab(QWidget):
    """Gallery tab for browsing and managing models"""
    
    def __init__(self, theme: Dict, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.parent = parent
        self.filter_status_text = ""
        self.storage_info_widget = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QHBoxLayout(self)
        
        # Left panel - filters
        left_panel = QWidget()
        left_panel.setMinimumWidth(250)
        left_panel.setMaximumWidth(300)
        
        # Create filter panel
        self.filter_panel = FilterPanel(self.theme)
        self.filter_panel.filter_changed.connect(self.apply_filters)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(self.filter_panel)
        
        # Right panel - gallery
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Top section with gallery title and storage info
        top_section = QHBoxLayout()
        
        # Gallery title
        gallery_title = QLabel("Model Gallery")
        gallery_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {self.theme['text']};")
        top_section.addWidget(gallery_title)
        
        # Filter status
        self.filter_status = QLabel(self.filter_status_text)
        self.filter_status.setStyleSheet(f"color: {self.theme['text_secondary']};")
        top_section.addWidget(self.filter_status)
        
        top_section.addStretch()
        
        # Compact storage info
        storage_info = QPushButton("Storage Info")
        storage_info.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme['accent']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {self.theme['accent_hover']};
            }}
        """)
        storage_info.clicked.connect(self.show_storage_dialog)
        top_section.addWidget(storage_info)
        
        right_layout.addLayout(top_section)
        
        # Model gallery scroll area
        self.gallery_scroll = QScrollArea()
        self.gallery_scroll.setWidgetResizable(True)
        self.gallery_scroll.setStyleSheet("background-color: transparent; border: none;")
        
        self.gallery_widget = QWidget()
        self.gallery_layout = QGridLayout(self.gallery_widget)
        self.gallery_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.gallery_layout.setContentsMargins(0, 0, 0, 0)
        self.gallery_layout.setSpacing(15)
        
        self.gallery_scroll.setWidget(self.gallery_widget)
        right_layout.addWidget(self.gallery_scroll)
        
        # Add panels to layout
        layout.addWidget(left_panel)
        layout.addWidget(right_panel)
        
        # Create storage info widget (not added to layout)
        self.storage_info_widget = StorageInfoWidget(self.theme)
    
    def set_theme(self, theme):
        """Update the theme"""
        self.theme = theme
        
        # Update UI styles
        self.filter_status.setStyleSheet(f"color: {self.theme['text_secondary']};")
        
        # Update child widgets
        self.filter_panel.set_theme(self.theme)
        self.storage_info_widget.set_theme(self.theme)
        
        # Update model cards
        self.refresh_gallery()
    
    def apply_filters(self, filters):
        """Apply filters to the gallery"""
        if self.parent and hasattr(self.parent, "models_db"):
            filtered_models = list(self.parent.models_db.models.values())
            
            # Type filter
            if filters["type"] != "all":
                filtered_models = [m for m in filtered_models if m.get("type") == filters["type"]]
            
            # Base model filter
            if filters["base_model"] != "all":
                filtered_models = [m for m in filtered_models if m.get("base_model") == filters["base_model"]]
            
            # Favorite filter
            if filters["favorite"]:
                filtered_models = [m for m in filtered_models if m.get("favorite", False)]
            
            # NSFW filter
            if filters["nsfw"] == "hide":
                filtered_models = [m for m in filtered_models if not m.get("nsfw", False)]
            elif filters["nsfw"] == "only":
                filtered_models = [m for m in filtered_models if m.get("nsfw", False)]
            
            # Search filter
            if filters["search"]:
                search_term = filters["search"].lower()
                filtered_models = [
                    m for m in filtered_models if
                    search_term in m.get("name", "").lower() or
                    search_term in m.get("creator", "").lower() or
                    any(search_term in tag.lower() for tag in m.get("tags", []))
                ]
            
            # Sort
            if filters["sort"] == "date":
                filtered_models.sort(key=lambda m: m.get("download_date", ""), reverse=True)
            elif filters["sort"] == "name":
                filtered_models.sort(key=lambda m: m.get("name", "").lower())
            elif filters["sort"] == "size":
                filtered_models.sort(key=lambda m: m.get("size", 0), reverse=True)
            elif filters["sort"] == "type":
                filtered_models.sort(key=lambda m: m.get("type", ""))
            
            # Update filter status
            filter_parts = []
            if filters["type"] != "all":
                filter_parts.append(f"Type: {filters['type']}")
            if filters["base_model"] != "all":
                filter_parts.append(f"Base: {filters['base_model']}")
            if filters["favorite"]:
                filter_parts.append("Favorites only")
            if filters["nsfw"] != "all":
                filter_parts.append(f"NSFW: {'Hidden' if filters['nsfw'] == 'hide' else 'Only'}")
            if filters["search"]:
                filter_parts.append(f"Search: '{filters['search']}'")
                
            if filter_parts:
                self.filter_status_text = f"Filters: {' | '.join(filter_parts)}"
            else:
                self.filter_status_text = ""
                
            self.filter_status.setText(self.filter_status_text)
            
            # Display models
            self.display_models(filtered_models)
    
    def display_models(self, models):
        """Display models in the gallery grid"""
        # Clear existing items
        while self.gallery_layout.count():
            item = self.gallery_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get number of columns from config
        columns = 4
        if self.parent and hasattr(self.parent, "config"):
            columns = self.parent.config.get("gallery_columns", 4)
        
        # Add models to grid
        row, col = 0, 0
        for model in models:
            card = ModelCard(model, self.theme)
            card.clicked.connect(self.show_model_details)
            card.delete_requested.connect(self.delete_model)
            card.update_requested.connect(self.update_model)
            card.favorite_toggled.connect(self.toggle_favorite)
            
            self.gallery_layout.addWidget(card, row, col)
            
            col += 1
            if col >= columns:
                col = 0
                row += 1
        
        # Add empty message if no models
        if not models:
            empty_label = QLabel("No models found matching your filters.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet(f"""
                color: {self.theme['text_tertiary']};
                font-size: 16px;
                padding: 40px;
            """)
            self.gallery_layout.addWidget(empty_label, 0, 0, 1, columns)
    
    def refresh_gallery(self):
        """Refresh the gallery"""
        # Apply current filters to refresh display
        if hasattr(self, 'filter_panel'):
            self.apply_filters(self.filter_panel.get_filters())
    
    def show_model_details(self, model_data):
        """Show model details dialog"""
        dialog = ModelDetailDialog(model_data, self.theme, self.parent)
        dialog.exec_()
    
    def delete_model(self, model_data):
        """Delete a model"""
        if self.parent and hasattr(self.parent, "models_db"):
            parent = self.parent
            model_id = model_data.get("id")
            
            if model_id and parent.models_db.remove_model(model_id):
                parent.models_db.save()
                self.refresh_gallery()
                
                if hasattr(parent, "status_bar"):
                    parent.status_bar.showMessage(f"Model '{model_data.get('name', 'Unknown')}' removed from database", 3000)
    
    def update_model(self, model_data):
        """Check for model updates"""
        # Not implemented yet
        if self.parent and hasattr(self.parent, "status_bar"):
            self.parent.status_bar.showMessage(f"Update check not implemented yet", 3000)
    
    def toggle_favorite(self, model_data, is_favorite):
        """Toggle favorite status for a model"""
        if self.parent and hasattr(self.parent, "models_db"):
            parent = self.parent
            model_id = model_data.get("id")
            
            if model_id:
                parent.models_db.update_model_field(model_id, "favorite", is_favorite)
                parent.models_db.save()
                
                status = "added to" if is_favorite else "removed from"
                if hasattr(parent, "status_bar"):
                    parent.status_bar.showMessage(f"'{model_data.get('name', 'Unknown')}' {status} favorites", 3000)
    
    def show_storage_dialog(self):
        """Show storage usage dialog"""
        if self.storage_info_widget:
            dialog = QDialog(self)
            dialog.setWindowTitle("Storage Usage")
            dialog.setMinimumSize(500, 600)
            
            layout = QVBoxLayout(dialog)
            layout.addWidget(self.storage_info_widget)
            
            close_btn = QPushButton("Close")
            close_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.theme['accent']};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                }}
                QPushButton:hover {{
                    background-color: {self.theme['accent_hover']};
                }}
            """)
            close_btn.clicked.connect(dialog.accept)
            
            layout.addWidget(close_btn)
            
            # Refresh storage analysis
            if self.parent and hasattr(self.parent, "storage_manager"):
                total, free, categories = self.parent.storage_manager.get_storage_usage()
                self.storage_info_widget.update_usage(total, free, categories)
            
            dialog.exec_()