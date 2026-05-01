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

## Skill 设计原则

### 隐私与数据分离
- Skill 本身**不得包含**具体社群的隐私信息（人名、角色分配、具体规则等）
- 社群特定数据存放在**工作路径**下的外部文件中（如 `docs/{skill-name}/context/`）
- Skill 目录下的 `context/` 只保留**空白模板**，供新社群初始化时参考
- 保证可迁移性：换到另一个社群时，只需替换工作路径下的数据文件

### Agent 驱动
- 优先使用 Agent 完成数据提取、推理、生成，减少脚本依赖
- 如需脚本辅助，仅限 Python 标准库，零第三方依赖
- 脚本负责 I/O 协调，复杂推理由 Agent 完成

### 上下文文件规范
- Skill 运行时应先读取工作路径下的上下文文件获取社群规则
- 上下文文件路径统一使用 `docs/{skill-name}/context/` 格式
- 上下文文件类型：
  - `community-rules.md` — 社群角色定义、格式规范、数据源路径
  - `name-corrections.md` — ASR 错误修正、昵称-实名映射
  - `topic-tags.md` — 话题标签词库

## 跨 Harness 兼容

- 禁止在 skill 中硬编码 harness 特定 API
- 如需 harness 特定逻辑，通过配置注入或条件分支处理
- 新增 harness 时，优先复制现有 harness 的 skill 骨架适配
