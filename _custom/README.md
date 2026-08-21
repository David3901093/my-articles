# _custom · 自定义资产保险柜

本目录存放 QQ 空间采集工具不会生成、但可能在重新采集时被覆盖的自定义资产。
恢复入口：`py custom_restore.py`（项目根目录，幂等，可重复运行）。

## 资产清单

- `custom-css-block.css` — `Common/css/common.css` 末尾的自定义排版样式块（标题/引用/表格/代码块/图片居中，含精确的 CRLF 前置分隔）。恢复脚本检测标记 `/* ===== 日志正文排版`，缺失则按字节级追回。
- `images/` — 开发手记存档的配图（ep11~ep14 各期 flow-N.png）。恢复脚本把 `_custom/images/` 中站点 `Blogs/images/` 缺失的图拷回。
- 第九期两张图（ep09-flow-1.png、ep09-flow-2.png）目前源文件缺失，**拿到后请同时放入 `Blogs/images/` 与本目录 `images/`**，一并纳入保护。

## 保护范围一览（哪些靠什么机制）

| 资产 | 保护机制 |
|---|---|
| 16 篇开发手记存档 + 7 篇既有手动文章（blogs.js 三文件） | `py merge.py backup`（采集前快照）＋ `py merge.py merge`（采集后按 custom_source=manual 合回）；merge 已自动改回 index.html 计数 |
| 自定义 CSS 样式块 | 本目录 + `py custom_restore.py` |
| 存档配图 | 本目录 images/ + `py custom_restore.py` |
| 全部文件 | git 仓库（已推 GitHub，终极兜底：`git checkout -- <文件>`） |

## 重新采集标准流程

```
1. py merge.py backup      ← 采集前快照（必做，否则 merge 无可合）
2. 打开 QQ 空间导出助手采集
3. py merge.py merge       ← 合回手动文章 + 重新生成拆分文件 + 自动更新计数
4. py custom_restore.py    ← 恢复 CSS 样式块 + 缺失配图 + 校验计数与存档篇数
5. netlify deploy --prod --dir=.
```
