# Flutter Plugin 项目规则

> 本文件是 **superpowers + dart-flutter 两个插件协同工作的项目级规则**,面向 **Flutter plugin package** 开发。
>
> plugin 和 app 的关键区别:plugin 是**被依赖的库**,每个公开 util/类/方法都是**已发布 API 表面**,
> 必须保持签名稳定;`example/` 只用于演示,**不是 app**;还可能涉及平台通道/原生模块。
>
> **使用方式**:新建 plugin 时,把本文件复制到项目根目录,完成下方【复制后必填】两节,删掉未选的预设。

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

## 二、插件类型【复制后必填】

> plugin 有两种典型形态。**复制到项目后:选定一种,删掉另一种,把结果填到「本项目最终类型」。**
> 类型决定下方哪些纪律适用。

### 类型 A:通用 Flutter plugin(平台能力/原生桥接)

适用于:封装平台能力、原生模块、设备 API、联邦接口(federated)plugin。

特征:
- `pubspec.yaml` 声明 `flutter.plugin.platforms`(android/ios/linux/macos/windows/web)
- 走**联邦接口**:`<name>.dart`(面向端接口)→ `<name>_platform_interface.dart`(抽象)→ `<name>_method_channel.dart`(MethodChannel 实现)→ 原生 `Plugin.kt`/`Plugin.swift`
- 有 `example/` app 仅用于演示和验证插件表面
- 可能含 iOS Podspec / Android Gradle 原生依赖

### 类型 B:工具库风格(纯 Dart 工具模块)

适用于:纯 Dart 工具集合(如 `cutils`:money/format/encrypt/utils…),无或极少平台通道。

特征:
- `lib/<domain>/<module>.dart` 自包含模块,被下游**按全路径直接 import**(如 `package:xxx/num/money_utils.dart`)
- `lib/<name>.dart` 主入口**不一定** re-export 各模块(按需)
- 无平台通道时 `pubspec.yaml` 不声明 `flutter.plugin.platforms`
- `example/` 仅做调用演示
- TDD 极契合(纯函数多)

### 自定义模板(混合形态或特殊 plugin 时填这里)

```
- 插件定位:
- 是否含平台通道:
- 支持平台:
- 是否走联邦接口:
- example 用途:
```

### 本项目最终类型【选定后填这一行,删掉上面未选项】

> (在此填写本项目实际类型,例如:工具库风格,纯 Dart 工具模块,无平台通道)

---

## 三、superpowers + dart-flutter 分工

| 层 | 插件 | 职责 |
|---|---|---|
| 流程层 | **superpowers** | brainstorming→writing-plans→worktree→TDD→subagent→verification→review→finishing 工程闭环 |
| 技术层 | **dart-flutter** | Dart/Flutter 任务怎么写对(测试/分析/模式匹配/序列化/FFI) |
| 工具层 | **dart-flutter** Dart MCP + Stop hooks | 暴露 Dart 工具;会话停止自动 `dart-format` + `dart-analyze` |

**核心心智模型**:superpowers 说「做什么」(先写失败测试→看它失败→写最小实现),dart-flutter 说「Dart 里怎么做」。两者分层,**不冲突**。

**触发规则**:每个任务开始前先检查是否有 skill 适用(superpowers 的 1% 规则)。

---

## 四、标准工作流(端到端)

```
brainstorming → writing-plans → [using-git-worktrees] → test-driven-development / subagent-driven-development
→ verification-before-completion → requesting-code-review → (等待提交指令) → finishing-a-development-branch
```

