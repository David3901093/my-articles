# -*- coding: utf-8 -*-
"""
合并脚本：QQ空间重新采集后，将手动添加的文章合并回 blogs.js
然后重新生成 blogs_meta.js 和 blogs/ 目录下的内容文件

使用方法：
1. 采集前运行：py merge.py backup    （备份当前数据）
2. 采集QQ空间数据（会覆盖 blogs.js）
3. 采集后运行：py merge.py merge    （合并手动文章到新数据，重新生成拆分文件）
"""
import json, sys, os, shutil, base64
sys.stdout.reconfigure(encoding='utf-8')

BLOGS_FILE = 'Blogs/json/blogs.js'
BACKUP_FILE = 'Blogs/json/blogs_manual_backup.js'
META_FILE = 'Blogs/json/blogs_meta.js'
CONTENT_DIR = 'Blogs/json/blogs'

META_FIELDS = [
    'blogId', 'blogType', 'pubTime', 'lastModifyTime',
    'cate', 'cateHex', 'title', 'custom_title',
    'commentNum', 'replynum', 'category',
    'abstract', 'artype', 'blogid',
    'custom_author', 'custom_source',
    'custom_visitor', 'likeTotal', 'effect',
]

def read_blogs(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return json.loads(content[len('window.blogs = '):])

def write_blogs(filepath, data):
    output = 'window.blogs = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(output)

def regenerate_split_files(data):
    """从完整数据重新生成 blogs_meta.js 和 blogs/ 目录"""
    os.makedirs(CONTENT_DIR, exist_ok=True)

    meta = []
    for b in data:
        m = {}
        for f in META_FIELDS:
            if f in b and b[f] is not None:
                m[f] = b[f]
        meta.append(m)

        blog_id = b.get('blogid', b.get('blogId'))
        content_path = os.path.join(CONTENT_DIR, f'blog_{blog_id}.js')
        with open(content_path, 'w', encoding='utf-8') as cf:
            cf.write('window.blogDetail = ' + json.dumps(b, ensure_ascii=False, separators=(',', ':')))

    with open(META_FILE, 'w', encoding='utf-8') as f:
        f.write('window.blogs = ' + json.dumps(meta, ensure_ascii=False, separators=(',', ':')))

    print(f'  生成 {META_FILE}: {os.path.getsize(META_FILE)//1024} KB')
    print(f'  生成 {CONTENT_DIR}/: {len(data)} 个内容文件')

def cmd_backup():
    """采集前：备份 blogs.js + blogs_meta.js + blogs/ 目录"""
    if not os.path.exists(BLOGS_FILE):
        print(f'错误: {BLOGS_FILE} 不存在')
        return

    # 备份完整数据（采集兼容 + merge 数据源）
    shutil.copy2(BLOGS_FILE, BACKUP_FILE)

    # 备份元数据和内容文件（秒恢复用）
    meta_backup = 'Blogs/json/blogs_meta_backup.js'
    content_backup = 'Blogs/json/blogs_backup'
    if os.path.exists(META_FILE):
        shutil.copy2(META_FILE, meta_backup)
    if os.path.exists(CONTENT_DIR):
        if os.path.exists(content_backup):
            shutil.rmtree(content_backup)
        shutil.copytree(CONTENT_DIR, content_backup)

    data = read_blogs(BLOGS_FILE)
    manual = [b for b in data if b.get('custom_source') == 'manual']
    content_count = len([f for f in os.listdir(CONTENT_DIR)]) if os.path.exists(CONTENT_DIR) else 0
    print(f'已备份到:')
    print(f'  {BACKUP_FILE}')
    print(f'  {meta_backup}')
    print(f'  {content_backup}/ ({content_count} 个内容文件)')
    print(f'  总文章: {len(data)} 篇 | 手动文章: {len(manual)} 篇')
    for b in manual:
        print(f'    - {b.get("custom_title", "")}')

def cmd_merge():
    """采集后：从备份中提取手动文章，合并到新数据，重新生成拆分文件"""
    if not os.path.exists(BACKUP_FILE):
        print(f'错误: 备份文件 {BACKUP_FILE} 不存在')
        print('请先运行: py merge.py backup')
        return

    old_data = read_blogs(BACKUP_FILE)
    new_data = read_blogs(BLOGS_FILE)

    manual = [b for b in old_data if b.get('custom_source') == 'manual']

    if len(manual) == 0:
        print('备份中未找到手动文章（custom_source=manual）')
        print('仍需重新生成拆分文件...')
        regenerate_split_files(new_data)
        return

    # 去重：新数据中可能已有相同 blogId 的文章
    new_ids = set(b.get('blogId') for b in new_data)
    manual_to_add = [b for b in manual if b.get('blogId') not in new_ids]

    # 校对文章：用备份中的校对版本覆盖新数据中的原始版本
    proofread = {b.get('blogId'): b for b in old_data if b.get('custom_proofread')}
    proofread_count = 0
    for i, b in enumerate(new_data):
        bid = b.get('blogId')
        if bid in proofread:
            new_data[i] = proofread[bid]
            proofread_count += 1

    if proofread_count > 0:
        print(f'恢复校对修正: {proofread_count} 篇')

    # 合并所有文章，按日期降序排列（最新在前）
    all_articles = manual_to_add + new_data

    def parse_pubtime(b):
        pt = b.get('pubTime', '')
        if isinstance(pt, (int, float)):
            return pt
        if isinstance(pt, str) and pt:
            try:
                from datetime import datetime
                return datetime.strptime(pt[:16], '%Y-%m-%d %H:%M')
            except ValueError:
                return 0
        return 0

    all_articles.sort(key=parse_pubtime, reverse=True)

    # 写回完整 blogs.js（保留原始格式供未来采集兼容）
    write_blogs(BLOGS_FILE, all_articles)
    print(f'采集数据: {len(new_data)} 篇')
    print(f'手动文章: {len(manual_to_add)} 篇')
    print(f'合并后: {len(all_articles)} 篇（已按日期降序排列）')
    for b in manual_to_add:
        print(f'  + {b.get("custom_title", "")}')

    # 重新生成拆分文件
    regenerate_split_files(all_articles)
    print(f'\n已写回 {BLOGS_FILE}')
    print(f'请更新 index.html 中的日志计数为 {len(all_articles)}')

def cmd_status():
    """查看当前状态"""
    data = read_blogs(BLOGS_FILE)
    manual = [b for b in data if b.get('custom_source') == 'manual']
    has_backup = os.path.exists(BACKUP_FILE)
    has_meta = os.path.exists(META_FILE)
    content_files = len([f for f in os.listdir(CONTENT_DIR) if f.startswith('blog_')]) if os.path.exists(CONTENT_DIR) else 0

    print(f'当前文章: {len(data)} 篇')
    print(f'手动文章: {len(manual)} 篇')
    print(f'备份文件: {"存在" if has_backup else "不存在"}')
    print(f'元数据文件: {"存在" if has_meta else "不存在"}')
    print(f'内容文件: {content_files} 个')
    if manual:
        for b in manual:
            print(f'  - {b.get("custom_title", "")}')

def cmd_restore():
    """从备份恢复拆分文件（blogs_meta.js + blogs/ 目录）"""
    meta_backup = 'Blogs/json/blogs_meta_backup.js'
    content_backup = 'Blogs/json/blogs_backup'

    if not os.path.exists(meta_backup):
        print(f'错误: 备份 {meta_backup} 不存在，请先运行 py merge.py backup')
        return

    shutil.copy2(meta_backup, META_FILE)
    print(f'  恢复 {META_FILE}')

    if os.path.exists(content_backup):
        if os.path.exists(CONTENT_DIR):
            shutil.rmtree(CONTENT_DIR)
        shutil.copytree(content_backup, CONTENT_DIR)
        count = len([f for f in os.listdir(CONTENT_DIR)])
        print(f'  恢复 {CONTENT_DIR}/ ({count} 个内容文件)')

    print('恢复完成')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法:')
        print('  py merge.py backup   - 采集前备份（blogs.js + 拆分文件）')
        print('  py merge.py merge    - 采集后合并 + 重新生成拆分文件')
        print('  py merge.py restore  - 从备份恢复拆分文件（不出问题时不需要）')
        print('  py merge.py status   - 查看状态')
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == 'backup':
        cmd_backup()
    elif cmd == 'merge':
        cmd_merge()
    elif cmd == 'status':
        cmd_status()
    else:
        print(f'未知命令: {cmd}')
