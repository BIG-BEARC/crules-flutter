# IoT / 外设通信（收银硬件接入）

> 触发场景：接入 / 调试外设、多屏、设备类排障前 Read 本文件。
> 来源：backend 角色卡「设备通信铁律」升格（S14 处置，2026-09-08）+ saas-cashier（日活 7w 餐饮 POS）8 类设备实证。批1（打印机 / 扫码枪 / 扫码盒 / 钱箱）、批2（电子秤 / 串口 / 副屏）、批3（客显 / 语音播报）2026-09-24 全量沉淀。
> 归属：硬件协议 / 设备行为级坑（含型号怪癖——**型号是主检索键**，不外放消费工程 memory）住本文件；框架级坑（OS / SDK / 依赖交叉，如 Windows IME 吞扫码枪字符）住 `references/platform-pitfalls.md`，本文件只留指针。
> 锚口径：commit 哈希为 saas-cashier 私有仓锚，按其仓内口径视作**信任声明**；`doc/…` 路径为其仓文档（可复核锚优先）。全卡核验 2026-09-24。
> 升格触发：多轮自持的 IoT 调试任务（协议调试 + 原生通道一体）实证后，评估独立 `iot` agent——素材即本文件。

## 通用铁律（自 backend 角色卡迁入，原文全量）

- 写入与读取要有应答确认机制，不要「发了就当成功」
- 分帧 / MTU 安全值要保守，不踩协议边界
- 先订阅再写入，否则通知丢失
- 不要在长生命周期 stream 上用一次性消费操作（如 `firstWhere`）——长流持续监听，短流才一次性
- 重连必须 dispose 旧上下文创建新的，不复用旧订阅
- 延迟类异步必须有可取消句柄——`Future.delayed` 不可取消，页面销毁后照样执行（孤儿回调 / 句柄泄漏）；用 `Timer?` 字段持句柄、dispose 中 `cancel()`（实证：秤弹窗 EventBus 延迟重连踩此，05cb54b66）
- 协议文档不可全信，**以实际设备字节日志为准**
- 长操作要有超时和断连处理，不阻塞事件循环

## 外设类（按通信方式分节）

### 蓝牙（BLE / SPP：打印机、扫描外设）

**iOS BLE 写入超 MTU 被静默截断**——症状：蓝牙票「发送失败≈4s」且只出一半，无异常无日志（静默丢数据）。withoutResponse 队列满即丢；iOS 15.6 典型 ATT MTU=185 → 单包上限≈182，分块 200B 即超；全仓 6 个打印插件曾 0 处检查 `maximumWriteValueLength`。修法：withResponse 串行 + 按 MTU 分块 + 连接失败 8s 兜底。锚：f8c22f969、47de61637、cee15a646；doc/ios_bluetooth_print_crash_fix_design.md §8。

**Android 蓝牙 SPP 写入须「小块 + 节流」——与 USB 连发相反（实测）**——16KB+flush / 一次性 write / 3KB 连续+末尾 flush 全部卡顿；**1KB（恰一个 L2CAP/RFCOMM 帧）+ sleep(10ms) 节流最优**。根因：USB bulkTransfer 有精确硬件流控可连续发；蓝牙射频吞吐 + RFCOMM 协议栈须软件节流匹配打印机处理速度。锚：fef75d305、e58120e9f。

**iOS 蓝牙「每次 connect 前强制 disconnect」可引爆休眠 IUO 缺陷（SIGTRAP 冷启动崩溃循环）**——Swift 侧 `connectedPeripheral: CBPeripheral!` 为 nil IUO 时强解必崩；典型自锁链：一个修复把死代码变活、激活另一处休眠缺陷。修法：connect 幂等快路径 + 单槽 FlutterResult 模式；教训：信号名不能作判据（SIGTRAP 非 SIGILL）。锚：02e22a0d3、f8c22f969、1071d157c；doc/ios_bluetooth_print_crash_fix_design.md（D1–D13 全缺陷表）。

**蓝牙链路光栅位图（customImg）不放开（工程结论）**——放开后等待久 / 出纸卡顿 / 一定概率乱码（乱码=票据损坏、资损级）；SPP 吞吐低 + 部分固件接收缓冲小，光栅大包不可靠，分包优化换不来收益（已实测拍板）。维持仅文字拦截，别试图放开。锚：da32ad182；doc/printer/decisions.md DEC-2026-09-11。

**蓝牙设备 MAC 大小写不归一 → 同机重复 / 编辑误拦**——iOS 大写 / Android 小写混用同一批设备；比较前统一大小写、编辑查重排除自身 id。「connect 前 disconnect」在 Android 侧是刚需、在 iOS 侧有崩溃副作用（见上卡）——平台差异须分支处理，不能一把梭。锚：cf73751d5、ecd66a354；doc/pitfall_knowledge_base_2026.md §三。

