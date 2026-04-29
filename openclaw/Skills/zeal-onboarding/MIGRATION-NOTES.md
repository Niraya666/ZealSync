# OpenClaw Onboarding Skill 迁移说明

## 迁移概览

将 `hermes/Skills/zeal-onboarding/` 迁移到 `openclaw/Skills/zeal-onboarding/`，适配 OpenClaw Agent 的工具和特性。

## 分支

`feature/openclaw-onboarding` (from `develop`)

## 文件映射

| 源文件 (hermes) | 目标文件 (openclaw) | 改动类型 |
|---|---|---|
| `SKILL.md` | `SKILL.md` | 轻度修改 |
| `init/SKILL.md` | `init/SKILL.md` | 无修改（直接复制） |
| `extract/SKILL.md` | `extract/SKILL.md` | 中度修改 |
| `interview/SKILL.md` | `interview/SKILL.md` | 重度修改 |
| `hitl/SKILL.md` | `hitl/SKILL.md` | 轻度修改 |
| `user-profile-template.md` | `user-profile-template.md` | 无修改（直接复制） |
| `hitl/hitl-template.html` | `hitl/hitl-template.html` | 轻度修改 |
| `hitl/save-server.py` | `hitl/save-server.py` | 无修改（直接复制） |
| `evals/evals.json` | `evals/evals.json` | 轻度修改 |

## 详细改动分析

### 1. SKILL.md (主入口) — 轻度修改

**改动点**：
- Step 2 (extract): 更新 memory 提取方式描述
  - 从 "Hermes 通过 `session_search` 和 `memory` 工具读取历史记忆"
  - 改为 "OpenClaw 通过 `memory_search` 和 `memory_get` 工具读取历史记忆"
- Step 3 (interview): 更新对话方式描述
  - 从 "通过 `clarify` 工具分轮次补充"
  - 改为 "通过自然对话分轮次补充"

**可直接移植**: 状态机、流程编排、文件约定、YAML frontmatter 格式

### 2. init/SKILL.md — 无修改

lark-cli 的安装和认证检查完全通用，无需修改。

### 3. extract/SKILL.md — 中度修改

**改动点**：
- Harness 检测表: 更新 OpenClaw 检测方式描述
  - 添加 "存在 `~/.openclaw/workspace/` 目录、支持 `memory_search` / `memory_get` 工具"
- Memory 提取表: 添加 OpenClaw 行
  - 来源: `~/.openclaw/workspace/USER.md` + `memory/*.md`
  - 提取方式: **文件直接读取（优先）**，辅以 `memory_search` / `memory_get` 工具
  - 内容: 用户画像、记忆、历史上下文
- 新增 "OpenClaw 特殊说明" 段落
  - 说明 OpenClaw 可直接读取文件，与 Hermes 必须通过工具访问不同
  - 列出具体方式: `read()` 直接读取 + `memory_search()` / `memory_get()` 搜索补充

**可直接移植**: harness 检测逻辑、隐私过滤原则、社交媒体补充策略、草稿生成逻辑

### 4. interview/SKILL.md — 重度修改

**改动点**（核心差异）:
- **clarify → 自然对话**
  - Hermes 的 `clarify` 是显式 tool call，需要在 SKILL.md 中描述调用方式
  - OpenClaw 使用直接对话交互，Agent 直接向用户提问，用户直接回复
- 移除 "Hermes 的 `clarify` 工具说明" 段落
- 每轮对话从 "`clarify` 工具调用示例" 改回 "自然语言提问"

**可直接移植**: 差距分析逻辑、轮次设计主题、跳过策略、标签生成、错误处理

### 5. hitl/SKILL.md — 轻度修改

**改动点**：
- 路径更新: `./hermes/Skills/...` → `./openclaw/Skills/...`
- 提示文本: "回到 Hermes 对话" → "回到对话中"

**可直接移植**: 本地保存服务、HTML 生成、浏览器打开、上传飞书、错误处理

### 6. hitl/hitl-template.html — 轻度修改

**改动点**：
- 提示文本: "回到 Hermes 对话窗口" → "回到对话中"

### 7. evals/evals.json — 轻度修改

**改动点**：
- eval 1: 更新期望输出描述（OpenClaw harness、自然对话）
- eval 1 expectations: "clarify 工具" → "自然对话"

## 关键差异总结

| 方面 | Hermes | OpenClaw |
|---|---|---|
| 对话收集 | `clarify` (显式 tool call) | 自然对话（用户直接回复） |
| Memory 读取 | `memory` / `session_search` 工具 | **文件直接读取** + `memory_search` / `memory_get` 工具补充 |
| Skill 格式 | Markdown + YAML frontmatter | Markdown + YAML frontmatter (相同) |
| 路径结构 | `~/.hermes/skills/` | `~/.openclaw/workspace/skills/` |
| HTML 预览 | 通用 | 通用（仅需修改提示文本） |
| 飞书上传 | 通用 lark-cli | 通用 lark-cli |

## 安装方式

将 `openclaw/Skills/zeal-onboarding/` 复制到 OpenClaw 的 skills 目录：

```bash
cp -r /path/to/ZealSync/openclaw/Skills/zeal-onboarding \
      ~/.openclaw/workspace/skills/zeal-onboarding
```

OpenClaw 会自动识别 skills 目录下的 skill，无需额外加载命令。

## 与 Claude-code 版本的关系

| 方面 | Claude-code | OpenClaw |
|---|---|---|
| 对话收集 | `AskUserQuestion` (内置函数) | 自然对话（直接交互） |
| Memory 读取 | 直接文件系统读取 | **文件直接读取** + `memory_search` / `memory_get` 工具补充 |
| Skill 格式 | Markdown + YAML frontmatter | Markdown + YAML frontmatter (相同) |

OpenClaw 版本在对话交互方式上与 claude-code 更接近（都是直接对话，而非显式工具调用），但在 memory 读取方式上与 Hermes 更接近（都使用工具而非直接文件读取）。
