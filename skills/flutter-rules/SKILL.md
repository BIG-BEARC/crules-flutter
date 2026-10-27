---
name: flutter-rules
description: Flutter/Dart 技术最佳实践参考——写/审 Flutter 代码时查找风格、架构、主题、布局、颜色、字体、无障碍等规范细节用；技术栈预设族全文（app 预设 A/B/C＋plugin 类型 A/B——原双模板 §七，1.3.0 下沉）与状态管理纪律用 references/state-management.md、testing.md（TDD 适用范围）；分层架构用 references/architecture.md；通用与 plugin 专项规范用 references/general.md；写设计方案 / 出方案时用「方案骨架」（references/design-doc.md）；引平台依赖、写平台代码、升级或排障时查「平台坑库」（references/platform-pitfalls.md）；选 dart-flutter skill 时查「dart-flutter skill 速查」节。与 dart-flutter skills 重叠处以 dart-flutter skills 为准，本 skill 是补充参考（清单/规范类内容为主，按域拆 references/ 分文件按需 Read）。
---

# AI rules for Flutter（crules-flutter 技术参考库）

> **定位**：Dart/Flutter 技术参考的**薄索引**——触发只载本文件，具体内容按域 Read `references/` 分文件（progressive disclosure：本 skill 曾是 39KB 单文件，问状态管理会把字体对比度一并拖入上下文）。
> **优先级（重要）**：与项目技术栈约定（`.claude/memory/PROJECT.md` §七——宪法 §七预设的所选档）冲突时，**以项目落点为准**——项目选型（Riverpod/Bloc/Provider、路由、序列化）压过本库通用偏好；状态管理与路由方案永远看 PROJECT.md §七。
> **与 dart-flutter 插件的分工**：执行类内容（测试/分析/生成/修错/路由配置/序列化操作步骤）归 dart-flutter skills（场景映射见本文件「dart-flutter skill 速查」节——1.0.10 自双模板 §十一下沉），本库只留它不覆盖的规范、清单与项目特有内容。
> **MCP 工具降级**：文中 `dart_format` / `analyze_files` / `pub_dev_search` 等工具不存在时，用等价 CLI（`dart format` / `dart analyze` / `flutter pub add` + pub.dev 检索）替代。

## 按域取用（references/）

