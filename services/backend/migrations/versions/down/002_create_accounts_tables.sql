-- Migration: 002_create_accounts_tables
-- Description: Rollback all accounts module tables (users, profiles, tokens)
-- Created: 2025-06-09

-- Drop trigger and function
DROP TRIGGER IF EXISTS trigger_accounts_users_updated_at ON accounts_users;
DROP FUNCTION IF EXISTS update_accounts_users_updated_at();

-- Drop indexes
DROP INDEX IF EXISTS idx_accounts_users_email;
DROP INDEX IF EXISTS idx_accounts_users_group_id;
DROP INDEX IF EXISTS idx_accounts_users_is_active;
DROP INDEX IF EXISTS idx_accounts_users_created_at;

DROP INDEX IF EXISTS idx_accounts_user_profiles_user_id;
DROP INDEX IF EXISTS idx_accounts_user_profiles_gender;

DROP INDEX IF EXISTS idx_accounts_activation_tokens_token;
DROP INDEX IF EXISTS idx_accounts_activation_tokens_user_id;
DROP INDEX IF EXISTS idx_accounts_activation_tokens_expires_at;

DROP INDEX IF EXISTS idx_accounts_password_reset_tokens_token;
DROP INDEX IF EXISTS idx_accounts_password_reset_tokens_user_id;
DROP INDEX IF EXISTS idx_accounts_password_reset_tokens_expires_at;

DROP INDEX IF EXISTS idx_accounts_refresh_tokens_token;
DROP INDEX IF EXISTS idx_accounts_refresh_tokens_user_id;
DROP INDEX IF EXISTS idx_accounts_refresh_tokens_expires_at;

-- Drop tables in correct order (foreign key dependencies)
DROP TABLE IF EXISTS accounts_refresh_tokens;
DROP TABLE IF EXISTS accounts_password_reset_tokens;
DROP TABLE IF EXISTS accounts_activation_tokens;
DROP TABLE IF EXISTS accounts_user_profiles;
DROP TABLE IF EXISTS accounts_users;
DROP TABLE IF EXISTS accounts_user_groups;

-- Drop ENUM types
DROP TYPE IF EXISTS accounts_gender_enum;
DROP TYPE IF EXISTS accounts_user_group_enum;
