import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv
from typing import Generator

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432")
}

# Global variable for the connection pool
db_pool = None

def initialize_db_pool():
    global db_pool
    try:
        db_pool = pool.SimpleConnectionPool(
            minconn=1, 
            maxconn=10, 
            **DB_CONFIG
        )
        print("Database connection pool initialized successfully.")
    except Exception as e:
        print(f"Error initializing database connection pool: {e}")
        raise

def close_db_pool():
    global db_pool
    if db_pool:
        db_pool.closeall()
        print("Database connection pool closed.")

def get_db() -> Generator[psycopg2.extensions.connection, None, None]:
    conn = None
    try:
        if not db_pool:
            raise Exception("Database pool not initialized.")
        conn = db_pool.getconn()
        yield conn
    finally:
        if conn:
            db_pool.putconn(conn)
