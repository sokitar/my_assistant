"""
Gmail service for sending and receiving emails.
"""
import base64
import os
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional, Tuple

from googleapiclient.errors import HttpError
import logging

from ..utils.auth import build_gmail_service, get_credentials
from ..utils.helpers import truncate_text

logger = logging.getLogger("assistant.gmail")


class GmailService:
    """Service class for Gmail API operations."""
    
    def __init__(self):
        """Initialize the Gmail service."""
        self.service = None
        self.user_id = 'me'  # Default user ID for Gmail API
    
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API.
        
        Returns:
            True if authentication is successful, False otherwise
        """
        try:
            self.service = build_gmail_service()
            return self.service is not None
        except Exception as e:
            logger.error(f"Gmail authentication error: {e}")
            return False
    
    def send_email(self, to: str, subject: str, body: str, 
                  html_content: Optional[str] = None, cc: Optional[str] = None, 
                  bcc: Optional[str] = None) -> bool:
        """
        Send an email using Gmail API.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Plain text email body
            html_content: HTML content for the email (optional)
            cc: Carbon copy recipients (optional)
            bcc: Blind carbon copy recipients (optional)
            
        Returns:
            True if the email was sent successfully, False otherwise
        """
        if not self.service:
            if not self.authenticate():
                return False
        
        try:
            message = MIMEMultipart('alternative')
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc
            
            # Attach plain text and HTML parts
            message.attach(MIMEText(body, 'plain'))
            if html_content:
                message.attach(MIMEText(html_content, 'html'))
            
            # Encode the message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Create the message
            create_message = {
                'raw': encoded_message
            }
            
            # Send the message
            send_message = self.service.users().messages().send(
                userId=self.user_id, body=create_message).execute()
            
            logger.info(f"Email sent. Message ID: {send_message['id']}")
            return True
            
        except HttpError as error:
            logger.error(f"Error sending email: {error}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return False
    
    def get_unread_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get unread emails from the inbox.
        
        Args:
            max_results: Maximum number of emails to retrieve
            
        Returns:
            List of unread email messages
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            # Search for unread emails in inbox
            query = "is:unread in:inbox"
            result = self.service.users().messages().list(
                userId=self.user_id, q=query, maxResults=max_results).execute()
            
            messages = result.get('messages', [])
            
            # Get full message details for each message
            email_list = []
            for msg in messages:
                message_id = msg['id']
                message = self.service.users().messages().get(
                    userId=self.user_id, id=message_id).execute()
                
                # Extract headers
                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                
                # Extract body
                body = self._get_message_body(message)
                
                email_list.append({
                    'id': message_id,
                    'threadId': message['threadId'],
                    'sender': sender,
                    'subject': subject,
                    'date': date,
                    'snippet': message.get('snippet', ''),
                    'body': body
                })
            
            return email_list
            
        except HttpError as error:
            logger.error(f"Error retrieving emails: {error}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error retrieving emails: {e}")
            return []
    
    def _get_message_body(self, message: Dict[str, Any]) -> str:
        """
        Extract the message body from a Gmail message.
        
        Args:
            message: Gmail message object
            
        Returns:
            Message body as text
        """
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        data = part['body']['data']
                        return base64.urlsafe_b64decode(data).decode('utf-8')
        
        # If no plain text part found, try to get body data directly
        if 'body' in message['payload'] and 'data' in message['payload']['body']:
            data = message['payload']['body']['data']
            return base64.urlsafe_b64decode(data).decode('utf-8')
        
        return "No message body found."
    
    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark an email as read.
        
        Args:
            message_id: ID of the message to mark as read
            
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            if not self.authenticate():
                return False
        
        try:
            self.service.users().messages().modify(
                userId=self.user_id,
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error marking message as read: {e}")
            return False
    
    def search_emails(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search emails using Gmail search syntax.
        
        Args:
            query: Gmail search query
            max_results: Maximum number of results to return
            
        Returns:
            List of matching email messages
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            result = self.service.users().messages().list(
                userId=self.user_id, q=query, maxResults=max_results).execute()
            
            messages = result.get('messages', [])
            
            # Get full message details for each message
            email_list = []
            for msg in messages:
                message_id = msg['id']
                message = self.service.users().messages().get(
                    userId=self.user_id, id=message_id).execute()
                
                # Extract headers
                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                
                # Extract snippet
                snippet = message.get('snippet', '')
                
                email_list.append({
                    'id': message_id,
                    'threadId': message['threadId'],
                    'sender': sender,
                    'subject': subject,
                    'date': date,
                    'snippet': snippet
                })
            
            return email_list
            
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return []
    
    def get_email_thread(self, thread_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages in an email thread.
        
        Args:
            thread_id: ID of the thread
            
        Returns:
            List of messages in the thread
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            thread = self.service.users().threads().get(
                userId=self.user_id, id=thread_id).execute()
            
            messages = []
            for message in thread['messages']:
                # Extract headers
                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                
                # Extract body
                body = self._get_message_body(message)
                
                messages.append({
                    'id': message['id'],
                    'sender': sender,
                    'subject': subject,
                    'date': date,
                    'body': body
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"Error retrieving email thread: {e}")
            return []
