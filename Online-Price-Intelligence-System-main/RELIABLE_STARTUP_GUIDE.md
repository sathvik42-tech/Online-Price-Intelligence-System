# Online Price Intelligence System: Reliable Execution Guide

This guide provides a step-of-step process to run the entire project correctly. Follow these steps if you encounter any errors or need to restart the system.

## Prerequisites
- **Node.js**: Installed and in your PATH.
- **Python 3.10+**: Installed and in your PATH.
- **PostgreSQL**: Running locally on port 5432.
- **Redis (optional but recommended)**: Running locally on port 6379 for faster caching.

---

## Step 1: Synchronize Environment Variables
Ensure your root `.env` and `backend-express/.env` match.
**Important**: The `DB_NAME`, `DB_USER`, and `DB_PASSWORD` MUST be identical.

- **Recommended `price_intelligence_db` credentials:**
  - `DB_USER=postgres`
  - `DB_PASSWORD=12345678` (or your local postgres password)

---

## Step 2: Initialize the Database
Before running the backends, ensure the database schema is ready.
Open a terminal in the project root and run:
```bash
python init_db.py
```

---

## Step 3: Start the Backend Services
We recommend running each service in a separate terminal to monitor logs.

### 1. Express Backend (Auth & User Data)
This service handles login, registration, and user profiles.
```bash
cd backend-express
npm install
node server.js
```
*Runs on: http://localhost:5001*

### 2. Python Backend (AI & Scraping)
This service handles image analysis and price comparisons.
```bash
cd backend
pip install -r requirements.txt
cd ..
# Set PYTHONPATH to the root directory
$env:PYTHONPATH="."
python -m uvicorn backend.app.main:app --port 8000 --reload
```
*Runs on: http://localhost:8000*

---

## Step 4: Start the Frontend
With both backends running, start the user interface.
```bash
cd frontend
npm install
npm run dev
```
*Runs on: http://localhost:5173*

---

## Troubleshooting
- **HTTP 500 on Login**: Check if PostgreSQL is running and the `DB_PASSWORD` in `backend-express/.env` matches your local password.
- **Image Analysis Timeout**: Ensure the Python backend is running and you have an active internet connection for scrapers.
- **Vite Proxy Errors**: Ensure the backends are running on ports 5001 and 8000 specifically.

---

## Automatic Startup Script
You can also use the optimized startup script I created:
`run_project.bat` (located in the root directory).
