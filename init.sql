-- Enable extensions for trigram and unaccent support
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

-- Create text‐search configuration that strips accents and stems English
CREATE TEXT SEARCH CONFIGURATION public.english_unaccent ( COPY = pg_catalog.english );
ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
  ALTER MAPPING FOR hword, hword_part, word
  WITH unaccent, english_stem;

-- Master categories
CREATE TABLE catalog_master_category (
  master_category_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

-- Sub-categories → each belongs to one master_category
CREATE TABLE catalog_sub_category (
  sub_category_id SERIAL PRIMARY KEY,
  master_category_id INT NOT NULL
    REFERENCES catalog_master_category(master_category_id)
    ON DELETE RESTRICT,
  name TEXT NOT NULL,
  UNIQUE (master_category_id, name)
);

-- Article types → each belongs to one sub_category
CREATE TABLE catalog_article_type (
  article_type_id SERIAL PRIMARY KEY,
  sub_category_id INT NOT NULL
    REFERENCES catalog_sub_category(sub_category_id)
    ON DELETE RESTRICT,
  name TEXT NOT NULL,
  UNIQUE (sub_category_id, name)
);

-- Base colors
CREATE TABLE catalog_base_colour (
  base_colour_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

-- Seasons
CREATE TABLE catalog_season (
  season_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

-- Usage types
CREATE TABLE catalog_usage_type (
  usage_type_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

-- Products fact table
CREATE TABLE catalog_products (
  id                       SERIAL PRIMARY KEY,
  product_id               INT          NOT NULL UNIQUE,
  gender                   TEXT         NOT NULL,
  year                     SMALLINT,
  product_display_name     TEXT,
  image_url                TEXT,
  article_type_id          INT REFERENCES catalog_article_type(article_type_id),
  base_colour_id           INT REFERENCES catalog_base_colour(base_colour_id),
  season_id                INT REFERENCES catalog_season(season_id),
  usage_type_id            INT REFERENCES catalog_usage_type(usage_type_id)
);

-- Full-text search index on product_display_name
CREATE INDEX IF NOT EXISTS idx_catalog_products_display_tsv
  ON public.catalog_products
  USING GIN (
    to_tsvector('public.english_unaccent', product_display_name)
  );

-- Trigram index for fast ILIKE/LIKE '%…%' searches
CREATE INDEX IF NOT EXISTS idx_catalog_products_display_trgm
  ON public.catalog_products
  USING GIN (product_display_name gin_trgm_ops);

-- Grant privileges
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
