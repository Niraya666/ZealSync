# 向其他 AI 咨询的 Prompt

## 复制以下内容

---

我正在设计一个名为 **ZealSync** 的社群 Agent 信息撮合系统的用户画像模板（USER.md），想请你从产品设计角度帮我审视这个维度框架。

## 项目背景

**ZealSync** 是一个基于 Agent Skills 的社群信息撮合系统：
- **核心场景**：Coffee-chat 撮合、组队找人、信息匹配
- **交互方式**：用户通过对话式交互（Agent 引导问答 + 可选上传外部链接）完成画像收集
- **输出目标**：生成结构化的个人画像档案 USER.md，存储于飞书文档
- **当前阶段**：Phase-0 MVP，聚焦"信息整合获取"，只做首次画像生成

## 设计灵感

参考了 **claude-code memory 机制**的模板化设计理念：
- 固定 Section Headers + 斜体描述行，系统提示词硬性约束不可修改
- 总长度限制 12,000 tokens，单个 Section 不超过 2,000 tokens
- 防止长对话中结构膨胀，确保 Agent 能精确读写特定 Section

## 候选 Section 框架（8 + 1）

```markdown
# [Nickname] Profile
_ZealSync Community Profile — 社群 Agent 信息撮合档案_

<!-- 模板约束：Section Headers 和斜体描述行固定不可改。总长度 ≤ 12,000 tokens，单 Section ≤ 2,000 tokens。 -->

# Identity
_Who are you? Core identity, location, and community presence._

# What I Do
_What do you spend your time on? Profession, projects, and daily focus._

# What I Can Offer
_What can you bring to a collaboration? Skills, resources, time, and expertise._

# What I'm Looking For
_What would make you say "yes" to a connection? Opportunities, people, and outcomes you seek._

# My Projects
_What are you building or thinking about? Current and planned initiatives._

# My Style
_How do you prefer to work and communicate? Collaboration preferences and constraints._

# External Context
_What else should someone know? Links to blog, social media, portfolio, and key takeaways._

# Metadata
_Profile version, generation info, and data lineage._
```

## 设计意图

把 USER.md 视为**多维度的"可被搜索的索引"** —— 后续匹配 Agent 从不同 Section 搜索和筛选：
- **Identity** → 地理位置、社群归属
- **What I Do** → 领域匹配、话题发现
- **What I Can Offer** → Supply 侧搜索、技能互补
- **What I'm Looking For** → Demand 侧搜索、需求对接
- **My Projects** → 项目找人、合作机会
- **My Style** → 匹配质量、沟通兼容性
- **External Context** → 深度了解、信任建立
- **Metadata** → 数据可信度、更新追踪

## 想请教的问题

1. **覆盖度**：这 8 个 Section 是否覆盖了 Coffee-chat 撮合和组队找人所需的全部关键维度？有没有明显的遗漏？

2. **冗余与重叠**：哪些 Section 之间可能存在信息重叠？例如 "What I Do" 和 "My Projects" 是否太接近？"What I Can Offer" 和 "What I Do" 如何区分边界？

3. **粒度平衡**：对于 Phase-0 MVP（只做首次生成），是否需要 8 个 Section 这么多？哪些可以合并或延后到 Phase-1？

4. **撮合友好性**：从匹配算法的角度看，哪些信息维度是"高信号"（能显著提升匹配质量），哪些是"低信号"（收集成本高但匹配价值低）？

5. **外部对标**：LinkedIn、Twitter、即刻、脉脉等平台的用户画像，有哪些值得借鉴的设计？

6. **Agent 可写性**：哪些 Section 适合 Agent 自动生成（如 External Context），哪些必须用户亲口确认（如 What I'm Looking For）？

请从产品设计 + 信息架构的角度给出分析和建议。

---
