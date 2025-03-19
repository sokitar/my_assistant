"""
General helper utilities for the personal assistant.
"""
import os
import json
import logging
import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("assistant.log")
    ]
)
logger = logging.getLogger("assistant")


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load and parse a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the parsed JSON data
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        return {}


def save_json_file(data: Dict[str, Any], file_path: str) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data: Dictionary to save
        file_path: Path to save the JSON file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {e}")
        return False


def format_datetime(dt: datetime.datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object to a string.
    
    Args:
        dt: Datetime object to format
        format_str: Format string
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime.datetime]:
    """
    Parse a datetime string to a datetime object.
    
    Args:
        dt_str: Datetime string to parse
        format_str: Format string
        
    Returns:
        Datetime object or None if parsing fails
    """
    try:
        return datetime.datetime.strptime(dt_str, format_str)
    except Exception as e:
        logger.error(f"Error parsing datetime {dt_str}: {e}")
        return None


def get_env_var(var_name: str, default: Any = None) -> Any:
    """
    Get an environment variable with a default value.
    
    Args:
        var_name: Name of the environment variable
        default: Default value if the variable is not set
        
    Returns:
        Value of the environment variable or the default value
    """
    return os.environ.get(var_name, default)


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def create_directory_if_not_exists(directory_path: str) -> bool:
    """
    Create a directory if it doesn't exist.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory_path}: {e}")
        return False


def load_user_preferences(user_id: str) -> Dict[str, Any]:
    """
    Load user preferences from a JSON file.
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary containing user preferences
    """
    prefs_dir = "user_data"
    create_directory_if_not_exists(prefs_dir)
    prefs_file = os.path.join(prefs_dir, f"{user_id}_preferences.json")
    
    if not os.path.exists(prefs_file):
        # Create default preferences
        default_prefs = {
            "user_id": user_id,
            "created_at": format_datetime(datetime.datetime.now()),
            "theme": "light",
            "notifications_enabled": True,
            "email_signature": "",
            "preferred_greeting": "Hello",
            "creativity_level": "balanced"
        }
        save_json_file(default_prefs, prefs_file)
        return default_prefs
    
    return load_json_file(prefs_file)


def update_user_preferences(user_id: str, updates: Dict[str, Any]) -> bool:
    """
    Update user preferences.
    
    Args:
        user_id: User ID
        updates: Dictionary containing preference updates
        
    Returns:
        True if successful, False otherwise
    """
    prefs = load_user_preferences(user_id)
    prefs.update(updates)
    prefs["updated_at"] = format_datetime(datetime.datetime.now())
    
    prefs_dir = "user_data"
    prefs_file = os.path.join(prefs_dir, f"{user_id}_preferences.json")
    return save_json_file(prefs, prefs_file)
