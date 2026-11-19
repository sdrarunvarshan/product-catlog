-- PostgreSQL initialization script
-- Creates separate databases for each microservice

-- Create databases
CREATE DATABASE ecommerce_auth;
CREATE DATABASE ecommerce_products;
CREATE DATABASE ecommerce_orders;
CREATE DATABASE ecommerce_payments;

-- Grant permissions (adjust username/password as needed)
-- GRANT ALL PRIVILEGES ON DATABASE ecommerce_auth TO user;
-- GRANT ALL PRIVILEGES ON DATABASE ecommerce_products TO user;
-- GRANT ALL PRIVILEGES ON DATABASE ecommerce_orders TO user;
-- GRANT ALL PRIVILEGES ON DATABASE ecommerce_payments TO user;