| 场景 | Read | 内容 |
|---|---|---|
| 写设计方案 / 出方案 / PRD | [references/design-doc.md](references/design-doc.md) | 方案骨架（章节模板 / 裁剪档位 / Gate 映射 / 6.2 自测用例表生命周期 / 行业参考查证纪律）+ 配图约定（图型对照 / AI 常驻文件不加图） |
| 引依赖 / 写平台代码 / 升级 SDK / 平台排障 | [references/platform-pitfalls.md](references/platform-pitfalls.md) | 平台坑库（三归属坑卡带出处与最后核验 / 入预置门槛 / 维护义务——维护者侧内容也在此，不占消费侧常驻） |
| 主题 / 颜色 / 字体 / 暗黑 / Material 3 / A11Y | [references/theming.md](references/theming.md) | ThemeExtension 设计令牌（copyWith/lerp 全例）/ ColorScheme.fromSeed / WidgetStateProperty / WCAG 对比度 / Semantics / google_fonts |
| 布局 / Overflow / 叠层 / 浮层 / 屏幕适配 / 字体策略 | [references/layout.md](references/layout.md) | Expanded-Flexible-Wrap 边界 / 滚动容器选型 / Stack 定位 / OverlayPortal 浮层全例 / 适配三选一（A1/A2/A3）/ 字体策略（1.3.0 自双模板 §七 下沉） |
| 技术栈预设族（app 预设 A/B/C＋plugin 类型 A/B）/ 状态管理 | [references/state-management.md](references/state-management.md) | 预设族全文与选型注记（1.3.0 自双模板 §七 下沉）/ Notifier 模式 / Provider 就近组织 / ConsumerWidget vs ConsumerStatefulWidget 强制 / autoDispose 生命周期（选 A 时生效） |
| 分层 / 架构纪律 | [references/architecture.md](references/architecture.md) | app 分层架构（MVVM/Repository）/ plugin 架构纪律与类型 A/B 额外纪律（1.3.0 自双模板 §十 下沉） |
| 通用工程规范 / plugin 专项 | [references/general.md](references/general.md) | app 全栈通用（assets / 文件头 / import 排序）/ plugin 专项（平台通道选型 / pub 发布检查）（1.3.0 自双模板 §八 下沉） |
| 测试选型 / 补测（TDD 适用范围） | [references/testing.md](references/testing.md) | App 按层分档表 + plugin 公开 API 全覆盖表 / 同构批量红绿细则 / 自产用例五维自查 |
| 接入 / 调试打印机（蓝牙 / USB / 网口 / 内置 / 标签）、打印排障 | [references/printer.md](references/printer.md) | 打印域（蓝牙·USB·网口链路卡 / 打印专项跨链路 / 一体机内置 / 标签 TSPL） |
| 接入 / 调试电子秤、数字客显、串口设备排障 | [references/scale.md](references/scale.md) | 秤·客显串口设备域（串口 RS232 公共底座 / 电子秤含 USB 秤 / 数字客显——平行双实现并为一文件） |
| 扫码枪 / 扫码盒接入、盲扫与 HID 排障 | [references/scanner.md](references/scanner.md) | 扫码域（USB HID 键盘流 / 盲扫与业务面） |
| 外设通用铁律、钱箱、副屏、语音播报、KDS | [references/iot-devices.md](references/iot-devices.md) | IoT 枢纽（通用铁律 / 外设域文件地图 / 钱箱 / 副屏 / 语音播报 / KDS 指针——打印 / 秤客显 / 扫码三域已拆分独立文件） |
| MQTT / 消息推送接入 / 推送到达性排障 | [references/network-comms.md](references/network-comms.md) | 网络通信域（连接生命周期·重连重订 / 订阅与 QoS·分发面 / 业务到达性案卷 / broker 配置安全） |
| 卡顿 / 内存 / 低配设备 / 线上崩溃 | [references/performance.md](references/performance.md) | DevTools 双线程归因（UI/Raster 列说话）/ 图片按显示尺寸解码（低配 OOM 头号根因）/ FlutterError + PlatformDispatcher 双钩子 / 符号化依赖 |
| 配 CI / 出包 / 签名 / 混淆 / 发 pub 包 | [references/build-release.md](references/build-release.md) | flavor 与 dart-define 选型 / keystore 与 iOS 证书纪律 / symbols 归档 / App 发布前检查与 pub 发布检查 |
| 支付 / 退款 / 核销 / 涉钱接口 | [references/payment.md](references/payment.md) | 防重三层口径（判定线 / 请求号语义警示）/ 不可逆操作时序 / 重试红线 |

## dart-flutter skill 速查（1.0.10 自双模板 §十一下沉）

**App 向**（App 工程）：

| 场景 | 调用 skill |
|---|---|
| 新项目/重构做分层 | `flutter-apply-architecture-best-practices` |
| 配置 go_router 声明式路由 | `flutter-setup-declarative-routing` |
| 初始化国际化 | `flutter-setup-localization` |
| REST 请求 | `flutter-use-http-package`（轻量）或按技术栈用 Dio |
| 模型序列化 | `flutter-implement-json-serialization` |
| 适配手机/平板 | `flutter-build-responsive-layout` |
| 修 overflow/unbounded 等布局错 | `flutter-fix-layout-issues` |
| 组件级测试 | `flutter-add-widget-test` |
| 端到端测试 | `flutter-add-integration-test` |
| 组件可视化预览 | `flutter-add-widget-preview` |
| 跑静态分析 | `dart-run-static-analysis` |
| 写单测 | `dart-add-unit-test` |
| 包版本冲突 | `dart-resolve-package-conflicts` |
| switch 表达式/模式匹配 | `dart-use-pattern-matching` |
| 主构造函数 | `dart-use-primary-constructors` |

**plugin 向**（plugin / 工具库工程）：

