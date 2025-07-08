from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from models import Puzzle
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR,"puzzles.db")
engine = create_engine(f"sqlite:///{db_path}")
Session = sessionmaker(bind=engine)
session = Session()

puzzles = [
    Puzzle(category="میوه", prompt="میوه‌ای که سقوطش قوانین دنیا را آشکار کرد، طعمش بهشت را از آدم گرفت، و نامش در دست همه جاودانه شد.", answer="سیب", language="fa"),
    Puzzle(category="fruit", prompt="The fruit whose fall revealed the laws of the world, its taste took paradise from Adam, and its name became eternal in everyone's hands.", answer="apple", language="en"),
    Puzzle(category="اشیاء", prompt="تو را نشان می‌دهد، اما خودش هیچ‌وقت تغییر نمی‌کند. اگر شکسته شود، باز هم حقیقت را پنهان نمی‌کند.", answer="آینه", language="fa"),
    Puzzle(category="objects", prompt="It shows you but never changes itself. If it breaks, it still doesn't hide the truth.", answer="mirror", language="en"),
    Puzzle(category="مفهومی", prompt="دست به دست می‌چرخد و همه به دنبال آن می‌دوند.", answer="پول", language="fa"),
    Puzzle(category="conceptual", prompt="It passes from hand to hand and everyone chases after it.", answer="money", language="en"),
    Puzzle(category="اشیاء", prompt="بی‌صدا سخن می‌گوید و هر بار که بازش کنی، سفری تازه آغاز می‌شود.", answer="کتاب", language="fa"),
    Puzzle(category="objects", prompt="It speaks without a sound, and every time you open it, a new journey begins.", answer="book", language="en"),
    Puzzle(category="اشیاء", prompt="با هر قدمش، ردپایی از دانایی به جا می‌گذارد، اما هرچه بیشتر می‌نویسد، کوتاه‌تر می‌شود.", answer="مداد", language="fa"),
    Puzzle(category="objects", prompt="With every step, it leaves a trace of knowledge, yet the more it writes, the shorter it becomes.", answer="pencil", language="en"),
    Puzzle(category="اشیاء", prompt="روی دیوار نشسته است، همیشه در حرکت است، اما هیچ‌وقت جایی نمی‌رود.", answer="ساعت دیواری", language="fa"),
    Puzzle(category="objects", prompt="It sits on the wall, always in motion, yet it never goes anywhere.", answer="wall clock", language="en"),
    Puzzle(category="اشیاء", prompt="چهار پا دارد، اما نمی‌دود. همیشه آماده است تا بار سنگین تو را تحمل کند.", answer="میز", language="fa"),
    Puzzle(category="objects", prompt="It has four legs but never runs. Always ready to carry your heavy load.", answer="table", language="en"),
    Puzzle(category="میوه", prompt="قهوه‌ای و کوچک است، از دل گرما می‌آید و انرژی را به تو هدیه می‌دهد.", answer="خرما", language="fa"),
    Puzzle(category="fruit", prompt="It’s small and brown, comes from the heart of the heat, and offers you energy.", answer="date", language="en"),
]

for puzzle in puzzles:
    try:
        session.add(puzzle)
        session.commit()
    except IntegrityError:
        session.rollback()

print("puzzles added!")
