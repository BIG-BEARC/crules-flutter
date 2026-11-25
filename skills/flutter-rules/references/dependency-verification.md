# 三方包与 SDK 版本核验（先查后写）

> 触发：写第三方包调用（非基础用法）／用与 SDK 版本相关的特性或门槛／升级依赖后报错
  ——先核「本机实际装的这个版本」，不凭记忆；查的动作本身用不了几个 token，错一轮返工远贵于此
> 维护基线：as-of 2026-11-25；出处逐行内标；事实随时间失效时照坑库维护义务更新

## 三触发（何时必须查）

①写非基础用法调用 ②版本相关特性/门槛 ③升级后报错——基础常见调用不触发

## 定位已装版本（第一步永远是 package_config，按 rootUri 形态分三路）

- 第一步：读工程 `.dart_tool/package_config.json` → `rootUri`——解析到哪个路径，跑的就是哪份，最权威
- hosted 依赖 → rootUri 指向 pub cache 的 hosted 子目录：
  `~/.pub-cache/hosted/<镜像域>/<包-版本>/`；Windows `%LOCALAPPDATA%\Pub\Cache`
  （出处：dart.dev/tools/pub/environment-variables）；`PUB_CACHE` 可改址；
  镜像目录名随所配镜像变（维护者本机 as-of 2026-11-25：pub.dev 与 pub.flutter-io.cn 两域并存）
- git 依赖 → rootUri 指向 cache 的 git 检出目录（形如 `~/.pub-cache/git/<仓库名>-<commit>`）——
  pubspec 里的 git 坐标只是来源，不是本机位置；源码就在检出处
  （本机实证 as-of 2026-11-25：file_saver 六个 commit 检出带 pubspec.yaml 在案；
  现役工程暂无 git 依赖——活体 rootUri 样本缺，本节形态系 pub 行为陈述＋cache 实存佐证）
- path 依赖 → rootUri 指向 pubspec 所写实际目录（三类 pubspec 依赖中唯一不在 cache 的一路；
  SDK 自带包的 rootUri 亦不在 cache——实证：工程一 flutter_test rootUri 指向 flutterSdk 目录）
- SDK：`flutter --version`／`dart --version`；fvm 多版本确认当前生效版

## 核什么

- API 签名与行为＝源码为准；CHANGELOG（同主版本 patch 也可能带行为变化）；`example/`；版本区间注记

## 查不到 / 拿不准

- 以 analyze / test 实跑结果判定（红线「引用皆有实测依据」同源）；不凭记忆落笔

## 与坑库、checklist 的分工

- 坑库＝已实证的坑（症状反查）；本件＝查法（主动核验）；新坑照旧走坑库入库
- 升级流程（lock diff／读 changelog／以测试判）照插件 cache `checklist.md`「依赖变更专项」；本件管写调用前核已装版本
