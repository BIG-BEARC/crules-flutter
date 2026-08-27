# Flutter 专项 Checklist 与模块清单

> Flutter / 移动端**特有**的审查条目与工程化模块。通用条目见通用包 [`../crules/进阶/审查与复核纪律.md`](../crules/进阶/审查与复核纪律.md) 的 Review Checklist（架构 / 边界 / 功能 / Git 等中性条目），本文件只补 Flutter 专项。
>
> 启用条件：Flutter 项目（app / plugin）做 code review 或工程化设计时。

---

## Flutter 专项 Review Checklist

在通用 Checklist 的 8 大类之上，Flutter 项目额外查：

### 组件 / 视图（Flutter 专项）

- [ ] 避免不必要 rebuild（`const` 构造、`Selector` / `Consumer` 精确订阅、不在 `build` 里做重活）
- [ ] 颜色 / 文本样式 / 间距归口主题或常量类，无 inline 字面量
- [ ] 新增颜色语义化命名，禁止 `color0xXXXXXX` 复读式命名
- [ ] 暗黑模式 / 主题切换走 `ThemeExtension` 或统一扩展，不硬编码
- [ ] 响应式适配（`MediaQuery` / `LayoutBuilder` / `flutter_screenutil`）符合项目约定

### 状态管理（Flutter 专项）

- [ ] 选用的状态管理方案符合项目技术栈（Riverpod / Bloc / Provider，不混用）
- [ ] 异步正确处理 loading / error / data 三态（`AsyncValue` / `FutureBuilder` 合理）
- [ ] 状态单元生命周期合理（页面级 `autoDispose` vs 全局单例）
- [ ] 视图不直接 watch 多个底层源，跨源经聚合层

### 平台 / 原生（Flutter 专项）

- [ ] 平台差异显式处理（`Platform.isXxx` 或 federated 接口），不假设两端一致
- [ ] 原生权限 / 后台任务考虑系统回收与弹窗
- [ ] 改了原生一侧，另一侧对等更新（Kotlin ↔ Swift）
- [ ] 平台通道数据类型在边界显式转换

### 国际化（Flutter 专项）

- [ ] 用户可见文本走 `AppLocalizations` / i18n 接口
- [ ] 新增 Key 同步多语言文件，并跑了 `flutter gen-l10n`（或等价生成命令）
- [ ] 长翻译的 UI 溢出已处理

---

## Flutter 工程化模块清单

大需求做 PRD 时，Flutter 项目的模块清单（在通用模块之上补充）：

| 模块 | Flutter 专项要点 |
|---|---|
| 架构概览 | 是否新增路由 / 入口；federated 接口拆分；状态管理方案归属 |
| 数据模型 | `fromJson` / `toJson`（`json_serializable` / `freezed`）；本地存储 Key；是否新增实体 |
| 业务 / 状态层 | Riverpod `Notifier` / Bloc / Cubit；依赖关系；`autoDispose` 策略 |
| UI / 视觉 | 页面骨架；复用组件；`ThemeExtension` 归口；暗黑 / `screenutil` 适配 |
| 国际化 | 新增 Key 列表；多语言同步；`gen-l10n` 生成 |
| 平台 / 原生差异 | 权限；后台；MethodChannel / federated；Kotlin ↔ Swift 对等 |
| 边界与失败 | Loading / Empty / Error / 超时 / 鉴权失效兜底 |

---

## 常见 Flutter 反模式（审查时留意）

- 在 `build` 方法里发请求 / 做副作用 → 自反馈死循环（放 `initState`）
- `watch` 全量状态导致重建丢字段 → 按需 `select` / `listen`
- 长生命周期 stream 上用 `firstWhere` 等一次性消费 → 下游断开
- 热重载残留旧资源 / 旧连接 → 需清理机制或重启验证
- 跨语言桥接处类型不一致 → 边界显式 assert / 转换
