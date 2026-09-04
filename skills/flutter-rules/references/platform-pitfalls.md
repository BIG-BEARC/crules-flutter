# 平台坑库（预置首批 · 维护者策展）

> 触发场景：引依赖 / 写平台代码 / 升级 SDK / 平台排障前 Read 本文件。来源：flutter-rules skill「平台坑库」节（B1 瘦身拆出，内容未改）。

> **定位**：框架级通用坑住本节（跨项目复现）；项目相关坑住消费工程 `.claude/memory/platform-pitfalls.md`。项目坑跨项目复现后经 `/crules-flutter:distill` 提名进本节（fork 维护者裁决）。
> **入预置门槛**（满足其一，防 stale 大杂烩）：①我们 / 同行实证踩过 ②官方 issue / release notes 明示版本区间 ③常见矩阵区间内高概率触发。每条带出处与「最后核验」；查不到出处不预置。首批 ≤10 条宁缺毋滥（Android 允许一卡多区间合并）。
> **维护义务**：Flutter / 平台大版本出现 → 扫本节标【待重验】→ 核验刷新——此后每次 minor 的例行内容（「技术栈相关 → 只进本包」查表逻辑）。

## 三方依赖

### [Windows 7] permission_handler 初始化导致启动闪退

- 归属：三方依赖（插件层 permission_handler Windows 实现 + Flutter 引擎层 Windows 桌面支持）
- 触发场景：Win7 目标机上启动即崩（permission_handler 平台初始化路径） ｜ 症状：应用完全无法启动（issue 原文 "nothing, but app can't start"）、无有效日志 ｜ 根因：Flutter 本体仅支持 Windows 10+，维护者不为 Win7 投入支持；早期 Win10 版本同类崩溃源于插件静态链接新版 Win10 API（PR #1389 改动态加载修复「早期 Win10」区间，不覆盖 Win7） ｜ 规避：dependency_overrides 指向 no-op 实现（github.com/localsend/permission_handler_windows_noop）/ fork 插件剔除 Windows 实现 / 不将插件引入 Windows 构建
- 区间：issue #1322 针对 v11.3.1 报告并 Closed as not planned；其他版本区间未查证（官方未声明 Win7 支持矩阵、未见修复版本）——倾向结论：全区间不受支持（官方口径 Win10+），精确闪退区间未查证
- 状态：未修复（Closed as not planned） ｜ 最后核验：2026-09-04
- 出处：实证复盘（升格自原模板样例卡）+ [issue #1322](https://github.com/Baseflow/flutter-permission-handler/issues/1322)（Win7 无法启动，v11.3.1）、[issue #1388](https://github.com/Baseflow/flutter-permission-handler/issues/1388)（旧版 Windows 崩溃）、[PR #1389](https://github.com/Baseflow/flutter-permission-handler/pull/1389)（早期 Win10 崩溃修复：动态加载 API）、[flutter#129716](https://github.com/flutter/flutter/issues/129716)（Flutter 本体在 Win7 崩溃）、[pub.dev](https://pub.dev/packages/permission_handler)

## Flutter SDK

### [iOS 26.x] tabbar / draw 渲染异常

- 归属：Flutter SDK（引擎 / 框架层——iOS 26 Liquid Glass 新 UI 与 Flutter 渲染不匹配）
- 触发场景：iOS 26 真机 / 模拟器上运行 Flutter 应用，涉及 CupertinoTabBar / 绘制类渲染 ｜ 症状：tab bar 样式与 iOS 26 Liquid Glass 不符（内容不延伸到底栏下方）、真机黑屏不渲染、debug 模式不可用等 ｜ 根因：iOS 26 引入 Liquid Glass 新 UI 范式，Flutter 未实现对应视觉 / 过渡特性（官方文档列 iPad 风格 tab bar #150590、liquid glass 支持 #170310 等为「尚未完全实现」；#186572 黑屏关联 Flutter 3.38 的 UISceneDelegate 迁移） ｜ 规避：等待官方实现（跟踪 #170310 / #150590）；社区方案 cupertino_native_better 提供 SwiftUI 原生 Liquid Glass tab bar
- 区间：受影响 Flutter 版本区间 / 修复版本——官方未给数字（截至官方文档 3.47.2 快照未列 affected/fixed 版本），倾向全区间（iOS 26 上）；社区信息称 debug 模式问题自 3.35.x 改善、黑屏与 3.38 迁移相关，但无 issue 内里程碑确认
- 状态：未修复（官方跟踪中） ｜ 最后核验：2026-09-04
- 出处：[Flutter 官方 iOS 26 支持状态文档](https://docs.flutter.dev/platform-integration/ios/ios-latest)、[flutter#150590](https://github.com/flutter/flutter/issues/150590)（iPad 风格 tab bar）、[flutter#170310](https://github.com/flutter/flutter/issues/170310)（liquid glass 支持）、[flutter#186572](https://github.com/flutter/flutter/issues/186572)（iOS 26 真机黑屏）、[cupertino_native_better](https://pub.dev/packages/cupertino_native_better)、[Stack Overflow 79747677](https://stackoverflow.com/questions/79747677/)

### [iOS/Android/Desktop] Impeller 渲染器换代——Skia 时代绕法失效

- 归属：Flutter SDK（引擎层——渲染器自 Skia 换代 Impeller，分平台分批默认）
- 触发场景：渲染异常 / 性能问题排查时套用 Skia 时代老绕法与性能 hack ｜ 症状：老绕法不生效或行为反转、渲染结果与 Skia 时期不一致 ｜ 根因：Impeller 已成默认引擎——**iOS 唯一支持引擎、无切回 Skia 能力**；Android API 29+ 默认（低版本或无 Vulkan 设备回退 legacy OpenGL；`--no-enable-impeller` 仅调试用）；macOS/Linux/Windows 自 **3.47** 默认（官方预告未来移除 opt-out）；Web 仍 Skia ｜ 规避：渲染问题按 Impeller 语境排查不套 Skia 经验；关注官方 migration 指南与 issue；Android 低端机注意 OpenGL 回退路径的行为差异
- 区间：iOS 全区间（唯一引擎）；Android API 29+ 默认（起默认的引擎版本号未逐字核验，官方 availability 节只给现状）；desktop 自 3.47；Web 全区间 Skia
- 状态：现行官方口径 ｜ 最后核验：2026-09-05
- 出处：[Impeller 官方文档 availability 节（3.47 快照逐字核验）](https://docs.flutter.dev/perf/impeller)

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
