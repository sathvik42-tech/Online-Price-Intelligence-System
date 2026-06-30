"""
Database Query Optimization Module

Provides:
- Optimized query patterns
- Index recommendations
- Query analysis helpers
- Connection pooling info
"""

# === MIGRATION GUIDE: Database Performance Optimization ===

# Run these SQL commands to optimize your PostgreSQL database:

SQL_OPTIMIZATIONS = """
-- ============================================================================
-- PERFORMANCE OPTIMIZATION SCRIPT FOR POSTGRESQL
-- ============================================================================

-- 1. COMPOSITE INDEXES for common query patterns
-- ============================================================================

-- For queries: WHERE user_id = ? AND created_at > ?
CREATE INDEX IF NOT EXISTS idx_price_alerts_user_created 
ON price_alerts(user_id, created_at DESC);

-- For queries: WHERE user_id = ? AND product_id = ?
CREATE INDEX IF NOT EXISTS idx_wishlist_user_product 
ON wishlist(user_id, product_id);

-- For queries: WHERE user_id = ? ORDER BY search_time DESC LIMIT ?
CREATE INDEX IF NOT EXISTS idx_search_history_user_time 
ON search_history(user_id, search_time DESC);

-- For queries: WHERE product_id = ? ORDER BY recorded_at DESC
CREATE INDEX IF NOT EXISTS idx_price_history_product_time 
ON price_history(product_id, recorded_at DESC);

-- 2. PARTIAL INDEXES for active/recent data
-- ============================================================================

-- Index only recent searches (last 3 months)
CREATE INDEX IF NOT EXISTS idx_search_history_recent 
ON search_history(user_id, search_time DESC) 
WHERE search_time > CURRENT_TIMESTAMP - INTERVAL '3 months';

-- Index only recent price history (last 30 days)
CREATE INDEX IF NOT EXISTS idx_price_history_recent 
ON price_history(product_id, recorded_at DESC)
WHERE recorded_at > CURRENT_TIMESTAMP - INTERVAL '30 days';

-- 3. CONSTRAINT and DATA TYPE OPTIMIZATION
-- ============================================================================

-- Ensure product_id is VARCHAR(255) for consistency across tables
ALTER TABLE price_alerts ALTER COLUMN product_id TYPE VARCHAR(255);
ALTER TABLE wishlist ALTER COLUMN product_id TYPE VARCHAR(255);

-- Add NOT NULL constraints where appropriate
ALTER TABLE price_alerts ALTER COLUMN user_id SET NOT NULL;
ALTER TABLE wishlist ALTER COLUMN user_id SET NOT NULL;

-- 4. ANALYZE DATABASE STATISTICS for Query Planner
-- ============================================================================

-- Run after data changes to update query planner statistics
ANALYZE users;
ANALYZE price_alerts;
ANALYZE search_history;
ANALYZE wishlist;
ANALYZE price_history;

-- 5. VACUUM to reclaim space and optimize performance
-- ============================================================================

-- Run periodically (daily/weekly) to clean up dead rows
VACUUM ANALYZE price_alerts;
VACUUM ANALYZE search_history;
VACUUM ANALYZE wishlist;
VACUUM ANALYZE price_history;

-- 6. ENABLE AUTOVACUUM for automatic maintenance
-- ============================================================================

ALTER TABLE price_alerts SET (autovacuum_vacuum_scale_factor = 0.01);
ALTER TABLE search_history SET (autovacuum_vacuum_scale_factor = 0.01);
ALTER TABLE wishlist SET (autovacuum_vacuum_scale_factor = 0.01);

-- 7. ADD PARTITIONING for very large tables (optional, for > 1M rows)
-- ============================================================================

-- Partition price_history by month for faster queries
-- CREATE TABLE price_history_2026_03 PARTITION OF price_history
--   FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

-- 8. ENABLE QUERY STATISTICS
-- ============================================================================

-- Create extensions for query analysis
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- View query performance stats:
-- SELECT query, calls, total_time, mean_time 
-- FROM pg_stat_statements 
-- ORDER BY mean_time DESC LIMIT 10;

-- 9. CONNECTION POOLING CONFIGURATION
-- ============================================================================

-- Configure PgBouncer for connection pooling:
-- Set in your application connection string:
-- postgres://user:pass@localhost:6432/price_intelligence?pool_size=20

-- Recommended pool sizes:
-- - max_connections = CPU cores * 4 (typically 8-16)
-- - min_idle = 2-4
-- - statement_timeout = 30000 (30 seconds)

"""

