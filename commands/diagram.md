---
description: 给存量人读文档补 mermaid 图——按内容形态选图型；AI 常驻文件（CLAUDE.md / memory）拒加图
---

# /crules-flutter:diagram <文件>

给**已存在的人读文档**补图（新方案写作时直接用 flutter-rules skill「方案骨架」的图型标注，不必事后补）。

## 图型对照

| 内容形态 | 图型 |
|---|---|
| 流程 / 决策 | flowchart |
| 调用链 / 交互时序 | sequenceDiagram |
| 数据模型 | erDiagram |
| 状态流转 | stateDiagram |
| 演进编年 | timeline |
| 规则 / 枚举 / 对比 | 表格（不是 mermaid） |
| 命名 / 协议 / 正则 | 代码块（不是 mermaid） |

## 流程

1. Read 目标文件，找「纯文字描述结构 / 流程 / 时序」的段落
2. 按上表选型；已有文字保留（图是增效不是替代），图插在段落**之后**
3. mermaid 语法自查：节点 / 箭头 / 引号闭合——渲染不出 = 未完成
4. 呈现 diff 给需求方过目后才算完（定位是「人工审后补图」）

## 守门（机械分支，先于一切）

- 目标命中 **根 CLAUDE.md / `.claude/memory/*`**（AI 常驻上下文文件）→ **显式拒绝并说明原因**（图对 AI 无增益、白耗每会话 token），不静默跳过
- 一次一个文件；全文重构式改写**禁止**（只插图不改写正文）
