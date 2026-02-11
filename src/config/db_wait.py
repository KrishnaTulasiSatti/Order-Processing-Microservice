import time
from sqlalchemy import create_engine
from config.settings import DATABASE_URL

def wait_for_db(retries=10, delay=5):
    engine = create_engine(DATABASE_URL)
    for attempt in range(1, retries + 1):
        try:
            print(f"🔌 Checking Database connection (attempt {attempt}/{retries})...", flush=True)
            with engine.connect() as connection:
                print("✅ Database is ready!", flush=True)
                return True
        except Exception as e:
            print(f"❌ Database not ready: {e}. Retrying in {delay} seconds...", flush=True)
            time.sleep(delay)
    
    raise Exception("❌ Could not connect to Database after multiple retries")
