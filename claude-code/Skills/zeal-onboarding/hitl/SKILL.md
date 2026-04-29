---
name: zeal-onboarding-hitl
description: ZealSync onboarding HITL 确认与提交。生成 HTML 预览，引导用户确认，上传至飞书文档。
---

# ZealSync Onboarding — HITL

## 职责

- 读取完善的 `USER.md`
- 生成美观的 HTML 预览页面
- 自动在浏览器中打开
- 引导用户确认或提出修改
- 确认后上传至飞书文档

## 流程

### 1. 生成 HTML 预览

**模板文件位置**：`hitl/hitl-template.html`（与 `SKILL.md` 同级目录）

**生成流程**：

1. 读取模板文件 `hitl/hitl-template.html`
2. 替换以下占位符：

| 占位符 | 替换内容 |
|---|---|
| `{{NICKNAME}}` | 用户昵称 |
| `{{DESCRIPTION}}` | YAML frontmatter 中的 description |
| `{{TIMESTAMP}}` | 当前时间 |
| `{{TAGS_HTML}}` | 标签渲染为 `<span class="tag">...</span>` |
| `{{SECTIONS_HTML}}` | 各 Section 渲染为 `<div class="section">...</div>` |
| `{{RAW_MARKDOWN}}` | 完整的 USER.md Markdown 原文（用于 textarea） |

3. 保存到 `./USER-profile/[nickname]/hitl-preview.html`

**Section 渲染规则**：

将 USER.md 中每个 Section 转换为 HTML：
```html
<div class="section">
  <h2>Section 标题</h2>
  <div>Section 内容（Markdown 转 HTML）</div>
</div>
```

- 空内容显示为 `<span class="pending">待补充</span>`
- 列表保持 `<ul>` / `<li>` 结构
- 代码块用 `<pre>` 包裹

**模板维护**：
- 修改样式或布局时，只需编辑 `hitl-template.html`
- `SKILL.md` 中不包含 HTML 代码，只描述替换逻辑

### 2. 打开浏览器

运行：
```bash
open ./USER-profile/[nickname]/hitl-preview.html
```

### 3. 等待用户确认

在对话中询问：

> 已在浏览器中打开你的画像预览，底部提供了 Markdown 编辑区。
>
> **确认方式（三选一）**：
> 1. 回复 **"确认提交"** — 保持当前版本直接上传
> 2. **粘贴修改后的完整 Markdown** — 在浏览器中编辑后复制，粘贴回对话
> 3. 回复 **"需要修改：[具体描述]"** — 告诉我改哪里，我来帮你改

### 4. 处理用户输入

**情况 A：用户回复 "确认提交"**
→ 直接进入 Step 5（选择上传位置）

**情况 B：用户粘贴了完整 Markdown**
→ 检测到输入内容包含 YAML frontmatter（`---`）和 Section headers：
1. 将粘贴的内容覆盖写入 `USER.md`
2. 向用户确认："检测到完整的画像内容，是否以此版本提交？"
3. 用户确认后进入 Step 5

**情况 C：用户描述具体修改（如"What I'm Looking For 里加上 xxx"）**
→ 直接在 `USER.md` 中应用修改
→ 重新生成 HTML 预览
→ 再次打开浏览器等待确认
→ 最多允许 **3 轮修改**，超过则建议完成后再更新

### 5. 选择上传位置

在确认提交前，询问用户希望上传到飞书的哪个位置：

> 你希望将画像上传到飞书的哪个位置？
> 1. **个人知识库**（默认，我的空间 › 知识库）
> 2. **指定文件夹**（提供 folder token）
> 3. **指定 Wiki 空间**（提供 space ID）

根据用户选择：

| 选项 | 命令参数 |
|---|---|
| 个人知识库 | `--parent-position my_library` |
| 指定文件夹 | `--parent-token {{folder_token}}` |
| 指定 Wiki | `--wiki-space {{space_id}}` |

如用户选择了文件夹或 Wiki 但无法提供 token，先执行：
```bash
# 搜索可用的 Wiki 空间
lark-cli wiki spaces list --format pretty

# 或搜索文件夹
lark-cli drive file list --params '{"folder_token":"root"}' --format pretty
```

### 6. 上传飞书文档

用户确认后，执行上传。注意以下要点：

**路径规则**：必须使用**相对路径**，先 `cd` 到 USER.md 所在目录再执行命令。

```bash
# 先进入文件所在目录（关键：lark-cli 要求相对路径）
cd ./USER-profile/{{nickname}}

# 创建飞书文档（默认上传到个人知识库）
lark-cli docs +create \
  --api-version v2 \
  --title "ZealSync Profile — {{nickname}}" \
  --content @USER.md \
  --doc-format markdown \
  --parent-position my_library
```

如需上传到指定位置，替换 `--parent-position` 为对应的参数：
- 指定文件夹：`--parent-token {{folder_token}}`
- 指定 Wiki：`--wiki-space {{space_id}}`

**从输出中提取**：
- `document_token` — 文档唯一标识
- `url` — 文档访问链接

如需要更新已存在的文档：
```bash
cd ./USER-profile/{{nickname}}
lark-cli docs +update \
  --api-version v2 \
  --doc {{document_token}} \
  --markdown @USER.md \
  --mode overwrite
```

**常见错误处理**：
- `invalid file path` → 确认使用了相对路径 `@USER.md` 而非绝对路径
- `Untitled` 文件名 → 确认传了 `--title` 参数
- 文件未出现在预期位置 → 确认传了 `--parent-position` 或对应路径参数

### 7. 完成标记

- 将文档 URL 记录到 `.state.json`
- 更新 `USER.md` 中的 Metadata：
  - `Confirmation Status: confirmed`
  - `Doc URL: {{url}}`
  - `Doc Token: {{token}}`
- 向用户展示：
  > 画像已提交至飞书！文档链接：[url]
  > 你可以随时说"更新我的画像"来修改。

## 输出

更新 `.state.json`：
```json
{
  "status": "completed",
  "nickname": "...",
  "docUrl": "https://...",
  "docToken": "...",
  "completedAt": "2026-04-28T...",
  "version": "v1.0.0"
}
```

## 错误处理

- 飞书 API 失败：保存 `USER.md` 到本地，提示用户稍后手动上传
- HTML 生成失败：退化为 Markdown 预览，直接在对话中展示
- 浏览器打开失败：提示用户手动打开 HTML 文件路径
