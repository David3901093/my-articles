# -*- coding: utf-8 -*-
"""
采集后修复说说图片：用备份里的图片文件补齐新采集丢失的图片。

原理：
  新 messages.js 里每张图有 (URL, 新文件名)。
  备份 messages.js.bak 里同一 URL 对应 (URL, 旧文件名) + 本地文件已备份。
  按 URL 关联：如果新图片文件不存在，把备份里的旧文件用新文件名复制过去。
"""
import json
import os
import shutil
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.abspath(__file__))
NEW_JS = os.path.join(ROOT, 'Messages', 'json', 'messages.js')
NEW_IMG_DIR = os.path.join(ROOT, 'Messages', 'images')
BACKUP_DIR = os.path.join(ROOT, '_pre_recollect_backup')
BAK_JS = os.path.join(BACKUP_DIR, 'messages.js.bak')
BAK_IMG_DIR = os.path.join(BACKUP_DIR, 'Messages_images')

URL_FIELDS = ('custom_url', 'o_url', 'b_url', 'hd_url', 's_url', 'url', 'burl')


def load_js(path, var_name='window.messages'):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    prefix = var_name + ' = '
    if not text.startswith(prefix):
        raise ValueError(f'{path} does not start with "{prefix}"')
    return json.loads(text[len(prefix):])


def iter_pics(messages):
    """遍历 messages 里所有可能含图片的 dict：返回 (pic_dict, filename, url_set)"""
    def walk(pic_list):
        if not isinstance(pic_list, list):
            return
        for pic in pic_list:
            if not isinstance(pic, dict):
                continue
            fn = pic.get('custom_filename') or ''
            urls = set()
            for k in URL_FIELDS:
                v = pic.get(k)
                if v and isinstance(v, str):
                    urls.add(v)
            if fn or urls:
                yield pic, fn, urls

    for m in messages:
        # 说说正文的图
        yield from walk(m.get('pic', []))
        yield from walk(m.get('rich_info', []))
        # 评论里的图
        for c in m.get('commentlist', []):
            yield from walk(c.get('pic', []))
            yield from walk(c.get('rich_info', []))
            for r in c.get('replylist', []) or []:
                yield from walk(r.get('pic', []))
                yield from walk(r.get('rich_info', []))


def main():
    if not os.path.exists(BAK_JS):
        print(f'ERROR: 备份不存在 {BAK_JS}')
        return 1
    if not os.path.exists(NEW_JS):
        print(f'ERROR: 新数据不存在 {NEW_JS}')
        return 1

    print('加载数据...')
    new_msgs = load_js(NEW_JS)
    bak_msgs = load_js(BAK_JS)

    # 备份索引：url -> old_filename
    url_to_old_fn = {}
    for _, fn, urls in iter_pics(bak_msgs):
        if not fn:
            continue
        for u in urls:
            url_to_old_fn.setdefault(u, fn)

    print(f'  新说说数: {len(new_msgs)}  备份说说数: {len(bak_msgs)}')
    print(f'  备份 URL→filename 映射: {len(url_to_old_fn)} 条')

    total_pics = 0
    ok_pics = 0
    missing_recovered = 0
    missing_unrecoverable = 0
    unrecoverable_list = []

    for pic, new_fn, urls in iter_pics(new_msgs):
        if not new_fn:
            continue
        total_pics += 1
        new_path = os.path.join(NEW_IMG_DIR, new_fn)
        if os.path.exists(new_path):
            ok_pics += 1
            continue
        # 新文件缺失，尝试用 URL 找备份里的旧文件
        old_fn = None
        for u in urls:
            if u in url_to_old_fn:
                old_fn = url_to_old_fn[u]
                break
        if old_fn:
            old_path = os.path.join(BAK_IMG_DIR, old_fn)
            if os.path.exists(old_path):
                shutil.copy2(old_path, new_path)
                missing_recovered += 1
                continue
        missing_unrecoverable += 1
        unrecoverable_list.append((new_fn, list(urls)[:1]))

    print()
    print('=== 修复报告 ===')
    print(f'  新数据引用图片总数:   {total_pics}')
    print(f'  新目录已存在:         {ok_pics}')
    print(f'  从备份恢复:           {missing_recovered}')
    print(f'  无法恢复:             {missing_unrecoverable}')

    if unrecoverable_list:
        print()
        print('无法恢复的图片（前20）：')
        for fn, urls in unrecoverable_list[:20]:
            print(f'  {fn}  <- {urls}')
        if len(unrecoverable_list) > 20:
            print(f'  ...共 {len(unrecoverable_list)} 张')

    return 0


if __name__ == '__main__':
    sys.exit(main())
