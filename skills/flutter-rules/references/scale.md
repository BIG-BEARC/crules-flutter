# 电子秤 / 数字客显（串口设备）

> 触发场景：接入 / 调试电子秤、数字客显、串口设备排障前 Read 本文件。
> 来源：saas-cashier（日活 7w 餐饮 POS）实证；2026-09-24 自 `iot-devices.md` 三域拆分迁入，卡面逐字迁移。客显并秤系需求方裁决——两者是平行双实现、互斥同口，共用串口公共底座，并为一文件内聚。
> 归属：设备 / 协议行为级坑（含型号怪癖——**型号是主检索键**）住本文件；框架级坑（OS / SDK / 依赖交叉）住 `references/platform-pitfalls.md`；通用铁律 / 钱箱 / 副屏 / 语音播报住 `references/iot-devices.md`。
> 锚口径：commit 哈希为 saas-cashier 私有仓锚，按其仓内口径视作**信任声明**；`doc/…` 路径为其仓文档（可复核锚优先）。

## 串口 RS232（秤 / 客显公共底座）

设备路径：`/dev/ttyS*`（POS 惯例 ttyS4 分给电子秤；一体秤实测 ttyS3@9600）、`ttyUSB*`（USB 转串口）、`ttyACM*`（CDC）、ttyAMA/ttyHS/ttyMT/ttyMSM（ARM/MTK/高通 OEM 变体）、`/dev/serial/by-id|by-path`（稳定符号链接，按路径重插不稳）；Windows 侧为 COM 口 + 波特率设置。操作卫生：连接后 / 读取前**清空输入输出缓冲区**（残留脏帧致首读解析异常）。

**串口 open 成功 ≠ 连的是秤：必须「收到有效数据」才算连接成功**——部分串口能打开但没接秤 / 接的是别的设备，绑错端口「连接成功」却永远没重量。修法 `connectWithValidation`：开串口后等有效称重数据（ latch 超时即断开试下一端口），收到数据才放行——批1「连接建立≠设备就绪」的串口版强化：不止等就绪，还要验「是你要的设备」。锚：82158f06f、334be5eeb。

**赋给 port 的 config 不可 dispose——悬垂指针 native 崩（当日回滚）**——`SerialPortConfig.dispose()` 释放底层原生结构，而 `_port!.config` 随后仍被读取（日志 / 波特率比较）→「应用停止工作」；放开注释当天即整体回滚，现行赋值后无任何 config dispose 调用（接受原生小泄漏或换 API 语义）。锚：6e75ff01f、a448ce79d。

**高频设备流消费策略终态：latest-wins + 节流，禁定长门控与计数阈值重连**——定长缓冲处理把人机交互（界面改重量）与机器连续帧耦合坏（门控吞掉人工改重窗口）；重连判据计数阈值对高频流无意义（200 次几秒打满），**持续异常时间窗（3s）**才区分抖动与真断；帧率高于 UI 需求时消费端节流（500ms trailing）、reader 只留最新包（`_pendingData` latest-wins），日志降频（重量 3s / 原始数据 10s）。演化链 2026-01-05~06 集中反转（含同日 Revert ×2——读取策略改动须带可回退验证）。锚：63bd6b4f7、998cc3abd、d61a78847、9c7af4751、d96d8ce26、9aa3efeaa、8324d4947。

**双插件同带 libserialport.so → 加载冲突：插件内 so 改名收编**——elec_scale_plugin 自带 native 串口库与 flutter_libserialport 同名同符号；终态 = 插件内 so 改名（`libserialport_elec.so` + `loadLibrary("serialport_elec")`，四 ABI），**勿**换 pubspec 依赖（曾走 flutter_libserialport→libserialport 替换，已回滚——落卡防复述中间态）。锚：0f11e10a4、a7dd9536d。

**双实现（SDK+兼容）生命周期动词必须双路径对称**——`stopGetData()` 只停原始实现、漏停兼容实现，读循环（200ms 定时）又不检查 `isRunning`，数据永不停止；引入兼容 / 双模路径时 start / stop / reconnect 每个动词都要覆盖全部活动路径。锚：704bf2091。

（帧协议解析与粘包拆包的秤侧实证见「秤」节 S3 / S4 / S11/S12 指针；客显与秤是**平行双实现**（客显 serial_util.dart / 秤 electronic_scale_serial.dart，互不 import），config dispose 坑两文件同日同修——客显卡见本文件「数字客显」节。）

## 电子秤（收银秤：串口 / USB / 一体机）

蓝牙链路秤零素材（在仓两秤插件均串口 / USB 链路，2026-09-24 全量检索确认）——秤卡集中于本文件「秤」节与「串口」节。

