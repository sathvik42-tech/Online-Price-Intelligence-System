@echo off
REM Health Check & Diagnostic Script for Performance Optimization (Windows)
REM Usage: health_check.bat

setlocal enabledelayedexpansion

echo ================================
echo Health Check ^& Diagnostics
echo ================================
echo.

REM ============================================================================
REM 1. Check Redis
REM ============================================================================
echo 1. Checking Redis...
redis-cli.exe ping >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Redis is running
    for /f "tokens=*" %%A in ('redis-cli.exe INFO stats 2^>nul') do (
        if "%%A"=="" goto end_redis
        echo %%A | findstr /C:"connected_clients" >nul && echo   Connected clients: %%A
    )
) else (
    echo [FAIL] Redis not accessible at localhost:6379
    echo   ^> Start Redis: docker run -d -p 6379:6379 redis:latest
)
:end_redis
echo.

REM ============================================================================
REM 2. Check PostgreSQL
REM ============================================================================
echo 2. Checking PostgreSQL...
psql -h localhost -U postgres -d price_intelligence -c "SELECT 1" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] PostgreSQL is running
    for /f %%A in ('psql -h localhost -U postgres -d price_intelligence -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'"') do (
        echo   Tables: %%A
    )
    for /f %%A in ('psql -h localhost -U postgres -d price_intelligence -t -c "SELECT count(*) FROM pg_indexes WHERE schemaname='public'"') do (
        echo   Indexes: %%A
    )
) else (
    echo [FAIL] PostgreSQL not accessible
    echo   ^> Start PostgreSQL: docker run -d -p 5432:5432 -e POSTGRES_DB=price_intelligence postgres:15
)
echo.

REM ============================================================================
REM 3. Check API Endpoints
REM ============================================================================
echo 3. Checking API Endpoints...

REM Python Backend
powershell -Command "try { $null = Invoke-WebRequest -Uri 'http://localhost:8000/' -TimeoutSec 2 -ErrorAction Stop; Write-Host '[OK] Python API (port 8000) is responding' } catch { Write-Host '[FAIL] Python API (port 8000) not responding' }"

REM Express Backend
powershell -Command "try { $null = Invoke-WebRequest -Uri 'http://localhost:5001/' -TimeoutSec 2 -ErrorAction Stop; Write-Host '[OK] Express API (port 5001) is responding' } catch { Write-Host '[WARN] Express API (port 5001) not responding' }"

REM Frontend
powershell -Command "try { $null = Invoke-WebRequest -Uri 'http://localhost:5173/' -TimeoutSec 2 -ErrorAction Stop; Write-Host '[OK] Frontend (port 5173) is responding' } catch { Write-Host '[WARN] Frontend (port 5173) not responding (may not be started)' }"

echo.

REM ============================================================================
REM 4. Check Processes
REM ============================================================================
echo 4. Checking Services...

tasklist | findstr /I "python.exe" >nul
if %errorlevel% equ 0 (
    echo [OK] Python process running
) else (
    echo [WARN] Python process not running
)

tasklist | findstr /I "node.exe npm.cmd" >nul
if %errorlevel% equ 0 (
    echo [OK] Node.js process running
) else (
    echo [WARN] Node.js process not running
)

echo.

REM ============================================================================
REM 5. Check Flower
REM ============================================================================
echo 5. Checking Flower Monitoring UI...
powershell -Command "try { $null = Invoke-WebRequest -Uri 'http://localhost:5555/' -TimeoutSec 2 -ErrorAction Stop; Write-Host '[OK] Flower UI (port 5555) is accessible' } catch { Write-Host '[WARN] Flower UI (port 5555) not found' }"

echo.

REM ============================================================================
REM 6. Check Configuration
REM ============================================================================
echo 6. Configuration Check...

if exist "backend\.env" (
    echo [OK] Backend .env file exists
    findstr /C:"REDIS_HOST" backend\.env >nul
    if %errorlevel% equ 0 (
        echo [OK] REDIS_HOST configured
    ) else (
        echo [FAIL] REDIS_HOST not configured
    )
) else (
    echo [WARN] Backend .env file not found
)

if exist "frontend\.env" (
    echo [OK] Frontend .env file exists
) else (
    echo [WARN] Frontend .env file not found (optional)
)

echo.

REM ============================================================================
REM 7. Check File Structure
REM ============================================================================
echo 7. Checking File Structure...

if exist "backend\app\redis_cache.py" (
    echo [OK] redis_cache.py exists
) else (
    echo [FAIL] redis_cache.py missing
)

if exist "backend\app\celery_app.py" (
    echo [OK] celery_app.py exists
) else (
    echo [FAIL] celery_app.py missing
)

if exist "backend\app\tasks.py" (
    echo [OK] tasks.py exists
) else (
    echo [FAIL] tasks.py missing
)

if exist "backend\app\main_optimized.py" (
    echo [OK] main_optimized.py exists
) else (
    echo [FAIL] main_optimized.py missing
)

if exist "frontend\src\utils\imageOptimization.js" (
    echo [OK] imageOptimization.js exists
) else (
    echo [FAIL] imageOptimization.js missing
)

if exist "frontend\src\utils\codeSplitting.jsx" (
    echo [OK] codeSplitting.jsx exists
) else (
    echo [FAIL] codeSplitting.jsx missing
)

if exist "frontend\src\utils\performanceMonitoring.js" (
    echo [OK] performanceMonitoring.js exists
) else (
    echo [FAIL] performanceMonitoring.js missing
)

echo.

REM ============================================================================
REM 8. Summary
REM ============================================================================
echo ================================
echo Health Check Complete
echo ================================
echo.
echo Key URLs:
echo   Frontend:       http://localhost:5173
echo   Python API:     http://localhost:8000
echo   Express API:    http://localhost:5001
echo   Flower (Tasks): http://localhost:5555
echo   API Metrics:    http://localhost:8000/api/metrics
echo.
echo Documentation:
echo   ^> PERFORMANCE_QUICK_START.md
echo   ^> PERFORMANCE_OPTIMIZATION_COMPLETE.md
echo.

endlocal
