from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Puzzle(Base):
    __tablename__ = 'puzzles'

    id = Column(Integer, primary_key=True)
    category = Column(String)
    prompt = Column(String)
    answer = Column(String)
