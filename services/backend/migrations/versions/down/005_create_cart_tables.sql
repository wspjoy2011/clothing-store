-- Migration: 005_create_cart_tables
-- Description: Rollback checkout module tables (checkout_cart_tokens, checkout_cart, checkout_cart_items)
-- Created: 2025-01-27

-- Drop triggers and functions
DROP TRIGGER IF EXISTS trigger_checkout_cart_items_updated_at ON checkout_cart_items;
DROP TRIGGER IF EXISTS trigger_checkout_cart_updated_at ON checkout_cart;
DROP TRIGGER IF EXISTS trigger_checkout_cart_tokens_updated_at ON checkout_cart_tokens;

DROP FUNCTION IF EXISTS update_checkout_cart_items_updated_at();
DROP FUNCTION IF EXISTS update_checkout_cart_updated_at();
DROP FUNCTION IF EXISTS update_checkout_cart_tokens_updated_at();

-- Drop indexes
DROP INDEX IF EXISTS idx_checkout_cart_items_updated_at;
DROP INDEX IF EXISTS idx_checkout_cart_items_product_id;
DROP INDEX IF EXISTS idx_checkout_cart_items_cart_id;

DROP INDEX IF EXISTS idx_checkout_cart_updated_at;
DROP INDEX IF EXISTS idx_checkout_cart_token_id;
DROP INDEX IF EXISTS idx_checkout_cart_user_id;

DROP INDEX IF EXISTS idx_checkout_cart_tokens_expires_at;
DROP INDEX IF EXISTS idx_checkout_cart_tokens_token;

-- Drop tables in correct order (foreign key dependencies)
DROP TABLE IF EXISTS checkout_cart_items;
DROP TABLE IF EXISTS checkout_cart;
DROP TABLE IF EXISTS checkout_cart_tokens;
