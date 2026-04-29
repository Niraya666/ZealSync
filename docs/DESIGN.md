# ZealSync 设计文档

> 为 Agent 设计产品，而不仅仅只是为人。
> 拥抱新的交互模式，from GUI to CLI。Agent = 市场入口。

---

## 一、项目目的

### 1.1 核心命题

**ZealSync 是一个面向 Agent 时代的社群信息撮合系统。**

传统的社群信息匹配依赖人工标签、表单填写和人工撮合，存在以下痛点：
- **填写门槛高**：用户需要主动填写大量结构化信息，多数人中途放弃
- **信息滞后**：个人资料一旦填写很少更新，无法反映当前状态
- **匹配粗糙**：基于关键词的匹配无法理解真实意图（"我想找做 AI 的人"≠"我想找懂大模型微调的人"）
- **隐私困境**：要么暴露过多个人信息，要么信息不足导致匹配失败

ZealSync 的解决思路是：**让 Agent 成为信息收集、理解、匹配的全流程中介**，人类只需要在关键节点做确认（HITL）。

### 1.2 核心场景

| 场景 | 描述 | 示例 |
|---|---|---|
| **组队** | 项目合作、活动组织、兴趣小组 | "找一个懂 React 的前端，一起做个 side project" |
| **Coffee-chat** | 经验交流、职业咨询、社交破冰 | "想和做过出海产品的 PM 聊聊市场策略" |
| **信息匹配** | 基于技能、兴趣、目标的人群推荐 | "推荐 3 个对 AI Agent 感兴趣且周末有空的成员" |

### 1.3 用户旅程（完整版）

```
Phase-0: 信息获取与上传
├─ 1. Onboarding：Agent 通过对话收集用户画像
├─ 2. 信息补充：用户提供社交媒体/博客链接（可选）
├─ 3. Agent 理解：解析多源信息，构建结构化画像
└─ 4. HITL 确认：用户查看、修改、确认画像内容

Phase-1: 匹配与撮合
├─ 5. 匹配推荐：Agent 自动发现潜在匹配对象
├─ 6. 双向确认：双方 Agent 交换信息，人类确认
└─ 7. 促成连接：提供联系方式 / 安排会议

Phase-2: 持续运营
├─ 8. 画像更新：Agent 定期回访，更新用户状态
└─ 9. 社群洞察：生成社群能力地图、热点趋势
```

### 1.4 设计哲学

| 原则 | 含义 |
|---|---|
| **MVP First** | Phase-0 只做最核心的信息整合获取，不扩展边缘功能 |
| **Harness Isolation** | 不同 harness 的 skills 完全隔离，禁止跨目录引用 |
| **Skill 驱动** | 每个功能模块封装为独立 skill，遵循 `/skill-creator` 规范 |
| **渐进迭代** | 每个 Phase 结束前必须完成画像数据的端到端闭环验证 |
| **隐私优先** | 主动过滤敏感信息，仅保留 nickname 与泛化描述 |
| **Agent-First** | 产品设计首先考虑 Agent 的交互方式，而非人类 GUI |

---

## 二、Skills 工作方式

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      用户 (Human)                            │
│         触发词 → 对话交互 → 确认/修改 → 查看结果              │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Agent (Harness)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  claude-code │  │   Hermes     │  │    Codex     │ ...  │
│  │   SKILL.md   │  │   SKILL.md   │  │   SKILL.md   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
          └────────────┬────┴─────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  子 Skills (统一结构)                         │
│  ┌────────┐ ┌─────────┐ ┌───────────┐ ┌──────────┐         │
│  │  init  │ │ extract │ │ interview │ │   hitl   │         │
│  │ 环境检查│ │信息提取 │ │ 对话完善  │ │ 确认提交 │         │
│  └────────┘ └─────────┘ └───────────┘ └──────────┘         │
└─────────────────────────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                      外部服务                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐          │
│  │ lark-cli │  │  Browser │  │ Memory (各Agent) │          │
│  │ 飞书文档  │  │ HTML预览 │  │ ~/.claude/ 等   │          │
│  └──────────┘  └──────────┘  └──────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Skill 目录结构