| 步骤 | superpowers 触发 | dart-flutter 配合 |
|---|---|---|
| 1. 提需求 | `brainstorming`(HARD-GATE:未获设计批准禁止写码) | — |
| 2. 拆任务 | `writing-plans`(2–5 分钟粒度,带验证步骤) | — |
| 3. 隔离(多功能并行时) | `using-git-worktrees` | — |
| 4. 写每个任务 | `test-driven-development`(red-green-refactor) | 写测试→`dart-add-unit-test`;序列化→`flutter-implement-json-serialization`;FFI→`dart-use-ffigen`/`dart-setup-ffi-assets`;模式匹配→`dart-use-pattern-matching`;主构造函数→`dart-use-primary-constructors` |
| 5. 派子代理 | `subagent-driven-development`(逐任务派发 + 两阶段评审) | — |
| 6. 会话停止 | — | **Stop hook 自动跑** `dart-format` + `dart-analyze` |
| 7. 声明完成前 | `verification-before-completion`(强制跑验证并贴输出) | `dart-run-static-analysis`;覆盖率→`dart-collect-coverage` |
| 8. 代码评审 | `requesting-code-review`(对照计划查) | — |
| 9. 提交 | ⚠️ **人工提交,见第六节** | — |
| 10. 收尾 | `finishing-a-development-branch`(合并/PR 选项) | — |

---

## 五、公开 API 稳定性纪律(plugin 特有,最重要)

> plugin 是被下游直接 import 的库,**每个公开符号都是已发布表面**。这条比 App 严格得多。

- **保持签名稳定**:不随意改名/改参数/改返回类型;破坏性改动必须升主版本号并写迁移说明。
- **避免破坏性重命名**:已有公开类/方法/顶层函数改名 = 破坏下游。要改先讨论影响。
- **新增优先于修改**:加新模块/新可选参数是安全的;改现有签名是危险的。
- **文档化公开表面**:公开模块写 Dartdoc,`@Author` 头部按既有模块惯例(见下)。
- **不 re-export 污染**:主入口 `<name>.dart` 按既有策略决定是否 re-export 子模块,不擅自改导出面。

---

<!-- AUTO-SYNC FROM crules/CLAUDE.md §二 提交策略 —— 改通用包后须同步本节 -->

## 六、提交策略(覆盖 superpowers 的自动提交)

> ⚠️ 这是与 superpowers 的**唯一硬冲突**,必须用本节压制。

- **本项目遵守人工提交**:即使 superpowers 的 `test-driven-development` 要求「绿灯后 commit」、`brainstorming` 要求「设计通过后 commit」,本项目一律**不自动提交**。
- 依据:`using-superpowers` 内置优先级 = **用户指令 > skill > 默认行为**。本 CLAUDE.md 属于用户指令。
- **只有**用户发送 `commit`/`push`/`提交` 指令,才执行 `git add → git commit → git push` 完整流程,推送到远端才算完成。
- **提交授权的边界**:`commit`/`push` 授权仅覆盖普通的暂存+提交+推送,**不覆盖**强制推送、`reset --hard`、删分支、改 CI 等破坏性操作(完整破坏性操作清单与 commit type 见通用包 CLAUDE.md §二)。

---

## 七、TDD 适用范围(plugin 导向)

plugin 极契合 TDD——大量纯函数和明确的公开 API。**public API 默认全覆盖**:

| 代码类型 | TDD 要求 | 「测试」形式 |
|---|---|---|
| 纯 Dart 工具/算法/格式化(money/num/encrypt/regex…) | **强制 red-green-refactor** | `package:test` 单测,边界值全覆盖 |
| 公开 API(public 类/方法/顶层函数) | **强制**,视为回归安全网 | 单测,固定输入→固定输出 |
| 数据模型/序列化 | 强制 | 覆盖 `fromJson`/`toJson` 边界 |
| 平台通道/原生桥接(类型 A) | 用 mock 测 Dart 侧;原生侧行为在 `example/` 手测 | `setMockMethodCallHandler` mock 通道 |
| 既有无测试代码 | 改动前先补「表征测试」锁现状,再改 | — |

> superpowers 会**删掉先于测试写的代码**。plugin 的公开 API 尤其要先用测试钉死行为,再动实现。

---

## 八、plugin 架构纪律

### 通用(两种类型都适用)

