# 打印（票据 / 标签打印机）

> 触发场景：接入 / 调试打印机（蓝牙 / USB / 网口 / 一体机内置 / 标签）、打印排障前 Read 本文件。
> 来源：saas-cashier（日活 7w 餐饮 POS）打印域实证；2026-09-24 自 `iot-devices.md` 三域拆分迁入，卡面逐字迁移。
> 归属：打印设备 / 协议行为级坑（含型号怪癖——**型号是主检索键**）住本文件；框架级坑（OS / SDK / 依赖交叉）住 `references/platform-pitfalls.md`；MQTT 推送到达性（重连失订 / QoS 双轨）住 `references/network-comms.md`；通用铁律 / 钱箱 / 副屏 / 语音播报住 `references/iot-devices.md`。
> 锚口径：commit 哈希为 saas-cashier 私有仓锚，按其仓内口径视作**信任声明**；`doc/…` 路径为其仓文档（可复核锚优先）。

## 蓝牙打印（BLE / SPP）

**iOS BLE 写入超 MTU 被静默截断**——症状：蓝牙票「发送失败≈4s」且只出一半，无异常无日志（静默丢数据）。withoutResponse 队列满即丢；iOS 15.6 典型 ATT MTU=185 → 单包上限≈182，分块 200B 即超；全仓 6 个打印插件曾 0 处检查 `maximumWriteValueLength`。修法：withResponse 串行 + 按 MTU 分块 + 连接失败 8s 兜底。锚：f8c22f969、47de61637、cee15a646；doc/ios_bluetooth_print_crash_fix_design.md §8。

**Android 蓝牙 SPP 写入须「小块 + 节流」——与 USB 连发相反（实测）**——16KB+flush / 一次性 write / 3KB 连续+末尾 flush 全部卡顿；**1KB（恰一个 L2CAP/RFCOMM 帧）+ sleep(10ms) 节流最优**。根因：USB bulkTransfer 有精确硬件流控可连续发；蓝牙射频吞吐 + RFCOMM 协议栈须软件节流匹配打印机处理速度。锚：fef75d305、e58120e9f。

**iOS 蓝牙「每次 connect 前强制 disconnect」可引爆休眠 IUO 缺陷（SIGTRAP 冷启动崩溃循环）**——Swift 侧 `connectedPeripheral: CBPeripheral!` 为 nil IUO 时强解必崩；典型自锁链：一个修复把死代码变活、激活另一处休眠缺陷。修法：connect 幂等快路径 + 单槽 FlutterResult 模式；教训：信号名不能作判据（SIGTRAP 非 SIGILL）。锚：02e22a0d3、f8c22f969、1071d157c；doc/ios_bluetooth_print_crash_fix_design.md（D1–D13 全缺陷表）。

**蓝牙链路光栅位图（customImg）不放开（工程结论）**——放开后等待久 / 出纸卡顿 / 一定概率乱码（乱码=票据损坏、资损级）；SPP 吞吐低 + 部分固件接收缓冲小，光栅大包不可靠，分包优化换不来收益（已实测拍板）。维持仅文字拦截，别试图放开。锚：da32ad182；doc/printer/decisions.md DEC-2026-09-11。

**蓝牙设备 MAC 大小写不归一 → 同机重复 / 编辑误拦**——iOS 大写 / Android 小写混用同一批设备；比较前统一大小写、编辑查重排除自身 id。「connect 前 disconnect」在 Android 侧是刚需、在 iOS 侧有崩溃副作用（见上卡）——平台差异须分支处理，不能一把梭。锚：cf73751d5、ecd66a354；doc/pitfall_knowledge_base_2026.md §三。

## USB 打印

**USB 连接态不可缓存布尔**——打印机断电重启 / 拔插后 App 侧一切「正常」但不再出纸：connect 若 `if(isConnected) return` 幂等空操作即踩（旧代码把 `openPort()` 注释掉、连接判断走 AtomicBoolean 缓存；2022 年同型坑复发两次）。连接态必须以 claimInterface / 端点实测为准。配套超时：Android bulkTransfer 500→800ms、Kotlin 层 DEFAULT_TIMEOUT_MS 0→5000ms（0=无限阻塞，挂死写线程）。锚：a660b9eaa、0b7addec7、caf9eab92、dcc747dbe、f52f68889。