### 串口 RS232（电子秤 / 部分打印机 / 数字客显）

设备路径：`/dev/ttyS*`（POS 惯例 ttyS4 分给电子秤；一体秤实测 ttyS3@9600）、`ttyUSB*`（USB 转串口）、`ttyACM*`（CDC）、ttyAMA/ttyHS/ttyMT/ttyMSM（ARM/MTK/高通 OEM 变体）、`/dev/serial/by-id|by-path`（稳定符号链接，按路径重插不稳）；Windows 侧为 COM 口 + 波特率设置。操作卫生：连接后 / 读取前**清空输入输出缓冲区**（残留脏帧致首读解析异常）。

**串口 open 成功 ≠ 连的是秤：必须「收到有效数据」才算连接成功**——部分串口能打开但没接秤 / 接的是别的设备，绑错端口「连接成功」却永远没重量。修法 `connectWithValidation`：开串口后等有效称重数据（ latch 超时即断开试下一端口），收到数据才放行——批1「连接建立≠设备就绪」的串口版强化：不止等就绪，还要验「是你要的设备」。锚：82158f06f、334be5eeb。

**赋给 port 的 config 不可 dispose——悬垂指针 native 崩（当日回滚）**——`SerialPortConfig.dispose()` 释放底层原生结构，而 `_port!.config` 随后仍被读取（日志 / 波特率比较）→「应用停止工作」；放开注释当天即整体回滚，现行赋值后无任何 config dispose 调用（接受原生小泄漏或换 API 语义）。锚：6e75ff01f、a448ce79d。

**高频设备流消费策略终态：latest-wins + 节流，禁定长门控与计数阈值重连**——定长缓冲处理把人机交互（界面改重量）与机器连续帧耦合坏（门控吞掉人工改重窗口）；重连判据计数阈值对高频流无意义（200 次几秒打满），**持续异常时间窗（3s）**才区分抖动与真断；帧率高于 UI 需求时消费端节流（500ms trailing）、reader 只留最新包（`_pendingData` latest-wins），日志降频（重量 3s / 原始数据 10s）。演化链 2026-01-05~06 集中反转（含同日 Revert ×2——读取策略改动须带可回退验证）。锚：63bd6b4f7、998cc3abd、d61a78847、9c7af4751、d96d8ce26、9aa3efeaa、8324d4947。

**双插件同带 libserialport.so → 加载冲突：插件内 so 改名收编**——elec_scale_plugin 自带 native 串口库与 flutter_libserialport 同名同符号；终态 = 插件内 so 改名（`libserialport_elec.so` + `loadLibrary("serialport_elec")`，四 ABI），**勿**换 pubspec 依赖（曾走 flutter_libserialport→libserialport 替换，已回滚——落卡防复述中间态）。锚：0f11e10a4、a7dd9536d。

**双实现（SDK+兼容）生命周期动词必须双路径对称**——`stopGetData()` 只停原始实现、漏停兼容实现，读循环（200ms 定时）又不检查 `isRunning`，数据永不停止；引入兼容 / 双模路径时 start / stop / reconnect 每个动词都要覆盖全部活动路径。锚：704bf2091。

（帧协议解析与粘包拆包的秤侧实证见「秤」节 S3 / S4 / S11/S12 指针；客显与秤是**平行双实现**（客显 serial_util.dart / 秤 electronic_scale_serial.dart，互不 import），config dispose 坑两文件同日同修——客显卡见「副屏 / 数字客显」节。）

### 秤（电子秤 / 收银秤：串口 / USB / 一体机）

蓝牙节秤零素材（在仓两秤插件均串口 / USB 链路，2026-09-24 全量检索确认）——秤卡集中于本节与串口 / USB 节。

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

### USB（扫码枪 HID 模式 / USB 打印机 / 钱箱 RJ11 经打印机触发）

**USB 连接态不可缓存布尔**——打印机断电重启 / 拔插后 App 侧一切「正常」但不再出纸：connect 若 `if(isConnected) return` 幂等空操作即踩（旧代码把 `openPort()` 注释掉、连接判断走 AtomicBoolean 缓存；2022 年同型坑复发两次）。连接态必须以 claimInterface / 端点实测为准。配套超时：Android bulkTransfer 500→800ms、Kotlin 层 DEFAULT_TIMEOUT_MS 0→5000ms（0=无限阻塞，挂死写线程）。锚：a660b9eaa、0b7addec7、caf9eab92、dcc747dbe、f52f68889。

