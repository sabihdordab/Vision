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
    Puzzle(
    category="اشیاء",
    prompt=" انگاری توی یه زندونه، روی دیوار. دائم می‌دوه، اما یه سانت هم جلو نمی‌ره.",
    answer="ساعت دیواری",
    language="fa"
),
    Puzzle(
    category="objects",
    prompt="It’s trapped on the wall—always running, never moving forward.",
    answer="wall clock",
    language="en"
),
    Puzzle(
    category="اشیاء",
    prompt="اون چیزی رو نشون می‌ده که گاهی خودت ازش فرار می‌کنی.\n نه می‌ترسه، نه قضاوت می‌کنه. \n اگه بشکنه، هنوز هم حقیقت از پشت ترک‌ها نگاهت می‌کنه.",
    answer="آینه",
    language="fa"
),
    Puzzle(
    category="objects",
    prompt="It reflects the version of you you’re too afraid to face.\n It doesn’t flinch. It doesn’t lie.\n Even shattered, it watches you through the cracks.",
    answer="mirror",
    language="en"
),
    Puzzle(
    category="میوه",
    prompt="وقتی از شاخه افتاد،\n نه فقط جاذبه، بلکه گناه رو هم به دنیا آورد.\n حالا هم توی دست‌های خیلی از آدما روشنه.",
    answer="سیب",
    language="fa"
),
    Puzzle(
    category="fruit",
    prompt="When it fell from the branch,\n it brought not just gravity—but sin.\n Now, it glows in the hands of many.",
    answer="apple",
    language="en"
),
    Puzzle(
    category="اشیاء",
    prompt="مثل در مخفی به یه دنیا دیگه‌ست.\n ساکته، ولی پر از فریاده.\n هر بار که بازش می‌کنی، یه جهان دیگه بیدار می‌شه.",
    answer="کتاب",
    language="fa"
),
    Puzzle(
    category="objects",
    prompt="It’s a hidden door to a world unknown.\n Silent, yet full of screams.\n Every time you open it, a new universe awakens.",
    answer="book",
    language="en"
),
Puzzle(
    category="مفهومی",
    prompt="گاهی از صد تا فریاد قوی‌تره. توی خشم، درد، یا عشق.\n نه صدا داره، نه شکل؛\n ولی همه حسش می‌کنن.",
    answer="سکوت",
    language="fa"
),
    Puzzle(
    category="conceptual",
    prompt="Sometimes louder than screams.\n It shows up in rage, pain, or love.\n No sound, no form—yet everyone feels it.",
    answer="silence",
    language="en"
),
    Puzzle(
    category="اشیاء",
    prompt="همه فکر می‌کنن صورت واقعیشه،\n ولی خودش حتی چهره‌ی خودش رو یادش رفته.\n پشت اون لبخند، شاید فقط تهی باشه.",
    answer="نقاب",
    language="fa"
),
    Puzzle(
    category="objects",
    prompt="Everyone thinks it's the real face,\n but even it forgot what’s underneath.\n Behind that smile… maybe just emptiness.",
    answer="mask",
    language="en"
),
    Puzzle(
    category="مفهومی",
    prompt="بی‌صدا شکل می‌گیره،\n بی‌وزن می‌چرخه،\n و گاهی همه‌چی رو تغییر می‌ده.\n کسی نمی‌بینتش، اما همه‌ی دنیا ازش ساخته شده.",
    answer="فکر",
    language="fa"
),
    Puzzle(
    category="conceptual",
    prompt="It forms in silence,\n floats weightless,\n and sometimes changes everything.\n No one sees it, yet the world is built on it.",
    answer="thought",
    language="en"
),
Puzzle(
    category="اشیاء",
    prompt="اون پرسید: «تو ازم یه عکس گرفتی… ولی چرا فقط خودت توی عکس افتادی؟»",
    answer="آینه",
    language="fa"
),
Puzzle(
    category="objects",
    prompt="She asked:\n “You took a picture of me… then why is it only you in the frame?”",
    answer="mirror",
    language="en"
),
Puzzle(
    category="مفهومی",
    prompt="شیر گفت:\n «اگه دلت برام تنگ شد… بندازش بالا. شاید این‌بار برگردم.»",
    answer="سکه",
    language="fa"
),

]

for puzzle in puzzles:
    try:
        session.add(puzzle)
        session.commit()
    except IntegrityError:
        session.rollback()

print("puzzles added!")
