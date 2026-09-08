# crules-flutter CHANGELOG

## 0.6.7 · 外审收口小批 + 质量脚本唯一入口

- **checklist 6 代码规范 +「质量脚本唯一入口」**：工程自定义 format / analyze / check 脚本即唯一入口，CLAUDE.md / §十二 写明并禁裸跑默认参数命令；排查插件行为先验 hook 加载路径（`hooks/hooks.json` 是否存在），声明文件 ≠ 已加载行为（实证 saas_pos_smart_edition：dart-flutter skill 引导的裸 `dart format` 默认 80 宽 × 工程 120 宽门禁，一次波及 166 文件；首判误归因插件 Stop hook，实为 agent 手动执行——hook 加载路径核验后证伪）
- **0.6.7 批（外审收口小批，计划评审两轮 v2 落地）**：① i18n.md easy_localization 裸并列 → 带「不推荐」注记（外审 G4/Y1 同型残留收口）；② 语义闸 +2 独立断言（test-self 15→**17**）——easy_localization 注记闸 + flutter_screenutil 白名单闸（注记词「已停更或维护缓慢」二选一，评审 🔴 消解）；③ README 新增「5 分钟上手路径」节（Y9，四段导览 + 指针防第三份同源口径）；④ 评审 v2 修订全吸收（PASS 计数口径 / 横幅同步）。**缓记**：Y11 守护覆盖矩阵归 P3（与 A1 溯源闸同批）。

## 0.6.6 · 实战复盘吸收批——报表模块多轮返工 + review 误报 M1/M2 契约定级

> 两份实战复盘（saas-cashier 报表模块，`29f490bae` / `51565c01c`）经 distill 吸收：字段契约靠猜多轮返工与 review 误报 M1/M2 均指向同一本质——**契约只存在于实现行为里，没有被显式化**。

- **reviewer agent 审查纪律 +2 条**：假设性发现必须标验证状态（`已验证（文件:行号）` / `推断（验证路径）`——未验证前提禁止直接给可达性等级，实证：最坏假设直接标 L1，人工核实 5 行代码即证伪）；错误处理类发现先读被调方契约（网络包装 / 拦截器的异常语义——结构对 ≠ 触发对）
- **checklist +3 处**：边界 4 +「调试期空值先显式暴露不加兜底文案」（兜底把字段错位变成「显示为其他」更迷惑的现象，延迟定位）；Git 规范 8 +「多仓 git -C 绝对路径 + push 前 `git remote -v` 核对目标仓」（实战 7 踩：cwd 命令间重置，裸 push 把主仓推出新远端分支）；复刻专项 +「追到 logic / 消费端确认字段服务端返回 vs 前端加工 + 样例响应注释优先」（entity 有字段 ≠ 接口返回）
- **layout.md 列表项 key 节 +治点**：StatefulWidget 常驻不卸载时切换数据源——实例复用致 `initState` 只读一次，挂 `ValueKey(切换侧标识)` 强制重挂 + widget 测试锁死（实证 `29f490bae` 日期滚轮）
- **frontend agent 工作流程 +1 步**：「参考 XX 样式」类需求动手前先确认目标组件 / 截图（实证：仅凭描述 4 轮返工）；动态条数布局先问单条 / 溢出排布
- **双模板实施纪律（跨仓条）扩充**：+`git -C` 一律绝对路径（cd 落位不可信）+ push 前 remote -v 核对——与 checklist 8 同源，双侧同步

## 0.6.5 · 坑卡例行核验刷新——iOS 26.x 与 Impeller 双卡 2026-09-08 复核

