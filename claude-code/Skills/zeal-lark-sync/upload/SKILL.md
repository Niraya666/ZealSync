---
name: zeal-lark-sync-upload
description: 将社群成员档案的 .md 文件批量上传到飞书云盘，作为原始备份。本 Skill 由 zeal-lark-sync 主 Skill 在 UPLOAD_DRIVE 阶段调用。
---

# zeal-lark-sync-upload

## 职责

- 遍历 `docs/member-profiles/*.md`
- 批量上传到飞书云盘指定文件夹
- 记录 file_token，生成 `{name: file_token}` 映射

## 输入

- `docs/zeal-lark-sync/context/upload-config.md` — 含 `folder_token`
- `docs/member-profiles/*.md` — 成员档案源文件

## 输出

- 云盘文件上传结果
- 终端输出 `NAME:file_token` 格式，供主 Skill 解析

## 工作流

### 1. 读取配置

从 `docs/zeal-lark-sync/context/upload-config.md` 读取 `folder_token`。如缺失，报错并提示先运行 INIT 阶段。

### 2. 调用 upload.py

```bash
python3 .claude/skills/zeal-lark-sync/upload/upload.py \
  --md-dir docs/member-profiles \
  --folder-token <FOLDER_TOKEN>
```

### 3. Frontmatter 转换

`upload.py` 在上传前自动将 YAML frontmatter 转换为 Markdown 表格：

**转换规则**：
- `---` 包裹的 YAML 块 → `| 属性 | 内容 |` 开头的 Markdown 表格
- 列表值（如 `tags: [a, b, c]`）→ 顿号分隔的纯文本（`a、b、c`）
- 引号包裹的字符串 → 去掉引号

**示例**：
```markdown
---
name: Shawn
description: 咨询管理创始人
tags: [咨询管理, 创始人, AI]
---
```

转换为：
```markdown
| 属性 | 内容 |
|------|------|
| name | Shawn |
| description | 咨询管理创始人 |
| tags | 咨询管理、创始人、AI |

# Identity
...
```

转换后的临时文件上传到云盘，原始 `.md` 文件不受影响。

### 4. 解析输出

`upload.py` 输出格式：
```
OK:<name>:<file_token>
FAIL:<name>:<error_message>
```

收集所有 `OK` 行，将 `{name: file_token}` 映射传递给主 Skill，用于后续「原始文件」字段回填。

### 5. 错误处理

- 单文件上传失败：记录错误，继续处理剩余文件
- 全部失败：终止并报告
- 部分成功：报告成功/失败数量，由主 Skill 决定是否继续

## 速率限制

- 连续上传间隔 >= 1.2 秒
- 单文件失败时重试 1 次，间隔 2 秒
