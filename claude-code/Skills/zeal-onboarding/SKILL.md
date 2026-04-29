---
name: zeal-onboarding
description: >
  ZealSync 社群画像 Onboarding Skill。引导用户完成对话式信息收集，
  生成结构化的 USER.md 社群画像，并上传至飞书文档。
  触发词："创建社群画像"、"生成 USER.md"、"ZealSync onboarding"、
  "我要加入社群"、"创建我的画像"。
---

# ZealSync Onboarding

## 触发条件

用户说出以下任意一种表达时触发：

- "帮我创建社群画像"
- "生成 USER.md"
- "ZealSync onboarding"
- "我要加入社群"
- "创建我的画像"
- "更新我的画像"

## 前置检查

1. 检查 `./USER-profile/` 目录是否存在
2. 若存在，读取 `./USER-profile/.state.json` 判断当前状态
3. 若状态为 `completed` 且 `USER.md` 存在，询问用户是"重新生成"还是"更新画像"

## 状态机

| 状态 | 含义 | 下一步动作 |
|---|---|---|
| `none` / 文件不存在 | 全新用户 | 从 Step 1 (init) 开始 |
| `initialized` | 环境检查通过 | 从 Step 2 (extract) 开始 |
| `extracted` | 已有信息提取完成 | 从 Step 3 (interview) 开始 |
| `interviewed` | 对话问答完成 | 从 Step 4 (hitl) 开始 |
| `completed` | 画像已生成并提交 | 询问更新或退出 |

## 执行流程

### Step 0: 状态判定

读取 `./USER-profile/.state.json`：

- 不存在 → 创建目录 `./USER-profile/`，写入初始状态 `{"status": "none"}`，进入 Step 1
- `status: none` → 进入 Step 1
- `status: initialized` → 进入 Step 2
- `status: extracted` → 进入 Step 3
- `status: interviewed` → 进入 Step 4
- `status: completed` → 询问是否更新，若否退出，若是重置为 `none` 重新执行

### Step 1: init（环境检查）

调用 `init/SKILL.md`：

- 检查 `lark-cli` 是否已安装（`which lark-cli`）
- 运行 `lark-cli doctor` 验证 auth 和 connectivity
- 如检查失败，引导用户完成安装和 OAuth 授权
- 成功后更新 `.state.json`: `{"status": "initialized"}`

### Step 2: extract（信息提取）

调用 `extract/SKILL.md`：

- 检测当前 harness（通过环境变量或会话特征判断）
- 询问用户是否愿意提供其他 harness 的 memory 作为初始化原料
- 从各 harness 的 memory 中提取已有用户信息（claude-code 读取 `~/.claude/projects/` 下 project 类型 memory）
- 可选：询问社交媒体链接，使用 subagent 抓取并摘要
- 输出：初步的 USER.md 草稿（YAML frontmatter + 各 Section 内容）
- 保存草稿到 `./USER-profile/[nickname]/USER.md.draft`
- 更新 `.state.json`: `{"status": "extracted"}`

### Step 3: interview（对话完善）

调用 `interview/SKILL.md`：

- 输入：extract 生成的 `USER.md.draft`
- 对比 USER.md 模板，找出缺失或不足的 Section
- 通过 `AskUserQuestion` 分轮次补充，尽量控制在 **5 轮以内**
- 每轮聚焦一个主题（如 Identity → What I Do → What I Can Offer → What I'm Looking For → My Style）
- 允许用户说"跳过"或"稍后补充"
- 输出：完善的 USER.md 内容
- 保存到 `./USER-profile/[nickname]/USER.md`
- 更新 `.state.json`: `{"status": "interviewed"}`

### Step 4: hitl（确认与提交）

调用 `hitl/SKILL.md`：

- 输入：完善的 `USER.md`
- 生成 HTML 预览文件（包含样式化的画像展示）
- 自动调用 `open <html-file>` 在浏览器中打开
- 用户可以在浏览器中查看，回到对话中确认或提出修改
- 若需修改，返回 Step 3（interview）或直接在对话中修正
- 确认后：
  1. 通过 `lark-cli docs +create --api-version v2 --content @USER.md --doc-format markdown` 创建飞书文档
  2. 获取返回的文档 token/URL，记录到 `.state.json`
  3. 删除草稿文件 `USER.md.draft`
  4. 更新 `.state.json`: `{"status": "completed", "docUrl": "...", "completedAt": "..."}`
- 向用户展示飞书文档链接，恭喜完成 onboarding

## 错误处理

- 任何步骤失败，记录错误到 `.state.json` 的 `lastError` 字段
- 下次触发时，先读取 `lastError`，询问用户是否从失败处重试
- 用户可随时说"跳过此步"进入下一步

## 文件约定

| 路径 | 用途 |
|---|---|
| `./USER-profile/.state.json` | 流程状态持久化 |
| `./USER-profile/[nickname]/USER.md` | 最终画像文件 |
| `./USER-profile/[nickname]/USER.md.draft` | 中间草稿 |
| `./USER-profile/[nickname]/hitl-preview.html` | HTML 预览文件 |

## YAML Frontmatter 格式

参见同目录下的 `user-profile-template.md` 模板文件。
