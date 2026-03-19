# ai-productivity-assistant
 AI Productivity Assistant

An AI-powered productivity tool designed to help users manage tasks, streamline workflows, and enhance efficiency with intelligent automation.

---

## 📌 Features
- **Task Management**: Create, update, and track tasks with AI assistance.
- **Smart Scheduling**: Suggests optimal times for meetings and deadlines.
- **Database Integration**: Stores and retrieves user data for personalized productivity.
- **Frontend Dashboard**: User-friendly interface for managing tasks and insights.
- **Backend API**: Handles requests, integrates AI models, and connects to the database.

---

## 📂 Project Structure
```
ai-productivity-assistant/
│── backend/        # API and AI logic
│── database/       # Database models and scripts
│── frontend/      
│── requirements.txt # Python dependencies
│── README.md        # Documentation
│── .gitignore       # Ignored files
```

---

## ⚙️ Installation

### Prerequisites
- **Python 3.9+**
- **Node.js & npm** (for frontend)
- **Database**: SQLite/PostgreSQL/MySQL (depending on configuration)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/NoorulNasiha/ai-productivity-assistant.git
   cd ai-productivity-assistant
   ```

2. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```bash
   python database/init_db.py
   ```

4. Run the backend server:
   ```bash
   python backend/app.py
   ```

5. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   npm start
   ```

---

## 🚀 Usage
- Access the **frontend dashboard** via `http://localhost:3000`.
- Use the **backend API** at `http://localhost:5000` for task management and AI features.
- Integrate with productivity tools (e.g., calendars, reminders).

---

## 🛠️ Tech Stack
- **Backend**: Python (Flask/FastAPI)
- **Database**: SQLite/PostgreSQL/MySQL
- **AI Models**: Python-based NLP/ML libraries

## 👩‍💻 Author
Developed by **NoorulNasih


