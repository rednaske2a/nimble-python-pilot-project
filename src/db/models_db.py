import json
from pathlib import Path
from typing import Dict, Any, List

from src.models.model_info import ModelInfo
from src.utils.logger import get_logger

logger = get_logger()

class ModelsDatabase:
    """
    Database for managing model information
    """
    def __init__(self):
        self.db_path = Path.home() / ".civitai_models_db.json"
        self.models = self.load()
    
    def load(self) -> Dict[str, Dict[str, Any]]:
        """Load models from database file"""
        models = {}
        
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    models = json.load(f)
                
                logger.info(f"Loaded {len(models)} models from database")
            except Exception as e:
                logger.error(f"Error loading models database: {str(e)}")
        else:
            logger.info("Models database file not found, starting with empty database")
        
        return models
    
    def save(self) -> bool:
        """Save models to database file"""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.models, f, indent=2)
            
            logger.info("Models database saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving models database: {str(e)}")
            return False
    
    def get_model(self, model_id: str) -> Dict[str, Any]:
        """Get a model by ID"""
        return self.models.get(model_id, {})
    
    def add_model(self, model_info: ModelInfo) -> None:
        """Add or update a model in the database"""
        model_id = str(model_info.id)
        self.models[model_id] = model_info.to_dict()
    
    def remove_model(self, model_id: str) -> bool:
        """Remove a model from the database"""
        if model_id in self.models:
            del self.models[model_id]
            return True
        return False
    
    def list_models(self) -> List[Dict[str, Any]]:
        """Get all models as a list"""
        return list(self.models.values())
    
    def update_model_field(self, model_id: str, field: str, value: Any) -> bool:
        """Update a specific field in a model"""
        if model_id in self.models:
            self.models[model_id][field] = value
            return True
        return False
    
    def clear(self) -> None:
        """Clear all models from the database"""
        self.models = {}