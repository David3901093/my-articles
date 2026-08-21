# QQ空间备份站点 - 博客更新指南

## 项目结构

- `index.html` — 首页入口，包含各模块统计数字
- `Blogs/index.html` — 日志列表页（JS 动态渲染，加载 `blogs_meta.js`）
- `Blogs/info.html` — 日志详情页（`?blogId=xxx` 按需加载 `blogs/blog_{blogId}.js`）
- `Blogs/json/blogs.js` — 完整数据文件（保留用于采集兼容，不直接加载）
- `Blogs/json/blogs_meta.js` — 列表页元数据（轻量，~265KB）
- `Blogs/json/blogs/` — 每篇文章独立内容文件 `blog_{blogId}.js`
- `Blogs/js/blogs.js` — 列表页渲染逻辑
- `Blogs/js/bloginfo.js` — 详情页渲染逻辑（按需加载）
- `merge.py` — 重新采集时的手动文章合并脚本

## 新增博客文章流程

用 Python 脚本操作数据，脚本头部加 `# -*- coding: utf-8 -*-` 和 `sys.stdout.reconfigure(encoding='utf-8')`。

### 1. 准备文章数据

```python
import base64, json, time, sys, os
sys.stdout.reconfigure(encoding='utf-8')

title = "文章标题"
author = "作者名"  # 可选，非空间主人时添加
paragraphs = ["段落1", "段落2", ...]  # 每个自然段对应一个 <div>

html_parts = ['                                                <div class="blog_details_20120222">']
for p in paragraphs:
    html_parts.append('<div>' + p + '</div>')
    html_parts.append('<div><br></div>')
html_parts.pop()
html_parts.append('</div>')
html_content = ''.join(html_parts)
custom_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
blogId = int(time.time())
```

### 2. 构造博客对象

```python
new_blog = {
    "blogId": blogId, "blogType": 0,
    "pubTime": "2026-05-22 20:00", "lastModifyTime": blogId,
    "cate": "个人日记", "cateHex": "b8f6c8cbc8d5bcc7",
    "title": title,
    "commentNum": 0, "effect1": 65536, "effect2": 524294,
    "ar": 0, "block": 0, "inproc": False, "appeal": 0,
    "abstract": paragraphs[1][:200], "artype": 1, "arUins": "",
    "blogid": blogId, "voteids": 0, "pubtime": blogId, "replynum": 0,
    "category": "个人日记", "effect": 65536,
    "exblogtype": 0, "sus_flag": False,
    "friendrelation": [], "lp_type": 0, "lp_id": 0, "lp_style": 0, "lp_flag": 0,
    "orguin": 619774944, "orgblogid": blogId,
    "mention_uins": [], "attach": [], "comments": [],
    "html": custom_html, "custom_title": title, "custom_html": custom_html,
    "custom_author": author,              # 可选
    "custom_visitor": {"viewCount": 50},  # 可选
    "likeTotal": 6,                       # 可选
    "custom_source": "manual",            # AI代写文章必须
    "uniKey": f"http://user.qzone.qq.com/619774944/blog/{blogId}"
}
```

### 3. 写入三个文件（blogs.js + blogs_meta.js + blogs/blog_xxx.js）

```python
META_FIELDS = [
    'blogId', 'blogType', 'pubTime', 'lastModifyTime',
    'cate', 'cateHex', 'title', 'custom_title',
    'commentNum', 'replynum', 'category',
    'abstract', 'artype', 'blogid',
    'custom_author', 'custom_source',
    'custom_visitor', 'likeTotal', 'effect',
]

# 3a. 写入完整 blogs.js（保留用于采集兼容）
with open('Blogs/json/blogs.js', 'r', encoding='utf-8') as f:
    data = json.loads(f.read()[len('window.blogs = '):])
data.insert(0, new_blog)
with open('Blogs/json/blogs.js', 'w', encoding='utf-8') as f:
    f.write('window.blogs = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')))

# 3b. 写入元数据 blogs_meta.js
meta = [{f: b[f] for f in META_FIELDS if f in b and b[f] is not None} for b in data]
with open('Blogs/json/blogs_meta.js', 'w', encoding='utf-8') as f:
    f.write('window.blogs = ' + json.dumps(meta, ensure_ascii=False, separators=(',', ':')))

# 3c. 写入单篇内容文件
os.makedirs('Blogs/json/blogs', exist_ok=True)
with open(f'Blogs/json/blogs/blog_{blogId}.js', 'w', encoding='utf-8') as f:
    f.write('window.blogDetail = ' + json.dumps(new_blog, ensure_ascii=False, separators=(',', ':')))
```

### 4. 更新首页统计、提交推送、部署上线

