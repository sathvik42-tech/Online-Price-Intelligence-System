@echo off
REM Setup & Deployment Script for Performance Optimization
REM Usage: setup.bat [option]
REM Options: docker | local | verify | clean

setlocal enabledelayedexpansion

color 0A
title Performance Optimization Setup

set OPTION=%~1
if "!OPTION!"=="" set OPTION=menu

:menu
if "!OPTION!"=="menu" (
    cls
    echo.
    echo ╔═══════════════════════════════════════════════════════════╗
    echo ║  Performance Optimization Setup Tool                      ║
    echo ╚═══════════════════════════════════════════════════════════╝
    echo.
    echo Choose setup mode:
    echo.
    echo 1. Docker Setup (Recommended)
    echo    Starts everything using Docker Compose
    echo.
    echo 2. Local Setup
    echo    Installs dependencies and starts services locally
    echo.
    echo 3. Verify Installation
    echo    Runs health checks on existing setup
    echo.
    echo 4. Clean Up
    echo    Stops and removes containers, clears temporary files
    echo.
    echo.
    set /p CHOICE="Enter choice (1-4): "
    
    if "!CHOICE!"=="1" set OPTION=docker
    if "!CHOICE!"=="2" set OPTION=local
    if "!CHOICE!"=="3" set OPTION=verify
    if "!CHOICE!"=="4" set OPTION=clean
    
    if "!CHOICE!" gtr "4" goto menu
)

REM ============================================================================
REM DOCKER SETUP
REM ============================================================================
if "!OPTION!"=="docker" (
    cls
    echo.
    echo ╔═══════════════════════════════════════════════════════════╗
    echo ║  Docker Setup (Recommended)                               ║
    echo ╚═══════════════════════════════════════════════════════════╝
    echo.
    
    REM Check Docker
    docker version >nul 2>&1
    if !errorlevel! neq 0 (
        echo [ERROR] Docker is not installed or not in PATH
        echo Please install Docker from: https://www.docker.com/products/docker-desktop
        echo.
        pause
        goto end
    )
    
    echo [OK] Docker is installed
    echo.
    
    REM Check Docker Compose
    docker-compose version >nul 2>&1
    if !errorlevel! neq 0 (
        echo [ERROR] Docker Compose is not installed
        echo Please install Docker Compose from: https://docs.docker.com/compose/install/
        echo.
        pause
        goto end
    )
    
    echo [OK] Docker Compose is installed
    echo.
    
    REM Create environment file if not exists
    if not exist ".env" (
        echo [INFO] Creating environment file...
        (
            echo POSTGRES_DB=price_intelligence
            echo POSTGRES_USER=postgres
            echo POSTGRES_PASSWORD=postgres
            echo REDIS_HOST=redis
            echo REDIS_PORT=6379
            echo CELERY_BROKER_URL=redis://redis:6379/1
            echo CELERY_RESULT_BACKEND=redis://redis:6379/2
        ) > .env
        echo [OK] .env file created
    ) else (
        echo [OK] .env file already exists
    )
    
    echo.
    echo Step 1: Pulling latest Docker images...
    docker-compose pull
    if !errorlevel! neq 0 (
        echo [WARNING] Some images could not be pulled, attempting to continue
    ) else (
        echo [OK] Images pulled successfully
    )
    
    echo.
    echo Step 2: Starting all services...
    echo This may take 2-3 minutes on first run
    docker-compose up -d
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to start Docker services
        pause
        goto end
    )
    
    echo [OK] All services are starting
    echo.
    echo Step 3: Waiting for health checks (this may take 1-2 minutes)...
    
    timeout /t 5 /nobreak
    
    set /a attempts=0
    :wait_loop
    set /a attempts+=1
    if !attempts! gtr 24 (
        echo [WARNING] Services taking longer than expected to start
        goto docker_done
    )
    
    docker-compose ps | findstr "healthy" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [OK] Services are healthy
        goto docker_done
    )
    
    echo   Waiting... (!attempts! of 24)
    timeout /t 5 /nobreak > nul
    goto wait_loop
    
    :docker_done
    echo.
    echo [COMPLETE] Docker setup finished!
    echo.
    echo Next steps:
    echo.
    echo 1. Open your browser and visit:
    echo    Frontend:  http://localhost:5173
    echo    API:       http://localhost:8000
    echo    Monitoring: http://localhost:5555 (Flower)
    echo.
    echo 2. Check service status:
    echo    docker-compose ps
    echo.
    echo 3. View logs:
    echo    docker-compose logs -f backend
    echo.
    echo 4. Stop all services:
    echo    docker-compose down
    echo.
    echo 5. Quick health check:
    echo    health_check.bat
    echo.
    pause
    goto end
)