- **模块自包含**:`lib/<domain>/<module>.dart` 各自独立,按全路径 import,互不隐式耦合。
- **import 分组注释**:文件头按 `// Dart imports:` → `// Flutter imports:` → `// Package imports:` → `// Project imports:` 顺序,新增文件沿用。
- **作者文档头**:实质性模块带 `/// * @Author: ...` 块,新模块沿用既有惯例。
- **注释语言**:领域逻辑用中文,文件内保持一致,不混用。
- **example/ 纪律**:`example/` 只演示插件表面、用于验证,**不当 app 开发**;example 的改动不进插件本体。

### 类型 A(平台 plugin)额外纪律

- **走联邦接口**:面向端 → `*_platform_interface`(抽象)→ `*_method_channel`(实现)→ 原生,分层清晰。
- **平台差异收敛**:平台特定代码放原生侧或 `*_platform_interface` 实现,Dart 端保持平台无关。
- **改原生侧要同步两端**:Android(Kotlin)和 iOS(Swift)的能力要保持对等,改一边要确认另一边。

### 类型 B(工具库)额外纪律

- **零平台依赖优先**:能用纯 Dart 解决就不引平台通道,降低下游集成成本。
- **重依赖要标注**:引入重依赖(如 `rxdart`、`dartx`、平台插件)时,在模块头注释标明,提醒下游。
- **未验证功能显式标注**:实验性/未验证模块标 `// 待验证` 等,不当作稳定 surface。

---

## 九、验证纪律

- dart-flutter 的 **Stop hook** 会自动在会话停止时跑 `dart-format` + `dart-analyze`——但仍要主动验证。
- **声明任何「完成/修复/通过」之前**,必须运行验证命令并**贴出输出**(superpowers `verification-before-completion`):
  - `dart analyze`(**零 warning** 才算过,warning 视为回归——plugin 尤其要干净,因为下游会看到)
  - `flutter test`(公开 API 测试全绿)
  - `cd example && flutter run`(改了平台桥接/插件本体的可见行为时,在 example 验证)
- 验证范围未覆盖的部分,**明确告知用户**,不谎报。

---

## 十、后台 agent 完成后必须展示 diff

后台 agent 的中间 Edit/Write 步骤主对话不可见。后台 agent 完成、汇总给用户前,**主控必须主动**:

1. `git status`——列出新增/修改/删除文件清单
2. `git diff`(含未暂存)和 `git diff --staged`——展示完整变更;过长按文件分批,先给「哪些文件改了」概览
3. 把 agent 自报「做了什么」与实际 diff **逐项对照**,不一致或遗漏要指出

> 这是后台模式下用户审阅代码的**唯一入口**,禁止跳过、禁止只贴 agent 摘要。

---

## 十一、plugin 向 dart-flutter skill 速查

| 场景 | 调用 skill |
|---|---|
| 写/补单测 | `dart-add-unit-test` |
| 跑静态分析(零 warning) | `dart-run-static-analysis` |
| 机械性 lint 自动修 | 配合 `dart fix --apply` |
| 收集测试覆盖率 | `dart-collect-coverage` |
| 包版本冲突 | `dart-resolve-package-conflicts` |
| 用 switch 表达式/模式匹配 | `dart-use-pattern-matching` |
| 用主构造函数 | `dart-use-primary-constructors` |
| 迁移到 `package:checks` | `dart-migrate-to-checks-package` |
| 模型序列化 | `flutter-implement-json-serialization` |
| 生成 mock(unit test) | `dart-generate-test-mocks` |
| FFI 绑定生成(类型 A 原生) | `dart-use-ffigen` |
| 打包 C/C++ 为代码资产(类型 A) | `dart-setup-ffi-assets` |
| 修运行时错误(配合 LSP/热重载) | `dart-fix-runtime-errors` |
| 构建命令行工具(若 plugin 含 CLI) | `dart-build-cli-app` |
