# Performance Optimization Troubleshooting Guide

## Common Issues and Solutions

### 1. Redis Connection Issues

#### Problem: "Redis connection refused"

**Error Message:**
```
ConnectionError: Error 111 connecting to localhost:6379. Connection refused.
```

**Solutions:**

1. **Check if Redis is running:**
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

2. **Start Redis using Docker:**
   ```bash
   docker run -d -p 6379:6379 --name redis-cache redis:7-alpine
   ```

3. **Check Redis port in environment:**
   ```bash
   # In backend/.env
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

4. **Verify Redis is accessible:**
   ```bash
   redis-cli -h localhost -p 6379 ping
   ```

5. **If using Docker Compose:**
   ```bash
   docker-compose logs redis
   docker-compose restart redis
   ```

---

### 2. PostgreSQL Connection Issues

#### Problem: "PostgreSQL connection failed"

**Error Message:**
```
psycopg2.OperationalError: could not connect to server
```

**Solutions:**

1. **Verify PostgreSQL is running:**
   ```bash
   psql --version
   psql -h localhost -U postgres -d price_intelligence -c "SELECT 1"
   ```

2. **Check database exists:**
   ```bash
   psql -h localhost -U postgres -c "CREATE DATABASE price_intelligence;"
   psql -h localhost -U postgres -d price_intelligence -c "SELECT 1"
   ```

3. **Verify credentials:**
   ```bash
   # In backend/.env or docker-compose.yml
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=price_intelligence
   ```

4. **Check PostgreSQL service:**
   ```bash
   # Windows
   net start postgresql-x64-15
   
   # Linux/Mac
   sudo service postgresql start
   ```

5. **Reset PostgreSQL password:**
   ```bash
   sudo -u postgres psql
   ALTER USER postgres WITH PASSWORD 'postgres';
   \q
   ```

---

### 3. Celery Worker Issues

#### Problem: "No Celery worker processes found"

**Error Message:**
```
No running Celery workers were found
Tasks are being ignored
```

**Solutions:**

1. **Start Celery worker:**
   ```bash
   cd backend
   celery -A app.celery_app worker --loglevel=info
   ```

2. **Check if Redis broker is running:**
   - Celery requires Redis to be available
   - Run: `redis-cli ping` to verify

3. **Monitor worker status:**
   ```bash
   celery -A app.celery_app inspect active
   celery -A app.celery_app inspect stats
   ```

4. **Using Docker Compose:**
   ```bash
   docker-compose logs celery-worker
   docker-compose up -d celery-worker
   ```

5. **Verify Celery configuration:**
   ```python
   # backend/app/celery_app.py
   CELERY_BROKER_URL = 'redis://localhost:6379/1'
   CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'
   ```

---

### 4. Flower Monitoring Issues

#### Problem: "Flower UI not accessible"

**Error Message:**
```
Failed to connect to http://localhost:5555
```

**Solutions:**

1. **Start Flower:**
   ```bash
   celery -A app.celery_app flower --port=5555
   ```

2. **Check port availability:**
   ```bash
   # Windows
   netstat -ano | findstr :5555
   
   # Linux/Mac
   lsof -i :5555
   ```

3. **Kill process using port 5555:**
   ```bash
   # Windows
   taskkill /PID <PID> /F
   
   # Linux/Mac
   kill -9 <PID>
   ```

4. **Access Flower:**
   ```
   http://localhost:5555
   ```

5. **Using Docker Compose:**
   ```bash
   docker-compose up -d flower
   docker-compose logs flower
   ```

---

### 5. API Response Performance Issues

#### Problem: "API responses are slow"

**Error:**
```
API response time > 1000ms
```

**Debugging Steps:**

1. **Check Redis cache hits:**
   ```bash
   curl http://localhost:8000/api/cache-stats
   ```
   Expected: Cache hit rate > 70%

2. **Monitor API performance:**
   ```bash
   curl http://localhost:8000/api/metrics
   ```
   Look for slow endpoints (> 1s)

3. **Force async processing:**
   ```bash
   curl -X POST http://localhost:8000/api/compare-prices \
     -H "Content-Type: application/json" \
     -d '{"product": "laptop", "async_mode": true}'
   ```

4. **Check database query performance:**
   ```bash
   PGPASSWORD=postgres psql -h localhost -U postgres -d price_intelligence << EOF
   SELECT query, calls, mean_exec_time FROM pg_stat_statements 
   ORDER BY mean_exec_time DESC LIMIT 10;
   EOF
   ```

5. **Verify GZIP compression is enabled:**
   ```bash
   curl -i http://localhost:8000/api/metrics | grep -i content-encoding
   # Should show: Content-Encoding: gzip
   ```

---

### 6. Database Optimization Issues

#### Problem: "Database indexes not created"

**Error:**
```
SELECT * FROM price_history is not using indexes
```

**Solutions:**

1. **Apply optimization migration:**
   ```bash
   PGPASSWORD=postgres psql -h localhost -U postgres -d price_intelligence \
     < backend-express/db/00_performance_optimization.sql
   ```

2. **Verify indexes exist:**
   ```bash
   PGPASSWORD=postgres psql -h localhost -U postgres -d price_intelligence << EOF
   SELECT schemaname, tablename, indexname FROM pg_indexes 
   WHERE schemaname='public' ORDER BY tablename;
   EOF
   ```

3. **Check index usage:**
   ```bash
   PGPASSWORD=postgres psql -h localhost -U postgres -d price_intelligence << EOF
   SELECT relname, idx_blks_read, idx_blks_hit FROM pg_statio_user_indexes;
   EOF
   ```

4. **Analyze query plan:**
   ```bash
   PGPASSWORD=postgres psql -h localhost -U postgres -d price_intelligence << EOF
   EXPLAIN ANALYZE SELECT * FROM price_history WHERE product_id = 1;
   EOF
   ```

---

### 7. Docker Compose Issues

#### Problem: "Docker Compose fails to start"

**Error:**
```
ERROR: Service 'postgres' failed to start: driver failed programming external connectivity
```

**Solutions:**

1. **Check Docker daemon is running:**
   ```bash
   docker ps
   ```

2. **Check port conflicts:**
   ```bash
   netstat -ano | findstr :5432  # PostgreSQL
   netstat -ano | findstr :6379  # Redis
   netstat -ano | findstr :8000  # API
   ```

3. **Clean up existing containers:**
   ```bash
   docker-compose down -v
   docker system prune -a
   docker-compose up -d
   ```

4. **Check Docker compose file:**
   ```bash
   docker-compose config  # Validates syntax
   ```

5. **View service logs:**
   ```bash
   docker-compose logs postgres
   docker-compose logs redis
   ```

---

### 8. Memory/CPU Issues

#### Problem: "High memory or CPU usage"

**Solutions:**

1. **Monitor resource usage:**
   ```bash
   # Windows
   Get-Process | Where-Object {$_.Name -like "python*" -or $_.Name -like "node*"}
   
   # Linux
   top -bn1 | head -20
   ```

2. **Reduce Celery worker concurrency:**
   ```bash
   celery -A app.celery_app worker --concurrency=2 --loglevel=info
   ```

3. **Check Redis memory:**
   ```bash
   redis-cli INFO memory
   # Look for: used_memory_human
   ```

4. **Reduce Redis cache size:**
   ```python
   # backend/app/redis_cache.py
   # Reduce TTL values:
   CACHE_KEYS = {
       'search': (300, 3600),      # Reduce from 600 to 300
       'compare': (300, 3600),     # Reduce from 600 to 300
       'product': (900, 3600),     # Reduce from 1800 to 900
   }
   ```

5. **Clear cache to free memory:**
   ```bash
   redis-cli FLUSHDB
   ```

---

### 9. Frontend Performance Issues

#### Problem: "Frontend loads slowly"

**Solutions:**

1. **Check browser DevTools:**
   - Open: `F12` → Network tab
   - Look for slow resources
   - Check: Script sizes, DOM rendering time

2. **Enable code splitting in React:**
   ```javascript
   // src/App.jsx
   import { LazyLoadSection } from './utils/codeSplitting'
   
   <LazyLoadSection>
     <YourComponent />
   </LazyLoadSection>
   ```

3. **Enable lazy image loading:**
   ```javascript
   // src/components/ProductCard.jsx
   import { LazyImage } from '../utils/imageOptimization'
   
   <LazyImage src={imageUrl} alt="Product" />
   ```

4. **Check Vite bundle size:**
   ```bash
   cd frontend
   npm run build
   npm run preview
   ```

5. **Use browser Performance API:**
   ```javascript
   // Check performance monitoring
   curl http://localhost:8000/api/metrics
   ```

---

### 10. Async Task Not Completing

#### Problem: "Task status remains 'PENDING'"

**Solutions:**

1. **Check task in Flower:**
   - Open: `http://localhost:5555`
   - Look for task status and logs

