from typing import Dict

from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QTextCursor
import time

from src.constants import STATUS_ICONS

class LogWidget(QTextEdit):
    """Widget for displaying log messages"""
    
    def __init__(self, theme: Dict, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.setReadOnly(True)
        self.apply_theme()
    
    def apply_theme(self):
        """Apply the current theme"""
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.theme['background']};
                color: {self.theme['text']};
                border: 1px solid {self.theme['border']};
                border-radius: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }}
        """)
    
    def set_theme(self, theme):
        """Update the theme"""
        self.theme = theme
        self.apply_theme()
    
    def add_log(self, message, status="info"):
        """Add a log message with status icon"""
        timestamp = time.strftime("%H:%M:%S")
        icon = STATUS_ICONS.get(status, "")
        
        # Set color based on status
        if status == "error":
            color = "#ff5555"
        elif status == "warning":
            color = "#ffaa00"
        elif status == "success":
            color = "#55ff55"
        elif status == "download":
            color = "#5555ff"
        elif status == "queue":
            color = "#aa55ff"
        else:
            color = self.theme['text']
            
        self.append(f"<span style='color:{self.theme['text_tertiary']};'>[{timestamp}]</span> <span style='color:{color};'>{icon} {message}</span>")
        
        # Scroll to bottom
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)