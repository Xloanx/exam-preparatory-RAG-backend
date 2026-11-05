from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    parent_id = Column(Integer, nullable=True)
    description = Column(String, nullable=True)

    children = relationship("Category", remote_side=[id], back_populates="parent")
    parent = relationship("Category", back_populates="children")
    users = relationship("User", back_populates="category")
