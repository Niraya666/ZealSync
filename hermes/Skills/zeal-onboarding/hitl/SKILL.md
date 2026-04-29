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

### 1. 启动本地保存服务（优先方案）

**前置检测**：检查系统是否有 Python 3

```bash
which python3 || which python || echo "NO_PYTHON"
```

- **有 Python**：启动本地保存服务 `save-server.py`
- **无 Python**：退回到方案 A（VS Code 直接编辑）

**启动服务**：

```bash
# 启动后台 server，自动选择可用端口
python3 ./hermes/Skills/zeal-onboarding/hitl/save-server.py \
  ./USER-profile/{{nickname}}/USER.md \
  > /tmp/zeal-server-{{nickname}}.log 2>&1 &

SERVER_PID=$!

# 等待 server 启动并获取端口
sleep 1
SERVER_PORT=$(grep "SERVER_PORT:" /tmp/zeal-server-{{nickname}}.log | head -1 | cut -d: -f2)
```

**保存服务说明**：
- 零第三方依赖，仅使用 Python 标准库
- 监听随机可用端口，避免冲突
- 接收 POST `/save` 请求，将内容写入指定文件路径
- CORS 已配置，支持 file:// 页面的跨域请求

**无 Python 时的降级方案**：

如系统无 Python，跳过 HTML 预览，直接执行：

```bash
open ./USER-profile/{{nickname}}/USER.md
```

用户用系统默认编辑器（VS Code / Typora 等）编辑并保存后，回到对话中确认。

### 2. 生成 HTML 预览

**模板文件位置**：`hitl/hitl-template.html`

**生成流程**：

1. 读取模板文件 `hitl/hitl-template.html`
2. 替换占位符：

| 占位符 | 替换内容 |
|---|---|
| `{{NICKNAME}}` | 用户昵称 |
| `{{DESCRIPTION}}` | YAML frontmatter 中的 description |
| `{{TIMESTAMP}}` | 当前时间 |
| `{{TAGS_HTML}}` | 标签渲染为 `<span class="tag">...</span>` |
| `{{SECTIONS_HTML}}` | 各 Section 渲染为 `<div class="section">...</div>` |
| `{{RAW_MARKDOWN}}` | 完整的 USER.md Markdown 原文 |
| `{{SERVER_PORT}}` | 本地保存服务的端口号 |

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

**保存交互逻辑**：

浏览器中的"保存"按钮执行：
1. `fetch('http://localhost:{{SERVER_PORT}}/save')` POST 修改后的内容
2. Server 直接写入 `./USER-profile/{{nickname}}/USER.md`
3. 无路径选择弹窗，一键保存到默认位置
4. 如 server 不可用，自动降级为文件下载

### 3. 打开浏览器

```bash
open ./USER-profile/{{nickname}}/hitl-preview.html
```

### 4. 等待用户确认

在对话中询问：

> 已在浏览器中打开你的画像预览，底部提供了 Markdown 编辑区。
>
> **操作方式**：
> 1. 在浏览器中直接编辑，点击"保存"自动覆盖 `USER.md`
> 2. 回到 Hermes 对话中回复 **"已保存"** 或 **"确认提交"**
> 3. 如需 Agent 帮忙修改，回复 **"需要修改：[具体描述]"**

### 5. 处理用户输入

**情况 A：用户回复 "确认提交" 或 "已保存"**
→ 读取 `./USER-profile/[nickname]/USER.md` 最新内容
→ 关闭本地保存服务：`kill $SERVER_PID`
→ 进入 Step 6（选择上传位置）

**情况 B：用户描述具体修改**
→ 直接在 `USER.md` 中应用修改
→ 重新生成 HTML 预览
→ 再次打开浏览器等待确认
→ 最多允许 **3 轮修改**

### 6. 选择上传位置

**默认策略**：优先使用「个人知识库」(`--parent-position my_library`)，避免额外 OAuth scope 授权。

在确认提交前询问：

> 你希望将画像上传到飞书的哪个位置？
> 1. **个人知识库**（推荐默认，无需额外授权）
> 2. **指定文件夹**（需 `space:document:retrieve` scope，可能触发额外授权）
> 3. **指定 Wiki 空间**（需 space ID）

根据用户选择：

| 选项 | 命令参数 |
|---|---|
| 个人知识库 | `--parent-position my_library` |
| 指定文件夹 | `--parent-token {{folder_token}}` |
| 指定 Wiki | `--wiki-space {{space_id}}` |

如用户选择了文件夹但无法提供 token，执行：
```bash
# 搜索可用的文件夹
lark-cli drive files list --params '{"folder_token":"root"}' --format pretty
```

### 7. 构造上传文件

Lark v2 API 不支持 `--title` 参数，需通过 content 中的 H1 设置文档标题。同时，YAML frontmatter 会被 Lark 解析为正文内容，上传前需剥离。

**构造步骤**：

```bash
cd ./USER-profile/{{nickname}}

# Step 1: 剥离 frontmatter，添加 H1 标题
python3 -c "
import re
with open('USER.md', 'r') as f:
    content = f.read()

# 去掉 frontmatter
content = re.sub(r'^---\n.*?\n---\n+', '', content, flags=re.DOTALL)

# 在开头添加 H1 标题
content = '# ZealSync Profile — {{nickname}}\n\n' + content

with open('USER-lark.md', 'w') as f:
    f.write(content)
"
```

生成的 `USER-lark.md`：
- 不含 YAML frontmatter
- 以 `# Title` 开头，作为文档显示标题
- 保留所有 Section 正文

### 8. 上传飞书文档

**路径规则**：使用相对路径，先 `cd` 到文件所在目录。

```bash
cd ./USER-profile/{{nickname}}

# 创建飞书文档
lark-cli docs +create \
  --api-version v2 \
  --content @USER-lark.md \
  --doc-format markdown \
  --parent-position my_library
```

**设置文档元数据标题**（文档列表、浏览器标签中显示）：
```bash
# 获取 document_token 从上一步输出
lark-cli drive files patch \
  --params '{"file_token":"DOC_TOKEN","type":"docx"}' \
  --data '{"new_title":"ZealSync Profile — {{nickname}}"}' \
  --yes
```

**如需更新已存在的文档**：
```bash
cd ./USER-profile/{{nickname}}
lark-cli docs +update \
  --api-version v2 \
  --doc {{document_token}} \
  --markdown @USER-lark.md \
  --mode overwrite
```

**常见错误处理**：
- `invalid file path` → 确认使用了相对路径 `@USER-lark.md` 而非绝对路径
- `Untitled` 文件名 → 确认 `USER-lark.md` 以 `# Title` 开头
- 权限不足 → 如使用「指定文件夹」，运行 `lark-cli auth login --scope "space:document:retrieve"` 补充授权

### 9. 完成标记

- 关闭本地保存服务（如仍在运行）：`kill $SERVER_PID 2>/dev/null || true`
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
