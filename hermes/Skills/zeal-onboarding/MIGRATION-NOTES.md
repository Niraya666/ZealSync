# Hermes Onboarding Skill 迁移说明

## 迁移概览

将 `claude-code/Skills/zeal-onboarding/` 迁移到 `hermes/Skills/zeal-onboarding/`，适配 Hermes Agent 的工具和特性。

## 分支

`feature/hermes-onboarding` (from `develop`)

## 文件映射

| 源文件 (claude-code) | 目标文件 (hermes) | 改动类型 |
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
  - 从 "claude-code 读取 `~/.claude/projects/` 下 project 类型 memory"
  - 改为 "Hermes 通过 `session_search` 和 `memory` 工具读取历史记忆"
- Step 3 (interview): 更新对话工具描述
  - 从 "通过 `AskUserQuestion` 分轮次补充"
  - 改为 "通过 `clarify` 工具分轮次补充"

**可直接移植**: 状态机、流程编排、文件约定、YAML frontmatter 格式

### 2. init/SKILL.md — 无修改

lark-cli 的安装和认证检查完全通用，无需修改。

### 3. extract/SKILL.md — 中度修改

**改动点**：
- Harness 检测表: 更新 Hermes 检测方式描述
  - 添加 "支持 `memory` / `session_search` / `clarify` 工具"
- Memory 提取表: 添加 Hermes 行
  - 来源: `~/.hermes/memories/` 下的记忆文件 + 历史会话
  - 提取方式: `memory` / `session_search` 工具（而非直接文件读取）
  - 内容: 用户偏好、项目经验、兴趣、工作风格
- 新增 "Hermes 特殊说明" 段落
  - 说明 Hermes 的 memory 系统通过工具访问
  - 列出具体工具: `memory(action="read")` 和 `session_search(query="...")`

**可直接移植**: harness 检测逻辑、隐私过滤原则、社交媒体补充策略、草稿生成逻辑

### 4. interview/SKILL.md — 重度修改

**改动点**（核心差异）:
- **AskUserQuestion → clarify 工具**
  - Claude-code 的 `AskUserQuestion` 是内置函数式调用，Agent 直接在对话中提问
  - Hermes 的 `clarify` 是显式 tool call，需要在 SKILL.md 中描述调用方式
- 新增 "Hermes 的 `clarify` 工具说明" 段落
  - 说明两种模式: 多选 / 开放式
  - 明确 interview 场景使用开放式 clarify
- 每轮对话从 "自然语言描述" 改为 "`clarify` 工具调用示例"
  - 例如: `clarify(question="为了帮你创建...")`

**可直接移植**: 差距分析逻辑、轮次设计主题、跳过策略、标签生成、错误处理

### 5. hitl/SKILL.md — 轻度修改

**改动点**：
- 路径更新: `./claude-code/Skills/...` → `./hermes/Skills/...`
- 提示文本: "回到 Claude Code 对话窗口" → "回到 Hermes 对话"

**可直接移植**: 本地保存服务、HTML 生成、浏览器打开、上传飞书、错误处理

### 6. hitl/hitl-template.html — 轻度修改

**改动点**：
- 提示文本: "回到 Claude Code 对话窗口" → "回到 Hermes 对话"

### 7. evals/evals.json — 轻度修改

**改动点**：
- eval 1: 更新期望输出描述（Hermes harness、clarify 工具）
- eval 1 expectations: "AskUserQuestion" → "clarify 工具"

## 关键差异总结

| 方面 | Claude-code | Hermes |
|---|---|---|
| 对话收集 | `AskUserQuestion` (内置) | `clarify` (显式 tool call) |
| Memory 读取 | 直接文件系统读取 | `memory` / `session_search` 工具 |
| Skill 格式 | Markdown + YAML frontmatter | Markdown + YAML frontmatter (相同) |
| 路径结构 | `~/.claude/skills/` | `~/.hermes/skills/` |
| HTML 预览 | 通用 | 通用（仅需修改提示文本） |
| 飞书上传 | 通用 lark-cli | 通用 lark-cli |

## 安装方式

将 `hermes/Skills/zeal-onboarding/` 复制到 Hermes 的 skills 目录：

```bash
cp -r /path/to/ZealSync/hermes/Skills/zeal-onboarding \
      ~/.hermes/skills/zeal-onboarding
```

在 Hermes 对话中加载 skill：
```
/skill zeal-onboarding
```

或启动时预加载：
```bash
hermes -s zeal-onboarding
```
