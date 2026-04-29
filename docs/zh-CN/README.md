# ZealSync

> 社群 Agent 信息撮合系统

---

## 项目简介

ZealSync 是一个基于 Agent 的社群信息撮合系统。通过对话式信息收集与 Agent 智能分析，为社群成员生成精准画像，实现信息的高效匹配与撮合。

**当前阶段**：Phase-0 MVP，聚焦"信息整合获取"

## 核心特性

- **对话式画像生成**：Agent 通过自然对话收集用户基本信息，降低填写门槛
- **多源信息整合**：自动读取用户已有的 Agent 工具记忆（claude-code / openClaw / Hermes），减少重复输入
- **隐私优先设计**：主动过滤真实姓名、公司名、手机号等敏感信息，仅保留 nickname 与泛化描述
- **人机协同确认（HITL）**：生成画像后提供可视化编辑页面，用户可浏览并修改后再提交
- **飞书文档输出**：画像确认后自动上传至飞书文档，便于社群共享与检索

## 信息流程

```
对话式收集 → 可选上传社交媒体 → Subagent 汇总 → 画像生成
      ↓
用户确认 → 可视化编辑 → 存储输出（飞书文档）
```

## 项目结构

```
ZealSync/
├── claude-code/                    # claude-code harness skills
│   └── Skills/
│       └── zeal-onboarding/        # 核心 onboarding skill
│           ├── init/               # 环境检查与初始化
│           ├── extract/            # 信息提取与隐私过滤
│           ├── interview/          # 对话式问答（≤5轮）
│           ├── hitl/               # 浏览器可视化编辑
│           ├── evals/              # 测试用例
│           ├── user-profile-template.md  # USER.md 统一模板
│           └── SKILL.md            # 主入口
├── hermes/                         # Hermes harness skills
│   └── Skills/
│       └── zeal-onboarding/        # Hermes 版 onboarding skill
├── codex/                          # codex harness skills（预留）
├── openClaw/                       # openClaw harness skills（预留）
├── .claude/rules/                  # 开发规范
├── .docs/                          # 设计文档与经验总结
└── USER-profile/                   # 用户画像输出目录
```

## 安装

### 前提条件

- Git
- 对应 Harness 的 Agent 工具已安装（Claude Code / Hermes 等）
- 飞书 CLI (`lark-cli`) 已安装并完成 OAuth 授权（用于上传文档）

### 通用安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/Niraya666/ZealSync.git
cd ZealSync

# 2. 根据你的 Agent 工具，选择对应的安装方式（见下方）
```

### Claude Code

```bash
# 复制 skill 到 Claude Code 的 skills 目录
mkdir -p ~/.claude/skills

cp -r ./claude-code/Skills/zeal-onboarding \
      ~/.claude/skills/zeal-onboarding
```

触发方式：在 Claude Code 对话中输入任意触发词
- "帮我创建社群画像"
- "生成 USER.md"
- "ZealSync onboarding"
- "我要加入社群"

### Hermes

```bash
# 复制 skill 到 Hermes 的 skills 目录
mkdir -p ~/.hermes/skills

cp -r ./hermes/Skills/zeal-onboarding \
      ~/.hermes/skills/zeal-onboarding
```

触发方式：
```bash
# 启动时预加载
hermes -s zeal-onboarding

# 或在对话中动态加载
/skill zeal-onboarding
```

### Codex（预留）

尚未适配，欢迎贡献。

### OpenClaw（预留）

尚未适配，欢迎贡献。

## 快速开始

**流程状态机**：

| 状态 | 说明 | 下一步 |
|---|---|---|
| `none` | 新用户 | 环境检查 |
| `initialized` | 环境就绪 | 信息提取 |
| `extracted` | 提取完成 | 对话问答 |
| `interviewed` | 问答完成 | HITL 确认 |
| `completed` | 已提交 | 可更新或重新生成 |

## 开发规范

- [Skills 开发规范](../../.claude/rules/skills-dev.md)
- [Git 工作流规范](../../.claude/rules/git-workflow.md)
- [Memory 使用规范](../../.claude/rules/memory-usage.md)

## 相关文档

- [MIGRATION-NOTES.md](../../hermes/Skills/zeal-onboarding/MIGRATION-NOTES.md) — Hermes 迁移说明
