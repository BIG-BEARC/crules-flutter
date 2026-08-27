# Flutter App 项目规则

> 本文件是 **superpowers + dart-flutter 两个插件协同工作的项目级规则**。
> superpowers 管「流程怎么走」(设计→计划→TDD→评审→合并),
> dart-flutter 管「Flutter 怎么写对」(分层/路由/i18n/测试…)。
> 本文件负责钉死**技术栈约定、提交策略、TDD 适用范围**——这两者都不会替你决定的东西。
>
> **使用方式**:新建 App 时,把本文件复制到项目根目录,完成下方【复制后必填】两节,删掉未选的预设。

---

<!-- AUTO-SYNC FROM crules/CLAUDE.md §一 协作红线 —— 改通用包后须同步本节 -->

## 一、协作红线(最高优先级)

- **始终中文回复**:即使工具输出是英文也用中文转述
- **简洁直接**:先给可执行结论,少讲空话,不重复解释
- **禁止自动提交**:不自动 `git commit`/`git push`;只有用户发 `commit`/`push`/`提交` 指令才开始提交流程
- **先读后改**:改代码前先 Read 相关文件,基于现有上下文改,不凭猜测乱改
- **优先编辑现有文件**:非必要不新建
- **必须不虚构事实和证据**:不得虚构文件、接口、参数、命令结果、测试结果或完成状态;无法读取/搜索/验证时明确说“当前无法确认”;**测试代码存在 ≠ 已运行,构建通过 ≠ 功能可用**
- **必须守住范围边界**:只处理本次已确认的需求;范围外问题只记录报告,不自行修复/重构/清理/优化;出现新范围须说明原因、影响、可选方案,等重新确认
- **风险操作先确认**:`rm -rf`、`git reset --hard`、`git push -force`、改 CI、删分支等,先明确提醒再执行
- **方案先确认再实现**:非平凡改动先讨论方案、获用户确认,再写码
- **多方案走选项卡**:需用户在可枚举方案中取舍时,用 `AskUserQuestion` 呈现,不要手动加「自定义输入」(工具自带 Other 入口)
- **敏感数据安全兜底**:涉及密钥/凭据/生产数据时,默认不写日志、不入 git、不外发,除非需求方明确授权

### 代码修改红线

- **改动局限于需求范围**:不顺手做无关重构、不引入“为未来留余地”的抽象;三段相似代码胜过过早抽象
- **不做半成品实现**:要么完整实现,要么明确告知未实现的边界;禁止 `// TODO` 占位、空函数体
- **不硬编码**:URL、密钥、Token、用户可见字符串、魔法数字走配置/环境变量/i18n/常量类
- **最小必要改动**:优先复用现有能力和平台原生实现;不借机做全局格式化、目录调整、依赖升级

---

## 二、技术栈约定【复制后必填】

> 本项目使用 Flutter App 开发。下方列了 3 套主流预设 + 1 个自定义模板。
> **复制到项目后:选定一套,删掉其余,把结果填到「本项目最终技术栈」。**
> 涉及这些技术时,优先调用 dart-flutter 对应 skill,不另造轮子。

### 预设 A:Riverpod + go_router + Dio(现代主流)

- 状态管理:`flutter_riverpod`(优先 `Notifier`/`AsyncNotifier`,避免过时 `StateNotifier`)
- 路由:`go_router`(声明式,`MaterialApp.router`)
- 网络:`dio` + `retrofit`(接口声明式)+ `interceptors`(鉴权/日志/重试)
- 序列化:`json_serializable` + `build_runner`(`.g.dart` 生成,不手写)
- 本地存储:`hive` 或 `shared_preferences`
- 国际化:`easy_localization` 或 `flutter_localizations` + `intl`
- 主题/适配:`flutter_screenutil` + 暗黑模式走统一 `ThemeExtension`

### 预设 B:Bloc + go_router + Dio(事件驱动、强约束)

- 状态管理:`flutter_bloc`(`Bloc`/`Cubit`,事件驱动,适合中大团队)
- 路由:`go_router`
- 网络:`dio`
- 序列化:`freezed` + `json_serializable`(不可变模型 + 联合类型)
- 本地存储:`hive`
- 国际化:`flutter_localizations` + `intl`

### 预设 C:Provider + http(轻量小项目)

- 状态管理:`provider` + `ChangeNotifier`
- 路由:`Navigator 1.0`(命名路由)
- 网络:`http` 包
- 序列化:`dart:convert` 手写 `fromJson`/`toJson`
- 本地存储:`shared_preferences`
- 国际化:`flutter_localizations` + `intl`

