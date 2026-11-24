# 多渠道马甲包（flavor 四平台落地 / 渠道矩阵 / 打包）

> 触发场景：新加渠道马甲包、多渠道共存出包、四平台（Android/iOS/Windows/macOS）flavor 落地、渠道包排障时 Read 本文件。定位：**小白可跟做的实操指南**——步骤即动手顺序，每节末有验证标准；决策点选型（flavor vs dart-define）见 [build-release.md](build-release.md)。
> **出处与时点**（引用纪律，全部实读非转述）：
> - 语雀《云店收银台多渠道马甲包方案》登录态实读，as-of 2026-11-24（现行工程做法来源，内含配置截图）
> - Flutter 官方四页 `.md` 直取，as-of 2026-11-24：[Android](https://docs.flutter.dev/deployment/flavors) / [iOS＋macOS 合页](https://docs.flutter.dev/deployment/flavors-ios) / [Windows](https://docs.flutter.dev/deployment/flavors-windows) / Linux
> - 本机 fvm Flutter 3.27.4 实测（CLI help / SDK 源码 grep）；Flutter 官方发布清单（GCS）实测 stable=3.50.1（2026-11-20 发布，取于 2026-11-24）
> **纪律**：活稿——工程升 Flutter 或新增渠道后回写；MQTT 密钥等敏感值**不入任何仓（含本仓）**，用时分头保管。

## 0. 一分钟心智模型

马甲包 = 同一代码库，按渠道换皮＋换行为。换的东西分三层，各管各的：

| 层 | 管什么 | 怎么传 |
|---|---|---|
| **Native 层**（flavor） | 包名、应用图标、应用名称、窗口标题 | 打包命令 `--flavor 渠道名` |
| **Dart 层**（读渠道） | 域名、MQTT、定制逻辑（如限制打印机品牌） | 老路 `--dart-define=APP_CHANNEL=渠道名`；官方路直接读 `appFlavor` 常量 |
| **资产层** | 渠道专属 logo / 启动图 / 素材 | pubspec `assets: flavors:` 分束，只进对应渠道的包 |

**一条铁律（三处同名）**：`--flavor` 的值 = Android `productFlavors` 里的名字 = iOS/macOS Xcode scheme 的名字。拼错一个，包就打不出或打错。

## 1. 第一步：查 Flutter 版本（决定 Windows 走哪条路）

```sh
flutter --version
```

| 你的版本 | Android/iOS/macOS `--flavor` | Windows `--flavor` | 结论 |
|---|---|---|---|
| ≥ 3.47（含现行 stable 3.50.x） | ✅ | ✅ 原生支持 | 四平台全走官方 flavor 路 |
| < 3.47（如本机 3.27.4） | ✅ | ❌ 无此旗标 | Windows 走 §6 B 路（手工渠道目录） |

依据：官方 Windows/Linux 文档明写「Built-in support requires Flutter 3.47 or later」；本机 3.27.4 实测 `flutter build windows -h` 无 `--flavor`、`flutter build macos -h` 有。

## 2. 渠道矩阵（云店现有 7 渠道，as-of 2026-11-24 语雀实读）

| 渠道 | 包名 | 平台 | 域名 | MQTT | 定制点 |
|---|---|---|---|---|---|
| 云店收银台（默认） | `com.jlpay.cashier` | A+iOS+Win | eshop-mch.**xgd**.com | 阿云 Pro 实例 | — |
| 福掌柜 | `com.jlpay.cashier.fuboss` | A | 同上 | 同云店 | USB 打印机仅芯烨；EN=FU BOSS、繁=福掌櫃 |
| NexgoShop（澳门） | `...nexgoshop`；Win `com.jlpay.windows.nexgoShopPOS` | A+Win | eshop-mch.**xgdmo**.com | 阿云 ProHK 实例 | 无语音播报 |
| NexgoShop Mini | `com.jlpay.jlcashiermini.nexgoshop` | A | xgdmo | — | — |
| YammysPOS | `...yammysPos`；iOS `com.jlpay.yammysPos` | A+iOS+Win | xgdmo | — | 无语音播报 |
| Yammys Mini | `com.jlpay.jlcashiermini.yammys` | A | xgdmo | — | — |
| 云店国补 | `com.jlpay.jlcashider.subsidy` | A+iOS | xgdmo | — | — |

- 三方监控全渠道友盟/bugly/rum：友盟可配渠道属性；**rum/bugly 要按渠道单独注册**。
- 商家 H5/PCWeb 也吃渠道（渠道=3 用福掌柜 logo/登录页文案——「3」的编码语义语雀原文未释，真做 H5 渠道化先问清）。
- ⚠️ **脱敏注**：语雀原文表格里有 MQTT accessKey/Secret 明文，本文件不复制；用时回语雀原文取，且**不进任何 git**。
- macOS 目前**无渠道行**——首个 macOS 渠道要先定：应用名/logo/bundle id/域名/MQTT 实例/语言集。
- 语言集**全渠道一致**（简中/繁体/英文），差异只在各语文案（如福掌柜 EN=FU BOSS、繁=福掌櫃）——做新渠道三种语言文案都要备齐。
- 云店国补包名 `jlcashider` 为语雀原文如此（疑 `jlcashier` 拼写），以工程实际为准。

图标尺寸两套（做新渠道先备图）：
- Android mipmap 六档：36/48/72/96/144/192。
- iOS/**macOS** 共用十九档：16→1024（16/20/29/32/40/58/60/64/76/80/87/120/128/152/167/180/256/512/1024）。

## 3. Dart 层（全平台共用，先做这步）

1. **加渠道枚举**（沿用现行工程 `AppChannel` / `AppChannelManager`）：

   ```dart
   enum AppChannel { jlpay, fuboss, nexgoshop, /* 新渠道加这里 */ }
   ```

2. **读渠道值，两路二选一**：
   - 老路（现行工程，Windows <3.47 也有效）：`--dart-define=APP_CHANNEL=FUBOSS`，代码里 `AppChannelManager.CHANNEL` 取。**键名必须和代码常量名完全一致。**
   - 官方路（3.27.4 已支持，本机 SDK 实证）：`import 'package:flutter/services.dart';` 后直接用 `appFlavor`（值 = `--flavor` 名，没传为 null）。Windows <3.47 时它恒为 null，这就是老路存在的原因。

3. **按渠道分支**（域名/定制逻辑；`String.fromEnvironment` 默认值须生产安全——见 build-release.md 多环境节）：

   ```dart
   void main() {
     const channel = appFlavor ?? String.fromEnvironment('APP_CHANNEL');
     if (channel == 'FUBOSS') {
       Config.apiUrl = 'https://eshop-mch.xgd.com';
       // 福掌柜：USB 打印机仅芯烨
     }
     runApp(const MyApp());
   }
   ```

4. **（可选）渠道资产分束**（3.27.4 实证可用）——渠道专属素材只进对应包，防包膨胀：

   ```yaml
   flutter:
     assets:
       - assets/common/
       - path: assets/fuboss/
         flavors: [FUBOSS]
   ```

5. **（可选）默认渠道**：pubspec 加 `flutter: default-flavor: JLPAY`，本地不敲 `--flavor` 也不怕打错。

## 4. Android（两版本通用，最成熟）

1. `android/app/build.gradle`（新工程是 `.kts`）加 flavor：

   ```groovy
   android {
     defaultConfig { flavorDimensions = ["channel"] }
     productFlavors {
       JLPAY  { dimension "channel"; applicationId "com.jlpay.cashier" }
       FUBOSS { dimension "channel"; applicationId "com.jlpay.cashier.fuboss" }
     }
   }
   ```

   官方新写法用 `applicationIdSuffix ".fuboss"`（在默认包名后加后缀），语义等价。
   ⚠️ AGP 9.0 起 flavor 里 `resValue()` 默认报错——应用名一律走下面第 2 步的 `strings.xml`。

2. 建渠道资源目录 `android/app/src/FUBOSS/res/`：
   - `mipmap-*/ic_launcher.png`：六档图标全换；
   - `values/strings.xml`：`<string name="app_name">福掌柜</string>`；
   - **每个国际化 `values-xx/` 文件夹都要同步改**（漏一个，该语言下就穿帮显示默认名）。

3. 确认 `AndroidManifest.xml` 用的是引用：`android:label="@string/app_name"`、`android:icon="@mipmap/ic_launcher"`。

4. 验证：`flutter run --flavor FUBOSS` → 桌面图标、应用名、包名（设置→应用详情）三处都对才算过。

## 5. iOS

> 现行工程（语雀原文）走的是「每渠道复制一个完整 Target」路，十步：复制渠道 project 目录 → LaunchScreen 国际化 → InfoPlist 国际化（文件名不能改）→ Assets 换 logo/启动 logo（Target Membership 仅勾对应渠道）→ 改 info.plist → 新增渠道 Target → 指定 info.plist 路径 → Project 配渠道环境 → Podfile 加渠道 target → Copy Bundle Resources 查重（细目与截图见语雀原文）。官方推荐单 Target＋多 scheme（`--flavor` 本来就是选 scheme）。
> **选路规则：存量工程加新渠道 → 跟随工程既有路数（同一工程两路别混用）；新工程或整体迁移 → 走本节官方路。**

1. 开工程：`open ios/Runner.xcworkspace`。
2. **建 scheme**：Product > Scheme > New Scheme，Target 选 Runner，名字 = 渠道名（如 `FUBOSS`）。Manage Schemes 里确认 **Shared ✅ 必须勾**（不共享 Flutter CLI 找不到）。
3. **建 configuration**：工程 Info tab > Configurations，复制 Debug/Profile/Release 各一份，命名 `Debug-fuboss` 等——**后缀渠道名必须小写**（CLI 识别规则），且基于 `Debug.xcconfig`/`Release.xcconfig`（不是 Pods-Runner）。
4. **把 configuration 挂到 scheme**：编辑 scheme，Run/Test/Analyze 用 `Debug-fuboss`、Profile 用 `Profile-fuboss`、Archive 用 `Release-fuboss`。
5. **应用名**：Build Settings 加 User-Defined Setting `APP_DISPLAY_NAME`（三个 config 都填「福掌柜」），`Info.plist` 的 `CFBundleDisplayName` 改成 `$(APP_DISPLAY_NAME)`。
6. **图标**：Assets 里新建 `AppIcon-fuboss`（十九档图拖齐），General > App Icons 字段按 configuration 选对应 AppIcon。
7. **包名**：Build Settings > Packaging > Product Bundle Identifier，展开后按 configuration 填渠道包名（如 `com.jlpay.cashier.fuboss`），并在苹果开发者账号注册该 App ID。
8. **Podfile**（有 pod 依赖才需要）：`project 'Runner', {...}` 映射里补 `'Debug-fuboss' => :debug, 'Release-fuboss' => :release, 'Profile-fuboss' => :release`。
9. 验证：`flutter run --flavor FUBOSS`；再检查 Build Phases > Copy Bundle Resources **无重复资源**（有错编不过）。

⚠️ CI 硬约束：iOS 渠道包**只能命令行打**（`flutter build ipa --flavor FUBOSS`）——Xcode GUI 打包带不上渠道名。

## 6. Windows（先看 §1 版本，二选一）

### A 路：Flutter ≥ 3.47（官方原生，升级后优先）

1. `--flavor` 直接可用，零配置即隔离构建目录（产物在 `build/windows/<arch>/FUBOSS/runner/Release/`）。
2. Flutter 把渠道名写进 `windows/flutter/ephemeral/generated_config.cmake` 的 `FLUTTER_APP_FLAVOR`——**只在 `add_subdirectory(${FLUTTER_MANAGED_DIR})` 之后可见**（if 判断放早了会被静默跳过，官方原文特别标注的坑）。
3. 窗口标题/图标走 CMake 模板。`windows/runner/CMakeLists.txt` 在 `add_executable` 前加：

   ```cmake
   if(DEFINED FLUTTER_APP_FLAVOR)
     if(FLUTTER_APP_FLAVOR STREQUAL "FUBOSS")
       set(RUNNER_APP_ICON "fuboss.ico")
       set(WINDOW_TITLE "福掌柜")
     endif()
   endif()
   configure_file(main.cpp.in main.cpp @ONLY)
   configure_file(Runner.rc.in  Runner.rc  @ONLY)
   ```

4. 把 `main.cpp` 改名 `main.cpp.in`，窗口标题位换成 `L"@WINDOW_TITLE@"`；`Runner.rc` 改名 `Runner.rc.in`，图标行换 `"resources\\@RUNNER_APP_ICON@"`，`ProductName`/`FileDescription` 也可用 `@WINDOW_TITLE@`。**两个生成物加进 .gitignore，模板 `.in` 进 git。**
5. 渠道 `.ico` 放 `windows/runner/resources/`。验证：`flutter run -d windows --flavor FUBOSS`。

### B 路：Flutter < 3.47（现行 3.27.x 状态，语雀原路）

1. 复制 `windows/runner` → `windows/fuboss`（runner 目录=默认渠道云店收银）。
2. 改渠道目录内：`resources/` 换 logo；`CMakeLists.txt` 改 `project()` 名；`main.cpp` 改 `wsprintf` 与 `window.CreateAndShow`（窗口标题）；`Runner.rc` 改图标/产品信息。
3. **每次打包前**手工改顶层 `windows/CMakeLists.txt` 指向渠道目录（这是 B 路最大的维护痛点，升级 A 路即消）。
4. 打包机 InstallerConfig（Qt Installer Framework）：复制默认渠道目录 → 改 Config/、`packages/<包名>/installscript.qs`、`package.xml`。
5. Jenkins 打包命令＋上传脚本对应改。

> InstallerConfig/打包机层 A/B 路都要，官方不管这层。

## 7. macOS（补齐平台，照 iOS 平移即可）

官方明说：iOS 步骤把 iOS 全部替换成 macOS 照做（`open macos/Runner.xcworkspace`，同样 scheme/configuration/APP_DISPLAY_NAME/AppIcon-fuboss/PRODUCT_BUNDLE_IDENTIFIER/Podfile）。`flutter build macos --flavor` 在 3.27.4 已支持（本机实测）。

与 iOS 的三个差异：

| 差异点 | macOS 做法 |
|---|---|
| 无 LaunchScreen.storyboard | 不用配启动屏；图标走 `AppIcon-fuboss`（十九档同 §2 表） |
| 窗口标题 | `MainFlutterWindow.swift` 设置（等价 Windows `main.cpp` 那层） |
| 分发 | Developer ID 签名＋**公证（notarize）**，Jenkins 要加对应步骤——iOS 清单之外唯一新增 |

首个渠道建议直接上云店收银台本尊（bundle id 如 `com.jlpay.cashier.mac`，以需求方裁定的矩阵行为准）。**本章为官方平移方案、待首个 macOS 渠道实证回写。**

## 8. 打包与 CI（Jenkins）

通用命令模板（四平台同构）：

```sh
flutter build apk   --release --flavor FUBOSS --dart-define=APP_CHANNEL=FUBOSS   # Android（dart-define 为老路兼容）
flutter build ipa   --release --flavor FUBOSS                                    # iOS，必带 --flavor
flutter build macos --release --flavor FUBOSS                                    # macOS
flutter build windows --release --flavor FUBOSS                                  # Windows（需 ≥3.47）
```

- 现行 Android 链路（换渠道照改）：`source …/env_android_jlcashier.sh` → `flutter clean` → `flutter pub get` → `flutter build apk --build-number ${BUILD_NUMBER} --release --flavor FUBOSS --dart-define=APP_CHANNEL=FUBOSS` → `resign_android.sh` → `upload_fir_common.sh`。完整旗标参考（`--split-debug-info`/`--obfuscate`/`--target-platform` 等）见语雀原文「Jenkins打包命令修改」节；混淆与 symbols 归档纪律见 [build-release.md](build-release.md)。
- Android 打包后走 resign 脚本 → fir 上传；**fir 新渠道四步**：fir 建项目 → 手动传一个不冲突包名的 apk → 查 appid → 打包机按渠道枚举建配置文件。
- iOS 打包机要有对应环境脚本配置文件。
- 维护成本：渠道多了别一个渠道一个 Jenkins task——抽「渠道名＋环境脚本」做参数化，一个 task 打多渠道（语雀文档已规划此方向）。

## 9. 坑位速查表（打不出来先对这张表）

| 症状/坑 | 原因与解法 |
|---|---|
| 打包报找不到 flavor | 三处不同名：`--flavor` 值 ≠ gradle `productFlavors` 名 ≠ Xcode scheme 名，逐个核对 |
| Dart 层拿不到渠道 | `--dart-define` 键名 ≠ 代码常量名；或 Windows <3.47 用了 `appFlavor`（恒 null，换 dart-define） |
| 某语言下应用名穿帮 | 国际化 `values-xx` / `InfoPlist.strings` 没同步改，每种语言一份都要过 |
| iOS configuration 不识别 | 后缀渠道名没**小写**；或 scheme 没勾 **Shared** |
| iOS 编译失败 | Build Phases > Copy Bundle Resources 有重复/错资源 |
| AGP 9.0 报 custom resource values | flavor 里 `resValue()` 禁用，改 `strings.xml` |
| abiFilters 放 flavor 里不生效/异常 | 官方不推荐；优先放 `defaultConfig`，确需放 flavor 时打包命令带 `-Pdisable-abi-filtering=true` |
| Windows CMake 的 if 不生效 | 判断放在 `add_subdirectory(FLUTTER_MANAGED_DIR)` 之前了（变量尚未定义） |
| Windows 打出默认渠道 | <3.47 忘了先改顶层 CMakeLists 切渠道目录（B 路）；≥3.47 忘带 `--flavor` |
| configure_file 生成物脏了 git | 生成物进 .gitignore，提交 `.in` 模板 |

## 变更记录

| 日期 | 变更 |
|---|---|
| 2026-11-24 | 建稿（cloud-kb 迁入本仓）：四平台实操指南（语雀原文＋官方四页＋本机 3.27.4/GCS stable 3.50.1 实证）；同日补漏修正——iOS/macOS 图标实为十九档（三处）、§5 选路规则（存量工程跟随既有 Target 复制路）、语言集一致注、国补包名存疑注、Jenkins 链路脚本名、abiFilters 坑；macOS 章为缺口补齐方案，待首个 macOS 渠道实证后回写 |