**USB 同品牌多台打印机枚举被首台短路**——枚举 for 循环内「本设备不匹配」直接 `return false`，同 VID/PID 的后续设备不再登记（第二台永远不可用）。设备发现按「实例」而非「型号」收集，任何型号级短路都会吞掉多台同型设备。锚：77735d838。

**USB 位图不跟随 ESC a 居中**——同票文字居中正常、图片永远靠左：多数固件 `ESC a` 只作用于文字行、不作用于 `GS v 0` / `ESC *` 光栅。对齐必须在图像数据内按列宽 pad 空白列，不依赖固件。锚：117734499。

**USB 末包 NAK → bulkTransfer=0 → 无退避重试 → 连打 N 张不切纸的重复票**（芯烨 XP-A160H / 80TS 实证，最多 15 连）——bulkTransfer 返回 0 ≠ 设备故障，是**流控信号**；重试须退避（[3s,5s,8s]）+ 末尾单包容忍（`isLastChunk && data.length>1` 才抛）+ Kotlin 侧短退避。附：DLE EOT 状态查询对解析不全的固件会把后续数据字节吞进状态回复 → 乱码。锚：14b44ea25。

**HID 键盘流帧定界依赖后缀，后缀不结尾则整码收不到**——扫码枪出厂未配（或被改配置）不追加 Enter/Linefeed 时，以「收到回车」为结束判定的缓冲区永不结算；Android 另有「特殊结束字符」变体。修法：回车截断 + 超时间隔（500ms Timer）双通道结算。锚：a914dad79、a2e95a7a3、bbab3878a。

**HID 键盘流经 IME 层可被全角化**（Windows 中文输入法全角态：数字 / 空格变全角码点，校验匹配全失败）——全角空格 12288→32、65281–65374 减 65248 统一转半角后再比对。反方向同域坑：券码大小写敏感（抖音系），客户端归一化即改码、核销必失败——「全角必须转」与「大小式不得转」分开判。锚：db82458e5、d5cb20021、7958d5434。

**HID 键流逐按键重组字符串：落单代理项写 TextField 即崩**（"string is not well-formed UTF-16"）——条码混入非 BMP 字符（emoji/生僻字）时代理项两半分属不同按键事件，任一半丢失即落单；聚合缓冲出口须 UTF-16 清洗 + 写框前兜底；退格须「先取内容再回写删末字符」（先 clear 再对空 buffer substring = 越界异常被吞、实际全删）。锚：4d2a89229。

**HID 键流双写：字符同时投递给全局钩子和焦点控件**（Windows 搜索框常驻焦点：枪扫码污染搜索框被当商品搜索 / 反向 69 码触发错路径）——逐字符回调层做类型过滤无效（每次只收到部分条码无法判型）；类型判定挪到 debounce 汇点 + 识别成功后同步清焦点框残留（抢在 debounce 前，异步延迟清不及）。锚：a3eaa1adc、bade35164、53040ad80、535eba157。

（Windows IME 吞扫码枪字符系框架级坑，住 platform-pitfalls.md，此处不重复。）

（Android 14+（targetSdk 34）上 USB 打印机 / 双秤插件会**先**炸于广播注册——`registerReceiver` 二参重载抛 IllegalArgumentException、filter 漏注册 DETACHED action 使拔出检测成死代码；OS 级主卡在 platform-pitfalls.md Android 14 节（锚 4ee867142），本节设备卡在 14 设备上须先过该门才谈得上连接逻辑。）

### 网口（打印机）

**TCP write 成功 ≠ 出纸**——「日志全是打印成功但后厨没纸」：connect(ip:9100)→write→close 全程无缺纸 / 无确认语义；多菜连发的 connect/write/disconnect 风暴使中低端网口模块（赛想 SX-86V / KeRuYun DP780 实证）偶发丢缓冲。修法：按打印机粒度的兼容模式（连发间隔保护，派发延迟 1000→2000ms，结构上不引入动态计算/定时器）。排障纪律：「老版本正常」= 出问题→升级的时间巧合，不能当回滚依据；RST 风暴判据指向设备劣化→断电重启 / 固件升级。残余风险：socket 错误分支清队后不回重试队列 = 该票直接消失（上报失败不重试）——接入网口打印时须自查此分支。锚：173e731c8、de9fe1500；doc/lan_printer_miss_print_case_report.md（301 行案卷含行业对比）。

**socket 写异常未捕获 → 打印 isolate 退出重启循环**——对端（打印机 / 劣化模块）中途关闭连接时，await 抛异常穿透 isolate 主循环 → isolate 死亡重建、任务全部积压。修法：逐包 try/catch + socket 错误标记（主 isolate 不重启）+ close 前 `await socket?.flush()`（Dart Socket 写有用户态缓冲，不 flush 丢尾包）。锚：58aa400c7。

