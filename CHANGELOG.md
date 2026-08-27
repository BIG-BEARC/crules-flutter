# crules-flutter CHANGELOG

## 0.1.3 · 批 3a 修复——skill 目录归位

- **`skills/flutter-rules/`**：SKILL.md 从 `.claude/skills/`（项目级约定）移至 plugin 根级 `skills/`（plugin 组件约定）——批 3a 消费侧首验抓出 Skills(0) 未挂载，plugin details 复验修复

## 0.1.2 · 批 3a——saas_pos 实战规范上移（§八两小节落地）

- **`app/CLAUDE.md` §八**：8.1 全栈通用（多 package assets 加载 / 文件头注释 / Import 排序——代码风格细则归 flutter-rules skill 不双份）+ 8.2 预设 A 特有（Notifier 模式 / Provider 就近组织 / ConsumerWidget 强制禁传 ref / autoDispose 策略——标「选 A 时生效」）；适用面判定 9 条入 [fork-coverage §三](docs/fork-coverage.md)；项目架构与业务域知识不上移（批 3b 下沉消费工程记忆库）

> 记能力级变化；fork 基线 crules `v74-fork-base`（ea4d25c）。版本口径：semver=分发版本，批号为实施批次。

## 0.1.0 · 批 2 收官（内容整合完成）

- **两模板本尊化**（批 2a）：app/plugin CLAUDE.md 重组为十二节——通用协作层（红线/提交/双 Gate/验证证据/完成定义/后台 diff）fork 自基线并修复旧孪生漂移（v50 安全红线、v51 提交语义分离等 6+ 条）；§八专项规范立占位（批 3 上移）；覆盖 diff 验收 [docs/fork-coverage.md](docs/fork-coverage.md)（全量 78% / 裁剪 18% 已归位进阶 / 场景替换 4%，无静默丢失）
- **知识层**（批 2b）：checklist 自持（通用 8 大类 + Flutter 专项）；进阶 5 篇 fork（链接重定位）；memory 6 模板 + agents 通用 3 角色落位（共 7 角色）；rules.md skill 化（flutter-rules，Testing 节去重留指针）
- **基建层**（批 2c）：hooks 三件 fork + `SYNCED-FROM: crules@ea4d25c` 戳；CI 四步含 **deny-list 同步比对**（crules 单一权威机械化看守）；scripts 三件（install --app/--plugin + 戳 + 护栏 / check-imports / release）；test-self 四断言（含 deny-list 幂等）

## 0.0.1 · 批 1（骨架）

- 建仓 + plugin 骨架 + README（种子库关系 / 共存指引 / 停用恢复）

## 0.1.1 · 批 2c 复盘整合

- **`app/CLAUDE.md` / `plugin/CLAUDE.md` 实施纪律各 +1 条**：「跨仓/跨目录操作一律绝对路径（cwd 会话间重置，实战 6 踩曾污染母版）+ 特殊字面串文件用专用写工具（防 deny-list 误拦）+ 跨仓收尾 git status 验零污染」——源：[docs/复盘-2026-08-27-批2c双坑.md](docs/复盘-2026-08-27-批2c双坑.md)
