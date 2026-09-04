---
description: crules-flutter 使用地图——什么场景用什么（命令 / agents / skill / hooks / 模板全景 + 收尾时序）
---

# /crules-flutter:help

> **同源声明**：本文件与 README「怎么用 / 工程接入与升级」节**同源**——本文件为权威全表、README 为压缩视图，语义级同步（防新孪生漂移）。

## 场景 → 动作 → 用什么

| 场景 | 动作 | 用什么 |
|---|---|---|
| 新工程接入 | 装规则 + 必填引导 | `/crules-flutter:init`（三处必填：§七 / §十二 / 支持矩阵） |
| 日常开发 | 双 Gate 走流程 | 根 `CLAUDE.md` §三；superpowers 可叠加（brainstorming / writing-plans / TDD） |
| 写设计方案 | 套骨架 + 配图 | **flutter-rules** skill「方案骨架」节（裁剪档位 / 图型对照 / Gate 映射） |
| 引依赖 | 坑库×矩阵筛 | `.claude/memory/platform-pitfalls.md`（T1）+ skill 平台坑节 |
| 写平台代码 | 涉域查坑 | 坑库（T2）+ skill 平台坑节（预置首批） |
| 交付收尾 | review + 自测 + 沉淀 | `checklist.md` + 收尾时序（下图）；沉淀候选 `/crules-flutter:distill` |
| 升级（SDK / 依赖） | 区间穿越 | 坑库筛「归属=Flutter SDK」（T3）+ 重跑相关自测用例 |
| 知识维护 | 蒸馏 / 刷新 | `/crules-flutter:distill --scope <需求>`；`/crules-flutter:update-memory` |
| 排障 | 错误排查 | `crules-flutter:error` agent + 坑库检索 |
| 存量文档补图 | 图型对照补 mermaid | `/crules-flutter:diagram <文件>` |

## 收尾时序（review 主工位）

```mermaid
sequenceDiagram
    participant AI as AI(主控)
    participant R as reviewer
    participant U as 需求方
    AI->>AI: 机械验证(build/test/lint)
    AI->>R: review(diff+引用链, checklist)
    R-->>AI: 发现与建议(只报告)
    AI->>AI: 修复→复验(重跑构建+重审受影响部分)
    AI->>U: 交付汇报(review结论+证据+沉淀候选计数)
    U-->>AI: 确认+授权提交(feat+docs 两笔)
```

## 全景（plugin 自动挂载，无需复制）

- **命令 ×5**：init / update-memory / help / distill / diagram
- **agents ×7**：frontend / backend / i18n / platform / error / reviewer / plan-reviewer（出场时机见 `进阶/Agent编排.md`）
- **skill**：flutter-rules（技术规范参考 + 方案骨架 + 平台坑节）
- **hooks ×2**：deny-list（PreToolUse 安全闸）/ pending-updates（PostToolUse 同步提示）（供应链说明见 README）
- **模板**：根 CLAUDE.md（App / Plugin 二选一）+ checklist + 进阶 5 篇 + memory 8 模板
