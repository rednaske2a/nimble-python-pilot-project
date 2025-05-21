"""
Application-wide constants
"""

# Default configuration
DEFAULT_CONFIG = {
    "api_key": "",
    "comfy_path": "",
    "top_image_count": 500,
    "fetch_batch_size": 200,
    "download_threads": 5,
    "auto_open_html": False,
    "download_images": True,
    "download_model": True,
    "create_html": False,
    "download_nsfw": True,
    "auto_organize": True,
    "theme": "dark",
    "gallery_columns": 4,
    "favorite_tags": [],
    "log_level": "info",
    "auto_check_updates": True,
    "default_sort": "date",
    "default_filter": "all"
}

# Application themes
APP_THEMES = {
    "dark": {
        "name": "Dark",
        "window": "#2d2d2d",
        "background": "#1e1e1e",
        "card": "#2d2d2d",
        "card_hover": "#333333",
        "text": "#e0e0e0",
        "text_secondary": "#aaaaaa",
        "text_tertiary": "#888888",
        "accent": "#2a5699",
        "accent_hover": "#3a67a9",
        "accent_pressed": "#1a4689",
        "danger": "#992a2a",
        "danger_hover": "#a93a3a",
        "success": "#2a9956",
        "success_hover": "#3aa967",
        "warning": "#996f2a",
        "warning_hover": "#a97f3a",
        "border": "#3d3d3d",
        "border_hover": "#5d5d5d",
        "input_bg": "#333333",
        "input_border": "#555555",
        "shadow": "#000000"
    },
    "light": {
        "name": "Light",
        "window": "#f5f5f5",
        "background": "#ffffff",
        "card": "#ffffff",
        "card_hover": "#f0f0f0",
        "text": "#333333",
        "text_secondary": "#555555",
        "text_tertiary": "#777777",
        "accent": "#2a5699",
        "accent_hover": "#3a67a9",
        "accent_pressed": "#1a4689",
        "danger": "#d32f2f",
        "danger_hover": "#e33e3e",
        "success": "#388e3c",
        "success_hover": "#4caf50",
        "warning": "#f57c00",
        "warning_hover": "#ff9800",
        "border": "#dddddd",
        "border_hover": "#bbbbbb",
        "input_bg": "#ffffff",
        "input_border": "#cccccc",
        "shadow": "#00000033"
    },
    "nord": {
        "name": "Nord",
        "window": "#2e3440",
        "background": "#3b4252",
        "card": "#434c5e",
        "card_hover": "#4c566a",
        "text": "#eceff4",
        "text_secondary": "#e5e9f0",
        "text_tertiary": "#d8dee9",
        "accent": "#5e81ac",
        "accent_hover": "#81a1c1",
        "accent_pressed": "#5077a5",
        "danger": "#bf616a",
        "danger_hover": "#d07983",
        "success": "#a3be8c",
        "success_hover": "#b9d0a5",
        "warning": "#ebcb8b",
        "warning_hover": "#f0d399",
        "border": "#4c566a",
        "border_hover": "#5e6779",
        "input_bg": "#3b4252",
        "input_border": "#4c566a",
        "shadow": "#00000066"
    },
    "dracula": {
        "name": "Dracula",
        "window": "#282a36",
        "background": "#282a36",
        "card": "#44475a",
        "card_hover": "#4d5066",
        "text": "#f8f8f2",
        "text_secondary": "#f8f8f2cc",
        "text_tertiary": "#f8f8f299",
        "accent": "#6272a4",
        "accent_hover": "#7282b4",
        "accent_pressed": "#5262a4",
        "danger": "#ff5555",
        "danger_hover": "#ff6e6e",
        "success": "#50fa7b",
        "success_hover": "#6dfa8e",
        "warning": "#ffb86c",
        "warning_hover": "#ffc285",
        "border": "#44475a",
        "border_hover": "#6272a4",
        "input_bg": "#282a36",
        "input_border": "#44475a",
        "shadow": "#00000066"
    }
}

# Model types and their folder paths
MODEL_TYPES = {
    "LORA": "models/loras",
    "Checkpoint": "models/checkpoints",
    "TextualInversion": "models/embeddings",
    "Hypernetwork": "models/hypernetworks",
    "AestheticGradient": "models/aestheticgradients",
    "Controlnet": "models/controlnet",
    "Poses": "models/poses",
    "Wildcards": "wildcards",
    "Workflows": "workflows",
    "Other": "models/other"
}

# Base models
BASE_MODELS = [
    "SD 1.5",
    "SDXL",
    "SD 2.0",
    "SD 2.1",
    "Pony",
    "Stable Cascade",
    "PixArt Σ",
    "Other"
]

# Status icons
STATUS_ICONS = {
    "success": "✓",
    "error": "✗",
    "warning": "⚠",
    "info": "ℹ",
    "download": "↓",
    "queue": "⋯",
    "debug": "🔍"
}

# Download status
DOWNLOAD_STATUS = {
    "QUEUED": "queued",
    "DOWNLOADING": "downloading",
    "COMPLETED": "completed",
    "FAILED": "failed",
    "CANCELED": "canceled"
}