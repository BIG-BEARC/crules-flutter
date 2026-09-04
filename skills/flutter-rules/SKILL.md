---
name: flutter-rules
description: Flutter/Dart 技术最佳实践参考——写/审 Flutter 代码时查找风格、架构、主题、布局、颜色、字体、无障碍等规范细节用；写设计方案 / 出方案时用「方案骨架」（references/design-doc.md）；引平台依赖、写平台代码、升级或排障时查「平台坑库」（references/platform-pitfalls.md）。与 dart-flutter skills 重叠处以 dart-flutter skills 为准，本 skill 是补充参考（清单/规范类内容为主，按域拆 references/ 分文件按需 Read）。
---

# AI rules for Flutter（crules-flutter 技术参考库）

> **定位**：Dart/Flutter 技术参考的**薄索引**——触发只载本文件，具体内容按域 Read `references/` 分文件（progressive disclosure：本 skill 曾是 39KB 单文件，问状态管理会把字体对比度一并拖入上下文）。
> **优先级（重要）**：与项目根 CLAUDE.md **§七技术栈约定 / §八专项规范** 冲突时，**以项目模板为准**——项目选型（Riverpod/Bloc/Provider、路由、序列化）压过本库通用偏好；状态管理与路由方案永远看项目 §七。
> **与 dart-flutter 插件的分工**：执行类内容（测试/分析/生成/修错/路由配置/序列化操作步骤）归 dart-flutter skills（映射见项目 CLAUDE.md §十一速查表），本库只留它不覆盖的规范、清单与项目特有内容。
> **MCP 工具降级**：文中 `dart_format` / `analyze_files` / `pub_dev_search` 等工具不存在时，用等价 CLI（`dart format` / `dart analyze` / `flutter pub add` + pub.dev 检索）替代。

## 按域取用（references/）

| 场景 | Read | 内容 |
|---|---|---|
| 写设计方案 / 出方案 / PRD | [references/design-doc.md](references/design-doc.md) | 方案骨架（章节模板 / 裁剪档位 / Gate 映射 / 6.2 自测用例表生命周期 / 行业参考查证纪律）+ 配图约定（图型对照 / AI 常驻文件不加图） |
| 引依赖 / 写平台代码 / 升级 SDK / 平台排障 | [references/platform-pitfalls.md](references/platform-pitfalls.md) | 平台坑库（三归属坑卡带出处与最后核验 / 入预置门槛 / 维护义务——维护者侧内容也在此，不占消费侧常驻） |
| 主题 / 颜色 / 字体 / 暗黑 / Material 3 / A11Y | [references/theming.md](references/theming.md) | ThemeExtension 设计令牌（copyWith/lerp 全例）/ ColorScheme.fromSeed / WidgetStateProperty / WCAG 对比度 / Semantics / google_fonts |
| 布局 / Overflow / 叠层 / 浮层 | [references/layout.md](references/layout.md) | Expanded-Flexible-Wrap 边界 / 滚动容器选型 / Stack 定位 / OverlayPortal 浮层全例 |

## 索引级速记（跨场景高频、一行可答的留这里）

- **lint 基线**：项目根 `analysis_options.yaml`（本包装载时落位）——规则与 checklist 条目的对应关系见该文件内注释；静态分析执行走 dart-flutter `dart-run-static-analysis`（零 warning 是硬门）
- **State Management / Navigation 未指定时**：优先 Flutter 内置（`ValueNotifier`/`ChangeNotifier` + `ValueListenableBuilder`、`Navigator`）；三方包仅在明确要求时引入——项目已选型时本条不适用（永远看项目 §七）
- **JSON 序列化**：`json_serializable`（`@JsonSerializable(fieldRename: FieldRename.snake)`）+ `build_runner` 生成，不手写；改模型后必跑 `dart run build_runner build --delete-conflicting-outputs`
- **结构化日志**：`dart:developer` 的 `log`（name/error/stackTrace 分级）——禁 `print`（lint 已拦，抽查即可）
- **文档注释**：`///` 一句话总结 + 空行分段；注释放注解**之前**；getter/setter 只文档其一；不为显然实现写复述性注释
- **私有 Widget 优于返回 Widget 的私有方法**（build 拆分同理）；长列表一律 `.builder` 构造

## 已删内容说明（B1 瘦身 · 2026-09-05）

通用最佳实践段（基线导言 persona / Interaction Guidelines / Package Management / Code Quality / Dart & Flutter Best Practices / API Design / Architecture / Lint 样例 / State-Routing-Serialization-Logging 代码长例 / 视觉设计铺陈）已删——2026 年模型已内化，边际价值趋零且触发即全量加载。删除清单与理由见 CHANGELOG；恢复源 = git 历史。项目特有内容（骨架 / 坑库 / 配图 / 优先级与降级机制）全部保留并按域拆分。
