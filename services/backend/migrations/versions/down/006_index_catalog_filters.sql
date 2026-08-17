-- Restore the indexes 006 dropped and remove the ones it added.

DROP INDEX IF EXISTS idx_products_gender_year;
DROP INDEX IF EXISTS idx_inventory_effective_price;

CREATE INDEX idx_products_master_category_complete
ON catalog_products (article_type_id, year, gender, product_id, product_display_name, image_url, slug)
WHERE year BETWEEN 2010 AND 2030;

CREATE INDEX idx_inventory_selective_filter
ON catalog_product_inventory (product_id)
WHERE is_active = true
  AND is_in_stock = true
  AND COALESCE(sale_price, base_price) BETWEEN 1.0 AND 5000.0;
