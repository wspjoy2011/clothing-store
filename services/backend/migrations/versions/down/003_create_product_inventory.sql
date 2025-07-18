-- Migration: 003_create_product_inventory
-- Description: Rollback product inventory table
-- Created: 2025-01-18

-- Drop trigger and function
DROP TRIGGER IF EXISTS trigger_catalog_product_inventory_updated_at ON catalog_product_inventory;
DROP FUNCTION IF EXISTS update_catalog_product_inventory_updated_at();

-- Drop indexes
DROP INDEX IF EXISTS idx_catalog_product_inventory_product_id;
DROP INDEX IF EXISTS idx_catalog_product_inventory_is_active;
DROP INDEX IF EXISTS idx_catalog_product_inventory_is_in_stock;
DROP INDEX IF EXISTS idx_catalog_product_inventory_base_price;
DROP INDEX IF EXISTS idx_catalog_product_inventory_available_quantity;

-- Drop table
DROP TABLE IF EXISTS catalog_product_inventory;
