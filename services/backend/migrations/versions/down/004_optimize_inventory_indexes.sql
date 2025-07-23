-- Migration: 004_optimize_inventory_indexes
-- Description: Rollback targeted inventory optimization indexes
-- Created: 2025-01-23

-- Drop all optimization indexes
DROP INDEX IF EXISTS idx_inventory_availability_price_filter;
DROP INDEX IF EXISTS idx_inventory_product_availability;
DROP INDEX IF EXISTS idx_products_category_filter;
DROP INDEX IF EXISTS idx_products_master_category_complete;
DROP INDEX IF EXISTS idx_article_type_subcategory;
DROP INDEX IF EXISTS idx_subcategory_master;
DROP INDEX IF EXISTS idx_inventory_selective_filter;

-- Restore original single-column indexes
CREATE INDEX idx_catalog_product_inventory_is_active ON catalog_product_inventory(is_active);
CREATE INDEX idx_catalog_product_inventory_is_in_stock ON catalog_product_inventory(is_in_stock);
