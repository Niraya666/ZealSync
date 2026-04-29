# Skills 开发规范

<!-- 适用于: claude-code/ codex/ openClaw/ 目录下的所有 skill 开发 -->

## 目录结构

每个 harness 目录下统一使用 `Skills/` 子目录存放技能：

```
claude-code/
└── Skills/
    ├── skill-creator/          # 参考用，不修改
    └── <skill-name>/
        ├── SKILL.md            # 主入口：触发条件、状态机、流程编排
        ├── init/               # 环境检查、初始化（可选子 skill）
        ├── extract/            # 信息提取（可选子 skill）
        ├── interview/          # 对话收集（可选子 skill）
        ├── hitl/               # 人机确认（可选子 skill）
        │   ├── SKILL.md
        │   ├── hitl-template.html   # HTML 模板文件
        │   └── save-server.py       # 本地保存服务（标准库 only）
        └── evals/
            └── evals.json
```

**子 skill 约定**：
- 主 `SKILL.md` 负责流程编排，通过描述引用子目录下的 `SKILL.md`
- 子 skill 目录名使用 kebab-case，与职责对应
- 辅助文件（模板、脚本）放在对应子 skill 目录下

**辅助文件规范**：
- HTML 模板：供浏览器渲染的静态模板，使用 `{{PLACEHOLDER}}` 占位符
- Python 脚本：仅限标准库，零第三方依赖，通过 `python3 script.py` 调用
- 脚本输出统一格式：`KEY:value`，便于 skill 用 `grep` / `cut` 解析

## Skill 开发流程

- 新建 skill 前必须阅读 `/skill-creator` 的 SKILL.md 了解完整规范
- 使用 `python ~/.claude/skills/skill-creator/scripts/quick_validate.py <skill-path>` 验证结构
- 每个 skill 必须包含 `evals/evals.json` 测试用例
- Skill 命名使用 kebab-case，与目录名一致

## 跨 Harness 兼容

- 禁止在 skill 中硬编码 harness 特定 API
- 如需 harness 特定逻辑，通过配置注入或条件分支处理
- 新增 harness 时，优先复制现有 harness 的 skill 骨架适配
