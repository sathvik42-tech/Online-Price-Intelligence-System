import psycopg2
from psycopg2 import OperationalError
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_connection():
    """
    Creates and returns a connection to the PostgreSQL database using environment variables.
    """
    connection = None
    try:
        connection = psycopg2.connect(
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        print("Successfully connected to the PostgreSQL database.")
    except OperationalError as e:
        print(f"Error connecting to the PostgreSQL database: {e}")
    
    return connection

if __name__ == "__main__":
    # Test the connection
    conn = get_connection()
    if conn:
        try:
            # Perform a simple query to confirm connection
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()
            print(f"PostgreSQL version: {db_version}")
            cursor.close()
        except Exception as e:
            print(f"Error executing test query: {e}")
        finally:
            conn.close()
            print("Database connection closed.")
    else:
        print("Failed to establish a connection. Please check your .env settings.")
