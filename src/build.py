"""בונה את index.html מהתבנית + בנקי השאלות.

הרצה:  python build.py      (מתוך התיקייה הזו)
כותב גם ל-fm-quiz/index.html וגם לעותק הנוח בתיקיית הקורס.
"""
import os, sys, re, glob
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE   = os.path.dirname(os.path.abspath(__file__))
REPO   = os.path.dirname(HERE)                     # .../fm-quiz
COURSE = os.path.dirname(REPO)                     # תיקיית הקורס

TARGETS = [
    os.path.join(REPO, "index.html"),
    os.path.join(COURSE, "בוחן תרגול - ניהול תשתיות גלובליות.html"),
]

tpl  = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
bank = "\n".join(open(f, encoding="utf-8").read()
                 for f in sorted(glob.glob(os.path.join(HERE, "bank*.js"))))
html = tpl.replace("/*__BANK__*/", bank)

for t in TARGETS:
    open(t, "w", encoding="utf-8").write(html)
    print("נכתב:", t)
print("גודל: %.0f KB" % (len(html) / 1024))

# ---------- בדיקות שפיות ----------
objs = re.findall(r'\{t:"(.*?)",s:"(.*?)",q:', bank)
print("\nשאלות:", len(objs))

topics, srcs = {}, {}
for t, s in objs:
    topics[t] = topics.get(t, 0) + 1
    srcs[s]   = srcs.get(s, 0) + 1
print("\nלפי נושא:")
for k, v in sorted(topics.items(), key=lambda x: -x[1]):
    print("  %-26s %3d" % (k, v))
print("לפי מקור:")
for k, v in sorted(srcs.items(), key=lambda x: -x[1]):
    print("  %-16s %3d" % (k, v))

# פיזור התשובה הנכונה בקוד המקור (האפליקציה ממילא מערבבת אותן בכל סבב)
cs = re.findall(r',c:(\d),e:"', bank)
dist = {}
for c in cs:
    dist[c] = dist.get(c, 0) + 1
print("\nפיזור אינדקס התשובה הנכונה במקור:", dict(sorted(dist.items())))
if len(cs) != len(objs):
    print("!! אזהרה: לא כל השאלות נותחו (%d מתוך %d)" % (len(cs), len(objs)))
