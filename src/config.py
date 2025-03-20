"""
Configuration module for the Gmail and Google Calendar Agent.
Handles loading and validating environment variables and application settings.
"""
import os
from dataclasses import dataclass
from typing import Optional

class MissingConfigError(Exception):
    """Exception raised when a required configuration value is missing."""
    pass

@dataclass
class AppConfig:
    """Application configuration container."""
    # OpenAI API settings
    openai_api_key: str
    
    # Google API settings
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    
    # Application settings
    app_host: str
    app_port: int
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        # OpenAI API settings
        self.openai_api_key = self._get_env("OPENAI_API_KEY")
        
        # Google API settings
        self.google_client_id = self._get_env("GOOGLE_CLIENT_ID")
        self.google_client_secret = self._get_env("GOOGLE_CLIENT_SECRET")
        self.google_redirect_uri = self._get_env("GOOGLE_REDIRECT_URI")
        
        # Application settings
        self.app_host = self._get_env("APP_HOST", "localhost")
        self.app_port = int(self._get_env("APP_PORT", "8000"))
    
    def _get_env(self, key: str, default: Optional[str] = None) -> str:
        """
        Get environment variable or raise exception if not found and no default.
        
        Args:
            key: Environment variable name
            default: Optional default value
            
        Returns:
            The environment variable value
            
        Raises:
            MissingConfigError: If the environment variable is not set and no default is provided
        """
        value = os.environ.get(key, default)
        if value is None:
            raise MissingConfigError(f"Missing required environment variable: {key}")
        return value