**USB 同品牌多台打印机枚举被首台短路**——枚举 for 循环内「本设备不匹配」直接 `return false`，同 VID/PID 的后续设备不再登记（第二台永远不可用）。设备发现按「实例」而非「型号」收集，任何型号级短路都会吞掉多台同型设备。锚：77735d838。

**USB 位图不跟随 ESC a 居中**——同票文字居中正常、图片永远靠左：多数固件 `ESC a` 只作用于文字行、不作用于 `GS v 0` / `ESC *` 光栅。对齐必须在图像数据内按列宽 pad 空白列，不依赖固件。锚：117734499。

**USB 末包 NAK → bulkTransfer=0 → 无退避重试 → 连打 N 张不切纸的重复票**（芯烨 XP-A160H / 80TS 实证，最多 15 连）——bulkTransfer 返回 0 ≠ 设备故障，是**流控信号**；重试须退避（[3s,5s,8s]）+ 末尾单包容忍（`isLastChunk && data.length>1` 才抛）+ Kotlin 侧短退避。附：DLE EOT 状态查询对解析不全的固件会把后续数据字节吞进状态回复 → 乱码。锚：14b44ea25。

## 网口打印

**TCP write 成功 ≠ 出纸**——「日志全是打印成功但后厨没纸」：connect(ip:9100)→write→close 全程无缺纸 / 无确认语义；多菜连发的 connect/write/disconnect 风暴使中低端网口模块（赛想 SX-86V / KeRuYun DP780 实证）偶发丢缓冲。修法：按打印机粒度的兼容模式（连发间隔保护，派发延迟 1000→2000ms，结构上不引入动态计算/定时器）。排障纪律：「老版本正常」= 出问题→升级的时间巧合，不能当回滚依据；RST 风暴判据指向设备劣化→断电重启 / 固件升级。残余风险：socket 错误分支清队后不回重试队列 = 该票直接消失（上报失败不重试）——接入网口打印时须自查此分支。锚：173e731c8、de9fe1500；doc/lan_printer_miss_print_case_report.md（301 行案卷含行业对比）。

**socket 写异常未捕获 → 打印 isolate 退出重启循环**——对端（打印机 / 劣化模块）中途关闭连接时，await 抛异常穿透 isolate 主循环 → isolate 死亡重建、任务全部积压。修法：逐包 try/catch + socket 错误标记（主 isolate 不重启）+ close 前 `await socket?.flush()`（Dart Socket 写有用户态缓冲，不 flush 丢尾包）。锚：58aa400c7。

**失败重试队列死代码 + 无退避冲击 + 单任务卡死拖死整队**——失败队列处理放在永不执行的分支 = 死代码（积压票永不补打）；重试须指数退避（10/20/40/60s）+ 次数上限 + 丢弃时上报服务端；`_isPrinting` 永真须看门狗（阻塞 >50s 强制复位）。锚：9d410dd46、359e92ed9、a50a6b9fa。

（MQTT 断线重连后 print topic 静默失订 → 全店收不到单：「重连成功 ≠ 订阅还在」，须显式重订 + 身份就绪后再过滤——已独立沉淀至 `network-comms.md` 连接生命周期节（头号坑卡），此处留指针；锚 12365c95a / 693904bbb / doc/pitfall_knowledge_base_2026.md。）

## 打印专项（跨链路）

**58mm 多列 rowWithSpaces 无限递归 → 栈溢出闪退**——行内容超列宽（384dot）时空格补齐按固定步长递归不收敛；文本补齐 / 折行类递归必须证明收敛，或以「剩余预算>0」做护栏。锚：5322bcccc。

**ESC/POS 控制序列耦合三坑**——① `generator.image()`（ESC *）内部隐式发 `ESC 3 0`+`ESC 2` 破坏调用方设定的行距，QR / 图行后必须重设；② hybrid 混排末尾须先 `ESC 2` 复位再空行走纸（否则走纸距离与纯文字票不一致）；③ `GS v 0` 光栅无旋转参数，旋转 90° 打二维码得不可扫图（须走 ESC * 或矢量路径）；密度语义：ESC * ≈180dpi、GS v 0 ≈203dpi，同图两链路差 12.8%。工程教训：改 vendored 插件代码必须看**生成物的实际字节**而非只读源码（`_toRasterFormat` 行填充写在逐像素循环内 → 输出恒全白，曾以旁路函数规避）。锚：c39d0be7c、7d825922d、a1467c1ef、af087bc88；docs/superpowers/specs/2026-06-17-esc-pos-hybrid-print-design.md。

