---
name: zeal-onboarding-interview
description: ZealSync onboarding 对话式问答。基于已有草稿对比模板，通过自然对话在5轮内完善 USER.md。
---

# ZealSync Onboarding — Interview

## 职责

- 读取 `USER.md.draft`，对比完整模板，识别缺失维度
- 通过自然对话分轮次补充信息
- 控制总轮数在 **5 轮以内**
- 输出完善的 `USER.md`

## 输入

`./USER-profile/[nickname]/USER.md.draft`

## 分析流程

### 1. 差距分析

读取草稿后，逐 Section 检查：

| Section | 检查项 | 判定标准 |
|---|---|---|
| **Identity** | nickname, role, location, background, MBTI | 每个子项是否有具体内容（非占位符） |
| **What I Do & Build** | current role, domain, topics, recent focus, building/exploring | 是否有具体描述，非泛泛而谈 |
| **What I Can Offer** | skills, expertise, resources, network, time | 是否有可执行、可匹配的具体项 |
| **What I'm Looking For** | matching intents, ideal people, opportunities, boundaries | 是否有明确的"yes"条件 |
| **My Style & Interests** | availability, communication prefs, working style, constraints | 是否有时间/沟通偏好 |
| **Metadata & External Context** | sources, links, freshness | 基础信息是否完整 |

判定每个 Section 为：
- `filled` — 内容充实
- `partial` — 有内容但不足
- `empty` — 无内容或仅占位符

### 2. 生成补充问题

按优先级排序（对撮合价值最高的优先）：

1. **What I'm Looking For**（ Demand 侧是匹配的核心）
2. **What I Can Offer**（ Supply 侧）
3. **Identity**（基础信息）
4. **What I Do & Build**（上下文）
5. **My Style & Interests**（匹配质量）

合并同类问题，尽量每轮覆盖一个 Section 的多个子项。

### 3. 对话轮次设计（最多 5 轮）

OpenClaw 使用自然对话交互，Agent 直接向用户提问，用户直接回复。**无需显式工具调用**。

**第 1 轮：Identity + 基础信息**

> 为了帮你创建精准的社群画像，先确认几个基础信息：
> - 你希望用什么**昵称**展示给社群？（不需要真实姓名）
> - 你目前的主要身份或职业方向是什么？（如"AI 产品经理"、"全栈开发者"，不需要具体公司名）
> - 你所在的城市或时区？（或是否接受远程）
>
> 请直接回复你的答案，或回复"跳过"。

**第 2 轮：What I Do & Build**

> 接下来了解你目前投入的领域：
> - 你目前在做什么项目或工作？用 1-2 句话描述
> - 你最近在学习或探索什么新方向？
> - 如果有项目需要合作，你现在最需要什么样的 collaborator？
>
> 请直接回复你的答案，或回复"跳过"。

**第 3 轮：What I Can Offer**

> 你能为社群其他成员提供什么？
> - 你的核心技能或专长是什么？（技术/非技术都可以）
> - 你有哪些资源可以分享？（人脉、工具、场地、经验等）
> - 你每周大概能投入多少时间参与社群互动？
>
> 请直接回复你的答案，或回复"跳过"。

**第 4 轮：What I'm Looking For**

> 这是画像中最关键的部分 —— 你想找什么：
> - 你目前最想连接什么样的人？（具体描述，比如"做 AI 产品的产品经理"）
> - 你希望获得什么样的机会？（学习、合作、招聘、投资等）
> - 有什么是你明确不想要的？（帮助排除不匹配）
>
> 请直接回复你的答案，或回复"跳过"。

**第 5 轮：My Style & Interests**

> 最后确认一下你的偏好：
> - 你更喜欢哪种交流方式？（线上文字 / 语音 / 线下见面）
> - 你的大致可用时间？（工作日晚上 / 周末 / 灵活）
> - 有什么个人标签或兴趣想展示？（如 MBTI、爱好、价值观等）
>
> 请直接回复你的答案，或回复"跳过"。

### 4. 用户跳过策略

每轮必须尊重用户的"跳过"选择。用户跳过的 Section 保留占位符，在最终 USER.md 中标记为 `[待补充]`。

## 输出

将收集到的信息填入模板，生成完整的 `USER.md`。

模板参见同目录下的 `user-profile-template.md`。生成时：
- `Version` 填 `v1.0.0`
- `Sources` 追加 `onboarding interview`
- `Confirmation Status` 填 `pending`
- 所有占位符用用户提供的实际内容填充
- 用户跳过的 Section 保留占位符并在内容中标记为 `[待补充]`

保存到 `./USER-profile/[nickname]/USER.md`，删除 `USER.md.draft`。

## 标签生成

基于所有 Section 的内容，自动提取 5-10 个关键词标签填入 YAML frontmatter：

- 从 Skills 提取技术标签（如 `python`, `ai-product`, `design`）
- 从 Interests 提取领域标签（如 `web3`, `healthcare`, `education`）
- 从 Style 提取偏好标签（如 `remote-friendly`, `weekend-only`）

## 错误处理

- 如用户中途退出，保存已收集的内容到 `USER.md.draft`，记录已完成的轮次
- 下次触发时，从断点继续
