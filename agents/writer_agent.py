"""
Content Drafter Agent.
Transforms research briefs into engaging blog narratives.
"""

from pathlib import Path

from crewai import Agent


def _load_prompt() -> str:
    """Load the writer prompt from the prompts directory."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "writer_prompt.txt"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8").strip()
    return "You are a Senior Content Writer. Transform research into engaging blog articles."


def create_writer_agent(llm=None) -> Agent:
    """
    Create and return the Content Drafter agent.

    Args:
        llm: Optional LLM instance. If None, uses CrewAI default.

    Returns:
        Agent: Configured writer agent.
    """
    backstory = _load_prompt()

    agent_kwargs = dict(
        role="Content Drafter",
        goal=(
            "Transform the research brief into a compelling, well-structured "
            "blog article of approximately 800 words. Apply the specified tone "
            "and writing style. Ensure the content is engaging, informative, "
            "and naturally incorporates the researched keywords."
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
