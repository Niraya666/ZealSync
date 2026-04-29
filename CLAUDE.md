# ZealSync

<!-- Last reviewed: 2026-04-28 -->
<!-- Phase: Phase-0 MVP -->

社群 Agent 信息撮合系统。通过对话式信息收集与 Agent 智能分析，为社群成员生成精准画像，实现信息的高效匹配与撮合。

## Project Overview

- **Phase**: Phase-0 MVP，聚焦"信息整合获取"
- **Core Mechanism**: 基于 agent 的 skills 实现各 harness 的能力
- **Multi-Harness**: claude-code / codex / openClaw，各自独立目录
- **Tech Stack**: 未定，后续迭代确定

## Architecture

```
ZealSync/
├── claude-code/          # claude-code harness skills
├── codex/                # codex harness skills
├── openClaw/             # openClaw harness skills
└── .claude/rules/        # 开发规范
```

## Information Flow (Phase-0)

1. **对话式收集**: Agent 通过对话收集用户基本信息
2. **可选上传**: 用户提供社交媒体链接或 blog URL
3. **Subagent 汇总**: 通过子 Agent 抓取并汇总外部信息
4. **画像生成**: Agent 生成个人画像摘要
5. **用户确认**: 用户确认或修改画像内容
6. **可视化编辑**: 跳转 Web 页面进行 HITL 编辑
7. **存储输出**: MVP 版本上传至飞书文档（后续迁移至专用 API）

## Development Rules

@.claude/rules/skills-dev.md
@.claude/rules/git-workflow.md
@.claude/rules/memory-usage.md

## Feishu (Lark) Integration Notes

When uploading documents via `lark-cli`:

- **v2 API has no `--title` flag**: Document title must be set via H1 in the Markdown content body. After creation, use `lark-cli drive files patch` with `"new_title":"..."` to set the metadata title (visible in doc lists and browser tabs).
- **Strip YAML frontmatter before upload**: Lark v2 Markdown parser treats `---` delimiters as content blocks, rendering frontmatter as an h2 heading. Always construct a separate upload file with frontmatter removed.
- **Prefer personal library to reduce OAuth friction**: Default to `--parent-position my_library`. Only request `space:document:retrieve` scope when the user explicitly chooses to upload to a specific folder.
- **Use relative paths with `@` prefix**: When passing files to `lark-cli docs +create`, use `--content @USER-lark.md` after `cd` into the target directory. Absolute paths often cause `invalid file path` errors.

## File Path & CWD Best Practices

- **Be explicit about working directory**: Commands that `cd` into subdirectories must either use absolute paths for all subsequent file operations, or `cd` back afterward.
- **Avoid `cd` when possible**: Prefer absolute paths in arguments over changing the working directory mid-script.
- **State mutations must be atomic**: If a step creates a temporary file for upload, clean it up or keep it in a well-known temp location (e.g., `/tmp/` or a local `.tmp/`).

## Principles

- **MVP First**: Phase-0 只做最核心的信息整合获取，不扩展边缘功能
- **Harness Isolation**: 不同 harness 的 skills 完全隔离，禁止跨目录引用
- **Skill 驱动**: 每个功能模块封装为独立 skill，遵循 `/skill-creator` 规范
- **渐进迭代**: 每个 Phase 结束前必须完成画像数据的端到端闭环验证