每个 harness 的 skill 遵循统一结构：

```
<harness>/
└── Skills/
    └── zeal-onboarding/
        ├── SKILL.md                    # 主入口：触发条件、状态机、流程编排
        ├── user-profile-template.md    # USER.md 统一模板
        ├── MIGRATION-NOTES.md          # 跨 harness 迁移说明（可选）
        ├── init/
        │   └── SKILL.md                # 环境检查、初始化
        ├── extract/
        │   └── SKILL.md                # 信息提取与隐私过滤
        ├── interview/
        │   └── SKILL.md                # 对话式问答
        ├── hitl/
        │   ├── SKILL.md                # HITL 确认与提交
        │   ├── hitl-template.html      # HTML 预览模板
        │   └── save-server.py          # 本地保存服务（标准库 only）
        └── evals/
            └── evals.json              # 测试用例
```

**子 skill 约定**：
- 主 `SKILL.md` 负责流程编排，通过描述引用子目录下的 `SKILL.md`
- 子 skill 目录名使用 kebab-case，与职责对应
- 辅助文件（模板、脚本）放在对应子 skill 目录下

### 2.3 状态机

Onboarding 的核心是一个持久化状态机：

| 状态 | 含义 | 下一步动作 | 持久化位置 |
|---|---|---|---|
| `none` / 文件不存在 | 全新用户 | 从 Step 1 (init) 开始 | `.state.json` |
| `initialized` | 环境检查通过 | 从 Step 2 (extract) 开始 | `.state.json` |
| `extracted` | 已有信息提取完成 | 从 Step 3 (interview) 开始 | `.state.json` |
| `interviewed` | 对话问答完成 | 从 Step 4 (hitl) 开始 | `.state.json` |
| `completed` | 画像已生成并提交 | 询问更新或退出 | `.state.json` |

状态持久化文件：`./USER-profile/.state.json`

断点续传：任何步骤失败，记录错误到 `lastError` 字段，下次触发时询问是否从失败处重试。

### 2.4 各子 Skill 详解

#### init — 环境初始化

**职责**：
- 检查 `lark-cli` 是否已安装且可用
- 验证 OAuth 认证状态
- 确认飞书账号

**输出**：`{"larkReady": true, "userName": "..."}`

**关键设计**：安装和 OAuth 流程不由 Agent 自动执行（涉及 npm/brew 和浏览器弹窗），而是引导用户手动完成。Agent 只做检测和验证。

#### extract — 信息提取

**职责**：
- 检测当前 harness
- 从各 harness 的 memory 中提取用户信息
- 可选：收集社交媒体链接
- 生成 USER.md 草稿

**Harness 检测方式**：

| Harness | 检测方式 |
|---|---|
| claude-code | `~/.claude/` 目录存在 |
| Hermes | `~/.hermes/` 目录存在，支持 `memory` / `session_search` 工具 |
| openClaw | `~/.openclaw/` 目录存在 |

**Memory 提取差异**：

| Harness | 提取方式 | 说明 |
|---|---|---|
| claude-code | 文件系统读取 | `~/.claude/projects/**/memory/*.md` |
| Hermes | 工具调用 | `memory(action="read")` + `session_search(query="...")` |
| openClaw | 文件系统读取 + 工具搜索补充 | 直接读取 `~/.openclaw/workspace/`，辅以 `memory_search`/`memory_get` |

**隐私过滤（强制）**：
- 真实姓名 → 仅保留 nickname
- 公司/组织全称 → 保留行业描述
- 手机号、邮箱、身份证号 → 完全丢弃
- 具体地址 → 仅保留城市级别
- 未公开的项目/客户名称 → 泛化描述

#### interview — 对话完善

**职责**：
- 读取草稿，对比模板，识别缺失维度
- 通过对话分轮次补充信息（≤5 轮）
- 生成完善的 USER.md

**轮次设计**：

| 轮次 | 主题 | 优先级 |
|---|---|---|
| 第 1 轮 | Identity + 基础信息 | 中 |
| 第 2 轮 | What I Do & Build | 中 |
| 第 3 轮 | What I Can Offer | 高 |
| 第 4 轮 | What I'm Looking For | 最高 |
| 第 5 轮 | My Style & Interests | 低 |

