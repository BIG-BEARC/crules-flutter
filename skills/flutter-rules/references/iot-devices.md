# IoT / 外设通信（收银硬件接入）

> 触发场景：外设通用铁律、钱箱、副屏、语音播报、KDS 接入 / 排障前 Read 本文件；打印、秤·客显、扫码三域已拆分独立文件（见下方文件地图）。
> 来源：backend 角色卡「设备通信铁律」升格（S14 处置，2026-09-08）+ saas-cashier（日活 7w 餐饮 POS）8 类设备实证。批1（打印机 / 扫码枪 / 扫码盒 / 钱箱）、批2（电子秤 / 串口 / 副屏）、批3（客显 / 语音播报）2026-09-24 全量沉淀；同日三域拆分（打印 / 秤·客显 / 扫码独立成文件，本文件枢纽化）。
> 归属：硬件协议 / 设备行为级坑（含型号怪癖——**型号是主检索键**）按设备域住四文件；框架级坑（OS / SDK / 依赖交叉，如 Windows IME 吞扫码枪字符）住 `references/platform-pitfalls.md`，本文件只留指针；网络层消息通道（MQTT）住 `references/network-comms.md`。
> 锚口径：commit 哈希为 saas-cashier 私有仓锚，按其仓内口径视作**信任声明**；`doc/…` 路径为其仓文档（可复核锚优先）。全卡核验 2026-09-24。
> 升格触发：多轮自持的 IoT 调试任务（协议调试 + 原生通道一体）实证后，评估独立 `iot` agent——素材即本域四文件。

## 通用铁律（自 backend 角色卡迁入，原文全量）

- 写入与读取要有应答确认机制，不要「发了就当成功」
- 分帧 / MTU 安全值要保守，不踩协议边界
- 先订阅再写入，否则通知丢失
- 不要在长生命周期 stream 上用一次性消费操作（如 `firstWhere`）——长流持续监听，短流才一次性
- 重连必须 dispose 旧上下文创建新的，不复用旧订阅
- 延迟类异步必须有可取消句柄——`Future.delayed` 不可取消，页面销毁后照样执行（孤儿回调 / 句柄泄漏）；用 `Timer?` 字段持句柄、dispose 中 `cancel()`（实证：秤弹窗 EventBus 延迟重连踩此，05cb54b66）
- 协议文档不可全信，**以实际设备字节日志为准**
- 长操作要有超时和断连处理，不阻塞事件循环

## 外设域文件地图（2026-09-24 三域拆分）

| 域 | 文件 | 收编内容 |
|---|---|---|
| 打印 | `references/printer.md` | 蓝牙（BLE / SPP）/ USB / 网口链路卡 + 打印专项（跨链路：ESC-POS / 编码 / 图像 / 排版）+ 一体机内置 + 标签 TSPL |
| 秤·客显 | `references/scale.md` | 串口 RS232 公共底座 + 电子秤（含 USB 秤）+ 数字客显（与秤平行双实现、互斥同口，并为一文件） |
| 扫码 | `references/scanner.md` | USB HID 键盘流 + 盲扫与业务面 |
| 本文件 | `iot-devices.md` | 通用铁律 / 钱箱 / 副屏 / 语音播报 / KDS 指针 / 平台前置门 |

（Android 14+（targetSdk 34）上 USB 打印机 / 双秤插件会**先**炸于广播注册——`registerReceiver` 二参重载抛 IllegalArgumentException、filter 漏注册 DETACHED action 使拔出检测成死代码；OS 级主卡在 platform-pitfalls.md Android 14 节（锚 4ee867142），printer.md / scale.md 的设备卡在 14 设备上须先过该门才谈得上连接逻辑。）

## 钱箱（RJ11 经打印机指令触发 / 一体机内置通道）

**开钱箱前连接结果必检查，失败裸发指令闪退**——connect 失败（设备离线 / 占用）后仍调 drawer()，对无效句柄操作崩到 native；`connect == success` 才发 kick + close（闸门现行在打印管理器层，非早期 helper 文件）；打印机启用状态判定用 enable 枚举、别用 status 字符串语义。锚：0e4cd1da3、6b7c77fd7。

