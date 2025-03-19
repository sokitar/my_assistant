"""
Web search service for retrieving information from the internet.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
import aiohttp
import asyncio

from ..utils.helpers import get_env_var

logger = logging.getLogger("assistant.web_search")


class WebSearchService:
    """Service class for web search operations."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the web search service.
        
        Args:
            api_key: API key for the search service (optional)
        """
        self.api_key = api_key or get_env_var("SERPER_API_KEY")
        self.base_url = "https://google.serper.dev/search"
        
    async def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the web for information.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results
        """
        if not self.api_key:
            logger.error("No API key provided for web search")
            return []
        
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "num": num_results
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url, 
                    headers=headers, 
                    json=payload
                ) as response:
                    if response.status != 200:
                        logger.error(f"Search API error: {response.status}")
                        return []
                    
                    data = await response.json()
                    
                    # Extract organic search results
                    organic_results = data.get("organic", [])
                    
                    # Format results
                    formatted_results = []
                    for result in organic_results:
                        formatted_results.append({
                            "title": result.get("title", ""),
                            "link": result.get("link", ""),
                            "snippet": result.get("snippet", ""),
                            "position": result.get("position", 0)
                        })
                    
                    return formatted_results
                    
        except Exception as e:
            logger.error(f"Error during web search: {e}")
            return []
    
    def search_sync(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Synchronous version of the search method.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results
        """
        return asyncio.run(self.search(query, num_results))
    
    async def get_content(self, url: str) -> Optional[str]:
        """
        Get the content of a web page.
        
        Args:
            url: URL of the web page
            
        Returns:
            Content of the web page or None if retrieval failed
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"Error retrieving content: {response.status}")
                        return None
                    
                    return await response.text()
                    
        except Exception as e:
            logger.error(f"Error retrieving content: {e}")
            return None
    
    def get_content_sync(self, url: str) -> Optional[str]:
        """
        Synchronous version of the get_content method.
        
        Args:
            url: URL of the web page
            
        Returns:
            Content of the web page or None if retrieval failed
        """
        return asyncio.run(self.get_content(url))
    
    async def search_and_summarize(self, query: str, num_results: int = 3) -> Dict[str, Any]:
        """
        Search the web and return summarized results.
        
        Args:
            query: Search query
            num_results: Number of results to include
            
        Returns:
            Dictionary with search results and summary
        """
        results = await self.search(query, num_results)
        
        if not results:
            return {
                "query": query,
                "results": [],
                "summary": "No results found."
            }
        
        # Format results for summary
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result["title"],
                "snippet": result["snippet"],
                "url": result["link"]
            })
        
        return {
            "query": query,
            "results": formatted_results,
            "summary": f"Found {len(results)} results for '{query}'."
        }
    
    def search_and_summarize_sync(self, query: str, num_results: int = 3) -> Dict[str, Any]:
        """
        Synchronous version of the search_and_summarize method.
        
        Args:
            query: Search query
            num_results: Number of results to include
            
        Returns:
            Dictionary with search results and summary
        """
        return asyncio.run(self.search_and_summarize(query, num_results))