**GBK 固件编码逐字符不可靠，判定与编码必须镜像**——扩展拉丁字符 `ñ/ç/ö/ß` 实测不可编码而 `à/é/ü` 可（逐字符判断不可靠）；`€` 需特殊映射 0x80；「这行可编码吗」的判定函数必须与实际编码函数的替换表**完全镜像**，否则判定可编码、编码时却被替换（两头不一致）；降级判定按字符计数（>60% 非可编码才整行转图）。锚：a5d675f00、f810f0047。

**打印输出是 1-bit：二值化吃色吃浅灰**——彩色图取 R 通道 → 红 R=255 变白 = 无墨（红色元素整个消失）、绿蓝变黑块；阈值 127 二值化下 #333 灰字笔画边缘被吞；58mm 图层宽超 384dot 丢末列。收口：文字色一律纯黑、彩色素材强制灰度化或禁上、58mm 图层 370px（输出 368=46×8 列对齐）。锚：827e1b01a、42fdc894d；doc/printer_image_printing_knowledge.md §3.2。

**截图打印链路 DPI / scale 类坑**——裸 `MemoryImage(bytes)` 把物理像素当逻辑像素（Windows 2K 屏同一 logo 比 Android 小 ~28%）；样式裸像素数字逃过 `.w` 适配即错位；SDK 布局用 `image.width/_scale`，ImageProvider.scale 缺失 = DPI 错位。修法：scale 传 pixelRatio 倒数（现行实现变量化传入）、裸像素一律 `.w`、scaleDown 只缩不放（放大必经插值+阈值二值化断线）、超纸宽按满宽拍板并令旧缓存 key 失效；机制级守护测试在位。锚：e8834d496、c55536e0a、5d279115f。

**多列排版手段必须按打印引擎分流，禁止全链路统一**——蓝牙链路仅文字只能拼空格；原生 multiColumn 机型拼空格反而列重叠（字符宽度模型不同）；ESC/POS 没有可靠「列」原语，排版 = 每固件独立实现（内置机商米 / 一敏 / 美团各不同）。vendored esc_pos_utils 的 collection 版本要钉（^1.18.0——SDK 锁定包，放宽须带兼容注释）。锚：61afe68e8、9083576b9；doc/hybrid_multicol_image_row_wrap_design.md。

**字形缺失（维语 / 阿拉伯语 / 泰语等设备无法渲染的 Unicode）用文字渲染为图兜底**（与坑卡「系统字体回退不可信」联动）。锚：aaa9995fd（ParagraphBuilder 文字转图渲染器）。

## 内置打印机（一体机：商米 / 一敏 / 美团 / 联迪类）

**特殊符号致单据截断**——`·`（U+00B7 间隔号）在内置打印 SDK 文本渲染引发截断（`•` U+2022 项目符号已处理 ≠ `·` 已处理）；替换表按「实测打挂」清单维护（·、•、€ 等），别按 Unicode 区间推理。锚：62d364b53。

**熄屏亮屏后打印机服务休眠**——printBind=true 缓存「已绑定」，打印服务进程熄屏被回收后状态失效（亮屏后再也不打，重启 App 恢复）；每次打印前实时 `getPrinterStatus() != NORMAL` 即强制重绑——与 USB「连接态不可缓存」同构家族。锚：66a556e1a。

**AIDL 服务绑定链 × 副屏开启**——商米 T1 开副屏后 openDrawer 静默 false：bindService 回调未到达 / 到达即 NPE（确切机制未查明，如实标注）；修法 = 调用前显式 init + bind/connect/openDrawer/drawerStatus 全链路日志兜底。锚：32bb147da（与 `iot-devices.md` 钱箱节互链）。副屏开启改变服务/进程生命周期同族坑另见 `iot-devices.md` 副屏节「exit 先关副屏窗口」卡；支付外设屏类设备开钱箱走系统广播通道（非 AIDL 非 RJ11），见 `iot-devices.md` 副屏节 ef60 卡。

## 标签打印机（TSPL）

**关端口延迟须按指令体系区分**——TSPL 固件消化 `PRINT m,n` 后走纸 / 定位比 ESC/POS 即时执行慢，写完固定短延迟即关 USB 口会丢末标签（历史修法：TSPL 800ms / ESC/POS 600ms 分治；现行实现已重构为重试退避 [500,700,900]ms——机制沉淀不变：标签机固件是「命令缓冲执行制」，端口关闭时机不能沿用票据机经验值）。锚：1a453167c、a8c5e52a6。
