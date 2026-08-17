-- Drop indexes that duplicate a UNIQUE constraint.
--
-- A UNIQUE constraint creates its own index, so a second index on the same column
-- serves no read while doubling the write cost of the table.

DROP INDEX IF EXISTS idx_accounts_users_email;
DROP INDEX IF EXISTS idx_accounts_user_profiles_user_id;
DROP INDEX IF EXISTS idx_accounts_activation_tokens_token;
DROP INDEX IF EXISTS idx_accounts_password_reset_tokens_token;
DROP INDEX IF EXISTS idx_accounts_refresh_tokens_token;
DROP INDEX IF EXISTS idx_catalog_products_slug;
DROP INDEX IF EXISTS idx_checkout_cart_user_id;
DROP INDEX IF EXISTS idx_checkout_cart_token_id;