**跨 Harness 对话工具差异**：

| Harness | 对话工具 | 特点 |
|---|---|---|
| claude-code | `AskUserQuestion` | 内置函数式调用，Agent 直接提问 |
| Hermes | `clarify` | 显式 tool call，支持多选/开放式 |
| openClaw | 自然对话 | 直接对话交互，用户直接回复 |

**跳过策略**：每轮必须提供"跳过"选项，用户跳过的 Section 在最终 USER.md 中标记为 `[待补充]`。

#### hitl — 确认与提交

**职责**：
- 生成 HTML 预览页面
- 在浏览器中打开
- 引导用户确认或修改
- 确认后上传至飞书文档

**HTML 预览架构**：

```
┌─────────────────┐     ┌───────────────┐     ┌─────────────────┐
│  hitl-template  │────▶│  Python server │────▶│  Browser (file) │
│   (静态模板)     │     │  save-server.py│     │  (用户编辑)     │
└─────────────────┘     └───────────────┘     └─────────────────┘
         │                      ▲                       │
         │                      │ POST /save            │
         ▼                      │                       ▼
  ┌──────────────┐      ┌──────┴──────┐        ┌──────────────┐
  │  SKILL.md    │─────▶│  替换占位符  │        │ 用户点击保存  │
  │ (渲染逻辑)   │      │  {{NICKNAME}}│        │ 覆盖 USER.md  │
  └──────────────┘      └─────────────┘        └──────────────┘
```

**飞书上传流程**：

1. 剥离 YAML frontmatter（Lark 不支持）
2. 在 content 开头添加 H1 标题（v2 API 无 `--title` 参数）
3. 使用相对路径 + `@` 前缀上传：`--content @USER-lark.md`
4. 调用 `drive files patch` 设置元数据标题（文档列表显示）
5. 默认使用「个人知识库」(`--parent-position my_library`)，减少 OAuth 摩擦

### 2.5 USER.md 画像格式

```yaml
---
name: nickname
description: 一句话自我介绍
rule: optional matching rule hints
tags: [auto-generated tags]
---

# Identity
# What I Do & Build
# What I Can Offer
# What I'm Looking For
# My Style & Interests
# Metadata & External Context
```

**设计原则**：
- YAML frontmatter 供 Agent 解析，正文供人类阅读
- Section 顺序按撮合价值排列（What I'm Looking For 最关键）
- 所有内容使用 Markdown，便于 Lark 渲染和版本控制

---

## 三、跨 Harness 适配策略

### 3.1 适配原则

| 原则 | 说明 |
|---|---|
| **禁止硬编码 harness API** | Skill 中不直接调用 harness 特有的 API |
| **条件分支处理差异** | 如需 harness 特定逻辑，通过配置或条件分支处理 |
| **优先复制骨架适配** | 新增 harness 时，复制现有 skill 骨架，针对性修改 |
| **工具抽象** | 将 harness 差异封装在对应子 skill 中，主 skill 保持通用 |

### 3.2 当前适配状态

| Harness | 状态 | 核心差异 |
|---|---|---|
| claude-code | ✅ 已完成 | `AskUserQuestion` 对话，文件系统读 memory |
| Hermes | ✅ 已完成 | `clarify` 工具对话，`memory`/`session_search` 读 memory |
| Codex | ⏳ 预留 | 待适配 |
| openClaw | ✅ 已完成 | 自然对话，`memory_search`/`memory_get` 读 memory，文件直接读取 |

### 3.3 迁移检查清单

将 skill 从 harness A 迁移到 harness B 时，重点检查：

- [ ] **对话工具**：`AskUserQuestion` → `clarify` 或其他等价工具
- [ ] **Memory 读取**：文件系统 → 工具调用，或反之（openClaw 为文件直接读取 + `memory_search`/`memory_get` 补充）
- [ ] **路径引用**：`<harness-a>/Skills/...` → `<harness-b>/Skills/...`
- [ ] **提示文本**：Harness 名称在 HTML 模板和对话中的引用
- [ ] **Eval 期望**：测试用例中的 harness 检测和工具调用描述

