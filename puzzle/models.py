from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Puzzle(Base):
    __tablename__ = 'puzzles'

    id = Column(Integer, primary_key=True)
    category = Column(String)
    prompt = Column(String)
    answer = Column(String)
    language = Column(String)

    __table_args__ = (
        UniqueConstraint('prompt', name='uix_prompt'),
    )
