#!/bin/bash

# Health Check & Diagnostic Script for Performance Optimization
# Usage: ./health_check.sh

set -e

echo "================================"
echo "Health Check & Diagnostics"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_passed() {
    echo -e "${GREEN}✓${NC} $1"
}

check_failed() {
    echo -e "${RED}✗${NC} $1"
}

check_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# ============================================================================
# 1. Check Redis
# ============================================================================
echo "1. Checking Redis..."
if redis-cli ping &>/dev/null; then
    check_passed "Redis is running"
    redis_info=$(redis-cli INFO stats)
    echo "   Connected clients: $(echo "$redis_info" | grep connected_clients | cut -d: -f2)"
    echo "   Total commands: $(echo "$redis_info" | grep total_commands_processed | cut -d: -f2)"
else
    check_failed "Redis not accessible at localhost:6379"
    echo "   → Start Redis: docker run -d -p 6379:6379 redis:latest"
fi
echo ""

# ============================================================================
# 2. Check PostgreSQL
# ============================================================================
echo "2. Checking PostgreSQL..."
if PGPASSWORD=postgres psql -h localhost -U postgres -d price_intelligence -c "SELECT 1" &>/dev/null; then
    check_passed "PostgreSQL is running"
    table_count=$(PGPASSWORD=postgres psql -h localhost -U postgres -d price_intelligence -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'")
    echo "   Tables: $table_count"
    
    # Check indexes
    index_count=$(PGPASSWORD=postgres psql -h localhost -U postgres -d price_intelligence -t -c "SELECT count(*) FROM pg_indexes WHERE schemaname='public'")
    echo "   Indexes: $index_count"
else
    check_failed "PostgreSQL not accessible"
    echo "   → Start PostgreSQL: docker run -d -p 5432:5432 -e POSTGRES_DB=price_intelligence postgres:15"
fi
echo ""

# ============================================================================
# 3. Check API Endpoints
# ============================================================================
echo "3. Checking API Endpoints..."

# Python Backend
if curl -s http://localhost:8000/ &>/dev/null; then
    check_passed "Python API (port 8000) is responding"
    response_time=$(curl -s -o /dev/null -w '%{time_total}' http://localhost:8000/)
    echo "   Response time: ${response_time}s"
    
    # Check health endpoint
    if curl -s http://localhost:8000/api/metrics &>/dev/null; then
        check_passed "Metrics endpoint is working"
    fi
else
    check_failed "Python API (port 8000) not responding"
fi

# Express Backend
if curl -s http://localhost:5001/ &>/dev/null; then
    check_passed "Express API (port 5001) is responding"
else
    check_failed "Express API (port 5001) not responding"
fi

# Frontend
if curl -s http://localhost:5173/ &>/dev/null; then
    check_passed "Frontend (port 5173) is responding"
else
    check_warning "Frontend (port 5173) not responding (may not be started)"
fi
echo ""

# ============================================================================
# 4. Check Celery Workers
# ============================================================================
echo "4. Checking Celery..."
if ps aux | grep -q "[c]elery.*worker"; then
    check_passed "Celery worker is running"
    active_tasks=$(curl -s http://localhost:5555/api/tasks | grep -o '"task_id"' | wc -l 2>/dev/null || echo "?")
    echo "   Active tasks: $(($active_tasks))"
else
    check_warning "Celery worker not detected (run: celery -A app.celery_app worker)"
fi

if ps aux | grep -q "[c]elery.*beat"; then
    check_passed "Celery beat scheduler is running"
else
    check_warning "Celery beat not detected (optional, run: celery -A app.celery_app beat)"
fi
echo ""

# ============================================================================
# 5. Check Monitoring
# ============================================================================
echo "5. Checking Monitoring/UI..."

# Flower
if curl -s http://localhost:5555/ &>/dev/null; then
    check_passed "Flower UI (port 5555) is accessible"
    echo "   → http://localhost:5555"
else
    check_warning "Flower UI (port 5555) not found (run: flower -A app.celery_app --port 5555)"
fi
echo ""

# ============================================================================
# 6. Performance Tests
# ============================================================================
echo "6. Performance Tests..."

# Test caching
echo "   Testing Redis caching..."
test_key="perf_test_$(date +%s)"
redis-cli SET "$test_key" "test_value" EX 60 &>/dev/null
cached=$(redis-cli GET "$test_key")
if [ "$cached" = "test_value" ]; then
    check_passed "Redis caching working"
else
    check_failed "Redis caching test failed"
fi
redis-cli DEL "$test_key" &>/dev/null

# Test API response time
echo "   Testing API performance..."
response_time=$(curl -s -o /dev/null -w '%{time_total}' "http://localhost:8000/api/metrics")
response_ms=$(echo "$response_time * 1000" | bc)
if (( $(echo "$response_time < 1" | bc -l) )); then
    check_passed "API response time: ${response_ms}ms (< 1000ms)"
else
    check_warning "API response time: ${response_ms}ms (> 1000ms)"
fi

# Test database
echo "   Testing database queries..."
start_time=$(date +%s%N)
PGPASSWORD=postgres psql -h localhost -U postgres -d price_intelligence -c "SELECT count(*) FROM users" &>/dev/null
end_time=$(date +%s%N)
query_time=$((($end_time - $start_time) / 1000000))  # Convert to ms
if [ "$query_time" -lt 100 ]; then
    check_passed "Database query time: ${query_time}ms (< 100ms)"
elif [ "$query_time" -lt 500 ]; then
    check_warning "Database query time: ${query_time}ms (moderate)"
else
    check_failed "Database query time: ${query_time}ms (slow)"
fi
echo ""

# ============================================================================
# 7. Configuration Check
# ============================================================================
echo "7. Configuration Check..."

if [ -f "backend/.env" ]; then
    check_passed "Backend .env file exists"
    
    # Check key variables
    if grep -q "REDIS_HOST" backend/.env; then
        check_passed "REDIS_HOST configured"
    else
        check_failed "REDIS_HOST not configured"
    fi
    
    if grep -q "CELERY_BROKER_URL" backend/.env; then
        check_passed "CELERY_BROKER_URL configured"
    else
        check_failed "CELERY_BROKER_URL not configured"
    fi
else
    check_warning "Backend .env file not found (use .env.example as template)"
fi

if [ -f "frontend/.env" ]; then
    check_passed "Frontend .env file exists"
else
    check_warning "Frontend .env file not found (optional)"
fi
echo ""

# ============================================================================
# 8. Disk Usage
# ============================================================================
echo "8. System Resources..."

# Disk space
disk_usage=$(df -h . | awk 'NR==2 {print $5}')
echo "   Disk usage: $disk_usage"

# Memory usage
if [ -x "$(command -v free)" ]; then
    mem_usage=$(free -h | awk 'NR==2 {print $3 "/" $2}')
    echo "   Memory usage: $mem_usage"
fi

# CPU cores
cpu_cores=$(nproc)
echo "   CPU cores: $cpu_cores"
echo ""

# ============================================================================
# 9. Summary
# ============================================================================
echo "================================"
echo "Health Check Complete"
echo "================================"
echo ""
echo "Key URLs:"
echo "  Frontend:      http://localhost:5173"
echo "  Python API:    http://localhost:8000"
echo "  Express API:   http://localhost:5001"
echo "  Flower (Tasks): http://localhost:5555"
echo "  API Metrics:   http://localhost:8000/api/metrics"
echo ""
echo "Documentation:"
echo "  → PERFORMANCE_QUICK_START.md"
echo "  → PERFORMANCE_OPTIMIZATION_COMPLETE.md"
echo ""
