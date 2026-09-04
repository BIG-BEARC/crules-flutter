# crules-flutter CHANGELOG

## 0.5.2 · 清池批——A3 Stop 读侧闭环 + D3 hooks 降级链 + D2 + E 组打磨

- **A3 漂移队列读侧闭环**（复核之复核 §5 自守卫版）：新 Stop hook [stop-reminder.py](hooks/stop-reminder.py)——队列非空经 `additionalContext` 注入事实提醒（模型可据此补索引），`stop_hook_active` 自守卫防连环续轮（官方：与 decision:block 共享同一套 8 次上限——勘A 修正落地），文案事实陈述 <10k 字符；fixture 五态全绿（无队列/空队列/连环轮抑制/非空出提醒/坏输入）入 test-self；hooks.json +Stop 事件——pending-updates 写侧（PostToolUse）与读侧（Stop）闭环合龙，**新会话生效**
- **D3 hooks 降级显式化**：install.sh 双级警告（无 python3=三 hooks 全失效 / 缺 fcntl=仅漂移队列降级）+ pending-updates.py fcntl 条件导入（Windows 降级无锁 `O_APPEND` 追加——单行写原子性兜底，从「装了白装」变「降级可用」）+ README 环境要求措辞对齐
- **D2 standalone 缓解**：两模板 §九 +「未装 superpowers/dart-flutter 时本节可忽略」（叠加协作非前置依赖）
- **E1** README 升级命令空匹配守护（原 zsh glob 失败静默产出 `SRC=/..`）；**E2** install.sh 复制/写入失败计错不虚报（汇总 +失败数，非零退出）；**E4** CI 链接检查步（坑卡出处 404/410/5xx 红，反爬与限流态放行；本地预跑 21 条全绿）；**E5** 七 agents 默认 `model` 档位（i18n=haiku / frontend·backend·platform·error=sonnet / reviewer·plan-reviewer=opus）+ Agent编排 维护注（档位名随可用模型演进）
- **池清空**：三审裁决表全回填；余 B2/B3（常驻瘦身+基线实测）按裁决等真实试点观测后单开

## 0.5.1 · 留池裁决批——C2 三坑卡 + C1 预设栈刷新 + D1 双模板孪生守护

- **C2 坑库补强**（skill `references/platform-pitfalls.md`）：Android 基线卡扩两区间——**16KB page size**（Play 期限原 2025-11 延至 **2027-02-01**；Flutter 3.38 起默认 `ndkVersion` = NDK r28，3.38 blog 原句验真）与 **edge-to-edge 强制**（targetSdk 35 强制 / Android 16 豁免移除 + Flutter `SystemUiMode` 破坏性变更——沿用旧 opt-out 在 Android 16+ 可能崩溃，复核之复核「新3」落实）；新增 **Impeller 换代卡**（iOS 唯一引擎无 Skia 回退 / Android API 29+ 默认 / desktop 自 3.47 默认 / Web 仍 Skia——官方 availability 节逐字核验）；全部官方出处 + 最后核验 2026-09-05
- **C1 预设栈刷新**（app §七）：存储 hive→`shared_preferences`/`drift`（原版停更 2022-06 注记 + `hive_ce` 延续）、国际化 easy_localization→官方 `gen-l10n`/`slang`（维护缓慢不推荐）、适配 screenutil→`MediaQuery`/断点优先（停更 2024-05 + 多端短板注记）——五包 pub.dev 版本 2026-09-05 逐一核验；§七 头部加「最后核验」字段，**栈审视义务**入 README 维护节（与坑节义务并列，每次 minor）
- **D1 双模板孪生守护**：test-self 新断言（节序号集 + §一/三/四/五/六 条数一致；§二 plugin 独有「发版特殊性」条目系合法不对称、豁免注明）——**装闸即抓真漂移**：plugin §四 缺「静默失败验到现象层」条目（example assets 热重载同样适用），同批补齐
- **裁决记录**（选项卡 2026-09-05）：C1/C2/D1 进本批；A3（Stop hook 读侧自守卫版）留池；B2/B3（常驻瘦身+基线实测）等真实试点观测后单开

## 0.5.0 · B1 skill 瘦身拆分（三审裁决 P1 首批·skill-creator 流程执行）

