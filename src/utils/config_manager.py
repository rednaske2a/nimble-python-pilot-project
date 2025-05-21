import json
from pathlib import Path
from typing import Dict, Any

from src.constants import DEFAULT_CONFIG

class ConfigManager:
    """
    Manager for application configuration
    """
    def __init__(self):
        self.config_path = Path.home() / ".civitai_model_manager.json"
        self.config = self.load()
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from file"""
        config = DEFAULT_CONFIG.copy()
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge loaded config with defaults to ensure all keys exist
                    config.update(loaded_config)
            except Exception as e:
                print(f"Error loading config: {str(e)}")
        
        return config
    
    def save(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {str(e)}")
            return False
    
    def get(self, key: str, default=None) -> Any:
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        self.config[key] = value
    
    def update(self, values: Dict[str, Any]) -> None:
        """Update multiple configuration values"""
        self.config.update(values)