# MPLAD Integrity Engine 🛡️🏛️

> An AI-powered civic integrity and expenditure monitoring observatory for India's Members of Parliament Local Area Development Scheme (MPLADS) — tracking real fund allocations, district sanction velocity, and multi-signal anomalies across 60,362+ verified official records.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF?logo=vite)](https://vitejs.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript)](https://www.typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-38B2AC?logo=tailwind-css)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📊 Real-Time Observatory Metrics (Full Dataset)

| Metric | Official Verified Value | Insight / Audit Observation |
| :--- | :--- | :--- |
| **Total Works Ingested** | **60,362 projects** | Pan-India coverage across all States & Union Territories |
| **Total Recommended Capital** | **₹34,987.47 Cr** | Cumulative allocation requests made by Hon'ble MPs |
| **Total Sanctioned Capital** | **₹5,057.36 Cr** | Officially approved by District Implementing Agencies (IDAs) |
| **District Sanction Rate** | **14.45%** | **₹29,930.11 Cr** in 50,888 projects awaiting district approval |
| **Completed Projects** | **1,506 projects** | ₹827.07 Cr in completed civic infrastructure |
| **Active Projects (Ongoing)** | **629 projects** | ₹537.19 Cr in active physical execution |
| **High Value Projects (≥ ₹25L)**| **1,400 projects** | Includes 131 mega projects exceeding ₹1.00 Crore |

---

## 🚀 Key Features

- 🏛️ **True Full-Dataset Telemetry**: Live SQLite database aggregations across 60,362 records via `/api/works/summary`.
- 🔍 **Server-Side Search & Multi-Filter Query Engine**: Instant fuzzy search across descriptions, MP names, constituencies, states, and agencies, with server-side pagination (15, 25, 50, 100 per page).
- 📈 **State-Wise Capital Radar**: Comparative analysis of Recommended vs Sanctioned amounts per State / Union Territory with calculated sanction ratios.
- 🎯 **MP Allocation Leaderboard**: Track highest allocation volumes and project distribution per Member of Parliament.
- 🚦 **Project Status Pipeline**: Interactive Donut chart classifying Unsanctioned, Sanctioned, Completed, Ongoing, and Unspecified works.
- 📥 **One-Click CSV Export**: Download current paginated or filtered views for offline auditing and reporting.
- ⚖️ **Multi-Signal Anomaly Detection**: Cost outlier detection, timeline inconsistency tracking, duplicate identification, and data completeness auditing.

---

## 🗂️ Project Architecture

```
MPLAD_Integrity_Engine/
├── backend/                        # FastAPI Python Backend
│   ├── app/
│   │   ├── adapters/               # Official MPLADS CSV & eSakshi data adapters
│   │   ├── detectors/              # Statistical, peer, timeline & cost anomaly detectors
│   │   ├── models/                 # SQLAlchemy models (Work, Progress, Payment, Audit)
│   │   ├── routers/
│   │   │   ├── works.py            # Summary aggregations, search, filtering, and pagination
│   │   │   └── reconciliation.py   # Multi-source cross-reconciliation endpoints
│   │   └── services/               # Feature store, ML framework, lifecycle state machine
│   ├── data/
│   │   └── mplad_integrity.db      # High-performance indexed SQLite database (60,362 rows)
│   ├── main.py                     # FastAPI application entrypoint & CORS config
│   ├── ingest_official.py          # Adapter ingestion script for official MOSPI exports
│   └── requirements.txt            # Python dependencies
│
├── frontend/                       # React 19 + TypeScript + Vite 8
│   ├── src/
│   │   ├── components/             # MetricCard, StatusBadge, AuditBadge, Navbar, LoadingSkeleton
│   │   ├── pages/
│   │   │   ├── HomePage.tsx        # Executive telemetry dashboard & interactive analytics
│   │   │   ├── WorksPage.tsx       # 60k projects search table with server pagination
│   │   │   ├── WorkDetailPage.tsx  # Deep dossier on individual work projects
│   │   │   └── CoveragePage.tsx    # Detector coverage and auditing rules
│   │   ├── services/
│   │   │   └── api.ts              # Axios client connecting to backend API
│   │   ├── types/                  # Strict TypeScript interfaces
│   │   └── utils/
│   │       └── formatters.ts       # Accurate Indian currency (₹ Lakhs & Crores) formatting
│   ├── vite.config.ts              # Vite reverse proxy config for dev and preview
│   └── package.json
│
├── start_backend.bat               # One-click startup for FastAPI backend
└── start_frontend.bat              # One-click startup for Vite frontend
```

---

## ⚡ Quick Start

### 1. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`
- Live Summary: `http://localhost:8000/api/works/summary`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run build
npm run preview
```
- Web Application: `http://localhost:4173` (or `http://localhost:5173` in development via `npm run dev`)

---

## 📡 API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/works/summary` | `GET` | Aggregated dataset analytics across all 60,362 works |
| `/api/works/filters` | `GET` | Distinct states, statuses, and financial years for UI filters |
| `/api/works/` | `GET` | Server-paginated works list supporting `search`, `state`, `status`, `sort_by`, `sort_order`, `page`, `limit` |
| `/api/works/{work_id}` | `GET` | Detailed project dossier by unique identifier |
| `/health` | `GET` | Server health and database connection status |
| `/coverage` | `GET` | Audit detector rule coverage evaluation |

---

## 📜 Provenance & Truthfulness Guarantee
This engine enforces strict civic data provenance:
- Observed values directly originate from official MOSPI and eSAKSHI exports.
- Fields not publicly disclosed in official sources remain untouched as `NULL` and are flagged with audit badges to prevent synthetic hallucination.

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