**失败重试队列死代码 + 无退避冲击 + 单任务卡死拖死整队**——失败队列处理放在永不执行的分支 = 死代码（积压票永不补打）；重试须指数退避（10/20/40/60s）+ 次数上限 + 丢弃时上报服务端；`_isPrinting` 永真须看门狗（阻塞 >50s 强制复位）。锚：9d410dd46、359e92ed9、a50a6b9fa。

（MQTT 断线重连后 print topic 静默失订 → 全店收不到单：「重连成功 ≠ 订阅还在」，须显式重订 + 身份就绪后再过滤——归网络域，锚 12365c95a / 693904bbb / doc/pitfall_knowledge_base_2026.md。）

### 打印专项（跨链路）

**58mm 多列 rowWithSpaces 无限递归 → 栈溢出闪退**——行内容超列宽（384dot）时空格补齐按固定步长递归不收敛；文本补齐 / 折行类递归必须证明收敛，或以「剩余预算>0」做护栏。锚：5322bcccc。

**ESC/POS 控制序列耦合三坑**——① `generator.image()`（ESC *）内部隐式发 `ESC 3 0`+`ESC 2` 破坏调用方设定的行距，QR / 图行后必须重设；② hybrid 混排末尾须先 `ESC 2` 复位再空行走纸（否则走纸距离与纯文字票不一致）；③ `GS v 0` 光栅无旋转参数，旋转 90° 打二维码得不可扫图（须走 ESC * 或矢量路径）；密度语义：ESC * ≈180dpi、GS v 0 ≈203dpi，同图两链路差 12.8%。工程教训：改 vendored 插件代码必须看**生成物的实际字节**而非只读源码（`_toRasterFormat` 行填充写在逐像素循环内 → 输出恒全白，曾以旁路函数规避）。锚：c39d0be7c、7d825922d、a1467c1ef、af087bc88；docs/superpowers/specs/2026-06-17-esc-pos-hybrid-print-design.md。

**GBK 固件编码逐字符不可靠，判定与编码必须镜像**——扩展拉丁字符 `ñ/ç/ö/ß` 实测不可编码而 `à/é/ü` 可（逐字符判断不可靠）；`€` 需特殊映射 0x80；「这行可编码吗」的判定函数必须与实际编码函数的替换表**完全镜像**，否则判定可编码、编码时却被替换（两头不一致）；降级判定按字符计数（>60% 非可编码才整行转图）。锚：a5d675f00、f810f0047。

**打印输出是 1-bit：二值化吃色吃浅灰**——彩色图取 R 通道 → 红 R=255 变白 = 无墨（红色元素整个消失）、绿蓝变黑块；阈值 127 二值化下 #333 灰字笔画边缘被吞；58mm 图层宽超 384dot 丢末列。收口：文字色一律纯黑、彩色素材强制灰度化或禁上、58mm 图层 370px（输出 368=46×8 列对齐）。锚：827e1b01a、42fdc894d；doc/printer_image_printing_knowledge.md §3.2。

**截图打印链路 DPI / scale 类坑**——裸 `MemoryImage(bytes)` 把物理像素当逻辑像素（Windows 2K 屏同一 logo 比 Android 小 ~28%）；样式裸像素数字逃过 `.w` 适配即错位；SDK 布局用 `image.width/_scale`，ImageProvider.scale 缺失 = DPI 错位。修法：scale 传 pixelRatio 倒数（现行实现变量化传入）、裸像素一律 `.w`、scaleDown 只缩不放（放大必经插值+阈值二值化断线）、超纸宽按满宽拍板并令旧缓存 key 失效；机制级守护测试在位。锚：e8834d496、c55536e0a、5d279115f。

**多列排版手段必须按打印引擎分流，禁止全链路统一**——蓝牙链路仅文字只能拼空格；原生 multiColumn 机型拼空格反而列重叠（字符宽度模型不同）；ESC/POS 没有可靠「列」原语，排版 = 每固件独立实现（内置机商米 / 一敏 / 美团各不同）。vendored esc_pos_utils 的 collection 版本要钉（^1.18.0——SDK 锁定包，放宽须带兼容注释）。锚：61afe68e8、9083576b9；doc/hybrid_multicol_image_row_wrap_design.md。

**字形缺失（维语 / 阿拉伯语 / 泰语等设备无法渲染的 Unicode）用文字渲染为图兜底**（与坑卡「系统字体回退不可信」联动）。锚：aaa9995fd（ParagraphBuilder 文字转图渲染器）。

### 内置打印机（一体机：商米 / 一敏 / 美团 / 联迪类）