### 自定义模板(以上都不合适时填这里)

```
- 状态管理:
- 路由:
- 网络:
- 序列化:
- 本地存储:
- 国际化:
- 主题/适配:
```

### 本项目最终技术栈【选定后填这一行,删掉上面未选项】

> (在此填写本项目实际采用的技术栈,例如:Riverpod + go_router + Dio + json_serializable + hive + easy_localization)

---

## 三、superpowers + dart-flutter 分工

| 层 | 插件 | 职责 |
|---|---|---|
| 流程层 | **superpowers** | brainstorming→writing-plans→worktree→TDD→subagent→verification→review→finishing 工程闭环 |
| 技术层 | **dart-flutter** | 每个 Flutter 任务怎么写对(架构/路由/i18n/测试/序列化/响应式) |
| 工具层 | **dart-flutter** Dart MCP + Stop hooks | 暴露 Dart 工具;会话停止自动 `dart-format` + `dart-analyze` |

**核心心智模型**:superpowers 说「做什么」(先写失败测试→看它失败→写最小实现),dart-flutter 说「Flutter 里怎么做」(用 `WidgetTester` 写 widget 测试、`fromJson` 怎么生成)。两者分层,**不冲突**。

**触发规则**:每个任务开始前先检查是否有 skill 适用(superpowers 的 1% 规则——1% 可能适用就调用)。

---

## 四、标准工作流(端到端,每步哪个 skill 配合)

```
brainstorming → writing-plans → [using-git-worktrees] → test-driven-development / subagent-driven-development
→ verification-before-completion → requesting-code-review → (等待提交指令) → finishing-a-development-branch
```

| 步骤 | superpowers 触发 | dart-flutter 配合 |
|---|---|---|
| 1. 提需求 | `brainstorming`(HARD-GATE:未获设计批准禁止写码) | `flutter-apply-architecture-best-practices` 提供分层模型(UI/Logic/Data) |
| 2. 拆任务 | `writing-plans`(2–5 分钟粒度,带验证步骤) | — |
| 3. 隔离(多功能并行时) | `using-git-worktrees` | — |
| 4. 写每个任务 | `test-driven-development`(red-green-refactor) | View 任务→`flutter-add-widget-test`;Model→`flutter-implement-json-serialization`;网络→`flutter-use-http-package`;路由→`flutter-setup-declarative-routing`;i18n→`flutter-setup-localization`;响应式→`flutter-build-responsive-layout` |
| 5. 派子代理 | `subagent-driven-development`(逐任务派发 + 两阶段评审:规范/质量) | — |
| 6. 会话停止 | — | **Stop hook 自动跑** `dart-format` + `dart-analyze` |
| 7. 声明完成前 | `verification-before-completion`(强制跑验证并贴输出) | `dart-run-static-analysis` |
| 8. 代码评审 | `requesting-code-review`(对照计划查) | — |
| 9. 提交 | ⚠️ **人工提交,见第五节** | — |
| 10. 收尾 | `finishing-a-development-branch`(合并/PR 选项) | — |

**跨模块大改动**(新页面/新业务流/跨多端):在步骤 2 之前额外走「工程化补充流程」——输出 PRD(`.claude/plans/prd-<feature>.md`;若启用 spec-kit,用 `/speckit` 产出 spec 替代),按模块逐段确认,任务带验证清单,两阶段独立审查(先规范合规,再代码质量)。

---

<!-- AUTO-SYNC FROM crules/CLAUDE.md §二 提交策略 —— 改通用包后须同步本节 -->

## 五、提交策略(覆盖 superpowers 的自动提交)

> ⚠️ 这是与 superpowers 的**唯一硬冲突**,必须用本节压制。

- **本项目遵守人工提交**:即使 superpowers 的 `test-driven-development` 要求「绿灯后 commit」、`brainstorming` 要求「设计通过后 commit」,本项目一律**不自动提交**。
- 依据:`using-superpowers` 内置优先级 = **用户指令 > skill > 默认行为**。本 CLAUDE.md 属于用户指令,优先级高于 skill。
- **只有**用户发送 `commit`/`push`/`提交` 指令,才执行 `git add → git commit → git push` 完整流程,推送到远端才算完成。
- **提交授权的边界**:`commit`/`push` 授权仅覆盖普通的暂存+提交+推送,**不覆盖**强制推送、`reset --hard`、删分支、改 CI 等破坏性操作(完整破坏性操作清单与 commit type 见通用包 CLAUDE.md §二)。
- superpowers 的 TDD 流程中,「commit」这一步在本项目改为「标记任务完成、保留变更等用户审阅」。

