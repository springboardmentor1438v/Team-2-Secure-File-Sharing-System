from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Folder(Base):

    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)

    folder_name = Column(String(255), nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User")