**设备读数 ≠ 本件重量：连续称重必须基线锚定**——秤面读数是多件累计绝对值，直接当「本件净重」消费：删非首件按绝对值扣减 = 资损；登出走不到统一清理的路径（强制 / 超时登出）时基线跨账号残留，「下一会话首件称重静默少称或卡 0」（提交体原文）。修法：净重 = current − baseline、确认时重锚、登出 / 切桌 / 删末件归零；该中间字段后被整体移除、删菜回归纯反算——**机制教训不随字段消亡**。措辞纪律：提交信息「存 delta」实际语义是「存净重」，KB 辨析经 diff 逐字核实。锚：8068d7616、a1600005f、2570ae73f、e111267a7。

**同型秤帧头多变体：判据 = 头魔数 + 尾魔数 + 定长，按猜的长度适配三连败**——顶尖系帧头 [1,2,83] / [1,2,85] / [1,2,53]、尾 [3,4]、16 字节定长；曾有「13 字节、[17,0,1] 头」变体三次尝试当日全部 Revert——新变体先抓字节流实证再改判据。锚：84c28d181、319ac7325、2f2549aef。

**秤重启后吐垃圾帧：按已知错误签名重连，宽判会误杀半帧**——收银机重启后大华秤 7 字节垃圾帧（签名头 [152,128,230] / [109,109,109]）无法取重；判据演化两轮：放宽「任意 7 字节坏帧即重连」→ 同日收紧「须命中签名」。提交信息自述「根本原因可能是波特率」无 diff 佐证——**未证实，如实标注**。锚：4aaf214e6、01dd75ee6、69cf55d64。

**isStable 稳定标志跨机型语义不一致，不能当「数据变化」判据**——「不同电子秤这里可能不同，不用该属性判断」（diff 注释原文）；变化门控上报既误判数据变化又吞人工改重窗口（移除门控的提交标题直书「防止在界面上改重量」）。现行：持续上报 + 消费端节流，isStable 仅按帧内含 'S' 解析（大华分支恒 true）。锚：3bd09dc0d、d61a78847。

**PendingIntent FLAG_IMMUTABLE 版本门设 M：反致 Android 6-11 部分机型重启后拿不到 USB 秤权限**——为修 Android 12+ SecurityException 把门设成 `>=M`，部分 OEM 机型重启后授权结果收不到；门移到 `>=S` 仅改一处即修复（Android 12+ 强制 immutable，6-11 不必）。推测机制（immutable 阻止系统向广播注入 extras）无日志佐证——**根因保持未查明**。与打印机「重启后 USB 失效」同族（5f36501de）。锚：7c8a371ae、ff5035feb。

**USB 串口秤断开顺序错 + 伪单例 → USB 权限一直被持有无法复连**——旧 disconnect 先关 USB connection 后关 serial port 且无异常保护、`mInstance = this` 每实例各一份（伪单例）、「枚举设备列表前不断开既有连接」；终态：`@Volatile` 双检锁真单例，断开顺序 = stop IO manager → close serial port（try/catch）→ close USB connection（try/catch）→ 清引用，`getDeviceList` 前先 disconnect。与「USB 连接态不可缓存」「连接建立≠设备就绪」同族。锚：6ef61de19。

**专有协议 SDK 握手拒绝非本品牌秤：改二进制 SDK 跳过校验 + 数据验证 + 兼容模式多协议解析**——AclasOS2Sdk 连接发 `"ACLAS"` 握手并要求专有应答，别的秤只发标准称重数据 → ret:-6。三件套：① 二进制修改 vendored jar 使连接直接返回 0（**存 `_original.jar` 备份**——改二进制的纪律动作）；② 连接有效性改「数据验证」：等有效数据 ≤2s（20×100ms）无数据断开试下一端口；③ 兼容模式自动扫串口 + 多协议解析（标准 / ASCII / 大华 / 顶尖帧格式），端口优先级 = SDK 读到数据的端口 > 用户首选 > 其他。策略结论：专有 SDK 锁品牌链路不可靠时，通用协议兼容层是终态。锚：52f77ba37、82158f06f、2e8c478b9、8d2af1484、ec8be58a6。

**一体秤插件原生层崩溃族（一周三连修）**——① SDK 重连时内部状态不完整，读版本 / 设备信息 NPE（混淆后内部类为 null）→ try-catch 包住「读设备信息」：连接成功但读信息失败，**秤仍可正常工作**；② **fdsan SIGABRT**（Android 10+）：SDK 断开时关掉已被系统接管的 fd（"attempted to close file descriptor owned by SocketImpl"）→ 断开后与重建实例前各 sleep 等 fd 释放——跨设备通用的原生 fd 所有权坑；③ EventSink 竞态：UI 线程回调执行时 events 已被关闭置 null → `runOnUiThread` 内部**二次**判空（外层判过不算）；④ **EventChannel.success 后台线程调用必崩**：平台通道回调必须在主线程 → `Handler(Looper.getMainLooper()).post` + Activity 生命周期四回调置空 / 重绑、detach 时关设备（跨设备通用铁律）。另有 initDevice 异步化 / 取重加超时防 ANR。锚：334be5eeb、9e5d735f9、5cba61efc、b28d0c211、63c32b4b5。

