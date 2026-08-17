-- Migration: 005_create_cart_tables
-- Description: Create checkout module tables (checkout_cart_tokens, checkout_cart, checkout_cart_items)
-- Created: 2025-01-27

-- Cart tokens table for anonymous users
CREATE TABLE checkout_cart_tokens (
    id SERIAL PRIMARY KEY,
    token VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '30 days'),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Main cart table
CREATE TABLE checkout_cart (
    id SERIAL PRIMARY KEY,

    -- Either authenticated user OR anonymous token (mutually exclusive)
    user_id INTEGER UNIQUE REFERENCES accounts_users(id) ON DELETE CASCADE,
    cart_token_id INTEGER UNIQUE REFERENCES checkout_cart_tokens(id) ON DELETE CASCADE,

    -- Cart metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints: exactly one of user_id or cart_token_id must be set
    CHECK (
        (user_id IS NOT NULL AND cart_token_id IS NULL) OR
        (user_id IS NULL AND cart_token_id IS NOT NULL)
    )
);

-- Cart items table
CREATE TABLE checkout_cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL REFERENCES checkout_cart(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES catalog_products(product_id) ON DELETE CASCADE,

    -- Item details
    quantity INTEGER NOT NULL DEFAULT 1,
    added_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    UNIQUE(cart_id, product_id),
    CHECK (quantity > 0)
);

-- Create indexes for performance
CREATE INDEX idx_checkout_cart_tokens_token ON checkout_cart_tokens(token);
CREATE INDEX idx_checkout_cart_tokens_expires_at ON checkout_cart_tokens(expires_at);

CREATE INDEX idx_checkout_cart_user_id ON checkout_cart(user_id);
CREATE INDEX idx_checkout_cart_token_id ON checkout_cart(cart_token_id);
CREATE INDEX idx_checkout_cart_updated_at ON checkout_cart(updated_at);

CREATE INDEX idx_checkout_cart_items_cart_id ON checkout_cart_items(cart_id);
CREATE INDEX idx_checkout_cart_items_product_id ON checkout_cart_items(product_id);
CREATE INDEX idx_checkout_cart_items_updated_at ON checkout_cart_items(updated_at);

-- Create triggers for updated_at automatic update
CREATE OR REPLACE FUNCTION update_checkout_cart_tokens_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_checkout_cart_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_checkout_cart_items_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers
CREATE TRIGGER trigger_checkout_cart_tokens_updated_at
    BEFORE UPDATE ON checkout_cart_tokens
    FOR EACH ROW
    EXECUTE FUNCTION update_checkout_cart_tokens_updated_at();

CREATE TRIGGER trigger_checkout_cart_updated_at
    BEFORE UPDATE ON checkout_cart
    FOR EACH ROW
    EXECUTE FUNCTION update_checkout_cart_updated_at();

CREATE TRIGGER trigger_checkout_cart_items_updated_at
    BEFORE UPDATE ON checkout_cart_items
    FOR EACH ROW
    EXECUTE FUNCTION update_checkout_cart_items_updated_at();

