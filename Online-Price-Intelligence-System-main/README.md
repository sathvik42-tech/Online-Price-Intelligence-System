# 🚀 Online Price Intelligence System

A high-performance, professional price comparison and intelligence platform. It aggregates real-time data from major e-commerce stores using advanced web scraping and **AI-assisted image recognition for product matching** to provide users with the best deals and product insights.

---

## 🎯 Problem Statement & Solution

**The Problem**: In today's fragmented e-commerce market, shoppers struggle to find the best prices manually. Dynamic pricing and varying product descriptions across stores (Amazon, Flipkart, eBay) make manual comparison time-consuming and often inaccurate.

**The Solution**: This platform automates the entire process. By combining multi-threaded web scraping with AI-driven image analysis, we provide a unified dashboard where users can instantly compare prices, track history, and get smart recommendations based on visual similarity.

---

## 🔄 Data Flow

1.  **Frontend**: User submits a search query or uploads a product image.
2.  **FastAPI**: The central intelligence engine receives the request and dispatches concurrent scraping tasks.
3.  **Scrapers**: Isolated modules fetch raw HTML/JSON data from stores like Amazon, eBay, and Flipkart.
4.  **AI Layer**: The system processes product images to verify matches and extract features, ensuring "Shoes" on Store A are the same as "Shoes" on Store B.
5.  **Database**: Results are validated and persisted in PostgreSQL for historical tracking and user wishlists.
6.  **Response**: The system returns a structured, ranked JSON response to the React frontend for rendering.

---

## 🏗️ System Architecture

The system is built with a modular, distributed architecture to ensure scalability and reliability:

- **Frontend**: A modern, responsive React application.
- **Auth & DB Service**: Express.js server handling user authentication and core metadata.
- **Intelligence Engine**: Python FastAPI service managing scrapers, AI model inference, and background processing.
- **Data Persistence**: PostgreSQL for relational data and Redis for caching and task queuing.
- **Asynchronous Workers**: Celery workers for handling intensive scraping and image analysis tasks.

---

## 🛠️ Technology Stack

| Category | Technologies |
| :--- | :--- |
| **Frontend** | React, Vite, Material UI (MUI), Framer Motion, Chart.js, Axios |
| **Backend (Core)** | Express.js, JWT, Sequelize/Prisma (Optional) |
| **Backend (Intelligence)** | Python 3.10+, FastAPI, Uvicorn, Celery, Redis |
| **AI & Computer Vision** | TensorFlow, NumPy, Pillow (PIL), OCR Engines |
| **Scraping** | BeautifulSoup4, Requests, Scrapy (Internal Modules) |
| **Database** | PostgreSQL |
| **Infrastructure** | Docker, Docker Compose, Flower (Celery Monitoring) |

---

## ✅ Pre-run Checklist

Before starting, ensure the following are installed and running:
- [ ] **PostgreSQL**: Running on port `5432`.
- [ ] **Redis**: Running on port `6379` (critical for Celery).
- [ ] **Ports Available**: `5173` (UI), `8000` (Python API), `5001` (Auth API).
- [ ] **Python 3.10+**: Installed and added to PATH.

---

## 🔑 Environment Variables

Each service requires specific environment variables. Create a `.env` file in the respective directories:

### Python Backend (`/backend/.env`)
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/price_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your_fastapi_secret
```

### Express Backend (`/backend-express/.env`)
```bash
PORT=5001
DATABASE_URL=postgresql://postgres:password@localhost:5432/price_db
JWT_SECRET=your_jwt_secret_key
```

### Frontend (`/frontend/.env`)
```bash
VITE_API_URL=http://localhost:8000
VITE_AUTH_API_URL=http://localhost:5001
```

---

## 🚀 Quick Start for Teammates

### 🐳 Option 1: Docker (Recommended)
This is the fastest way to get the entire environment running with a single command.

1.  **Clone & Enter**:
    ```bash
    git clone <repository-url>
    cd Online-Price-Intelligence-System
    ```
2.  **Launch**:
    ```bash
    docker-compose up --build
    ```
3.  **Access**:
    - **Frontend**: [http://localhost:5173](http://localhost:5173)
    - **API Docs (FastAPI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
    - **Task Monitor (Flower)**: [http://localhost:5555](http://localhost:5555)

---

### 💻 Option 2: Manual Setup (Development Mode)

If you need to run services individually for debugging:

#### 1. Databases & Setup
- Ensure **PostgreSQL** and **Redis** are active.
- **Database**: Create a database named `price_db`.
- **Initialization**: Run `python init_db.py` to create tables automatically.

#### 2. Express Auth Backend
```bash
cd backend-express
npm install
npm run dev # Runs on port 5001
```

#### 3. Python Intelligence Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m uvicorn app.main_optimized:app --reload --port 8000
```

#### 4. React Frontend
```bash
cd frontend
npm install
npm run dev # Runs on port 5173
```

---

## 📡 Sample API Endpoints

- `GET /search?q=laptop` - Search products across multiple platforms.
- `GET /product/{id}` - Get comprehensive details and history for a specific item.
- `POST /wishlist` - Securely save a product to user account (requires JWT).

---

## 📁 Project Structure

```text
├── backend/            # FastAPI Intelligence Engine (AI & Scrapers)
├── backend-express/    # Express.js Auth & Metadata Server
├── frontend/           # React + Vite UI
├── docs/               # Architecture and Strategy Docs
├── scripts/            # Database initialization and diagnostics
└── docker-compose.yml  # Full-stack orchestration
```

## 🛠️ Troubleshooting

- **Port Conflict**: If an error says "Port already in use", check if another instance is running or change the ports in `.env`.
- **DB Connection**: Ensure PostgreSQL credentials in `.env` match your local setup.
- **Redis Error**: If Celery fails to start, verify the Redis server is listening on `6379`.
- **Scraping Blocked**: Some stores may block IP addresses. Use a VPN or wait if scraping fails repeatedly.

---

## 📸 Screenshots

*(Add your screenshots here for the PPT presentation)*
![Dashboard Placeholder](https://via.placeholder.com/800x400?text=Dashboard+Overview)

---
## 🤝 Contribution Guidelines
- **Branches**: Always create a feature branch (`feature/your-feature`).
- **Commits**: Use descriptive commit messages.
- **Code Style**: Python (PEP 8), JS (ESLint + Prettier).

---
*Developed as part of the Infosys Internship Program.*
