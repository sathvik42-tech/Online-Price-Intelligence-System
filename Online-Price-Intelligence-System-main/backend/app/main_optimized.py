"""
Enhanced API with Performance Optimizations:
- Redis caching for common queries
- Celery async task processing (non-blocking)
- Gzip compression for all responses
- Result pagination
- Performance profiling
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging
import os
import time
import asyncio
import uuid
from .preprocessing import preprocess_image
from .model import predict_image
from .routers import upload, auth
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
# Robust module imports
from .fast_search import fast_search_all_platforms
from ..utils.aggregation import aggregate_prices
from ..utils.scoring import find_best_deal
from ..reporting import calculate_stats
from ..utils.history import record_price_history
from ..main_scraper import search_all_platforms
from ..database import get_connection
from .redis_cache import cache, CACHE_KEYS
from .celery_app import celery_app
from .tasks import (
    scrape_all_platforms,
    process_price_comparison,
    process_image,
)

logger = logging.getLogger(__name__)

# Configure logging to a file for better debugging
file_handler = logging.FileHandler("backend_debug.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

app = FastAPI(
    title="Online Price Intelligence System API",
    description="Optimized API with Redis caching and async task processing"
)

# Enable GZIP compression
app.add_middleware(GZipMiddleware, minimum_size=500)

app.include_router(upload.router, prefix="/api")
app.include_router(auth.router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Static Files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
UPLOADS_DIR = os.path.join(STATIC_DIR, "uploads")
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Performance profiling middleware
try:
    from .performance_profiler import PerformanceProfiler
    profiler = PerformanceProfiler()
except ImportError:
    profiler = None

@app.middleware("http")
async def profile_request(request, call_next):
    try:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        if profiler:
            profiler.record_request(request.url.path, request.method, process_time)
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        import traceback
        error_msg = f"GLOBAL ERROR: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        with open("backend_crash.log", "a") as f:
            f.write(error_msg + "\n" + "="*50 + "\n")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal Server Error: {str(e)}", "traceback": traceback.format_exc()}
        )

# Rate Limiter
rate_limit_store = {}
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    rate_limit_store[client_ip] = [t for t in rate_limit_store.get(client_ip, []) if current_time - t < 60]
    if len(rate_limit_store[client_ip]) >= 100:
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    rate_limit_store[client_ip].append(current_time)
    return await call_next(request)

@app.get("/")
async def root():
    return {
        "message": "Online Price Intelligence System API v2.0",
        "cache": "connected" if cache.get_stats().get("available") else "disconnected"
    }

# --- Price Comparison ---

@app.post("/api/compare-prices")
async def compare_prices_async(
    product: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    async_mode: bool = Query(True),
    fast: bool = Query(True)
):
    q_key = " ".join(product.strip().split()).lower()
    cache_key = CACHE_KEYS["compare"]["key"].format(query=q_key)
    cached_data = cache.get(cache_key)
    
    if cached_data:
        popular_key = CACHE_KEYS["popular_searches"]["key"]
        cache.zincrby(popular_key, 1, q_key)
        products = cached_data.get("products", [])[offset : offset + limit]
        return {**cached_data, "products": products, "source": "cache"}

    # If not cached, perform search
    if fast:
        raw_results = {}
        try:
            # Robust selection and execution of search backend
            try:
                # Robust selection and execution of search backend
                if fast_search_all_platforms:
                    raw_results = await asyncio.wait_for(
                        fast_search_all_platforms(q_key, timeout=25),
                        timeout=55.0,
                    )
                
                if (not raw_results) and search_all_platforms:
                    raw_results = await asyncio.wait_for(
                        asyncio.to_thread(search_all_platforms, q_key, deep_scan=True, timeout=50),
                        timeout=60.0,
                    )
            except asyncio.TimeoutError:
                logger.error(f"Search timed out for: {q_key}")
                if not raw_results:
                    raise HTTPException(status_code=408, detail="Search timed out. Please try again later.")
            except Exception as e:
                logger.error(f"Search backend error: {str(e)}", exc_info=True)
                if not raw_results:
                    raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

            # Final safety check for any awaitable results (Futures, Coroutines, etc.)
            while hasattr(raw_results, "__await__") or asyncio.iscoroutine(raw_results):
                logger.info("Awaiting unexpected search result object...")
                raw_results = await raw_results

            if not isinstance(raw_results, dict):
                logger.error(f"Search backend returned {type(raw_results)} instead of dict. Attempting conversion...")
                if hasattr(raw_results, "items"):
                    raw_results = dict(raw_results)
                else:
                    raw_results = {}

            # Remove snapdeal results from raw_results before aggregation
            if "snapdeal" in raw_results:
                logger.info("Filtering out Snapdeal results as requested.")
                del raw_results["snapdeal"]

            aggregated = aggregate_prices(raw_results, query=q_key) if raw_results else []
            
            # Additional filter just in case Snapdeal results were added by other means
            aggregated = [p for p in aggregated if p.get("platform", "").lower() != "snapdeal"]

            best_deal = find_best_deal(aggregated) if (aggregated and find_best_deal) else None
            stats = calculate_stats(aggregated) if (aggregated and calculate_stats) else {}
            
            result = {
                "query": q_key,
                "products": aggregated,
                "best_deal": best_deal,
                "statistics": stats,
                "status": "success",
            }
            if cache:
                cache.set(cache_key, result, ttl=CACHE_KEYS["compare"]["ttl"])
            return {**result, "products": aggregated[offset : offset + limit], "source": "fast"}
        except asyncio.TimeoutError:
            logger.error(f"Search timed out for: {q_key}")
            # Try to aggregate whatever results we got if any, or return empty
            # If fast_search populated some partial results in a shared dict (not the case here yet)
            # For now, return a more helpful error than a generic 500
            raise HTTPException(
                status_code=408, 
                detail="The search is taking longer than expected. Please try again or check back in a moment."
            )
        except Exception as e:
            logger.error(f"Search error: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
    
    # thorough search (can be slower)
    if not fast and not async_mode:
        try:
            # Fallback to standard search if fast search is disabled
            if fast_search_all_platforms:
                raw_results = await fast_search_all_platforms(q_key, timeout=40)
            elif search_all_platforms:
                raw_results = await asyncio.to_thread(search_all_platforms, q_key)
            else:
                raise HTTPException(status_code=503, detail="Search backend unavailable")
                
            aggregated = aggregate_prices(raw_results, query=q_key)
            result = {
                "query": q_key,
                "products": aggregated,
                "best_deal": find_best_deal(aggregated),
                "statistics": calculate_stats(aggregated),
                "status": "success",
            }
            cache.set(cache_key, result, ttl=CACHE_KEYS["compare"]["ttl"])
            return {**result, "products": aggregated[offset : offset + limit], "source": "sync"}
        except Exception as e:
            logger.error(f"Thorough search error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    if async_mode:
        task = process_price_comparison.apply_async(args=[q_key], expires=35)
        return JSONResponse(status_code=202, content={"task_id": task.id, "status": "processing"})
    
    raise HTTPException(status_code=400, detail="Invalid request parameters")

@app.get("/api/compare-prices")
async def get_compare_prices(
    product: str = Query(...), 
    limit: int = 10, 
    offset: int = 0,
    async_mode: bool = False,
    fast: bool = True
):
    return await compare_prices_async(product, limit, offset, async_mode, fast)

@app.get("/api/task-status/{task_id}")
async def get_task_status(task_id: str, limit: int = 10, offset: int = 0):
    task = celery_app.AsyncResult(task_id)
    if task.state == "SUCCESS":
        result = task.result
        if isinstance(result, dict) and "products" in result:
            products = result.get("products", [])[offset : offset + limit]
            return {**result, "products": products, "status": "completed"}
        return {"result": result, "status": "completed"}
    return {"status": task.state.lower()}

@app.get("/api/popular-searches")
async def get_popular_searches(limit: int = 10):
    popular_key = CACHE_KEYS["popular_searches"]["key"]
    items = cache.zrevrange(popular_key, 0, limit - 1, withscores=True)
    return [{"query": m, "count": int(s)} for m, s in (items or [])]

@app.delete("/api/cache")
async def clear_cache(product: str = None):
    if product:
        cache.delete(CACHE_KEYS["compare"]["key"].format(query=product.lower()))
        return {"status": "success"}
    cache.clear_pattern("compare_*")
    return {"status": "success"}

@app.get("/api/cache-stats")
async def get_cache_stats():
    return {"cache_status": cache.get_stats()}

@app.get("/api/products/{product_id}")
async def get_product_details(product_id: int):
    cache_key = CACHE_KEYS["product_details"]["key"].format(id=product_id)
    cached = cache.get(cache_key)
    if cached: return {"source": "cache", **cached}
    if not get_connection: raise HTTPException(status_code=503, detail="DB Init failed")
    
    def _query():
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT product_id, name, category, image_url, description, created_at FROM products WHERE product_id = %s", (product_id,))
                row = cur.fetchone()
                if not row: return None
                cur.execute("SELECT store_name, price, currency, product_url, timestamp FROM prices WHERE product_id = %s ORDER BY timestamp DESC LIMIT 20", (product_id,))
                prices = cur.fetchall()
                return {
                    "product": {"id": row[0], "name": row[1], "category": row[2], "image": row[3], "desc": row[4], "date": row[5].isoformat() if row[5] else None},
                    "recent_prices": [{"store": r[0], "price": float(r[1]), "currency": r[2], "url": r[3], "time": r[4].isoformat()} for r in prices]
                }
        finally: conn.close()
    
    data = await asyncio.to_thread(_query)
    if not data: raise HTTPException(status_code=404)
    cache.set(cache_key, data, ttl=CACHE_KEYS["product_details"]["ttl"])
    return {"source": "database", **data}

@app.post("/api/predict")
async def predict_image_async(
    file: UploadFile = File(...),
    async_mode: bool = Query(False)
):
    contents = await file.read()
    image_id = str(uuid.uuid4())
    ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    filename = f"{image_id}.{ext}"
    file_path = os.path.join(UPLOADS_DIR, filename)
    with open(file_path, "wb") as f: f.write(contents)
    
    # Use relative path for proxy support
    image_url = f"/static/uploads/{filename}"

    if async_mode:
        try:
            task = process_image.delay(file_path, filename)
            return JSONResponse(status_code=202, content={"task_id": task.id, "image_url": image_url, "status": "processing"})
        except Exception as e:
            logger.warning(f"Celery failed, falling back to inline prediction: {e}")
            # Fallback to synchronous prediction
    
    try:
        # Offload CPU-intensive model prediction and preprocessing to a thread
        processed_image = await asyncio.to_thread(preprocess_image, contents)
        # Pass raw contents to predict_image for OCR analysis
        predictions = await asyncio.to_thread(predict_image, processed_image, 3, contents)
        return {"image_url": image_url, "predictions": predictions, "status": "success"}
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze image: {str(e)}")

@app.get("/api/price-history")
async def get_price_history(product_id: str):
    return {"product_id": product_id, "history": []}

@app.get("/api/metrics")
async def get_metrics():
    return {"cache": cache.get_stats(), "status": "healthy"}

@app.get("/api/performance")
async def get_performance_summary():
    return profiler.get_summary() if profiler else {}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
