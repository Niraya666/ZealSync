# zeal-mining

## 触发条件

当用户需要以下操作时触发本 Skill：
- "挖掘社群历史纪要中的成员信息"
- "从会议纪要中提取成员画像"
- "对齐小作文和会议纪要中的人名"
- "生成成员档案"
- "汇总活动参与记录"
- "分析社群成员数据"

## 概述

本 Skill 将分散在社群历史活动记录中的成员信息挖掘出来，对齐到统一的命名空间，生成可累积的个人档案和活动汇总表。

**核心机制**：
- 从两类文档中提取结构化数据：好物分享汇总（小作文）和 AI 会议纪要
- 通过多 Agent Loop 解决三重命名空间对齐（小作文昵称 ↔ 纪要实名 ↔ 说话人编号）
- 生成以**小作文昵称**为 canonical_name 的个人档案
- 支持一次性初始化（全量）和增量更新（每期追加）

**设计原则**：
- 全部 Agent 驱动，无脚本
- Skill 本身不包含具体社群的隐私信息（人名、角色分配等）
- 社群特定数据存放在**工作路径**下的 `docs/zeal-mining/context/` 中
- Skill 运行时读取工作路径下的 context 文件
- Skill 目录下的 `context/` 只保留空白模板，供新社群初始化时参考
- 保证可迁移性：换到另一个社群时，只需替换工作路径下的 context 文件

## 上下文文件

运行本 Skill 前，Agent 应先读取以下上下文文件：

| 文件 | 内容 | 用途 |
|------|------|------|
| `docs/zeal-mining/context/community-rules.md` | 社群角色定义、格式规范、数据源路径 | Extract + Align |
| `docs/zeal-mining/context/name-corrections.md` | ASR 错误修正、昵称-实名映射、特殊格式处理 | Align |
| `docs/zeal-mining/context/topic-tags.md` | 话题标签词库 | Profile |

## 状态机

```
[INIT] → [EXTRACT] → [ALIGN] → [PROFILE] → [MERGE] → [DONE]
           ↑___________________________|
           (增量更新时，从 MERGE 回到 EXTRACT 处理下一期)
```

### 状态说明

| 状态 | 说明 | 输入 | 输出 |
|------|------|------|------|
| INIT | 确定处理范围（全量/增量），读取 context 文件 | 用户指令 | 待处理的期数列表 |
| EXTRACT | 提取结构化数据 | 原始 Markdown | `session-{n}-raw.json` |
| ALIGN | 身份对齐 | `session-{n}-raw.json` | `session-{n}-aligned.json` |
| PROFILE | 生成档案 | 对齐结果 + 原始数据 | `{canonical-name}.md` |
| MERGE | 合并到索引 | 档案 + 现有索引 | 更新后的 `index.json` |
| DONE | 完成 | - | 最终报告 |

## 流程编排

### 初始化模式（全量处理）

```
1. 读取 docs/zeal-mining/context/community-rules.md 了解社群规则
2. 读取 docs/zeal-mining/context/name-corrections.md 了解已知映射
3. 识别所有待处理期数（扫描会议纪要目录）
4. FOR each 期数:
   a. 调用 Extract Agent → 生成 session-{n}-raw.json
   b. 调用 Align Agent → 生成 session-{n}-aligned.json
   c. 调用 Profile Agent → 生成/更新各成员档案
   d. 调用 Merge Agent → 更新 index.json
5. 生成最终报告
```

### 增量模式（单期追加）

```
1. 读取 context 文件（如已更新）
2. 确定新期数
3. 调用 Extract Agent → 生成 session-{n}-raw.json
4. 调用 Align Agent → 生成 session-{n}-aligned.json
5. FOR each canonical_name IN aligned结果:
   a. 检查档案是否存在
   b. 存在 → Merge Agent 追加更新
   c. 不存在 → Profile Agent 生成新档案
6. Merge Agent 更新 index.json
7. 生成增量报告
```

## 子 Skill 调用

### Extract Agent

```
调用条件：进入 EXTRACT 状态
输入：
  - 好物分享汇总文档（对应期数的小作文段落）
  - 会议纪要文档（纪要全文）
输出：
  - docs/member-profiles/session-{n}-raw.json
上下文：读取 docs/zeal-mining/context/community-rules.md 了解格式规范
说明：参见 extract/SKILL.md
```

### Align Agent

```
调用条件：EXTRACT 完成后进入 ALIGN 状态
输入：
  - docs/member-profiles/session-{n}-raw.json
输出：
  - docs/member-profiles/session-{n}-aligned.json
上下文：读取 docs/zeal-mining/context/name-corrections.md 了解已知映射和 ASR 修正
说明：参见 align/SKILL.md。采用多 Agent Loop（Extractor→Matcher→Verifier→Judge）
```

### Profile Agent

```
调用条件：ALIGN 完成后进入 PROFILE 状态
输入：
  - docs/member-profiles/session-{n}-aligned.json
  - docs/member-profiles/session-{n}-raw.json
输出：
  - docs/member-profiles/{canonical-name}.md
上下文：读取 docs/zeal-mining/context/topic-tags.md 了解话题分类
说明：参见 profile/SKILL.md
```

### Merge Agent

```
调用条件：PROFILE 完成后进入 MERGE 状态
输入：
  - 新生成的/更新的档案文件
  - 现有 docs/member-profiles/index.json
输出：
  - 更新后的 docs/member-profiles/index.json
  - 更新后的档案文件
说明：参见 merge/SKILL.md
```

## 输出规范

### 个人档案路径

```
docs/member-profiles/
├── index.json                    # 活动汇总表和成员统计
├── {nickname}.md                 # 成员个人档案
└── ...
```

### 中间产物路径

```
docs/member-profiles/
├── session-{n}-raw.json          # Extract 输出
├── session-{n}-aligned.json      # Align 输出
└── ...
```

### 档案命名规则

- 文件名使用 canonical_name（小作文昵称）
- 保留原始大小写和字符

## 增量更新触发

每期新活动结束后，可通过以下方式触发增量更新：
1. 用户明确指令："更新第X期数据"
2. 检测到新的纪要文件

## 质量检查清单

每完成一期处理，检查：
- [ ] 所有小作文中的昵称都有对应的 canonical_name
- [ ] 所有说话人都有映射（或明确标记为 UNCERTAIN）
- [ ] 主持人已正确识别
- [ ] 领航员已正确识别
- [ ] 档案中包含 Identity + Activity History
- [ ] 好物分享已提取并分类
- [ ] index.json 已更新

## 迁移到新社群

1. 替换工作路径下的 `docs/zeal-mining/context/community-rules.md`
2. 替换工作路径下的 `docs/zeal-mining/context/name-corrections.md`
3. 替换工作路径下的 `docs/zeal-mining/context/topic-tags.md`
4. Skill 核心逻辑（SKILL.md 和各子 skill）无需修改
