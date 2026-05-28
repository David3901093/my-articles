# QQ空间备份站

基于 [QQ空间导出助手](https://github.com/ShunCai/QZoneExport) 导出的个人空间数据，部署为静态网站。

## 项目结构

```
.
├── index.html              # 首页（各模块统计数字）
├── merge.py                # 重新采集后的合并脚本
├── Blogs/
│   ├── index.html          # 日志列表页
│   ├── info.html           # 日志详情页（?blogId=xxx）
│   ├── json/blogs.js       # 所有日志数据（JSON）
│   └── js/                 # 列表页 & 详情页渲染逻辑
├── Messages/               # 说说
├── Albums/                 # 相册
├── Videos/                 # 视频
├── Boards/                 # 留言板
├── Diaries/                # 日记
├── Friends/                # 好友
├── Visitors/               # 访客
├── Shares/                 # 分享
├── Favorites/              # 收藏
├── Statistics/             # 统计
└── Common/                 # 公共资源（CSS、JS、图片）
```

## 日志数据说明

所有日志内容存储在 `Blogs/json/blogs.js` 中，格式为：

```javascript
window.blogs = [
  {
    "blogId": 1747929600,
    "pubTime": "2026-05-22 20:00",
    "title": "文章标题",
    "html": "Base64编码的HTML内容",
    "custom_source": "manual",       // 手动添加的文章（非QQ空间采集）
    "custom_proofread": true,         // 已校对的文章
    ...
  },
  ...
]
```

文章按 `pubTime` 降序排列（最新在前）。

## 重新采集流程（重要）

手动添加的文章和校对过的文章不在QQ空间上，全量采集会覆盖丢失。**每次重新采集必须按以下三步操作：**

```
第1步：py merge.py backup     ← 采集前，备份当前数据
第2步：用QQ空间导出助手采集    ← 新数据会覆盖 blogs.js
第3步：py merge.py merge      ← 采集后，自动合并恢复
```

### merge.py 做了什么？

- **备份（backup）**：把当前 `blogs.js` 复制一份到 `blogs_manual_backup.js`
- **合并（merge）**：从备份中找出需要保护的文章，合并到新采集的数据中
  - 带 `custom_source: "manual"` 的文章 → 追加回新数据（AI代写等非QQ空间文章）
  - 带 `custom_proofread: true` 的文章 → 用备份版本覆盖新数据中的原始版本（保留校对修正）
  - **所有文章按日期降序排列**，不按来源分组

### 其他命令

```bash
py merge.py status     # 查看当前手动文章数量和备份状态
```

## 技术栈

- 纯静态站点，无需后端
- jQuery + Bootstrap 4
- 文章内容 Base64 编码存储在 JSON 中，前端动态渲染
