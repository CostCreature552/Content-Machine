"""
Chief Editor Agent.
Polishes content and ensures SEO optimization.
"""

from pathlib import Path

from crewai import Agent


def _load_prompt() -> str:
    """Load the editor prompt from the prompts directory."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "editor_prompt.txt"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8").strip()
    return "You are a Chief Editor and SEO Specialist. Polish content to publication-ready quality."


def create_editor_agent(llm=None) -> Agent:
    """
    Create and return the Chief Editor agent.

    Args:
        llm: Optional LLM instance. If None, uses CrewAI default.

    Returns:
        Agent: Configured editor agent.
    """
    backstory = _load_prompt()

    agent_kwargs = dict(
        role="Chief Editor",
        goal=(
            "Review and polish the draft blog article to publication-ready quality. "
            "Ensure proper heading structure (one H1, 3-5 H2s), keyword density of 1-2%, "
            "readability score in the Flesch 60-70 range, and generate SEO metadata "
            "including meta title and meta description. Output the final article "
            "and metadata in the specified format."
        ),
        backstory=backstory,
        tools=[],
        verbose=True,
        allow_delegation=False,
        max_iter=5,
    )

    if llm is not None:
        agent_kwargs["llm"] = llm

    return Agent(**agent_kwargs)
