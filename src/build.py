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
try:
    with tempfile.TemporaryDirectory() as td:
        jsf = os.path.join(td, "bank.js"); open(jsf, "w", encoding="utf-8").write(bank)
        chk = os.path.join(td, "check.js"); open(chk, "w", encoding="utf-8").write(CHECK)
        r = subprocess.run(["node", chk, jsf], capture_output=True, text=True, encoding="utf-8")
        s = json.loads(r.stdout.strip())
        n = s["n"]
        pct = lambda x: int(round(x / n * 100))
        print("\nבדיקת אורך התשובות (כדי שלא ניתן יהיה לענות בלי לקרוא):")
        print("  \"בחר את הארוכה ביותר\" = %d%%   \"בחר את הקצרה ביותר\" = %d%%   [מקרי ≈ 25%%]"
              % (pct(s["long"]), pct(s["short"])))
        print("  פיזור דירוג-האורך של הנכונה:", "  ".join("%d%%" % pct(x) for x in s["rank"]),
              "  [אחיד = 25% בכל מקום]")
        worst = max(s["rank"])
        if pct(worst) > 45:
            print("  !! אזהרה: אפשר לצבור %d%% בלי לקרוא — הארך מסיחים בשאלות החורגות" % pct(worst))
        elif pct(s["long"]) > 40:
            print("  !! אזהרה: התשובה הנכונה היא הארוכה ביותר לעיתים קרובות מדי")
        else:
            print("  תקין.")
except Exception as e:
    print("\n(בדיקת האורך דילגה — נדרש node:", e, ")")
