"""
Google Calendar service for managing calendar events.
"""
import datetime
import logging
from typing import Dict, Any, List, Optional, Tuple

from googleapiclient.errors import HttpError

from ..utils.auth import build_calendar_service
from ..utils.helpers import format_datetime, parse_datetime

logger = logging.getLogger("assistant.calendar")


class CalendarService:
    """Service class for Google Calendar API operations."""
    
    def __init__(self):
        """Initialize the Calendar service."""
        self.service = None
        self.calendar_id = 'primary'  # Default calendar ID
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Calendar API.
        
        Returns:
            True if authentication is successful, False otherwise
        """
        try:
            self.service = build_calendar_service()
            return self.service is not None
        except Exception as e:
            logger.error(f"Calendar authentication error: {e}")
            return False
    
    def get_upcoming_events(self, max_results: int = 10, 
                           time_min: Optional[datetime.datetime] = None) -> List[Dict[str, Any]]:
        """
        Get upcoming calendar events.
        
        Args:
            max_results: Maximum number of events to retrieve
            time_min: Minimum time for events (defaults to now)
            
        Returns:
            List of upcoming events
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        if time_min is None:
            time_min = datetime.datetime.utcnow()
        
        time_min_str = time_min.isoformat() + 'Z'  # 'Z' indicates UTC time
        
        try:
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min_str,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'start': start,
                    'end': end,
                    'creator': event.get('creator', {}),
                    'attendees': event.get('attendees', []),
                    'htmlLink': event.get('htmlLink', '')
                })
            
            return formatted_events
            
        except HttpError as error:
            logger.error(f"Error retrieving calendar events: {error}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error retrieving calendar events: {e}")
            return []
    
    def create_event(self, summary: str, start_time: datetime.datetime, 
                    end_time: datetime.datetime, description: str = '', 
                    location: str = '', attendees: List[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """
        Create a new calendar event.
        
        Args:
            summary: Event title/summary
            start_time: Start time of the event
            end_time: End time of the event
            description: Event description
            location: Event location
            attendees: List of attendees (dicts with 'email' key)
            
        Returns:
            Created event details or None if creation failed
        """
        if not self.service:
            if not self.authenticate():
                return None
        
        if attendees is None:
            attendees = []
        
        # Format times to RFC3339 format
        start_time_str = start_time.isoformat()
        end_time_str = end_time.isoformat()
        
        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time_str,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time_str,
                'timeZone': 'UTC',
            },
            'attendees': attendees,
            'reminders': {
                'useDefault': True
            }
        }
        
        try:
            created_event = self.service.events().insert(
                calendarId=self.calendar_id, body=event).execute()
            
            logger.info(f"Event created: {created_event.get('htmlLink')}")
            return created_event
            
        except HttpError as error:
            logger.error(f"Error creating calendar event: {error}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating calendar event: {e}")
            return None
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing calendar event.
        
        Args:
            event_id: ID of the event to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated event details or None if update failed
        """
        if not self.service:
            if not self.authenticate():
                return None
        
        try:
            # First get the existing event
            event = self.service.events().get(
                calendarId=self.calendar_id, eventId=event_id).execute()
            
            # Update the event with new values
            for key, value in updates.items():
                if key in ['start', 'end']:
                    # Handle start and end times specially
                    if 'dateTime' in value:
                        event[key]['dateTime'] = value['dateTime']
                    if 'timeZone' in value:
                        event[key]['timeZone'] = value['timeZone']
                else:
                    event[key] = value
            
            updated_event = self.service.events().update(
                calendarId=self.calendar_id, eventId=event_id, body=event).execute()
            
            logger.info(f"Event updated: {updated_event.get('htmlLink')}")
            return updated_event
            
        except HttpError as error:
            logger.error(f"Error updating calendar event: {error}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error updating calendar event: {e}")
            return None
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete a calendar event.
        
        Args:
            event_id: ID of the event to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if not self.service:
            if not self.authenticate():
                return False
        
        try:
            self.service.events().delete(
                calendarId=self.calendar_id, eventId=event_id).execute()
            
            logger.info(f"Event deleted: {event_id}")
            return True
            
        except HttpError as error:
            logger.error(f"Error deleting calendar event: {error}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting calendar event: {e}")
            return False
    
    def get_event_details(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details of a specific calendar event.
        
        Args:
            event_id: ID of the event
            
        Returns:
            Event details or None if retrieval failed
        """
        if not self.service:
            if not self.authenticate():
                return None
        
        try:
            event = self.service.events().get(
                calendarId=self.calendar_id, eventId=event_id).execute()
            
            return event
            
        except HttpError as error:
            logger.error(f"Error retrieving calendar event: {error}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving calendar event: {e}")
            return None
    
    def search_events(self, query: str, max_results: int = 10, 
                     time_min: Optional[datetime.datetime] = None,
                     time_max: Optional[datetime.datetime] = None) -> List[Dict[str, Any]]:
        """
        Search for calendar events.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            time_min: Minimum time for events (defaults to now)
            time_max: Maximum time for events
            
        Returns:
            List of matching events
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        if time_min is None:
            time_min = datetime.datetime.utcnow()
        
        time_min_str = time_min.isoformat() + 'Z'  # 'Z' indicates UTC time
        
        params = {
            'calendarId': self.calendar_id,
            'q': query,
            'timeMin': time_min_str,
            'maxResults': max_results,
            'singleEvents': True,
            'orderBy': 'startTime'
        }
        
        if time_max:
            params['timeMax'] = time_max.isoformat() + 'Z'
        
        try:
            events_result = self.service.events().list(**params).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'start': start,
                    'end': end,
                    'creator': event.get('creator', {}),
                    'attendees': event.get('attendees', []),
                    'htmlLink': event.get('htmlLink', '')
                })
            
            return formatted_events
            
        except HttpError as error:
            logger.error(f"Error searching calendar events: {error}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching calendar events: {e}")
            return []