**指令「发了但没响」：写后关闭生命周期错位**——`drawer(); close();` 序列中 Dart 层 close 抢先释放，kick 指令未真正到达设备；修法 = 取纯指令字节（drawerCmd）经 writeBytes 直写、由插件层统一收尾（插件层 writeBytes 自动关闭连接，Dart 不再手动 disconnect）；顺带：vendorId / productId 可空不可强解包。锚：5c8944369。

**开钱箱广播给非当前设备**——配置列表里的历史设备 ≠ 物理在位设备；发指令前须本地 USB 枚举比对（Windows 按 printName / Android 按 vendorId+productId），仅当前在连的打印机才发。锚：3c059a47a、1cf37aedc。

**连接建立 ≠ 设备就绪：首包字节丢失**——connect 成功后立即写首包被固件吞（钱箱 kick 通常就是唯一一包，丢头 = 完全失效，偶发不开 / 时好时坏）；连接后 delay 200ms 再写、写完 delay 200ms 释放；插件层首包前再加就绪延时（历史 150ms、现行 Android 侧 100ms——值随版本演化，机制不变）。锚：cd88b2717。

**一体机内置通道（AIDL）开钱箱失效**——见 `printer.md`「内置打印机」节商米 T1 卡，锚 32bb147da。

**触发条件求值层：整型解析当通用数值解析**——开班备用金「20.5」这类小数 `toInt()` 解析为 null → 金额>0 条件不成立、钱箱不弹；金额判定用 toDouble。锚：f10af0642。

## 多屏类

### 副屏

Flutter 多 window（`View` / Display API）或平台通道投屏；主副屏生命周期与分辨率差异。副屏三条链路（Android Presentation 双引擎 / Windows desktop_multi_window / ef60 支付外设屏）。数字客显（串口 COM 链路）已并入 `references/scale.md`（与秤平行双实现、互斥同口，并为一文件）。

**副屏是第二 FlutterEngine：插件不自动注册、初始化不裸奔**——子引擎上 GeneratedPluginRegistrant 不执行，调任何插件 API 必 MissingPluginException（实测案例：30s 轮询类调用刷屏 203 条/100min）。本项目终态选「不注册任何三方插件」路线（registerThirdPlugins 整体注释），副屏侧代码禁调未注册插件、轮询首错即停；确需插件走白名单手动注册。配套两条：① 子引擎插件字段勿用 lateinit——detach 后访问必 UninitializedPropertyAccessException，改可空 + `?.`，引擎初始化链（FlutterEngine 构造 + executeDartEntrypoint）整段 try/catch；② 副屏入口不做主屏全局初始化（「某些初始化在副屏环境下可能失败导致闪退」——注释原文）。与秤 mainLooper 卡（`references/scale.md`）同族：回调/引用生命周期对齐问题在副屏以「引擎」为界。锚：8a912208b、d0abdfd8e。

**Windows 副屏窗口销毁后主屏仍 invokeMethod → PlatformException(target window not found)**——windowId 窗口关闭后失效，只判 `window == null` 不够，须 `window == null || windowId < 0` 早退 + try/catch + 异常落日志；配套：config 下发前查 subScreenType==close 早退、副屏收到新 config 须重置页面状态防残留。锚：8f8b37c53、079686f38、99d488af5。

**Windows 开副屏时 exit 前必须先关副屏窗口，否则进程杀不掉**——副屏子窗口（独立引擎）未先销毁，`exit(0)` 时窗口/引擎句柄悬挂、界面关了进程残留；`window?.close()` 是异步操作，关窗后须延时（500ms）再退（Android 走 SystemNavigator.pop）。八笔同日 cherry-pick 变体收敛一卡。锚：c769d304d、1f0b0446f、929657136。

**多窗口入口判定必须校验 args 协议魔数，不能只看参数个数**——exe 被更新器/快捷方式带参二次拉起时 `args.length > 1` 误判为子窗口进程，主界面不出；desktop_multi_window 协议 = 新进程 + `args[0]=='multi_window'` + windowId + json。Android 侧入口判定原语不同（路由名判定），两平台不可混用。锚：0c55f780e。

