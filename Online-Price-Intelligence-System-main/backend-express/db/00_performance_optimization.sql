-- ============================================================================
-- DATABASE PERFORMANCE OPTIMIZATION MIGRATION
-- Online Price Intelligence System
-- ============================================================================

-- Run this migration to optimize your PostgreSQL database for production.
-- Expected improvement: 5-20x faster query performance

-- ============================================================================
-- 1. ADD COMPOSITE INDEXES
-- ============================================================================

-- Index for common alert queries: user + created_at
CREATE INDEX IF NOT EXISTS idx_price_alerts_user_created 
ON price_alerts(user_id, created_at DESC);

-- Index for wishlist queries: user + product
CREATE INDEX IF NOT EXISTS idx_wishlist_user_product 
ON wishlist(user_id, product_id);

-- Index for search history queries: user + time
CREATE INDEX IF NOT EXISTS idx_search_history_user_time 
ON search_history(user_id, search_time DESC);

-- Index for price history queries: product + time
CREATE INDEX IF NOT EXISTS idx_price_history_product_time 
ON price_history(product_id, recorded_at DESC);

-- ============================================================================
-- 2. ADD PARTIAL INDEXES for recent data (common use case)
-- ============================================================================

-- Index only recent searches (last 3 months) - faster for most queries
CREATE INDEX IF NOT EXISTS idx_search_history_recent 
ON search_history(user_id, search_time DESC) 
WHERE search_time > CURRENT_TIMESTAMP - INTERVAL '3 months';

-- Index only recent price history (last 30 days) - smaller, faster index
CREATE INDEX IF NOT EXISTS idx_price_history_recent 
ON price_history(product_id, recorded_at DESC)
WHERE recorded_at > CURRENT_TIMESTAMP - INTERVAL '30 days';

-- ============================================================================
-- 3. ADD FUNCTIONAL INDEXES for search optimization
-- ============================================================================

-- Index for email-based searches (case-insensitive)
CREATE INDEX IF NOT EXISTS idx_users_email_lower 
ON users(LOWER(email));

-- Index for product name searches (for filtering)
CREATE INDEX IF NOT EXISTS idx_wishlist_product_name 
ON wishlist(LOWER(product_name));

-- ============================================================================
-- 4. OPTIMIZE DATA TYPES and CONSTRAINTS
-- ============================================================================

-- Ensure consistent VARCHAR lengths
ALTER TABLE price_alerts 
  ALTER COLUMN product_id TYPE VARCHAR(255);

ALTER TABLE wishlist 
  ALTER COLUMN product_id TYPE VARCHAR(255);

-- Ensure required columns are NOT NULL
ALTER TABLE price_alerts 
  ALTER COLUMN user_id SET NOT NULL;

ALTER TABLE wishlist 
  ALTER COLUMN user_id SET NOT NULL;

ALTER TABLE search_history 
  ALTER COLUMN user_id SET NOT NULL;

-- ============================================================================
-- 5. ADD USEFUL COLUMNS for better querying
-- ============================================================================

-- Add updated_at column for tracking modifications
ALTER TABLE price_alerts ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE wishlist ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Index on updated_at for sorting by recent changes
CREATE INDEX IF NOT EXISTS idx_price_alerts_updated 
ON price_alerts(updated_at DESC);

-- ============================================================================
-- 6. UPDATE STATISTICS for Query Planner
-- ============================================================================

-- Analyze all tables to update query planner statistics
-- This helps PostgreSQL make better index decisions
ANALYZE;

-- Specific table analysis (if preferred)
-- ANALYZE users;
-- ANALYZE price_alerts;
-- ANALYZE search_history;
-- ANALYZE wishlist;
-- ANALYZE price_history;

-- ============================================================================
-- 7. RECLAIM SPACE AND OPTIMIZE (VACUUM)
-- ============================================================================

-- Optional: Run VACUUM FULL for maximum optimization
-- WARNING: This locks tables. Run during maintenance window
-- VACUUM FULL ANALYZE;

-- For production: Use regular VACUUM
-- VACUUM ANALYZE price_alerts;
-- VACUUM ANALYZE search_history;
-- VACUUM ANALYZE wishlist;
-- VACUUM ANALYZE price_history;

-- ============================================================================
-- 8. SET UP AUTOVACUUM for ongoing optimization
-- ============================================================================

-- Tune autovacuum for high-traffic tables
ALTER TABLE price_alerts SET (autovacuum_vacuum_scale_factor = 0.01);
ALTER TABLE search_history SET (autovacuum_vacuum_scale_factor = 0.01);
ALTER TABLE wishlist SET (autovacuum_vacuum_scale_factor = 0.01);

-- ============================================================================
-- 9. ENABLE QUERY STATISTICS TRACKING
-- ============================================================================

-- Create extension for query statistics (optional but recommended)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Verify indexes are created:
-- SELECT * FROM pg_stat_user_indexes WHERE tablename IN ('price_alerts', 'wishlist', 'search_history', 'price_history');

-- Check table sizes:
-- SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
-- FROM pg_tables WHERE schemaname = 'public';

-- View slowest queries (requires pg_stat_statements):
-- SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
