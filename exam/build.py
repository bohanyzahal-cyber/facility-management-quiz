# -*- coding: utf-8 -*-
"""בונה את חוברת החומר הפתוח: מזריק content.js לתוך template.html.

הדפדוף, מספור העמודים, השער והמפתח נבנים בזמן טעינה בדפדפן — כך
מספרי העמודים במפתח תמיד נכונים גם אחרי עריכת תוכן, בלי לתחזק אותם ביד.

הרצה:  python build.py
"""
import io, os, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(os.path.dirname(HERE), "..", "מדריך מבחן - ניהול תשתיות גלובליות.html")

tpl = io.open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
dat = io.open(os.path.join(HERE, "content.js"),   encoding="utf-8").read()

html = re.sub(r"/\*DATA\*/.*?/\*DATA\*/", lambda m: dat.strip(), tpl, flags=re.S)
io.open(os.path.join(HERE, "preview.html"), "w", encoding="utf-8").write(html)
io.open(os.path.abspath(OUT), "w", encoding="utf-8").write(html)

# ספירה גסה של פריטים, כדי לראות שהתוכן אכן גדל
items = len(re.findall(r'" :: ', dat)) + len(re.findall(r'\], \[', dat))
print("נבנה. %d תווים, ~%d פריטי תוכן." % (len(html), items))
print("  ", os.path.abspath(OUT))
