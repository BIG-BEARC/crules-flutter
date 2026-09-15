# 状态管理参考（预设 A · Riverpod 四条纪律）

> 2026-09-15 自 app 模板 §8.2 下沉（1.0.10 常驻收敛批；内容源自消费工程实战规范上移——0.1.2）——**选预设 A 时生效**，涉状态管理任务时随本文件按需 Read；选 B/C 的工程不适用，等价规范由对应预设沉淀。

- **Notifier 模式**：不可变 `State` 类（含 `copyWith`）+ `Notifier<T>`（`build()` 里 `ref.read` 注入依赖，不用过时 `StateNotifier`）
- **Provider 组织（就近原则）**：模块专用 Provider 放模块自己的 `presentation/` 或 `data/`；全局 DAO / API / 用户态等放全局 providers 目录——禁止把模块专用状态挂到全局
- **ConsumerWidget vs ConsumerStatefulWidget（强制）**：当私有方法需要 `ref` 时，**必须用 `ConsumerStatefulWidget`，禁止把 `WidgetRef` 作为参数传给私有方法**（`ref` 作类属性自动可用）；仅 `build` 用 `ref` → `ConsumerWidget`；需 `initState` / `dispose` / 访问构造参数 → `ConsumerStatefulWidget`
- **生命周期**：页面级状态用 `autoDispose`（离开页面释放），全局单例显式不 dispose——策略在 Provider 定义处声明，不在调用处补救
