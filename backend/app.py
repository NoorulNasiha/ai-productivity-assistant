import os
import sys
from flask import Flask, request, jsonify, send_file
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Task
import spacy
import nltk
from nltk.tokenize import word_tokenize
from dateutil import parser as dateparser
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# ensure module path
sys.path.append(os.path.dirname(__file__))

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'tasks.db')
engine = create_engine(f'sqlite:///{DB_PATH}', connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

app = Flask(__name__)

# Load NLTK punkt (safe)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Try to load spaCy model safely once
def load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        # Model not found; proceed without spaCy
        return None
    except Exception:
        return None

nlp = load_spacy_model()

def parse_natural_text(text: str):
    # Tokenize (works with or without spaCy)
    try:
        tokens = word_tokenize(text)
    except Exception:
        tokens = text.split()

    # Try spaCy entities if available
    date_ent = None
    if nlp:
        try:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ in ('DATE', 'TIME'):
                    date_ent = ent.text
                    break
        except Exception:
            date_ent = None

    # Fallback heuristics if spaCy not available or no entity found
    if not date_ent:
        lower = text.lower()
        common_dates = [
            "today", "tomorrow", "tonight", "morning", "afternoon", "evening",
            "next week", "next month",
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
            "am", "pm"
        ]
        for kw in common_dates:
            if kw in lower:
                date_ent = kw
                break

    # Parse deadline
    deadline = None
    if date_ent:
        try:
            dt = dateparser.parse(date_ent, fuzzy=True)
            deadline = dt.isoformat()
        except Exception:
            deadline = date_ent  # store raw string if parsing fails

    # Priority detection
    priority = None
    for t in tokens:
        lt = t.lower()
        if lt in ('high', 'urgent', 'asap', 'critical'):
            priority = 'high'
            break
        if lt in ('medium', 'normal'):
            priority = 'medium'
            break
        if lt in ('low', 'minor', 'later'):
            priority = 'low'
            break

    # Description cleanup
    desc = text
    if date_ent:
        try:
            desc = desc.replace(date_ent, '').strip()
        except Exception:
            pass

    for kw in ('add', 'create', 'schedule', 'set'):
        if desc.lower().startswith(kw):
            desc = desc[len(kw):].strip()

    # Ensure description is non-empty
    if not desc:
        desc = text

    return {'description': desc, 'deadline': deadline, 'priority': priority}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'python_executable': sys.executable,
        'using_venv': 'venv' in sys.executable.lower(),
        'spacy_loaded': bool(nlp),
        'db_path': DB_PATH
    })

@app.route('/add_task', methods=['POST'])
def add_task():
    try:
        data = request.get_json() or {}
        description = data.get('description')
        deadline = data.get('deadline')
        priority = data.get('priority')
        status = data.get('status', 'pending')

        # If only natural text provided, parse it
        if not description and data.get('text'):
            parsed = parse_natural_text(data.get('text'))
            description = parsed.get('description')
            deadline = parsed.get('deadline')
            priority = parsed.get('priority')

        if not description:
            return jsonify({'error': 'description required'}), 400

        session = Session()
        task = Task(description=description, deadline=deadline, priority=priority, status=status)
        session.add(task)
        session.commit()

        return jsonify({
            'id': task.id,
            'description': task.description,
            'deadline': task.deadline,
            'priority': task.priority,
            'status': task.status
        })
    except Exception as e:
        # Don’t crash; return useful info
        return jsonify({'error': 'failed to add task', 'details': str(e)}), 500

@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    session = Session()
    tasks = session.query(Task).all()
    out = [{'id': t.id, 'description': t.description, 'deadline': t.deadline, 'priority': t.priority, 'status': t.status} for t in tasks]
    return jsonify(out)

@app.route('/update_task/<int:id>', methods=['PUT'])
def update_task(id):
    data = request.get_json() or {}
    session = Session()
    task = session.query(Task).get(id)
    if not task:
        return jsonify({'error': 'not found'}), 404
    if 'status' in data:
        task.status = data['status']
    if 'description' in data:
        task.description = data['description']
    if 'deadline' in data:
        task.deadline = data['deadline']
    if 'priority' in data:
        task.priority = data['priority']
    session.commit()
    return jsonify({'message': 'updated'})

@app.route('/delete_task/<int:id>', methods=['DELETE'])
def delete_task(id):
    session = Session()
    task = session.query(Task).get(id)
    if not task:
        return jsonify({'error': 'not found'}), 404
    session.delete(task)
    session.commit()
    return jsonify({'message': 'deleted'})

@app.route('/export/csv', methods=['GET'])
def export_csv():
    session = Session()
    tasks = session.query(Task).all()
    df = pd.DataFrame([{'id': t.id, 'description': t.description, 'deadline': t.deadline, 'priority': t.priority, 'status': t.status} for t in tasks])
    buf = BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return send_file(buf, mimetype='text/csv', as_attachment=True, download_name='tasks.csv')

@app.route('/export/pdf', methods=['GET'])
def export_pdf():
    session = Session()
    tasks = session.query(Task).all()
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    data = [['ID', 'Description', 'Deadline', 'Priority', 'Status']]
    for t in tasks:
        data.append([str(t.id), t.description, t.deadline or '', t.priority or '', t.status])
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    doc.build([table])
    buf.seek(0)
    return send_file(buf, mimetype='application/pdf', as_attachment=True, download_name='tasks.pdf')

if __name__ == '__main__':
    app.run(debug=True)