# Codex Onboarding Skill 迁移说明

## 迁移概览

将 `openClaw/Skills/zeal-onboarding/` 迁移到 `codex/Skills/zeal-onboarding/`，适配 Codex 的 workspace-first 工作方式、技能安装目录和权限确认机制。

## 分支

`codex/codex-onboarding-skills` (from `main`)

## 文件映射

| 源文件 (openClaw) | 目标文件 (codex) | 改动类型 |
|---|---|---|
| `SKILL.md` | `SKILL.md` | 中度修改 |
| `init/SKILL.md` | `init/SKILL.md` | 轻度修改 |
| `extract/SKILL.md` | `extract/SKILL.md` | 重度修改 |
| `interview/SKILL.md` | `interview/SKILL.md` | 轻度修改 |
| `hitl/SKILL.md` | `hitl/SKILL.md` | 中度修改 |
| `hitl/hitl-template.html` | `hitl/hitl-template.html` | 轻度修改 |
| `hitl/generate-preview.py` | `hitl/generate-preview.py` | 轻度修改 |
| `hitl/save-server.py` | `hitl/save-server.py` | 无修改（直接复制） |
| `user-profile-template.md` | `user-profile-template.md` | 无修改（直接复制） |
| `evals/evals.json` | `evals/evals.json` | 轻度修改 |

## 详细改动分析

### 1. SKILL.md (主入口)

**改动点**：
- description 改为 Codex 可触发格式，强调创建、更新、确认和提交 ZealSync 社群画像
- Step 2 (extract): 当前 harness 改为 Codex，优先读取当前 workspace 与用户提供资料
- Step 3 (interview): 明确 Codex 通过自然对话补充信息
- Step 4 (hitl): 不再默认 `open <html-file>`，优先使用 Codex Browser 或返回本地 HTML 绝对路径
- 新增 Codex 特性约定：源文件位于 `codex/Skills/`，安装目录为 `~/.agents/skills/`

### 2. init/SKILL.md

**改动点**：
- description 改为 Codex 触发语义
- 增加 Codex 权限说明：安装 CLI、打开浏览器授权、写入用户主目录或运行联网命令前先说明目的并确认

### 3. extract/SKILL.md

**核心差异**：
- Codex 没有统一的可读用户 memory 数据库，因此以当前 workspace 为主
- `.agents/skills/` 是技能目录，不应当作个人画像来源
- 读取 `~/.claude/`、`~/.openclaw/`、`~/.hermes/` 等其他 harness 目录前必须获得用户明确同意
- 多来源合并默认在当前 Codex 对话中完成，只有用户明确授权并且当前会话支持并行 agent 时才使用 subagent

**Codex 来源优先级**：

| 优先级 | 来源 | 用途 |
|---|---|---|
| 1 | 用户直接回答或粘贴资料 | 核心画像内容 |
| 2 | `./USER-profile/**/USER.md` | 更新或续写既有画像 |
| 3 | `./docs/member-profiles/*.md` | 参考社群画像格式，需用户确认对应本人或可复用 |
| 4 | 其他 harness memory | 仅在用户授权后读取 |

### 4. interview/SKILL.md

Codex 与 OpenClaw 都是自然对话，不需要显式 `clarify` 或 `AskUserQuestion` 工具。Codex 版补充：
- 每轮最多 3 个问题
- 已经充实的 Section 直接跳过
- 只有影响匹配质量的关键信息才追问

### 5. hitl/SKILL.md

**改动点**：
- 路径更新：`./openClaw/Skills/...` → `./codex/Skills/...`
- 浏览器打开策略：优先 Codex Browser；不可用则返回 HTML 绝对路径；需要系统 GUI `open` 时先确认权限
- Lark 上传仍保留相对路径 `@USER-lark.md` 规则，以规避 `lark-cli docs +create` 的绝对路径问题

### 6. hitl/generate-preview.py

**改动点**：
- HTML 输出对 nickname、description、tags、sections 和原始 Markdown 做 escaping，避免用户画像内容破坏预览页结构

### 7. evals/evals.json

**改动点**：
- eval 1 更新为 Codex harness
- 增加对"读取其他 harness 前先取得用户同意"和"优先 Codex Browser 或返回 HTML 路径"的期望

## 关键差异总结

| 方面 | OpenClaw | Codex |
|---|---|---|
| 对话收集 | 自然对话 | 自然对话 |
| 当前记忆来源 | `~/.openclaw/workspace/USER.md` + memory 文件 | 当前 workspace、既有 profile、用户粘贴资料 |
| 技能安装目录 | `~/.openclaw/workspace/skills/` | `~/.agents/skills/` |
| 本地预览 | 可直接打开浏览器 | 优先 Codex Browser 或返回 HTML 绝对路径 |
| 权限处理 | harness 自身能力 | 遵循 Codex sandbox / approval 机制 |

## 安装方式

将 `codex/Skills/zeal-onboarding/` 复制到 Codex 的 skills 目录：

```bash
mkdir -p ~/.agents/skills
cp -r /path/to/ZealSync/codex/Skills/zeal-onboarding \
      ~/.agents/skills/zeal-onboarding
```

在 Codex 对话中使用任意触发词：

- "帮我创建社群画像"
- "生成 USER.md"
- "ZealSync onboarding"
- "我要加入社群"
- "创建我的画像"
- "更新我的画像"
