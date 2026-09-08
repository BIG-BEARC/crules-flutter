# 性能 · 观测与优化 / 图片内存 / 线上崩溃监控

> 触发场景：卡顿排查、低配设备适配（收银机 / 工控屏 / 老旧安卓）、内存占用高、大图列表、接入或排查线上崩溃时 Read 本文件。定位：**观测先于优化**——没有 timeline 证据不猜瓶颈；2026 年模型已内化的通用优化常识（const / builder 懒加载 / 避免build 重活）不重复，见 checklist「性能」节。

## 观测工具与线程模型

- **DevTools Performance 视图**（`flutter run --profile` 下看，debug 数值不可信）：帧图表（Frame Chart）逐帧看 UI / Raster 两列耗时，>16ms（60Hz）/ >8ms（120Hz）即 jank
- **双线程心智模型**：UI 线程跑 Dart（build / 布局 / 逻辑），Raster 线程跑光栅化（Skia/Impeller）。**Raster 列长**→ 疑复杂着色器 / 大图缩放 / 无谓 saveLayer（阴影 / clip / Opacity）；**UI 列长**→ 疑 build 过重 / 长同步计算。修哪边由列说话，别凭感觉
- **Timeline 事件**：自定义段用 `Timeline.startSync`/`finishSync`（或 `dart:developer` `TimelineTask`）标出业务阶段，在 DevTools Timeline 里对齐看
- **内存**：DevTools Memory 视图看 heap 曲线与快照 diff；图片解码占用看 `imageCache`（`PaintingBinding.instance.imageCache`，`maximumSizeBytes` 默认 1000 幅 / 100MB 量级——大图场景可显式调小）

## 图片解码与内存（低配设备刚需）

- **按显示尺寸解码**：`Image.asset`/`Image.network` 传 `cacheWidth`（或 `cacheHeight`，给一边即可按比例）——`2048×2048` 原图解码进内存 ~16MB，显示 200px 就该按 ~200 解码；大图列表 / 相册 / 商品图墙**必传**，这是低配设备 OOM 与 Raster 卡顿的头号常见根因
- 大图文件本身：发布资产用构建期压缩（不对运行时缩放抱幻想）；超长图（小票 / 报表）考虑分片或 PDF 方案
- **图片缓存策略显式化**：轮播 / 换页大量换图时确认 `imageCache` 上限是否够用 / 该不该 `clear()`；`precacheImage` 用于首屏关键图（冷启动白屏缓解），勿全量预热

## 低配设备实操序

1. `flutter run --profile` 真机（目标低配机型本体，不是开发机）
2. DevTools 帧图表过**关键路径**（开台 / 下单 / 结账），记录 UI/Raster 双列基线
3. 只修超标帧：按列归因（见上），一次一改复测
4. 内存：操作 N 轮后 heap 是否回落（不回落 = 泄漏：controller / stream / 全局 cache 持有）

## 线上崩溃监控

- **全局错误钩子双兜底**（未接 SDK 也先立住，日志至少落本地 / 上报通道）：
  - `FlutterError.onError`（Flutter 框架异常）→ 转发 `FlutterError.presentError` + 自行上报
  - `PlatformDispatcher.instance.onError`（Dart 2.15+，捕获未被 zone 捕的孤立错误——**`runZonedGuarded` 旧写法在此之后可省**）
- **SDK 选型**：`sentry_flutter`（跨端 / 自托管可用 / 上报上下文丰富）或 `crashlytics`（Firebase 系 / Google 系标配）；离线 / 内网设备无第三方通道时——自建上报（ dio 上报到自有日志端）或至少本地环形日志（排障时导出）
- **符号化**：release 混淆构建（`--obfuscate --split-debug-info=...`）后崩溃栈须用构建时产出的 symbols 文件符号化——**符号文件随构建产物归档**（见 references/build-release.md），丢了就无法还原线上栈
- 上报内容纪律：堆栈 + 版本号 + 机型必带；token / 密钥 / 完整卡号**永不入上报**（checklist 条目 6 资损线同源）