**特殊符号致单据截断**——`·`（U+00B7 间隔号）在内置打印 SDK 文本渲染引发截断（`•` U+2022 项目符号已处理 ≠ `·` 已处理）；替换表按「实测打挂」清单维护（·、•、€ 等），别按 Unicode 区间推理。锚：62d364b53。

**熄屏亮屏后打印机服务休眠**——printBind=true 缓存「已绑定」，打印服务进程熄屏被回收后状态失效（亮屏后再也不打，重启 App 恢复）；每次打印前实时 `getPrinterStatus() != NORMAL` 即强制重绑——与 USB「连接态不可缓存」同构家族。锚：66a556e1a。

**AIDL 服务绑定链 × 副屏开启**——商米 T1 开副屏后 openDrawer 静默 false：bindService 回调未到达 / 到达即 NPE（确切机制未查明，如实标注）；修法 = 调用前显式 init + bind/connect/openDrawer/drawerStatus 全链路日志兜底。锚：32bb147da（与钱箱节互链）。副屏开启改变服务/进程生命周期同族坑另见副屏节「exit 先关副屏窗口」卡；支付外设屏类设备开钱箱走系统广播通道（非 AIDL 非 RJ11），见副屏节 ef60 卡。

### 标签打印机（TSPL）

**关端口延迟须按指令体系区分**——TSPL 固件消化 `PRINT m,n` 后走纸 / 定位比 ESC/POS 即时执行慢，写完固定短延迟即关 USB 口会丢末标签（历史修法：TSPL 800ms / ESC/POS 600ms 分治；现行实现已重构为重试退避 [500,700,900]ms——机制沉淀不变：标签机固件是「命令缓冲执行制」，端口关闭时机不能沿用票据机经验值）。锚：1a453167c、a8c5e52a6。

### 扫码专项

**手动弹窗与全局盲扫双路并发，同码双触发**——弹窗自身输入处理与全局盲扫链同时消费同一枪扫 → 支付 / 会员登录被触发两次；修法 = 引用计数 pause/resume（弹窗挂起对应类型盲扫），此机制是后续全部盲扫防重的闸门底座。锚：558f9df29、9fe749e3c；doc/blind_scan_dup_guard_design.md。

**支付结果轮询并发回包，重复入账**——queryPayStatus 并发返回多笔成功同时进 addPayList；汇点须 payId 查重 + 标志复位须 whenComplete / finally 语义（异常路径悬挂 = 永久阻塞后续结账）。锚：a160b33f7。

**「扫出来短码」≠「中文输入法」**——以长度启发式（<5 字符）猜 IME 问题的提示话术是误报源（短码可能是会员卡号本尊 / 残码）；排障话术不得以伪因提示商户。锚：0287a3486。

### 钱箱（RJ11 经打印机指令触发 / 一体机内置通道）

**开钱箱前连接结果必检查，失败裸发指令闪退**——connect 失败（设备离线 / 占用）后仍调 drawer()，对无效句柄操作崩到 native；`connect == success` 才发 kick + close（闸门现行在打印管理器层，非早期 helper 文件）；打印机启用状态判定用 enable 枚举、别用 status 字符串语义。锚：0e4cd1da3、6b7c77fd7。

**指令「发了但没响」：写后关闭生命周期错位**——`drawer(); close();` 序列中 Dart 层 close 抢先释放，kick 指令未真正到达设备；修法 = 取纯指令字节（drawerCmd）经 writeBytes 直写、由插件层统一收尾（插件层 writeBytes 自动关闭连接，Dart 不再手动 disconnect）；顺带：vendorId / productId 可空不可强解包。锚：5c8944369。

**开钱箱广播给非当前设备**——配置列表里的历史设备 ≠ 物理在位设备；发指令前须本地 USB 枚举比对（Windows 按 printName / Android 按 vendorId+productId），仅当前在连的打印机才发。锚：3c059a47a、1cf37aedc。

**连接建立 ≠ 设备就绪：首包字节丢失**——connect 成功后立即写首包被固件吞（钱箱 kick 通常就是唯一一包，丢头 = 完全失效，偶发不开 / 时好时坏）；连接后 delay 200ms 再写、写完 delay 200ms 释放；插件层首包前再加就绪延时（历史 150ms、现行 Android 侧 100ms——值随版本演化，机制不变）。锚：cd88b2717。

**一体机内置通道（AIDL）开钱箱失效**——见「内置打印机」节商米 T1 卡，锚 32bb147da。

**触发条件求值层：整型解析当通用数值解析**——开班备用金「20.5」这类小数 `toInt()` 解析为 null → 金额>0 条件不成立、钱箱不弹；金额判定用 toDouble。锚：f10af0642。

## 多屏类

### 副屏 / 数字客显