```bash
# 编辑 index.html 中日志 badge 数字 +1
git add Blogs/json/blogs.js Blogs/json/blogs_meta.js Blogs/json/blogs/ index.html
git commit -m "Add blog: YYYY-MM-DD update blog count to NNN"
git push
netlify deploy --prod --dir=.
```

- Git push 到 GitHub 保留（备份），Netlify 部署通过本地 CLI 直接上传，不再依赖 GitHub 自动触发
- 站点已关联：`david-ge-and-bros-hut`（ID: `6eef1aab-7bb3-49ed-9223-6885fdf4e601`）

## 修改已有文章

```python
import base64, json, sys
sys.stdout.reconfigure(encoding='utf-8')

# 读取完整数据
with open('Blogs/json/blogs.js', 'r', encoding='utf-8') as f:
    data = json.loads(f.read()[len('window.blogs = '):])

META_FIELDS = [
    'blogId', 'blogType', 'pubTime', 'lastModifyTime',
    'cate', 'cateHex', 'title', 'custom_title',
    'commentNum', 'replynum', 'category',
    'abstract', 'artype', 'blogid',
    'custom_author', 'custom_source',
    'custom_visitor', 'likeTotal', 'effect',
]

for b in data:
    if '标题关键词' in b.get('title', ''):
        html = base64.b64decode(b['custom_html']).decode('utf-8')
        html = html.replace('旧文本', '新文本')
        b['custom_html'] = base64.b64encode(html.encode('utf-8')).decode('utf-8')
        b['html'] = b['custom_html']
        b['custom_proofread'] = True

        # 同步更新单篇内容文件
        blog_id = b.get('blogid', b.get('blogId'))
        with open(f'Blogs/json/blogs/blog_{blog_id}.js', 'w', encoding='utf-8') as f:
            f.write('window.blogDetail = ' + json.dumps(b, ensure_ascii=False, separators=(',', ':')))
        break

# 同步更新 blogs.js 和 blogs_meta.js
with open('Blogs/json/blogs.js', 'w', encoding='utf-8') as f:
    f.write('window.blogs = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')))
meta = [{f: b[f] for f in META_FIELDS if f in b and b[f] is not None} for b in data]
with open('Blogs/json/blogs_meta.js', 'w', encoding='utf-8') as f:
    f.write('window.blogs = ' + json.dumps(meta, ensure_ascii=False, separators=(',', ':')))
```

## 关键注意事项

- **分类默认「个人日记」**：除非用户明确指定
- **段落数与原文一致**：每个自然段对应一个 `<div>`
- **不创建单独 HTML 文件**：内容全部在 JS 文件中
- **作者字段**：非空间主人时添加 `custom_author`
- **手动文章标记**：AI代写等必须加 `"custom_source": "manual"`
- **校对文章标记**：校对过的文章加 `"custom_proofread": true`
- **Python 环境**：Windows 用 `py` 命令，禁止 bash 内联 `-c`（中文转义问题）
- **commit message 用英文**：Windows bash 下中文会转义失败
- **修改后同时更新 `custom_html` 和 `html` 字段**
- **写入三文件**：每次新增/修改必须同步更新 `blogs.js`、`blogs_meta.js`、`blogs/blog_{id}.js`

## 数据同步自动化规则

用户随时可能采集覆盖 blogs.js、随时粘贴文章、随时写入数据。所有同步操作全自动执行，不询问用户、不等待确认。

### 每次操作博客数据前，先跑同步检测

```python
# 自动检测并同步，每次操作博客前执行
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('Blogs/json/blogs.js', 'r', encoding='utf-8') as f:
    js_ids = set(b.get('blogId', b.get('blogid')) for b in json.loads(f.read()[len('window.blogs = '):]))
content_dir = 'Blogs/json/blogs'
existing_ids = set(int(f.replace('blog_', '').replace('.js', '')) for f in os.listdir(content_dir) if f.startswith('blog_')) if os.path.exists(content_dir) else set()
if js_ids != existing_ids:
    # 需要同步，自动执行 merge（已包含去重）
    os.system('py merge.py merge')
    # 更新 index.html 日志计数并推送
```

### 自动处理的所有场景

| 场景 | 检测方式 | 自动处理 |
|------|---------|---------|
| 采集覆盖了 blogs.js | blogId 集合与 blogs/ 目录不匹配 | merge 合并 + 去重 + 重新生成拆分文件 |
| 手动文章与采集文章重复 | merge.py 自动按 blogId 去重 | 保留较新版本，不产生重复条目 |
| 校对过的文章被采集覆盖 | merge.py 自动恢复 custom_proofread 标记的版本 | 用备份中的校对版覆盖采集版 |
| 三文件不一致 | blogs.js / blogs_meta.js / blogs/ 中 blogId 数量不同 | 以 blogs.js 为准，重新生成另外两个 |

