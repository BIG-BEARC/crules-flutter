# IoT / 外设通信（收银硬件接入）

> 触发场景：接入 / 调试外设、多屏、设备类排障前 Read 本文件。
> 来源：backend 角色卡「设备通信铁律」升格（S14 处置，2026-09-08）+ saas-cashier（日活 7w 餐饮 POS）8 类设备实证。批1（打印机 / 扫码枪 / 扫码盒 / 钱箱）2026-09-24 沉淀；批2（电子秤 / 副屏）、批3（客显 / 语音播报）占位待采。
> 归属：硬件协议 / 设备行为级坑（含型号怪癖——**型号是主检索键**，不外放消费工程 memory）住本文件；框架级坑（OS / SDK / 依赖交叉，如 Windows IME 吞扫码枪字符）住 `references/platform-pitfalls.md`，本文件只留指针。
> 锚口径：commit 哈希为 saas-cashier 私有仓锚，按其仓内口径视作**信任声明**；`doc/…` 路径为其仓文档（可复核锚优先）。全卡核验 2026-09-24。
> 升格触发：多轮自持的 IoT 调试任务（协议调试 + 原生通道一体）实证后，评估独立 `iot` agent——素材即本文件。

## 通用铁律（自 backend 角色卡迁入，原文全量）

- 写入与读取要有应答确认机制，不要「发了就当成功」
- 分帧 / MTU 安全值要保守，不踩协议边界
- 先订阅再写入，否则通知丢失
- 不要在长生命周期 stream 上用一次性消费操作（如 `firstWhere`）——长流持续监听，短流才一次性
- 重连必须 dispose 旧上下文创建新的，不复用旧订阅
- 协议文档不可全信，**以实际设备字节日志为准**
- 长操作要有超时和断连处理，不阻塞事件循环

## 外设类（按通信方式分节）

### 蓝牙（BLE / SPP：打印机、扫描外设）

**iOS BLE 写入超 MTU 被静默截断**——症状：蓝牙票「发送失败≈4s」且只出一半，无异常无日志（静默丢数据）。withoutResponse 队列满即丢；iOS 15.6 典型 ATT MTU=185 → 单包上限≈182，分块 200B 即超；全仓 6 个打印插件曾 0 处检查 `maximumWriteValueLength`。修法：withResponse 串行 + 按 MTU 分块 + 连接失败 8s 兜底。锚：f8c22f969、47de61637、cee15a646；doc/ios_bluetooth_print_crash_fix_design.md §8。

**Android 蓝牙 SPP 写入须「小块 + 节流」——与 USB 连发相反（实测）**——16KB+flush / 一次性 write / 3KB 连续+末尾 flush 全部卡顿；**1KB（恰一个 L2CAP/RFCOMM 帧）+ sleep(10ms) 节流最优**。根因：USB bulkTransfer 有精确硬件流控可连续发；蓝牙射频吞吐 + RFCOMM 协议栈须软件节流匹配打印机处理速度。锚：fef75d305、e58120e9f。

**iOS 蓝牙「每次 connect 前强制 disconnect」可引爆休眠 IUO 缺陷（SIGTRAP 冷启动崩溃循环）**——Swift 侧 `connectedPeripheral: CBPeripheral!` 为 nil IUO 时强解必崩；典型自锁链：一个修复把死代码变活、激活另一处休眠缺陷。修法：connect 幂等快路径 + 单槽 FlutterResult 模式；教训：信号名不能作判据（SIGTRAP 非 SIGILL）。锚：02e22a0d3、f8c22f969、1071d157c；doc/ios_bluetooth_print_crash_fix_design.md（D1–D13 全缺陷表）。

**蓝牙链路光栅位图（customImg）不放开（工程结论）**——放开后等待久 / 出纸卡顿 / 一定概率乱码（乱码=票据损坏、资损级）；SPP 吞吐低 + 部分固件接收缓冲小，光栅大包不可靠，分包优化换不来收益（已实测拍板）。维持仅文字拦截，别试图放开。锚：da32ad182；doc/printer/decisions.md DEC-2026-09-11。

**蓝牙设备 MAC 大小写不归一 → 同机重复 / 编辑误拦**——iOS 大写 / Android 小写混用同一批设备；比较前统一大小写、编辑查重排除自身 id。「connect 前 disconnect」在 Android 侧是刚需、在 iOS 侧有崩溃副作用（见上卡）——平台差异须分支处理，不能一把梭。锚：cf73751d5、ecd66a354；doc/pitfall_knowledge_base_2026.md §三。

### 串口 RS232（电子秤 / 部分打印机）

帧协议解析、粘包拆包。【无实证不预置——批2 电子秤采证后处置】

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

**AIDL 服务绑定链 × 副屏开启**——商米 T1 开副屏后 openDrawer 静默 false：bindService 回调未到达 / 到达即 NPE（确切机制未查明，如实标注）；修法 = 调用前显式 init + bind/connect/openDrawer/drawerStatus 全链路日志兜底。锚：32bb147da（与钱箱节互链）。

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

Flutter 多 window（`View` / Display API）或平台通道投屏；主副屏生命周期与分辨率差异。【待项目沉淀——批2 采证】

## 独立 App 类（指针节）

### KDS / 叫号大屏

另一端是**独立 app**（另一台设备），走网络同步协议（WebSocket / 轮询）——归 backend 网络域，不属本机设备通信；设备侧坑（大屏分辨率 / 常亮 / 开机自启）住项目 memory 坑库。
