"""
Gradio UI interface for the Gmail and Google Calendar Agent.
Implements a clean, efficient, and user-friendly interface.
"""
import gradio as gr
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Tuple, Any, Optional

from src.config import AppConfig
from src.services.agent_service import AgentService
from src.services.google_api import GoogleAPIService
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger("ui_interface")

# Custom CSS for a sleek interface
CUSTOM_CSS = """
.container {
    max-width: 1000px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}
.header {
    text-align: center;
    margin-bottom: 20px;
}
.header h1 {
    margin-bottom: 5px;
}
.header p {
    color: #666;
    margin-top: 0;
}
.chat-window {
    height: 400px;
    overflow-y: auto;
    border-radius: 10px;
    border: 1px solid #ddd;
    padding: 15px;
    background-color: #f9f9f9;
}
.email-card, .event-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 10px;
    background-color: white;
}
.email-subject, .event-title {
    font-weight: bold;
    margin-bottom: 5px;
}
.email-sender, .event-time {
    color: #666;
    font-size: 0.9em;
    margin-bottom: 5px;
}
.email-snippet, .event-details {
    font-size: 0.9em;
}
.tabs {
    margin-top: 20px;
}
"""

def create_interface(config: AppConfig) -> gr.Blocks:
    """
    Create the Gradio interface for the application.
    
    Args:
        config: Application configuration
        
    Returns:
        Configured Gradio Blocks interface
    """
    # Initialize services
    google_service = GoogleAPIService(
        config.google_client_id,
        config.google_client_secret,
        config.google_redirect_uri
    )
    
    agent_service = AgentService(config.openai_api_key, google_service)
    
    # Create Gradio interface
    with gr.Blocks(css=CUSTOM_CSS) as demo:
        # Header
        with gr.Row(elem_classes=["header"]):
            gr.Markdown("# Gmail & Calendar Assistant")
            gr.Markdown("Your intelligent email and calendar management agent")
        
        # Authentication status
        with gr.Row():
            auth_status = gr.Textbox(
                label="Authentication Status",
                value="Checking authentication status...",
                interactive=False
            )
            auth_button = gr.Button("Authenticate with Google")
            auth_code_input = gr.Textbox(
                label="Enter Authentication Code",
                placeholder="Paste the authentication code here",
                visible=False
            )
            auth_submit = gr.Button("Submit Code", visible=False)
        
        # Main interface with tabs
        with gr.Tabs(elem_classes=["tabs"]) as tabs:
            # Chat tab
            with gr.Tab("Assistant"):
                with gr.Row():
                    with gr.Column(scale=2):
                        chatbot = gr.Chatbot(
                            label="Conversation",
                            elem_classes=["chat-window"],
                            height=400
                        )
                        
                        with gr.Row():
                            user_input = gr.Textbox(
                                label="Message",
                                placeholder="Ask me about your emails or calendar...",
                                lines=2
                            )
                            submit_btn = gr.Button("Send", variant="primary")
            
            # Email tab
            with gr.Tab("Recent Emails"):
                with gr.Row():
                    email_container = gr.HTML(label="Recent Emails")
                    refresh_emails_btn = gr.Button("Refresh Emails")
            
            # Calendar tab
            with gr.Tab("Calendar"):
                with gr.Row():
                    with gr.Column():
                        events_container = gr.HTML(label="Upcoming Events")
                        refresh_events_btn = gr.Button("Refresh Events")
                    
                    with gr.Column():
                        with gr.Group():
                            gr.Markdown("### Create New Event")
                            event_title = gr.Textbox(label="Title")
                            event_start = gr.Datetime(label="Start Time")
                            event_end = gr.Datetime(label="End Time")
                            event_description = gr.Textbox(label="Description", lines=3)
                            event_location = gr.Textbox(label="Location")
                            create_event_btn = gr.Button("Create Event")
                            event_status = gr.Textbox(label="Status", interactive=False)
        
        # Helper functions
        def check_auth_status():
            """Check and update authentication status."""
            auth_result, auth_url = google_service.authenticate()
            
            if auth_result:
                return (
                    "✅ Authenticated with Google",
                    gr.Button.update(visible=False),
                    gr.Textbox.update(visible=False),
                    gr.Button.update(visible=False)
                )
            else:
                return (
                    f"🔑 Authentication required. Click the button to authenticate.",
                    gr.Button.update(visible=True),
                    gr.Textbox.update(visible=False),
                    gr.Button.update(visible=False)
                )
        
        def start_auth():
            """Start the authentication process."""
            _, auth_url = google_service.authenticate()
            
            # Open the auth URL in a new tab
            gr.utils.launch_browser(auth_url)
            
            return (
                "Please complete authentication in the opened browser window and paste the code here",
                gr.Button.update(visible=False),
                gr.Textbox.update(visible=True),
                gr.Button.update(visible=True)
            )
        
        def submit_auth_code(code):
            """Submit the authentication code."""
            success = agent_service.handle_auth_callback(code)
            
            if success:
                return (
                    "✅ Authentication successful",
                    gr.Button.update(visible=False),
                    gr.Textbox.update(visible=False, value=""),
                    gr.Button.update(visible=False)
                )
            else:
                return (
                    "❌ Authentication failed. Please try again.",
                    gr.Button.update(visible=True),
                    gr.Textbox.update(visible=False, value=""),
                    gr.Button.update(visible=False)
                )
        
        def user_message(message, history):
            """Process user message and update chat history."""
            if not message.strip():
                return history, ""
            
            # Add user message to history
            history.append((message, None))
            return history, ""
        
        def bot_response(history):
            """Generate bot response based on the latest user message."""
            if not history:
                return history
            
            # Get the last user message
            last_message = history[-1][0]
            
            # Process with agent
            response = agent_service.process_message(last_message)
            
            # Update history with bot response
            history[-1] = (last_message, response)
            return history
        
        def format_emails(emails):
            """Format emails for display."""
            if not emails:
                return "<div class='email-card'>No recent emails found</div>"
            
            html = ""
            for email in emails:
                html += f"""
                <div class='email-card'>
                    <div class='email-subject'>{email['subject']}</div>
                    <div class='email-sender'>From: {email['sender']} • {email['date']}</div>
                    <div class='email-snippet'>{email['snippet']}</div>
                </div>
                """
            return html
        
        def refresh_emails():
            """Refresh the email list."""
            emails = google_service.get_recent_emails(20)
            return format_emails(emails)
        
        def format_events(events):
            """Format calendar events for display."""
            if not events:
                return "<div class='event-card'>No upcoming events found</div>"
            
            html = ""
            for event in events:
                # Format start time
                start_time = event['start']
                if 'T' in start_time:  # It's a datetime
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    start_formatted = dt.strftime('%Y-%m-%d %H:%M')
                else:  # It's a date
                    start_formatted = start_time
                
                location = event.get('location', '')
                location_html = f"<div>📍 {location}</div>" if location else ""
                
                html += f"""
                <div class='event-card'>
                    <div class='event-title'>{event['summary']}</div>
                    <div class='event-time'>🕒 {start_formatted}</div>
                    {location_html}
                    <div class='event-details'>{event.get('description', '')}</div>
                </div>
                """
            return html
        
        def refresh_events():
            """Refresh the calendar events list."""
            events = google_service.get_upcoming_events(20)
            return format_events(events)
        
        def create_event(title, start, end, description, location):
            """Create a new calendar event."""
            if not title:
                return "Please enter an event title"
            
            if not start or not end:
                return "Please select start and end times"
            
            # Ensure end time is after start time
            if end <= start:
                return "End time must be after start time"
            
            # Create event
            success = google_service.create_calendar_event(
                title,
                start,
                end,
                description or "",
                location or "",
                "UTC"  # Default timezone
            )
            
            if success:
                # Refresh events
                refresh_events()
                return "✅ Event created successfully"
            else:
                return "❌ Failed to create event"
        
        # Set up event handlers
        demo.load(check_auth_status, outputs=[auth_status, auth_button, auth_code_input, auth_submit])
        auth_button.click(start_auth, outputs=[auth_status, auth_button, auth_code_input, auth_submit])
        auth_submit.click(submit_auth_code, inputs=[auth_code_input], outputs=[auth_status, auth_button, auth_code_input, auth_submit])
        
        # Chat functionality
        submit_btn.click(
            user_message,
            inputs=[user_input, chatbot],
            outputs=[chatbot, user_input],
            queue=False
        ).then(
            bot_response,
            inputs=[chatbot],
            outputs=[chatbot]
        )
        
        # Email functionality
        refresh_emails_btn.click(refresh_emails, outputs=[email_container])
        
        # Calendar functionality
        refresh_events_btn.click(refresh_events, outputs=[events_container])
        create_event_btn.click(
            create_event,
            inputs=[event_title, event_start, event_end, event_description, event_location],
            outputs=[event_status]
        )
        
        # Load initial data
        tabs.select(fn=refresh_emails, outputs=[email_container], inputs=None)
        tabs.select(fn=refresh_events, outputs=[events_container], inputs=None)
        
        return demo
