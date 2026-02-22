# Content Machine 🚀

An AI-powered blog generator that uses a 3-agent CrewAI pipeline to research, write, and edit SEO-optimized blog articles from a single topic input.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                       │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  Topic Input │  │ Tone Selector│  │ Target Audience │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                ORCHESTRATION LAYER (CrewAI)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  Researcher  │──│   Writer     │──│     Editor      │   │
│  │   Agent      │  │   Agent      │  │     Agent       │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌──────────────┐          ┌──────────────┐
│ Serper API   │          │ OpenAI GPT-4o│
│ (Web Search) │          │   (LLM)      │
└──────────────┘          └──────────────┘
```

## Features

- **3-Agent Pipeline**: Research Specialist → Content Drafter → Chief Editor
- **Web Research**: Live Google Search via Serper API for up-to-date facts
- **Tone Selection**: Professional, Conversational, or Academic
- **SEO Analysis**: Keyword density, Flesch readability score, heading structure validation
- **Multi-Format Export**: Download as Markdown, PDF, or DOCX
- **Model Selection**: GPT-4o, GPT-4o-mini, GPT-4-turbo
- **Generation History**: Maintained across sessions via Streamlit session state

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Streamlit | Web UI with session state |
| Orchestration | CrewAI | Multi-agent sequential pipeline |
| LLM | OpenAI GPT-4o | Text generation & reasoning |
| Search | Serper API | Live web search |
| Export | fpdf2, python-docx | PDF & DOCX generation |

## Project Structure

```
content-machine/
├── app.py                      # Streamlit entry point
├── requirements.txt            # Python dependencies
├── .env                        # API keys (not committed)
├── .streamlit/config.toml      # UI theming
├── agents/
│   ├── research_agent.py       # Agent 1: Research (temp 0.3)
│   ├── writer_agent.py         # Agent 2: Writer (temp 0.7)
│   ├── editor_agent.py         # Agent 3: Editor (temp 0.2)
│   └── crew_setup.py           # CrewAI orchestration
├── tools/
│   └── search_tool.py          # SerperDevTool wrapper
├── utils/
│   ├── validators.py           # SEO scoring & readability
│   └── exporters.py            # MD/PDF/DOCX export
└── prompts/
    ├── researcher_prompt.txt
    ├── writer_prompt.txt
    └── editor_prompt.txt
```

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/content-machine.git
cd content-machine
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API keys

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-openai-key-here
SERPER_API_KEY=your-serper-key-here
```

- Get an OpenAI API key at [platform.openai.com](https://platform.openai.com)
- Get a Serper API key at [serper.dev](https://serper.dev) (2,500 free searches)

### 5. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## How It Works

1. **Enter a topic** in the sidebar (e.g., "The Future of AI in Healthcare")
2. **Select tone** (Professional / Conversational / Academic)
3. **Specify target audience** (e.g., "Tech professionals")
4. **Click Generate** — the 3-agent pipeline kicks off:
   - 🔍 **Research Agent** searches the web for facts, keywords, and trends
   - ✍️ **Writer Agent** drafts an ~800 word SEO-optimized article
   - 📝 **Editor Agent** polishes grammar, validates SEO, and generates metadata
5. **View results** across 4 tabs: Article, SEO Metadata, SEO Analysis, Export

## Cost Estimate

| Component | Usage | Cost |
|-----------|-------|------|
| Serper API | ~10 searches | $0.01 |
| GPT-4o Input | ~3,000 tokens | $0.015 |
| GPT-4o Output | ~2,500 tokens | $0.0375 |
| **Total per article** | | **~$0.06** |

## License

MIT
