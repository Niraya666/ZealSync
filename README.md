# ZealSync

> 社群 Agent 信息撮合系统 | Community Agent Information Matching System

**Languages**: [简体中文](#cn) · [English](#en)

---

<a name="cn"></a>

## 中文版

[→ 切换到英文版本](#en)

### 项目简介

ZealSync 是一个基于 Agent 的社群信息撮合系统。通过对话式信息收集与 Agent 智能分析，为社群成员生成精准画像，实现信息的高效匹配与撮合。

**当前阶段**：Phase-0 MVP，聚焦"信息整合获取"

### 核心特性

- **对话式画像生成**：Agent 通过自然对话收集用户基本信息，降低填写门槛
- **多源信息整合**：自动读取用户已有的 Agent 工具记忆（claude-code / openClaw / Hermes），减少重复输入
- **隐私优先设计**：主动过滤真实姓名、公司名、手机号等敏感信息，仅保留 nickname 与泛化描述
- **人机协同确认（HITL）**：生成画像后提供可视化编辑页面，用户可浏览并修改后再提交
- **飞书文档输出**：画像确认后自动上传至飞书文档，便于社群共享与检索

### 信息流程

```
对话式收集 → 可选上传社交媒体 → Subagent 汇总 → 画像生成
      ↓
用户确认 → 可视化编辑 → 存储输出（飞书文档）
```

### 项目结构

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
├── codex/                          # codex harness skills（预留）
├── openClaw/                       # openClaw harness skills（预留）
├── .claude/rules/                  # 开发规范
├── .docs/                          # 设计文档与经验总结
└── USER-profile/                   # 用户画像输出目录
```

### 安装

将 `claude-code/Skills/zeal-onboarding/` 目录下的内容复制到 Claude Code 的 skills 目录即可使用：

```bash
# 默认 skills 目录路径
mkdir -p ~/.claude/skills

cp -r /path/to/ZealSync/claude-code/Skills/zeal-onboarding \
      ~/.claude/skills/zeal-onboarding
```

复制完成后，在 Claude Code 对话中触发 onboarding：

- "帮我创建社群画像"
- "生成 USER.md"
- "ZealSync onboarding"
- "我要加入社群"

### 快速开始

**流程状态机**：

| 状态 | 说明 | 下一步 |
|---|---|---|
| `none` | 新用户 | 环境检查 |
| `initialized` | 环境就绪 | 信息提取 |
| `extracted` | 提取完成 | 对话问答 |
| `interviewed` | 问答完成 | HITL 确认 |
| `completed` | 已提交 | 可更新或重新生成 |

---

<a name="en"></a>

## English

[→ Switch to Chinese version](#cn)

### Introduction

ZealSync is a community information matching system powered by AI Agents. Through conversational information collection and Agent-driven intelligent analysis, it generates precise community member profiles and enables efficient information matching.

**Current Phase**: Phase-0 MVP, focused on "information integration and acquisition"

### Key Features

- **Conversational Profile Generation**: The Agent collects user information through natural dialogue, lowering the barrier to entry
- **Multi-Source Information Integration**: Automatically reads existing Agent tool memories (claude-code / openClaw / Hermes) to reduce repetitive input
- **Privacy-First Design**: Actively filters real names, company names, phone numbers, and other sensitive data — only nicknames and generalized descriptions are retained
- **Human-in-the-Loop (HITL)**: After profile generation, a visual editing page is provided for users to review and modify before submission
- **Lark (Feishu) Document Output**: Confirmed profiles are automatically uploaded to Lark documents for community sharing and retrieval

### Information Flow

```
Conversational Collection → Optional Social Media Upload → Subagent Summarization → Profile Generation
                    ↓
User Confirmation → Visual Editing → Storage Output (Lark Document)
```

### Project Structure

```
ZealSync/
├── claude-code/                    # claude-code harness skills
│   └── Skills/
│       └── zeal-onboarding/        # Core onboarding skill
│           ├── init/               # Environment check & initialization
│           ├── extract/            # Information extraction & privacy filtering
│           ├── interview/          # Conversational Q&A (≤5 rounds)
│           ├── hitl/               # Browser-based visual editing
│           ├── evals/              # Test cases
│           ├── user-profile-template.md  # Unified USER.md template
│           └── SKILL.md            # Main entry point
├── codex/                          # codex harness skills (reserved)
├── openClaw/                       # openClaw harness skills (reserved)
├── .claude/rules/                  # Development rules
├── .docs/                          # Design docs & lessons learned
└── USER-profile/                   # User profile output directory
```

### Installation

Copy `claude-code/Skills/zeal-onboarding/` into your Claude Code skills directory:

```bash
# Default skills directory path
mkdir -p ~/.claude/skills

cp -r /path/to/ZealSync/claude-code/Skills/zeal-onboarding \
      ~/.claude/skills/zeal-onboarding
```

Once installed, trigger onboarding in a Claude Code conversation with any of the following:

- "帮我创建社群画像"
- "生成 USER.md"
- "ZealSync onboarding"
- "我要加入社群"

### Quick Start

**State Machine**:

| Status | Description | Next Step |
|---|---|---|
| `none` | New user | Environment check |
| `initialized` | Environment ready | Information extraction |
| `extracted` | Extraction complete | Conversational interview |
| `interviewed` | Interview complete | HITL confirmation |
| `completed` | Submitted | Can update or regenerate |