QUERY_OPTIMIZATION_GUIDE = """
-- ============================================================================
-- OPTIMIZED QUERY PATTERNS
-- ============================================================================

-- 1. GET USER ALERTS (with limit to avoid loading too much data)
-- ============================================================================

-- OPTIMIZED (fast):
SELECT id, product_name, current_price, target_price, created_at
FROM price_alerts
WHERE user_id = $1
ORDER BY created_at DESC
LIMIT 20 OFFSET $2;

-- NOT OPTIMIZED (slow):
SELECT * FROM price_alerts WHERE user_id = $1;  -- loads all columns
SELECT * FROM price_alerts WHERE user_id = $1 AND product_id = $2;  -- no LIMIT

-- 2. GET SEARCH HISTORY with pagination
-- ============================================================================

-- OPTIMIZED (fast):
SELECT search_query, search_time
FROM search_history
WHERE user_id = $1
ORDER BY search_time DESC
LIMIT 50 OFFSET $2;

-- Benefits:
-- - Uses covering index idx_search_history_user_time
-- - LIMIT prevents loading entire history
-- - Pagination allows client-side iteration

-- 3. GET RECENT PRICE HISTORY
-- ============================================================================

-- OPTIMIZED (fast):
SELECT price, recorded_at
FROM price_history
WHERE product_id = $1
  AND recorded_at > CURRENT_TIMESTAMP - INTERVAL '30 days'
ORDER BY recorded_at DESC
LIMIT 100;

-- Benefits:
-- - Uses partial index idx_price_history_recent
-- - Date filter reduces result set
-- - Most queries only need recent data

-- 4. BULK INSERT with BATCH for efficiency
-- ============================================================================

-- OPTIMIZED (fast):
INSERT INTO price_history (product_id, price, recorded_at)
VALUES
  ($1, $2, $3),
  ($4, $5, $6),
  ($7, $8, $9)
ON CONFLICT DO NOTHING;

-- Benefits:
-- - Single network round trip
-- - Single query plan
-- - Faster than multiple individual INSERTs

-- 5. JOIN QUERY with LIMIT
-- ============================================================================

-- OPTIMIZED (fast):
SELECT u.id, u.email, COUNT(pa.id) as alert_count
FROM users u
LEFT JOIN price_alerts pa ON u.id = pa.user_id
WHERE u.created_at > CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY u.id
LIMIT 100;

-- Benefits:
-- - Explicit JOIN returns only needed columns
-- - GROUP BY aggregates efficiently
-- - LIMIT prevents large result sets

-- 6. DELETE OLD DATA with batch size limit
-- ============================================================================

-- OPTIMIZED (fast):
DELETE FROM price_history
WHERE recorded_at < CURRENT_TIMESTAMP - INTERVAL '90 days'
LIMIT 1000;

-- Benefits:
-- - LIMIT prevents long transactions
-- - Can be run frequently without blocking
-- - Run this in a scheduled job

"""

PERFORMANCE_TIPS = """
-- ============================================================================
-- PERFORMANCE TIPS & BEST PRACTICES
-- ============================================================================

1. ALWAYS USE INDEXES FOR:
   - WHERE columns (filter)
   - JOIN columns (join key)  
   - ORDER BY columns (sorting)
   - GROUP BY columns (grouping)

2. AVOID:
   - SELECT * (use specific columns)
   - Large result sets (use LIMIT/OFFSET)
   - Functions in WHERE clause (WHERE LOWER(name) = ?)
   - Correlated subqueries
   - N+1 queries (batch related queries)

3. USE EXPLAIN ANALYZE:
   EXPLAIN ANALYZE
   SELECT * FROM price_alerts WHERE user_id = $1 LIMIT 20;
   
   Look for:
   - Sequential Scans = bad (need index)
   - High actual rows = fetch too much
   - High planning time = complex query

4. CONNECTION POOLING:
   - Use connection pools (min 2, max CPU*4)
   - Set statement_timeout to catch slow queries
   - Monitor active connections

5. CACHING STRATEGY:
   - Cache queries executed > 100 times/day
   - Cache results with TTL 5-30 minutes
   - Invalidate on write operations
   - Monitor cache hit rate (target: 80%+)

6. DATA CLEANUP:
   - Archive old data (>90 days) to separate table
   - Run VACUUM ANALYZE weekly
   - Monitor table sizes with: 
     SELECT * FROM pg_tables WHERE schemaname != 'pg_catalog';

7. MONITORING:
   - Monitor slow queries (> 1 second)
   - Check index bloat: SELECT * FROM pg_stat_user_indexes;
   - Monitor lock contention
   - Check cache hit ratio

"""

