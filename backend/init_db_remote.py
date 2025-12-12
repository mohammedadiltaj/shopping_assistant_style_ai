import os
import sys
from sqlalchemy import create_engine, text
from models import Base
from dotenv import load_dotenv

# Load env vars
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not found in environment")
    sys.exit(1)

print(f"Connecting to: {DATABASE_URL.split('@')[1]}") # Print host only for privacy

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # 1. Enable vector extension if not exists (try to do it, if prompt fails user might have done it)
        print("Checking/Enabling vector extension...")
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            print("Vector extension enabled.")
        except Exception as e:
            print(f"Warning: Could not create extension (might need superuser): {e}")
            print("Assuming user ran it manually as requested.")

        # 2. Create Schema
        print("Creating 'retail' schema...")
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS retail"))
        conn.commit()

        # 3. Create Tables
        print(f"Registered models: {Base.metadata.tables.keys()}")
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
        
        # 4. Verify
        print("Verifying connection...")
        # Check information_schema
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'retail'"))
        tables = [row[0] for row in result]
        print(f"Tables in retail schema: {tables}")

        result = conn.execute(text("SELECT count(*) FROM retail.product")) # Note: table name is singular 'product' in models.py
        count = result.scalar()
        print(f"Connection verified! Found {count} products.")

except Exception as e:
    print(f"Database initialization failed: {e}")
    sys.exit(1)
