from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from models import Puzzle

engine = create_engine('sqlite:///puzzles.db')
Session = sessionmaker(bind=engine)
session = Session()

puzzles = [
    Puzzle(category="میوه", prompt="میوه‌ای که سقوطش قوانین دنیا را آشکار کرد، طعمش بهشت را از آدم گرفت، و نامش در دست همه جاودانه شد.", answer="سیب", language="fa"),
    Puzzle(category="fruit", prompt="The fruit whose fall revealed the laws of the world, its taste took paradise from Adam, and its name became eternal in everyone's hands.", answer="apple", language="en"),

]

for puzzle in puzzles:
    try:
        session.add(puzzle)
        session.commit()
    except IntegrityError:
        session.rollback()

print("puzzles added!")