REM ============================================================================
REM LOCAL SETUP
REM ============================================================================
if "!OPTION!"=="local" (
    cls
    echo.
    echo ╔═══════════════════════════════════════════════════════════╗
    echo ║  Local Setup (Manual)                                     ║
    echo ╚═══════════════════════════════════════════════════════════╝
    echo.
    
    REM Check Python
    python --version >nul 2>&1
    if !errorlevel! neq 0 (
        echo [ERROR] Python is not installed
        echo Please install Python 3.9+ from: https://www.python.org/
        pause
        goto end
    )
    
    for /f "tokens=2" %%A in ('python --version 2^>^&1') do set PYTHON_VERSION=%%A
    echo [OK] Python !PYTHON_VERSION! is installed
    echo.
    
    REM Check Redis
    redis-cli.exe --version >nul 2>&1
    if !errorlevel! neq 0 (
        echo [WARNING] Redis CLI not found, but Redis container can be used
        echo To start Redis with Docker:
        echo   docker run -d -p 6379:6379 --name redis-cache redis:7-alpine
        echo.
        set /p CONTINUE="Continue with local setup anyway? (Y/N): "
        if /i "!CONTINUE!" neq "Y" goto end
    ) else (
        for /f "tokens=2" %%A in ('redis-cli.exe --version 2^>^&1') do set REDIS_VERSION=%%A
        echo [OK] Redis !REDIS_VERSION! is installed
    )
    echo.
    
    REM Check PostgreSQL
    psql --version >nul 2>&1
    if !errorlevel! neq 0 (
        echo [WARNING] PostgreSQL is not installed
        echo Please install PostgreSQL from: https://www.postgresql.org/download/windows/
        pause
        goto end
    )
    
    for /f "tokens=3" %%A in ('psql --version 2^>^&1') do set PG_VERSION=%%A
    echo [OK] PostgreSQL !PG_VERSION! is installed
    echo.
    
    REM Install Python dependencies
    echo Step 1: Installing Python dependencies...
    pip install -q redis celery[redis] flower pillow psutil fastapi uvicorn sqlalchemy psycopg2-binary >nul 2>&1
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install Python packages
        pause
        goto end
    )
    echo [OK] Python packages installed
    echo.
    
    REM Create environment file
    if not exist "backend\.env" (
        echo Step 2: Creating environment file...
        (
            echo REDIS_HOST=localhost
            echo REDIS_PORT=6379
            echo CELERY_BROKER_URL=redis://localhost:6379/1
            echo CELERY_RESULT_BACKEND=redis://localhost:6379/2
            echo DATABASE_URL=postgresql://postgres:postgres@localhost:5432/price_intelligence
        ) > backend\.env
        echo [OK] backend\.env created
    ) else (
        echo [OK] backend\.env already exists
    )
    echo.
    
    REM Create database
    echo Step 3: Setting up database...
    psql -h localhost -U postgres -c "CREATE DATABASE price_intelligence;" 2>nul
    echo [OK] Database setup complete
    echo.
    
    echo [COMPLETE] Local setup finished!
    echo.
    echo Next steps - Start services manually:
    echo.
    echo Terminal 1 (Backend API):
    echo   cd backend
    echo   python -m uvicorn app.main_optimized:app --reload --host 0.0.0.0 --port 8000
    echo.
    echo Terminal 2 (Celery Worker):
    echo   cd backend
    echo   celery -A app.celery_app worker --loglevel=info -c 4
    echo.
    echo Terminal 3 (Celery Beat Scheduler):
    echo   cd backend
    echo   celery -A app.celery_app beat --loglevel=info
    echo.
    echo Terminal 4 (Flower Monitoring):
    echo   celery -A app.celery_app flower --port=5555
    echo.
    echo Terminal 5 (Frontend):
    echo   cd frontend
    echo   npm install
    echo   npm run dev
    echo.
    pause
    goto end
)

REM ============================================================================
REM VERIFY INSTALLATION
REM ============================================================================
if "!OPTION!"=="verify" (
    cls
    echo.
    echo ╔═══════════════════════════════════════════════════════════╗
    echo ║  Verify Installation                                      ║
    echo ╚═══════════════════════════════════════════════════════════╝
    echo.
    call health_check.bat
    goto end
)

REM ============================================================================
REM CLEAN UP
REM ============================================================================
if "!OPTION!"=="clean" (
    cls
    echo.
    echo ╔═══════════════════════════════════════════════════════════╗
    echo ║  Clean Up                                                 ║
    echo ╚═══════════════════════════════════════════════════════════╝
    echo.
    echo This will:
    echo - Stop all Docker containers
    echo - Remove containers and networks created by docker-compose
    echo - Remove temporary cache files
    echo.
    set /p CONFIRM="Continue? (Y/N): "
    
    if /i "!CONFIRM!" neq "Y" (
        echo Cleanup cancelled
        goto end
    )
    
    echo.
    
    REM Stop Docker Compose services
    docker-compose version >nul 2>&1
    if !errorlevel! equ 0 (
        echo Stopping Docker services...
        docker-compose down --remove-orphans
        echo [OK] Docker services stopped and removed
    )
    
    REM Clean Python cache
    if exist "__pycache__" (
        echo Removing Python cache...
        rmdir /s /q __pycache__ >nul 2>&1
    )
    
    if exist "backend\__pycache__" (
        rmdir /s /q backend\__pycache__ >nul 2>&1
    )
    
    if exist "backend\app\__pycache__" (
        rmdir /s /q backend\app\__pycache__ >nul 2>&1
    )
    
    REM Clean node modules cache
    if exist "frontend\node_modules\.vite" (
        echo Removing Vite cache...
        rmdir /s /q frontend\node_modules\.vite >nul 2>&1
    )
    
    echo [OK] Caches cleaned
    echo.
    echo Cleanup complete!
    echo.
    pause
    goto end
)

REM ============================================================================
REM END
REM ============================================================================
:end
color 07