- **Impeller 卡**：desktop 3.47 默认经官方 blog 复核属实；+桌面初期阵痛实证 [flutter#191860](https://github.com/flutter/flutter/issues/191860)（Windows 3.47.1 Impeller 启动显著慢于 Skia——桌面升 3.47 启动回归先核此 issue）；最后核验 09-05 → 09-08
- **iOS 26.x 卡**：状态维持「未修复·官方跟踪中」；+社区口径「Flutter 团队不打算在 Cupertino 组件实现 Liquid Glass（设计决策非待修 bug）」标注（以官方 issue 里程碑为准）；`cupertino_native_better` 社区方案活跃维持；最后核验 09-04 → 09-08

## 0.6.4 · saas-cashier 生产实证吸收批——列表 key 错乱 / SP 启动白屏 / 图片解码异常 / Impeller Vulkan 崩溃

> 用户指认三笔生产问题（列表错乱加 key / Windows SP 白屏 / 图片异常），经 saas-cashier 全史 git 检索钉出实证后吸收；点单页库存角标错乱未钉到单笔 commit，按同型多笔实证吸收并如实标注。

- **坑库 +1 卡（8/≤10）**：[三方依赖] shared_preferences 初始化时序与文件损坏——**启动白屏**（SP init 挂起 / 抛错阻塞首帧）/ Android `channel-error`（pigeon channel 窗口期）/ deviceId 种子漂移「升级换号」；规避四条：init 失败降级默认配置继续启动 / 种子数据冻结文件化 / 备份恢复机制 / Android 重试 ×3。实证 `af24988e3` / `4017e21c1` / `4df1c2702` / `f890669f2`
- **Impeller 卡 +实证追加**：saas-cashier `d1a86dc1d`——Android POS 定制设备 Vulkan GPU SIGSEGV，`EnableImpeller=false` 回退 Skia 修复；定制设备 GPU 驱动是回退开关的现实主战场
- **layout.md 新增「列表项 key」节**：库存 / 选中态串行显示的防（key 绑业务 id 禁下标）与治（配置驱动子组件挂 `ValueKey(配置值)` 强制重建）——实证 `31302e77d` / `0111c1d7d` / 点单页库存角标同型
- **checklist 组件节 +1 条**：列表项 key 绑业务 id（涉增删重排时查）
- **performance.md 崩溃钩子 +扩展点实证**：`7d1573584`（生产问题）——Windows 图片解码 `Codec failed` 异常经 `FlutterError.onError` 静默捕获记录，不拖垮 App

## 0.6.3 · 留池四项收口批——性能·CI·监控三空白补域 + 记忆库钩子推广 + plugin §八 实体化

> 0.6.2 留池四项按序收口三项；第四项（POS 垂直拆层 core+pos-vertical）系开源定位裁决项，另行方案。

- **skill 新增两域文件**（`references/performance.md`）：DevTools 双线程归因（UI/Raster 列说话，不凭感觉）/ 图片按显示尺寸解码（`cacheWidth`——低配收银机 OOM 头号常见根因，大图场景必传）/ 低配设备实操序 / `FlutterError.onError` + `PlatformDispatcher.onError` 双钩子与 sentry·crashlytics·自建选型 / 符号化与上报纪律；（`references/build-release.md`）：flavor 与 dart-define 选型（共存多包才上 flavor）/ keystore 与 iOS 证书纪律 / `--obfuscate --split-debug-info` 与 symbols 归档 / App 发布前检查 + pub 发布检查全表。SKILL.md 按域取用表 +2 行
- **checklist**：性能节 +2 条（大图按显示尺寸解码 / 全局错误钩子在位）；新增「构建 / 发布专项」条件条 3 项（symbols 归档+混淆首跑回归 / 密钥不入库+环境值集中 / 发布前检查表）
- **记忆库钩子推广（软约定显式化）**：frontend/backend/platform/i18n/error/reviewer 六 agents 统一 +「记忆库联动」行（涉业务规则 / 不变量 / 惯用模式先 Read `business-rules` / `INVARIANTS` / `patterns`——防重复发明与破坏不变量）；plan-reviewer 原有对读保留
- **plugin 模板 §八 实体化**：平台通道选型（结构化多端对等优先 **Pigeon**——两侧签名漂移的机械化方案）+ pub 发布检查 4 项（dry-run 零警告 / semver 与 CHANGELOG 一致 / Kotlin↔Swift 对等与 federated 同步 / example 可跑 + 净工程拉取实测）——原为纯占位

## 0.6.2 · 🟢 轻微项清池批 + 外部复核必修批——审查留池全清 + 语义闸上闸

> [审查 §四](docs/审查-2026-09-05-时效性与合适性.md) 🟢 9 条：2 条已随 0.5.0 瘦身消化，7 条本批清；随后外部复核（AI-coding 侧）抓出必修 3 + 漂移 2，同批修并上闸。**两轮审查留池至此全空。**

- **必修（外部复核，全部核验属实）**：checklist:78 触控目标错标纠正——`48dp（Material/Android 最低推荐）/ 44pt（Apple HIG·iOS）`（原 44×44 误标 Material）；frontend.md + app §十 两处 screenutil 正面残留清除（改指 §七 所选方案——0.6.2 首轮只修了 checklist 漏了执行面）；app 预设 B 裸 `hive` → `hive_ce`（0.5.1 栈审视刷了 A 漏了 B 的同文件矛盾）
- **漂移修复**：README 横幅 0.5.2 → 0.6.2（滞后三个版本）；help.md hooks ×2 → ×3（0.5.2 stop-reminder 漏计——自称权威全表恰最不该漂）
- **语义闸上闸（test-self 第 15 断言）**：README 横幅版本 ↔ plugin.json 分发版本一致 / help hooks 数 ↔ `hooks/*.py` 实际数一致 / 停更栈禁推（agents 无 screenutil 推荐、app 无未注记裸 hive）——把本轮 grep 级可检的漂移形态机械化看守；首跑即抓到自注记误伤，口径与 hive 一致排除「停更」注记行
- **过度绝对化软化**：layout.md「不要混用 Expanded/Flexible」→ 合法常见写法 + 明确弹性意图（外部复核 🟡 采纳项）；app 预设 C 手写序列化 + 边界注记（skill 默认生成不手写，此为克制依赖例外）
- **🟢 轻微项 7 条**：checklist:45 `Selector` 按方案对号（provider `Selector` / Riverpod `select`）｜agents ×7 `§2`→`§二（提交策略）` 15 处｜error.md「修复」→「诊断与修复建议」｜platform.md 职责 + Web｜app 预设 C 注「仅极端克制依赖时选」｜memory/reference-map 三行餐饮示例压一行占位｜AO 头注 +flutter_lints 大版本复查
- **使用面同步补遗（0.6.0 漏同步）**：README「装完必填三处」① 与 init 引导补**适配方案三选一 + 字体策略**（公共必选）；README 升级节新增**跨版本迁移要点表**（≤0.3→0.4 checklist 重排与记忆库接线 / 0.5→0.6 两必填环节补答 / 任意跨度 memory 只对照不强合）——老工程合并 `.new` 此前只有机械三步、无合并要点指引
- **留池（独立裁决项，非本批）**：性能 profiling / CI·发布（flavor·签名·混淆·符号化）/ 线上崩溃监控三领域空白；POS 垂直内容拆 core+pos-vertical（开源定位裁决）；patterns/INVARIANTS 机械钩子推广；plugin §八 Pigeon/发布检查补位

## 0.6.1 · 审查留池收尾批——S16 checklist 补节 + S9-S11 关闭核验

> 审查文档（[时效性与合适性审查](docs/审查-2026-09-05-时效性与合适性.md)）留池项收尾：S9-S16 全部关闭，仅余 🟢 轻微项随日常维护消化。

- **S16**：checklist Flutter 专项补「无障碍」（对比度 / Semantics / 字体放大可用性 / 触控目标 ≥44-48dp）与「性能」（builder 懒加载 / 重活不落 build+Isolate.run / controller 与订阅释放）两小节——审查侧对齐 skill A11Y 声称的覆盖面
- **S11**：theming.md 对比度行补「WCAG 2.2」版本号（数值与 2.1 相同，纯口径）
- **S9/S10/S15 关闭核验**（对新结构重跑，随本批记入审查文档头注）：`compute(` 零命中、审美说教零命中（均随 0.5.0 瘦身消化）；google_fonts 分场景已由 0.6.0 A5 落地
- **审查文档头注刷新**：S1-S16 处置状态全量回填（此前 S9-S11 待重跑 / S13-S16 待裁决）

## 0.6.0 · 吸收与模板演进批——适配三选一 + 字体策略 + IoT 抽层 + 订单折算吸收

> minor 口径：模板**交互环节**变更（§七新增必选环节、文件头规则语义反转），非纯内容增补——沿 0.5.0「模板交互变化升 minor」先例。依据链：[适配方案](docs/方案-2026-09-08-适配三选一与字体策略.md)（评审终裁：仅 app 落正文 / 三档断点）· [IoT 抽层方案](docs/方案-2026-09-08-IoT外设知识抽层.md) · [订单折算吸收方案](docs/吸收方案-2026-09-05-订单折算复盘.md)（落点按 0.5.2 基线修订）· [实施计划](docs/实施计划-2026-09-08-0.6.0批.md)（评审两意见轮全采纳）

- **模板（app）**：§七 新增「屏幕适配方案【复制后三选一】」——A1 弹性优先+断点（三档 Compact<600/Medium<840/Expanded≥840，默认推荐）/ A2 设计稿缩放（screenutil ~28 个月无稳定版注记）/ A3 自定义；8.1 新增「字体策略（公共·必选）」四要素（字体打包 / 统一注入点禁内联 TextStyle / fontFamilyFallback / 设备字形转图兜底）——实证源 saas-cashier 三笔（bbf976e42 Android Roboto 全字重 / 0508ac9b5 Windows 普惠体 / 656558508 内联绕过复发）+ flutter#154166/#145069
- **模板（plugin）**：§八 +1 行指针（适配/字体属 App 形态课题，example 按模板 §七对号）——不落正文，防孪生守护（`###` 子节不入节序号集，C4 实证）
- **文件头 S13 渗漏修正（双模板）**：@Author 五件套从模板正文撤下 →「默认跟随项目现状」——存量带头循既有格式（不含 @Email，作者权威在 git）、无头不加、惯例不一致问一次落附录；plugin:254 @Author 文档头同步改写
- **checklist（5 处）**：:47 改「按 §七 所选方案对号审查」（解 screenutil 点名与模板 A1 默认的 🔴 矛盾）；:80 「暗黑 / 按所选方案适配」；组件/视图节 +2 字体条（统一注入点 / 打包字体+fallback）；**R1-R3 半句并入**（金额展示铁律→9 ｜ 窄屏极值→4 ｜ iOS 生成文件 pathspec→8）+ **R4 新增「复刻 / 折算专项」条件条**（一个控件查两遍 + 像素对齐对象界定 + 6.2 复跑）+ 0.6.0 差集标注
- **skill（订单折算吸收 C1-C4）**：layout.md +2 bullet（Row 内 Text ellipsis 须先包 Flexible/Expanded；UAX#14 无断词点长串逐字符 Wrap）；platform-pitfalls.md +2 卡（三方依赖 Riverpod defunct 三板斧——区间如实标未查证；Flutter SDK 系统字体回退不可信）——坑库 5→7 卡仍 ≤10 配额
- **skill（IoT 抽层 S14）**：新建 `references/iot-devices.md`——backend 角色卡「设备通信铁律」7 条迁入升格 + 8 类设备分节框架（外设按通信方式 / 多屏 / 独立 App 指针节），实证 3 处（173e731c1 网口漏打连发间隔 / aaa9995fd 文字转图 / db82458e5 全半角）；backend.md 铁律节 → 一行指针；error.md:26 通用表述保留 + 指针半句；theming.md google_fonts 分场景（**离线/内网设备禁运行时拉取**，字体打包 assets）；SKILL.md 按域取用表 +1 行
- **fork-coverage**：§六节题改「边界记账」通用名 + 追加 0.6.0 行（S13 公司制度渗漏修正 / S14 IoT 抽层 / 本批通用机制不反哺 crules）

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