### 关键原则

- **零交互**：检测到不同步就自动修复，不要问用户是否需要同步
- **blogs.js 为唯一数据源**：拆分文件都是从它派生的，采集覆盖后 merge 会把手动文章合并回来
- **去重逻辑**：相同 blogId 只保留一篇，手动版本优先于采集版本

## 校对规则

### 校对五层次

1. **字/标点**：字形是否正确，"的地得"混用、标点不统一（并列分句该用分号处用了逗号或句号）
2. **词**：词法是否正确，包括：
   - 词性误用（名词当动词、动词名词搭配不当，如"纠葛"→"纠缠"、"挤奶牛"→"挤牛奶"）
   - 近音/近义字误用（如"经"与"仅"、"品味"与"品位"）
   - 感情色彩是否符合作者意图（如"固执"与"执着"、"狡猾"与"机智"）
3. **句**：语法与语义，包括：
   - 冗余助词（多余的"的""了""着"）、连词堆叠、代词冗余、主语缺失（尤其跨句号省略）
   - 搭配不当、逻辑连词准确性（"虽然…但是"与"尽管…却"语气轻重不同）
   - 句意常识：语义是否自洽、符合常理
   - 语义歧义：同一句子是否存在两种合理解读，上下文能否消歧，无法判断时标记与用户讨论
4. **段落结构**：梳理段落内的时间线/逻辑线，检查连接词（如果、然后、紧接着等）是否与骨架一致，是否存在虚假的时间推进或逻辑断裂
5. **整篇通读**：以读者视角审查全文，关注叙事节奏、情感弧线、段落过渡、前后文一致性（如人物描写前后矛盾）

### 修改原则

- **只改语法句式，不改变作者原意**，不揣度添加词句
- **不拘泥于单字**，整个短语或句式需要调整就调整
- **以下内容不予修改**：专有名词、专业术语、颜文字/表情、修辞手法（拈连、通感、拟人、比喻等）、作者有意的口语化表达和节奏处理
- **识别并尊重作者风格**：校对前先扫描语言风格特征（语体、修辞偏好、句式节奏、口吻、颜文字使用习惯），修改时以此为基线。拿不准是"风格"还是"语病"时，标记与用户讨论，不擅自判断

### 校对讨论流程

当用户提出语法疑问时，禁止直接改，按以下流程：

1. 读取文章，定位句子
2. **输出完整句子及上下文**，让用户阅读原文感受语感
3. 分析问题，给出诊断
4. **输出修改后的完整句子及上下文**，让用户再次阅读确认
5. 确认后执行修改，自动 commit → push → `netlify deploy --prod --dir=.`

## QQ空间重新采集流程

手动文章不在QQ空间上，全量采集会覆盖丢失：

```
1. py merge.py backup     ← 采集前备份（blogs.js + 拆分文件）【必做，否则 merge 无可合】
2. 打开QQ空间导出助手采集  ← 新数据会覆盖 blogs.js
3. py merge.py merge      ← 从备份合并回手动文章 + 重新生成拆分文件 + 自动更新 index.html 日志计数
4. py custom_restore.py   ← 恢复自定义资产（见下节）
5. netlify deploy --prod --dir=.
```

- `py merge.py status` — 查看当前手动文章数量和备份状态
- `py merge.py restore` — 万一 merge 出问题，直接恢复拆分文件（不出问题时不需要）
- 备份文件：`Blogs/json/blogs_manual_backup.js`，不要手动删除

## 自定义资产保护（2026-08-21 起）

重新采集除覆盖文章数据外，还可能覆盖站点模板文件。以下自定义资产已建立保护，恢复入口统一为 `py custom_restore.py`（幂等）：

| 资产 | 内容 | 保护机制 |
|---|---|---|
| 手动文章数据 | 16 篇「开发手记」存档（第一至十五期＋提纲笔记，custom_source=manual）＋ 7 篇既有手动文章 | merge.py backup/merge 流程 |
| CSS 自定义样式块 | `Common/css/common.css` 末尾约 150 行存档长文排版（标题/引用/表格/终端风代码块/图片居中） | `_custom/custom-css-block.css` + custom_restore.py 字节级追回 |
| 存档配图 | `Blogs/images/ep*-flow-*.png`（14 张，第九期 2 张源文件缺失待补，补齐时同时放 `_custom/images/`） | `_custom/images/` + custom_restore.py |
| 首页日志计数 | index.html 徽章 | merge.py 自动更新 + custom_restore.py 校验 |

终极兜底是 git（仓库已推 GitHub；代理 `git config --global http.https://github.com.proxy http://127.0.0.1:7892`）：任何文件被覆盖后 `git checkout -- <文件>` 可恢复。详见 `_custom/README.md`。