Flutter 多 window（`View` / Display API）或平台通道投屏；主副屏生命周期与分辨率差异。副屏三条链路（Android Presentation 双引擎 / Windows desktop_multi_window / ef60 支付外设屏）+ 数字客显（串口 COM 链路：Windows COM 口 / Android 串口，与秤平行双实现）。

**副屏是第二 FlutterEngine：插件不自动注册、初始化不裸奔**——子引擎上 GeneratedPluginRegistrant 不执行，调任何插件 API 必 MissingPluginException（实测案例：30s 轮询类调用刷屏 203 条/100min）。本项目终态选「不注册任何三方插件」路线（registerThirdPlugins 整体注释），副屏侧代码禁调未注册插件、轮询首错即停；确需插件走白名单手动注册。配套两条：① 子引擎插件字段勿用 lateinit——detach 后访问必 UninitializedPropertyAccessException，改可空 + `?.`，引擎初始化链（FlutterEngine 构造 + executeDartEntrypoint）整段 try/catch；② 副屏入口不做主屏全局初始化（「某些初始化在副屏环境下可能失败导致闪退」——注释原文）。与秤 mainLooper 卡同族：回调/引用生命周期对齐问题在副屏以「引擎」为界。锚：8a912208b、d0abdfd8e。

**Windows 副屏窗口销毁后主屏仍 invokeMethod → PlatformException(target window not found)**——windowId 窗口关闭后失效，只判 `window == null` 不够，须 `window == null || windowId < 0` 早退 + try/catch + 异常落日志；配套：config 下发前查 subScreenType==close 早退、副屏收到新 config 须重置页面状态防残留。锚：8f8b37c53、079686f38、99d488af5。

**Windows 开副屏时 exit 前必须先关副屏窗口，否则进程杀不掉**——副屏子窗口（独立引擎）未先销毁，`exit(0)` 时窗口/引擎句柄悬挂、界面关了进程残留；`window?.close()` 是异步操作，关窗后须延时（500ms）再退（Android 走 SystemNavigator.pop）。八笔同日 cherry-pick 变体收敛一卡。锚：c769d304d、1f0b0446f、929657136。

**多窗口入口判定必须校验 args 协议魔数，不能只看参数个数**——exe 被更新器/快捷方式带参二次拉起时 `args.length > 1` 误判为子窗口进程，主界面不出；desktop_multi_window 协议 = 新进程 + `args[0]=='multi_window'` + windowId + json。Android 侧入口判定原语不同（路由名判定），两平台不可混用。锚：0c55f780e。

**主副屏状态不同步是引擎隔离的必然：语言/货币符号须显式推送**——副屏独立引擎，主屏 updateLocale 只影响主引擎；货币符号不同步是发布日志级用户可见 bug。终态机制：每次切页事件**捎带** languageCode/countryCode/currencySymbol（不依赖一次性同步）+ null→"" 判空加固（`Locale(null,…)` 崩溃风险）。教训：跨引擎状态没有共享内存幻觉。锚：23ece0169、53c917787、927dd6778、eb42afc90。

**跨屏数据传输必须全链 toJson——嵌套实体未序列化 + 键名错写双杀**——实体对象直接塞 map 跨 MethodChannel 静默丢数据（编译期无感知）；同一处还键名错写（activity 写在 coupon 键下）。纪律：跨屏/跨 channel 只传 JSON 原语，toJson 覆盖全部嵌套字段且键名与字段对齐；跨屏专用 DTO 集中建。锚：00c486752、dc9f32197。

**ef60 类支付外设副屏：屏显与支付交易共用 ECR doTransaction 通道**——排障时勿把屏显流水当支付交易误读（transType 靠约定区分）；金额字段协议要求 **12 位定长字符串**（不足补位）；功能开关是三重门（平台 + 渠道 + 用户设置），排查先逐门确认；SDK 连接态双标志防重入、onConnectError 后须完整重置再 doInit；此类设备开钱箱走**系统广播**（`android.intent.action.CASHBOX`）——与打印机 RJ11 kick 完全不同通道。注意：仓内曾硬编码内网测试 IP 残留（已泛称化，接入时自查）。锚：dc9f32197、2adfa95b1、d2b20c1d8、8db736b8c。

（Android 14 副屏窗口类型 / 广播注册族住 platform-pitfalls.md——targetSdk 34 起副屏与 USB 外设先炸于 OS 层，再谈本节设备坑。）

