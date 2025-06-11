-- Migration: 002_create_accounts_tables
-- Description: Create all accounts module tables (users, profiles, tokens)
-- Created: 2025-06-09

-- Create ENUM types for user groups and gender
CREATE TYPE accounts_user_group_enum AS ENUM ('user', 'moderator', 'admin');
CREATE TYPE accounts_gender_enum AS ENUM ('man', 'woman');

-- User groups table
CREATE TABLE accounts_user_groups (
    id SERIAL PRIMARY KEY,
    name accounts_user_group_enum NOT NULL UNIQUE
);

-- Users table
CREATE TABLE accounts_users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    group_id INTEGER NOT NULL REFERENCES accounts_user_groups(id) ON DELETE CASCADE
);

-- User profiles table
CREATE TABLE accounts_user_profiles (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar VARCHAR(255),
    gender accounts_gender_enum,
    date_of_birth DATE,
    info TEXT,
    user_id INTEGER NOT NULL UNIQUE REFERENCES accounts_users(id) ON DELETE CASCADE
);

-- Activation tokens table
CREATE TABLE accounts_activation_tokens (
    id SERIAL PRIMARY KEY,
    token VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '1 day'),
    user_id INTEGER NOT NULL UNIQUE REFERENCES accounts_users(id) ON DELETE CASCADE
);

-- Password reset tokens table
CREATE TABLE accounts_password_reset_tokens (
    id SERIAL PRIMARY KEY,
    token VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '1 day'),
    user_id INTEGER NOT NULL UNIQUE REFERENCES accounts_users(id) ON DELETE CASCADE
);

-- Refresh tokens table
CREATE TABLE accounts_refresh_tokens (
    id SERIAL PRIMARY KEY,
    token VARCHAR(512) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '1 day'),
    user_id INTEGER NOT NULL REFERENCES accounts_users(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX idx_accounts_users_email ON accounts_users(email);
CREATE INDEX idx_accounts_users_group_id ON accounts_users(group_id);
CREATE INDEX idx_accounts_users_is_active ON accounts_users(is_active);
CREATE INDEX idx_accounts_users_created_at ON accounts_users(created_at);

CREATE INDEX idx_accounts_user_profiles_user_id ON accounts_user_profiles(user_id);
CREATE INDEX idx_accounts_user_profiles_gender ON accounts_user_profiles(gender);

CREATE INDEX idx_accounts_activation_tokens_token ON accounts_activation_tokens(token);
CREATE INDEX idx_accounts_activation_tokens_user_id ON accounts_activation_tokens(user_id);
CREATE INDEX idx_accounts_activation_tokens_expires_at ON accounts_activation_tokens(expires_at);

CREATE INDEX idx_accounts_password_reset_tokens_token ON accounts_password_reset_tokens(token);
CREATE INDEX idx_accounts_password_reset_tokens_user_id ON accounts_password_reset_tokens(user_id);
CREATE INDEX idx_accounts_password_reset_tokens_expires_at ON accounts_password_reset_tokens(expires_at);

CREATE INDEX idx_accounts_refresh_tokens_token ON accounts_refresh_tokens(token);
CREATE INDEX idx_accounts_refresh_tokens_user_id ON accounts_refresh_tokens(user_id);
CREATE INDEX idx_accounts_refresh_tokens_expires_at ON accounts_refresh_tokens(expires_at);

-- Create trigger for updated_at automatic update
CREATE OR REPLACE FUNCTION update_accounts_users_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_accounts_users_updated_at
    BEFORE UPDATE ON accounts_users
    FOR EACH ROW
    EXECUTE FUNCTION update_accounts_users_updated_at();

-- Insert default user groups
INSERT INTO accounts_user_groups (name) VALUES
    ('user'),
    ('moderator'),
    ('admin');

-- Grant privileges
GRANT ALL PRIVILEGES ON TABLE accounts_user_groups TO admin;
GRANT ALL PRIVILEGES ON TABLE accounts_users TO admin;
GRANT ALL PRIVILEGES ON TABLE accounts_user_profiles TO admin;
GRANT ALL PRIVILEGES ON TABLE accounts_activation_tokens TO admin;
GRANT ALL PRIVILEGES ON TABLE accounts_password_reset_tokens TO admin;
GRANT ALL PRIVILEGES ON TABLE accounts_refresh_tokens TO admin;

GRANT ALL PRIVILEGES ON SEQUENCE accounts_user_groups_id_seq TO admin;
GRANT ALL PRIVILEGES ON SEQUENCE accounts_users_id_seq TO admin;
GRANT ALL PRIVILEGES ON SEQUENCE accounts_user_profiles_id_seq TO admin;
GRANT ALL PRIVILEGES ON SEQUENCE accounts_activation_tokens_id_seq TO admin;
GRANT ALL PRIVILEGES ON SEQUENCE accounts_password_reset_tokens_id_seq TO admin;
GRANT ALL PRIVILEGES ON SEQUENCE accounts_refresh_tokens_id_seq TO admin;
