import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

def setup_logger(log_level: str = "info") -> logging.Logger:
    """
    Set up application logger
    
    Args:
        log_level: Logging level (debug, info, warning, error)
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("civitai_model_manager")
    
    # Set level based on configuration
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR
    }
    logger.setLevel(level_map.get(log_level.lower(), logging.INFO))
    
    # Create handlers if not already configured
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)
        
        # File handler
        try:
            log_path = Path.home() / ".civitai_model_manager_logs"
            log_path.mkdir(exist_ok=True)
            
            log_file = log_path / f"log_{datetime.now().strftime('%Y%m%d')}.txt"
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not set up file logging: {str(e)}")
    
    return logger

def get_logger() -> logging.Logger:
    """Get the application logger"""
    logger = logging.getLogger("civitai_model_manager")
    
    # If logger not set up yet, set up with defaults
    if not logger.handlers:
        logger = setup_logger()
    
    return logger