**主副屏状态不同步是引擎隔离的必然：语言/货币符号须显式推送**——副屏独立引擎，主屏 updateLocale 只影响主引擎；货币符号不同步是发布日志级用户可见 bug。终态机制：每次切页事件**捎带** languageCode/countryCode/currencySymbol（不依赖一次性同步）+ null→"" 判空加固（`Locale(null,…)` 崩溃风险）。教训：跨引擎状态没有共享内存幻觉。锚：23ece0169、53c917787、927dd6778、eb42afc90。

**跨屏数据传输必须全链 toJson——嵌套实体未序列化 + 键名错写双杀**——实体对象直接塞 map 跨 MethodChannel 静默丢数据（编译期无感知）；同一处还键名错写（activity 写在 coupon 键下）。纪律：跨屏/跨 channel 只传 JSON 原语，toJson 覆盖全部嵌套字段且键名与字段对齐；跨屏专用 DTO 集中建。锚：00c486752、dc9f32197。

**ef60 类支付外设副屏：屏显与支付交易共用 ECR doTransaction 通道**——排障时勿把屏显流水当支付交易误读（transType 靠约定区分）；金额字段协议要求 **12 位定长字符串**（不足补位）；功能开关是三重门（平台 + 渠道 + 用户设置），排查先逐门确认；SDK 连接态双标志防重入、onConnectError 后须完整重置再 doInit；此类设备开钱箱走**系统广播**（`android.intent.action.CASHBOX`）——与打印机 RJ11 kick 完全不同通道。注意：仓内曾硬编码内网测试 IP 残留（已泛称化，接入时自查）。锚：dc9f32197、2adfa95b1、d2b20c1d8、8db736b8c。

（Android 14 副屏窗口类型 / 广播注册族住 platform-pitfalls.md——targetSdk 34 起副屏与 USB 外设先炸于 OS 层，再谈本节设备坑。）

## 语音播报（收银语音 / 叫号）

收银语音播报 = **预录 mp3 资产**（zh / zh-hk 双语种目录）+ **双引擎**（win10+ / Android / iOS 走 just_audio；win7/8/未知 Windows 走 minisound FFI，或 SP 手动开关切入）+ 单例任务队列（dealing 门 + 完成回调）+ MQTT 推送触发。本仓无 TTS 路线（全仓零命中）、云播报盒 / 收款云喇叭零素材（如实不预置）。网络侧坑（QoS / 推送到达 / 重连订阅）已独立沉淀至 `network-comms.md`，见节尾指针。

**播报触发源生命周期绑页面 = 多实例重复播 / 离页退订无声**——外卖列表逻辑多处 binding 各自注册 MQTT 消息监听 → 一条推送播 N 遍；`onClose` 退订 topic → 离开页面即无声。终态：全局单例 `Get.put(permanent: true)` 注册、删页面注册点与退订。教训：全局型触发源（播报 / 轮询 / 心跳）不随页面生死，注册一次、不退订。锚：10ca98c2e、a547410d5。

**音频焦点被抢占 → 播报队列停摆**——just_audio 被其他音频（提示音等）打断后 `playing=false && processingState=ready`，任务完成回调永不到来，`dealing` 门卡 true，后续所有播报哑。修法 = playerStateStream 监听该状态自动续播 + 每个播报入口先 `restartLoop()` 重放队头任务（新任务强抢重放被抢占队列）。锚：4e12202a7。

**Windows 版本 → 引擎路线九笔摇摆（2024-01 ~ 2025-06）**——win7 上 just_audio（系统媒体栈）闪退 / 无声 → 初始化 try-catch 止血 → 整体屏蔽 return → 版本门禁静默跳过 → minisound（miniaudio FFI）兜底支持 win7 → 「win10 也走 win7 流程」4 天后一行 diff 翻回 just_audio → 全量压 minisound → 回退版本门禁 + SP 手动开关（异常机型用户自切）。教训：引擎选型判定靠 osVersion **字符串包含匹配**，一行 diff 即全量改线上路线；排障先查开关与版本判定分档。锚：e828deabd、fef932d57、f7867f249、93939fe13、e3b0fa003、c362e295f、cd6ea0d3e、bd96894f2、59cace9f2。

