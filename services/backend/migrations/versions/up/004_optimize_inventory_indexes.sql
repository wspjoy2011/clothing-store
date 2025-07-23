-- Migration: 004_optimize_inventory_indexes
-- Description: Add targeted indexes based on EXPLAIN ANALYZE results
-- Created: 2025-01-23

-- Drop existing single-column indexes that will be replaced by composite ones
DROP INDEX IF EXISTS idx_catalog_product_inventory_is_active;
DROP INDEX IF EXISTS idx_catalog_product_inventory_is_in_stock;

-- CRITICAL: Main filter index for availability + price filtering
-- This will eliminate Seq Scan on inventory table
CREATE INDEX idx_inventory_availability_price_filter
ON catalog_product_inventory (is_active, is_in_stock, base_price, sale_price)
WHERE is_active = true AND is_in_stock = true;

-- Secondary index for efficient product joins
CREATE INDEX idx_inventory_product_availability
ON catalog_product_inventory (product_id, is_active, is_in_stock)
WHERE is_active = true AND is_in_stock = true;

-- Index for products filtering (year + gender + category joins)
CREATE INDEX idx_products_category_filter
ON catalog_products (article_type_id, year, gender, product_id);

-- Covering index for master category filtering
CREATE INDEX idx_products_master_category_complete
ON catalog_products (article_type_id, year, gender, product_id, product_display_name, image_url, slug)
WHERE year BETWEEN 2010 AND 2030;

-- Index for article_type joins
CREATE INDEX idx_article_type_subcategory
ON catalog_article_type (sub_category_id, article_type_id);

-- Index for subcategory filtering
CREATE INDEX idx_subcategory_master
ON catalog_sub_category (master_category_id, sub_category_id);

-- Partial index specifically for price+availability queries (most selective)
CREATE INDEX idx_inventory_selective_filter
ON catalog_product_inventory (product_id)
WHERE is_active = true
  AND is_in_stock = true
  AND COALESCE(sale_price, base_price) BETWEEN 1.0 AND 5000.0;
