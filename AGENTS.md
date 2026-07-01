# AGENTS.md

## Cursor Cloud specific instructions

Content Machine is a single Streamlit app (`app.py`) that runs a 3-agent CrewAI pipeline
(Research → Write → Edit) to generate SEO-optimized blog articles. There is one service to run.

### Environment

- Python dependencies are installed into a virtualenv at `venv/` (gitignored). The startup
  update script recreates it if missing and installs `requirements.txt`. Use `./venv/bin/python`
  (or `source venv/bin/activate`) to get the right interpreter.
- `crewai` resolves to a newer major version (1.x) than the pinned floor (`>=0.86.0`); the
  project imports still work against it.

### Running the app (dev)

- `./venv/bin/python -m streamlit run app.py` — serves on port 8501 (headless mode and port are
  set in `.streamlit/config.toml`). Health check: `curl http://localhost:8501/_stcore/health`.

### API keys (required for generation only)

- Full blog generation calls OpenAI and Serper, so it needs `OPENAI_API_KEY` and `SERPER_API_KEY`,
  supplied via a `.env` file in the repo root or as environment variables. Without both keys the
  sidebar shows red ✗ indicators and the "Generate Blog" button stays disabled.
- The SEO/readability validators (`utils/validators.py`) and exporters (`utils/exporters.py`,
  Markdown/PDF/DOCX) are pure-Python and can be exercised without any API keys.

### Lint / test

- There is no lint config or automated test suite in this repo.
