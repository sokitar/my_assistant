# Personal AI Assistant

A powerful personal assistant application built with OpenAI's AI Agents SDK and Svelte that can:
- Send and receive emails (Gmail integration)
- Manage calendar events (Google Calendar integration)
- Provide chat-based assistance with AI
- Perform web searches and information retrieval
- Beautiful responsive UI with Tailwind CSS

## Features

- **Modern Web Interface**: Sleek, responsive UI built with Svelte and Tailwind CSS
- **Email Management**: Send, receive, and organize emails through Gmail
- **Calendar Integration**: Create, view, and manage calendar events with Google Calendar
- **AI Chat Interface**: Natural language interaction with the OpenAI-powered assistant
- **Web Search**: Find information from the web
- **Consistent Memory**: The assistant remembers previous interactions and preferences
- **Secure Authentication**: OAuth2 integration with Google services
- **Mobile-Friendly Design**: Access your assistant from any device

## Project Structure

```
personal_assistant/
├── app/                  # Backend application code
│   ├── __init__.py
│   ├── main.py           # FastAPI application entry point
│   ├── routes/           # API endpoints
│   └── templates/        # HTML templates
├── frontend/             # Svelte frontend application
│   ├── src/              # Source code
│   │   ├── components/   # Reusable UI components
│   │   ├── services/     # API service integrations
│   │   ├── stores/       # Svelte stores for state management
│   │   ├── App.svelte    # Main application component
│   │   └── main.ts       # Application entry point
│   ├── public/           # Static assets
│   ├── package.json      # Frontend dependencies
│   └── tailwind.config.js # Tailwind CSS configuration
├── agents/               # OpenAI Agents implementation
│   ├── __init__.py
│   ├── assistant.py      # Main assistant agent
│   ├── email_agent.py    # Email handling agent
│   └── calendar_agent.py # Calendar management agent
├── services/             # Backend service integrations
│   ├── __init__.py
│   ├── gmail.py          # Gmail API integration
│   ├── calendar.py       # Google Calendar API integration
│   └── web_search.py     # Web search functionality
├── utils/                # Utility functions and helpers
│   ├── __init__.py
│   ├── auth.py           # Authentication utilities
│   └── helpers.py        # General helper functions
├── .env.example          # Example environment variables
├── requirements.txt      # Backend dependencies
└── README.md             # Project documentation
```

## Setup Instructions

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/personal-assistant.git
   cd personal-assistant
   ```

2. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up Google API credentials:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Gmail API and Google Calendar API
   - Configure the OAuth consent screen
   - Create OAuth 2.0 credentials (Web application)
   - Add `http://localhost:8000/auth/callback` as an authorized redirect URI
   - Download the credentials JSON file and save it as `credentials.json` in the project root

4. Create a `.env` file based on `.env.example` and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   ```

### Frontend Setup

1. Install frontend dependencies:
   ```bash
   cd personal_assistant/frontend
   npm install
   ```

2. Build the frontend (production):
   ```bash
   npm run build
   ```

   Or start the development server:
   ```bash
   npm run dev
   ```

### Running the Application

1. Start the backend server:
   ```bash
   cd personal_assistant
   python -m app.main
   ```

2. Access the application:
   - If running in production mode: http://localhost:8000
   - If running in development mode: http://localhost:5173 (frontend) and http://localhost:8000 (API)

## Usage Guide

### First-Time Setup

1. Open the application in your browser
2. Click "Sign in with Google" to authorize the application
3. Grant the necessary permissions for Gmail and Google Calendar access

### Dashboard

The dashboard provides an overview of:
- Recent emails
- Upcoming calendar events
- Quick action buttons for common tasks
- AI assistant suggestions

### Email Management

1. **View Emails**:
   - Navigate to the Email section from the sidebar
   - Browse your inbox, sent items, and other folders
   - Click on an email to view its contents

2. **Send an Email**:
   - Click the "Compose" button
   - Enter recipient(s), subject, and message body
   - Optionally attach files
   - Click "Send"

3. **Search Emails**:
   - Use the search bar at the top of the Email section
   - Enter keywords, sender names, or other search criteria
   - View matching results

### Calendar Management

1. **View Calendar**:
   - Navigate to the Calendar section from the sidebar
   - Toggle between day, week, and month views
   - Click on events to view details

2. **Create an Event**:
   - Click the "New Event" button or click on a time slot
   - Enter event details (title, location, time, description)
   - Add participants if needed
   - Set reminders
   - Click "Save"

3. **Edit or Delete Events**:
   - Click on an existing event
   - Use the edit button to modify details
   - Use the delete button to remove the event

### AI Assistant

1. **Chat with the Assistant**:
   - Navigate to the Assistant section from the sidebar
   - Type your question or request in the chat input
   - The AI will respond with helpful information or perform requested actions

2. **Example Commands**:
   - "Send an email to John about the meeting tomorrow"
   - "Schedule a team lunch next Friday at noon"
   - "Find my recent emails from Sarah"
   - "What's on my calendar for next week?"
   - "Search the web for the latest AI news"

### Mobile Usage

The application is fully responsive and works on mobile devices:
- Use the bottom navigation bar to switch between sections
- All features are optimized for smaller screens
- Enjoy the same functionality on the go

## Troubleshooting

### Authentication Issues
- Ensure your Google API credentials are correctly configured
- Check that the redirect URI matches exactly in your Google Cloud Console settings
- Try clearing your browser cookies and cache

### API Connection Problems
- Verify your OpenAI API key is valid and has sufficient credits
- Check your internet connection
- Ensure the backend server is running

### Frontend Issues
- If the UI doesn't load, make sure the frontend build was successful
- Check browser console for any JavaScript errors
- Try a different browser if problems persist

## Development Guidelines

- **Backend**: Follow PEP 8 style guidelines for Python code
- **Frontend**: Adhere to Svelte best practices
  - Keep components small and focused
  - Use stores for state management
  - Follow proper TypeScript typing
- **CSS**: Use Tailwind utility classes for styling
- **Documentation**: Write clear docstrings and comments
- **Testing**: Add unit tests for new functionality

## License

MIT
