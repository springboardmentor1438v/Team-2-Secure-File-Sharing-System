from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from app.database.database import Base


class Share(Base):
    __tablename__ = "shares"

    id = Column(Integer, primary_key=True, index=True)

    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    shared_with = Column(Integer, ForeignKey("users.id"), nullable=False)

    permission = Column(String(20), nullable=False)

    expiry_date = Column(DateTime)

    download_limit = Column(Integer, default=0)

    download_count = Column(Integer, default=0)

    is_revoked = Column(Boolean, default=False)