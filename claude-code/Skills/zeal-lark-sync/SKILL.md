---
name: zeal-lark-sync
description: 同步社群成员档案到飞书，建立云盘原始备份和多维表格查询入口。当用户提到"上传档案到飞书"、"同步到多维表格"、"备份成员数据"、"创建飞书查询表"、"lark 同步"时触发本 Skill。
---

# zeal-lark-sync

## 触发条件

当用户需要以下操作时触发本 Skill：
- "上传档案到飞书" / "同步到飞书"
- "创建多维表格" / "同步到多维表格"
- "备份成员数据" / "云盘备份"
- "创建飞书查询表" / "lark 同步"
- "将 mining 结果导入飞书"

## 概述

本 Skill 将 `docs/member-profiles/` 下的成员档案（`.md` + `index.json`）同步到飞书，形成**云盘原始备份 + 多维表格主查询入口**的双轨架构。

**核心机制**：
- 云盘：原始 `.md` 文件备份，保留完整 frontmatter
- 多维表格：主查询入口，含结构化字段 + 完整档案正文
- 全部字段使用 text/number 类型，避免 select/multiSelect 的选项限制
- JSON 通过文件中转传递，避免换行符截断

## 前置依赖

- `lark-cli` 已安装且认证通过（`lark-cli doctor` 返回 ok）
- `docs/member-profiles/index.json` 和 `.md` 档案已生成

## 配置管理

配置存储在工作路径的 `docs/zeal-lark-sync/context/upload-config.md` 中。
**Agent 应自动获取 token**，仅在获取失败时才提示用户手动填写。

### Token 自动获取流程

INIT 阶段 Agent 按以下步骤自动获取配置：

1. 检查 `docs/zeal-lark-sync/context/upload-config.md` 是否存在
2. 如存在，提取已有 token（用 `grep` 或 Python 解析）
3. 如缺失 `folder_token`：
   - 运行 `lark-cli drive folder create --name "成员档案备份" --parent-position my_library`
   - 从 JSON 输出提取 `folder_token`（取最后一行可解析的 JSON）
4. 如缺失 `base_token`：
   - 运行 `lark-cli base +base-create --name "社群成员档案"`
   - 从 JSON 输出提取 `base_token`
5. 如缺失 `members_table_id` 或 `sessions_table_id`：
   - 运行 `lark-cli base +table-list --base-token <base_token>`
   - 如已有对应表名，提取 table_id
   - 如无，提示用户在 Base 中手动创建表（lark-cli 的 table-create 不稳定）
6. 将获取到的 token 写入 `upload-config.md`

### 配置解析

Agent 读取配置时，使用以下命令快速提取：
```bash
python3 -c "import re; text=open('docs/zeal-lark-sync/context/upload-config.md').read(); print({m.group(1): m.group(2).strip().strip('\"').strip(\"'\") for m in re.finditer(r'^([a-z_]+):\\s*(.+)$', text, re.M)})"
```

## 状态机

```
[INIT] → [UPLOAD_DRIVE] → [CREATE_BASE] → [IMPORT_DATA] → [VERIFY] → [DONE]
```

### 状态说明

| 状态 | 说明 | 输入 | 输出 |
|------|------|------|------|
| INIT | 环境检查，读取/创建配置 | 用户指令 | `upload-config.md` |
| UPLOAD_DRIVE | 云盘上传原始 `.md` | `.md` 文件 | 云盘 file_token 映射 |
| CREATE_BASE | 创建/确认多维表格结构 | 配置 token | 成员总表 + 活动记录表 |
| IMPORT_DATA | 批量导入成员和活动数据 | `index.json` + `.md` | 50 条成员 + 10 条活动 |
| VERIFY | 验证数据完整性 | 表格数据 | 验证报告 |
| DONE | 完成 | - | 最终报告 |

## 流程编排

### INIT — 环境检查与配置

1. 运行 `lark-cli doctor` 确认认证状态
2. 检查 `docs/zeal-lark-sync/context/` 目录是否存在，如不存在则创建
3. 尝试读取 `docs/zeal-lark-sync/context/upload-config.md`
4. **自动获取缺失 token**（参见「配置管理」→「Token 自动获取流程」）
5. 全部 token 就绪后进入 UPLOAD_DRIVE

### UPLOAD_DRIVE — 云盘上传

参考 `upload/SKILL.md` 执行：
- 遍历 `docs/member-profiles/*.md`
- 调用 `upload.py` 批量上传到云盘文件夹
- 记录每个文件的 `file_token`（用于「原始文件」字段）

### CREATE_BASE — 多维表格初始化

参考 `table/SKILL.md` 执行：
- 检查 Base 中是否已有「成员总表」和「活动记录」
- 如无，创建表和字段（全部 text/number 类型）

**成员总表字段**：
| 字段名 | 类型 | 说明 |
|--------|------|------|
| 昵称 | text | 主键，canonical_name |
| 行业 | text | |
| 岗位 | text | |
| 标签 | text | 顿号分隔 |
| 参与期数 | number | |
| 首次参与 | text | |
| 最近参与 | text | |
| 角色历史 | text | 格式：期数:角色;... |
| 置信度 | text | 极高/高/中/低 |
| 档案文档 | text | 飞书文档 URL（可选） |
| 原始文件 | text | 云盘文件 URL |
| 档案内容 | text | 完整 Markdown 正文（无 frontmatter） |

**活动记录表字段**：
| 字段名 | 类型 | 说明 |
|--------|------|------|
| 期数 | text | 如「第一期」|
| 日期 | text | |
| 主题 | text | |
| 参与人数 | number | |
| 领航员 | text | |
| 主持人 | text | |
| 状态 | text | 已处理/待处理 |

### IMPORT_DATA — 数据导入

参考 `table/SKILL.md` 执行：
- 调用 `import.py` 读取 `index.json` 和 `.md` 文件
- 成员数据分批导入（每批 5 条，sleep 5s 限流）
- 活动记录一次性导入（10 条以内无需分批）
- **关键**：JSON 必须通过临时文件中转，使用 `$(cat file.json)` 方式传给 `lark-cli`

### VERIFY — 验证

1. 检查成员总表记录数 == `index.json` 中 members 数量
2. 检查活动记录表记录数 == `index.json` 中 sessions 数量
3. 抽查 3 个成员的「档案内容」长度 > 500 字符
4. 抽查「原始文件」URL 格式正确（含 file_token）

## 子 Skill 引用

| 子 Skill | 路径 | 职责 |
|----------|------|------|
| Upload Agent | `upload/SKILL.md` | 云盘上传、文件管理 |
| Table Agent | `table/SKILL.md` | 多维表格创建、数据导入 |

## 关键经验（必读）

1. **不要直接使用 docs +create --content**：v2 API 有兼容性问题，创建的文档内容为空
2. **batch create JSON 必须文件中转**：含换行符的长文本直接通过 subprocess 传参会被截断
3. **不要用 record-upsert 做批量更新**：未指定 `--record-id` 时会创建重复记录
4. **全部用 text 字段**：select/multiSelect 有选项值预定义限制，text 最可靠
5. **档案内容字段存完整正文**：让用户在表格内直接查看档案，无需跳转
