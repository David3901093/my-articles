# -*- coding: utf-8 -*-
import json, sys, base64, re
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

with open('Blogs/json/blogs.js', 'r', encoding='utf-8') as f:
    raw = f.read()
data = json.loads(raw[len('window.blogs = '):])

print(f'Total: {len(data)}')

# Year distribution
years = Counter()
for b in data:
    t = b.get('pubTime','')[:4]
    if t:
        years[t] += 1
print('\n=== Year ===')
for y in sorted(years.keys()):
    print(f'  {y}: {years[y]}')

# Categories
print('\n=== Categories ===')
cats = Counter(b.get('cate','') or b.get('category','') or '(无)' for b in data)
for c, n in cats.most_common(20):
    print(f'  {c}: {n}')

# Source
print('\n=== Source ===')
src = Counter(b.get('custom_source','') or '(采集)' for b in data)
for s, n in src.most_common():
    print(f'  {s}: {n}')

# Text length distribution
print('\n=== Text length (chars) ===')
lengths = []
for b in data:
    html = b.get('custom_html') or b.get('html') or ''
    try:
        decoded = base64.b64decode(html).decode('utf-8')
        # strip HTML tags
        text = re.sub(r'<[^>]+>', '', decoded)
        text = re.sub(r'\s+', '', text)
        lengths.append(len(text))
    except:
        lengths.append(0)

lengths.sort(reverse=True)
print(f'  Max: {lengths[0]} chars')
print(f'  Min: {lengths[-1]} chars')
print(f'  Median: {lengths[len(lengths)//2]} chars')
print(f'  Mean: {sum(lengths)//len(lengths)} chars')

# Articles with >1000 chars (substantial)
substantial = sum(1 for l in lengths if l > 1000)
print(f'  >1000 chars: {substantial}')
print(f'  >5000 chars: {sum(1 for l in lengths if l > 5000)}')
print(f'  >10000 chars: {sum(1 for l in lengths if l > 10000)}')

# Recent 3 years (2024-2026) substantial articles
print('\n=== Recent 3 years (2024-2026) with >1000 chars ===')
recent = []
for b in data:
    t = b.get('pubTime','')[:4]
    html = b.get('custom_html') or b.get('html') or ''
    try:
        decoded = base64.b64decode(html).decode('utf-8')
        text = re.sub(r'<[^>]+>', '', decoded)
        text = re.sub(r'\s+', '', text)
        l = len(text)
    except:
        l = 0
    if t in ('2024','2025','2026') and l > 1000:
        recent.append((t, b.get('pubTime',''), b.get('title',''), l, b.get('cate','') or b.get('category',''), b.get('custom_source','')))

print(f'Count: {len(recent)}')
for r in sorted(recent, key=lambda x: x[0])[::-1]:
    print(f'  [{r[0]}] {r[1]} | {r[3]}字 | {r[4]} | {r[5] or ""} | {r[2][:50]}')