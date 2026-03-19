# AI-Powered Productivity Assistant

This project includes:
- Backend Flask API with SQLite + SQLAlchemy and NLP parsing (spaCy + NLTK).
- Streamlit dashboard frontend with task list, completion metrics, weekly chart, and export buttons.
- CSV and PDF export endpoints.

Quick start

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Download spaCy model and NLTK data:

```powershell
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt')"
```

3. Run the backend API (from project root):

```powershell
python backend\app.py
```

4. In another terminal, run the Streamlit dashboard:

```powershell
streamlit run frontend\app.py
```

Notes
- The backend creates `tasks.db` in the project root on first run.
- Use the Streamlit UI to add tasks via natural language (e.g., `Add meeting tomorrow at 10 AM`).
- Exports: use dashboard buttons to download CSV or PDF.

Files created
- `backend/app.py` - Flask API and NLP parsing
- `backend/models.py` - SQLAlchemy model
- `frontend/app.py` - Streamlit dashboard
- `database/schema.sql` - SQL schema for tasks
- `requirements.txt` - Python deps

