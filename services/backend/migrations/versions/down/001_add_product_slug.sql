-- Migration: 001_add_product_slug
-- Description: Rollback slug column from catalog_products table
-- Created: 2025-06-06

-- Drop unique constraint
ALTER TABLE catalog_products
DROP CONSTRAINT IF EXISTS unique_product_slug;

-- Drop index
DROP INDEX IF EXISTS idx_catalog_products_slug;

-- Drop slug column
ALTER TABLE catalog_products
DROP COLUMN IF EXISTS slug;

-- Drop create_slug function
DROP FUNCTION IF EXISTS create_slug(TEXT, INTEGER);