---

## 六、TDD 适用范围

superpowers 的 TDD 是教义级纪律,但 Flutter 不同层适用方式不同:

| 代码类型 | TDD 要求 | 「测试」的形式 |
|---|---|---|
| 纯逻辑/工具/数据层(ViewModel、Repository、Service、utils) | **强制 red-green-refactor** | `package:test` 单测 |
| 数据模型/序列化 | 强制 | 单测覆盖 `fromJson`/`toJson` 边界 |
| UI 渲染(widget) | 用 widget test 充当 TDD 的「测试」 | `flutter-add-widget-test`(`WidgetTester`) |
| 完整用户流程 | 不强制每步,关键路径要覆盖 | `flutter-add-integration-test` |
| 既有代码无测试时 | 改动前先补「表征测试」(characterization test)锁住现状,再重构 | — |

> 规则:superpowers 会**删掉先于测试写的代码**。所以先写测试,再写实现。

---

## 七、分层架构纪律(对应 flutter-apply-architecture-best-practices)

严格关注点分离,**禁止** UI 与业务/数据逻辑混层:

- **UI 层(Presentation)**:MVVM。View 只渲染+UI 逻辑(动画/布局),数据全从 ViewModel 取;ViewModel(`ChangeNotifier` 或 Riverpod `Notifier`)管状态、处理交互、注入 Repository,对外暴露**不可变**状态快照。
- **Data 层**:Repository 模式。Service 包外部 API(HTTP/DB/平台插件)返回原始模型或 `Result`;Repository 消费 Service、转 Domain Model、管缓存/重试,对 ViewModel 暴露 Domain Model。
- **Logic 层(Domain,可选)**:仅当业务逻辑复杂到污染 ViewModel、或需跨 ViewModel 复用时,抽 Use Case。
- **跨层纪律**:View 只调自己的 ViewModel/聚合层,**不跨页面调别人的状态、不跨层直接 watch 多个底层源**;需要跨源时先在聚合层暴露。
- **响应式/暗黑**:走统一扩展(`ThemeExtension`/`ScreenUtil`),颜色/字号/间距归口常量类,**不硬编码**。

---

## 八、验证纪律

- dart-flutter 的 **Stop hook** 会自动在会话停止时跑 `dart-format` + `dart-analyze`——但仍要主动验证。
- **声明任何「完成/修复/通过」之前**,必须运行验证命令并**贴出输出**(superpowers `verification-before-completion`):
  - `dart analyze`(零 warning 才算过,warning 视为回归)
  - `flutter test`(相关测试全绿)
  - UI 改动尽量在模拟器/真机跑关键路径
- 验证范围未覆盖的部分,**明确告知用户**,不谎报。

---

## 九、后台 agent 完成后必须展示 diff

由于后台 agent 的中间 Edit/Write 步骤主对话不可见,后台 agent 完成、汇总给用户前,**主控必须主动**:

1. `git status`——列出新增/修改/删除文件清单
2. `git diff`(含未暂存)和 `git diff --staged`——展示完整变更;过长则按文件分批,先给「哪些文件改了」概览
3. 把 agent 自报的「做了什么」与实际 diff **逐项对照**,不一致或遗漏要指出

> 这一步是后台模式下用户审阅代码的**唯一入口**,禁止跳过、禁止只贴 agent 摘要。配合 superpowers 的 `subagent-driven-development` 尤其重要。

---

## 十、App 向 dart-flutter skill 速查

| 场景 | 调用 skill |
|---|---|
| 新项目/重构做分层 | `flutter-apply-architecture-best-practices` |
| 配置 go_router 声明式路由 | `flutter-setup-declarative-routing` |
| 初始化国际化 | `flutter-setup-localization` |
| REST 请求 | `flutter-use-http-package`(轻量)或按技术栈用 Dio |
| 模型序列化 | `flutter-implement-json-serialization` |
| 适配手机/平板 | `flutter-build-responsive-layout` |
| 修 overflow/unbounded 等布局错 | `flutter-fix-layout-issues` |
| 组件级测试 | `flutter-add-widget-test` |
| 端到端测试 | `flutter-add-integration-test` |
| 组件可视化预览 | `flutter-add-widget-preview` |
| 跑静态分析 | `dart-run-static-analysis` |
| 写单测 | `dart-add-unit-test` |
| 包版本冲突 | `dart-resolve-package-conflicts` |
| 用 switch 表达式/模式匹配 | `dart-use-pattern-matching` |
| 用主构造函数 | `dart-use-primary-constructors` |
