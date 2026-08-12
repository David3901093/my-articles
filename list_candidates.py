# -*- coding: utf-8 -*-
import json, sys, base64, re
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

with open('Blogs/json/blogs.js', 'r', encoding='utf-8') as f:
    raw = f.read()
data = json.loads(raw[len('window.blogs = '):])

def extract_text(html):
    try:
        decoded = base64.b64decode(html).decode('utf-8')
        text = re.sub(r'<[^>]+>', '\n', decoded)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    except:
        return ''

# Focus: 2016-2026 articles with >1500 chars (real writing, not notes)
# Also include "作文选揖" category which likely has earlier literary work
candidates = []
for b in data:
    t = b.get('pubTime','')[:4]
    html = b.get('custom_html') or b.get('html') or ''
    text = extract_text(html)
    l = len(text.replace('\n',''))
    cat = b.get('cate','') or b.get('category','')
    if l >= 1500 and (t in ('2016','2017','2018','2019','2020','2021','2022','2023','2024','2025','2026') or cat == '作文选揖'):
        candidates.append({
            'year': t,
            'time': b.get('pubTime',''),
            'title': b.get('title',''),
            'chars': l,
            'cat': cat,
            'source': b.get('custom_source','') or '',
            'text_preview': text[:200].replace('\n',' ')
        })

# Sort by year
candidates.sort(key=lambda x: x['time'])

print(f'Candidates (>=1500 chars, 2016+ or 作文选揖): {len(candidates)}')
print()
for c in candidates:
    tag = f'[{c["source"]}]' if c['source'] else ''
    print(f'{c["year"]} | {c["chars"]:>6}字 | {c["cat"]} {tag} | {c["title"][:60]}')
    print(f'       preview: {c["text_preview"][:100]}')
    print()