2. **Check Celery logs:**
   ```bash
   celery -A app.celery_app inspect active
   celery -A app.celery_app inspect registered
   ```

3. **Manually test task:**
   ```python
   from backend.app.celery_app import app
   
   result = app.send_task('app.tasks.debug_task')
   print(result.get(timeout=10))
   ```

4. **Check Redis for task status:**
   ```bash
   redis-cli KEYS "celery-*"
   redis-cli GET "celery-task-meta-<task_id>"
   ```

5. **Increase task timeout:**
   ```python
   # backend/app/celery_app.py
   app.conf.task_soft_time_limit = 600  # 10 minutes
   app.conf.task_time_limit = 900       # 15 minutes
   ```

---

## Health Check Commands

Run these to verify all systems are working:

```bash
# 1. Redis
redis-cli ping
# Expected: PONG

# 2. PostgreSQL
psql -h localhost -U postgres -c "SELECT 1"
# Expected: (1 row)

# 3. Python API
curl http://localhost:8000/api/metrics
# Expected: JSON response

# 4. Celery workers
celery -A app.celery_app inspect active
# Expected: List of active tasks

# 5. All services (Docker)
docker-compose ps
# Expected: All services "Up"

# 6. Health check script
./health_check.bat
# Expected: All checks pass
```

