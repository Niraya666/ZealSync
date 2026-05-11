# ZealSync

> Community Agent Information Matching System

---

## Introduction

ZealSync is a community information matching system powered by AI Agents. Through conversational information collection and Agent-driven intelligent analysis, it generates precise community member profiles and enables efficient information matching.

**Current Phase**: Phase-0 MVP, focused on "information integration and acquisition"

## Key Features

- **Conversational Profile Generation**: The Agent collects user information through natural dialogue, lowering the barrier to entry
- **Multi-Source Information Integration**: Reads user-approved Agent tool memories and Codex workspace context (claude-code / openClaw / Hermes / Codex) to reduce repetitive input
- **Privacy-First Design**: Actively filters real names, company names, phone numbers, and other sensitive data — only nicknames and generalized descriptions are retained
- **Human-in-the-Loop (HITL)**: After profile generation, a visual editing page is provided for users to review and modify before submission
- **Lark (Feishu) Document Output**: Confirmed profiles are automatically uploaded to Lark documents for community sharing and retrieval

## Information Flow

```
Conversational Collection → Optional Social Media Upload → Subagent Summarization → Profile Generation
                    ↓
User Confirmation → Visual Editing → Storage Output (Lark Document)
```

## Project Structure

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
├── hermes/                         # Hermes harness skills
│   └── Skills/
│       └── zeal-onboarding/        # Hermes onboarding skill
├── codex/                          # Codex harness skills
│   └── Skills/
│       └── zeal-onboarding/        # Codex onboarding skill
├── openClaw/                       # openClaw harness skills
│   └── Skills/
│       └── zeal-onboarding/        # openClaw onboarding skill
├── .claude/rules/                  # Development rules
├── .docs/                          # Design docs & lessons learned
└── USER-profile/                   # User profile output directory
```

## Installation

### Prerequisites

- Git
- Your preferred Agent tool installed (Claude Code / Hermes, etc.)
- Lark CLI (`lark-cli`) installed and OAuth authorized (for document upload)

### General Installation

```bash
# 1. Clone the repository
git clone https://github.com/Niraya666/ZealSync.git
cd ZealSync

# 2. Follow the harness-specific instructions below
```

### Claude Code

```bash
# Copy skill to Claude Code's skills directory
mkdir -p ~/.claude/skills

cp -r ./claude-code/Skills/zeal-onboarding \
      ~/.claude/skills/zeal-onboarding
```

Trigger in a Claude Code conversation with any of:
- "帮我创建社群画像"
- "生成 USER.md"
- "ZealSync onboarding"
- "我要加入社群"

### Hermes

```bash
# Copy skill to Hermes' skills directory
mkdir -p ~/.hermes/skills

cp -r ./hermes/Skills/zeal-onboarding \
      ~/.hermes/skills/zeal-onboarding
```

Trigger via:
```bash
# Preload at startup
hermes -s zeal-onboarding

# Or load dynamically in conversation
/skill zeal-onboarding
```

### OpenClaw

```bash
# Copy skill to OpenClaw's skills directory
cp -r ./openClaw/Skills/zeal-onboarding \
      ~/.openclaw/workspace/skills/zeal-onboarding
```

Trigger in an OpenClaw conversation with any of:
- "帮我创建社群画像"
- "生成 USER.md"
- "ZealSync onboarding"
- "我要加入社群"

**OpenClaw Features**:
- Conversation: Natural dialogue (no explicit tool calls required)
- Memory reading: Direct file reads from `~/.openclaw/workspace/` + `memory_search`/`memory_get` as supplementary search

### Codex

```bash
# Copy skill to Codex's skills directory
mkdir -p ~/.agents/skills

cp -r ./codex/Skills/zeal-onboarding \
      ~/.agents/skills/zeal-onboarding
```

Trigger in a Codex conversation with any of:
- "帮我创建社群画像"
- "生成 USER.md"
- "ZealSync onboarding"
- "我要加入社群"

**Codex Features**:
- Workspace-first: reads the current workspace, existing `USER-profile/`, and user-provided material first
- Permission-aware: asks before reading other harness directories, using network/OAuth flows, or opening GUI apps
- HITL preview: prefers Codex Browser for local HTML; falls back to returning the absolute preview path

## Quick Start

**State Machine**:

| Status | Description | Next Step |
|---|---|---|
| `none` | New user | Environment check |
| `initialized` | Environment ready | Information extraction |
| `extracted` | Extraction complete | Conversational interview |
| `interviewed` | Interview complete | HITL confirmation |
| `completed` | Submitted | Can update or regenerate |

## Development Rules

- [Skills Development Rules](../../.claude/rules/skills-dev.md)
- [Git Workflow](../../.claude/rules/git-workflow.md)
- [Memory Usage](../../.claude/rules/memory-usage.md)

## Related Docs

- [MIGRATION-NOTES.md](../../hermes/Skills/zeal-onboarding/MIGRATION-NOTES.md) — Hermes migration notes
- [MIGRATION-NOTES.md](../../openClaw/Skills/zeal-onboarding/MIGRATION-NOTES.md) — OpenClaw migration notes
- [Codex Onboarding](../zeal-onboarding/codex.md) — Codex version notes
- [MIGRATION-NOTES.md](../../codex/Skills/zeal-onboarding/MIGRATION-NOTES.md) — Codex migration notes
