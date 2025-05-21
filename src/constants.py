
"""
Application constants
"""

# Download status constants
DOWNLOAD_STATUS = {
    "QUEUED": "queued",
    "DOWNLOADING": "downloading",
    "COMPLETED": "completed",
    "FAILED": "failed",
    "CANCELED": "canceled"
}

# Model type to folder mapping
MODEL_TYPES = {
    "Checkpoint": "models/Stable-diffusion",
    "TextualInversion": "embeddings",
    "Hypernetwork": "models/hypernetworks",
    "LORA": "models/Lora",
    "LoCon": "models/Lora",  # LoCon is treated as LORA in ComfyUI
    "VAE": "models/VAE",
    "Controlnet": "models/controlnet",
    "Upscaler": "models/upscale_models",
    "Motionmodule": "models/motion_module",
    "Aesthetic Gradient": "embeddings",
    "Poses": "models/poses",
    "Wildcards": "wildcards",
    "Workflows": "workflows",
    "Other": "models/other"
}

# Application themes
APP_THEMES = {
    "dark": {
        "name": "Dark",
        "window": "#121212",
        "background": "#181818",
        "card": "#1E1E1E",
        "card_hover": "#2A2A2A",
        "text": "#FFFFFF",
        "text_secondary": "#B3B3B3",
        "accent": "#BB86FC",
        "accent_hover": "#C9A5FD",
        "border": "#333333",
        "border_hover": "#555555",
        "input_bg": "#2A2A2A",
        "success": "#4CAF50",
        "success_hover": "#5BBF5E",
        "warning": "#FFC107",
        "warning_hover": "#FFD257",
        "danger": "#F44336",
        "danger_hover": "#F55A4E",
        "info": "#2196F3",
        "info_hover": "#42A5F5",
        "shadow": "#00000080"
    },
    "light": {
        "name": "Light",
        "window": "#F5F5F5",
        "background": "#FFFFFF",
        "card": "#FFFFFF",
        "card_hover": "#F9F9F9",
        "text": "#212121",
        "text_secondary": "#757575",
        "accent": "#673AB7",
        "accent_hover": "#7E57C2",
        "border": "#E0E0E0",
        "border_hover": "#BDBDBD",
        "input_bg": "#F5F5F5",
        "success": "#4CAF50",
        "success_hover": "#5BBF5E",
        "warning": "#FF9800",
        "warning_hover": "#FFA726",
        "danger": "#F44336",
        "danger_hover": "#F55A4E",
        "info": "#2196F3",
        "info_hover": "#42A5F5",
        "shadow": "#00000040"
    }
}

# File extensions by type
FILE_EXTENSIONS = {
    "model": [".safetensors", ".ckpt", ".pt", ".pth"],
    "image": [".jpg", ".jpeg", ".png", ".webp", ".gif"],
    "video": [".mp4", ".webm"],
    "metadata": [".json", ".yaml", ".yml"],
}

# Model view columns
MODEL_VIEW_COLUMNS = ["Name", "Type", "Base Model", "Size", "Download Date", "Rating"]
