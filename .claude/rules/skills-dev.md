# Skills 开发规范

<!-- 适用于: claude-code/ codex/ openClaw/ 目录下的所有 skill 开发 -->

## 目录结构

每个 harness 目录下统一使用 `Skills/` 子目录存放技能：

```
claude-code/
└── Skills/
    ├── skill-creator/          # 参考用，不修改
    └── <skill-name>/
        ├── SKILL.md
        ├── references/
        └── evals/
```

## Skill 开发流程

- 新建 skill 前必须阅读 `/skill-creator` 的 SKILL.md 了解完整规范
- 使用 `python -m scripts.quick_validate` 验证 skill 结构
- 每个 skill 必须包含 `evals/evals.json` 测试用例
- Skill 命名使用 kebab-case，与目录名一致

## 跨 Harness 兼容

- 禁止在 skill 中硬编码 harness 特定 API
- 如需 harness 特定逻辑，通过配置注入或条件分支处理
- 新增 harness 时，优先复制现有 harness 的 skill 骨架适配
