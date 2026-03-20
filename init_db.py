import psycopg2
import os

print("🗄️ Initializing Unicorn Database...")

# Connect to our internal PostgreSQL container
db_host = os.environ.get("DB_HOST", "localhost")
conn = psycopg2.connect(
    dbname="unicorn_engine",
    user="unicorn_admin",
    password="unicorn_secret",
    host=db_host,
    port="5432"
)
conn.autocommit = True
cursor = conn.cursor()

# 1. The Paywall: Users Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    subscription_status VARCHAR(50) DEFAULT 'TRIAL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 2. The Vault: Encrypted Broker Keys
cursor.execute("""
CREATE TABLE IF NOT EXISTS broker_keys (
    key_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    broker_name VARCHAR(100) NOT NULL,
    client_id VARCHAR(255) NOT NULL,
    encrypted_token TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 3. The Fleet: Track Active Strategies
cursor.execute("""
CREATE TABLE IF NOT EXISTS deployments (
    deployment_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    strategy_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'STOPPED',
    container_id VARCHAR(255),
    deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

print("✅ Database Schema Created Successfully. The Vault is ready.")
cursor.close()
conn.close()