| 场景 | 调用 skill |
|---|---|
| 写/补单测 | `dart-add-unit-test` |
| 跑静态分析（零 warning） | `dart-run-static-analysis` |
| 机械性 lint 自动修 | 配合 `dart fix --apply` |
| 收集测试覆盖率 | `dart-collect-coverage` |
| 包版本冲突 | `dart-resolve-package-conflicts` |
| switch 表达式/模式匹配 | `dart-use-pattern-matching` |
| 主构造函数 | `dart-use-primary-constructors` |
| 迁移到 `package:checks` | `dart-migrate-to-checks-package` |
| 模型序列化 | `flutter-implement-json-serialization` |
| 生成 mock（unit test） | `dart-generate-test-mocks` |
| FFI 绑定生成（类型 A 原生） | `dart-use-ffigen` |
| 打包 C/C++ 为代码资产（类型 A） | `dart-setup-ffi-assets` |
| 修运行时错误（配合 LSP/热重载） | `dart-fix-runtime-errors` |
| 构建命令行工具（若 plugin 含 CLI） | `dart-build-cli-app` |

## superpowers＋dart-flutter 协作（1.3.0 自双模板 §九 下沉）

| 层 | 插件 | 职责 |
|---|---|---|
| 流程层 | **superpowers** | brainstorming→writing-plans→worktree→TDD→subagent→verification→review→finishing 工程闭环 |
| 技术层 | **dart-flutter** | App：每个 Flutter 任务怎么写对（架构/路由/i18n/测试/序列化/响应式）；plugin：Dart/Flutter 任务怎么写对（测试/分析/模式匹配/序列化/FFI） |
| 工具层 | **dart-flutter** Dart MCP + Stop hooks | 暴露 Dart 工具；会话停止自动 `dart-format` + `dart-analyze` |

> 未装 superpowers / dart-flutter 时本节可忽略——本节定义的是叠加协作，非前置依赖。

**核心心智模型**：superpowers 说「做什么」（先写失败测试→看它失败→写最小实现），dart-flutter 说「Flutter/Dart 里怎么做」。两者分层，**不冲突**。**触发规则**：每个任务开始前先检查是否有 skill 适用（superpowers 的 1% 规则）。

### TDD 适用范围

App / plugin 按层分档表与同构批量红绿细则见 [references/testing.md](references/testing.md)——涉测试选型 / 补测时按需加载。plugin 极契合 TDD——大量纯函数和明确的公开 API，**public API 默认全覆盖**。

## 索引级速记（跨场景高频、一行可答的留这里）

- **lint 基线**：人择采纳后的项目 `analysis_options.yaml`（建议稿 `.claude/memory/analysis-options.suggested.yaml`——1.1.5 起人择并入，规则与插件 cache `checklist.md` 条目的对应关系见建议稿内注释）；静态分析执行走 dart-flutter `dart-run-static-analysis`（零 warning 是硬门）
- **State Management / Navigation 未指定时**：优先 Flutter 内置（`ValueNotifier`/`ChangeNotifier` + `ValueListenableBuilder`、`Navigator`）；三方包仅在明确要求时引入——项目已选型时本条不适用（永远看 PROJECT.md §七）
- **JSON 序列化**：`json_serializable`（`@JsonSerializable(fieldRename: FieldRename.snake)`）+ `build_runner` 生成，不手写；改模型后必跑 `dart run build_runner build --delete-conflicting-outputs`
- **结构化日志**：`dart:developer` 的 `log`（name/error/stackTrace 分级）——禁 `print`（lint 已拦，抽查即可）
- **文档注释**：`///` 一句话总结 + 空行分段；注释放注解**之前**；getter/setter 只文档其一；不为显然实现写复述性注释
- **私有 Widget 优于返回 Widget 的私有方法**（build 拆分同理）；长列表一律 `.builder` 构造

## 已删内容说明（B1 瘦身 · 2026-09-05）

通用最佳实践段（基线导言 persona / Interaction Guidelines / Package Management / Code Quality / Dart & Flutter Best Practices / API Design / Architecture / Lint 样例 / State-Routing-Serialization-Logging 代码长例 / 视觉设计铺陈）已删——2026 年模型已内化，边际价值趋零且触发即全量加载。删除清单与理由见 CHANGELOG；恢复源 = git 历史。项目特有内容（骨架 / 坑库 / 配图 / 优先级与降级机制）全部保留并按域拆分。
