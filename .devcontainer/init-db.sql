-- PostgreSQL initialization script for Agentex
-- This script runs when the PostgreSQL container is first created

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schema (optional, using public by default)
-- CREATE SCHEMA IF NOT EXISTS agentex;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE agentex TO agentex;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Agentex database initialized successfully';
END $$;
