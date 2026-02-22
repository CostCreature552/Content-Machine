"""
Research Specialist Agent.
Gathers verifiable data, trends, and competitor angles using web search.
"""

import os
from pathlib import Path

from crewai import Agent


def _load_prompt() -> str:
    """Load the researcher prompt from the prompts directory."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "researcher_prompt.txt"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8").strip()
    return "You are a Senior Research Specialist. Conduct thorough research and return structured JSON findings."


def create_research_agent(search_tool, llm=None) -> Agent:
    """
    Create and return the Research Specialist agent.

    Args:
        search_tool: The SerperDevTool instance for web searching.
        llm: Optional LLM instance. If None, uses CrewAI default.

    Returns:
        Agent: Configured research agent.
    """
    backstory = _load_prompt()

    agent_kwargs = dict(
        role="Research Specialist",
        goal=(
            "Conduct comprehensive research on the given topic. "
            "Gather verifiable facts, identify trending keywords, "
            "analyze competitor content angles, and compile authoritative sources. "
            "Return findings as a structured JSON brief."
        ),
        backstory=backstory,
        tools=[search_tool],
        verbose=True,
        allow_delegation=False,
        max_iter=10,
        max_rpm=10,
    )

    if llm is not None:
        agent_kwargs["llm"] = llm

    return Agent(**agent_kwargs)
