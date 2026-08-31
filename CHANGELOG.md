# crules-flutter CHANGELOG

## 0.3.0 · 跟随 crules v77——外部行为准则残差 3 条镜像

- **`app/CLAUDE.md` / `plugin/CLAUDE.md` 实施纪律各 +3 条**（跟/不跟查表：跟则 bump minor）：**假设显式化**（开工前列关键假设标注已核实/推断）/ **清理自身孤儿**（自身改动产生的失效 import/变量/函数同批清，预存死代码只报告）/ **更简方案推回**（更简路径提出而非擅自改，采纳归需求方）——措辞按本包精简风格镜像，源为 crules 母版 v77（karpathy-guidelines 残差吸收，整包不吸收理由见母版 CHANGELOG v77）

## 0.2.4 · README 使用文档补全发版

- **README「工程接入与升级」节新增**：落位物表（AO 三态 / memory 永不覆盖）/ agents 不复制说明 / 装完必填两处（§七三选一 + §十二附录）/ 项目模板升级三步命令（check-imports → install --force 出 .new 伴生 → 人工合并）/ `/crules-flutter:update-memory` 兜底——README 使用面与 0.2.2/0.2.3 实际行为对齐（此前落后两版）；状态行刷至外审四轮收口（f8d3084）

## 0.2.3 · 三轮外审 F1/F2 收口

- **F1** AO 判定重写：剥注释签名（`grep -vE '^[[:space:]]*#|空行'` 后非空行 ⊆ {flutter_lints include / linter: / rules:}，**白名单允许缩进**）——原 ≤6 行判定对真机 flutter create 的 28 行注释版无效，UPGRADE 曾是死代码（外审真机实测坐实）；修复过程自身再犯两小错（if/elif 拧反、白名单漏缩进的 `  rules:`），真机 fixture 三场景首验当场抓当场修
- **F2** 真机 28 行脚手架产物签入 `scripts/testdata/scaffold-analysis_options.yaml` + **test-self 扩至 8 断言**（+真脚手架→UPGRADE / 自定义→SIDE-CAR / force→memory KEEP+.new）——手工 E2E 固化回归，「测过了还要确认测的是真样本」教训落机制

## 0.2.2 · 二轮外审 N1-N6 收口 + 消费态首验补课

- **N1** `commands/init.md` 源定位改 **glob 自发现**（cache 最大版本）——`${CLAUDE_PLUGIN_ROOT}` 在 Bash 工具环境为空（实测），cache 用户原走死路
- **N2+N5** `install.sh` 三态写入：--force 改**安全升级**（模板类出 `.new` 伴生待人/AI 合并，不原地打爆已填内容）；**memory/ 永不覆盖**（含 --force）——制度资产语义
- **N3** analysis_options 智能落位：flutter create 脚手架特征（≤6 行纯 include）→ 升级替换留 `.scaffold-bak`；有自定义 → 落 `.crules-flutter.yaml` 伴生提示合并；头注修错（flutter_lints 须在 dev_dependencies，缺依赖 analyzer 静默跳过 include）
- **N4/N6** SKILL 第四处 Built-in 残留改写；memory 两文件裸命令改 `/crules-flutter:update-memory`
- **消费态首验补课**（外审总评采纳）：模拟 flutter create 壳从 cache/工作区真跑——首验当场再抓一个方法错：**cache 里是旧版脚本**（未 bump 先验 cache = 验旧不验新，v31 纪律重犯）；工作区版三场景全绿（脚手架 UPGRADE / force 出 .new 且 memory KEEP / 自定义 lint SIDE-CAR）

## 0.2.1 · 外审 #5——commands 化

- **`commands/init.md` 新增**（plugin 分发 → `/crules-flutter:init`）：分流（新项目 / 老项目无戳不自动装 / 有戳版本差）→ 跑 install.sh 机械安装 → 引导 §七必填与 §十二附录——消灭手动 install 步骤（外审 #5 推荐项）
- **`commands/update-memory.md` 新增**（→ `/crules-flutter:update-memory`）：记忆库全量刷新兜底命令（此前 #4 改为手动兜底的命令化回归）
- README「怎么用」②步改命令入口

## 0.2.0 · 外审 P1 收口轮（五项）

- **#2** `release.sh draft` 修复：CHANGELOG 路径 docs/→根 + 段头日期式→版本式（按顶部版本对应发版 commit 取边界，无锚 fallback 最近 10 条）；test-self 补 draft 断言（外审②）
- **#4** 失效引用清零：5 处「模板包同级 ../flutter/」→ 项目根 checklist.md；§十二两模板补 checklist 行；update-memory 指名改手动兜底；memory 两文件 crules 措辞；README 状态刷新（外审④）
- **#6** **agents 分发改 plugin-only**：install.sh 停止复制 agents（plugin 自动挂载 7 角色——消灭双通道 AUTO-SYNC 孪生，外审⑤），实测项目内无 agents 目录
- **#3** SKILL.md 预设适配：头部「与项目 §七/§八 冲突以项目模板为准」+ State Management / Navigation / 反三方默认三处矛盾改写 + 双 H1 修复 + MCP 工具降级注（外审③⑨）
- **#7** **lint 基线首期**：`analysis_options.yaml` 模板（flutter_lints + strict 三开关 + 规则对应 checklist 条目标注），install.sh 复制（项目已有则保留）；custom_lint 深度工具化留二期（外审⑧）

## 0.1.4 · CI 首跑红修复——同步比对剥戳逻辑

- **`ci.yml` 同步比对步**：剥戳从 `tail -n +2`（从第2行起=保留戳，错位）改 `sed '2d'`（删第2行戳，shebang 后）——CI 首跑红抓出的实现 bug，本地以 `git show origin/main` 模拟比对验证一致（v48「CI 首跑红→根因修复」同款先例）

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
