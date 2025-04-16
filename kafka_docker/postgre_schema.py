import psycopg2

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "logs_db"
DB_USER = "admin"
DB_PASSWORD = "password"

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# Create request_logs table (pastebin_api_logs)
cur.execute("""
    CREATE TABLE IF NOT EXISTS request_logs (
        id SERIAL PRIMARY KEY,
        timestamp BIGINT NOT NULL,
        endpoint VARCHAR(255) NOT NULL,
        method VARCHAR(10) NOT NULL,
        status_code INTEGER NOT NULL,
        response_time_ms INTEGER NOT NULL,
        error_message TEXT,
        username VARCHAR(255) NOT NULL
    )
""")

# Create auth_logs table
cur.execute("""
    CREATE TABLE IF NOT EXISTS auth_logs (
        id SERIAL PRIMARY KEY,
        event VARCHAR(50) NOT NULL,
        username VARCHAR(255) NOT NULL,
        timestamp BIGINT NOT NULL,
        result TEXT NOT NULL,
        endpoint VARCHAR(255) NOT NULL,
        method VARCHAR(10) NOT NULL,
        status_code INTEGER NOT NULL
    )
""")

# Create paste_logs table
cur.execute("""
    CREATE TABLE IF NOT EXISTS paste_logs (
        id SERIAL PRIMARY KEY,
        event VARCHAR(50) NOT NULL,
        username VARCHAR(255) NOT NULL,
        paste_id VARCHAR(36),
        timestamp BIGINT NOT NULL,
        endpoint VARCHAR(255) NOT NULL,
        method VARCHAR(10) NOT NULL,
        status_code INTEGER NOT NULL,
        content TEXT,
        result TEXT
    )
""")

# Create access_logs table
cur.execute("""
    CREATE TABLE IF NOT EXISTS access_logs (
        id SERIAL PRIMARY KEY,
        event VARCHAR(50) NOT NULL,
        username VARCHAR(255) NOT NULL,
        timestamp BIGINT NOT NULL,
        endpoint VARCHAR(255) NOT NULL,
        method VARCHAR(10) NOT NULL,
        status_code INTEGER NOT NULL,
        keyword TEXT,
        result_count INTEGER NOT NULL
    )
""")

conn.commit()
cur.close()
conn.close()

print("Database schema created successfully.")