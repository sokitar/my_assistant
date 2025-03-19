"""
Authentication utilities for Google API services.
"""
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scopes needed for Gmail and Calendar
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose'
]

CALENDAR_SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]

# Combined scopes for a single authentication flow
ALL_SCOPES = GMAIL_SCOPES + CALENDAR_SCOPES

# Path to store token
TOKEN_PATH = Path("token.json")
CREDENTIALS_PATH = Path("credentials.json")


def get_credentials(scopes: list = None) -> Optional[Credentials]:
    """
    Get and refresh OAuth2 credentials for Google APIs.
    
    Args:
        scopes: List of API scopes to request access for
        
    Returns:
        Credentials object or None if authentication fails
    """
    if scopes is None:
        scopes = ALL_SCOPES
        
    creds = None
    
    # Load existing token if available
    if TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, scopes)
        except Exception as e:
            print(f"Error loading credentials: {e}")
    
    # If no valid credentials available, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                # If refresh fails, force re-authentication
                creds = None
        
        # If still no valid credentials, start OAuth flow
        if not creds:
            if not CREDENTIALS_PATH.exists():
                raise FileNotFoundError(
                    "credentials.json not found. Please download OAuth credentials from Google Cloud Console."
                )
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH, scopes
                )
                creds = flow.run_local_server(port=0)
                
                # Save credentials for future use
                with open(TOKEN_PATH, "w") as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Authentication error: {e}")
                return None
    
    return creds


def build_gmail_service(credentials: Credentials = None):
    """
    Build and return a Gmail API service object.
    
    Args:
        credentials: OAuth2 credentials
        
    Returns:
        Gmail API service object
    """
    if credentials is None:
        credentials = get_credentials(GMAIL_SCOPES)
    
    if credentials:
        return build('gmail', 'v1', credentials=credentials)
    return None


def build_calendar_service(credentials: Credentials = None):
    """
    Build and return a Google Calendar API service object.
    
    Args:
        credentials: OAuth2 credentials
        
    Returns:
        Calendar API service object
    """
    if credentials is None:
        credentials = get_credentials(CALENDAR_SCOPES)
    
    if credentials:
        return build('calendar', 'v3', credentials=credentials)
    return None


def get_user_info(credentials: Credentials) -> Dict[str, Any]:
    """
    Get user profile information from Google.
    
    Args:
        credentials: OAuth2 credentials
        
    Returns:
        Dictionary containing user information
    """
    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()
    return user_info
