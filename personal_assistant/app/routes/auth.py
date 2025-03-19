"""
Authentication routes for the personal assistant.
"""
import os
import logging
from typing import Dict, Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Request, HTTPException, Depends, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from ...utils.auth import (
    get_oauth_flow,
    get_credentials,
    save_credentials,
    get_user_info,
    revoke_token
)

# Configure logging
logger = logging.getLogger("app.routes.auth")

# Create router
router = APIRouter(prefix="/auth", tags=["auth"])


class AuthStatusResponse(BaseModel):
    """Authentication status response model."""
    gmail_authenticated: bool
    calendar_authenticated: bool
    user_info: Optional[Dict] = None


@router.get("/login")
async def login(request: Request, service: str = "all"):
    """
    Start the OAuth2 login flow for Google services.
    
    Args:
        request: The request object
        service: The service to authenticate (gmail, calendar, or all)
        
    Returns:
        Redirect to Google OAuth2 authorization URL
    """
    try:
        # Determine the scopes based on the requested service
        scopes = []
        if service == "gmail" or service == "all":
            scopes.extend([
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/gmail.modify"
            ])
        
        if service == "calendar" or service == "all":
            scopes.extend([
                "https://www.googleapis.com/auth/calendar.readonly",
                "https://www.googleapis.com/auth/calendar.events"
            ])
        
        if not scopes:
            raise HTTPException(status_code=400, detail=f"Invalid service: {service}")
        
        # Create the OAuth2 flow
        flow = get_oauth_flow(scopes)
        
        # Generate the authorization URL
        # The redirect_uri should match what's configured in the Google Cloud Console
        redirect_uri = f"{request.url.scheme}://{request.url.netloc}/auth/callback"
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent"
        )
        
        # Store the flow state in the session or a temporary storage
        # This is a simplified example - in a real app, you'd need to store the state securely
        # and retrieve it in the callback
        
        return RedirectResponse(auth_url)
    
    except Exception as e:
        logger.error(f"Error starting OAuth flow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/callback")
async def callback(request: Request, code: str, state: Optional[str] = None):
    """
    Handle the OAuth2 callback from Google.
    
    Args:
        request: The request object
        code: The authorization code from Google
        state: The state parameter from the authorization request
        
    Returns:
        Redirect to the home page after successful authentication
    """
    try:
        # Retrieve the flow from the session or temporary storage
        # This is a simplified example - in a real app, you'd need to retrieve the state securely
        
        # Create a new flow with the same scopes
        # In a real app, you would retrieve the original flow with its state
        scopes = [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.modify",
            "https://www.googleapis.com/auth/calendar.readonly",
            "https://www.googleapis.com/auth/calendar.events"
        ]
        flow = get_oauth_flow(scopes)
        
        # Set the redirect URI to match the one used in the authorization request
        redirect_uri = f"{request.url.scheme}://{request.url.netloc}/auth/callback"
        flow.redirect_uri = redirect_uri
        
        # Exchange the authorization code for credentials
        flow.fetch_token(code=code)
        
        # Save the credentials
        save_credentials(flow.credentials)
        
        # Redirect to the home page
        return RedirectResponse("/")
    
    except Exception as e:
        logger.error(f"Error handling OAuth callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=AuthStatusResponse)
async def auth_status():
    """
    Check authentication status for Google services.
    
    Returns:
        Authentication status for Gmail and Calendar
    """
    try:
        gmail_creds = get_credentials(["https://www.googleapis.com/auth/gmail.readonly"])
        calendar_creds = get_credentials(["https://www.googleapis.com/auth/calendar.readonly"])
        
        # Get user info if authenticated
        user_info = None
        if gmail_creds and gmail_creds.valid:
            user_info = get_user_info(gmail_creds)
        
        return AuthStatusResponse(
            gmail_authenticated=gmail_creds is not None and gmail_creds.valid,
            calendar_authenticated=calendar_creds is not None and calendar_creds.valid,
            user_info=user_info
        )
    except Exception as e:
        logger.error(f"Error checking auth status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout():
    """
    Revoke the Google OAuth2 tokens and log out.
    
    Returns:
        Success message
    """
    try:
        # Get the credentials
        creds = get_credentials([])
        
        if creds and creds.valid:
            # Revoke the token
            revoke_token(creds)
            
            return {"message": "Successfully logged out"}
        else:
            return {"message": "No active session to log out from"}
    
    except Exception as e:
        logger.error(f"Error logging out: {e}")
        raise HTTPException(status_code=500, detail=str(e))
