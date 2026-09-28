# MPLAD Integrity Engine ???

> An AI-powered integrity monitoring system for India's Members of Parliament Local Area Development (MPLAD) scheme — detecting anomalies, flagging duplicates, and surfacing data quality issues across public fund expenditures.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF?logo=vite)](https://vitejs.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript)](https://www.typescriptlang.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## ?? Overview

The MPLAD Integrity Engine ingests MPLAD scheme data from multiple sources (e-Sakshi, official MPLADS CSV exports), runs them through a multi-signal anomaly detection pipeline, and presents findings through an interactive React dashboard.

**Key capabilities:**
- ?? **Cost anomaly detection** — Flags works priced above statistical thresholds
- ?? **Duplicate detection** — Identifies potentially duplicate works across sources
- ?? **Timeline anomaly detection** — Catches works with impossible or suspicious date sequences
- ?? **Data quality scoring** — Surfaces missing fields, inconsistencies, and incomplete records
- ? **Multi-signal engine** — Combines all signals for a composite risk score per work

---

## ??? Project Structure

```
MPLAD_Integrity_Engine/
+-- backend/                    # FastAPI backend
¦   +-- app/
¦   ¦   +-- adapters/           # Data source adapters (eSakshi, official MPLADS CSV)
¦   ¦   +-- api/                # API versioning & route definitions
¦   ¦   +-- detectors/          # Anomaly detection modules
¦   ¦   ¦   +-- cost_anomaly.py
¦   ¦   ¦   +-- data_quality.py
¦   ¦   ¦   +-- multi_signal_engine.py
¦   ¦   ¦   +-- potential_duplicate.py
¦   ¦   ¦   +-- timeline_anomaly.py
¦   ¦   +-- models/             # SQLAlchemy ORM models
¦   ¦   +-- routers/            # FastAPI route handlers
¦   ¦   +-- services/           # Business logic layer
¦   ¦   +-- utils/              # Shared utilities
¦   +-- main.py                 # Application entrypoint
¦   +-- ingest.py               # Data ingestion script
¦   +-- init_db.py              # Database initialisation
¦   +-- requirements.txt        # Python dependencies
¦
+-- frontend/                   # React + TypeScript dashboard
¦   +-- src/
¦   ¦   +-- components/         # Reusable UI components
¦   ¦   +-- hooks/              # Custom React hooks
¦   ¦   +-- pages/              # Route-level page components
¦   ¦   +-- services/
¦   ¦   ¦   +-- api.ts          # Axios API client (proxied to backend)
¦   ¦   +-- types/              # TypeScript type definitions
¦   ¦   +-- utils/              # Frontend utilities
¦   +-- vite.config.ts          # Vite config (with dev & preview proxy)
¦   +-- package.json
¦
+-- data/                       # Data directory
¦   +-- input/                  # Raw CSV files (large files git-ignored)
¦
+-- sync/                       # Data sync utilities
+-- synthetic/                  # Synthetic data generation scripts
+-- tests/                      # Backend integration & unit tests
¦
+-- demo_scenario.py            # End-to-end demo scenario runner
+-- ingest_real_csv.py          # Real CSV ingestion helper
+-- run_ml_actual.py            # ML pipeline runner
+-- start_backend.bat           # One-click backend start (Windows)
+-- start_frontend.bat          # One-click frontend start (Windows)
+-- README.md
```

---

## ?? Getting Started

### Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.10 or higher |
| Node.js | 18 or higher |
| npm | 9 or higher |
| Git | any |

---

### 1. Clone the Repository

```bash
git clone https://github.com/Abhialert/MPLADS.git
cd MPLADS
```

---

### 2. Backend Setup

```bash
# Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Initialise the database
python init_db.py

# (Optional) Ingest sample data
python ingest.py
```

**Start the backend server:**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Or on Windows, simply double-click **`start_backend.bat`**.

The API will be live at **http://localhost:8000**  
Interactive API docs at **http://localhost:8000/docs**

---

### 3. Frontend Setup

```bash
cd frontend
npm install
```

**Development mode (hot reload):**
```bash
npm run dev
# ? http://localhost:5173
```

**Production preview:**
```bash
npm run build
npm run preview
# ? http://localhost:4173
```

Or on Windows, simply double-click **`start_frontend.bat`**.

---

## ?? API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/status` | System status & stats |
| `GET` | `/coverage` | Detector coverage summary |
| `GET` | `/api/works/` | List all works (paginated) |
| `GET` | `/api/works/{work_id}` | Get a specific work by ID |

Full interactive documentation: **http://localhost:8000/docs**

---

## ?? Running Tests

```bash
# From the project root (with venv active)
cd backend
pytest tests/ -v
```

Or on Windows:
```bat
run_tests.bat
```

---

## ?? Configuration

Create a `.env` file in the `backend/` directory:

```env
# Allowed CORS origins (comma-separated)
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:4173

# Database URL (defaults to SQLite)
DATABASE_URL=sqlite:///./mplad_integrity.db
```

---

## ??? Architecture

```
CSV / eSakshi Data
       ¦
       ?
  Data Adapters  --------------? SQLite Database
       ¦                              ¦
       ?                              ?
Anomaly Detectors              FastAPI Backend
  +-- Cost Anomaly              (REST API :8000)
  +-- Duplicate Detection             ¦
  +-- Timeline Anomaly                ?
  +-- Data Quality            React Dashboard
  +-- Multi-Signal Engine      (Vite :5173 / :4173)
```

---

## ?? Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## ?? License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## ?? Contact

**Abhishek Gupta** — [@Abhialert](https://github.com/Abhialert)  
Project Link: [https://github.com/Abhialert/MPLADS](https://github.com/Abhialert/MPLADS)
