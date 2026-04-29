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
| **claude-code** | 存在 `CLAUDE.md` 上下文、支持 `AskUserQuestion`、有 `~/.claude/` 目录 |
| **codex** | 环境变量 `CODEX_*` 或特定 CLI 特征 |
| **openClaw** | 存在 `claw` 相关上下文或环境变量 |
| **Hermes** | 存在 `hermes` 相关上下文 |

检测逻辑：
1. 检查环境变量（`CODEX_*`, `HERMES_*`, `CLAW_*`）
2. 检查文件系统特征（`~/.claude/`, `~/.claw/`, `~/.hermes/`）
3. 通过对话确认："你当前正在使用哪个 Agent 工具？"

## Memory 提取

### claude-code

**检测**：检查 `~/.claude/projects/` 目录是否存在。

**提取前必须征得用户同意**：

> "检测到你正在使用 claude-code。我可以读取你本地 `~/.claude/projects/` 下的 project 类型 memory 文件，从中提取你的技能、项目经验和兴趣领域来初始化画像。
>
> **是否同意读取？**（同意 / 跳过 / 只读取特定项目）"

用户同意后，执行：
```bash
find ~/.claude/projects -name "*.md" -path "*/memory/*" 2>/dev/null
```

提取规则：
- 只读取 `type: project` 的 memory（排除 `feedback`、`user` 等个人偏好）
- 优先读取最近 90 天内的 memory
- 使用 subagent 并行分析多个 memory 文件，每个文件提取与画像相关的要点

提取维度：
- 用户技能、项目经验 → `# What I Can Offer`
- 用户兴趣领域 → `# What I Do & Build`
- 踩坑记录中的背景信息 → `# Identity`
- 工作风格和偏好 → `# My Style & Interests`

### openClaw

**检测**：检查 `~/.openclaw/workspace/USER.md` 是否存在。

**提取前必须征得用户同意**：

> "检测到你可能使用 openClaw，默认画像位置为 `~/.openclaw/workspace/USER.md`。
>
> **是否同意读取作为初始化原料？**（同意 / 跳过）"

用户同意后读取并解析，归入对应 Section。

### Hermes

**检测**：检查 `~/.hermes/memories/USER.md` 是否存在。

**提取前必须征得用户同意**：

> "检测到你可能使用 Hermes，默认画像位置为 `~/.hermes/memories/USER.md`。
>
> **是否同意读取作为初始化原料？**（同意 / 跳过）"

用户同意后读取并解析，归入对应 Section。

### 多 Harness 并行分析

如用户同意使用多个 harness 的信息来源，启动多个 subagent 并行分析：
- Subagent A: 分析 claude-code memory → 输出要点
- Subagent B: 分析 openClaw USER.md（`~/.openclaw/workspace/USER.md`） → 输出要点
- Subagent C: 分析 Hermes USER.md（`~/.hermes/memories/USER.md`） → 输出要点

汇总所有要点，去重后按 Section 归类。

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
- `WebFetch` 面临反爬机制，稳定性和成功率不可控
- MVP 阶段优先保证核心流程可用，外部信息抓取延后到 Phase-1

处理方式：
- 收集用户提供的所有链接
- 将链接原样归入 `# Metadata & External Context` 的 `External Links` 列表
- 标记为 `[用户提供的参考链接，待后续抓取]`

## 生成 USER.md 草稿

基于提取的信息，生成 `USER.md.draft`：

```markdown
---
name: {{从 Identity 中提取的 nickname，或询问用户}}
description: {{一句话自我介绍，基于 What I Do 生成}}
rule: {{如有匹配规则，填写}}
tags: [{{自动提取的关键词标签}}]
---

# Identity
_Who are you? Core identity, Background, location, MBTI._

{{提取的信息，或占位符}}

# What I Do & Build
_What do you currently spend time on? Role, domain, topics, and recent focus. building or exploring?, collaborator needs, and project-specific asks_

{{提取的信息，或占位符}}

# What I Can Offer
_What can you actively provide to others? Skills, expertise, resources, network, and time._

{{提取的信息，或占位符}}

# What I'm Looking For
_What would make you say "yes" to a connection? Current matching intents, ideal people, opportunities, outcomes, and boundaries._

{{提取的信息，或占位符}}

# My Style & Interests
_How do you prefer to connect and collaborate?. Availability, communication preferences, working style, constraints, and contact permissions._

{{提取的信息，或占位符}}

# Metadata & External Context
_Profile version, generation info, data lineage, confirmation status, freshness, and visibility rules. What external evidence or context should be considered? Links, summaries, key takeaways, and source notes._

- Version: draft-v1
- Generated: {{timestamp}}
- Sources: [{{memory 来源列表}}]
- External Links: [{{社交媒体链接}}]
```

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
