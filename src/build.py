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

# ---------- בדיקת "תל האורך" ----------
# כשכותבים שאלות בכמות, התשובה הנכונה יוצאת כמעט תמיד הארוכה ביותר,
# ואז אפשר לענות נכון בלי לקרוא. זו בדיקה שהבעיה לא חזרה.
import json, subprocess, tempfile
CHECK = r"""
const fs=require('fs');
eval(fs.readFileSync(process.argv[2],'utf8'));
const n=BANK.length, rank=[0,0,0,0];
let long=0, short=0;
BANK.forEach(q=>{
  const L=q.o.map(o=>o.length), max=Math.max(...L), min=Math.min(...L);
  if(L.indexOf(max)===q.c) long++;
  if(L.indexOf(min)===q.c) short++;
  rank[L.map((l,i)=>[l,i]).sort((a,b)=>b[0]-a[0]).map(x=>x[1]).indexOf(q.c)]++;
});
console.log(JSON.stringify({n,long,short,rank}));
"""
def length_stats(js_text, td, tag):
    """מריץ את בדיקת האורך על קטע קוד נתון ומחזיר סטטיסטיקה."""
    jsf = os.path.join(td, "b_%s.js" % tag)
    # קובץ ראשון מגדיר את BANK בעצמו; השאר מוסיפים אליו
    prefix = "" if js_text.lstrip().startswith("var BANK") else "var BANK=[];\n"
    open(jsf, "w", encoding="utf-8").write(prefix + js_text)
    chk = os.path.join(td, "check.js")
    if not os.path.exists(chk):
        open(chk, "w", encoding="utf-8").write(CHECK)
    r = subprocess.run(["node", chk, jsf], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError((r.stderr or "")[:200])
    return json.loads(r.stdout.strip())

def report(s, label, indent="  "):
    """מדווח על שתי האסטרטגיות שנבחן אם ניתן להפעיל אותן בלי לקרוא:
       'בחר את הארוכה ביותר' ו'בחר את הקצרה ביותר'. אלו היחידות שאדם
       באמת מסוגל להפעיל בעין; פיזור הדירוג המלא מוצג כמידע בלבד
       (למשל 'שלישית באורכה' אינו תל שניתן לנצל בפועל)."""
    n = s["n"]
    if not n:
        return False
    pct = lambda x: int(round(x / n * 100))
    flag = "  <-- !!" if max(pct(s["long"]), pct(s["short"])) > 45 else ""
    print("%s%-14s n=%-4d ארוכה=%3d%%  קצרה=%3d%%  (פיזור %s)%s"
          % (indent, label, n, pct(s["long"]), pct(s["short"]),
             "/".join("%d" % pct(x) for x in s["rank"]), flag))
    return bool(flag)

try:
    with tempfile.TemporaryDirectory() as td:
        print("\nבדיקת אורך התשובות (כדי שלא ניתן יהיה לענות בלי לקרוא) — [מקרי ≈ 25%, אחיד = 25/25/25/25]:")
        bad_files = []
        # כל קובץ בנפרד — כך רואים מיד אם מנה חדשה של שאלות חורגת,
        # גם כשהממוצע הכולל עדיין נראה תקין.
        for f in sorted(glob.glob(os.path.join(HERE, "bank*.js"))):
            name = os.path.basename(f)
            txt = open(f, encoding="utf-8").read()
            if report(length_stats(txt, td, name), name):
                bad_files.append(name)
        print("  " + "-" * 58)
        report(length_stats(bank, td, "all"), "סה\"כ")
        if bad_files:
            print("  !! חריגה ב:", ", ".join(bad_files),
                  "— אפשר לצבור שם מעל 45% בלי לקרוא. הארך (או קצר) מסיחים בקובץ החורג.")
        else:
            print("  תקין — אף אסטרטגיה עיוורת אינה עוברת 45% באף קובץ.")
except Exception as e:
    print("\n(בדיקת האורך דילגה — נדרש node:", e, ")")
