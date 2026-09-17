import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

from app.models.user import Base
from app.models.file import File
from app.models.file_share import FileShare
from app.models.activity_log import ActivityLog

# Only create tables & sync schema when NOT running tests (tests handle this via conftest.py)
if not os.getenv("PYTEST_RUNNING"):
    Base.metadata.create_all(bind=engine)
    
    # Auto-synchronize missing columns in existing MySQL tables
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        with engine.begin() as conn:
            # Sync 'files' table
            if "files" in existing_tables:
                file_cols = [c["name"] for c in inspector.get_columns("files")]
                if "encryption_key" not in file_cols:
                    conn.execute(text("ALTER TABLE files ADD COLUMN encryption_key VARCHAR(500) NULL"))
                if "uploaded_at" not in file_cols:
                    conn.execute(text("ALTER TABLE files ADD COLUMN uploaded_at DATETIME NULL"))

            # Sync 'file_shares' table
            if "file_shares" in existing_tables:
                share_cols = [c["name"] for c in inspector.get_columns("file_shares")]
                if "permission" not in share_cols:
                    conn.execute(text("ALTER TABLE file_shares ADD COLUMN permission VARCHAR(20) DEFAULT 'DOWNLOAD' NOT NULL"))
                if "expires_at" not in share_cols:
                    conn.execute(text("ALTER TABLE file_shares ADD COLUMN expires_at DATETIME NULL"))
                if "download_limit" not in share_cols:
                    conn.execute(text("ALTER TABLE file_shares ADD COLUMN download_limit INT NULL"))
                if "download_count" not in share_cols:
                    conn.execute(text("ALTER TABLE file_shares ADD COLUMN download_count INT DEFAULT 0 NOT NULL"))
                if "is_revoked" not in share_cols:
                    conn.execute(text("ALTER TABLE file_shares ADD COLUMN is_revoked BOOLEAN DEFAULT FALSE NOT NULL"))
                if "shared_at" not in share_cols:
                    conn.execute(text("ALTER TABLE file_shares ADD COLUMN shared_at DATETIME NULL"))

            # Sync 'users' table
            if "users" in existing_tables:
                user_cols = [c["name"] for c in inspector.get_columns("users")]
                if "role" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'"))
                if "is_active" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
    except Exception as sync_err:
        print(f"Notice: Schema sync check completed with note: {sync_err}")



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()