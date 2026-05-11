# ZealSync Onboarding — Codex 版本

## 目的

Codex 版 onboarding skill 用于在 Codex 中完成社群成员画像的端到端生成：从当前 workspace 和用户授权资料中初始化 `USER.md`，通过自然对话补充缺失信息，生成 HITL 预览页，确认后上传到飞书文档。

## 目录

```text
codex/Skills/zeal-onboarding/
├── SKILL.md
├── init/SKILL.md
├── extract/SKILL.md
├── interview/SKILL.md
├── hitl/
│   ├── SKILL.md
│   ├── hitl-template.html
│   ├── generate-preview.py
│   └── save-server.py
├── user-profile-template.md
├── MIGRATION-NOTES.md
└── evals/evals.json
```

## 安装

```bash
mkdir -p ~/.agents/skills
cp -r ./codex/Skills/zeal-onboarding \
      ~/.agents/skills/zeal-onboarding
```

如果在 ZealSync repo 内调试，也可以保留源码在 `codex/Skills/zeal-onboarding/`，再按需复制到 `~/.agents/skills/`。

## 触发词

- "帮我创建社群画像"
- "生成 USER.md"
- "ZealSync onboarding"
- "我要加入社群"
- "创建我的画像"
- "更新我的画像"

## Codex 适配点

| 模块 | Codex 行为 |
|---|---|
| `init` | 检查 `lark-cli` 与 OAuth；安装、联网、浏览器授权前先说明目的并确认 |
| `extract` | 优先读取当前 workspace、既有 `USER-profile/`、用户粘贴资料；读取其他 harness 目录前必须获得用户同意 |
| `interview` | 通过自然对话补足画像，最多 5 轮，每轮最多 3 个问题 |
| `hitl` | 生成本地 HTML 预览；优先使用 Codex Browser 打开，失败时返回绝对路径 |
| `upload` | 继续遵循 Lark v2 限制：上传前剥离 YAML frontmatter，并使用相对路径 `@USER-lark.md` |

## 隐私规则

生成画像时不得写入真实姓名、公司/组织全称、手机号、邮箱、身份证号、精确地址和未公开项目/客户名称。保留 nickname、城市级别位置、行业/领域描述和用户明确愿意公开的信息。

## 验证

基础验证项：

```bash
PYTHONPYCACHEPREFIX=/tmp/zealsync-pycache \
python3 -m py_compile codex/Skills/zeal-onboarding/hitl/generate-preview.py \
  codex/Skills/zeal-onboarding/hitl/save-server.py
```

结构验证项：

- `SKILL.md` 与子 skill 均存在 YAML frontmatter
- `evals/evals.json` 可解析为 JSON
- `hitl/SKILL.md` 中脚本路径指向 `codex/Skills/zeal-onboarding/`
- 文档中不再把 Codex 标记为 reserved
