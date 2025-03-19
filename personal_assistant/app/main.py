"""
Main application entry point for the personal assistant.
"""
import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, Request, HTTPException, Depends, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ..agents.assistant import AssistantAgent
from ..agents.email_agent import EmailAgent
from ..agents.calendar_agent import CalendarAgent
from ..utils.auth import get_credentials, get_user_info
from ..utils.helpers import load_user_preferences, update_user_preferences

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO if not os.getenv("DEBUG") else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("app")

# Create the FastAPI app
app = FastAPI(
    title="Personal Assistant",
    description="A personal assistant that can handle emails, calendar, and chat",
    version="0.1.0"
)

# Create static files directory if it doesn't exist
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Set up templates
templates = Jinja2Templates(directory="app/templates")

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


# Define routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Render the home page."""
    return templates.TemplateResponse(
        "index.html", {"request": request, "title": "Personal Assistant"}
    )


@app.post("/api/chat", response_model=ChatResponse)
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


@app.post("/api/email", response_model=ChatResponse)
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


@app.post("/api/calendar", response_model=ChatResponse)
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


@app.post("/api/email/send")
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


@app.post("/api/calendar/create")
async def create_calendar_event(request: CalendarEventRequest):
    """
    Create a calendar event.
    
    Args:
        request: Calendar event request containing event details
        
    Returns:
        Success message
    """
    try:
        import datetime
        
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
            return {"message": f"Event '{request.summary}' created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create event")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        logger.error(f"Error creating calendar event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/auth/status")
async def auth_status():
    """
    Check authentication status for Google services.
    
    Returns:
        Authentication status for Gmail and Calendar
    """
    try:
        gmail_creds = get_credentials(["https://www.googleapis.com/auth/gmail.readonly"])
        calendar_creds = get_credentials(["https://www.googleapis.com/auth/calendar.readonly"])
        
        return {
            "gmail_authenticated": gmail_creds is not None and gmail_creds.valid,
            "calendar_authenticated": calendar_creds is not None and calendar_creds.valid
        }
    except Exception as e:
        logger.error(f"Error checking auth status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/preferences/{user_id}")
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


@app.post("/api/preferences/{user_id}")
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


# Run the application
if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
