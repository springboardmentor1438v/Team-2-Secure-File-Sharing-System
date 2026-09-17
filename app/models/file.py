from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String(255), nullable=False)

    original_filename = Column(String(255), nullable=False)

    version = Column(Integer, default=1)

    filepath = Column(String(500), nullable=False)

    folder_id = Column(
        Integer,
        ForeignKey("folders.id"),
        nullable=True
    )

    folder = relationship("Folder")

    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    owner = relationship("User")