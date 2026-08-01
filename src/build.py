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

def bank_files():
    """מיון מספרי — מיון לקסיקוגרפי היה שם את bank10 לפני bank2."""
    fs = glob.glob(os.path.join(HERE, "bank*.js"))
    return sorted(fs, key=lambda f: int(re.search(r"bank(\d+)", os.path.basename(f)).group(1)))

tpl  = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
bank = "\n".join(open(f, encoding="utf-8").read() for f in bank_files())
html = tpl.replace("/*__BANK__*/", bank)

for t in TARGETS:
    open(t, "w", encoding="utf-8").write(html)
    print("נכתב:", t)
print("גודל: %.0f KB" % (len(html) / 1024))

# ---------- בדיקות שפיות ----------
objs = re.findall(r'\{t:"(.*?)",s:"(.*?)",q:', bank)
# המחרוזות במקור הן JS מוברח — \" חוזר להיות " (למשל: נדל"ן)
objs = [(t.replace('\\"', '"'), s.replace('\\"', '"')) for t, s in objs]
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

# ---------- עדכון אוטומטי של ה-README ----------
# הטבלה התיישנה בכל פעם שנוספו שאלות, ולכן היא נבנית מהנתונים עצמם.
def update_readme():
    path = os.path.join(REPO, "README.md")
    if not os.path.exists(path):
        return
    txt = open(path, encoding="utf-8").read()
    start, end = "<!-- STATS:START", "<!-- STATS:END -->"
    i, j = txt.find(start), txt.find(end)
    if i < 0 or j < 0:
        return
    ordered = sorted(topics.items(), key=lambda x: -x[1])
    # שלוש עמודות, מילוי לפי שורות
    rows = (len(ordered) + 2) // 3
    cols = [ordered[k*rows:(k+1)*rows] for k in range(3)]
    lines = ["| נושא | | נושא | | נושא |", "|---|---|---|---|---|"]
    for r in range(rows):
        cells = []
        for c in range(3):
            cells.append("%s · %d" % cols[c][r] if r < len(cols[c]) else "")
        lines.append("| %s | | %s | | %s |" % tuple(cells))
    src_line = " · ".join("%s (%d)" % (k, v) for k, v in sorted(srcs.items(), key=lambda x: -x[1]))
    block = (
        "<!-- STATS:START — נוצר אוטומטית על ידי src/build.py, אין לערוך ידנית -->\n"
        "**%d שאלות** בפורמט המבחן — רב-ברירתי (אמריקאי), 4 תשובות לשאלה, חומר פתוח, ציון עובר 60.\n\n"
        "%s\n\n"
        "**לפי מקור:** %s\n"
        % (len(objs), "\n".join(lines), src_line)
    )
    open(path, "w", encoding="utf-8").write(txt[:i] + block + txt[j:])
    print("עודכן:", path)

update_readme()

# ---------- בדיקות מבנה ----------
# עד כה נבדקו ידנית בדפדפן. כאן הן רצות בכל בנייה.
import json, subprocess, tempfile

STRUCT = r"""
const fs=require('fs');
eval(fs.readFileSync(process.argv[2],'utf8'));
/* דפוסים תלויי-מיקום: האפליקציה מערבבת את סדר האפשרויות בכל סבב,
   ולכן מסיח כמו "כל התשובות נכונות" או "תשובות א'+ב'" נשבר.
   הביטוי צר בכוונה — "כל הנ" הרחב תפס גם "בכל הנוגע" ו"כל הנכסים". */
const POS=/כל התשובות נכונות|כל הנ["״']ל|תשובות? א['׳']\s*\+|א['׳']\s*\+\s*ב['׳']|אף תשובה אינה|כל האמור לעיל/;
const err=[], seen={};
BANK.forEach((q,i)=>{
  const at=`#${i} ${(q.q||'').slice(0,40)}`;
  if(!q.t||!q.s||!q.q||!q.e)             err.push(at+' — שדה חסר');
  if(!Array.isArray(q.o)||q.o.length!==4) err.push(at+' — אין בדיוק 4 אפשרויות');
  else if(new Set(q.o).size!==4)          err.push(at+' — אפשרות כפולה');
  if(typeof q.c!=='number'||q.c<0||q.c>3) err.push(at+' — c מחוץ לתחום');
  if((q.o||[]).some(o=>POS.test(o)))      err.push(at+' — מסיח תלוי-מיקום');
  if((q.e||'').length<40)                 err.push(at+' — הסבר קצר מדי');
  if(seen[q.q]!==undefined)               err.push(at+' — שאלה כפולה (גם ב-#'+seen[q.q]+')');
  else seen[q.q]=i;
});
console.log(JSON.stringify({n:BANK.length,err}));
"""

try:
    with tempfile.TemporaryDirectory() as td:
        jsf = os.path.join(td, "all.js")
        open(jsf, "w", encoding="utf-8").write(bank)
        chk = os.path.join(td, "struct.js")
        open(chk, "w", encoding="utf-8").write(STRUCT)
        r = subprocess.run(["node", chk, jsf], capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            raise RuntimeError((r.stderr or "")[:300])
        s = json.loads(r.stdout.strip())
        print("\nבדיקות מבנה (%d שאלות):" % s["n"])
        if s["err"]:
            for e in s["err"][:25]:
                print("  !!", e)
            if len(s["err"]) > 25:
                print("  ... ועוד %d" % (len(s["err"]) - 25))
        else:
            print("  תקין — ללא כפילויות, שדות חסרים או מסיחים תלויי-מיקום.")
except Exception as e:
    print("\n(בדיקות המבנה דילגו — נדרש node:", e, ")")

# ---------- בדיקת "תל האורך" ----------
# כשכותבים שאלות בכמות, התשובה הנכונה יוצאת כמעט תמיד הארוכה ביותר,
# ואז אפשר לענות נכון בלי לקרוא. זו בדיקה שהבעיה לא חזרה.
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
        for f in bank_files():
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
