"""
API routes for the personal assistant.
"""
import logging
from typing import Dict, Any, List, Optional
import datetime

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ...agents.assistant import AssistantAgent
from ...agents.email_agent import EmailAgent
from ...agents.calendar_agent import CalendarAgent
from ...utils.helpers import load_user_preferences, update_user_preferences

# Configure logging
logger = logging.getLogger("app.routes.api")

# Create router
router = APIRouter(prefix="/api", tags=["api"])

# Initialize agents
assistant_agent = AssistantAgent()
email_agent = EmailAgent()
calendar_agent = CalendarAgent()


# Define request models
class ChatRequest(BaseModel):
    """Chat message request model."""
    message: str
    user_id: str = "default"


class ChatResponse(BaseModel):
    """Chat message response model."""
    response: str
    source: str = "assistant"  # assistant, email, or calendar


class EmailRequest(BaseModel):
    """Email request model."""
    to: str
    subject: str
    body: str
    cc: Optional[str] = None
    bcc: Optional[str] = None


class CalendarEventRequest(BaseModel):
    """Calendar event request model."""
    summary: str
    start_time: str
    end_time: str
    description: Optional[str] = None
    location: Optional[str] = None


# Chat routes
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message and return a response.
    
    Args:
        request: Chat request containing the message and user ID
        
    Returns:
        Chat response
    """
    try:
        # Process the message with the assistant agent
        response = await assistant_agent.process_message(request.message, request.user_id)
        return ChatResponse(response=response, source="assistant")
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email", response_model=ChatResponse)
async def email_chat(request: ChatRequest):
    """
    Process an email-related message and return a response.
    
    Args:
        request: Chat request containing the message and user ID
        
    Returns:
        Chat response
    """
    try:
        # Process the message with the email agent
        response = await email_agent.process_message(request.message)
        return ChatResponse(response=response, source="email")
    except Exception as e:
        logger.error(f"Error processing email message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calendar", response_model=ChatResponse)
async def calendar_chat(request: ChatRequest):
    """
    Process a calendar-related message and return a response.
    
    Args:
        request: Chat request containing the message and user ID
        
    Returns:
        Chat response
    """
    try:
        # Process the message with the calendar agent
        response = await calendar_agent.process_message(request.message)
        return ChatResponse(response=response, source="calendar")
    except Exception as e:
        logger.error(f"Error processing calendar message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Email routes
@router.post("/email/send")
async def send_email(request: EmailRequest):
    """
    Send an email.
    
    Args:
        request: Email request containing recipient, subject, and body
        
    Returns:
        Success message
    """
    try:
        # Send the email using the email agent
        success = email_agent.gmail_service.send_email(
            to=request.to,
            subject=request.subject,
            body=request.body,
            cc=request.cc,
            bcc=request.bcc
        )
        
        if success:
            return {"message": f"Email sent successfully to {request.to}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/email/unread")
async def get_unread_emails(max_results: int = 10):
    """
    Get unread emails.
    
    Args:
        max_results: Maximum number of emails to retrieve
        
    Returns:
        List of unread emails
    """
    try:
        emails = email_agent.gmail_service.get_unread_emails(max_results)
        return emails
    except Exception as e:
        logger.error(f"Error getting unread emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/email/search")
async def search_emails(query: str, max_results: int = 10):
    """
    Search emails.
    
    Args:
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        List of matching emails
    """
    try:
        emails = email_agent.gmail_service.search_emails(query, max_results)
        return emails
    except Exception as e:
        logger.error(f"Error searching emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Calendar routes
@router.post("/calendar/create")
async def create_calendar_event(request: CalendarEventRequest):
    """
    Create a calendar event.
    
    Args:
        request: Calendar event request containing event details
        
    Returns:
        Success message
    """
    try:
        # Parse ISO format times
        start = datetime.datetime.fromisoformat(request.start_time)
        end = datetime.datetime.fromisoformat(request.end_time)
        
        # Create the event using the calendar agent
        event = calendar_agent.calendar_service.create_event(
            summary=request.summary,
            start_time=start,
            end_time=end,
            description=request.description or "",
            location=request.location or ""
        )
        
        if event:
            return {"message": f"Event '{request.summary}' created successfully", "event": event}
        else:
            raise HTTPException(status_code=500, detail="Failed to create event")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        logger.error(f"Error creating calendar event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calendar/events")
async def get_upcoming_events(max_results: int = 10):
    """
    Get upcoming calendar events.
    
    Args:
        max_results: Maximum number of events to retrieve
        
    Returns:
        List of upcoming events
    """
    try:
        events = calendar_agent.calendar_service.get_upcoming_events(max_results)
        return events
    except Exception as e:
        logger.error(f"Error getting upcoming events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calendar/search")
async def search_calendar_events(query: str, max_results: int = 10):
    """
    Search calendar events.
    
    Args:
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        List of matching events
    """
    try:
        events = calendar_agent.calendar_service.search_events(query, max_results)
        return events
    except Exception as e:
        logger.error(f"Error searching calendar events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# User preferences routes
@router.get("/preferences/{user_id}")
async def get_preferences(user_id: str = "default"):
    """
    Get user preferences.
    
    Args:
        user_id: User ID
        
    Returns:
        User preferences
    """
    try:
        prefs = load_user_preferences(user_id)
        return prefs
    except Exception as e:
        logger.error(f"Error getting preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preferences/{user_id}")
async def update_preferences(user_id: str, updates: Dict[str, Any]):
    """
    Update user preferences.
    
    Args:
        user_id: User ID
        updates: Preference updates
        
    Returns:
        Updated preferences
    """
    try:
        success = update_user_preferences(user_id, updates)
        
        if success:
            return load_user_preferences(user_id)
        else:
            raise HTTPException(status_code=500, detail="Failed to update preferences")
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))
