-- Migration: 003_create_product_inventory
-- Description: Add product inventory table for prices and stock management
-- Created: 2025-01-18

-- Create product inventory table
CREATE TABLE catalog_product_inventory (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES catalog_products(product_id) ON DELETE CASCADE,

    -- Pricing information
    base_price DECIMAL(10,2) NOT NULL,
    sale_price DECIMAL(10,2),
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',

    -- Stock management
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,
    available_quantity INTEGER GENERATED ALWAYS AS (stock_quantity - reserved_quantity) STORED,

    -- Product status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_in_stock BOOLEAN GENERATED ALWAYS AS (stock_quantity - reserved_quantity > 0) STORED,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    UNIQUE(product_id),
    CHECK (base_price >= 0),
    CHECK (sale_price IS NULL OR sale_price >= 0),
    CHECK (stock_quantity >= 0),
    CHECK (reserved_quantity >= 0),
    CHECK (reserved_quantity <= stock_quantity)
);

-- Create indexes for performance
CREATE INDEX idx_catalog_product_inventory_product_id ON catalog_product_inventory(product_id);
CREATE INDEX idx_catalog_product_inventory_is_active ON catalog_product_inventory(is_active);
CREATE INDEX idx_catalog_product_inventory_is_in_stock ON catalog_product_inventory(is_in_stock);
CREATE INDEX idx_catalog_product_inventory_base_price ON catalog_product_inventory(base_price);
CREATE INDEX idx_catalog_product_inventory_available_quantity ON catalog_product_inventory(available_quantity);

-- Create trigger for updated_at automatic update
CREATE OR REPLACE FUNCTION update_catalog_product_inventory_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_catalog_product_inventory_updated_at
    BEFORE UPDATE ON catalog_product_inventory
    FOR EACH ROW
    EXECUTE FUNCTION update_catalog_product_inventory_updated_at();
