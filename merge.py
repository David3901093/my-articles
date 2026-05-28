# -*- coding: utf-8 -*-
"""
合并脚本：QQ空间重新采集后，将手动添加的文章合并回 blogs.js

使用方法：
1. 重新采集QQ空间数据（会生成新的 blogs.js）
2. 运行此脚本：py merge.py
3. 脚本会自动保留手动文章，合并到新数据最前面
"""
import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

BLOGS_FILE = 'Blogs/json/blogs.js'
BACKUP_FILE = 'Blogs/json/blogs.js.bak'

with open(BLOGS_FILE, 'r', encoding='utf-8') as f:
    content = f.read()
data = json.loads(content[len('window.blogs = '):])

# 分离：手动文章 vs 采集文章
manual = [b for b in data if b.get('custom_source') == 'manual']
collected = [b for b in data if not b.get('custom_source') == 'manual']

print(f'当前数据: {len(data)} 篇 (手动 {len(manual)} 篇, 采集 {len(collected)} 篇)')

if len(manual) == 0:
    print('未找到手动文章（custom_source=manual），请确认标记是否正确')
    sys.exit(1)

# 备份当前文件
import shutil
if os.path.exists(BLOGS_FILE):
    shutil.copy2(BLOGS_FILE, BACKUP_FILE)
    print(f'已备份到 {BACKUP_FILE}')

# 手动文章插入最前面（按原顺序）
merged = manual + collected

# 更新首页计数
print(f'合并后总数: {len(merged)} 篇')

output = 'window.blogs = ' + json.dumps(merged, ensure_ascii=False, separators=(',', ':'))
with open(BLOGS_FILE, 'w', encoding='utf-8') as f:
    f.write(output)

print(f'已合并写回 {BLOGS_FILE}')
print(f'请手动更新 index.html 中的日志计数为 {len(merged)}')
