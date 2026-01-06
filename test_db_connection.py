import psycopg2
import sys

try:
    conn = psycopg2.connect(
        host = os.environ.get("EXTERNAL_DB_HOST")
        database = os.environ.get("EXTERNAL_DB_NAME")
        user = os.environ.get("EXTERNAL_DB_USER")
        password = os.environ.get("EXTERNAL_DB_PASSWORD")
    )
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
    sys.exit(1)
