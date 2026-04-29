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

将 `USER.md` 渲染为 HTML 文件：

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>ZealSync 画像预览 — {{nickname}}</title>
  <style>
    body { font-family: -apple-system, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #333; }
    h1 { border-bottom: 2px solid #0066ff; padding-bottom: 10px; }
    h2 { color: #0066ff; margin-top: 30px; font-size: 1.2em; }
    .meta { color: #666; font-size: 0.9em; margin-bottom: 20px; }
    .section { margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; }
    .pending { color: #999; font-style: italic; }
    .tag { display: inline-block; background: #0066ff; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.85em; margin: 2px; }
    .actions { position: fixed; bottom: 20px; right: 20px; }
    .btn { padding: 10px 24px; border: none; border-radius: 6px; cursor: pointer; font-size: 1em; }
    .btn-primary { background: #0066ff; color: white; }
    .btn-secondary { background: #e0e0e0; color: #333; margin-right: 10px; }
  </style>
</head>
<body>
  <h1>{{nickname}} 的社群画像</h1>
  <div class="meta">{{description}} | 版本: v1.0.0 | 生成时间: {{timestamp}}</div>
  <div class="tags">{{#each tags}}<span class="tag">{{this}}</span>{{/each}}</div>

  <div class="section">
    <h2>Identity</h2>
    <div>{{identity_content}}</div>
  </div>

  <!-- 其他 Section 类似 -->

  <div class="actions">
    <button class="btn btn-secondary" onclick="window.close()">关闭预览</button>
  </div>

  <div style="margin-top: 40px; padding: 20px; background: #fff3cd; border-radius: 8px;">
    <strong>请回到 Claude Code 对话中确认</strong><br>
    在对话中回复："确认提交" 或 "需要修改：[具体修改内容]"
  </div>
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

> 已在浏览器中打开你的画像预览，请查看。
>
> 如果确认无误，回复 **"确认提交"**。
> 如果需要修改，请告诉我具体要改哪里（例如："What I'm Looking For 里加上 xxx"）。

### 4. 处理修改请求

如用户提出修改：
- 直接在 `USER.md` 中应用修改
- 重新生成 HTML 预览
- 再次打开浏览器等待确认
- 最多允许 **3 轮修改**，超过则建议完成后再更新

### 5. 上传飞书文档

用户确认后，执行上传：

```bash
# 创建飞书文档
lark-cli docs +create \
  --api-version v2 \
  --title "ZealSync Profile — {{nickname}}" \
  --content @./USER-profile/[nickname]/USER.md \
  --doc-format markdown
```

从输出中提取：
- `document_token` — 文档唯一标识
- `url` — 文档访问链接

如需要更新已存在的文档：
```bash
lark-cli docs +update \
  --api-version v2 \
  --doc {{document_token}} \
  --markdown @./USER-profile/[nickname]/USER.md \
  --mode overwrite
```

### 6. 完成标记

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