**R8 混淆吞 vendored 秤 SDK 反射类 → 一体秤 release 闪退**——先整体关 `minifyEnabled`/`shrinkResources`，后补 keep 规则；keep 按 SDK 全包名（伴随包 `.data/.io/.util` 一并，`com.example.scaler.**` 系）。**现状**：该仓混淆整体仍关、keep 规则在位——开混淆前须过秤实机回归。通用条见 build-release.md 混淆节指针。锚：af901bc09、e7e9117a1、11e2b6fb9。

**设备数据回调越过引擎生命周期：mainLooper lateinit 崩溃**——引擎分离 / 重建后 USB 数据回调仍到达，`onNewData` 直接 `mainLooper.postDelayed` → 「lateinit property mainLooper has not been initialized」（线上崩溃上报标题原文）。修法 `mainLooper?.postDelayed` + `events?.success` 判空——设备回调生命周期 ≥ 页面 / 引擎生命周期，跨回调引用一律可空。与副屏插件 lateinit 卡同族。锚：755e56470。

**Windows 实现被 Android 路径触达：一套业务多平台实现必须入口分流**——Windows 串口秤（FFI）在 Android 上跑到「对象未初始化报错」；修法连接 / 逻辑层平台判空守卫，现行按 android/ 子目录分层。锚：757ba54cf。

## 数字客显

数字客显（串口 COM 链路：Windows COM 口 / Android 串口，与秤平行双实现——客显 serial_util.dart / 秤 electronic_scale_serial.dart，互不 import，公共底座见「串口」节）。

**客显串口异常面在枚举 / 构造段，先于 open**——无串口机器上 `SerialPort.availablePorts` 直接抛异常（Windows 缺 serialport.dll 同炸，日志「串口初始化失败，可能是缺少serialport.dll」）→ 包 try/catch 返回 `[]`；释放路径 `_port!` 空崩 → 全空安全 `_port?.close(); _port?.dispose(); _port = null`；构造器里 `_init()` 与否当日反复（禁→恢复，终态恢复）。单例不自毁（`_ins = null` 曾致懒汉重建循环）——「连接建立≠设备就绪」再前置一步：**设备枚举都可能失败**。锚：50b0e9f64、7a036f353、2fe0464a1、48f26cda3、895038715、cc63f6135。

**关开关清零竞态：异步写未完成即同步释放 → 清零写不出去**——`writeByteLEDByAddress` 是 async Future，写完 0.00 立即同步 `disposeRecourse` 会把端口在写入完成前关掉（27 分钟两笔接力修复）。修法 = 写函数加完成回调参数，释放挪进回调再 +100ms 延迟——async 写 + 同步释放的时序错位是串口设备通用坑。锚：053e8dae5、db22ac18a。

**客显开关策略三连反转，终态 = 保持连接、仅关开关时延迟关**——随用随开（每次写建连）→ 写完即关（金额显示毕 close）→ 终态：连接常驻、`resetZero` 关开关时经回调延迟关；写失败仅释放资源保留对象（下次重开复用）。附带两处**现行缺陷**（接入前自查）：`close()` 方法已无任何调用方（死代码）；重试计数 `retryCunt = 3` 只减不复位——单例终身累计 3 次 open 失败后零重试（疑似「开机设备就绪慢当天不显示」机制之一）。锚：ac49c312c、425e58d2b。

**LED 字库仅 0-9 与点：金额必须无千分位格式**——字表无逗号，`currencyFormat`（千分位）传入即抛 → 统一 `currencyFormatWithDef`（两位定长无分隔）。**现行缺陷**：`isValidPrice` 正则交替未分组（`^([1-9]\d*\.?\d*)|(0\.\d*[1-9])$` 前半支无 `$` 锚、后半支无 `^` 锚）——「0.50」类 0.x0 金额判 false 回退显示 0.00（0.99 正常）、`12ab` 脏串被前半支放行后字表取值抛异常；正则多分支锚定必须整支闭合。锚：477e3e0b8。

**写失败自愈链反复：无界递归重试是反模式**——open 失败 catch 里延迟 500ms 再入自身（无界递归，设备长期不在时无限循环）→ 删递归改单次重写 → 终态不再重写（仅释放资源，下次业务写时重建）。失败重试必须有次数边界与退出路径。锚：31a480e27、d5c5ffe3e。

**开机客显不显示 = 串口流控线未配置**——v2.5.13 发布注记「开机不显示」修复主锚：构造器恢复 `_init()` + 补全六项流控参数（parity/xonXoff/rts/cts/dsr/dtr，终态现行在位）+ 单例不自毁。机制推断「RTS/DTR 未置位时部分 LED 客显不理数据」**无日志佐证，如实标注**——但「串口参数必须逐项显式配置、不能只设波特率」的教训独立成立。锚：f5e784b58。

**关客显开关须清配置释放 COM 口，且与秤互斥提示**——关闭开关同步清 SP 缓存配置释放端口（否则重开机后 COM 口仍被占）；设置页 COM 下拉对被秤占用的端口标注「已被电子秤占用」（秤/客显互斥同口，选型即冲突预防）。锚：89bc52b2b。