**客显串口异常面在枚举 / 构造段，先于 open**——无串口机器上 `SerialPort.availablePorts` 直接抛异常（Windows 缺 serialport.dll 同炸，日志「串口初始化失败，可能是缺少serialport.dll」）→ 包 try/catch 返回 `[]`；释放路径 `_port!` 空崩 → 全空安全 `_port?.close(); _port?.dispose(); _port = null`；构造器里 `_init()` 与否当日反复（禁→恢复，终态恢复）。单例不自毁（`_ins = null` 曾致懒汉重建循环）——「连接建立≠设备就绪」再前置一步：**设备枚举都可能失败**。锚：50b0e9f64、7a036f353、2fe0464a1、48f26cda3、895038715、cc63f6135。

**关开关清零竞态：异步写未完成即同步释放 → 清零写不出去**——`writeByteLEDByAddress` 是 async Future，写完 0.00 立即同步 `disposeRecourse` 会把端口在写入完成前关掉（27 分钟两笔接力修复）。修法 = 写函数加完成回调参数，释放挪进回调再 +100ms 延迟——async 写 + 同步释放的时序错位是串口设备通用坑。锚：053e8dae5、db22ac18a。

**客显开关策略三连反转，终态 = 保持连接、仅关开关时延迟关**——随用随开（每次写建连）→ 写完即关（金额显示毕 close）→ 终态：连接常驻、`resetZero` 关开关时经回调延迟关；写失败仅释放资源保留对象（下次重开复用）。附带两处**现行缺陷**（接入前自查）：`close()` 方法已无任何调用方（死代码）；重试计数 `retryCunt = 3` 只减不复位——单例终身累计 3 次 open 失败后零重试（疑似「开机设备就绪慢当天不显示」机制之一）。锚：ac49c312c、425e58d2b。

**LED 字库仅 0-9 与点：金额必须无千分位格式**——字表无逗号，`currencyFormat`（千分位）传入即抛 → 统一 `currencyFormatWithDef`（两位定长无分隔）。**现行缺陷**：`isValidPrice` 正则交替未分组（`^([1-9]\d*\.?\d*)|(0\.\d*[1-9])$` 前半支无 `$` 锚、后半支无 `^` 锚）——「0.50」类 0.x0 金额判 false 回退显示 0.00（0.99 正常）、`12ab` 脏串被前半支放行后字表取值抛异常；正则多分支锚定必须整支闭合。锚：477e3e0b8。

**写失败自愈链反复：无界递归重试是反模式**——open 失败 catch 里延迟 500ms 再入自身（无界递归，设备长期不在时无限循环）→ 删递归改单次重写 → 终态不再重写（仅释放资源，下次业务写时重建）。失败重试必须有次数边界与退出路径。锚：31a480e27、d5c5ffe3e。

**开机客显不显示 = 串口流控线未配置**——v2.5.13 发布注记「开机不显示」修复主锚：构造器恢复 `_init()` + 补全六项流控参数（parity/xonXoff/rts/cts/dsr/dtr，终态现行在位）+ 单例不自毁。机制推断「RTS/DTR 未置位时部分 LED 客显不理数据」**无日志佐证，如实标注**——但「串口参数必须逐项显式配置、不能只设波特率」的教训独立成立。锚：f5e784b58。

**关客显开关须清配置释放 COM 口，且与秤互斥提示**——关闭开关同步清 SP 缓存配置释放端口（否则重开机后 COM 口仍被占）；设置页 COM 下拉对被秤占用的端口标注「已被电子秤占用」（秤/客显互斥同口，选型即冲突预防）。锚：89bc52b2b。

## 语音播报（收银语音 / 叫号）

收银语音播报 = **预录 mp3 资产**（zh / zh-hk 双语种目录）+ **双引擎**（win10+ / Android / iOS 走 just_audio；win7/8/未知 Windows 走 minisound FFI，或 SP 手动开关切入）+ 单例任务队列（dealing 门 + 完成回调）+ MQTT 推送触发。本仓无 TTS 路线（全仓零命中）、云播报盒 / 收款云喇叭零素材（如实不预置）。网络侧坑（QoS / 推送到达 / 重连订阅）归网络域，见节尾指针。

**播报触发源生命周期绑页面 = 多实例重复播 / 离页退订无声**——外卖列表逻辑多处 binding 各自注册 MQTT 消息监听 → 一条推送播 N 遍；`onClose` 退订 topic → 离开页面即无声。终态：全局单例 `Get.put(permanent: true)` 注册、删页面注册点与退订。教训：全局型触发源（播报 / 轮询 / 心跳）不随页面生死，注册一次、不退订。锚：10ca98c2e、a547410d5。

**音频焦点被抢占 → 播报队列停摆**——just_audio 被其他音频（提示音等）打断后 `playing=false && processingState=ready`，任务完成回调永不到来，`dealing` 门卡 true，后续所有播报哑。修法 = playerStateStream 监听该状态自动续播 + 每个播报入口先 `restartLoop()` 重放队头任务（新任务强抢重放被抢占队列）。锚：4e12202a7。

