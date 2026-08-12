# -*- coding: utf-8 -*-
"""
Extract selected articles from QQ-zone blogs.js for style profile learning.
Output: style_corpus.md (concatenated text with metadata headers)
"""
import json, sys, base64, re

sys.stdout.reconfigure(encoding='utf-8')

with open('Blogs/json/blogs.js', 'r', encoding='utf-8') as f:
    raw = f.read()
data = json.loads(raw[len('window.blogs = '):])

# Selected titles (exact match against blog title field)
SELECTED = [
    # Recent era (2024-2026) - strongest weight
    '寒窗与语言',
    '信息技术,AIGC,Vibe Coding与我',
    '中盘的胜负手',
    '不知如何开口',
    '先抑后扬的旅行——我与草原二三事',
    '这个毕业季，我想对自己说……',
    '我看“智能”——我们是旷野，它是清风',
    '7月1日   星期三  小雨转晴',
    '开发周年小记',
    '时光故事',
    '转岗小记',
    '写于2025年的第1封信',
    '写给18岁的你——致小弟成年礼',
    # Literary-analytical era (2018-2020)
    '诗画江南',
    '一脉江山换绝唱， 赤子之心永流芳——“千古词帝” 李煜',
    '行走在浪漫中的大唐谪仙—— “诗仙”李白',
    '红尘出走半生，归来仍是少年——“落魄才子”李商隐',
    '异禀绝世神独立，才情兼得是佳人——“词宗” 李清照',
    '浩荡千里快哉风，俗世人间烟火情——“词圣”苏轼',
    # Teacher/professional era (2022-2024)
    '又是一年好春光',
    '最后的叮咛',
    '教育：让树成为树，让花成为花。',
    '“学”以致“用”——数据库应用课程与编码思维培养的实践与反思',
    '书本与人间',
    '未竟',
]

def extract_text(html):
    try:
        decoded = base64.b64decode(html).decode('utf-8')
        # Replace </div> with newlines, strip other tags
        decoded = re.sub(r'</div>', '\n', decoded)
        decoded = re.sub(r'<br\s*/?>', '\n', decoded)
        decoded = re.sub(r'<[^>]+>', '', decoded)
        decoded = re.sub(r'&nbsp;', ' ', decoded)
        decoded = re.sub(r'&amp;', '&', decoded)
        decoded = re.sub(r'&lt;', '<', decoded)
        decoded = re.sub(r'&gt;', '>', decoded)
        decoded = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), decoded)
        decoded = re.sub(r'\n{3,}', '\n\n', decoded)
        return decoded.strip()
    except Exception as e:
        return f'[EXTRACT ERROR: {e}]'

matched = []
not_found = []
for target in SELECTED:
    found = False
    for b in data:
        title = b.get('title','')
        # Try exact match, then fuzzy
        if title.strip() == target.strip():
            html = b.get('custom_html') or b.get('html') or ''
            text = extract_text(html)
            pub = b.get('pubTime','')
            cat = b.get('cate','') or b.get('category','')
            chars = len(re.sub(r'\s','',text))
            matched.append({
                'title': title,
                'pubTime': pub,
                'cat': cat,
                'chars': chars,
                'text': text,
                'source': b.get('custom_source','') or ''
            })
            found = True
            break
    if not found:
        not_found.append(target)

print(f'Matched: {len(matched)} / {len(SELECTED)}')
print(f'Not found: {not_found}')
print()

total_chars = 0
for m in matched:
    total_chars += m['chars']
    print(f'  [{m["pubTime"][:4]}] {m["chars"]:>6}字 | {m["cat"]} | {m["source"] or ""} | {m["title"][:60]}')
print(f'\nTotal: {total_chars} chars')

# Write corpus
with open('style_corpus.md', 'w', encoding='utf-8') as f:
    for i, m in enumerate(matched, 1):
        f.write(f'\n\n---\n## Article {i}: {m["title"]} ({m["pubTime"]}, {m["chars"]}字)\n---\n\n')
        f.write(m['text'])
        f.write('\n')

print('\nWritten to style_corpus.md')