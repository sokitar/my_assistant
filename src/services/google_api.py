"""
Google API integration service for Gmail and Google Calendar.
Handles authentication and API operations for both services.
"""
import base64
import os
import pickle
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional, Tuple, Any

import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger("google_api")

# Define scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]

class GoogleAPIService:
    """Service for interacting with Google APIs (Gmail and Calendar)."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Initialize the Google API service.
        
        Args:
            client_id: Google OAuth client ID
            client_secret: Google OAuth client secret
            redirect_uri: OAuth redirect URI
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.credentials = None
        self.gmail_service = None
        self.calendar_service = None
        
        # Create token directory if it doesn't exist
        os.makedirs("tokens", exist_ok=True)
    
    def authenticate(self) -> Tuple[bool, Optional[str]]:
        """
        Authenticate with Google APIs.
        
        Returns:
            Tuple of (success status, auth URL if needed)
        """
        creds = None
        token_path = "tokens/google_token.pickle"
        
        # Load credentials from token file if it exists
        if os.path.exists(token_path):
            with open(token_path, "rb") as token:
                creds = pickle.load(token)
        
        # Check if credentials are valid
        if creds and creds.valid:
            self.credentials = creds
            self._build_services()
            return True, None
        
        # Refresh credentials if expired
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                self.credentials = creds
                self._build_services()
                
                # Save refreshed credentials
                with open(token_path, "wb") as token:
                    pickle.dump(creds, token)
                
                return True, None
            except Exception as e:
                logger.error(f"Error refreshing credentials: {e}")
        
        # Create new authorization flow
        flow = InstalledAppFlow.from_client_config(
            {
                "installed": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uris": [self.redirect_uri],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            SCOPES,
        )
        
        # Generate authorization URL
        auth_url, _ = flow.authorization_url(
            access_type="offline", include_granted_scopes="true", prompt="consent"
        )
        
        return False, auth_url
    
    def handle_auth_callback(self, auth_code: str) -> bool:
        """
        Handle OAuth callback and save credentials.
        
        Args:
            auth_code: Authorization code from OAuth callback
            
        Returns:
            Success status
        """
        try:
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uris": [self.redirect_uri],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                },
                SCOPES,
            )
            
            # Exchange auth code for credentials
            flow.fetch_token(code=auth_code)
            self.credentials = flow.credentials
            
            # Save credentials
            with open("tokens/google_token.pickle", "wb") as token:
                pickle.dump(self.credentials, token)
            
            # Build API services
            self._build_services()
            
            return True
        except Exception as e:
            logger.error(f"Error handling auth callback: {e}")
            return False
    
    def _build_services(self) -> None:
        """Build Gmail and Calendar API services."""
        if not self.credentials:
            logger.error("No credentials available to build services")
            return
        
        try:
            # Build Gmail service
            self.gmail_service = build(
                "gmail", "v1", credentials=self.credentials, cache_discovery=False
            )
            
            # Build Calendar service
            self.calendar_service = build(
                "calendar", "v3", credentials=self.credentials, cache_discovery=False
            )
            
            logger.info("Successfully built Gmail and Calendar services")
        except Exception as e:
            logger.error(f"Error building services: {e}")
    
    def is_authenticated(self) -> bool:
        """
        Check if the user is authenticated.
        
        Returns:
            Authentication status
        """
        return (
            self.credentials is not None
            and self.gmail_service is not None
            and self.calendar_service is not None
        )
    
    # Gmail API methods
    
    def send_email(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        """
        Send an email using Gmail API.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            html: Whether the body is HTML
            
        Returns:
            Success status
        """
        if not self.is_authenticated():
            logger.error("Not authenticated to send email")
            return False
        
        try:
            # Create message
            message = MIMEMultipart()
            message["to"] = to
            message["subject"] = subject
            
            # Add body
            content_type = "html" if html else "plain"
            message.attach(MIMEText(body, content_type))
            
            # Encode message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send message
            self.gmail_service.users().messages().send(
                userId="me", body={"raw": encoded_message}
            ).execute()
            
            logger.info(f"Email sent to {to}")
            return True
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def get_recent_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent emails from Gmail.
        
        Args:
            max_results: Maximum number of emails to retrieve
            
        Returns:
            List of email data
        """
        if not self.is_authenticated():
            logger.error("Not authenticated to get emails")
            return []
        
        try:
            # Get messages
            results = self.gmail_service.users().messages().list(
                userId="me", maxResults=max_results
            ).execute()
            
            messages = results.get("messages", [])
            emails = []
            
            # Get message details
            for message in messages:
                msg = self.gmail_service.users().messages().get(
                    userId="me", id=message["id"]
                ).execute()
                
                # Extract headers
                headers = msg["payload"]["headers"]
                subject = next(
                    (h["value"] for h in headers if h["name"].lower() == "subject"),
                    "(No subject)",
                )
                sender = next(
                    (h["value"] for h in headers if h["name"].lower() == "from"),
                    "(Unknown sender)",
                )
                date = next(
                    (h["value"] for h in headers if h["name"].lower() == "date"),
                    "(Unknown date)",
                )
                
                # Extract snippet
                snippet = msg.get("snippet", "")
                
                emails.append({
                    "id": message["id"],
                    "subject": subject,
                    "sender": sender,
                    "date": date,
                    "snippet": snippet,
                })
            
            return emails
        except Exception as e:
            logger.error(f"Error getting emails: {e}")
            return []
    
    # Calendar API methods
    
    def get_upcoming_events(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get upcoming calendar events.
        
        Args:
            max_results: Maximum number of events to retrieve
            
        Returns:
            List of event data
        """
        if not self.is_authenticated():
            logger.error("Not authenticated to get events")
            return []
        
        try:
            # Get current time
            now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
            
            # Get events
            events_result = self.calendar_service.events().list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            ).execute()
            
            events = events_result.get("items", [])
            formatted_events = []
            
            # Format events
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                
                formatted_events.append({
                    "id": event["id"],
                    "summary": event.get("summary", "(No title)"),
                    "start": start,
                    "location": event.get("location", ""),
                    "description": event.get("description", ""),
                })
            
            return formatted_events
        except Exception as e:
            logger.error(f"Error getting events: {e}")
            return []
    
    def create_calendar_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: str = "",
        location: str = "",
        timezone: str = "UTC",
    ) -> bool:
        """
        Create a calendar event.
        
        Args:
            summary: Event title
            start_time: Event start time
            end_time: Event end time
            description: Event description
            location: Event location
            timezone: Event timezone
            
        Returns:
            Success status
        """
        if not self.is_authenticated():
            logger.error("Not authenticated to create event")
            return False
        
        try:
            # Format times
            tz = pytz.timezone(timezone)
            start_time = start_time.astimezone(tz)
            end_time = end_time.astimezone(tz)
            
            # Create event
            event = {
                "summary": summary,
                "location": location,
                "description": description,
                "start": {
                    "dateTime": start_time.isoformat(),
                    "timeZone": timezone,
                },
                "end": {
                    "dateTime": end_time.isoformat(),
                    "timeZone": timezone,
                },
            }
            
            # Add event to calendar
            self.calendar_service.events().insert(
                calendarId="primary", body=event
            ).execute()
            
            logger.info(f"Event created: {summary}")
            return True
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            return False
