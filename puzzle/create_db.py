from sqlalchemy import create_engine
from models import Base
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR,"puzzles.db")
engine = create_engine(f"sqlite:///{db_path}")
Base.metadata.create_all(engine)

print("Database created!")
