# Flutter 工程 Review Checklist 与模块清单

> **fork 自 crules v74-fork-base 的审查纪律并合并 Flutter 专项**——本文件自持（不依赖 crules 包）：通用 8 大类（自 crules 审查与复核纪律 fork）+ Flutter 专项。完整审查方法论（业务可达性 Gate / L0-L2 / 资损克制 / 两阶段审查）见 [`进阶/审查与复核纪律.md`](进阶/审查与复核纪律.md)。
>
> 启用条件：Flutter 项目（app / plugin）做 code review 或工程化设计时。

---

## 通用 Review Checklist（8 大类，fork 自 crules）

> 逐条 PASS / FAIL + 原因，FAIL 项附修复建议（精确到文件行号）。

**0. 协作表达**：沟通简练精准；先给可执行结论；无废话 / 重复 / 过度铺垫。

**1. 架构合规**：遵循分层（表现层 → 逻辑层 → 数据层 → 网络）；表现层只渲染不做业务逻辑；每个视图只调自己的页面级状态 / 聚合层，禁止跨页或跨层直接订阅多个底层源；跨源组合经聚合层暴露；网络 / 存储走统一封装，路径 / Key 集中定义。

**2. 组件 / 视图设计**：拆分粒度合理（单组件约 200 行内）；复用组件归公共目录；间距 / 圆角 / 尺寸用约定值或主题常量；无硬编码颜色。

**3. 状态管理**：状态单元职责单一；生命周期合理（页面级 vs 全局单例）；非平凡实现已先获确认。

**4. 边界处理**：Loading 有反馈；Error 有用户可见提示；Empty 有占位；网络异常有兜底（离线 / 重试）；输入校验走统一工具；长操作（外设通信 / 上传 / 长连接）有超时与断连处理。

**5. 国际化**：用户可见文本走 i18n；新增 Key 同步多语言文件；必要时执行 i18n 代码生成。

**6. 代码规范**：文件头注释（如项目要求）；无调试日志（**`avoid_print` lint 已拦**，抽查即可）；无硬编码 URL / 密钥；命名规范；**无新引入 lint 警告（`flutter analyze` 零 warning 是硬门——模板自带 `analysis_options.yaml` 基线）**；import 分组有序。

**7. 功能完整性**：spec 功能点均已实现（非 stub）；用户可完成完整流程；关键路径无崩溃；新增入口 / 路由已注册。

**8. Git 规范**：commit message 清晰；不提交不该入库的生成文件；不提交调试临时代码。

---

## Flutter 专项 Review Checklist

在通用 8 大类之上，Flutter 项目额外查：

### 组件 / 视图（Flutter 专项）

- [ ] 避免不必要 rebuild（`const` 构造——**lint 已拦**（`prefer_const_constructors`），抽查即可；`Selector` / `Consumer` 精确订阅、不在 `build` 里做重活）
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