**Windows 版本 → 引擎路线九笔摇摆（2024-01 ~ 2025-06）**——win7 上 just_audio（系统媒体栈）闪退 / 无声 → 初始化 try-catch 止血 → 整体屏蔽 return → 版本门禁静默跳过 → minisound（miniaudio FFI）兜底支持 win7 → 「win10 也走 win7 流程」4 天后一行 diff 翻回 just_audio → 全量压 minisound → 回退版本门禁 + SP 手动开关（异常机型用户自切）。教训：引擎选型判定靠 osVersion **字符串包含匹配**，一行 diff 即全量改线上路线；排障先查开关与版本判定分档。锚：e828deabd、fef932d57、f7867f249、93939fe13、e3b0fa003、c362e295f、cd6ea0d3e、bd96894f2、59cace9f2。

**语音包白名单多份维护漂移 → 静默不播（本域头号坑）**——`checkVoiceBag` 要求播报序列全在白名单内否则**静默 return**；白名单曾有 2-3 份拷贝（主引擎 / win7 引擎各自清单），新增播报类型只改一份 → 部分平台不播、无报错无日志。修法 = 提取共享常量单一来源（但提取当日仍漏 3 行、同日补齐）。**现行缺陷**：京东出餐完成播报是哑弹——文案→key 映射在（「京东上报出餐完成」→ wm_jd_chucan）、白名单与资产均无此 mp3、触发分支在但前缀分派未接：上膛状态，谁接通谁踩；且校验失败日志曾被加后随重构消失 = 重新纯静默。纪律：新增播报类型 = 资产 + 清单 + 文案映射 + 前缀分派**四处同步**，校验失败必须留日志。锚：d394162d7、45eed8582、cb51138cc。

**双语种资产漂移：校验只对默认语种清单**——播放路径按渠道选 zh-hk 目录，白名单校验却只查 zh 清单；zh-hk 缺 16 个资产（取消 / 退款 / 出餐 / 付款码类），特定渠道触发即运行时找不到资产 → 异常任务丢弃（**现行缺陷**，暴露面随渠道业务开通而变）。纪律：多语种白名单逐语种成对维护，校验与播放**同源**（校哪个目录用哪个清单）。锚：d33a63072。

**金额→中文语音读法：跨级缺零 / 高位截断 / 无守卫**——旧算法「100002」读漏零、千万位以上直接截断、无入参守卫；重写为万级 / 个级分段（补零衔接）+ 范围守卫（越界记日志拒绝播报）。金额读法是对账敏感面：改动必须带跨级零、边界值用例。锚：ac878f9cd、ed65f8b22、42aa6f9a4、7178aa9b2。

**设置开关「显示值 ≠ 生效值」两张皮**——两笔实证：① 初始化 `defValue: true` 而生效侧按 false 处理，界面画开实际关；② 控件绑错变量（优惠付款码开关界面实际读写订单播报开关的值）。开关类界面：初始化默认值、控件绑定变量、生效侧读取三处逐一对账。锚：c86a75a53、aab31168b。

**win7 引擎播放失败不回调 → 队列永久卡死（现行缺陷，无事故锚）**——win7 侧 `_voicePlay` 的 catch **只记日志不调完成回调**，对照 just_audio 侧 catch 有「丢掉当前失败的任务」（`taskFinishBack(true)`）；叠加队列两处（callback==null 早退 / loop 自身 catch）均不复位 dealing 门 → win7 机器一次播放失败后所有播报静默到重启。加重项：taskId 随机生成去重永不命中；播完靠 `Future.delayed(sound.duration)` 计时、无完成回调语义。修法方向 = 对齐 just_audio 侧 catch 补回调。接入 win7 播报前必查此点（锚：现行代码，接入前自查）。

（网络域指针：takeout 主题推送丢失 → 自动接单无声——QoS 升 atLeastOnce 后仍丢 = 下行推送无对账，与网口打印「下行无确认」同型归网络域；叫号 TV 经 MQTT callNumberTopic + 大屏 socket 下发，收银侧触发与开关落本节、送达属网络域——见「独立 App 类」KDS 节。）

## 独立 App 类（指针节）

### KDS / 叫号大屏

另一端是**独立 app**（另一台设备），走网络同步协议（WebSocket / 轮询）——归 backend 网络域，不属本机设备通信；设备侧坑（大屏分辨率 / 常亮 / 开机自启）住项目 memory 坑库。收银侧叫号触发与语音开关见「语音播报」节（MQTT callNumberTopic + voiceCallFlag 字段控制 TV 端是否出声）。
