# -*- coding: utf-8 -*-
"""
合并脚本：QQ空间重新采集后，将手动添加的文章合并回 blogs.js

使用方法：
1. 采集前运行：py merge.py backup    （备份当前数据）
2. 采集QQ空间数据（会覆盖 blogs.js）
3. 采集后运行：py merge.py merge    （合并手动文章到新数据）
"""
import json, sys, os, shutil
sys.stdout.reconfigure(encoding='utf-8')

BLOGS_FILE = 'Blogs/json/blogs.js'
BACKUP_FILE = 'Blogs/json/blogs_manual_backup.js'

def read_blogs(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return json.loads(content[len('window.blogs = '):])

def write_blogs(filepath, data):
    output = 'window.blogs = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(output)

def cmd_backup():
    """采集前：备份当前 blogs.js"""
    if not os.path.exists(BLOGS_FILE):
        print(f'错误: {BLOGS_FILE} 不存在')
        return
    shutil.copy2(BLOGS_FILE, BACKUP_FILE)

    data = read_blogs(BLOGS_FILE)
    manual = [b for b in data if b.get('custom_source') == 'manual']
    print(f'已备份到 {BACKUP_FILE}')
    print(f'  总文章: {len(data)} 篇')
    print(f'  手动文章: {len(manual)} 篇')
    for b in manual:
        print(f'    - {b.get("custom_title", "")}')

def cmd_merge():
    """采集后：从备份中提取手动文章，合并到新数据"""
    if not os.path.exists(BACKUP_FILE):
        print(f'错误: 备份文件 {BACKUP_FILE} 不存在')
        print('请先运行: py merge.py backup')
        return

    old_data = read_blogs(BACKUP_FILE)
    new_data = read_blogs(BLOGS_FILE)

    manual = [b for b in old_data if b.get('custom_source') == 'manual']

    if len(manual) == 0:
        print('备份中未找到手动文章（custom_source=manual）')
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
        """从 pubTime 字段提取可排序的日期值"""
        pt = b.get('pubTime', '')
        if isinstance(pt, (int, float)):
            return pt
        if isinstance(pt, str) and pt:
            # 格式如 "2026-05-22 20:00"，取前10字符做日期比较
            try:
                from datetime import datetime
                return datetime.strptime(pt[:16], '%Y-%m-%d %H:%M')
            except ValueError:
                return 0
        return 0

    all_articles.sort(key=parse_pubtime, reverse=True)

    write_blogs(BLOGS_FILE, all_articles)

    print(f'采集数据: {len(new_data)} 篇')
    print(f'手动文章: {len(manual_to_add)} 篇')
    print(f'合并后: {len(all_articles)} 篇（已按日期降序排列）')
    for b in manual_to_add:
        print(f'  + {b.get("custom_title", "")}')
    print(f'\n已写回 {BLOGS_FILE}')
    print(f'请更新 index.html 中的日志计数为 {len(all_articles)}')

def cmd_status():
    """查看当前状态"""
    data = read_blogs(BLOGS_FILE)
    manual = [b for b in data if b.get('custom_source') == 'manual']
    has_backup = os.path.exists(BACKUP_FILE)

    print(f'当前文章: {len(data)} 篇')
    print(f'手动文章: {len(manual)} 篇')
    print(f'备份文件: {"存在" if has_backup else "不存在"}')
    if manual:
        for b in manual:
            print(f'  - {b.get("custom_title", "")}')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法:')
        print('  py merge.py backup   - 采集前备份')
        print('  py merge.py merge    - 采集后合并')
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
