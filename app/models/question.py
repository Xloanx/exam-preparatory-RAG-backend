from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.models.base import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, default="GENERATED")
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    chunk_id = Column(Integer, ForeignKey("chunks.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    stem = Column(String, nullable=False)
    options = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
