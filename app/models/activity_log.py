from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database.database import Base


class ActivityLog(Base):

    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    action = Column(
        String(100),
        nullable=False
    )

    resource_type = Column(
        String(100),
        nullable=True
    )

    resource_id = Column(
        Integer,
        nullable=True
    )

    description = Column(
        String(500),
        nullable=True
    )

    status = Column(
        String(20),
        nullable=False
    )

    ip_address = Column(
        String(100),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )