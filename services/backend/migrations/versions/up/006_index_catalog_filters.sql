-- Support the filters the catalogue actually receives, and drop indexes no query can use.

-- Gender and year are filtered without a category, which the existing index cannot
-- serve because it leads with article_type_id. Trailing product_id also serves the
-- default ordering.
CREATE INDEX IF NOT EXISTS idx_products_gender_year
ON catalog_products (gender, year, product_id);

-- Both the price filter and the price ordering key on this expression, so it needs
-- to be indexed as an expression rather than as a column.
CREATE INDEX IF NOT EXISTS idx_inventory_effective_price
ON catalog_product_inventory ((COALESCE(sale_price, base_price)));

-- A partial index is only usable when the planner can prove the query implies its
-- predicate. Neither predicate below is ever implied: the listing never mentions a
-- year window, and the price bounds arrive as parameters. Both indexes cost write
-- amplification on every insert and can serve nothing.
DROP INDEX IF EXISTS idx_products_master_category_complete;
DROP INDEX IF EXISTS idx_inventory_selective_filter;
