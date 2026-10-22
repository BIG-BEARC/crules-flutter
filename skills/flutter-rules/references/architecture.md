# 分层与架构纪律（app 分层架构＋plugin 架构）

> 2026-10-22 自宪法模板下沉（1.3.0 常驻分层批，语义零删减迁入）：app 模板 §十（分层架构纪律）、plugin 模板 §十 架构纪律（通用＋类型 A/B 额外）。涉分层 / 架构任务时 Read 本文件，不常驻。**公开 API 稳定性（plugin 红线级）未下沉**——仍在宪法 §十。

## app 分层架构（原 app 模板 §十）

严格关注点分离，**禁止** UI 与业务/数据逻辑混层：

- **UI 层（Presentation）**：MVVM。View 只渲染 + UI 逻辑，数据全从 ViewModel 取；ViewModel（Riverpod `Notifier` 或所选方案）管状态、处理交互、注入 Repository，对外暴露**不可变**状态快照
- **Data 层**：Repository 模式。Service 包外部 API（HTTP/DB/平台插件）；Repository 消费 Service、转 Domain Model、管缓存/重试
- **Logic 层（Domain，可选）**：仅当业务逻辑复杂到污染 ViewModel、或需跨 ViewModel 复用时抽 Use Case
- **跨层纪律**：View 只调自己的 ViewModel/聚合层，**不跨页面调别人的状态、不跨层直接 watch 多个底层源**
- **响应式/暗黑**：走统一扩展（`ThemeExtension` + 所选适配方案——见 [layout.md](layout.md) 适配节），颜色/字号/间距归口常量类，**不硬编码**

## plugin 架构纪律（通用；原 plugin 模板 §十）

- **模块自包含**：`lib/<domain>/<module>.dart` 各自独立，按全路径 import，互不隐式耦合
- **import 分组注释**：`// Dart imports:` → `// Flutter imports:` → `// Package imports:` → `// Project imports:`，新增文件沿用
- **作者文档头（默认跟随项目现状，可覆写）**：默认——新模块作者头沿用项目主流惯例：存量普遍带 `/// * @Author:` 块 → 循既有格式（不含 @Email——作者与时间以 git 记录为准，头注不双写）；存量普遍无头 → 不加。惯例不一致时问一次需求方，答复记入 `.claude/memory/PROJECT.md` §十二附录（覆写为「强制开/强制关」）
- **注释语言**：领域逻辑用中文，文件内保持一致，不混用
- **example/ 纪律**：只演示插件表面、用于验证，**不当 app 开发**；example 的改动不进插件本体

## plugin 类型 A（平台 plugin）额外纪律

- **走联邦接口**：面向端 → platform_interface（抽象）→ method_channel（实现）→ 原生
- **平台差异收敛**：平台特定代码放原生侧或接口实现层，Dart 端保持平台无关
- **改原生侧要同步两端**：Android 与 iOS 能力保持对等，改一边要确认另一边

## plugin 类型 B（工具库）额外纪律

- **零平台依赖优先**：能用纯 Dart 解决就不引平台通道，降低下游集成成本
- **重依赖要标注**：引入重依赖时在模块头注释标明，提醒下游
- **未验证功能显式标注**：实验性模块标 `// 待验证`，不当作稳定 surface
