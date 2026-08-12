# -*- coding: utf-8 -*-
"""
采集后修复各模块图片：用备份里的图片文件补齐新采集丢失的图片。

原理：
  扫描新 js / 备份 js 里所有含 (远程URL, 本地路径) 的对象。
  按 URL 关联：新目录里本地文件缺失时，从备份复制过去（用新采集分配的文件名）。

支持模块：
  Messages, Blogs, Boards, Visitors, Friends（如果任一模块无备份则跳过）
"""
import json
import os
import re
import shutil
import sys
from base64 import b64decode

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(ROOT, '_pre_recollect_backup')

# 每个模块: (显示名, 新 js 路径, 备份 js 路径, 变量名, 新图片目录, 备份图片目录)
MODULES = [
    ('Messages',
     os.path.join(ROOT, 'Messages', 'json', 'messages.js'),
     os.path.join(BACKUP_DIR, 'messages.js.bak'),
     'window.messages',
     os.path.join(ROOT, 'Messages', 'images'),
     os.path.join(BACKUP_DIR, 'Messages_images')),
    ('Blogs',
     os.path.join(ROOT, 'Blogs', 'json', 'blogs.js'),
     os.path.join(BACKUP_DIR, 'blogs.js.bak'),
     'window.blogs',
     os.path.join(ROOT, 'Blogs', 'images'),
     os.path.join(BACKUP_DIR, 'Blogs_images')),
    ('Boards',
     os.path.join(ROOT, 'Boards', 'json', 'boards.js'),
     os.path.join(BACKUP_DIR, 'boards.js.bak'),
     'window.boardInfo',
     os.path.join(ROOT, 'Boards', 'images'),
     os.path.join(BACKUP_DIR, 'Boards_images')),
]

URL_RE = re.compile(r'^https?://', re.I)
LOCAL_RE = re.compile(r'^images/[^/]+$|^[^/]+\.(jpe?g|png|gif|webp|bmp)$', re.I)


def load_js(path, var_name):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    prefix = var_name + ' = '
    if not text.startswith(prefix):
        raise ValueError(f'{path} 不是以 "{prefix}" 开头')
    return json.loads(text[len(prefix):])


def collect_pics(root):
    """
    递归遍历，找到所有 (urls_set, local_filename) 对。
    识别规则：dict 里既有 http URL 字符串值，又有 images/ 或 xxx.jpg 这样的本地路径值。
    """
    results = []

    def walk(obj):
        if isinstance(obj, dict):
            urls = set()
            locals_ = set()
            for v in obj.values():
                if isinstance(v, str):
                    if URL_RE.match(v):
                        urls.add(v)
                    elif LOCAL_RE.match(v):
                        # 只取 basename
                        locals_.add(os.path.basename(v))
                elif isinstance(v, (dict, list)):
                    walk(v)
            if locals_ and urls:
                for fn in locals_:
                    results.append((urls, fn))
            # 处理博客的 custom_html/html 里嵌入的 <img>: 无 URL 对应，跳过
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(root)
    return results


def process_module(name, new_js, bak_js, var_name, new_img_dir, bak_img_dir):
    if not os.path.exists(new_js):
        print(f'  [跳过] 新数据不存在: {new_js}')
        return
    if not os.path.exists(bak_js):
        print(f'  [跳过] 备份不存在: {bak_js}')
        return
    if not os.path.exists(bak_img_dir):
        print(f'  [跳过] 备份图片目录不存在: {bak_img_dir}')
        return
    os.makedirs(new_img_dir, exist_ok=True)

    try:
        new_data = load_js(new_js, var_name)
        bak_data = load_js(bak_js, var_name)
    except Exception as e:
        print(f'  [错误] 加载失败: {e}')
        return

    # 备份索引：url -> old_filename
    url_to_old = {}
    for urls, fn in collect_pics(bak_data):
        for u in urls:
            url_to_old.setdefault(u, fn)

    total = 0
    already_ok = 0
    recovered = 0
    unrecoverable = []

    for urls, new_fn in collect_pics(new_data):
        total += 1
        new_path = os.path.join(new_img_dir, new_fn)
        if os.path.exists(new_path):
            already_ok += 1
            continue
        # 尝试用 URL 找旧文件
        old_fn = None
        for u in urls:
            if u in url_to_old:
                old_fn = url_to_old[u]
                break
        if old_fn:
            old_path = os.path.join(bak_img_dir, old_fn)
            if os.path.exists(old_path):
                shutil.copy2(old_path, new_path)
                recovered += 1
                continue
        unrecoverable.append((new_fn, next(iter(urls), '')))

    print(f'  引用: {total}  已存在: {already_ok}  已恢复: {recovered}  无法恢复: {len(unrecoverable)}')
    if unrecoverable:
        for fn, url in unrecoverable[:10]:
            print(f'    缺: {fn}  <- {url[:80]}')
        if len(unrecoverable) > 10:
            print(f'    ...共 {len(unrecoverable)} 条')


def main():
    if not os.path.isdir(BACKUP_DIR):
        print(f'ERROR: 备份目录不存在 {BACKUP_DIR}')
        return 1
    for mod in MODULES:
        print(f'\n=== {mod[0]} ===')
        process_module(*mod)
    print('\n完成。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
