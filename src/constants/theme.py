
"""
Constants for the application theme
"""

# Theme colors
DARK_THEME = {
    "primary": "#121212",          # Background
    "secondary": "#1E1E1E",        # Cards
    "accent": "#BB86FC",           # Interactive elements
    "accent_hover": "#A66DF0",     # Interactive elements hover
    "text": "#FFFFFF",             # Primary text
    "text_secondary": "#B3B3B3",   # Secondary text 
    "text_tertiary": "#8E8E8E",    # Tertiary text
    "success": "#4CAF50",          # Success status
    "warning": "#FFC107",          # Warning status
    "danger": "#F44336",           # Error/danger status
    "danger_hover": "#D32F2F",     # Error/danger hover
    "border": "#303030",           # Border color
    "border_hover": "#505050",     # Border hover color
    "input_bg": "#252525",         # Input background
    "card": "#1E1E1E",             # Card background
    "card_hover": "#252525",       # Card hover background
    "shadow": "#000000AA",         # Shadow color
}

LIGHT_THEME = {
    "primary": "#FAFAFA",          # Background
    "secondary": "#F0F0F0",        # Cards
    "accent": "#6200EE",           # Interactive elements
    "accent_hover": "#3700B3",     # Interactive elements hover
    "text": "#121212",             # Primary text
    "text_secondary": "#555555",   # Secondary text
    "text_tertiary": "#777777",    # Tertiary text
    "success": "#43A047",          # Success status
    "warning": "#FB8C00",          # Warning status
    "danger": "#E53935",           # Error/danger status
    "danger_hover": "#C62828",     # Error/danger hover
    "border": "#DDDDDD",           # Border color
    "border_hover": "#AAAAAA",     # Border hover color
    "input_bg": "#FFFFFF",         # Input background
    "card": "#FFFFFF",             # Card background
    "card_hover": "#F5F5F5",       # Card hover background
    "shadow": "#00000044",         # Shadow color
}

# Get theme based on name
def get_theme(name):
    """Get theme by name"""
    if name.lower() == "dark":
        return DARK_THEME
    else:
        return LIGHT_THEME
