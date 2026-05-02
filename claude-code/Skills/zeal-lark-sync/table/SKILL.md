---
name: zeal-lark-sync-table
description: 创建飞书多维表格并批量导入社群成员档案数据。本 Skill 由 zeal-lark-sync 主 Skill 在 CREATE_BASE 和 IMPORT_DATA 阶段调用。
---

# zeal-lark-sync-table

## 职责

- 检查并创建「成员总表」和「活动记录」表
- 批量导入成员数据（含完整 Markdown 正文）
- 批量导入活动记录数据

## 输入

- `docs/zeal-lark-sync/context/upload-config.md` — 含 `base_token`
- `docs/member-profiles/index.json` — 成员索引和活动记录
- `docs/member-profiles/*.md` — 成员档案源文件（用于「档案内容」字段）
- `{name: file_token}` 映射 — 来自 Upload Agent（用于「原始文件」字段）

## 输出

- 多维表格记录
- 终端输出导入进度和统计

## 工作流

### 1. 读取配置

从 `docs/zeal-lark-sync/context/upload-config.md` 读取 `base_token`。如缺失，报错并提示先运行 INIT 阶段。

### 2. 检查/创建表格

使用 `lark-cli base +table-list` 检查是否已有「成员总表」和「活动记录」。

如不存在：
- 创建「成员总表」：使用 `import.py --create-members-table`
- 创建「活动记录」：使用 `import.py --create-sessions-table`

### 3. 导入成员数据

```bash
python3 .claude/skills/zeal-lark-sync/table/import.py \
  --base-token <BASE_TOKEN> \
  --members-table <TABLE_ID> \
  --index docs/member-profiles/index.json \
  --md-dir docs/member-profiles \
  --file-map <file_map_json>
```

### 4. 导入活动记录

```bash
python3 .claude/skills/zeal-lark-sync/table/import.py \
  --base-token <BASE_TOKEN> \
  --sessions-table <TABLE_ID> \
  --index docs/member-profiles/index.json \
  --import-sessions
```

### 5. 解析输出

`import.py` 输出格式：
```
批次 1: 成功 5 条
批次 2: 成功 5 条
...
总计导入: 50/50
```

## 关键约束

- **batch size = 5**，sleep 5 秒，避免限流
- **JSON 必须文件中转**：`import.py` 内部将 payload 写入 `/tmp/batch-{n}.json`，通过 `$(cat file)` 传给 lark-cli
- **全部字段用 text/number**，不用 select/multiSelect
- **档案内容**从 `.md` 读取，去掉 frontmatter

## 字段设计

### 成员总表

| 字段名 | 类型 | 来源 |
|--------|------|------|
| 昵称 | text | index.json canonical_name |
| 行业 | text | index.json industry |
| 岗位 | text | index.json role |
| 标签 | text | index.json tags（顿号分隔）|
| 参与期数 | number | index.json session_count |
| 首次参与 | text | index.json first_session |
| 最近参与 | text | index.json last_session |
| 角色历史 | text | index.json session_roles（格式：期数:角色;...）|
| 置信度 | text | index.json alignment_confidence |
| 档案文档 | text | 飞书文档 URL（可选）|
| 原始文件 | text | 云盘文件 URL（来自 upload.py）|
| 档案内容 | text | .md 正文（去掉 frontmatter）|

### 活动记录表

| 字段名 | 类型 | 来源 |
|--------|------|------|
| 期数 | text | index.json sessions.phase |
| 日期 | text | sessions.date |
| 主题 | text | sessions.topic |
| 参与人数 | number | sessions.participants_count |
| 领航员 | text | sessions.navigator |
| 主持人 | text | sessions.host |
| 状态 | text | 已处理 |