- **结构**：SKILL.md 850 行/39.2KB 单文件 → **薄索引 33 行/4.3KB** + `references/` 四域文件（design-doc 方案骨架+配图 / platform-pitfalls 坑库 / theming / layout），合计 249 行/17.8KB——**触发加载 −89%**（progressive disclosure 官方三級形态：metadata 常驻 / 触发载索引 / 按域 Read）；维护者侧内容（坑库维护义务）随迁出消费侧常驻
- **删除账本**：通用最佳实践段删除（基线导言 persona / Interaction Guidelines / Package Management / Code Quality / Dart & Flutter Best Practices / API Design / Architecture / Lint 样例 / State-Routing-Serialization-Logging 代码长例 / 视觉设计铺陈）——2026 年模型已内化 + 与 lint 基线、模板 §十重复；项目特有内容（骨架 / 坑库 / 配图 / 优先级与降级机制）全保留，恢复源 = git 历史
- **指针修复 4 处**：app/plugin 模板方案 Gate 行与 help.md 场景表直指 `references/design-doc.md`；app §8.1 风格细则指针改写（原目标内容已删——通用归 lint 基线硬拦，细节按需查 theming/layout）
- **A/B 评测**（skill-creator 流程，3 场景 × 新旧版子代理对照）：**13 断言双绿**（内容可达性无损、按域路由三题全对、浓缩版 theming.md 扛住 lerp/copyWith 全例复用）+ 新版耗时均值 **−16.7%**（290.3/141.8/452.9 vs 330.2/243.1/489.7s）；断言全程序化判定——完整记录见 [docs/评测-2026-09-05-skill瘦身AB对照.md](docs/评测-2026-09-05-skill瘦身AB对照.md)
- **description 触发优化（不采纳·如实记载）**：20 条应触/不应触查询经 skill-creator run_loop 跑 3/5 轮即止损终止——三轮 Test recall 全钉 0–8% 地板（precision 100% 系「几乎不触发」另一面），**判定为评测查询设计与参考库型 skill 的结构性不适配**（文档化现象：模型对一行问答型查询凭内化知识直答、不咨询 skill——A/B 评测 6 子代理在「查规范」语境下均正确读取本 skill，真实消费触发正常），候选 description 全部从噪声中选出故不采纳、保留现版；教训：触发评估的应触查询须为**多步实质任务**。完整记录见 [评测文档 §5](docs/评测-2026-09-05-skill瘦身AB对照.md)

## 0.4.1 · 三审裁决 P0 批——lint 死配置修复 + 记忆库接线 + retrofit 主次排序

> 依据链：[外审](docs/外审-2026-09-04-0.4.0整体评审与优化方向.md) → [复核](docs/复核-2026-09-04-外审0.4.0逐条核实与勘误.md) → [复核之复核](docs/复核之复核-2026-09-05-复核文档勘误.md)（三审全实测/官方文档双源核验）；裁决记录见外审 §7

- **A1**：`analysis_options.yaml` 删两行死配置——`cancelled_token_use`（analyzer 诊断名非 lint 规则，3.5/3.47.2 双验 undefined_lint）与 `public_member_api_docs: false`（flutter_lints 未启用的空 disable，map 形态条目且扰动列表解析致报警行号偏移），意图注释保留（CancelToken 纪律落点 checklist 异步纪律节，custom_lint 二期候选）；test-self 增「AO 内容过真 analyzer 零 warning」断言（本机无 dart 时 SKIP）+ ci.yml 增 setup-dart 步硬拦——0.2.3 F2「真样本」教训对 AO **内容侧**补完闭环
- **A2**：两 CLAUDE.md 模板 §十二 +「记忆库接线」节——`@.claude/memory/NAVIGATION.md` 启动内联（最小集；MAINTENANCE/patterns/INVARIANTS 等保持涉域前 Read，**不整库 @import**——prose 引用不加载，经官方文档确证）；init 步骤4 +接线确认项（NAVIGATION 占位表裁剪联动）；memory README / 记忆库体系 twin 表「加载时机」列对齐事实；记忆库体系「会话开始时加载」示例块改 @ 语法——0.4.0 记忆体系从「装而不用」变真加载
- **E3**：flutter-rules description「重叠处以 skill 为准」→「以 dart-flutter skills 为准」（指代消歧）
- **R2**：app §七 预设 A 网络行改主次排序——`dio` + `interceptors` 默认，接口规模大可加 `retrofit`（声明式 codegen 层，与 Dio 非互斥；复核勘4 确证其活跃维护）
- **环境坑修复（bash 5.3，验证阻断）**：`set -u` 下 `$var` 紧邻多字节字符（中文标点）时 bash 5.3+ 会把多字节首字节吸入变量名致 **unbound 中止**（brew 2026-09-05 升级 bash 5.3.15 后实测炸出——install.sh 汇总行中止于文件已写完之后、exit 127；CI ubuntu bash 5.2 未触发故此前无感）——install / check-imports / test-self 共 12 处全部改 `${var}` 花括号隔离（LC_ALL=C 与花括号均免疫；v59 BSD grep 环境坑同款教训，注记于 test-self 头部）
- **裁决状态**：B1（skill 瘦身拆分·默认中档）已裁走官方 skill-creator 执行，P1 启动；B2/B3/C1 余项/C2/D1/A3/D2/D3/E1-E5 留池待裁（外审 §7 表）

