# -*- coding: utf-8 -*-
"""בונה את חוברת החומר הפתוח: מזריק content.js לתוך template.html.

הדפדוף, מספור העמודים, השער והמפתח נבנים בזמן טעינה בדפדפן — כך
מספרי העמודים במפתח תמיד נכונים גם אחרי עריכת תוכן, בלי לתחזק אותם ביד.

הרצה:  python build.py
"""
import io, os, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)                      # נשלח גם לאתר
OUT  = [os.path.join(REPO, "exam.html"),
        os.path.join(REPO, "..", "מדריך מבחן - ניהול תשתיות גלובליות.html")]

tpl = io.open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
dat = io.open(os.path.join(HERE, "content.js"),   encoding="utf-8").read()

html = re.sub(r"/\*DATA\*/.*?/\*DATA\*/", lambda m: dat.strip(), tpl, flags=re.S)


def for_course_folder(page):
    """העותק בתיקיית הקורס נמצא רמה אחת מעל fm-quiz, ולכן הקישורים היחסיים
    לבוחן ולפודקאסט צריכים קידומת. בלי זה הם שבורים."""
    for href in ('"index.html"', '"podcast/"'):
        page = page.replace("href=" + href, 'href="fm-quiz/' + href[1:])
    return page


for i, p in enumerate(OUT):
    page = html if i == 0 else for_course_folder(html)
    io.open(os.path.abspath(p), "w", encoding="utf-8").write(page)

# ספירה גסה של פריטים, כדי לראות שהתוכן אכן גדל
items = dat.count(" :: ") + dat.count("],[") + dat.count("], [")
print("נבנה. %d תווים, ~%d פריטי תוכן." % (len(html), items))
for p in OUT:
    print("  ", os.path.abspath(p))


# מספר העמודים נקבע רק בדפדפן, בזמן טעינה, ולכן הבנייה אינה יכולה לחשב
# אותו. מה שהיא כן יכולה: להראות מי מצהיר עליו בטקסט קבוע. פעם אחת כבר
# קרה שהחוברת גדלה ל-38 והקישורים באתר המשיכו להבטיח 36.
CLAIMS = [
    ("src/template.html",  r"(\d+) עמודי A4"),
    ("README.md",          r"(\d+) עמודי A4"),
    ("podcast/build.py",   r"(\d+) עמודים להדפסה"),
    ("podcast/index.html", r"(\d+) עמודים להדפסה"),
]
found = {}
for rel, pat in CLAIMS:
    path = os.path.join(REPO, rel)
    if not os.path.exists(path):
        continue
    for m in re.finditer(pat, io.open(path, encoding="utf-8").read()):
        found.setdefault(m.group(1), []).append(rel)

if found:
    print("\nמספר העמודים המוצהר בטקסט קבוע:")
    for n, files in sorted(found.items()):
        print("   %s עמודים — %s" % (n, ", ".join(sorted(set(files)))))
    if len(found) > 1:
        print("   !! הצהרות סותרות. יש ליישר את כולן.")
    print("   השוו למחוון שבפינת הדף הבנוי (\"NN עמודים · תקין\");")
    print("   אם השתנה — עדכנו את הקבצים שלמעלה והריצו מחדש גם את podcast/build.py.")
