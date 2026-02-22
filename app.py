"""
Content Machine — AI-Powered Blog Generator
Main Streamlit application entry point.

A 3-agent pipeline (Research → Write → Edit) powered by CrewAI and GPT-4o
that generates SEO-optimized blog articles from a single topic input.
"""

import os
import sys
import time
import json
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ─── Page Configuration ───────────────────────────────────────────────────────

st.set_page_config(
    page_title="Content Machine — AI Blog Generator",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #FF6B6B, #FF8E53);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #888;
        margin-top: 0;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #1A1F2E;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #2A2F3E;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Session State Initialization ─────────────────────────────────────────────

if "generation_history" not in st.session_state:
    st.session_state.generation_history = []
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<p class="main-header">✍️ Content Machine</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Blog Generator</p>', unsafe_allow_html=True)

    st.divider()

    # API Key Status
    st.markdown("### 🔑 API Configuration")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    serper_key = os.getenv("SERPER_API_KEY", "")

    openai_configured = openai_key and openai_key != "your_openai_api_key_here"
    serper_configured = serper_key and serper_key != "your_serper_api_key_here"

    col1, col2 = st.columns(2)
    with col1:
        if openai_configured:
            st.success("OpenAI ✓", icon="✅")
        else:
            st.error("OpenAI ✗", icon="❌")
    with col2:
        if serper_configured:
            st.success("Serper ✓", icon="✅")
        else:
            st.error("Serper ✗", icon="❌")

    if not openai_configured or not serper_configured:
        st.warning("Configure API keys in the `.env` file to get started.")
        with st.expander("How to configure API keys"):
            st.code(
                '# .env file\n'
                'OPENAI_API_KEY=sk-your-key-here\n'
                'SERPER_API_KEY=your-serper-key-here',
                language="bash",
            )
            st.markdown(
                "- [Get OpenAI API Key](https://platform.openai.com/api-keys)\n"
                "- [Get Serper API Key](https://serper.dev/)"
            )

    st.divider()

    # Input Controls
    st.markdown("### 📝 Blog Configuration")

    topic = st.text_area(
        "Blog Topic",
        placeholder="e.g., The Future of Remote Work in 2025",
        help="Enter the topic you want to write about. Be specific for better results.",
        height=80,
    )

    tone = st.selectbox(
        "Writing Tone",
        options=["Professional", "Conversational", "Academic"],
        index=0,
        help="Select the writing style for your blog article.",
    )

    target_audience = st.text_input(
        "Target Audience",
        placeholder="e.g., Tech professionals, Small business owners",
        value="General readers",
        help="Describe who this article is for.",
    )

    st.divider()

    # Advanced Settings
    with st.expander("⚙️ Advanced Settings"):
        model = st.selectbox(
            "LLM Model",
            options=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
            index=0,
            help="Select the OpenAI model to use.",
        )

    st.divider()

    # Generate Button
    generate_disabled = not (openai_configured and serper_configured and topic.strip())
    generate_button = st.button(
        "🚀 Generate Blog",
        type="primary",
        use_container_width=True,
        disabled=generate_disabled,
    )

    if not topic.strip() and openai_configured and serper_configured:
        st.caption("Enter a topic to enable generation.")

    st.divider()

    # History
    if st.session_state.generation_history:
        st.markdown("### 📚 History")
        for i, entry in enumerate(reversed(st.session_state.generation_history[-5:])):
            with st.expander(f"📄 {entry['topic'][:40]}...", expanded=False):
                st.caption(f"🕐 {entry['timestamp']}")
                st.caption(f"🎨 Tone: {entry['tone']}")
                if st.button(f"Load", key=f"load_{i}"):
                    st.session_state.current_result = entry["result"]
                    st.rerun()

    # Cost Estimate
    st.divider()
    st.markdown("### 💰 Estimated Cost")
    st.caption("~$0.06 per article")
    st.caption("Based on GPT-4o pricing + Serper API")

# ─── Main Content Area ────────────────────────────────────────────────────────

# Header
st.markdown('<p class="main-header">✍️ Content Machine</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Generate SEO-optimized blog articles with a 3-agent AI pipeline</p>',
    unsafe_allow_html=True,
)

# ─── Generation Logic ─────────────────────────────────────────────────────────

if generate_button and topic.strip():
    st.session_state.is_generating = True
    st.session_state.current_result = None

    with st.status("🚀 Generating your blog article...", expanded=True) as status:
        try:
            # Step 1: Research
            st.write("🔍 **Agent 1: Research Specialist** — Gathering facts and trends...")
            start_time = time.time()

            from agents.crew_setup import run_blog_crew

            result = run_blog_crew(
                topic=topic.strip(),
                tone=tone.lower(),
                target_audience=target_audience.strip(),
                model=model,
            )

            elapsed = time.time() - start_time

            # Store result
            st.session_state.current_result = result
            st.session_state.current_result["topic"] = topic.strip()
            st.session_state.current_result["tone"] = tone
            st.session_state.current_result["target_audience"] = target_audience
            st.session_state.current_result["elapsed_time"] = round(elapsed, 1)

            # Add to history
            st.session_state.generation_history.append(
                {
                    "topic": topic.strip(),
                    "tone": tone,
                    "target_audience": target_audience,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "result": st.session_state.current_result,
                }
            )

            status.update(
                label=f"✅ Blog generated successfully in {round(elapsed, 1)}s!",
                state="complete",
                expanded=False,
            )

        except ValueError as e:
            status.update(label="❌ Configuration Error", state="error")
            st.error(f"**Configuration Error:** {str(e)}")
            st.session_state.is_generating = False

        except Exception as e:
            status.update(label="❌ Generation Failed", state="error")
            st.error(f"**Error:** {str(e)}")
            st.info(
                "💡 **Troubleshooting tips:**\n"
                "- Check that your API keys are valid\n"
                "- Ensure you have sufficient API credits\n"
                "- Try a simpler topic\n"
                "- Check your internet connection"
            )
            st.session_state.is_generating = False

    st.session_state.is_generating = False

# ─── Display Results ──────────────────────────────────────────────────────────

if st.session_state.current_result:
    result = st.session_state.current_result
    article = result.get("article", "")
    metadata = result.get("metadata", {})

    # Metrics Row
    st.divider()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        word_count = metadata.get("word_count", str(len(article.split())))
        st.metric("📝 Word Count", word_count)
    with col2:
        reading_time = metadata.get("estimated_reading_time", f"{max(1, len(article.split()) // 200)} min")
        st.metric("⏱️ Reading Time", reading_time)
    with col3:
        st.metric("🎨 Tone", result.get("tone", "N/A"))
    with col4:
        elapsed = result.get("elapsed_time", "N/A")
        st.metric("⚡ Generation Time", f"{elapsed}s" if elapsed != "N/A" else "N/A")

    st.divider()

    # Tabbed Content Display
    tab_article, tab_metadata, tab_seo, tab_export = st.tabs(
        ["📄 Article", "📊 SEO Metadata", "🔍 SEO Analysis", "📥 Export"]
    )

    # ── Tab 1: Article ────────────────────────────────────────────────────────
    with tab_article:
        if article:
            st.markdown(article)
        else:
            st.warning("No article content was generated. Check the raw output below.")
            st.code(result.get("raw_output", "No output available"), language="markdown")

    # ── Tab 2: SEO Metadata ───────────────────────────────────────────────────
    with tab_metadata:
        if metadata:
            st.markdown("### SEO Metadata")

            if "meta_title" in metadata:
                st.markdown("**Meta Title:**")
                st.info(metadata["meta_title"])
                title_len = len(metadata["meta_title"])
                if 50 <= title_len <= 60:
                    st.success(f"✅ Title length: {title_len} characters (optimal: 50-60)")
                else:
                    st.warning(f"⚠️ Title length: {title_len} characters (optimal: 50-60)")

            if "meta_description" in metadata:
                st.markdown("**Meta Description:**")
                st.info(metadata["meta_description"])
                desc_len = len(metadata["meta_description"])
                if 150 <= desc_len <= 160:
                    st.success(f"✅ Description length: {desc_len} characters (optimal: 150-160)")
                else:
                    st.warning(f"⚠️ Description length: {desc_len} characters (optimal: 150-160)")

            if "primary_keywords" in metadata:
                st.markdown("**Primary Keywords:**")
                st.code(metadata["primary_keywords"])

            if "secondary_keywords" in metadata:
                st.markdown("**Secondary Keywords:**")
                st.code(metadata["secondary_keywords"])

            if "readability_notes" in metadata:
                st.markdown("**Readability Notes:**")
                st.caption(metadata["readability_notes"])

            if "seo_notes" in metadata:
                st.markdown("**SEO Notes:**")
                st.caption(metadata["seo_notes"])
        else:
            st.info("No structured metadata was extracted. Check the raw output in the Article tab.")
            if result.get("metadata_raw"):
                st.code(result["metadata_raw"])

    # ── Tab 3: SEO Analysis ───────────────────────────────────────────────────
    with tab_seo:
        if article:
            st.markdown("### Automated SEO Analysis")
            st.caption("Independent analysis of the generated article using built-in validators.")

            try:
                from utils.validators import SEOValidator

                # Extract keywords from metadata if available
                keywords = []
                if "primary_keywords" in metadata:
                    keywords.extend(
                        [k.strip() for k in metadata["primary_keywords"].split(",")]
                    )

                validator = SEOValidator(content=article, keywords=keywords)
                report = validator.get_full_report()

                # Overall Score
                score = report["overall_score"]
                if score >= 80:
                    st.success(f"### Overall SEO Score: {score}/100 🎉")
                elif score >= 60:
                    st.warning(f"### Overall SEO Score: {score}/100 ⚠️")
                else:
                    st.error(f"### Overall SEO Score: {score}/100 ❌")

                # Detailed Metrics
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**📝 Content Metrics**")
                    st.metric("Word Count", report["word_count"])
                    st.metric("Avg Sentence Length", f"{report['avg_sentence_length']} words")
                    st.metric("Reading Time", report["estimated_reading_time"])

                with col2:
                    st.markdown("**📖 Readability**")
                    readability = report["readability"]
                    if readability["flesch_reading_ease"] is not None:
                        st.metric("Flesch Reading Ease", readability["flesch_reading_ease"])
                        st.metric("Grade Level", readability["grade_level"])
                        st.caption(readability["interpretation"])
                    else:
                        st.caption("Install `textstat` for readability analysis")

                with col3:
                    st.markdown("**🏗️ Heading Structure**")
                    headings = report["heading_structure"]
                    st.metric("H1 Headings", headings["h1_count"])
                    st.metric("H2 Headings", headings["h2_count"])
                    if headings["is_valid"]:
                        st.success("Structure: Valid ✓")
                    else:
                        st.warning("Structure: Needs improvement")

                # Keyword Density
                if report["keyword_density"]:
                    st.markdown("**🔑 Keyword Density**")
                    for kw, density in report["keyword_density"].items():
                        if 1.0 <= density <= 2.0:
                            st.success(f"'{kw}': {density}% ✓")
                        elif density < 1.0:
                            st.warning(f"'{kw}': {density}% (low — target 1-2%)")
                        else:
                            st.error(f"'{kw}': {density}% (high — risk of keyword stuffing)")

                # Issues
                if report["issues"]:
                    st.markdown("**⚠️ Issues Found**")
                    for issue in report["issues"]:
                        st.warning(issue)

            except Exception as e:
                st.error(f"Error running SEO analysis: {str(e)}")
        else:
            st.info("Generate an article first to see SEO analysis.")

    # ── Tab 4: Export ─────────────────────────────────────────────────────────
    with tab_export:
        if article:
            st.markdown("### Export Your Article")
            st.caption("Download your blog article in your preferred format.")

            col1, col2, col3 = st.columns(3)

            # Markdown Export
            with col1:
                st.markdown("#### 📝 Markdown")
                st.caption("Best for CMS platforms, GitHub, and static site generators.")
                from utils.exporters import export_markdown

                md_bytes = export_markdown(article)
                st.download_button(
                    label="Download .md",
                    data=md_bytes,
                    file_name=f"blog_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

            # PDF Export
            with col2:
                st.markdown("#### 📕 PDF")
                st.caption("Best for sharing, printing, and archiving.")
                try:
                    from utils.exporters import export_pdf

                    pdf_bytes = export_pdf(article, title=result.get("topic", "Blog Article"))
                    st.download_button(
                        label="Download .pdf",
                        data=pdf_bytes,
                        file_name=f"blog_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except ImportError:
                    st.warning("Install `fpdf2` for PDF export: `pip install fpdf2`")

            # DOCX Export
            with col3:
                st.markdown("#### 📘 Word Document")
                st.caption("Best for editing in Microsoft Word or Google Docs.")
                try:
                    from utils.exporters import export_docx

                    docx_bytes = export_docx(article, title=result.get("topic", "Blog Article"))
                    st.download_button(
                        label="Download .docx",
                        data=docx_bytes,
                        file_name=f"blog_{datetime.now().strftime('%Y%m%d_%H%M')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )
                except ImportError:
                    st.warning("Install `python-docx` for DOCX export: `pip install python-docx`")

            # Full output with metadata
            st.divider()
            with st.expander("📋 Full Raw Output (Article + Metadata)"):
                st.code(result.get("raw_output", "No raw output available"), language="markdown")
        else:
            st.info("Generate an article first to export.")

# ─── Empty State ──────────────────────────────────────────────────────────────

elif not st.session_state.is_generating:
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            ### 🔍 Research
            Agent 1 searches the web for facts, trends,
            and competitor angles using Serper API.
            """
        )

    with col2:
        st.markdown(
            """
            ### ✏️ Write
            Agent 2 transforms research into an engaging
            ~800 word blog article in your chosen tone.
            """
        )

    with col3:
        st.markdown(
            """
            ### 🎯 Edit & Optimize
            Agent 3 polishes the draft, validates SEO,
            and generates metadata for search visibility.
            """
        )

    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; padding: 2rem;">
            <h3>👈 Configure your blog topic in the sidebar and click Generate</h3>
            <p>Each article costs approximately $0.06 using GPT-4o</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─── Footer ──────────────────────────────────────────────────────────────────

st.markdown("---")
st.caption(
    "Content Machine v1.0 — Powered by CrewAI, GPT-4o, and Serper API | "
    "Built with Streamlit"
)
