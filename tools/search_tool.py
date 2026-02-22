"""
Serper API Search Tool wrapper for CrewAI agents.
Provides Google Search integration for the Research Specialist agent.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_search_tool():
    """
    Initialize and return the SerperDevTool for web searching.
    
    Returns:
        SerperDevTool: Configured search tool instance.
    
    Raises:
        ValueError: If SERPER_API_KEY is not set in environment.
    """
    serper_api_key = os.getenv("SERPER_API_KEY")
    
    if not serper_api_key or serper_api_key == "your_serper_api_key_here":
        raise ValueError(
            "SERPER_API_KEY is not configured. "
            "Please set it in your .env file. "
            "Get your key from: https://serper.dev/"
        )
    
    # Set the environment variable for crewai-tools
    os.environ["SERPER_API_KEY"] = serper_api_key
    
    from crewai_tools import SerperDevTool
    
    search_tool = SerperDevTool(
        n_results=10,
    )
    
    return search_tool
