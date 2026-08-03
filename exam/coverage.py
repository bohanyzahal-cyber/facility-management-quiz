# -*- coding: utf-8 -*-
"""מצליב כל שאלה בבנק מול החוברת, ומדרג לפי כמה ממנה נמצא שם.

הרעיון: מכל שאלה נשלפים ה"עוגנים" — מספרים, מונחים באנגלית ומילים
עבריות נדירות — מתוך התשובה הנכונה ומההסבר. אלה הדברים שאי אפשר
לנסח מחדש. אם אף אחד מהם אינו בחוברת, כנראה שהנושא אינו שם.

זהו מחולל מועמדים, לא פסק דין: רעיון שנוסח בחוברת במילים אחרות
לגמרי ייראה כחסר. כל מה שנדלק נקרא ביד.

    python coverage.py            # סיכום + הרשימה הגרועה ביותר
    python coverage.py --all      # כל השאלות שאינן מכוסות במלואן
"""
import io, json, os, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- טעינת הבנק דרך node: bank1 מכריז var BANK, ולכן חייבים eval אחד ---
NODE = r"""
var fs=require('fs'), p=%s;
var fl=fs.readdirSync(p).filter(f=>/^bank\d+\.js$/.test(f))
        .sort((a,b)=>parseInt(a.slice(4))-parseInt(b.slice(4)));
eval(fl.map(f=>fs.readFileSync(p+'/'+f,'utf8')).join('\n'));
process.stdout.write(JSON.stringify(BANK));
""" % json.dumps(os.path.join(REPO, "src").replace("\\", "/"))
BANK = json.loads(subprocess.run(["node", "-e", NODE], capture_output=True,
                                 check=True).stdout.decode("utf-8"))

def norm(s):
    """מסיר את סימוני החוברת כדי שהשוואת מחרוזות לא תיפול עליהם."""
    s = re.sub(r"[*_«»⟨⟩\"'`׳״]", "", s)
    return re.sub(r"\s+", " ", s)

AID = norm(io.open(os.path.join(REPO, "exam", "content.js"), encoding="utf-8").read())

# מילים שכיחות מדי מכדי להעיד על כלום
STOP = set("""
של את זה זו זאת הוא היא הם הן אני אתה אנחנו יש אין לא כן גם רק אבל או
כי אם כך כמו עם על אל מן מה מי איך למה מתי כמה כל כלל בין לפי אחרי לפני
תחת מעל מתחת בתוך מחוץ אצל בלי עוד יותר פחות מאוד הרבה מעט אחד אחת שני
שתי שלוש ארבע חמש שש שבע שמונה תשע עשר היה היו יהיה תהיה להיות עושה
עשה לעשות נותן נתן לתת יכול יכולה צריך צריכה חייב חייבת אפשר אפשרי
בדרך כלל למשל כלומר כדי בגלל לכן ולכן ואז ואילו אשר שבו שבה שבהם אותו
אותה אותם הזה הזאת ההוא ההיא שלו שלה שלהם שלנו שלי לך לו לה להם לנו
במקום בזמן בשלב בתחום בעולם בארץ בישראל בחברה בארגון בעסק במקרה
המרצה בלשונו דוגמה הכלל העיקרון הסיבה המטרה התוצאה הפתרון הבעיה
נדרש נדרשת חשוב חשובה מקובל מקובלת נהוג ניתן צריכים אפשרות
""".split())

def anchors(q):
    """עוגנים: מספרים, מונחים לועזיים, ומילים עבריות ארוכות ולא שכיחות."""
    text = norm(q["o"][q["c"]] + " " + q.get("e", ""))
    out = set()
    out |= {m.group() for m in re.finditer(r"\d[\d,.]*", text) if len(m.group()) >= 2}
    out |= {m.group() for m in re.finditer(r"[A-Za-z][A-Za-z&\-]{2,}", text)}
    for w in re.findall(r"[\u0590-\u05FF]{4,}", text):
        if w not in STOP:
            out.add(w)
    return out

rows = []
for i, q in enumerate(BANK):
    a = anchors(q)
    if not a:
        continue
    miss = sorted(x for x in a if x not in AID)
    rows.append({"i": i, "q": q, "n": len(a), "miss": miss,
                 "cov": 1 - len(miss) / len(a)})

rows.sort(key=lambda r: (r["cov"], -r["n"]))

print(f"נבדקו {len(rows)} שאלות מתוך {len(BANK)}\n")
buckets = {"0%": 0, "עד 25%": 0, "25-50%": 0, "50-75%": 0, "75-99%": 0, "100%": 0}
for r in rows:
    c = r["cov"]
    k = ("100%" if c == 1 else "0%" if c == 0 else "עד 25%" if c < .25
         else "25-50%" if c < .5 else "50-75%" if c < .75 else "75-99%")
    buckets[k] += 1
for k, v in buckets.items():
    print(f"  כיסוי {k:<8} {v:>4} שאלות")

limit = len(rows) if "--all" in sys.argv else 70
print(f"\n{'='*70}\nהחשודים (כיסוי נמוך = הכי סביר שחסר בחוברת)\n{'='*70}")
for r in rows[:limit]:
    if r["cov"] >= 0.5:
        break
    q = r["q"]
    print(f"\n[{r['cov']:.0%} | {q['t']} | {q['s']}] #{r['i']}")
    print(f"  ש: {q['q'][:100]}")
    print(f"  ✓ {q['o'][q['c']][:110]}")
    print(f"  חסר: {', '.join(r['miss'][:12])}")
