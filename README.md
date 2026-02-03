# Chemical Equipment Parameter Visualizer (Hybrid Web + Desktop)

A hybrid application that runs as both a **Web Application** (React + Chart.js) and a **Desktop Application** (PyQt5 + Matplotlib). Both frontends connect to a common **Django REST** backend for CSV upload, analytics, and PDF reports.

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend (Web) | React.js + Chart.js | Table + charts |
| Frontend (Desktop) | PyQt5 + Matplotlib | Same visualization on desktop |
| Backend | Django + Django REST Framework | Common API |
| Data | Pandas | CSV parsing & analytics |
| Database | SQLite | Last 5 uploaded datasets |
| Auth | HTTP Basic Authentication | Login for API |

## Features

- **CSV Upload** – Upload CSV files from both Web and Desktop to the backend
- **Data Summary API** – Total count, averages (Flowrate, Pressure, Temperature), equipment type distribution
- **Visualization** – Charts via Chart.js (Web) and Matplotlib (Desktop)
- **History** – Last 5 uploaded datasets with summary stored in SQLite
- **PDF Report** – Generate and download summary PDF
- **Basic Authentication** – Sign in required for all API access

## Project Structure

```
Fossee/
├── backend/                 # Django API
│   ├── equipment_visualizer/
│   ├── api/
│   └── requirements.txt
├── frontend/                # React web app
│   ├── public/
│   ├── src/
│   └── package.json
├── desktop/                 # PyQt5 desktop app
│   ├── main.py
│   ├── api_client.py
│   └── requirements.txt
├── sample_equipment_data.csv
└── README.md
```

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for React)
- **pip** and **npm**

## Setup Instructions

### 1. Backend (Django)

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
# Enter username and password (e.g. admin / admin123)
python manage.py runserver
```

Backend runs at **http://localhost:8000**.

### 2. Web Frontend (React)

```bash
cd frontend
npm install
npm start
```

Web app runs at **http://localhost:3000**. Use the same username/password from `createsuperuser` to sign in.

### 3. Desktop Frontend (PyQt5)

```bash
cd desktop
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
python main.py
```

Sign in with the same Django user. Use **Upload CSV** to pick a file (e.g. the provided `sample_equipment_data.csv` in the repo root).

## CSV Format

CSV must include these columns (names exact):

- **Equipment Name**
- **Type**
- **Flowrate**
- **Pressure**
- **Temperature**

A sample file is provided: `sample_equipment_data.csv` at the project root. Use it for demo and testing.

## API Endpoints (all require Basic Auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload/` | Upload CSV; returns summary + records |
| GET | `/api/history/` | Last 5 datasets (id, name, row_count, summary_json) |
| GET | `/api/summary/<id>/` | Full summary for a dataset |
| GET | `/api/report/<id>/pdf/` | Download PDF report |

## Demo & Testing

1. Start backend: `cd backend && python manage.py runserver`
2. Create user: `python manage.py createsuperuser` (if not done)
3. **Web:** `cd frontend && npm start` → open http://localhost:3000 → sign in → Upload CSV (e.g. `sample_equipment_data.csv`)
4. **Desktop:** `cd desktop && python main.py` → sign in → Upload CSV → view charts and table → Generate PDF Report

## Submission

- Source code on GitHub (backend + both frontends)
- README with setup instructions (this file)
- Short demo video (2–3 minutes) – record upload, charts, history, and PDF from both Web and Desktop
- Optional: deployment link for web version (e.g. Vercel/Netlify with backend on Railway/Render)

## License

MIT (or as required by your organization.)
