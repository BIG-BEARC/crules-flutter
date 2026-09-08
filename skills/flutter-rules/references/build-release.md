# 构建 · CI · 发布（flavor / 签名 / 混淆 / 符号化 / 发布检查）

> 触发场景：配 CI、出测试 / 生产包、配多环境（dev/staging/prod）、签名、混淆、发 pub 包时 Read 本文件。定位：工程面清单——具体命令以 Flutter 官方文档为准，本文件管**决策点与检查项**（命令参数随版本变，清单不常变）。

## 多环境（flavor / dart-define）

- **选型**：简单环境差异（API 域名 / 开关）用 `--dart-define` 起步；需要**共存多包**（测试包 + 生产包同机安装）才上 flavor（Android `productFlavors` + iOS scheme/configuration，两端都要配，漏一侧行为不一致）
- 环境值集中定义（一处常量表 / 构建脚本注入），禁散落硬编码；`String.fromEnvironment` 的默认值须是**生产安全值**（拿不到 define 时宁可指向生产也不指向不存在的环境）
- CI 每 PR 跑 analyze + test，发布流水线跑构建 + 产物归档——CI 配置文件（`.github/workflows` 等）入 git，密钥走环境变量 / secret，不入库

## 签名

- **Android**：keystore 入库 = 供应链事故——keystore 与密码走 CI secret / 本地安全存储；`key.properties` 不提交（.gitignore 显式列出）；上传密钥（Play App Signing）与发布密钥分离是 Play 默认形态
- **iOS**：证书 / 描述文件过期是发版日常故障——CI 侧用 App Store Connect API key 自动化签名（`xcodebuild -allowProvisioningUpdates` 或 fastlane）；本地手动签名的项目在 §十二附录记证书到期日
- 签名变更 = 新包装不上旧包：换 keystore / 换包名前先确认卸载重装的可接受性

## 混淆与符号化

- `flutter build apk/appbundle --release --obfuscate --split-debug-info=<目录>`：混淆后包体更小 + 逆向成本升高，代价是崩溃栈不可读
- **symbols 文件（`app.android-arm64.symbols` 等）每次构建归档**（按版本号存目录 / CI artifact），线上崩溃还原全靠它——丢失即永久不可读；符号化命令与流程见官方 docs（Obfuscating Dart code 节），iOS dSYM 同理随构建归档
- 混淆开启后**首跑全量回归**：反射 / JSON 手写字段名依赖（`fromJson('snake_case')` 走代码生成的没事）在混淆下可能静默失效

## 发布前检查（App 形态）

- [ ] 版本号 / build 号已 bump（pubspec `version: x.y.z+n`）
- [ ] `flutter analyze` 零 warning + 全量测试绿
- [ ] 目标环境真机过关键路径（低配机型含——见 references/performance.md 实操序）
- [ ] 混淆构架 + symbols 归档 + 崩溃监控钩子在线（`FlutterError.onError` / `PlatformDispatcher.onError` 见 performance.md）
- [ ] 敏感信息扫描：硬编码 URL / 密钥 / 测试后门（checklist 条目 6 同源）
- [ ] Android：targetSdk 达商店当前要求（16KB / edge-to-edge 等区间看坑库 Android 基线卡）；iOS：隐私描述文案与实际权限对齐

## pub 包发布（Plugin 形态）

- [ ] `flutter pub dev publish --dry-run` 零警告（CHANGELOG / 版本号 / description / homepage 一致）
- [ ] 版本号语义化：破坏性 API 变更升 major；CHANGELOG 顶部版本与 pubspec 一致
- [ ] 平台接口对等核验：Kotlin ↔ Swift 两侧能力清单逐条对（checklist「改了原生一侧，另一侧对等更新」同源）
- [ ] example 工程可跑（consumer 视角首验——plugin 模板 §八 example 说明）；federated 插件确认 endorsed 平台包版本同步
- [ ] 发布后 `flutter pub deps` 于净工程实测拉取（发布成功 ≠ 可解析）