# Python helper functions for database optimization

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """Helper class for database optimization"""
    
    def __init__(self, db_connection):
        self.conn = db_connection
    
    def analyze_query(self, query: str, params: tuple = ()) -> Dict[str, Any]:
        """
        Analyze query performance using EXPLAIN ANALYZE
        
        Returns:
        {
            'plan': query plan,
            'runtime': execution time,
            'rows': actual rows returned,
            'optimizations': list of suggestions
        }
        """
        try:
            with self.conn.cursor() as cur:
                analysis_query = f"EXPLAIN ANALYZE {query}"
                cur.execute(analysis_query, params)
                plan = cur.fetchall()
                
                suggestions = []
                plan_str = str(plan)
                
                if "Seq Scan" in plan_str:
                    suggestions.append("Sequential scan detected. Consider adding an index.")
                if "Sort" in plan_str:
                    suggestions.append("Sort operation detected. Consider index on ORDER BY column.")
                if "actual rows" in plan_str and "estimated" in plan_str:
                    suggestions.append("Large difference between estimated and actual rows. Run ANALYZE.")
                
                return {
                    "plan": plan,
                    "suggestions": suggestions
                }
        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            return {"error": str(e)}
    
    def add_index(self, table: str, columns: List[str], index_name: str = None) -> bool:
        """Create index for better query performance"""
        if not index_name:
            index_name = f"idx_{table}_{'_'.join(columns)}"
        
        columns_str = ", ".join(columns)
        query = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({columns_str})"
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(query)
            self.conn.commit()
            logger.info(f"Index created: {index_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            return False
    
    def get_table_stats(self, table: str) -> Dict[str, Any]:
        """Get statistics about a table"""
        try:
            with self.conn.cursor() as cur:
                # Get table size
                cur.execute(f"""
                    SELECT 
                        pg_size_pretty(pg_total_relation_size('{table}')) as size,
                        (SELECT count(*) FROM {table}) as row_count
                """)
                size_row = cur.fetchone()
                
                # Get index info
                cur.execute(f"""
                    SELECT indexname, idx_scan, idx_tup_read, idx_tup_fetch
                    FROM pg_stat_user_indexes
                    WHERE relname = '{table}'
                """)
                indexes = cur.fetchall()
                
                return {
                    "size": size_row[0] if size_row else "?",
                    "rows": size_row[1] if size_row else 0,
                    "indexes": indexes
                }
        except Exception as e:
            logger.error(f"Error getting table stats: {e}")
            return {}
    
    def vacuum_and_analyze(self, table: str) -> bool:
        """Run VACUUM ANALYZE to optimize table"""
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"VACUUM ANALYZE {table}")
            self.conn.commit()
            logger.info(f"VACUUM ANALYZE completed for {table}")
            return True
        except Exception as e:
            logger.error(f"Error during VACUUM: {e}")
            return False
    
    def get_slow_queries(self, minutes: int = 60, limit: int = 10) -> List[Dict]:
        """Get slowest queries from pg_stat_statements"""
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"""
                    SELECT query, calls, total_time, mean_time
                    FROM pg_stat_statements
                    WHERE query NOT LIKE 'PLAN %'
                    ORDER BY mean_time DESC
                    LIMIT {limit}
                """)
                return cur.fetchall()
        except Exception as e:
            logger.error(f"Error getting slow queries: {e}")
            return []
