# QQ空间备份站点 - 博客更新指南

## 项目结构

- `index.html` — 首页入口，包含各模块统计数字（日志数、说说数等）
- `Blogs/index.html` — 日志列表页（通过 JS 动态渲染）
- `Blogs/info.html` — 日志详情页（通过 `?blogId=xxx` 参数加载）
- `Blogs/json/blogs.js` — 所有日志数据（JSON 格式，变量 `window.blogs`）
- `Blogs/js/blogs.js` — 列表页渲染逻辑
- `Blogs/js/bloginfo.js` — 详情页渲染逻辑

## 新增博客文章流程

### 1. 准备文章数据

用 Python 脚本操作 `Blogs/json/blogs.js`，步骤如下：

```python
# -*- coding: utf-8 -*-
import base64, json, time, sys
sys.stdout.reconfigure(encoding='utf-8')

title = "文章标题"
author = "作者名"  # 如与空间主人相同则不需要此字段
paragraphs = ["段落1", "段落2", ...]  # 每个段落对应用户给出的一个自然段

# 构建 HTML（与已有文章格式一致）
html_parts = ['                                                <div class="blog_details_20120222">']
for p in paragraphs:
    html_parts.append('<div>' + p + '</div>')
    html_parts.append('<div><br></div>')
html_parts.pop()  # 去掉最后一个多余的 <br>
html_parts.append('</div>')
html_content = ''.join(html_parts)

# Base64 编码
custom_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')

# 生成 blogId（用时间戳）
blogId = int(time.time())
```

### 2. 构造博客 JSON 对象

```python
new_blog = {
    "blogId": blogId,
    "blogType": 0,
    "pubTime": "2026-05-22 20:00",       # 发表日期
    "sLastModifyTime": None,
    "lastModifyTime": blogId,
    "cate": "个人日记",                     # 分类（默认，用户指定时替换）
    "cateHex": "b8f6c8cbc8d5bcc7",         # 分类的 hex 编码（个人日记固定值）
    "title": title,
    "commentNum": 0,                        # 评论数
    "effect1": 65536,
    "effect2": 524294,
    "ar": 0,
    "block": 0,
    "inproc": False,
    "appeal": 0,
    "abstract": paragraphs[1][:200],        # 摘要取正文第一段前200字
    "artype": 1,
    "arUins": "",
    "blogid": blogId,
    "voteids": 0,
    "pubtime": blogId,
    "replynum": 0,
    "category": "个人日记",
    "effect": 65536,
    "exblogtype": 0,
    "sus_flag": False,
    "friendrelation": [],
    "lp_type": 0, "lp_id": 0, "lp_style": 0, "lp_flag": 0,
    "orguin": 619774944,                    # 空间主人 UIN
    "orgblogid": blogId,
    "mention_uins": [],
    "attach": [],
    "comments": [],
    "html": custom_html,
    "custom_title": title,
    "custom_html": custom_html,
    "custom_author": "作者名",              # 可选，非空间主人时添加
    "custom_visitor": {"viewCount": 50},    # 可选，阅读数
    "likeTotal": 6,                         # 可选，点赞数
    "uniKey": f"http://user.qzone.qq.com/619774944/blog/{blogId}"
}
```

### 3. 写入数据文件

```python
# 读取现有数据
with open('Blogs/json/blogs.js', 'r', encoding='utf-8') as f:
    content = f.read()
prefix = 'window.blogs = '
data = json.loads(content[len(prefix):])

# 新文章插入最前面（最新文章排第一）
data.insert(0, new_blog)

# 写回（用 compact 格式节省空间）
output = prefix + json.dumps(data, ensure_ascii=False, separators=(',', ':'))
with open('Blogs/json/blogs.js', 'w', encoding='utf-8') as f:
    f.write(output)
```

### 4. 更新首页统计

编辑 `index.html`，将日志 badge 数字 +1：

```html
日志<span class="badge badge-primary badge-pill">301</span>
```

### 5. 提交推送

```bash
git add Blogs/json/blogs.js index.html
git commit -m "Add blog: 日期 update blog count to NNN"
git push
```

## 关键注意事项

- **分类默认「个人日记」**：除非用户在提示词中明确指定其他分类，否则一律使用默认值
- **段落数与原文一致**：用户给出的每个自然段对应一个 `<div>` 元素
- **不创建单独的 HTML 文件**：文章内容全部存储在 `Blogs/json/blogs.js` 中，通过 `info.html?blogId=xxx` 动态渲染
- **不改变跳转逻辑**：列表页和详情页通过 `blogid` 字段关联，无需修改其他文件
- **作者字段**：如果作者不是空间主人，添加 `custom_author` 字段；如果与空间主人相同则不需要
- **日期修改**：直接修改对应博客对象的 `pubTime` 字段即可
- **Python 环境**：Windows 下用 `py` 命令执行脚本，脚本头部加 `# -*- coding: utf-8 -*-`
- **手动文章标记**：非QQ空间采集的文章（由AI代写等）必须添加 `"custom_source": "manual"` 字段，以便采集时识别和保护
- **校对文章标记**：校对过的文章必须添加 `"custom_proofread": true` 字段，以便重新采集时通过 merge.py 保留校对修正

## QQ空间重新采集流程

手动添加的文章不在QQ空间上，全量采集会覆盖丢失。按以下步骤操作：

```
1. py merge.py backup    ← 采集前，备份当前数据（含手动文章）
2. 打开QQ空间导出助手采集  ← 新数据会覆盖 blogs.js
3. py merge.py merge     ← 采集后，从备份提取手动文章合并回新数据
4. 更新 index.html 中的日志计数
```

- `py merge.py status` — 随时查看当前手动文章数量和备份状态
- 备份文件保存在 `Blogs/json/blogs_manual_backup.js`，不要手动删除
- 合并脚本位于项目根目录 `merge.py`
