# -*- coding: utf-8 -*-
"""
自定义资产恢复脚本：QQ空间重新采集后，采集工具可能覆盖站点模板文件。
本脚本一键恢复三类自定义资产（全部幂等，重复运行安全）：
  1. Common/css/common.css 的自定义排版样式块（检测标记，缺失则追加）
  2. Blogs/images/ 下的存档配图（ep*-flow-*.png，缺失则从 _custom/images/ 拷回）
  3. index.html 的日志计数（按 blogs.js 实际篇数改写）
另外检查手动文章（custom_source=manual）是否在 blogs.js 中，缺失时提示走 merge 流程。

使用方法：py custom_restore.py
采集完整流程见 CLAUDE.md「QQ空间重新采集流程」。
"""
import json, os, re, shutil, sys
sys.stdout.reconfigure(encoding='utf-8')

CSS_FILE = 'Common/css/common.css'
CSS_BLOCK = '_custom/custom-css-block.css'
CSS_MARKER = '/* ===== 日志正文排版'
IMAGES_DIR = 'Blogs/images'
IMAGES_BACKUP = '_custom/images'
BLOGS_FILE = 'Blogs/json/blogs.js'
INDEX_FILE = 'index.html'


def restore_css():
    if not os.path.exists(CSS_BLOCK):
        print('[CSS] 备份块不存在:', CSS_BLOCK)
        return
    with open(CSS_BLOCK, 'r', encoding='utf-8', newline='') as f:
        block = f.read()
    cur = ''
    if os.path.exists(CSS_FILE):
        with open(CSS_FILE, 'r', encoding='utf-8', newline='') as f:
            cur = f.read()
    if CSS_MARKER in cur:
        print('[CSS] 自定义样式块已在位，无需恢复')
        return
    # 备份块自带精确的前置换行分隔（CRLF），这里只需给现有内容收尾一个换行
    with open(CSS_FILE, 'w', encoding='utf-8', newline='') as f:
        f.write(cur.rstrip('\r\n \t') + '\r\n' + block)
    print('[CSS] 已追加自定义样式块到', CSS_FILE)


def restore_images():
    if not os.path.isdir(IMAGES_BACKUP):
        print('[IMG] 备份目录不存在:', IMAGES_BACKUP)
        return
    os.makedirs(IMAGES_DIR, exist_ok=True)
    restored, ok = [], 0
    for f in sorted(os.listdir(IMAGES_BACKUP)):
        dst = os.path.join(IMAGES_DIR, f)
        if not os.path.exists(dst):
            shutil.copy2(os.path.join(IMAGES_BACKUP, f), dst)
            restored.append(f)
        else:
            ok += 1
    print(f'[IMG] 在位 {ok} 张，恢复 {len(restored)} 张' + ('：' + ', '.join(restored) if restored else ''))


def fix_badge():
    if not os.path.exists(BLOGS_FILE):
        print('[计数] 找不到', BLOGS_FILE)
        return
    with open(BLOGS_FILE, 'r', encoding='utf-8') as f:
        data = json.loads(f.read()[len('window.blogs = '):])
    count = len(data)
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        s = f.read()
    s2 = re.sub(r'(\u65e5\u5fd7<span class="badge badge-primary badge-pill">)\d+(</span>)',
                lambda m: m.group(1) + str(count) + m.group(2), s)
    if s2 != s:
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write(s2)
        print(f'[计数] index.html 日志计数已更新为 {count}')
    else:
        print(f'[计数] 日志计数已正确（{count}）')


def check_manual():
    with open(BLOGS_FILE, 'r', encoding='utf-8') as f:
        data = json.loads(f.read()[len('window.blogs = '):])
    manual = [b for b in data if b.get('custom_source') == 'manual']
    dev = [b for b in manual if b.get('cate') == '开发手记']
    print(f'[数据] 手动文章 {len(manual)} 篇，其中开发手记存档 {len(dev)} 篇')
    if len(dev) < 16:
        print('[数据] 警告：开发手记存档不足 16 篇，请运行: py merge.py merge （从备份合并回手动文章）')


if __name__ == '__main__':
    restore_css()
    restore_images()
    fix_badge()
    check_manual()
    print('完成。')
