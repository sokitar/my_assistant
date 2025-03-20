"""
OpenAI agent service for intelligent Gmail and Google Calendar interactions.
Implements agents using the OpenAI Agents SDK.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable

import openai
from openai import OpenAI
from openai_agents import Agent, Tool, AgentState

from src.services.google_api import GoogleAPIService
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger("agent_service")

class AgentService:
    """Service for AI agents that interact with Gmail and Google Calendar."""
    
    def __init__(self, api_key: str, google_service: GoogleAPIService):
        """
        Initialize the agent service.
        
        Args:
            api_key: OpenAI API key
            google_service: Google API service instance
        """
        self.api_key = api_key
        self.google_service = google_service
        self.client = OpenAI(api_key=api_key)
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """
        Create and configure the OpenAI agent.
        
        Returns:
            Configured Agent instance
        """
        # Define tools for the agent
        tools = [
            Tool(
                name="get_recent_emails",
                description="Get a list of recent emails from Gmail",
                function=self._get_recent_emails,
            ),
            Tool(
                name="send_email",
                description="Send an email using Gmail",
                function=self._send_email,
                parameters={
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email address"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body content"},
                        "html": {"type": "boolean", "description": "Whether the body is HTML"}
                    },
                    "required": ["to", "subject", "body"]
                }
            ),
            Tool(
                name="get_upcoming_events",
                description="Get upcoming events from Google Calendar",
                function=self._get_upcoming_events,
            ),
            Tool(
                name="create_calendar_event",
                description="Create a new event in Google Calendar",
                function=self._create_calendar_event,
                parameters={
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string", "description": "Event title"},
                        "start_datetime": {"type": "string", "description": "Start time in ISO format (YYYY-MM-DDTHH:MM:SS)"},
                        "end_datetime": {"type": "string", "description": "End time in ISO format (YYYY-MM-DDTHH:MM:SS)"},
                        "description": {"type": "string", "description": "Event description"},
                        "location": {"type": "string", "description": "Event location"},
                        "timezone": {"type": "string", "description": "Timezone (default: UTC)"}
                    },
                    "required": ["summary", "start_datetime", "end_datetime"]
                }
            ),
        ]
        
        # Create agent with system prompt
        system_prompt = """
        You are an intelligent assistant that helps users manage their emails and calendar.
        You can read recent emails, send new emails, view upcoming calendar events, and create new events.
        
        When helping users:
        1. Be concise and efficient in your responses
        2. Format information clearly and readably
        3. Suggest proactive actions when appropriate
        4. Handle scheduling with attention to timezone details
        5. Maintain a professional and helpful tone
        
        If you need to authenticate the user with Google, inform them clearly about the process.
        """
        
        # Create and return the agent
        return Agent(
            tools=tools,
            client=self.client,
            model="gpt-4o",
            system=system_prompt,
        )
    
    def process_message(self, message: str) -> str:
        """
        Process a user message using the agent.
        
        Args:
            message: User message
            
        Returns:
            Agent response
        """
        if not self.google_service.is_authenticated():
            auth_status, auth_url = self.google_service.authenticate()
            if not auth_status:
                return f"Please authenticate with Google first by visiting this URL: {auth_url}"
        
        try:
            # Run the agent with the user message
            response = self.agent.run(message)
            return response.output
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def handle_auth_callback(self, auth_code: str) -> bool:
        """
        Handle Google OAuth callback.
        
        Args:
            auth_code: Authorization code from OAuth callback
            
        Returns:
            Success status
        """
        return self.google_service.handle_auth_callback(auth_code)
    
    # Tool implementation methods
    
    def _get_recent_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Tool implementation for getting recent emails."""
        return self.google_service.get_recent_emails(max_results)
    
    def _send_email(self, to: str, subject: str, body: str, html: bool = False) -> Dict[str, Any]:
        """Tool implementation for sending an email."""
        success = self.google_service.send_email(to, subject, body, html)
        return {"success": success, "message": "Email sent successfully" if success else "Failed to send email"}
    
    def _get_upcoming_events(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Tool implementation for getting upcoming events."""
        return self.google_service.get_upcoming_events(max_results)
    
    def _create_calendar_event(
        self,
        summary: str,
        start_datetime: str,
        end_datetime: str,
        description: str = "",
        location: str = "",
        timezone: str = "UTC",
    ) -> Dict[str, Any]:
        """Tool implementation for creating a calendar event."""
        try:
            # Parse datetime strings
            start_time = datetime.fromisoformat(start_datetime.replace("Z", "+00:00"))
            end_time = datetime.fromisoformat(end_datetime.replace("Z", "+00:00"))
            
            # Create event
            success = self.google_service.create_calendar_event(
                summary, start_time, end_time, description, location, timezone
            )
            
            return {
                "success": success,
                "message": "Event created successfully" if success else "Failed to create event"
            }
        except ValueError as e:
            logger.error(f"Invalid datetime format: {e}")
            return {"success": False, "message": f"Invalid datetime format: {str(e)}"}
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
