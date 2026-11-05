from sqlalchemy import Column, ForeignKey, Integer, String, Text

from app.models.base import Base


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    source_doc = Column(String, nullable=False)
    section = Column(String, nullable=True)
    page = Column(Integer, nullable=True)
