# Chemical Equipment Parameter Visualizer (Hybrid Web + Desktop)

A hybrid application that runs as both a **Web Application** (React + Chart.js) and a **Desktop Application** (PyQt5 + Matplotlib). Both frontends connect to a common **Django REST** backend for CSV upload, analytics, and PDF reports.

## Login credentials (default)

| Field     | Value      |
|----------|------------|
| **Username** | `admin`  |
| **Password** | `admin123` |

Use these to sign in on the Web app (http://localhost:3000) and the Desktop app. Create this user by running `python manage.py createsuperuser` and entering the same values (or set your own).

## Tech Stack

| Layer   | Technology | Purpose |
|---------|------------|---------|
| Frontend (Web) | React.js + Chart.js | Table + charts |
| Frontend (Desktop) | PyQt5 + Matplotlib | Same visualization on desktop |
| Backend | Django + Django REST Framework | Common API |
| Data | Pandas | CSV parsing & analytics |
| Database | SQLite | Last 5 uploaded datasets |
| Auth | HTTP Basic Authentication | Login for API |

## Features

- **CSV Upload** – Upload CSV from Web and Desktop to the backend
- **Data Summary API** – Total count, averages (Flowrate, Pressure, Temperature), equipment type distribution
- **Visualization** – Charts via Chart.js (Web) and Matplotlib (Desktop)
- **History** – Last 5 uploaded datasets with summary in SQLite
- **PDF Report** – Generate and download summary PDF
- **Basic Authentication** – Sign in required for all API access

## Project Structure

```
Fossee/
├── backend/           # Django API
├── frontend/          # React web app
├── desktop/           # PyQt5 desktop app
├── sample_equipment_data.csv
└── README.md
```

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for React)
- **pip** and **npm**

## Setup

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
# Use username: admin, password: admin123 (or your choice)
python manage.py runserver
```

Backend runs at **http://localhost:8000**.

### 2. Web Frontend (React)

```bash
cd frontend
npm install
npm start
```

Web app runs at **http://localhost:3000**. Sign in with **admin** / **admin123** (or the user you created).

### 3. Desktop Frontend (PyQt5)

```bash
cd desktop
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
python main.py
```

Sign in with the same username and password. Use **Upload CSV** to select `sample_equipment_data.csv` from the project root.

## CSV Format

Required columns: **Equipment Name**, **Type**, **Flowrate**, **Pressure**, **Temperature**.

Sample file: `sample_equipment_data.csv` in the project root.

## API Endpoints (Basic Auth required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload/` | Upload CSV; returns summary + records |
| GET | `/api/history/` | Last 5 datasets |
| GET | `/api/summary/<id>/` | Summary for a dataset |
| GET | `/api/report/<id>/pdf/` | Download PDF report |
