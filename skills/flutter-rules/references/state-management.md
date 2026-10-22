# 技术栈预设族与状态管理（app 预设 A/B/C ＋ plugin 类型 A/B ＋ Riverpod 纪律）

> 2026-09-15 自 app 模板 §8.2 下沉 Riverpod 四条纪律（1.0.10 常驻收敛批；内容源自消费工程实战规范上移——0.1.2）——**选预设 A 时生效**，涉状态管理任务时随本文件按需 Read。
> 2026-10-22 自宪法模板 §七 下沉技术栈预设族全文（app 预设 A/B/C、plugin 类型 A/B——1.3.0 常驻分层批，语义零删减迁入）：**选定结果仍落 `.claude/memory/PROJECT.md` §七**，本文件承载全文与选型注记；预设条目按「最后核验」日期维护（**最后核验：2026-09-05**），栈审视与 skill 坑节维护义务并列，每次 minor 例行刷新。选 B/C 的工程：Riverpod 纪律节不适用，等价规范见文末空位声明。

## app 预设 A：Riverpod + go_router + Dio（现代主流）

- 状态管理：`flutter_riverpod`（优先 `Notifier`/`AsyncNotifier`，避免过时 `StateNotifier`）
- 路由：`go_router`（声明式，`MaterialApp.router`）
- 网络：`dio` + `interceptors`（鉴权/日志/重试）；接口规模大可加 `retrofit`（声明式 codegen 层，与 Dio 非互斥）
- 序列化：`json_serializable` + `build_runner`（`.g.dart` 生成，不手写）
- 本地存储：`shared_preferences`（轻 KV）或 `drift`（结构化）；`hive` 原版已停更（稳定版停于 2022-06）——NoSQL 需求用社区延续 `hive_ce`
- 国际化：官方 `flutter_localizations` + `gen-l10n`（或 `slang`）；`easy_localization` 维护缓慢，不推荐新项目
- 主题/适配：暗黑模式走统一 `ThemeExtension`；适配优先 `MediaQuery` / `LayoutBuilder` 断点方案——`flutter_screenutil` 已停更（2024-05 起）且平板 / 桌面多端有短板（适配细则见 [layout.md](layout.md) 适配节）

## app 预设 B：Bloc + go_router + Dio（事件驱动、强约束）

- 状态管理：`flutter_bloc`（`Bloc`/`Cubit`，事件驱动，适合中大团队）
- 路由：`go_router`
- 网络：`dio`
- 序列化：`freezed` + `json_serializable`（不可变模型 + 联合类型）
- 本地存储：`hive_ce`（hive 原版已停更 2022-06——社区延续版，口径同预设 A 存储注记）
- 国际化：`flutter_localizations` + `intl`

## app 预设 C：Provider + http（仅极端克制依赖时选——整体偏旧，常规项目选 A/B）

- 状态管理：`provider` + `ChangeNotifier`
- 路由：`Navigator 1.0`（命名路由）
- 网络：`http` 包
- 序列化：`dart:convert` 手写 `fromJson`/`toJson`（选 C 即接受手写维护成本——skill 默认 `json_serializable` 生成不手写，此为本预设克制依赖的例外）
- 本地存储：`shared_preferences`
- 国际化：`flutter_localizations` + `intl`

## plugin 类型 A：通用 Flutter plugin（平台能力/原生桥接）

适用于：封装平台能力、原生模块、设备 API、联邦接口（federated）plugin。

特征：

- `pubspec.yaml` 声明 `flutter.plugin.platforms`（android/ios/linux/macos/windows/web）
- 走**联邦接口**：`<name>.dart`（面向端接口）→ `<name>_platform_interface.dart`（抽象）→ `<name>_method_channel.dart`（MethodChannel 实现）→ 原生 `Plugin.kt`/`Plugin.swift`
- 有 `example/` app 仅用于演示和验证插件表面
- 可能含 iOS Podspec / Android Gradle 原生依赖

## plugin 类型 B：工具库风格（纯 Dart 工具模块）

适用于：纯 Dart 工具集合（如 `cutils`：money/format/encrypt/utils…），无或极少平台通道。

特征：

- `lib/<domain>/<module>.dart` 自包含模块，被下游**按全路径直接 import**（如 `package:xxx/num/money_utils.dart`）
- `lib/<name>.dart` 主入口**不一定** re-export 各模块（按需）
- 无平台通道时 `pubspec.yaml` 不声明 `flutter.plugin.platforms`
- `example/` 仅做调用演示
- TDD 极契合（纯函数多）

## Riverpod 四条纪律（选预设 A 时生效）

- **Notifier 模式**：不可变 `State` 类（含 `copyWith`）+ `Notifier<T>`（`build()` 里 `ref.read` 注入依赖，不用过时 `StateNotifier`）
- **Provider 组织（就近原则）**：模块专用 Provider 放模块自己的 `presentation/` 或 `data/`；全局 DAO / API / 用户态等放全局 providers 目录——禁止把模块专用状态挂到全局
- **ConsumerWidget vs ConsumerStatefulWidget（强制）**：当私有方法需要 `ref` 时，**必须用 `ConsumerStatefulWidget`，禁止把 `WidgetRef` 作为参数传给私有方法**（`ref` 作类属性自动可用）；仅 `build` 用 `ref` → `ConsumerWidget`；需 `initState` / `dispose` / 访问构造参数 → `ConsumerStatefulWidget`
- **生命周期**：页面级状态用 `autoDispose`（离开页面释放），全局单例显式不 dispose——策略在 Provider 定义处声明，不在调用处补救

> 等价规范空位（1.3.0 呈裁②随批声明）：预设 B/C、plugin 类型 A/B 的「特有纪律」尚未有消费工程实战源上移（宪法侧 §8.2 同款空位语义）——出现首个对应形态工程时按 §8.2 先例沉淀于本文件。