## 0.4.0 · 易用性与知识沉淀体系（设计方案 v2.1 落地）

- **命令 ×3 新增**：`/help`（场景使用地图）/ `/distill`（沉淀定稿闸——五问 / 闸表 / 三操作 / 档位 / 坑卡归属）/ `/diagram`（存量文档补图，常驻文件拒加图）——与 init / update-memory 组成 5 命令面板
- **memory 模板 6 → 8**：`reference-map.md`（分域参考系，只存指针不存结论）+ `platform-pitfalls.md`（支持矩阵【装完必填·第三处】+ 结构化坑卡带**归属**字段：OS 平台 / Flutter SDK / 三方依赖 / 未定性）；NAVIGATION / MAINTENANCE / memory README / 记忆库体系 twin 表同步 +2
- **init 必填两处 → 三处**：+支持矩阵**三段式自动初稿**（①机械读：平台目录 + minSdk + Podfile，kts 变体 / 失败保留占位符并报告 → ②人核对 → ③人补实测上限）；install.sh「下一步」echo 同步
- **两 CLAUDE.md 模板**各四处改：完成定义 +review 结论与沉淀候选判据 / 方案 Gate +骨架指针行 / 依赖红线 +坑库×矩阵步 / §三 +收尾时序注（两模板同源对照改）
- **脚本**：check-imports +memory 演进提示（源侧新增 + git 两版本 diff，不做目标全量比对）；test-self 扩三断言（8 模板 / 三处必填 / twin 一致性）；.gitignore 补 `__pycache__/`
- **skill**（批 2）：方案骨架全文（裁剪档位 / 图型 / Gate 映射 / 行业参考槽位 / 6.2 自测用例表）+ 配图约定 + 平台坑节**预置首批**（三归属分节：Win7 permission_handler / iOS 26.x / Android 基线一卡多区间，每条带出处与最后核验；[调研记录](docs/调研-2026-09-04-平台坑预置首批.md) 15 链接抽查属实，查不到出处的按未查证不预置）+ description 补「写设计方案」触发词
- **review 增强**（批 2）：checklist 差集标注增补（吞异常形态学 / 资损红线新增为条目 9 / 关键节点日志 / 敏感交叉 / 边界 Flutter 化 / 兼容性硬判据 / 机械项归位）；审查纪律 +「review 主工位与范围」节；工程化流程 §5 时序对齐（复验 = 重跑构建 + 重审）+ §7 模板并入 Review 结论位 / 沉淀候选位
- **README 使用面重写**（批 3）：5 命令面板 + 场景地图（与 `/help` 同源，双侧同步义务）+ 收尾时序 sequence 图；落位物表 memory 6→8（点名 `reference-map` / `platform-pitfalls`）；必填两处→三处（+支持矩阵三段式）；维护节 + skill 坑节维护义务 + 沉淀闸蜜月期说明
- **示范与记账**（批 3）：进阶配图示范两处（方案评审闭环 flowchart / Agent编排 sequenceDiagram）；[fork-coverage §六](docs/fork-coverage.md) 0.4.0 边界记账（通用机制不反哺母版 / 技术栈相关只进本包）

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
