# 平台坑库（预置首批 · 维护者策展）

> 触发场景：引依赖 / 写平台代码 / 升级 SDK / 平台排障前 Read 本文件。来源：flutter-rules skill「平台坑库」节（B1 瘦身拆出，内容未改）。

> **定位**：框架级通用坑住本节（跨项目复现）；项目相关坑住消费工程 `.claude/memory/platform-pitfalls.md`。项目坑跨项目复现后经 `/crules-flutter:distill` 提名进本节（fork 维护者裁决）。
> **入预置门槛**（满足其一，防 stale 大杂烩）：①我们 / 同行实证踩过 ②官方 issue / release notes 明示版本区间 ③常见矩阵区间内高概率触发。每条带出处与「最后核验」；查不到出处不预置。首批 ≤10 条宁缺毋滥（Android 允许一卡多区间合并）。
> **维护义务**：Flutter / 平台大版本出现 → 扫本节标【待重验】→ 核验刷新——此后每次 minor 的例行内容（「技术栈相关 → 只进本包」查表逻辑）。

## 三方依赖

### [Windows 7] Flutter SDK 版本上限——3.19 为最后支持线（升 SDK 前判死线）

- 归属：OS 平台（Windows 7/8）× Flutter SDK 桌面支持策略
- 触发场景：目标机含 Win7/8 却把 Flutter SDK 升过 3.19 ｜ 症状：3.22+ 构建产物在 Win7 上无法运行（引擎依赖提升至 Win10 API 线）｜ 根因：官方将 Win7/8 移入 unsupported tier、最低要求提至 Windows 10 ｜ 规避：目标含 Win7 → SDK 钉 **3.19.x 末位 patch（3.19.6）**；或接受自维护成本走社区 fork（RustDesk 自改 engine 续命先例，有持续维护负担）；新项目直接放弃 Win7 目标
- 区间：**3.19（2024-02，Dart 3.3）= 最后一个支持 Win7/8 的 stable**；3.22 起最低 Windows 10（3.19→3.22 间无其他 stable，3.19.6 即事实上限）；3.20/3.21 beta 线未查证
- 状态：官方既定政策（不可逆） ｜ 最后核验：2026-09-10
- 出处：[flutter#140830](https://github.com/flutter/flutter/issues/140830)（官方 tracking issue：Move Windows 7 and 8 to unsupported tier）+ [Flutter 3.19 release blog](https://flutter.dev/blog/whats-new-in-flutter-3-19)（ending support for Windows 7/8）+ [RustDesk fork 实录](https://rustdesk.com/blog/how-to-make-flutter-3-24-run-on-windows-7)；关联坑卡：permission_handler Win7 闪退（同根因——引擎层 Win10+ 依赖）

### [Android 4.x] Flutter SDK 版本上限——3.22 起最低 API 21（KitKat 4.4 及更早同线阵亡）

- 归属：OS 平台（Android KitKat 4.4 / API 19 及更早）× Flutter SDK 支持策略
- 触发场景：目标机含 Android 4.x / 5.x / 6.x（收银 / 门店平板存量设备常见）却把 Flutter SDK 升过对应死线 ｜ 症状：构建产物在低版本设备上**无法安装**（实证：saas-cashier master_new 以 3.38.10 构建，生产 Android <7.0 全部装不上——minSdkVersion 随 `flutter.minSdkVersion` 解析为 24）｜ 根因：官方分两步提下限：3.22 弃 4.x（→API 21）、**3.38 弃 5.x/6.x（→API 24）** ｜ 规避按目标钉版本：含 Android 6.x 及以下 → **3.35.x**；含 4.x → **3.19.6**（与 Win7 同钉法，混合存量可合并决策）；纯 7.0+ 目标 → 无约束。**注意**：`minSdkVersion = flutter.minSdkVersion` 会随构建机 SDK 漂移——多机 / CI 构建时下限不锁就会静默跳线，存量设备装不上往往到分发才发现
- 区间（三段死线）：3.22 起最低 **API 21**（弃 KitKat 4.4 及更早）；**3.38 起最低 API 24**（弃 Android 5.0/5.1/6.x——3.35.x = 最后可跑 5/6 的 stable）；本机 SDK 源码实证：3.19.6=19、3.27.4=21、3.38.10=24。插件下限可高于本体（如部分一方插件随 3.38 对齐 API 24+，flutter_local_notifications 提至 26）——引依赖前查其 minSdk
- 状态：官方既定政策（3.22 与 3.38 两段均已落地） ｜ 最后核验：2026-09-10
- 出处：[官方 breaking change 文档](https://docs.flutter.dev/release/breaking-changes/android-kitkat-deprecation)（KitKat 弃用）+ [Flutter 3.38 release blog](https://flutter.dev/blog/whats-new-in-flutter-3-38)（minSdkVersion → API 24+）+ [#170807](https://github.com/flutter/flutter/issues/170807)（API 24 计划 tracking，经 PR #179795 收口）+ **生产实证**（saas-cashier master_new · 3.38.10 构建 · Android <7.0 无法安装，2026-09）；关联坑卡：Win7 SDK 上限（同 3.19.6 钉法）

### [Windows 7] permission_handler 初始化导致启动闪退

- 归属：三方依赖（插件层 permission_handler Windows 实现 + Flutter 引擎层 Windows 桌面支持）
- 触发场景：Win7 目标机上启动即崩（permission_handler 平台初始化路径） ｜ 症状：应用完全无法启动（issue 原文 "nothing, but app can't start"）、无有效日志 ｜ 根因：Flutter 本体仅支持 Windows 10+，维护者不为 Win7 投入支持；早期 Win10 版本同类崩溃源于插件静态链接新版 Win10 API（PR #1389 改动态加载修复「早期 Win10」区间，不覆盖 Win7） ｜ 规避：dependency_overrides 指向 no-op 实现（github.com/localsend/permission_handler_windows_noop）/ fork 插件剔除 Windows 实现 / 不将插件引入 Windows 构建
- 区间：issue #1322 针对 v11.3.1 报告并 Closed as not planned；其他版本区间未查证（官方未声明 Win7 支持矩阵、未见修复版本）——倾向结论：全区间不受支持（官方口径 Win10+），精确闪退区间未查证
- 状态：未修复（Closed as not planned） ｜ 最后核验：2026-09-04
- 出处：实证复盘（升格自原模板样例卡）+ [issue #1322](https://github.com/Baseflow/flutter-permission-handler/issues/1322)（Win7 无法启动，v11.3.1）、[issue #1388](https://github.com/Baseflow/flutter-permission-handler/issues/1388)（旧版 Windows 崩溃）、[PR #1389](https://github.com/Baseflow/flutter-permission-handler/pull/1389)（早期 Win10 崩溃修复：动态加载 API）、[flutter#129716](https://github.com/flutter/flutter/issues/129716)（Flutter 本体在 Win7 崩溃）、[pub.dev](https://pub.dev/packages/permission_handler)

### [全平台] Riverpod Notifier dispose 后 defunct 崩溃三板斧

- 归属：三方依赖（riverpod）× Flutter 框架层（Element 生命周期）
- 触发场景：`Notifier`/`AsyncNotifier` 页面级状态，dispose 后仍有在途异步回调 / postFrame 回调触发 `ref` 写入或 setState ｜ 症状：`setState() called after dispose()` / 「cannot use 'ref' after the widget was disposed」断言崩溃（实证：delivery_order_notifier.dart:189） ｜ 根因：finalizeTree 先于 postFrameCallbacks；在途异步写入落在已 defunct 的 Element 上 ｜ 规避三板斧：①dispose 首行落存活闸门（bool）+ try-catch ②`postFrameCallback` 内 `if (!mounted) return` ③在途异步写入统一被闸门拦截（写前判活）
- 区间：框架断言机制全区间；riverpod 特定版本区间**未查证**（无单一 canonical issue——[flutter#73000](https://github.com/flutter/flutter/issues/73000) 为框架层同类断言、[riverpod discussion #3043](https://github.com/rrousselGit/riverpod/discussions/3043) 为最接近的官方讨论；按入预置门槛①实证预置，区间字段如实标）
- 状态：现行框架行为 ｜ 最后核验：2026-09-08
- 出处：实证复盘（订单折算复盘吸收 C3，见 CHANGELOG 0.6.0 条）+ flutter#73000 + riverpod discussion #3043

### [Android/Windows] shared_preferences 初始化时序与文件损坏——启动白屏 / 数据漂移

- 归属：三方依赖（shared_preferences 及其平台实现）
- 触发场景：`main()` 里 `await` SP 初始化后 `runApp`；SP 文件损坏 / 被旧版本改写；Android 冷启动 pigeon channel 未就绪即访问 ｜ 症状：**启动白屏**（SP init 挂起或抛错 → 首帧永不出——Windows 实证）；`channel-error: Unable to establish connection on channel`（Android 实证）；deviceId 等种子数据漂移、升级后「换号」（Windows 实证） ｜ 根因：SP 是启动路径上的单点阻塞且 Windows 实现文件易损；Android 侧 `shared_preferences_android` pigeon channel 初始化有窗口期 ｜ 规避四条：①**SP init 失败降级默认配置继续启动**（try-catch + 默认值，不阻塞首帧——`Global.init()` 同样包 try-catch 兜底）②SP 关键种子数据（deviceId 类）**冻结文件化**：文件 > SP 一次性迁移 > 现场采集，文件存在且非空永不覆盖 ③SP 读写封装带**备份恢复机制** ④Android 冷启动访问 SP 加**重试**（3 次 × 100ms 实证值）
- 区间：实证于 saas-cashier（Windows / Android POS 双端，2025-11~2026-08）；插件官方版本区间**未查证**（按入预置门槛①实证预置）
- 状态：现行 ｜ 最后核验：2026-09-08
- 出处：实证 saas-cashier `af24988e3`（SPUtil 备份恢复 + init 失败降级启动）/ `4017e21c1`（Android channel 重试）/ `4df1c2702`（deviceId 种子冻结文件化）/ `f890669f2`

## Flutter SDK

### [iOS 26.x] tabbar / draw 渲染异常

- 归属：Flutter SDK（引擎 / 框架层——iOS 26 Liquid Glass 新 UI 与 Flutter 渲染不匹配）
- 触发场景：iOS 26 真机 / 模拟器上运行 Flutter 应用，涉及 CupertinoTabBar / 绘制类渲染 ｜ 症状：tab bar 样式与 iOS 26 Liquid Glass 不符（内容不延伸到底栏下方）、真机黑屏不渲染、debug 模式不可用等 ｜ 根因：iOS 26 引入 Liquid Glass 新 UI 范式，Flutter 未实现对应视觉 / 过渡特性（官方文档列 iPad 风格 tab bar #150590、liquid glass 支持 #170310 等为「尚未完全实现」；#186572 黑屏关联 Flutter 3.38 的 UISceneDelegate 迁移） ｜ 规避：等待官方实现（跟踪 #170310 / #150590）；社区方案 cupertino_native_better 提供 SwiftUI 原生 Liquid Glass tab bar
- 区间：受影响 Flutter 版本区间 / 修复版本——官方未给数字（截至官方文档 3.47.2 快照未列 affected/fixed 版本），倾向全区间（iOS 26 上）；社区信息称 debug 模式问题自 3.35.x 改善、黑屏与 3.38 迁移相关，但无 issue 内里程碑确认
- 状态：未修复（官方跟踪中；2026-09-08 复核——社区口径称 Flutter 团队**不打算**在 Cupertino 组件实现 Liquid Glass（设计决策非待修 bug，[Stackademic 报道](https://blog.stackademic.com/flutter-wont-ship-liquid-glass-support-your-ios-26-app-is-stuck-in-2024-40a26af9b8fc)——以官方 issue 里程碑为准）；社区原生方案 `cupertino_native_better` 活跃（含 TabBar） ｜ 最后核验：2026-09-08
- 出处：[Flutter 官方 iOS 26 支持状态文档](https://docs.flutter.dev/platform-integration/ios/ios-latest)、[flutter#150590](https://github.com/flutter/flutter/issues/150590)（iPad 风格 tab bar）、[flutter#170310](https://github.com/flutter/flutter/issues/170310)（liquid glass 支持）、[flutter#186572](https://github.com/flutter/flutter/issues/186572)（iOS 26 真机黑屏）、[cupertino_native_better](https://pub.dev/packages/cupertino_native_better)、[Stack Overflow 79747677](https://stackoverflow.com/questions/79747677/)

### [iOS/Android/Desktop] Impeller 渲染器换代——Skia 时代绕法失效

- 归属：Flutter SDK（引擎层——渲染器自 Skia 换代 Impeller，分平台分批默认）
- 触发场景：渲染异常 / 性能问题排查时套用 Skia 时代老绕法与性能 hack ｜ 症状：老绕法不生效或行为反转、渲染结果与 Skia 时期不一致 ｜ 根因：Impeller 已成默认引擎——**iOS 唯一支持引擎、无切回 Skia 能力**；Android API 29+ 默认（低版本或无 Vulkan 设备回退 legacy OpenGL；`--no-enable-impeller` 仅调试用）；macOS/Linux/Windows 自 **3.47** 默认（官方预告未来移除 opt-out）；Web 仍 Skia ｜ 规避：渲染问题按 Impeller 语境排查不套 Skia 经验；关注官方 migration 指南与 issue；Android 低端机注意 OpenGL 回退路径的行为差异
- 区间：iOS 全区间（唯一引擎）；Android API 29+ 默认（起默认的引擎版本号未逐字核验，官方 availability 节只给现状）；desktop 自 3.47；Web 全区间 Skia
- 状态：现行官方口径 ｜ 最后核验：2026-09-08（desktop 3.47 默认经官方 blog 复核属实；desktop 初期阵痛实证：[flutter#191860](https://github.com/flutter/flutter/issues/191860) Windows 3.47.1 Impeller 启动显著慢于 Skia——桌面升级 3.47 后启动回归先核此 issue）
- 出处：[Impeller 官方文档 availability 节](https://docs.flutter.dev/perf/impeller) + [3.47 官方 blog](https://flutter.dev/blog/whats-new-in-flutter-3-47)｜**实证追加（2026-09-08）**：saas-cashier `d1a86dc1d`——Android POS 定制设备 Vulkan GPU native crash（SIGSEGV），`AndroidManifest` `EnableImpeller=false` 回退 Skia 修复——无 Vulkan / 驱动残缺的定制设备是回退开关的现实主战场（白屏 / 崩溃排障时先核设备 GPU 驱动）

### [Android/Windows/macOS] 系统字体回退不可信——跨端字重/字形异常

- 归属：Flutter SDK（引擎字体回退机制）× OS 平台（OEM ROM 字体裁剪 / 桌面缺中文字体）
- 触发场景：未显式打包字体、依赖系统字体回退的跨端 App；OEM 机型（ColorOS 等）/ Windows POS 设备 ｜ 症状：部分 Android 机型字重只剩两档（实证 Flutter 3.24.3）；Windows 中文渲染异常（实证 2022 起） ｜ 根因：Android 端未指定 fontFamily 时走系统回退，OEM ROM 裁剪/替换 Roboto 与中文字体（#154166：3.22.x 起 ColorOS 非英文字体仅两档字重）；Windows 默认中文字体不可用 ｜ 规避四要素：①关键字体打包进 app（Android：Roboto 全字重；桌面：指定中文字体，pubspec 显式声明 family 与字重映射）②统一注入点（平台条件 fontFamily 走统一 TextStyle 工厂/getter，**禁内联 TextStyle**——内联即绕过注入）③`fontFamilyFallback` 显式声明兜底链 ④打印等设备无法渲染的字形（维语/阿拉伯语等）文字转图兜底
- 区间：Android 自 Flutter 3.22.x（#154166 报告口径，实证 3.24.3）；桌面长期
- 状态：引擎回退机制现行，未变 ｜ 最后核验：2026-09-08
- 出处：实证三笔（saas-cashier `bbf976e42` Android Roboto 全字重打包 / `0508ac9b5` Windows 普惠体打包 / `656558508` 内联绕过复发修复）+ [flutter#154166](https://github.com/flutter/flutter/issues/154166)（ColorOS 字重裁剪）、[flutter#145069](https://github.com/flutter/flutter/issues/145069)（跨平台渲染不一致）、[官方自定义字体 Cookbook](https://docs.flutter.dev/cookbook/design/fonts)

## OS 平台

### [Android] 版本兼容基线（一卡多区间合并）

- 归属：OS 平台（Android 平台 / 系统策略层）
- 覆盖：
  1. **Scoped storage**：targetSdkVersion 29+（Android 10）起分区存储生效；API 29 可用 `requestLegacyExternalStorage` 临时豁免，Android 11 起强制
  2. **Photo picker**：系统级照片选择器原生随 Android 11（API 30）+ 提供，backport 到 Android 4.4（兼容库，经 Google Play services / ActivityResult）
  3. **Predictive back（返回手势）**：Android 13（API 33）引入预测性返回手势；targetSdk 34+ 对部分组件行为有强制要求（强制细节未逐字核验）
  4. **16KB page size**：Google Play 要求 targetSdk 35+ 的 64 位应用支持 16KB 内存页，原期限 2025-11-01 已延至 **2027-02-01**（届时不分 targetSdk 全量适用；延期申请通道至 2026-05-31）；含原生 `.so` 的 plugin 须对齐编译——Flutter 引擎默认 `ndkVersion` 自 3.38 起为 **NDK r28**（官方口径：native code 16KB 对齐的最低要求）
  5. **Edge-to-edge 强制**：targetSdk 35（Android 15）起系统强制全面屏绘制（`setStatusBarColor` 等失效）；Android 15 可 `windowOptOutEdgeToEdgeEnforcement` 临时退出，**Android 16（targetSdk 36）豁免移除**；Flutter 侧配套破坏性变更——默认 `SystemUiMode` 改 edge-to-edge，沿用旧 opt-out 机制的 Flutter 应用在 Android 16+ 可能崩溃
- 症状：越过基线后旧存储 API 失效 / 权限模型变化 / 返回手势行为差异 / Play 上架被 16KB 拦截 / 状态栏遮挡或崩溃 ｜ 规避：按官方文档采用 MediaStore / photo picker / OnBackPressedDispatcher + predictive back 声明；16KB 升级 Flutter ≥3.38（自有 `.so` 用 NDK r28 重编对齐）；edge-to-edge 改 `enableEdgeToEdge` + insets 适配并跟随 Flutter SystemUiMode 新默认
- 状态：官方文档口径（API 29 / 33 / 35 / 36 关键锚点；16KB 期限 2027-02-01）；photo picker 与 predictive back 细节部分未逐字核验 ｜ 最后核验：2026-09-05
- 出处：[Android 11 存储隐私](https://developer.android.com/about/versions/11/privacy/storage)、[存储总览](https://developer.android.com/training/data-storage)、[photo picker](https://developer.android.com/training/data-storage/shared/photopicker)、[预测性返回手势](https://developer.android.com/guide/navigation/predictive-back-gesture)、[16KB page size 要求与期限](https://developer.android.com/guide/practices/page-sizes)、[Android 15 行为变更](https://developer.android.com/about/versions/15/behavior-changes-15)、[Android 16 行为变更（豁免移除）](https://developer.android.com/about/versions/16/behavior-changes-16)、[Flutter 3.38（NDK r28 默认）](https://flutter.dev/blog/whats-new-in-flutter-3-38)、[Flutter SystemUiMode 破坏性变更](https://docs.flutter.dev/release/breaking-changes/default-systemuimode-edge-to-edge)
