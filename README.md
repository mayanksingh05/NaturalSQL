# ⚡ NaturalSQL: AI-Powered Natural Language to SQL Analytics Engine

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![SQLite](https://img.shields.io/badge/SQLite-Read--Only_Sandbox-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-1.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **Ask questions. Get SQL. Run instant visual insights.**  
> NaturalSQL converts plain English business questions into secure, optimized SQL queries and renders interactive Plotly visualizations across CSV, Excel (multi-sheet), and SQLite databases.

---

### 🌐 Live Production Links
- **Interactive Web App (Frontend):** [https://naturalsql.streamlit.app/](https://naturalsql.streamlit.app/)
- **RESTful API Service (Backend):** [https://naturalsql-backend.onrender.com/](https://naturalsql-backend.onrender.com/)
- **API Health Check:** [https://naturalsql-backend.onrender.com/health](https://naturalsql-backend.onrender.com/health)

---

## 📸 Overview & Key Features

NaturalSQL bridges the gap between raw datasets and non-technical stakeholders. Instead of writing complex queries or manual pivot tables, users can talk to their data in plain English.

- 🔑 **Bring Your Own Key (BYOK):** Zero telemetry of your private LLM credentials. Keys remain strictly in volatile memory and are never persisted to disk or databases.
- 📁 **Universal Data Ingestion:** Upload `.csv`, multi-sheet `.xlsx` / `.xls`, or SQLite `.db` / `.sqlite` files up to 100MB.
- 📑 **Automatic Schema Discovery:** Real-time extraction and grouping of table names, column types, and relational boundaries with sidebar schema inspection.
- 🧠 **Context-Aware SQL Generation:** Dynamically structured prompts fed into Google Gemini 1.5 with support for multi-table `JOIN`s, aggregations, and Common Table Expressions (CTEs).
- 🛡️ **Two-Tier Security Sandbox:**
  1. **Static AST Analysis:** Read-only query filter strictly allowing `SELECT` and `WITH` statements, rejecting destructive keywords (`DROP`, `DELETE`, `UPDATE`, `ALTER`, etc.).
  2. **Engine-Level Enforcement:** SQLite database connections opened via URI read-only flag (`?mode=ro`), guaranteeing immutable disk state.
- 📊 **Smart Visualization Engine:** Automatically inspects the schema and result distribution of executed queries to generate Plotly interactive Line charts, Bar charts, or tabular breakdowns.
- 📥 **One-Click Export:** Download executed SQL query results as standardized CSV files.
- 🧹 **Zero-Leak Session Isolation:** Each browser tab generates a cryptographic UUIDv4 session namespace with automatic background garbage collection of expired session databases.

---

## 🏛️ System Architecture

NaturalSQL employs a modern decoupled client-server microservices pattern:

```text
┌─────────────────────────────────┐
│     User Web Browser            │
│  (Desktop / Mobile Responsive)  │
└────────────────▲────────────────┘
                 │ HTTPS
┌────────────────▼──────────────────────────────────────────────┐
│           Streamlit Cloud Frontend (UI Layer)                 │
│  - Reactive Chat Interface & Sidebar Schema Inspector        │
│  - Plotly Express Adaptive Charts                             │
│  - Session State & In-Memory Gemini Key Isolation             │
└────────────────▲──────────────────────────────────────────────┘
                 │ RESTful API Calls (JSON & Multipart Form-Data)
┌────────────────▼──────────────────────────────────────────────┐
│           Render Web Service (FastAPI Engine Layer)           │
│  - Endpoints: /upload, /ask, /execute, /health                │
│  - CORS Middleware & Path Traversal Guards                    │
│  - Asynchronous Background Session Cleanup Tasks              │
└────────────▲──────────────────────────────────────▲───────────┘
             │                                      │
┌────────────▼──────────────┐         ┌─────────────▼───────────┐
│     Google Gemini API     │         │   Ephemeral SQLite DB   │
│  - Gemini 1.5 Flash / Pro │         │  - Read-Only URI Mode   │
│  - Strict SQL Generation  │         │  - 5000 Max Row Guard   │
└───────────────────────────┘         └─────────────────────────┘
```

---

## 📂 Repository Structure

```text
NaturalSQL/
├── backend/
│   ├── llm/
│   │   ├── base.py                 # Abstract base class for LLM providers
│   │   ├── gemini_provider.py      # Google Gemini 1.5 Flash/Pro integration
│   │   └── prompt_builder.py       # Multi-table dynamic schema prompt builder
│   ├── database.py                 # SQLite engine, Excel/CSV ingestion, URI security
│   ├── main.py                     # FastAPI app entry point, CORS & health routes
│   ├── routes.py                   # API router (/upload, /ask, /execute)
│   └── sql_service.py              # SQL validation, AST sanitization & extraction
├── frontend/
│   ├── api_client.py               # Resilient HTTP client with retry & timeout logic
│   ├── charts.py                   # Heuristic Plotly visualization engine
│   ├── streamlit_app.py            # Main interactive Streamlit application
│   └── ui_components.py            # Custom CSS, chat bubbles & SQL preview cards
├── .streamlit/
│   └── config.toml                 # Configures 100MB max file upload limit
├── .gitignore                      # Excludes uploads, db files, secrets & venv
├── .python-version                 # Pins Python 3.11.9 for deterministic cloud builds
├── Procfile                        # Uvicorn production command for Render / PaaS
├── requirements.txt                # Production dependency declarations
└── README.md                       # Project documentation
```

---

## ⚡ Quick Start: Running Locally

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/mayanksingh05/NaturalSQL.git
cd NaturalSQL
```

### 3. Create & Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Launch Backend Service
```bash
uvicorn backend.main:app --reload --port 8000
```
*API docs will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).*

### 6. Launch Frontend (In a separate terminal)
```bash
streamlit run frontend/streamlit_app.py
```
*The app will automatically open at [http://localhost:8501](http://localhost:8501).*

---

## 📡 REST API Reference

| Method | Endpoint | Description | Payload / Parameters |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Healthcheck & uptime monitor | None |
| `POST` | `/upload` | Ingests CSV, Excel, or SQLite DB | `file` (multipart), `session_id` (string) |
| `POST` | `/ask` | Converts English query to valid SQL | `question`, `api_key`, `session_id`, `schema_data` |
| `POST` | `/execute` | Runs SQL query against sandboxed DB | `query` (SQL), `session_id` (string) |

---

## 🔒 Security Design Highlights

1. **Read-Only SQLite Engine (`?mode=ro`):** Even if an adversarial prompt bypasses static string guards, SQLite's core engine physically prohibits file modifications.
2. **Zero Storage of API Keys:** User Gemini API keys are processed strictly in transit and volatile application memory.
3. **Strict Path Normalization:** File uploads use sanitized basenames and UUID validation to eliminate directory traversal (`../`) attacks.
4. **Memory Guardrails:** Result sets are capped at 5,000 records to prevent memory exhaustion and Denial-of-Service on free cloud tiers.
5. **Session Pruning:** Background asynchronous tasks automatically purge SQLite files older than 2 hours.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
