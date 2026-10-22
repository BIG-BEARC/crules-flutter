# 通用与专项工程规范（app 全栈通用＋plugin 专项）

> 2026-10-22 自宪法模板下沉（1.3.0 常驻分层批，语义零删减迁入）：app 模板 §八.1（任何预设生效）、plugin 模板 §八（Plugin 专项规范）。涉通用工程规范 / plugin 专项时 Read 本文件，不常驻。

## app 全栈通用（任何预设生效；原 app 模板 §八.1）

- **多 package 工程 assets 加载**：子工程被主工程引用时，加载子工程自己的 assets 用项目统一的加载入口（内部默认带 `package` 参数），**不要**用裸 `load()`——跨 package 资源不加 package 名必空（新增 assets 须完全重启，见宪法 §四）
- **文件头注释（默认跟随项目现状，可覆写）**：注释放在 import 语句**之后**（不是文件开头）。默认——新建文件的作者头沿用项目主流惯例：存量普遍带 @Author 头 → 循既有格式（不含 @Email——作者与时间以 git 记录为准，头注不双写）；存量普遍无头 → 不加。惯例不一致时问一次需求方，答复记入 `.claude/memory/PROJECT.md` §十二附录（覆写为「强制开/强制关」）
- **Import 排序**：Dart SDK → Flutter SDK → 外部包（字母序）→ 内部包（绝对路径 `package:<项目>/...`）→ 相对路径
- 代码风格细则不双份维护：通用风格（const 构造 / 命名 / 行宽）模型已知 + lint 基线硬拦；项目特有风格（头注释 / 适配 / import 分组）见本节各条；主题与布局细节按需查 [theming.md](theming.md) / [layout.md](layout.md)

## plugin 专项规范（原 plugin 模板 §八）

> 【按需手填占位】——当前无 plugin 形态消费工程的上移源（本包实战输入来自 App 工程）；项目特有规范沉淀于此。
> 屏幕适配与字体策略（App 形态课题）不入 plugin 模板——plugin 无 UI 适配语境；若 plugin 含 example App，按 app 预设族（[state-management.md](state-management.md)）与 [layout.md](layout.md) 适配节对号。

**平台通道选型**：简单参数传递用 `MethodChannel`；**结构化数据 / 多端对等接口优先 Pigeon**（类型化生成 Dart + Kotlin + Swift 三侧，消灭手写序列化与两侧签名漂移——原生侧对等纪律的机械化方案）；事件流用 `EventChannel`。

**pub 发布检查**（发版前逐项过，全表见 [build-release.md](build-release.md)「pub 包发布」节）：

- [ ] `flutter pub publish --dry-run` 零警告（CHANGELOG / 版本号 / description 一致）
- [ ] 破坏性 API 变更升 major；CHANGELOG 顶部版本与 pubspec 一致
- [ ] Kotlin ↔ Swift 平台能力清单逐条对等；federated 插件 endorsed 平台包版本同步
- [ ] example 工程可跑；发布后净工程 `flutter pub deps` 实测拉取
