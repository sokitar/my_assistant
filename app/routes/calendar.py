"""
Calendar routes for the personal assistant application.

This module handles all the routes related to calendar functionality,
including viewing, creating, updating, and deleting events.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from personal_assistant.agents.calendar_agent import CalendarAgent
from personal_assistant.app.routes.auth import get_current_user


# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/calendar", tags=["calendar"])


# Pydantic models for request and response validation
class EventBase(BaseModel):
    """Base model for calendar events."""
    summary: str
    start_time: str
    end_time: str
    location: Optional[str] = None
    description: Optional[str] = None


class EventCreate(EventBase):
    """Model for creating a new event."""
    pass


class EventUpdate(EventBase):
    """Model for updating an existing event."""
    pass


class EventResponse(EventBase):
    """Model for event response."""
    id: str
    created: str
    updated: str
    creator: Optional[dict] = None
    attendees: Optional[List[dict]] = None
    
    class Config:
        """Pydantic config for the model."""
        orm_mode = True


@router.get("/events", response_model=List[EventResponse])
async def get_events(
    start: Optional[str] = None,
    end: Optional[str] = None,
    max_results: int = Query(10, gt=0, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Get calendar events for the current user.
    
    Args:
        start: Optional start date/time (ISO format)
        end: Optional end date/time (ISO format)
        max_results: Maximum number of results to return
        current_user: Current authenticated user
        
    Returns:
        List of calendar events
    """
    try:
        # Default to events from today to 30 days in the future if not specified
        if not start:
            start = datetime.now().isoformat()
        if not end:
            end = (datetime.now() + timedelta(days=30)).isoformat()
        
        # Create calendar agent
        calendar_agent = CalendarAgent(user_credentials=current_user.get("credentials"))
        
        # Get events
        events = await calendar_agent.get_events(
            time_min=start,
            time_max=end,
            max_results=max_results
        )
        
        return events
    except Exception as e:
        logger.error(f"Error getting events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting events: {str(e)}")


@router.get("/event/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific calendar event by ID.
    
    Args:
        event_id: ID of the event to retrieve
        current_user: Current authenticated user
        
    Returns:
        Event details
    """
    try:
        # Create calendar agent
        calendar_agent = CalendarAgent(user_credentials=current_user.get("credentials"))
        
        # Get event
        event = await calendar_agent.get_event(event_id)
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return event
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event {event_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting event: {str(e)}")


@router.post("/create", response_model=EventResponse)
async def create_event(
    event: EventCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new calendar event.
    
    Args:
        event: Event details
        current_user: Current authenticated user
        
    Returns:
        Created event details
    """
    try:
        # Create calendar agent
        calendar_agent = CalendarAgent(user_credentials=current_user.get("credentials"))
        
        # Create event
        created_event = await calendar_agent.create_event(
            summary=event.summary,
            start_time=event.start_time,
            end_time=event.end_time,
            location=event.location,
            description=event.description
        )
        
        return created_event
    except Exception as e:
        logger.error(f"Error creating event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating event: {str(e)}")


@router.post("/update/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    event: EventUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing calendar event.
    
    Args:
        event_id: ID of the event to update
        event: Updated event details
        current_user: Current authenticated user
        
    Returns:
        Updated event details
    """
    try:
        # Create calendar agent
        calendar_agent = CalendarAgent(user_credentials=current_user.get("credentials"))
        
        # Update event
        updated_event = await calendar_agent.update_event(
            event_id=event_id,
            summary=event.summary,
            start_time=event.start_time,
            end_time=event.end_time,
            location=event.location,
            description=event.description
        )
        
        return updated_event
    except Exception as e:
        logger.error(f"Error updating event {event_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating event: {str(e)}")


@router.delete("/delete/{event_id}")
async def delete_event(
    event_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a calendar event.
    
    Args:
        event_id: ID of the event to delete
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    try:
        # Create calendar agent
        calendar_agent = CalendarAgent(user_credentials=current_user.get("credentials"))
        
        # Delete event
        await calendar_agent.delete_event(event_id)
        
        return {"message": "Event deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting event: {str(e)}")


@router.get("/search", response_model=List[EventResponse])
async def search_events(
    query: str,
    max_results: int = Query(10, gt=0, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Search for calendar events.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        current_user: Current authenticated user
        
    Returns:
        List of matching events
    """
    try:
        # Create calendar agent
        calendar_agent = CalendarAgent(user_credentials=current_user.get("credentials"))
        
        # Search events
        events = await calendar_agent.search_events(
            query=query,
            max_results=max_results
        )
        
        return events
    except Exception as e:
        logger.error(f"Error searching events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching events: {str(e)}")
