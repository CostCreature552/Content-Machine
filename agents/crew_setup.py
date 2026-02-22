"""
CrewAI Orchestration Layer.
Sets up the 3-agent sequential pipeline: Research → Write → Edit.
"""

import os
from typing import Dict, Optional

from dotenv import load_dotenv
from crewai import Crew, Task, Process

from agents.research_agent import create_research_agent
from agents.writer_agent import create_writer_agent
from agents.editor_agent import create_editor_agent
from tools.search_tool import get_search_tool

load_dotenv()


def _get_llm(temperature: float = 0.7, model: str = "gpt-4o"):
    """
    Create an LLM instance with the specified temperature.

    Args:
        temperature: The sampling temperature for the LLM.
        model: The model name to use.

    Returns:
        LLM instance configured for CrewAI.
    """
    from crewai import LLM

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        raise ValueError(
            "OPENAI_API_KEY is not configured. "
            "Please set it in your .env file. "
            "Get your key from: https://platform.openai.com/api-keys"
        )

    return LLM(
        model=model,
        temperature=temperature,
        api_key=api_key,
    )


def run_blog_crew(
    topic: str,
    tone: str = "professional",
    target_audience: str = "general readers",
    model: str = "gpt-4o",
    callback=None,
) -> Dict[str, str]:
    """
    Execute the 3-agent blog generation pipeline.

    Args:
        topic: The blog topic to write about.
        tone: Writing tone (conversational, professional, academic).
        target_audience: The intended audience for the blog.
        model: The OpenAI model to use.
        callback: Optional callback function for progress updates.

    Returns:
        Dict with keys: 'research', 'draft', 'final_article', 'metadata'
    """
    results = {}

    # Initialize tools
    search_tool = get_search_tool()

    # Initialize LLMs with different temperatures per agent
    research_llm = _get_llm(temperature=0.3, model=model)
    writer_llm = _get_llm(temperature=0.7, model=model)
    editor_llm = _get_llm(temperature=0.2, model=model)

    # Create agents
    researcher = create_research_agent(search_tool=search_tool, llm=research_llm)
    writer = create_writer_agent(llm=writer_llm)
    editor = create_editor_agent(llm=editor_llm)

    # Define tasks
    research_task = Task(
        description=(
            f"Research the following topic thoroughly: '{topic}'\n\n"
            f"Target Audience: {target_audience}\n\n"
            "Use the search tool to find:\n"
            "1. At least 5 key facts with source attribution\n"
            "2. Primary, secondary, and long-tail keywords\n"
            "3. At least 2 competitor content angles\n"
            "4. Authoritative sources (URLs)\n"
            "5. Emerging trends related to the topic\n"
            "6. Insights about what the target audience cares about\n\n"
            "Return your findings as a structured JSON object as specified in your instructions."
        ),
        expected_output=(
            "A structured JSON object containing: topic, key_facts (array of 5+ facts with sources), "
            "keywords (object with primary, secondary, long_tail arrays), competitor_angles (array), "
            "sources (array of URLs), trends (array), and target_audience_insights (string)."
        ),
        agent=researcher,
    )

    writing_task = Task(
        description=(
            f"Using the research brief provided, write a blog article about: '{topic}'\n\n"
            f"Writing Tone: {tone}\n"
            f"Target Audience: {target_audience}\n\n"
            "Requirements:\n"
            "1. Write approximately 800 words (700-1000 range)\n"
            "2. Use the specified tone throughout\n"
            "3. Include a compelling H1 headline with the primary keyword\n"
            "4. Structure with 3-5 H2 subheadings\n"
            "5. Naturally incorporate keywords from the research\n"
            "6. Include data points and statistics in each section\n"
            "7. Write an engaging introduction with a hook\n"
            "8. End with a conclusion and call-to-action\n"
            "9. Use short paragraphs (2-3 sentences)\n"
            "10. Output in clean Markdown format"
        ),
        expected_output=(
            "A well-structured blog article in Markdown format, approximately 800 words, "
            "with one H1 heading, 3-5 H2 subheadings, engaging introduction, "
            "data-backed body sections, and a conclusion with call-to-action."
        ),
        agent=writer,
        context=[research_task],
    )

    editing_task = Task(
        description=(
            "Review and polish the draft blog article to publication-ready quality.\n\n"
            f"Topic: '{topic}'\n"
            f"Tone: {tone}\n"
            f"Target Audience: {target_audience}\n\n"
            "Perform the following checks and optimizations:\n"
            "1. Fix grammar, spelling, and awkward phrasing\n"
            "2. Validate heading structure (exactly 1 H1, 3-5 H2s)\n"
            "3. Ensure keyword density is 1-2% for primary keywords\n"
            "4. Optimize readability (target Flesch Reading Ease 60-70)\n"
            "5. Ensure sentences average 15-20 words\n"
            "6. Verify all facts from the research are preserved\n"
            "7. Generate SEO metadata (meta title 50-60 chars, meta description 150-160 chars)\n\n"
            "Return your output in the exact format specified in your instructions, "
            "with the article between ---BEGIN ARTICLE--- and ---END ARTICLE--- markers, "
            "and metadata between ---BEGIN METADATA--- and ---END METADATA--- markers."
        ),
        expected_output=(
            "The polished article between ---BEGIN ARTICLE--- and ---END ARTICLE--- markers, "
            "followed by SEO metadata between ---BEGIN METADATA--- and ---END METADATA--- markers "
            "including: meta_title, meta_description, primary_keywords, secondary_keywords, "
            "word_count, estimated_reading_time, readability_notes, and seo_notes."
        ),
        agent=editor,
        context=[research_task, writing_task],
    )

    # Create and run the crew
    crew = Crew(
        agents=[researcher, writer, editor],
        tasks=[research_task, writing_task, editing_task],
        process=Process.sequential,
        verbose=True,
    )

    # Execute the crew
    result = crew.kickoff()

    # Parse the final output
    final_output = str(result)
    parsed = _parse_editor_output(final_output)

    return parsed


def _parse_editor_output(output: str) -> Dict[str, str]:
    """
    Parse the editor's output into article and metadata sections.

    Args:
        output: The raw output from the editor agent.

    Returns:
        Dict with 'article' and 'metadata' keys.
    """
    article = ""
    metadata = ""

    # Try to extract article between markers
    if "---BEGIN ARTICLE---" in output and "---END ARTICLE---" in output:
        start = output.index("---BEGIN ARTICLE---") + len("---BEGIN ARTICLE---")
        end = output.index("---END ARTICLE---")
        article = output[start:end].strip()
    else:
        # If markers not found, treat the whole output as the article
        # but try to separate metadata if present
        if "---BEGIN METADATA---" in output:
            article = output[: output.index("---BEGIN METADATA---")].strip()
        else:
            article = output.strip()

    # Try to extract metadata between markers
    if "---BEGIN METADATA---" in output and "---END METADATA---" in output:
        start = output.index("---BEGIN METADATA---") + len("---BEGIN METADATA---")
        end = output.index("---END METADATA---")
        metadata = output[start:end].strip()
    elif "---BEGIN METADATA---" in output:
        start = output.index("---BEGIN METADATA---") + len("---BEGIN METADATA---")
        metadata = output[start:].strip()

    # Parse metadata into a dict
    metadata_dict = {}
    if metadata:
        for line in metadata.split("\n"):
            line = line.strip()
            if ":" in line:
                key, value = line.split(":", 1)
                metadata_dict[key.strip()] = value.strip()

    return {
        "article": article,
        "metadata_raw": metadata,
        "metadata": metadata_dict,
        "raw_output": output,
    }
