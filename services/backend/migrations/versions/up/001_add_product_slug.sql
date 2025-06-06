-- Migration: 001_add_product_slug
-- Description: Add slug column to catalog_products table for SEO-friendly URLs
-- Created: 2025-06-06

-- Add slug column
ALTER TABLE catalog_products
ADD COLUMN IF NOT EXISTS slug VARCHAR(255);

-- Create function for slug generation
CREATE OR REPLACE FUNCTION create_slug(input_text TEXT, product_id INTEGER)
RETURNS TEXT AS $$
BEGIN
    RETURN product_id || '-' ||
           TRIM(BOTH '-' FROM
               REGEXP_REPLACE(
                   REGEXP_REPLACE(
                       LOWER(input_text),
                       '[^a-z0-9\s]+', '', 'g'
                   ),
                   '\s+', '-', 'g'
               )
           );
END;
$$ LANGUAGE plpgsql;

-- Fill slug for all existing records
UPDATE catalog_products
SET slug = create_slug(product_display_name, product_id);

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_catalog_products_slug ON catalog_products(slug);

-- Add unique constraint
ALTER TABLE catalog_products
ADD CONSTRAINT unique_product_slug UNIQUE (slug);
