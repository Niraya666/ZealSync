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

将 `USER.md` 渲染为 HTML 文件。页面分为两部分：上半部分展示渲染后的画像，下半部分提供 Markdown 编辑区。

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>ZealSync 画像预览 — {{nickname}}</title>
  <style>
    body { font-family: -apple-system, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #333; }
    h1 { border-bottom: 2px solid #0066ff; padding-bottom: 10px; }
    h2 { color: #0066ff; margin-top: 30px; font-size: 1.2em; }
    .meta { color: #666; font-size: 0.9em; margin-bottom: 20px; }
    .section { margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; }
    .pending { color: #999; font-style: italic; }
    .tag { display: inline-block; background: #0066ff; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.85em; margin: 2px; }
    .editor-section { margin-top: 40px; border-top: 3px solid #0066ff; padding-top: 20px; }
    .editor-section h2 { color: #333; margin-bottom: 10px; }
    .editor-section p { color: #666; font-size: 0.9em; margin-bottom: 15px; }
    textarea { width: 100%; min-height: 500px; font-family: 'Menlo', 'Monaco', monospace; font-size: 13px; line-height: 1.5; padding: 15px; border: 1px solid #ddd; border-radius: 8px; resize: vertical; }
    .btn { padding: 10px 24px; border: none; border-radius: 6px; cursor: pointer; font-size: 1em; margin-top: 15px; }
    .btn-primary { background: #0066ff; color: white; }
    .btn-secondary { background: #e0e0e0; color: #333; margin-right: 10px; }
    .feedback { color: #28a745; margin-left: 10px; display: none; font-weight: 500; }
    .hint-box { margin-top: 20px; padding: 15px; background: #e7f3ff; border-radius: 8px; border-left: 4px solid #0066ff; }
    .hint-box code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
  </style>
</head>
<body>
  <!-- 上半部分：渲染后的画像 -->
  <h1>{{nickname}} 的社群画像</h1>
  <div class="meta">{{description}} | 版本: v1.0.0 | 生成时间: {{timestamp}}</div>
  <div class="tags">{{#each tags}}<span class="tag">{{this}}</span>{{/each}}</div>

  <div class="section">
    <h2>Identity</h2>
    <div>{{identity_content}}</div>
  </div>

  <!-- 其他 Section 渲染类似 -->

  <!-- 下半部分：Markdown 编辑区 -->
  <div class="editor-section">
    <h2>编辑画像（Markdown）</h2>
    <p>直接在下方修改 Markdown 内容，改完后点击"复制"，然后粘贴回 Claude Code 对话中。</p>

    <textarea id="markdown-editor">{{raw_markdown_content}}</textarea>

    <div>
      <button class="btn btn-primary" onclick="copyMarkdown()">复制修改后的内容</button>
      <span class="feedback" id="copy-feedback">已复制到剪贴板！</span>
    </div>

    <div class="hint-box">
      <strong>如何使用：</strong>
      <ol>
        <li>在上方文本框中编辑你的画像（支持 Markdown 语法）</li>
        <li>点击"复制修改后的内容"按钮</li>
        <li>回到 Claude Code 对话窗口，粘贴内容并发送</li>
        <li>Agent 会自动应用你的修改</li>
      </ol>
      <p>或者直接回复 <code>确认提交</code> 保持当前版本不变。</p>
    </div>
  </div>

  <script>
    function copyMarkdown() {
      const textarea = document.getElementById('markdown-editor');
      textarea.select();
      try {
        document.execCommand('copy');
        const feedback = document.getElementById('copy-feedback');
        feedback.style.display = 'inline';
        setTimeout(() => { feedback.style.display = 'none'; }, 2000);
      } catch (err) {
        alert('复制失败，请手动按 Ctrl+C / Cmd+C 复制');
      }
    }
  </script>
</body>
</html>
```

保存到 `./USER-profile/[nickname]/hitl-preview.html`

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
