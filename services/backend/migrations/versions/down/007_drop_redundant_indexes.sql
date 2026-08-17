-- Recreate the indexes 007 dropped.

CREATE INDEX IF NOT EXISTS idx_accounts_users_email ON accounts_users(email);
CREATE INDEX IF NOT EXISTS idx_accounts_user_profiles_user_id ON accounts_user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_accounts_activation_tokens_token ON accounts_activation_tokens(token);
CREATE INDEX IF NOT EXISTS idx_accounts_password_reset_tokens_token ON accounts_password_reset_tokens(token);
CREATE INDEX IF NOT EXISTS idx_accounts_refresh_tokens_token ON accounts_refresh_tokens(token);
CREATE INDEX IF NOT EXISTS idx_catalog_products_slug ON catalog_products(slug);
CREATE INDEX IF NOT EXISTS idx_checkout_cart_user_id ON checkout_cart(user_id);
CREATE INDEX IF NOT EXISTS idx_checkout_cart_token_id ON checkout_cart(cart_token_id);
