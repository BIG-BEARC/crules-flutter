# 测试选型参考（TDD 适用范围分档 + 同构批量红绿）

> 2026-09-15 自双模板 §九「TDD 适用范围」小节下沉（1.0.10 常驻收敛批）——模板常驻面只留指针，涉测试选型 / 补测时随本文件按需 Read；内容逐字迁移未改写。

## App 向（按层分档）

| 代码类型 | TDD 要求 | 「测试」的形式 |
|---|---|---|
| 纯逻辑/工具/数据层（ViewModel、Repository、Service、utils） | **强制 red-green-refactor** | `package:test` 单测 |
| 数据模型/序列化 | 强制 | 单测覆盖 `fromJson`/`toJson` 边界 |
| UI 渲染（widget） | 用 widget test 充当 TDD 的「测试」 | `flutter-add-widget-test`（`WidgetTester`） |
| 完整用户流程 | 不强制每步，关键路径要覆盖 | `flutter-add-integration-test` |
| 既有代码无测试时 | 改动前先补「表征测试」锁住现状，再重构 | — |

> 同构用例集（数据类 / 参数化 / 纯映射）允许批量红绿：全部用例写完 → 一轮 RED → 实现 → 一轮 GREEN（抽 1-2 个断言故意错值确认会红，防恒真断言）；设计驱动型用例保持逐用例。

## plugin 向（公开 API 全覆盖）

plugin 极契合 TDD——大量纯函数和明确的公开 API。**public API 默认全覆盖**：

| 代码类型 | TDD 要求 | 「测试」形式 |
|---|---|---|
| 纯 Dart 工具/算法/格式化 | **强制 red-green-refactor** | `package:test` 单测，边界值全覆盖 |
| 公开 API（public 类/方法/顶层函数） | **强制**，视为回归安全网 | 单测，固定输入→固定输出 |
| 数据模型/序列化 | 强制 | 覆盖 `fromJson`/`toJson` 边界 |
| 平台通道/原生桥接（类型 A） | Dart 侧 mock 测；原生侧在 `example/` 手测 | `setMockMethodCallHandler` mock 通道 |
| 既有无测试代码 | 改动前先补「表征测试」锁现状，再改 | — |

> 同构用例集允许批量红绿（全部用例→一轮 RED→实现→一轮 GREEN，抽查断言有效性防恒真）；superpowers 会**删掉先于测试写的代码**——公开 API 尤其要先用测试钉死行为。
