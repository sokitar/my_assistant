"""
Email agent implementation for handling email-related tasks.
"""
import os
import logging
from typing import Dict, Any, List, Optional
import asyncio

from agents import Agent, Runner, function_tool

from ..services.gmail import GmailService

logger = logging.getLogger("assistant.email_agent")


class EmailAgent:
    """Specialized agent for handling email-related tasks."""
    
    def __init__(self):
        """Initialize the email agent."""
        self.gmail_service = GmailService()
        self.agent = self._create_email_agent()
    
    def _create_email_agent(self) -> Agent:
        """
        Create the email agent with tools.
        
        Returns:
            Configured Agent instance
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
        def read_email(email_id: str) -> str:
            """
            Read the content of a specific email.
            
            Args:
                email_id: ID of the email to read
                
            Returns:
                Email content as formatted text
            """
            # Get the email thread containing this email
            thread = self.gmail_service.get_email_thread(email_id)
            
            if not thread:
                return f"Could not find email with ID {email_id}."
            
            # Find the specific email in the thread
            email = next((msg for msg in thread if msg['id'] == email_id), None)
            
            if not email:
                return f"Could not find email with ID {email_id} in the thread."
            
            # Mark the email as read
            self.gmail_service.mark_as_read(email_id)
            
            formatted_email = f"From: {email['sender']}\n"
            formatted_email += f"Subject: {email['subject']}\n"
            formatted_email += f"Date: {email['date']}\n\n"
            formatted_email += f"{email['body']}\n"
            
            return formatted_email
        
        @function_tool
        def send_email(to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> str:
            """
            Send an email.
            
            Args:
                to: Recipient email address
                subject: Email subject
                body: Email body
                cc: Carbon copy recipients (optional)
                bcc: Blind carbon copy recipients (optional)
                
            Returns:
                Confirmation message
            """
            success = self.gmail_service.send_email(to, subject, body, cc=cc, bcc=bcc)
            
            if success:
                return f"Email sent successfully to {to}."
            else:
                return "Failed to send email. Please try again."
        
        @function_tool
        def search_emails(query: str, max_results: int = 5) -> str:
            """
            Search emails using Gmail search syntax.
            
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
                formatted_emails += f"   ID: {email['id']}\n"
                formatted_emails += f"   Snippet: {email['snippet']}\n\n"
            
            return formatted_emails
        
        @function_tool
        def get_email_thread(thread_id: str) -> str:
            """
            Get all messages in an email thread.
            
            Args:
                thread_id: ID of the thread
                
            Returns:
                Thread messages as formatted text
            """
            messages = self.gmail_service.get_email_thread(thread_id)
            
            if not messages:
                return f"Could not find thread with ID {thread_id}."
            
            formatted_thread = f"Email thread with {len(messages)} messages:\n\n"
            for i, message in enumerate(messages, 1):
                formatted_thread += f"Message {i}:\n"
                formatted_thread += f"From: {message['sender']}\n"
                formatted_thread += f"Subject: {message['subject']}\n"
                formatted_thread += f"Date: {message['date']}\n\n"
                formatted_thread += f"{message['body'][:500]}...\n\n"
                if i < len(messages):
                    formatted_thread += "---\n\n"
            
            return formatted_thread
        
        # Create the email agent
        email_agent = Agent(
            name="Email Agent",
            instructions="""You are a specialized agent for handling email-related tasks.
            You can help with reading unread emails, sending emails, and searching emails.
            Always format emails professionally and clearly.
            If the task is not related to emails, explain that you're specialized in email tasks.
            When composing emails, maintain a professional tone unless instructed otherwise.
            For sending emails, make sure to confirm the recipient, subject, and content with the user.
            """,
            tools=[get_unread_emails, read_email, send_email, search_emails, get_email_thread],
            model=os.environ.get("OPENAI_MODEL", "gpt-4-turbo")
        )
        
        return email_agent
    
    async def process_message(self, message: str) -> str:
        """
        Process a user message related to email tasks.
        
        Args:
            message: User message
            
        Returns:
            Agent response
        """
        try:
            # Run the email agent with the user message
            result = await Runner.run(self.agent, input=message)
            return result.final_output
            
        except Exception as e:
            logger.error(f"Error processing email message: {e}")
            return "I'm sorry, I encountered an error while processing your email request. Please try again."
    
    def process_message_sync(self, message: str) -> str:
        """
        Synchronous version of process_message.
        
        Args:
            message: User message
            
        Returns:
            Agent response
        """
        return asyncio.run(self.process_message(message))
