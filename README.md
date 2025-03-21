# Personal Assistant

A super sleek, compact, and efficient application that uses AI Agents to help manage your Gmail and Google Calendar. This application provides an intuitive interface for interacting with your emails and calendar events through natural language.

## Features

- **Email Management**: View recent emails and send new emails using natural language commands
- **Calendar Management**: View upcoming events and create new calendar events

## Architecture

The application follows clean architecture principles with a focus on maintainability and efficiency:

- **Frontend**: Gradio-based UI with responsive design
- **Backend**: Python services for Google API integration and OpenAI Agents SDK

## Setup Instructions

### Prerequisites

- Python 3.10+
- Poetry (dependency management)
- Google Cloud Platform account with Gmail and Calendar APIs enabled
- OpenAI API key

### Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd gmail-calendar-agent
   ```

2. Install dependencies with Poetry:

   ```bash
   # Install Poetry if you don't have it
   # curl -sSL https://install.python-poetry.org | python3 -

   # Install dependencies
   poetry install
   ```

3. Set up environment variables:

   - Copy `.env.example` to `.env`
   - Fill in your OpenAI API key and Google OAuth credentials

   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. Run the application:

   ```bash
   # Activate the Poetry virtual environment
   poetry shell

   # Run the app
   poetry run start
   # Or directly with Python
   python app.py
   ```

5. Open your browser and navigate to `http://localhost:8000`

### Google API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Gmail API and Google Calendar API
4. Configure the OAuth consent screen
5. Create OAuth 2.0 credentials (Web application type)
6. Add `http://localhost:8000/oauth2callback` as an authorized redirect URI
7. Copy the client ID and client secret to your `.env` file

## Usage

1. Launch the application and authenticate with your Google account
2. Use the chat interface to interact with the assistant
3. Example commands:
   - "Show me my recent emails"
   - "Send an email to example@example.com about the project update"
   - "What meetings do I have tomorrow?"
   - "Schedule a meeting with John on Friday at 2pm"

## Project Structure

```
gmail-calendar-agent/
├── app.py                 # Main application entry point
├── pyproject.toml         # Poetry configuration and dependencies
├── .env.example           # Example environment variables
├── README.md              # Project documentation
├── assets/                # Static assets
├── logs/                  # Application logs
├── tokens/                # Authentication tokens (gitignored)
└── src/                   # Source code
    ├── config.py          # Application configuration
    ├── ui/                # Gradio UI components
    │   └── interface.py   # Main UI interface
    ├── services/          # Business logic
    │   ├── agent_service.py  # OpenAI agent service
    │   └── google_api.py     # Google API integration
    └── utils/             # Utility functions
        └── logger.py      # Logging configuration
```

## Development

### Code Style

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **flake8**: Linting

Run the formatting tools:

```bash
# Format code
poetry run black .

# Sort imports
poetry run isort .

# Type checking
poetry run mypy .

# Linting
poetry run flake8
```

### Testing

Run tests with pytest:

```bash
poetry run pytest
```

## Security Notes

- Authentication tokens are stored locally in the `tokens/` directory
- The application uses OAuth 2.0 for secure authentication
- API keys and secrets are stored in the `.env` file (not committed to version control)
- Only necessary API scopes are requested

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