**语音包白名单多份维护漂移 → 静默不播（本域头号坑）**——`checkVoiceBag` 要求播报序列全在白名单内否则**静默 return**；白名单曾有 2-3 份拷贝（主引擎 / win7 引擎各自清单），新增播报类型只改一份 → 部分平台不播、无报错无日志。修法 = 提取共享常量单一来源（但提取当日仍漏 3 行、同日补齐）。**现行缺陷**：京东出餐完成播报是哑弹——文案→key 映射在（「京东上报出餐完成」→ wm_jd_chucan）、白名单与资产均无此 mp3、触发分支在但前缀分派未接：上膛状态，谁接通谁踩；且校验失败日志曾被加后随重构消失 = 重新纯静默。纪律：新增播报类型 = 资产 + 清单 + 文案映射 + 前缀分派**四处同步**，校验失败必须留日志。锚：d394162d7、45eed8582、cb51138cc。

**双语种资产漂移：校验只对默认语种清单**——播放路径按渠道选 zh-hk 目录，白名单校验却只查 zh 清单；zh-hk 缺 16 个资产（取消 / 退款 / 出餐 / 付款码类），特定渠道触发即运行时找不到资产 → 异常任务丢弃（**现行缺陷**，暴露面随渠道业务开通而变）。纪律：多语种白名单逐语种成对维护，校验与播放**同源**（校哪个目录用哪个清单）。锚：d33a63072。

**金额→中文语音读法：跨级缺零 / 高位截断 / 无守卫**——旧算法「100002」读漏零、千万位以上直接截断、无入参守卫；重写为万级 / 个级分段（补零衔接）+ 范围守卫（越界记日志拒绝播报）。金额读法是对账敏感面：改动必须带跨级零、边界值用例。锚：ac878f9cd、ed65f8b22、42aa6f9a4、7178aa9b2。

**设置开关「显示值 ≠ 生效值」两张皮**——两笔实证：① 初始化 `defValue: true` 而生效侧按 false 处理，界面画开实际关；② 控件绑错变量（优惠付款码开关界面实际读写订单播报开关的值）。开关类界面：初始化默认值、控件绑定变量、生效侧读取三处逐一对账。锚：c86a75a53、aab31168b。

**win7 引擎播放失败不回调 → 队列永久卡死（现行缺陷，无事故锚）**——win7 侧 `_voicePlay` 的 catch **只记日志不调完成回调**，对照 just_audio 侧 catch 有「丢掉当前失败的任务」（`taskFinishBack(true)`）；叠加队列两处（callback==null 早退 / loop 自身 catch）均不复位 dealing 门 → win7 机器一次播放失败后所有播报静默到重启。加重项：taskId 随机生成去重永不命中；播完靠 `Future.delayed(sound.duration)` 计时、无完成回调语义。修法方向 = 对齐 just_audio 侧 catch 补回调。接入 win7 播报前必查此点（锚：现行代码，接入前自查）。

（网络域指针：takeout 主题推送丢失 → 自动接单无声——QoS 升 atLeastOnce 后仍丢 = 下行推送无对账，已沉淀至 `network-comms.md`（QoS 双轨卡）；叫号 TV 经 MQTT callNumberTopic + 大屏 socket 下发，收银侧触发与开关落本节、送达与跨店串台见 `network-comms.md`——设备侧另见「独立 App 类」KDS 节。）

## 独立 App 类（指针节）

### KDS / 叫号大屏

另一端是**独立 app**（另一台设备），走网络同步协议（WebSocket / 轮询）——归 backend 网络域，不属本机设备通信；设备侧坑（大屏分辨率 / 常亮 / 开机自启）住项目 memory 坑库。收银侧叫号触发与语音开关见「语音播报」节（MQTT callNumberTopic + voiceCallFlag 字段控制 TV 端是否出声）。
