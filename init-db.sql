-- Initialize databases for SPORT_BETTING_MODULE
-- This script creates separate databases for each microservice

-- Create databases for each service
CREATE DATABASE betting_db;
CREATE DATABASE carousel_db;
CREATE DATABASE individual_bookmaker_db;
CREATE DATABASE risk_management_db;
CREATE DATABASE saga_db;
CREATE DATABASE sports_data_db;

-- Create users for each service (optional, for better security)
-- CREATE USER betting_user WITH PASSWORD 'betting_password';
-- CREATE USER carousel_user WITH PASSWORD 'carousel_password';
-- CREATE USER individual_bookmaker_user WITH PASSWORD 'individual_bookmaker_password';
-- CREATE USER risk_management_user WITH PASSWORD 'risk_management_password';
-- CREATE USER saga_user WITH PASSWORD 'saga_password';
-- CREATE USER sports_data_user WITH PASSWORD 'sports_data_password';

-- Grant privileges to users
-- GRANT ALL PRIVILEGES ON DATABASE betting_db TO betting_user;
-- GRANT ALL PRIVILEGES ON DATABASE carousel_db TO carousel_user;
-- GRANT ALL PRIVILEGES ON DATABASE individual_bookmaker_db TO individual_bookmaker_user;
-- GRANT ALL PRIVILEGES ON DATABASE risk_management_db TO risk_management_user;
-- GRANT ALL PRIVILEGES ON DATABASE saga_db TO saga_user;
-- GRANT ALL PRIVILEGES ON DATABASE sports_data_db TO sports_data_user;

-- Create extensions for each database
\c betting_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c carousel_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c individual_bookmaker_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c risk_management_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c saga_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c sports_data_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Switch back to main database
\c sport_betting_db;
