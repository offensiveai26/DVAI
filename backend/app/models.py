from sqlalchemy import Column, String, Integer, Boolean, DateTime, func

from app.db import Base


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    challenge_id = Column(String, nullable=False, unique=True)
    completed = Column(Boolean, default=False)
    flag = Column(String, nullable=True)
    completed_at = Column(DateTime, nullable=True, default=None)
    attempts = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
