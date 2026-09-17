from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

# Load environment variables from .env file
load_dotenv()

# Read values from .env
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Encode special characters in password (like @, #, %, etc.)
DB_PASSWORD = quote_plus(DB_PASSWORD)

# Create database connection URL
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Create SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# Create Session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all database models
Base = declarative_base()

# Test Database Connection
try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("✅ Connected to MySQL successfully!")
except Exception as e:
    print("❌ Database Connection Failed!")
    print(e)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()