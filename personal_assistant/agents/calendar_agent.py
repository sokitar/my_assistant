"""
Calendar agent implementation for handling calendar-related tasks.
"""
import os
import logging
import datetime
from typing import Dict, Any, List, Optional
import asyncio

from agents import Agent, Runner, function_tool

from ..services.calendar import CalendarService

logger = logging.getLogger("assistant.calendar_agent")


class CalendarAgent:
    """Specialized agent for handling calendar-related tasks."""
    
    def __init__(self):
        """Initialize the calendar agent."""
        self.calendar_service = CalendarService()
        self.agent = self._create_calendar_agent()
    
    def _create_calendar_agent(self) -> Agent:
        """
        Create the calendar agent with tools.
        
        Returns:
            Configured Agent instance
        """
        @function_tool
        def get_upcoming_events(max_results: int = 5) -> str:
            """
            Get upcoming calendar events.
            
            Args:
                max_results: Maximum number of events to retrieve
                
            Returns:
                Upcoming events as formatted text
            """
            events = self.calendar_service.get_upcoming_events(max_results)
            
            if not events:
                return "You have no upcoming events."
            
            formatted_events = f"You have {len(events)} upcoming events:\n\n"
            for i, event in enumerate(events, 1):
                formatted_events += f"{i}. {event['summary']}\n"
                formatted_events += f"   Start: {event['start']}\n"
                formatted_events += f"   End: {event['end']}\n"
                if event.get('location'):
                    formatted_events += f"   Location: {event['location']}\n"
                if event.get('description'):
                    formatted_events += f"   Description: {event['description']}\n"
                formatted_events += "\n"
            
            return formatted_events
        
        @function_tool
        def get_event_details(event_id: str) -> str:
            """
            Get details of a specific calendar event.
            
            Args:
                event_id: ID of the event
                
            Returns:
                Event details as formatted text
            """
            event = self.calendar_service.get_event_details(event_id)
            
            if not event:
                return f"Could not find event with ID {event_id}."
            
            formatted_event = f"Event: {event.get('summary', 'No Title')}\n"
            
            # Format start and end times
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            formatted_event += f"Start: {start}\n"
            formatted_event += f"End: {end}\n"
            
            if event.get('location'):
                formatted_event += f"Location: {event['location']}\n"
            
            if event.get('description'):
                formatted_event += f"Description: {event['description']}\n"
            
            # Format attendees
            attendees = event.get('attendees', [])
            if attendees:
                formatted_event += "\nAttendees:\n"
                for attendee in attendees:
                    status = attendee.get('responseStatus', 'unknown')
                    formatted_event += f"- {attendee.get('email')} ({status})\n"
            
            return formatted_event
        
        @function_tool
        def create_calendar_event(summary: str, start_time: str, end_time: str, 
                                 description: str = "", location: str = "") -> str:
            """
            Create a calendar event.
            
            Args:
                summary: Event title
                start_time: Start time (ISO format)
                end_time: End time (ISO format)
                description: Event description
                location: Event location
                
            Returns:
                Confirmation message
            """
            try:
                # Parse ISO format times
                start = datetime.datetime.fromisoformat(start_time)
                end = datetime.datetime.fromisoformat(end_time)
                
                event = self.calendar_service.create_event(
                    summary=summary,
                    start_time=start,
                    end_time=end,
                    description=description,
                    location=location
                )
                
                if event:
                    return f"Event '{summary}' created successfully."
                else:
                    return "Failed to create event. Please try again."
                
            except ValueError as e:
                return f"Invalid date format: {e}. Please use ISO format (YYYY-MM-DDTHH:MM:SS)."
        
        @function_tool
        def update_calendar_event(event_id: str, updates: Dict[str, Any]) -> str:
            """
            Update an existing calendar event.
            
            Args:
                event_id: ID of the event to update
                updates: Dictionary of fields to update
                
            Returns:
                Confirmation message
            """
            # Process any date/time fields in the updates
            processed_updates = {}
            for key, value in updates.items():
                if key in ['start', 'end'] and isinstance(value, str):
                    try:
                        dt = datetime.datetime.fromisoformat(value)
                        processed_updates[key] = {'dateTime': dt.isoformat(), 'timeZone': 'UTC'}
                    except ValueError as e:
                        return f"Invalid date format for {key}: {e}. Please use ISO format (YYYY-MM-DDTHH:MM:SS)."
                else:
                    processed_updates[key] = value
            
            updated_event = self.calendar_service.update_event(event_id, processed_updates)
            
            if updated_event:
                return f"Event updated successfully."
            else:
                return f"Failed to update event with ID {event_id}."
        
        @function_tool
        def delete_calendar_event(event_id: str) -> str:
            """
            Delete a calendar event.
            
            Args:
                event_id: ID of the event to delete
                
            Returns:
                Confirmation message
            """
            success = self.calendar_service.delete_event(event_id)
            
            if success:
                return f"Event with ID {event_id} deleted successfully."
            else:
                return f"Failed to delete event with ID {event_id}."
        
        @function_tool
        def search_calendar_events(query: str, max_results: int = 5) -> str:
            """
            Search calendar events.
            
            Args:
                query: Search query
                max_results: Maximum number of results
                
            Returns:
                Search results as formatted text
            """
            events = self.calendar_service.search_events(query, max_results)
            
            if not events:
                return f"No events found matching '{query}'."
            
            formatted_events = f"Found {len(events)} events matching '{query}':\n\n"
            for i, event in enumerate(events, 1):
                formatted_events += f"{i}. {event['summary']}\n"
                formatted_events += f"   ID: {event['id']}\n"
                formatted_events += f"   Start: {event['start']}\n"
                formatted_events += f"   End: {event['end']}\n"
                if event.get('location'):
                    formatted_events += f"   Location: {event['location']}\n"
                formatted_events += "\n"
            
            return formatted_events
        
        # Create the calendar agent
        calendar_agent = Agent(
            name="Calendar Agent",
            instructions="""You are a specialized agent for handling calendar-related tasks.
            You can help with viewing upcoming events, creating events, updating events, and searching events.
            Always format dates and times clearly and in a consistent format.
            If the task is not related to calendar, explain that you're specialized in calendar tasks.
            When creating or updating events, make sure to confirm the details with the user.
            For date and time inputs, guide users to use ISO format (YYYY-MM-DDTHH:MM:SS) for clarity.
            """,
            tools=[
                get_upcoming_events, 
                get_event_details, 
                create_calendar_event, 
                update_calendar_event, 
                delete_calendar_event, 
                search_calendar_events
            ],
            model=os.environ.get("OPENAI_MODEL", "gpt-4-turbo")
        )
        
        return calendar_agent
    
    async def process_message(self, message: str) -> str:
        """
        Process a user message related to calendar tasks.
        
        Args:
            message: User message
            
        Returns:
            Agent response
        """
        try:
            # Run the calendar agent with the user message
            result = await Runner.run(self.agent, input=message)
            return result.final_output
            
        except Exception as e:
            logger.error(f"Error processing calendar message: {e}")
            return "I'm sorry, I encountered an error while processing your calendar request. Please try again."
    
    def process_message_sync(self, message: str) -> str:
        """
        Synchronous version of process_message.
        
        Args:
            message: User message
            
        Returns:
            Agent response
        """
        return asyncio.run(self.process_message(message))
