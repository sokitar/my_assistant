"""
Main assistant agent implementation using OpenAI's Agents SDK.
"""
import os
import logging
from typing import Dict, Any, List, Optional, Callable
import asyncio

from agents import Agent, Runner, function_tool
from pydantic import BaseModel, Field

from ..services.gmail import GmailService
from ..services.calendar import CalendarService
from ..services.web_search import WebSearchService
from ..utils.helpers import load_user_preferences, update_user_preferences

logger = logging.getLogger("assistant.agent")


class AssistantAgent:
    """Main assistant agent that coordinates all functionality."""
    
    def __init__(self):
        """Initialize the assistant agent."""
        self.gmail_service = GmailService()
        self.calendar_service = CalendarService()
        self.web_search_service = WebSearchService()
        
        # Define the main assistant agent
        self.assistant = self._create_assistant_agent()
        
        # Define specialized agents
        self.email_agent = self._create_email_agent()
        self.calendar_agent = self._create_calendar_agent()
        
        # Add handoffs to the main assistant
        self.assistant.handoffs = [self.email_agent, self.calendar_agent]
        
        # Memory for conversation context
        self.conversation_memory = []
        
    def _create_assistant_agent(self) -> Agent:
        """
        Create the main assistant agent with tools.
        
        Returns:
            Configured Agent instance
        """
        @function_tool
        def search_web(query: str) -> str:
            """
            Search the web for information.
            
            Args:
                query: Search query
                
            Returns:
                Search results as formatted text
            """
            results = self.web_search_service.search_sync(query)
            
            if not results:
                return "No results found for your query."
            
            formatted_results = "Here's what I found on the web:\n\n"
            for i, result in enumerate(results, 1):
                formatted_results += f"{i}. {result['title']}\n"
                formatted_results += f"   {result['snippet']}\n"
                formatted_results += f"   URL: {result['link']}\n\n"
            
            return formatted_results
        
        @function_tool
        def get_user_preferences(user_id: str = "default") -> str:
            """
            Get user preferences.
            
            Args:
                user_id: User ID
                
            Returns:
                User preferences as formatted text
            """
            prefs = load_user_preferences(user_id)
            
            formatted_prefs = "User Preferences:\n\n"
            for key, value in prefs.items():
                formatted_prefs += f"{key}: {value}\n"
            
            return formatted_prefs
        
        @function_tool
        def update_preference(user_id: str, preference_name: str, preference_value: str) -> str:
            """
            Update a user preference.
            
            Args:
                user_id: User ID
                preference_name: Name of the preference to update
                preference_value: New value for the preference
                
            Returns:
                Confirmation message
            """
            success = update_user_preferences(user_id, {preference_name: preference_value})
            
            if success:
                return f"Successfully updated {preference_name} to {preference_value}."
            else:
                return f"Failed to update {preference_name}."
        
        # Create the main assistant agent
        assistant = Agent(
            name="Personal Assistant",
            instructions="""You are a helpful personal assistant that can help with emails, calendar, and general questions.
            You should be creative, helpful, and personable. Always try to provide the most relevant and accurate information.
            When the user asks about email or calendar, you can hand off to the specialized agents.
            For general questions, you can use your knowledge or search the web.
            Always maintain a consistent tone and style in your responses.
            Remember user preferences and adapt your responses accordingly.
            """,
            tools=[search_web, get_user_preferences, update_preference],
            model=os.environ.get("OPENAI_MODEL", "gpt-4-turbo")
        )
        
        return assistant
    
    def _create_email_agent(self) -> Agent:
        """
        Create the email specialized agent.
        
        Returns:
            Configured Agent instance for email operations
        """
        @function_tool
        def get_unread_emails(max_results: int = 5) -> str:
            """
            Get unread emails.
            
            Args:
                max_results: Maximum number of emails to retrieve
                
            Returns:
                Unread emails as formatted text
            """
            emails = self.gmail_service.get_unread_emails(max_results)
            
            if not emails:
                return "You have no unread emails."
            
            formatted_emails = f"You have {len(emails)} unread emails:\n\n"
            for i, email in enumerate(emails, 1):
                formatted_emails += f"{i}. From: {email['sender']}\n"
                formatted_emails += f"   Subject: {email['subject']}\n"
                formatted_emails += f"   Date: {email['date']}\n"
                formatted_emails += f"   Snippet: {email['snippet']}\n\n"
            
            return formatted_emails
        
        @function_tool
        def send_email(to: str, subject: str, body: str) -> str:
            """
            Send an email.
            
            Args:
                to: Recipient email address
                subject: Email subject
                body: Email body
                
            Returns:
                Confirmation message
            """
            success = self.gmail_service.send_email(to, subject, body)
            
            if success:
                return f"Email sent successfully to {to}."
            else:
                return "Failed to send email. Please try again."
        
        @function_tool
        def search_emails(query: str, max_results: int = 5) -> str:
            """
            Search emails.
            
            Args:
                query: Search query
                max_results: Maximum number of results
                
            Returns:
                Search results as formatted text
            """
            emails = self.gmail_service.search_emails(query, max_results)
            
            if not emails:
                return f"No emails found matching '{query}'."
            
            formatted_emails = f"Found {len(emails)} emails matching '{query}':\n\n"
            for i, email in enumerate(emails, 1):
                formatted_emails += f"{i}. From: {email['sender']}\n"
                formatted_emails += f"   Subject: {email['subject']}\n"
                formatted_emails += f"   Date: {email['date']}\n"
                formatted_emails += f"   Snippet: {email['snippet']}\n\n"
            
            return formatted_emails
        
        # Create the email agent
        email_agent = Agent(
            name="Email Agent",
            instructions="""You are a specialized agent for handling email-related tasks.
            You can help with reading unread emails, sending emails, and searching emails.
            Always format emails professionally and clearly.
            If the task is not related to emails, hand back to the main assistant.
            """,
            tools=[get_unread_emails, send_email, search_emails],
            model=os.environ.get("OPENAI_MODEL", "gpt-4-turbo")
        )
        
        return email_agent
    
    def _create_calendar_agent(self) -> Agent:
        """
        Create the calendar specialized agent.
        
        Returns:
            Configured Agent instance for calendar operations
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
                formatted_events += "\n"
            
            return formatted_events
        
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
            import datetime
            
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
            You can help with viewing upcoming events, creating events, and searching events.
            Always format dates and times clearly.
            If the task is not related to calendar, hand back to the main assistant.
            """,
            tools=[get_upcoming_events, create_calendar_event, search_calendar_events],
            model=os.environ.get("OPENAI_MODEL", "gpt-4-turbo")
        )
        
        return calendar_agent
    
    async def process_message(self, message: str, user_id: str = "default") -> str:
        """
        Process a user message and generate a response.
        
        Args:
            message: User message
            user_id: User ID
            
        Returns:
            Assistant response
        """
        # Load user preferences to adapt the response
        user_prefs = load_user_preferences(user_id)
        
        # Add user preferences to conversation memory if it's the first message
        if not self.conversation_memory:
            prefs_context = f"User preferences: {user_prefs}"
            self.conversation_memory.append({"role": "system", "content": prefs_context})
        
        # Add the user message to memory
        self.conversation_memory.append({"role": "user", "content": message})
        
        try:
            # Run the assistant with the user message
            result = await Runner.run(self.assistant, input=message)
            response = result.final_output
            
            # Add the assistant response to memory
            self.conversation_memory.append({"role": "assistant", "content": response})
            
            # Limit memory size to prevent context overflow
            if len(self.conversation_memory) > 20:
                # Keep the first system message and the last 19 messages
                self.conversation_memory = [self.conversation_memory[0]] + self.conversation_memory[-19:]
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "I'm sorry, I encountered an error while processing your message. Please try again."
    
    def process_message_sync(self, message: str, user_id: str = "default") -> str:
        """
        Synchronous version of process_message.
        
        Args:
            message: User message
            user_id: User ID
            
        Returns:
            Assistant response
        """
        return asyncio.run(self.process_message(message, user_id))
