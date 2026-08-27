---
description: 记忆库全量刷新兜底（对照 NAVIGATION 逐索引核对源码现状，增量修正）
disable-model-invocation: true
---

# /crules-flutter:update-memory

触发 `.claude/memory/` 全量刷新。适用于：长期未维护、或批量重构后索引大面积失效时兜底。日常维护仍以「写代码顺手更新」为最高优先（见 `.claude/memory/MAINTENANCE.md` 触发表）。

## 执行步骤

1. 读 `.claude/memory/NAVIGATION.md`，获取全部索引清单
2. 扫描源码目录，与各 `indexes/*.md` 现状对比
3. 对每个索引：新建/重命名/删除的源文件 → 更新清单表；过期条目（源已删仍记）→ 删除；复用提示失效 → 修正
4. 有影响多模块的未记录决策 → 补 `decisions/YYYY-MM-DD-<slug>.md`
5. 更新各索引「最后更新」日期
6. 输出更新摘要（改了哪些索引、增删多少条目）

## 注意

- 本命令是**兜底**，不替代顺手更新；全量刷新不是重写——仍守「只记是什么/在哪里，不记完整 API、不复制代码」
- 未启用记忆库（无 NAVIGATION.md）时提示先跑 `/crules-flutter:init`