---

## 四、后续可改善的地方

### 4.1 Phase-1：匹配与撮合

| 改进项 | 描述 | 优先级 |
|---|---|---|
| **匹配引擎** | 基于 USER.md 的向量相似度匹配，推荐潜在连接对象 | 高 |
| **双向确认** | 双方 Agent 交换脱敏画像，人类确认后才交换联系方式 | 高 |
| **社群能力地图** | 可视化展示社群成员的技能分布和兴趣热点 | 中 |
| **画像更新提醒** | Agent 定期回访用户，询问近况并更新画像 | 中 |
| **外部信息抓取** | 抓取用户提供的社交媒体链接，自动补充画像 | 低 |

### 4.2 Phase-2：平台化

| 改进项 | 描述 | 优先级 |
|---|---|---|
| **专用 API 后端** | 替代飞书文档，建立专用的画像存储和匹配 API | 高 |
| **多社群支持** | 一个用户可加入多个社群，每个社群有独立画像 | 中 |
| **画像版本历史** | 记录画像变更历史，支持回滚和对比 | 中 |
| **社群运营工具** | 为社群管理员提供成员分析和活动策划工具 | 低 |

### 4.3 技术债务与体验优化

| 改进项 | 描述 | 优先级 |
|---|---|---|
| **前端剥离** | HITL 的 HTML 编辑页面可以发展为独立 Web App，而非本地文件 | 高 |
| **状态机持久化** | 当前 `.state.json` 是本地文件，后续可迁移到 SQLite 或后端 | 中 |
| **自动化测试** | 为每个子 skill 编写可执行的自动化测试，而非仅 evals.json | 中 |
| **上传脚本封装** | 将 Lark 上传逻辑（剥离 frontmatter、构造 H1、patch 标题）封装为独立脚本 | 中 |
| **错误恢复增强** | 更细粒度的断点续传，支持单步骤重试而非整流程重来 | 低 |
| **多语言支持** | 画像模板和对话流程支持英文等多语言 | 低 |

### 4.4 已知问题与限制

| 问题 | 现状 | 计划修复 |
|---|---|---|
| Lark v2 API 无 `--title` | 用 content H1 + `drive files patch`  workaround | 封装为上传脚本 |
| YAML frontmatter 被 Lark 渲染为 h2 | 上传前手动剥离 | 上传脚本自动处理 |
| OAuth scope 额外申请 | 默认走「个人知识库」避免额外授权 | 保持现状 |
| 社交媒体抓取未实现 | MVP 阶段仅收集链接 | Phase-1 实现抓取 |
| 无专用后端 | 依赖飞书文档存储 | Phase-2 建设 API |

---

## 五、附录

### 5.1 相关文档

| 文档 | 位置 | 说明 |
|---|---|---|
| Skills 开发规范 | `.claude/rules/skills-dev.md` | 目录结构、命名规范、辅助文件要求 |
| Git 工作流 | `.claude/rules/git-workflow.md` | 分支策略、提交规范 |
| Memory 使用规范 | `.claude/rules/memory-usage.md` | 记忆持久化规则 |
| Hermes 迁移说明 | `hermes/Skills/zeal-onboarding/MIGRATION-NOTES.md` | 具体迁移改动分析 |
| OpenClaw 迁移说明 | `openclaw/Skills/zeal-onboarding/MIGRATION-NOTES.md` | 具体迁移改动分析 |
| Onboarding 踩坑记录 | `.docs/LESSON-LEARN-onboarding.md` | 首次端到端执行的经验总结 |

### 5.2 术语表

| 术语 | 含义 |
|---|---|
| **Harness** | Agent 运行环境/框架（如 Claude Code、Hermes、OpenClaw、Codex） |
| **Skill** | 封装的可复用 Agent 能力模块，包含触发条件、流程和工具调用 |
| **HITL** | Human-in-the-Loop，人机协同，在关键节点由人类确认 |
| **USER.md** | 标准化的用户画像文件，YAML frontmatter + Markdown 正文 |
| **Lark / 飞书** | 字节跳动的企业协作平台，MVP 阶段的文档存储和协作工具 |
