"""
Main application entry point for the Gmail and Google Calendar Agent.
This module initializes and runs the Gradio web interface.
"""
import os
import gradio as gr
from dotenv import load_dotenv

from src.config import AppConfig
from src.ui.interface import create_interface
from src.utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger()

def main():
    """Initialize and run the Gradio web interface."""
    logger.info("Starting Gmail and Google Calendar Agent")
    
    # Load configuration
    config = AppConfig()
    
    # Create and launch Gradio interface
    demo = create_interface(config)
    
    # Launch the app
    demo.launch(
        server_name=config.app_host,
        server_port=config.app_port,
        share=False,
        favicon_path="assets/favicon.ico"
    )

if __name__ == "__main__":
    main()