---

## Performance Benchmarking

Run performance tests to verify optimizations:

```bash
# Install test dependencies
pip install redis psycopg2-binary requests

# Run all benchmarks
python benchmark.py all

# Individual benchmarks
python benchmark.py redis
python benchmark.py async
python benchmark.py database
python benchmark.py compression
```

Expected Results:
- Redis operations: < 5ms
- API responses: < 50ms (async) vs 1-3s (sync)
- Database queries: < 100ms (with indexes)
- Response compression: 70-80% size reduction

---

## Getting Help

1. **Check logs:**
   ```bash
   docker-compose logs [service]
   ```

2. **Documentation:**
   - `PERFORMANCE_QUICK_START.md` - Quick setup guide
   - `PERFORMANCE_OPTIMIZATION_COMPLETE.md` - Full details
   - `CDN_IMPLEMENTATION_GUIDE.md` - Image delivery

3. **Debug mode:**
   ```bash
   # Enable verbose logging
   celery -A app.celery_app worker --loglevel=debug
   
   # API debug mode
   export FLASK_ENV=development
   python app/main_optimized.py
   ```

4. **Common error patterns:**
   - Connection refused: Service not running
   - Port already in use: Kill existing process
   - Permission denied: Run with admin/sudo
   - Out of memory: Reduce worker concurrency

---

## Quick Reset

If everything is broken, clean and restart:

```bash
# Stop all services
docker-compose down -v

# Clean up caches
rm -rf __pycache__ backend/__pycache__ backend/app/__pycache__

# Restart everything
docker-compose up -d

# Verify
./health_check.bat
```

