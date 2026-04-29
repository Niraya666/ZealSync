---
name: zeal-onboarding-extract
description: ZealSync onboarding 信息提取。检测当前 harness，读取已有 memory，可选抓取社交媒体信息，生成 USER.md 草稿。
---

# ZealSync Onboarding — Extract

## 职责

- 检测当前运行的 harness
- 从各 harness 的 memory 中提取用户信息作为初始化原料
- 可选：抓取社交媒体链接补充外部上下文
- 输出初步的 USER.md 草稿

## Harness 检测

通过以下特征判断当前 harness：

| Harness | 检测方式 |
|---|---|
| **claude-code** | 存在 `CLAUDE.md` 上下文、有 `~/.claude/` 目录 |
| **codex** | 环境变量 `CODEX_*` 或特定 CLI 特征 |
| **openClaw** | 存在 `~/.openclaw/workspace/` 目录、支持 `memory_search` / `memory_get` 工具 |
| **Hermes** | 存在 `~/.hermes/` 目录、支持 `clarify` 工具 |

检测逻辑：
1. 检查环境变量（`CODEX_*`, `HERMES_*`, `CLAW_*`）
2. 检查文件系统特征（`~/.claude/`, `~/.claw/`, `~/.hermes/`）
3. 通过对话确认："你当前正在使用哪个 Agent 工具？"

## Memory 提取流程

### Step 1: 检测当前使用的 Harness

通过环境变量和文件系统特征判断：

```bash
# 检查各 harness 特征
ls ~/.claude/projects/ 2>/dev/null && echo "HAS_CLAUDE_CODE"
ls ~/.openclaw/workspace/USER.md 2>/dev/null && echo "HAS_OPENCLAW"
ls ~/.hermes/memories/ 2>/dev/null && echo "HAS_HERMES"
```

### Step 2: 提取当前 Harness 的 Memory

**当前 harness 优先提取**，作为画像的主要原料。

根据检测结果，向用户确认：

> "检测到你正在使用 **{当前 harness}**。我可以读取该 harness 下已有的画像/记忆数据来初始化你的社群画像。
>
> **是否同意读取？**（同意 / 跳过）"

**各 harness 提取方式**：

| Harness | 提取来源 | 提取方式 | 提取内容 |
|---|---|---|---|
| **claude-code** | `~/.claude/projects/**/memory/*.md`（`type: project`） | 文件读取 | 技能、项目经验、兴趣、工作风格 |
| **openClaw** | `~/.openclaw/workspace/USER.md` + `memory/*.md` | `memory_search` / `memory_get` 工具 | 用户画像、记忆、历史上下文 |
| **Hermes** | `~/.hermes/memories/` 下的记忆文件 + 历史会话 | `memory` / `session_search` 工具 | 用户偏好、项目经验、兴趣、工作风格 |

**OpenClaw 特殊说明**：

OpenClaw 的 memory 系统通过工具访问：
- 使用 `memory_search(query="...")` 搜索历史记忆
- 使用 `memory_get(path="...")` 读取特定记忆文件
- 使用 `read(path="~/.openclaw/workspace/USER.md")` 读取用户画像
- 提取时注意过滤敏感信息，仅保留可用于画像构建的内容

### Step 3: 提取其他 Harness 的 Memory

当前 harness 提取完成后，询问：

> "除了 **{当前 harness}**，你是否还使用了其他 Agent 工具？我可以从多个来源整合信息，让画像更完整。
>
> 检测到的其他来源：{claude-code / openClaw / Hermes / ...}
>
> **选择要补充的来源**（可多选）：
> - [ ] openClaw (`~/.openclaw/workspace/USER.md`)
> - [ ] Hermes (`~/.hermes/memories/`)
> - [ ] 跳过，只用当前 harness 的数据"

如用户选择了其他 harness，依次征得同意并提取。

### Step 4: 汇总去重与隐私过滤

如使用了多个 harness 的信息来源，启动 subagent 并行分析，汇总所有要点，按 Section 归类并去重。

**隐私过滤原则（强制）**：
从 memory 提取时，必须过滤以下敏感信息，不得写入 USER.md：
- **真实姓名** → 仅保留 nickname/化名
- **公司/组织全称** → 可保留行业或领域描述（如"某 AI 创业公司"→"AI 领域"），不得保留具体公司名
- **手机号、邮箱、身份证号** → 完全丢弃
- **具体地址** → 仅保留城市级别（如"北京"、"上海"），丢弃街道/门牌号
- **未公开的项目/客户名称** → 用泛化描述替代

提取维度映射：
- 用户技能、项目经验 → `# What I Can Offer`
- 用户兴趣领域 → `# What I Do & Build`
- 背景信息（昵称、角色、城市、MBTI 等） → `# Identity`
- 工作风格和偏好 → `# My Style & Interests`

## 社交媒体补充（可选）

询问用户是否愿意提供社交媒体链接来丰富画像：

> "你可以提供社交媒体链接，作为画像的外部参考。是否愿意提供以下任意链接？
> - 小红书主页
> - LinkedIn 个人页
> - 个人博客
> - 微信公众号文章
> - GitHub 主页
> - Twitter/X 主页"

**MVP 版本策略**：只保留链接，不做抓取。

原因：
- 外部网页抓取面临反爬机制，稳定性和成功率不可控
- MVP 阶段优先保证核心流程可用，外部信息抓取延后到 Phase-1

处理方式：
- 收集用户提供的所有链接
- 将链接原样归入 `# Metadata & External Context` 的 `External Links` 列表
- 标记为 `[用户提供的参考链接，待后续抓取]`

## 生成 USER.md 草稿

基于提取的信息，生成 `USER.md.draft`。

模板参见同目录下的 `user-profile-template.md`。生成时：
- `Version` 填 `draft-v1`
- `Confirmation Status` 填 `pending`
- 所有占位符用提取到的内容填充，未提取到的保留占位符或留空
- 严格遵守[隐私过滤原则](#step-4-汇总去重与隐私过滤)

## 输出

保存到 `./USER-profile/[nickname]/USER.md.draft`

返回：
```json
{
  "draftPath": "./USER-profile/[nickname]/USER.md.draft",
  "sectionsFilled": ["Identity", "What I Can Offer"],
  "sectionsEmpty": ["What I'm Looking For", "My Style & Interests"],
  "externalSources": ["linkedin.com/in/xxx", "github.com/xxx"]
}
```
