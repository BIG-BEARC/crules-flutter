# crules-flutter CHANGELOG

## 1.0.27 · 评审卡「缺包即停」自护条款——事实切片包升派单前置 + test-self 防删改断言

> 依据链：消费工程复盘（2026-09-20）——无 Bash 的 plan-reviewer 被派 13k 行全读对比（基准 5123 行 + 待审 7810 行），52 分钟未完。根因：事实切片包契约（进阶/Agent编排.md「评审包契约化」节）**事发前已写明**，但只是推荐形态、无任何执行点——「有法无执行」（F11 同族）。修法经需求方三轮裁决终选「卡片自护」：角色卡即子代理的系统提示词、必进上下文，是全仓唯一送达有保证的位置；「评审代理会遵守角色卡」与「只报不改」是同一信任层级，不加新墙、只把现有的墙加高一行。备选的 hooks 派单闸（派单时机械校验、缺令牌即拦）留作后备，触发条件＝首次观测到代理无视条款——本批定义的令牌语法即将来闸要校验的同一契约，升级零浪费。

- **agents/plan-reviewer.md + agents/reviewer.md 各 +1 条「缺包即停（自护条款）」**：派发 prompt 无 `【切片包】`（被审 diff / 基准节选 / 已核实 file:line 清单）且无 `【切片包-免】` 豁免时，**第一步输出即退回**请补齐，禁以全文 Read 兜底开工（评审角色无 Bash，diff 类取材只能来自切片包）；到包后核 file:line 用定点窗口，禁全文 Read 作背景
- **进阶/Agent编排.md「评审包契约化」升格**：推荐形态 → **派单前置条件**，定义令牌语法 `【切片包】` / `【切片包-免】`（机械可查）；执行点双侧——代理侧卡内自护 + 派单侧主控自检三件齐备
- **test-self +1 断言（28→29）**：防删改检查——两卡「缺包即停」/「【切片包】」/「【切片包-免】」三串 + Agent编排「【切片包-免】」/「派单前置条件」在位，被无声删改时 test-self 变红
- **验证**：test-self 29/0 实跑绿（本机 Windows；断言先红后绿——落文前漂移清单 8 条精确命中、三文件落文后转绿）；常驻面预算闸零变化（app 16463 / plugin 15162，本批不触常驻面）
- **观测带数**：常驻基线——零常驻面变化（agents 卡与进阶篇不入常驻 token 面）；distill 四数——仍无数（止损线 2026-12-31）
- 双 json 1.0.27 + README 横幅同步

## 1.0.26 · 裁决必附具体内容——红线新条款 + 交付汇报末尾裁决区 + 禁自创黑话半句

> 依据链：需求方反馈（2026-09-20）——裁决请求常不附条目内容，需求方要往上翻很久之前的消息才能找到要裁决的是什么。盘点全项目五处裁决点：`AskUserQuestion` 选项卡（多方案 / distill 闸）本来就显示在提问处；review 逐条裁决（§五）、校验层列单裁决（收尾三档）、更简方案推回（§三）是普通文字回复，此前没有条款要求把内容写全。

- **app + plugin 双模板 §一 协作红线各 +1 条「裁决必附具体内容」**（「多方案走选项卡」之后）：能进选项卡的裁决一律走 `AskUserQuestion`，条目全文写进问题和选项说明，一次放不下的分批呈现；进不了选项卡的（条目多 / 需要开放讨论的）就在回复里把条目原文列全（编号 + 位置 + 原文 + 建议 + 上下文）；禁止只写「请裁决」「等确认」却不附内容，或让需求方翻很久之前的消息。**诚实边界**：这条规定只能靠 AI 自己执行——请求裁决发生在普通回复文字里，没有程序能在技术上强制检查；放进 §一 红线是为了让它常驻上下文、优先级最高
- **双模板 §五 交付汇报定义补「裁决区」**：任务收尾要裁决的事固定放在交付汇报末尾——有待裁决条目时逐条列出全文（编号 + 位置 + 原文 + 建议），没有就写明「无待裁决项」；极简任务的一行汇报不需要。两条配套：任务中途的裁决走选项卡（问题直接显示在对话里）；任务收尾的裁决看报告末尾（位置固定，有没有照做一眼能查）
- **双模板 §一「必须简洁直接」补半句**：不自创黑话新词——确需新概念先用大白话解释，一切以需求方好懂为准（同日需求方第二条反馈，随批落实；本批文档已同步自查，首轮条目里自造的词已全部换成平常话）
- **观测带数**：常驻基线——app 16463/18000、plugin 15162/16500 字符（预算闸内）；distill 四数——仍无数（止损线 2026-12-31）
- **验证**：test-self 28/0 四轮实跑绿（本机 Windows；§一 加条后、§五 加裁决区后、措辞平实化后、禁黑话半句后各一轮；常驻面预算闸 + 双模板孪生结构闸直接覆盖本改动）；grep 两模板「裁决必附具体内容」「裁决区」「不自创黑话新词」各 1 处；工作区同期的范围外变更（docs/方案-2026-09-14-review结果校验机制.md，P1 试点采证）已由另一会话以纯 docs 批先行提交（cd9052a，未占版本号，无撞号），不入本批
- 双 json 1.0.26 + README 横幅同步

## 1.0.25 · 轮次化删档——裁决单-09-15 全终态删除（F2 弧闭合）+ 撞号补正两处

> 依据链：1.0.23 预录条件「触发面金丝雀绿 → 裁决单全终态、随下轮轮次化可删（docs 6→5）」已满足——1.0.24 实测交付金丝雀绿（PowerShell 工具真实调用 + `git push --force` 字面量 → ps1 闸 deny、reason 全文回传，销 1.0.21 开口①）。F2 弧全程：1.0.17 落地 → 1.0.21 判据面/契约面实机收口 → 1.0.22 闸自失效兜底 → 1.0.23 触发面裁「再验」→ 1.0.24 金丝雀绿。本批即 1.0.23 落地方预报的删档轮（版本通告已发）。

- **删档**：docs/裁决单-2026-09-15-1.0.10全面外审与四批处置.md 删除（docs 6→5，余 09-14 五件套）。**死链声明**：CHANGELOG 既往 7 处该档 markdown 链接悬空属轮次化预期口径（1.0.19/1.0.20 同款）；可回溯性 = git 历史（v1.0.24 及更早 tag 树含该档）。已核零扰动面：scripts/ 与 yml 全仓零引用、test-self 无路径引用、CI 链接检查步只扫 skills/ 下 http URL（本地死链不红）
- **随附口径（不阻删档）**：1.0.24 诚实边界④——PowerShell 匹配器字符串形式的端到端复验（待 Windows 缓存装 1.0.24+ 后）——由 CHANGELOG 续 track；裁决单终态判据按 1.0.23 预录口径（金丝雀绿）已足
- **撞号补正（1.0.23/1.0.24 撞号改号遗留两处）**：①本文件 1.0.24 条目原压在 1.0.23 之下，恢复最新在前惯例；②README 环境节触发面句误引「1.0.23」→ 实落 1.0.24；连带 README 尾注「裁决沿革见裁决单 §7/§8」改指 CHANGELOG（档已删）
- **验证**：test-self 27 断言实跑绿（本机 mac；ps1 fixture 断言无 PowerShell 时 SKIP 不计，Windows 侧基线 28——平台差异非本批扰动）；grep 复核——条目顺序 25→24→23→22→21、README 无 1.0.23 误引残留、本文件该档链接计数 7 与声明一致（另本条目内 1 处为纯文本提及、非链接）、双 json 1.0.25
- **观测带数**：常驻基线——零常驻面变化（docs 不入分发面）；distill 四数——仍无数（止损线 2026-12-31）
- 双 json 1.0.25 + README 横幅同步

## 1.0.24 · ps1 闸补启动失败重试（PowerShell 匹配器 fail-open 缺口收口）+ py 驱动判定进程内化（165 spawn → 7）

> 依据链：1.0.22 后对本机 0xc0000142 弹窗的根治推演（2026-09-18）。实机事实链（64 位枚举 + Sysnative 复核，防 32 位视角假证据）：联软 UniAccess 的 AppInit_DLLs 注入**每个**新进程——64 位 python / 32 位 pwsh / powershell.exe / node / git bash / uv 蹦床**实测全中**（Claude Code 两个常驻 bash 未被注入，例外未解）；一次 py hook 调用 = bash + 蹦床 + 真解释器 **3 个注入进程**（`||` 兜底触发再 +2）。无管理员 → 注入不可关（原设计的秒级 A/B 亦无权限执行）。推演产出两件：**其一**（安全面）——PowerShell 匹配器**无重试**：powershell.exe 启动失败（本机实测 ≈0.6%/进程）→ hook 非零退出 → 官方语义 non-blocking error = **该次调用闸被静默绕过**（弹窗只是症状，绕过才是缺口）；**其二**（弹窗面）——py 测试驱动是全仓唯一密集 spawn 源（165 次/遍），判定逻辑是纯函数，没必要每例进程隔离。附带销账：1.0.21 诚实边界 ②「旧 npm CLI 2.1.81 剥 `args` → ps1 闸退化 fail-open」——exec form 改字符串形式后无 args 可剥，该失效模式一并消失；同开口 ①「双 matcher 端到端命中性」实机闭环（见验证）。**版本撞号处置**：本批开发期间（2026-09-17 18:26）另一会话已以纯 docs 批占用 1.0.23（裁决单状态戳）且 tag 已公开推送——本批代码改走 1.0.24，**不改写已推 tag**（改写公开历史正是 deny-list 要拦的破坏形态，1.0.18「tag 指向修复前树」教训的同族预防）；1.0.23 裁决「触发面再验（金丝雀）」的待办恰由本批实测交付（见验证）。

- **hooks.json（PowerShell 匹配器）**：exec form（command+args）→ 字符串形式 `powershell.exe … || powershell.exe …`（与 py 匹配器同形）。语义分岔（bash 单管道共享模型，三路实测）：**启动失败**（进程没起来、stdin 未读）→ 重试拿到完整输入、判定照常正确——弹窗只是烦，闸是对的；**读后失败**（首命令读完 stdin 再非零退出）→ 重试空 stdin → 落 1.0.22 `Invoke-DenyListSelfFailure` 判 **ask**（非 fail-open）。**代价与对冲（三笔）**：①放弃官方「Prefer exec form」的免 shell 注入面——`${CLAUDE_PLUGIN_ROOT}` 加引号覆盖空格/反斜杠（py 匹配器同款写法，1.0.0 起实证）；②ps1 匹配器从此与 py 匹配器**共享**「hook 执行壳须支持 `||`」假设——Git Bash / cmd 成立；若宿主以 **Windows PowerShell 5.1** 为执行壳则 `||` 即语法错误，但 py 侧 1.0.0 起同一假设未闻失效，属**归队既有假设而非新增**；③换得旧 CLI args 剥除失效模式消失（见依据链）。
- **test_deny_list.py（判定主体进程内化）**：**闸本体 deny-list.py 零改动**（安全组件不为测试便利动主流程——R3「需重构主流程，收益/风险比待裁」的原判维持），exec 闸源码 + 伪造三流（`_FakeStream` 接住 `_hook_utf8_streams` 的 reconfigure）+ 拦 `sys.exit`/`os._exit`（`gate_self_failure` 的 `os._exit` 拦成 SystemExit）全部承载在测试侧。165 spawn → **7**（契约锁 4 + 判定锚点 3）——按 0.6%/进程，单遍全量验证的「必有一弹」（≈63%）降到 ≈4%。
- **保真锚（防 harness 自信，三道）**：①锚点 3 例（拦/放/ask 各一）**两路并跑同判**才过；②`--diff` 全量 164 例两路并跑**比全文**——不只比 verdict：空 stdin 走 `os._exit` 拦截是 harness 最易失真处，显式覆盖（实测 0 不同判）；③汇总行常驻「判定路径：进程内 N / 子进程 spawn M」——`decision()` 若被改回 spawn，弹窗面悄悄回来而汇总行无变化 = 无痕回归，故必须可见。**诚实边界**：进程内只等价**判定语义**，不等价**进程契约**（退出码/真管道/空 stdin/`||` 链/UTF-8 流重配）——后者由 7 个真子进程钉住；改动 harness 或闸本体后须重跑一次 `--diff`（一次性全量 spawn 代价）。
- **验证**（实机）：hooks 命令串三路 bash 实测——A 正常 payload → **deny**；B `false || 闸`（首命令未读 stdin）→ 重试 → **deny**；C 闸以空 stdin 运行 → **ask**（非 fail-open）。py 驱动默认路径 `70 拦 + 30 放 + 11 warn + 单调性 50 变异 + 契约锁 4, 失败 0（判定路径：进程内 164 / 子进程 spawn 7）`，计数与 1.0.22 **逐字相同**；`--diff` 164 例 0 不同判（其间 1 次真实启动失败被重试计数捕获 ≈0.6%，与历史观测同量级——分布证据非孤例）。**触发面闭环（销 1.0.21 开口①，交付 1.0.23 裁决的「再验」）**：PowerShell 工具真实调用 + 破坏字面量（`git push --force` 赋值串）→ ps1 闸 deny，reason 全文回传——1.0.22 缓存 exec form 下实测；本版字符串形式换轨后的复验见诚实边界④。
- **弹窗面处置（机侧，不入包）**：常驻关框器 `%LOCALAPPDATA%\crules-diag\dialog-closer.ps1`（免提权、单实例锁；**只关「类 #32770 且正文含 0xc0000142」的框，不认识只记不关**——两条性质均实测：命中 4s 内自动关 + 记日志，普通框 4s 不动只记）；自启入口 vbs 留同目录由需求方自装（装 = 拷入 shell:startup）。**关框不掩盖安全缺口的前提即本版 ps1 重试**：py 路径弹窗的那次 `||` 兜底已正确判定，ps1 路径本版起同款。同目录另留已自检通过的弹窗追踪器（trace-python.ps1，抓标题/正文/进程快照）与进程内模块枚举器（modcheck.py）。
- **诚实边界（本版仍开口）**：①真 0xc0000142 框对 WM_CLOSE 的响应属**机制正确、未实测**（故障无法按需复现；MessageBox 同形框实测秒关）；②「PS 5.1 作为 hook 执行壳」的 `||` 失效面未实测（本机 Git Bash；同假设 py 侧 1.0.0 起未闻失效）；③联软注入 → 0xc0000142 的因果归因仍是**强嫌疑非铁证**（机制自洽 + 注入实证 + 失败率分布吻合，但无 A/B 对照——无管理员权限）；④~~字符串形式的端到端触发在**本版缓存安装后**才算换轨（本会话实测基于 1.0.22 缓存的 exec form）~~——**2026-09-18 已清**：插件更新（1.0.22→1.0.24）并会话重启后金丝雀复验通过（PowerShell 工具真实调用 + 破坏字面量 → deny）；1.0.24 缓存内 PowerShell 匹配器**仅存字符串形式**（exec form 已不存在，verify-cache 特征串在位），故该次拦截即字符串形式端到端生效之证。
- **观测带数**：常驻基线——零常驻面变化（hooks.json 改既有 hook 的命令形态、test 驱动不入常驻 token 面）；distill 四数——仍无数（止损线 2026-12-31）
- 双 json 1.0.24 + README 横幅同步（含 1.0.21 两开口销账）

## 1.0.23 · F2 触发面裁决落账——「再验」，裁决单状态戳刷新（D2 缺口补）

> 依据链：需求方裁决（2026-09-17）——F2 最后一项触发面（PowerShell 工具真会话里 ps1 hook 被触发并拦截）**不列接受边界、裁「再验」**：Windows 机设 `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` → 重开会话 → `/hooks` 确认 PowerShell 工具+hook 在列 → 金丝雀命令复验。判据面/契约面已实机全绿（1.0.21/1.0.22），此为最后一类证据。背景：1.0.21/1.0.22 落地后裁决单状态戳仍停「Windows 实机验证进行中」（D2 纪律缺口——裁决索引即状态戳，须反映最新终态），本批代刷。

- **[裁决单-2026-09-15](docs/裁决单-2026-09-15-1.0.10全面外审与四批处置.md) 状态戳**：F2 段刷为「判据面/契约面已完成（1.0.21/1.0.22）；仅余触发面，需求方已裁再验（2026-09-17）」——验毕该单全部终态，随下轮轮次化可删（docs 6→5，余 09-14 五件套）
- **README 环境节零改动**：触发面残余表述 1.0.21 已如实在位（「仍开口：ps1 分支的真机触发面未闭环」），本批仅裁决侧落账
- **验证**：test-self 28 断言实跑绿（纯 docs 面，零代码扰动）
- **观测带数**：常驻基线——零常驻面变化；distill 四数——仍无数（止损线 2026-12-31）
- 双 json 1.0.23 + README 横幅同步

## 1.0.22 · 闸自身失效兜底——空 stdin / 未预期异常改判 ask（`||` 兜底链静默 fail-open 收口）+ 驱动分辨「启动失败」与「判定失败」

> 依据链：1.0.21 头注 ③ **留裁项的收口**。裁据是官方 hooks 文档（2026-09-17 查证）的退出码语义——**唯一靠退出码就能拦的是 `exit 2`**；`exit 0` 且 stdout 无合法 JSON = **无判定**（走正常权限流，不等于放行）；**`exit 1` 及一切非 0/2 码 = non-blocking error，动作照常执行**（文档自陈：*Without valid JSON on stdout, Claude Code treats exit code 1 as a non-blocking error and proceeds with the action…If your hook is meant to enforce a policy, use `exit 2`*）；**超时的 command hook 亦不拦**。故「未捕获异常」与「兜底吃空 stdin」两条路都汇到**静默 fail-open**，且 PreToolUse 的纯文本 stdout **不进上下文**（只进 debug log）——静默得更彻底。

- **py 侧（deny-list.py）**：新增 `gate_self_failure(reason)` + `sys.excepthook` 接管——**stdin 空（含纯空白）/ 未预期异常 → 改判 `ask`**（不静默放行、不硬锁死，交需求方当场裁夺，与 warn 层同构；`ask` 在自动批准模式下仍强制弹窗）。`os._exit(0)` 绕开默认 traceback 与非阻塞退出码，stdout 显式 flush；JSON 走 `ensure_ascii`（纯 ASCII）→ 任何码页都编得出，**兜底自身不会再因编码二次失败**（P0-A 同族教训：兜底必须比正路更不可能失败）。**F10① 未变**：**非空**但非法 JSON 仍 `exit 0` fail-open（疑为探活/心跳，fail-closed 恐误伤正常流）。
- **ps1 侧（deny-list.ps1）**：同判 `Invoke-DenyListSelfFailure`（空 stdin / 流读失败 / 判据体未捕获异常）；入口段置 `$ErrorActionPreference = 'Stop'`（驱动 `$global:DENYLIST_LIB_ONLY` 短路在该行之前，故点源判定面不受扰动），判据体包 `try/catch`。
- **回归锁**：py 契约锁 4（空 stdin / 纯空白 / 非空非法 JSON / 文案锁）、ps 黑盒探针 ×4 → **×6**（新增空 stdin、纯空白两例，断言 `"permissionDecision":"ask"` + `crules-flutter` 闸标识）。**两条路必须同测**——只锁 ask 会让「把 F10① 也一并收口」的过度修正不被发现。
- **验证**（实机证据，非 CI 推演）：py 驱动 `70 拦 + 30 放 + 11 warn + 单调性 50 变异 + 契约锁 4, 失败 0`；ps 驱动 **Windows PowerShell 5.1 与 pwsh 7 均** `81 拦 + 38 放 + 17 warn + 单调性 24 变异 + 黑盒探针 6, 失败 0（os=win 全跑）`——计数与 1.0.21 **逐字相同**，即入口段改动未扰动判据面。**A/B 负控**（同机同解释器）：py 侧按 hooks.json 兜底链的**单管道共享**模型注入「首解释器读完 stdin 后再抛」→ PRE（HEAD 1.0.21 树）`rc=0` 实得 **allow（无输出 = 静默 fail-open）**，POST（本版）实得 **ask**；ps1 侧空 stdin 直喂 → PRE **空输出** vs POST **ask JSON**（探针 5/6 对 HEAD 即为红，非空锁）。
- **诚实边界（本版仍开口）**：①首解释器被**中途 kill**（超时）→ 管道剩半截 JSON（非空非法）→ 仍落 F10① 放行；②本文件**语法错误** → 解释器根本没跑起来、`excepthook` 未安装 → `exit 1` 放行（`release.sh` 的 py_compile + 夹具步是此路线的发行前闸）；③两解释器皆缺 → `exit 127` 放行（README 声明：终极防线回 Claude Code 原生权限确认）；④宿主**超时**的 hook 按官方口径本就不拦；⑤ps1 只捕获 **terminating** error（非终止错误不进 catch，`ErrorActionPreference='Stop'` 已尽量收紧）
- **验证环境缺陷（非本包缺陷，但直接影响证据可信度，故记录在案）**：本机装**联软 UniAccess** 终端管控 agent，它把 32 位 `Vozokopot.dll` 挂在 `AppInit_DLLs`（64 位 hive 与 WOW6432Node **两处**均 `LoadAppInit_DLLs=1`）→ 每个加载 user32 的新进程启动时都被注入，注入失败即 `STATUS_DLL_INIT_FAILED(0xc0000142)`，Windows 弹**加载器级硬错误框**——**不进 WER、不进事件日志**（故「查日志干净」不能作为「没发生」的证据）。密集 spawn 时偶发，曾表现为 py 驱动**概率性红**（子进程无输出被旧写法判成「非 deny」，与「判错」混成一条无从下手的红）。处置：驱动**分辨**「启动失败」（rc≠0 且 stdout 空）与「判定失败」——前者重试一次，且**重试/仍失败次数一律进汇总行**（不许静默——否则重试就把一次真实的环境故障洗成无痕的绿）；父进程设 `SetErrorMode(SEM_FAILCRITICALERRORS)` 抑制该框（**官方口径：子进程继承父进程 error mode**；故障本身偶发、无法按需复现，故属**机制正确 + 未实测**）。**本项属需求方终端管控面，处置须走 IT，本包不代改**。**实测率（本版发布时捕获）**：`release.sh 1.0.22` 的自动 verify 打出「重试 1 次 / 仍失败 0 次」——即约 165 次 spawn 中 1 次启动失败 ≈ **0.6%**，与本节此前观测到的概率红率同量级（旧写法下这一次就是一条无从下手的红）；重试后全绿，且计数在汇总行可见 = 该分类改造的直接收益
- **观测带数**：常驻基线——零常驻面变化（改动全在 `hooks/`，不入常驻面）；distill 四数——仍无数（止损线 2026-12-31）
- 双 json 1.0.22 + README 横幅同步

## 1.0.21 · Windows 实机验证（用户最终闸）——隐式码页缺陷族 7 处收口 + rm 白名单归一（test-self 22/6 → 28/0）

> 依据链：[裁决单-2026-09-15](docs/裁决单-2026-09-15-1.0.10全面外审与四批处置.md) §7/§8「Windows 实机为用户最终闸」的**实机执行**（2026-09-17，需求方本机 Windows 10 19045 / 系统码页 **cp950 繁中**）——1.0.20 落账时该单仅余此项。**底座事实**：本项目源码消息为**简体中文**，而 Big5 编不出简体字形（请/块/试/节…）——同一份代码在 zh-CN（cp936/GBK）不崩、在 cp950 必崩，故「CI 绿（macOS UTF-8 环境）」长期掩盖此族；「非 UTF-8 码页」须全修，不能只看崩不崩。

- **P0-A 隐式码页缺陷族（7 处，本轮最大发现）**：Python 未显式指定编码（`print` / `open()` / `sys.stdin`）→ 后果按「该码页能否编出消息里的字」**分岔**：①编不出 → `print` 抛 `UnicodeEncodeError`，拦截 JSON **一字未出**即退出；hooks.json 的 `python3 … || python …` 兜底链再把它洗白——首个解释器已读完 stdin，兜底那次拿到空输入 → `json.load` 失败 → `exit 0`，宿主侧与「无命中」不可区分（**实测 exit 0 + stdout 0 字节 = 完全静默 fail-open**，hard gate 整体归零）；②编得出（cp936 对简体消息）→ 不崩，但 stdout 是 **cp936 字节而非 UTF-8**，宿主按 UTF-8 读则 reason 失真（属未爆隐患、非安全态）。**stdin 方向不抛**（Windows 标准流 `errors=surrogateescape`）——坏字节变孤立代理项，属**失真非失败**（ASCII 骨架保留，判定面未见翻转）。落点与修法：hooks ×3（deny-list / stop-reminder / pending-updates）三流钉死 UTF-8（与 deny-list.ps1 入口段 `OpenStandardInput/Output + UTF8Encoding($false)` 同款——ps1 早有此手，py 侧补齐）；`test_deny_list.py` / `test_stop_reminder.py` 驱动两侧钉死（此前 cp950 下驱动自身中文 print 即崩，夹具根本跑不起来）；`scripts/render-blocks.py`（自测孪生闸恒红，与内容同步与否无关）；`scripts/install.sh` 与 `check-imports.sh` 的 `open()` 缺 `encoding`（→ `VER="unknown"` → 戳写 `vunknown` → `v[0-9]` 守卫认不出「本包装工程」→ **`--force/--upgrade` 全走「老项目无戳」分支中止**）；`scripts/release.sh` 读 HEAD 版本（`sys.stdin`）与 bump 段输出
- **rm 白名单归一（deny-list.py）**：根与 token 未**同经 normpath**——原写法拿字面 `"/tmp/"` 比 `os.path.normpath()` 结果，而 Windows 的 normpath 把 `/` 翻成 `\`（`normpath("/tmp/junk")` = `\tmp\junk`）→ 前缀恒不命中 → `/tmp`、`/var/folders` 白名单族 **5 例 both-allow 夹具在 Windows 全数误拦**（macOS 不翻分隔符，故 CI 长期绿）。两侧同经归一后 POSIX 语义逐字不变（`normpath("/tmp")` 仍 `/tmp`），Windows 侧与 ps1 **D-e**「字面 /tmp /var/folders 跨界仍对」的声明对齐（双源对照表 temp 根一项）。**隔离验证**：只差此一处的中间版 diff——仅 8 例白名单族翻转，11 例拦截侧（穿越 / 邻近串 `/tmp2` / `/etc` / `.` / `~` / 盘符路径）逐字未动，**零意外放宽**
- **test_deny_list.ps1 出口编码**：PS 5.1 重定向时 `Write-Output` 走系统 ANSI 码页，且**码页没有的字在写盘前即被替换成 `?`**（实测「测试」→ 字节 `3f 3f`，**不可逆丢失**，事后重新解码救不回）——汇总行与 **FAIL 行**（最需读清的诊断面）在宿主侧既乱码又缺字。改 `OpenStandardOutput + UTF8Encoding($false)` 流式写（deny-list.ps1 既有手法）；**不用** `[Console]::OutputEncoding`（R4：setter 依赖附加控制台，无控制台宿主下抛异常）。注入失败复验：`FAIL 应放未放: git push --force origin main` 完整可读、rc=1 正确传播
- **deny-list.ps1 `$env:` off-by-one（本版首次分发）**：`StartsWith('$env:\')` / `Substring(6)` 与惯用形 `$env:TEMP\build` 不匹配 → `UNRESOLVED` → 过度拦截（**D-e** 白名单自展开失效），2 例夹具红；改 `$env:` / `Substring(5)`。该修复落于 1.0.20 之后、未随任何版本分发，故记入本版
- **验证**（实机证据，非 CI 推演）：`scripts/test-self.sh` **PASS=22/FAIL=6 → PASS=28/FAIL=0（rc=0）**；双驱动夹具全绿——py 侧 `70 拦 + 30 放 + 11 warn + 单调性 50 变异，失败 0`（此前 5 红），ps 侧 Windows PowerShell 5.1 与 pwsh 7 均 `81 拦 + 38 放 + 17 warn + 单调性 24 变异 + 黑盒探针 4，失败 0（os=win 全跑）`；stop-reminder fixture 7/7。**A/B 对照**（PRE = v1.0.20 tag 树 979e2f2 / POST = 本版，同机同解释器，跑 hooks.json 逐字原样命令**含 `||` 兜底链**）：PRE **3/5 例失败且全部形如 exit 0 + stdout 0 字节**，POST 5/5 通过；含原始 UTF-8 非 ASCII 载荷 12 例——PRE 判定错 10/12（全崩 → allow），POST 1/12（该 1 例系探针期望笔误：`/tmp/中文/../Users` 折叠后落在 `/tmp` 内，放行正确）
- **诚实边界（本版仍开口）**：①**双 matcher 端到端命中性未实测**——本会话工具表无 PowerShell 工具，须 `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`（preview）才注册，ps1 分支的「真机触发」链条仍未闭环（判据面/契约面已实机全绿，触发面待启用该开关后复验）；②hooks.json 的 `args`（exec form）在**旧 npm CLI 2.1.81** 被 Zod 剥掉 → 退化为裸 `powershell.exe` → ps1 闸 fail-open（本机扩展版 2.1.274 有效）；③**`||` 兜底链结构性缺陷**留裁——本轮只堵「首个解释器崩」这一触发源，任何原因令其非零退出，兜底即吃空 stdin → `exit 0` 静默放行；可考虑把**空 stdin** 与「非法 JSON」区别对待（宿主总会送 JSON），属 fail-closed 方向、有误伤探活之虞，待裁
- **观测带数**：常驻基线——零常驻面变化（改动全在 hooks/ scripts/，不入常驻面）；distill 四数——仍无数（止损线 2026-12-31）
- 双 json 1.0.21 + README 横幅同步

## 1.0.20 · 裁决落账——评审后优化三批 Q4/Q5 销撤 + 批二/三整体废弃（docs 8→6）

> 依据链：需求方三裁（2026-09-17）——**Q4 销项**：D9 孪生内容等值闸废弃，canonical 生成化（1.0.12）+ D1 结构断言为孪生守护终态，与 1.0.12「构造优先」/ 1.0.15「双保险取消」预裁线一致（装回即翻案）；**Q5 撤项**：performance.md 线上崩溃监控节已超额（双兜底 + saas-cashier 实证 + 符号化/上报纪律），不再等素材；**批二（1.1.0）/批三（1.2.0）整体废弃**——1.0.x 线已用更强形态吸收大半（D6/D7 被 1.0.6「状态戳即索引」实质否决、D9 被 canonical 超越、D13 框架已超额、D11 坑卡 10/10 满配额），旧排期系虚假待办。**未吸收残差从方案解绑**：D8 溯源断言 / D10 golden 金额展示锁 / D12 bundle size·RepaintBoundary 两小节——需要时按 1.0.x 节奏单开小批，不再挂 1.1.0/1.2.0 批号。

- **两篇删除**（轮次化判据终态齐：批一 1.0.2 已落 + 批二/三裁废弃 + Q1-Q6 全裁）：`方案-2026-09-08-评审后优化三批.md` / `评审-plan-评审后优化三批.md`——CHANGELOG 既往依据链（1.0.2/1.0.3）链接悬空属轮次化预期口径（1.0.19 声明同款）；`评审-plan-review结果校验机制.md:47` 对后者的存史引用按 1.0.15「保留并注记」先例不动
- **[裁决单-2026-09-15](docs/裁决单-2026-09-15-1.0.10全面外审与四批处置.md) 待裁清点行**：「评审后优化三批 Q4/Q5」标记已裁销撤（该单仅余 F2 Windows 实机验证一项）
- **验证**：test-self 27 断言实跑绿（删档零断言面扰动，test-self 无此二文件路径引用）
- **观测带数**：常驻基线——零常驻面变化（docs 不入分发面）；distill 四数——仍无数（止损线 2026-12-31）
- 双 json 1.0.20 + README 横幅同步

## 1.0.19 · docs 轮次化——三篇批齐文档删除（孪生 F3 两篇 + 支付方案，11→8）

> 依据链：README 维护节轮次化义务（每次 minor 清点 docs/，已落地且批齐的删、裁决中途保留）。三篇判据——孪生方案（P1 落 1.0.12 / P2·P3 落账 1.0.15，批齐）+ 孪生评审档（状态戳「已闭环」）+ 支付方案（Q1/Q2/Q3 全裁；草稿①②落 1.0.16、草稿③按裁随消费工程走）。协调：flutter-ba 1.0.16-1.0.18 落地后共享面空闲、回执让位（本批 flutter-09 执行），版本无撞号。

- **删 3 篇**：`方案-2026-09-15-孪生同文块生成化.md` / `评审-plan-孪生同文块生成化.md` / `方案-2026-09-09-支付资损域沉淀-防重与核销时序.md`——结论已被代码与 CHANGELOG 吸收，git 可寻回。**历史死链声明**：本文件既往条目（1.0.12/1.0.15/1.0.16 等）「依据链」中指向此三篇的链接自本批起悬空，属轮次化预期口径（沿 1.0.3 审查质量落账方案被删先例），非漂移
- **README 去引用**（删前置——「被分发面引用的 docs 先去引用再删」）：维护节「同文块改动」条尾「见 docs/方案-…」指针删，操作要点（canonical 改源 + render 重生成 + 勿手改围栏区 + 尾随空行语义）正文自含无损；`scripts/render-blocks.py` 头部溯源注释保留（存史引用，1.0.15「保留并注记」先例）
- **保留 8 篇**（清点快照）：裁决单-2026-09-15（仅余 F2 Windows 实机验证进行中——关闭即整单可删）；09-14 五件套（A 案 P1 试点 / P2 制度化、B 案 P2 试点待行）；09-08 方案 + 评审（§9 待需求方裁）
- **验证**：test-self 27 断言实跑绿（删档零断言面扰动——D2 状态戳 grep 为模式扫描非文件级断言，test-self / CI 无 docs 路径引用，grep 实证）
- **观测带数**：常驻基线——零常驻面变化（docs 不入分发面，install.sh 不复制）；distill 四数——仍无数（止损线 2026-12-31）
- 双 json 1.0.19 + README 横幅同步

## 1.0.18 · 批F2 收口小笔——deny-list.ps1 Normalize Replace 重载炸点（本机便携 pwsh 复现 CI 首红）

> 依据链：1.0.17 CI 首跑即红（steps exit 1），本机便携 pwsh 7.4.6（GitHub release tarball 解包即用、不入库）当场复现：`$c.Replace($bt, '')` 被重载解析绑到 `Replace(char,char)`、空串转 char 抛，`$ErrorActionPreference=Stop` 放大为整脚本中止 → 改 `[regex]::Replace([regex]::Escape($bt),'')` 并加注释锁。修复后本机 pwsh 路径复验：ps 驱动全绿 + test-self 28/28；push 后 CI 回绿（徽章 passing）。
> **教训入册**：mac「无 pwsh」验证缺口可自建——brew 本 tap 装不下（cask 名冲突走 linux-only 渠道），GitHub release tarball 30 秒便携得 pwsh；**「CI pwsh 首跑前先本机跑」从被动等红变主动步骤**。1.0.17 验证条已含全程，本笔纯收口（双 json + 横幅 + cache 快照须含修复）。5.1 差异面（R2/R3/BOM）终验仍待用户实机。

## 1.0.17 · 批F2——deny-list PowerShell 原生实现 + Windows 接线 + 夹具单源双驱（Windows 防线落地）

> 依据链：[裁决单-2026-09-15](docs/裁决单-2026-09-15-1.0.10全面外审与四批处置.md) §7/§8 落账（2026-09-16 需求方裁：F2 恢复排期、本人在 Windows 原生开发并**实机验证**——§7「验证手段」之争由实机闸替代，CI pwsh 降为可选加固）。官方事实底座（claude-code-guide 六问查证，code.claude.com/docs/en/hooks·tools-reference·setup）：Windows 无 Git Bash 时注册的是 **PowerShell 工具**，`matcher:"Bash"` 永不触发（= 原防线在 Windows 原生静默归零的根因）；装了则两工具并存、模型可换 shell 绕过 → **两 matcher 双 handler**；exec form（command+args）不经 shell、占位符纯字符串注入（空格/反斜杠安全，官方含路径占位符明确「Prefer exec form」）；PreToolUse deny 含 bypass 全模式生效；JSON 契约平台无关。

- **夹具单源双驱**：`hooks/fixtures/deny-list-cases.json`（138 例 = 迁移 111 + ps 新增 27；schema/lang(both|bash|ps)/os(win)/src 谱系/note）——迁移由一次性 AST 生成器产出并**值序逐字节核验**（`orig==mig` True；源固定 HEAD 版列表防自引用漂移）；`test_deny_list.py` 改共读（跑 lang∈{both,bash} 子集），新增 `test_deny_list.ps1` 驱动（跑 {both,ps}）
- **deny-list.ps1**：逐函数镜像 deny-list.py（文末双源对照表 + 改判据两源同改义务入头注）；六处有意差异全声明——**D-a** 归一不做 `\<word>` 转义拼接删（\ 系 Windows 路径分隔符，删之破坏白名单方向；对应 2 例 lang:bash），改删 `\+NL`/`` `+NL `` 双续行 + 引号 + 残余反引号；**D-b** 命令名 IgnoreCase 但 **git 旗标字母保持区分**（-D/-d、-S/-s 语义差由 git.exe argv 自持）；**D-c** rm 别名域双标尺（git 域=py parse_flags 逐字等价；CMDLET 族 Remove-Item|ri|rm|del|erase|rd|rmdir 旗标 = bash 字母 ∪ **PS 前缀缩写**（方向=全称.StartsWith(输入)，实施自查修正过一次反向）∪ cmd 形 /s /q /f）；**D-d** pathspec TrimEnd 扩 `\`（`git restore .\` 真丢弃）；**D-e** 白名单自展开 Resolve-PsPath（hook 收字面串未经 shell——$env:/%%/~ 展开、未知变量 UNRESOLVED 即拒、纯字符串折叠 normpath 非 realpath、ToLowerInvariant 比较、根集含 GetTempPath∪env∪字面 /tmp /var/folders）；**D-f** warn 扩集（左 iwr/irm 族、右 iex 族、新形态 ①' `iex (iwr …)` 括号形、icacls /T、Start-Process -Verb RunAs）
- **v1 诚实边界（头注 FN 清单）**：`powershell -EncodedCommand` 整体旁路 / 变量与串拼接构造 / splatting / `Remove-Item -Recurse` 无 Force（**parity 刻意放行**，fixture 锁——py 同型 `rm -r` 放）/ robocopy /MIR 等 Windows 原生破坏族不入名单（黑名单不可穷尽原则同文）；终极防线 = Claude Code 原生权限确认
- **hooks.json 接线**：PreToolUse 增 `matcher:"PowerShell"` handler，exec form `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ${CLAUDE_PLUGIN_ROOT}/hooks/deny-list.ps1`；Bash handler 不动；非 Windows 上 PowerShell 工具系 opt-in（CLAUDE_CODE_USE_POWERSHELL_TOOL，review R7 订正——原「不注册」表述超卖），未启用即不触发；即便启用而 powershell.exe 缺失 → exec 失败为非阻断错误（fail-open 与 python 缺失同格）。**pending-updates / stop-reminder 本批不 port**（裁决仅 deny-list——Windows 原生会话漂移队列/Stop 提醒仍缺，README/install 措辞含）
- **install.sh D4 改分层**：「Windows hooks 不支持」作废 → Git Bash 会话（两域各拦各的 shell）/ 原生 PowerShell 会话（deny-list.ps1 生效 + 实机验证面提示 + 漂移/Stop 需 python）两式
- **驱动结构**：ps1 判据面**点源 in-process**（LIB_ONLY 短路入口段；黑盒逐例 spawn 冷启 0.4-1.0s×138 不可受）+ **契约黑盒探针 ×4**（deny JSON / 非法 JSON fail-open / ask JSON / 文案锁「不要尝试绕过」跨实现）+ 单调性 ps 集（引号插 / 反引号续行插；`\` 变异随 D-a 不入 ps 集）；os=win 例非 Windows 跳过并计数；黑盒子进程显式 UTF-8（5.1 GBK 码页坑——探针4 中文防乱码误红）
- **test-self 双驱步**：pwsh/powershell 可得则全跑计断言，否则 `SKIP deny-list.ps1 fixture` 打印不红（同 AO dart SKIP 先例）——本机 mac SKIP 计 27 断言，**CI pwsh 上为 28**（计数口径随环境，review R9 如实记）
- **CI pwsh 步转正**（§7a 可选加固位；ubuntu runner 预装 pwsh 零安装步骤）：步注声明证据级 = 「语法 + 判据逻辑回归」非 Windows 实证（PS Core on Linux ≠ Windows PowerShell 全同）；首跑即红已本机便携 pwsh 复现修复（见验证条）——**mac 验证缺口自此由便携 pwsh 临时封堵**，5.1 差异面仍需实机
- **实施后独立 review（3 major 全处置——三者恰全藏在「mac 无 pwsh」验证缺口内，CI pwsh7 一项拦不住，实证本批终验必在实机）**：R1 Get-RmFlags 字母扫描误作用长名（`-Force` 内含 r 假置 Recurse / `-WhatIf` 内含 f 假置 Force——单文件删与 dry-run 均误拦，且系未声明双源分歧）→ 字符扫描收窄 `^[rf]+$` 捆绑形 + fixture 补 2 allow 锁；R2 驱动 `StandardInputEncoding` 系 .NET Core 3.0+ API，5.1（验证闸本体）赋值抛 Stop 终止——删该属性（输入侧探针全 ASCII 不依赖）；R3 **两 ps1 无 BOM，5.1 按 ANSI 码页解析中文文案全乱**（GBK 模拟实证：解析不炸、机制仍效、但弹窗 reason 乱码 + 探针4 文案锁必红）→ 补 UTF-8 BOM（pwsh7 兼容）；R4 入口 `[Console]::InputEncoding` setter 无控制台宿主下抛→整闸静默 fail-open → 改 OpenStandardInput/Output + 显式 UTF8 StreamReader/Writer；R5 D-b 头注「子命令 IgnoreCase」过宽（stash "clear" 实为区分——与 py parity 且 git.exe 自身敏感）→ 头注分层订正；R6 install 无 python3 旧警告「三 hooks 均不生效」与分层矛盾 → 措辞修；R7 CHANGELOG「非 Windows 不注册」超卖（官方：opt-in 工具）→ 订正；R8 同步 handler 冷启 0.2-1s × 每条 PowerShell 命令的延迟成本（py ~30ms）→ 记录在案不处置（deny 硬闸语义优先，取舍随条目公开）
- **验证（终验前证据级）**：py 驱动迁移后全绿 **70+30+11+50 变异 = 111 例集零变化**（bash 侧行为不变的直接证据；夹具现 138 例 = 111+ps27）；Get-RmFlags 修正后语义全表模拟复推 12/12 格相符；**CI pwsh 首跑即红（v51 同型）——本机便携 pwsh 7.4.6 当场复现**：`Normalize` 末步 `.Replace($bt,'')` 被 PS 重载绑到 `Replace(char,char)`、空串转 char 抛（`$ErrorActionPreference=Stop` 放大为整脚本中止）→ 改 `[regex]::Replace(Escape)` 加注释；修复后 **ps 驱动 80 拦 + 36 放 + 17 warn + 24 变异 + 4 黑盒探针全绿（os=win 跳 3）**、pwsh 在 PATH 时 **test-self 28/28**（= CI 路径本机等价复验）；test-self mac SKIP 态 27/27；JSON 例数/值序断言过（迁移源固定 HEAD 版防自引用漂移）——**剩余终验 = 用户 Windows 5.1 实机**（pwsh7 已绿不覆盖 5.1 差异面：R2/R3/BOM）
- **实机自检清单**（交付用户，Windows PowerShell 5.1 会话）：① `git push --force origin main` 拦 ② `Remove-Item -Recurse -Force C:\...\proj` 拦、`rd /s /q` 拦 ③ `Remove-Item -Recurse -Force $env:TEMP\build` 放 ④ `iex (iwr -useb http://…)` 弹 ask ⑤ `git restore .\` 拦 ⑥ 驱动 `powershell -NoProfile -ExecutionPolicy Bypass -File hooks/test_deny_list.ps1` 全绿；不触发首查 plugin 版本 / 新会话生效 / 工具确为 PowerShell
- **观测带数**：常驻基线——零常驻面变化（hooks 不占模板常驻）；distill 四数——仍无数（止损线 2026-12-31）
- 双 json 1.0.17 + README 横幅同步

## 1.0.16 · 支付资损域沉淀落地（Q1 逐组采纳）——skill 新增 payment 域 + checklist 条目 9 回链

> 依据链：[方案-2026-09-09](docs/方案-2026-09-09-支付资损域沉淀-防重与核销时序.md) §6 Q1（需求方 2026-09-16 裁逐组采纳）→ 本批落地。落地前机械复证（saas-cashier + eshop-busi 直读，只读零修改）：V1-V6 全部属实。

- **草稿① 落地**：新建 `skills/flutter-rules/references/payment.md`（防重三层口径含判定线与三易错认知 / 不可逆操作时序两段式 / 重试白名单红线，溯源三事故 commits）+ SKILL.md 按域表 +1 行——纯按需触发面，零常驻
- **草稿② 落地**：checklist 条目 9 幂等短语后加回链句（支付/退款/撤销/核销类核「请求号+在途锁」与重试白名单，口径指 skill 支付域）
- **草稿③ 不落本仓**（照方案定性：saas-cashier 接入时照填 INV-PAY-001/002）——填法示例随 §2.5 增补更新后在该工程记忆库走
- **复证新事实（§2.5 两增补，2026-09-16）**：① B 向（重复核销）修复已在途——saas-cashier `9fe749e3c`（09-11）盲扫全量防重「团购核销全链闸门」，未进 master（仅 dev/2.10.8）；A 向（时序两段式）零进展——INV 照填措辞须含此进境；② 现金路径「500ms 防抖」出处不成立于 order_pay_logic（实证在扫码组件），矩阵措辞已修正——三层判定不含防抖，落地面文字不受影响
- **验收**：A1 payment.md 在位 + SKILL 表可索引（grep 实证）；A2 checklist 回链句在位（reviewer 首用随真实 review）；A3 test-self 27 断言不受扰（实跑绿——新增纯内容无断言面）
- **观测带数**：常驻基线——零常驻变化（references 按需 Read；SKILL 表 +1 行 ≈ 0.1K 字按需面）；distill 四数——仍无数（止损线 2026-12-31）
- 双 json 1.0.16 + README 横幅同步

## 1.0.15 · test-self 夹具根 mktemp 隔离（并发互踩根治）+ 批D P2 落账 / P3 删旧 byte 互锁

> 依据链：1.0.13 连带发现（固定 /tmp 夹具根跨实例并发互踩、四种失败签名全归因——留独立批裁决）→ 本批落地；[孪生方案](docs/方案-2026-09-15-孪生同文块生成化.md) P2/P3 前置（试点两 minor = 1.0.13 / 1.0.14）已满随批落账。协调：flutter-09 让位回执（其全程只读），版本 1.0.15 无撞号。

- **夹具根 mktemp 隔离**：7 个固定 /tmp 根（cf-selftest / cf-upg / cf-ao1 / cf-ao2 / cf-pitfalls / cf-ao-dart / cf-gi）全部改 `mktemp -d /tmp/cf-*.XXXXXX`（1.0.12 T6 先行 idiom 全面化）；收尾清理改删变量；**U 夹具补收尾**——原代码从不清理 U（靠下一跑开头 `rm -rf` 兜底），mktemp 化后兜底失效每跑漏一目录，迁移当场抓出补上；DA 特例：mktemp 占唯一名后删目录再 `dart create`（其要求目标不存在）。模板留 cf- 前缀，崩溃残骸可寻
- **并发实证**：4 实例并行全绿（29/29 ×4、rc=0 ×4——修复前同场景 3 连跑出 3 种失败签名）+ P3 后 3 并行复跑（27/27 ×3）；单跑前后 `/tmp/cf-*` diff 零新增残骸
- **P2 落账（弱行使如实记）**：观察期两 minor 满、生成闸（第 28 断言）每跑全绿；但两 minor 均未动 canonical 内容，「改了 canonical 忘跑 render」失败模式**未被实际触发**——观察结论为「闸在位且绿」，非「失败模式被拦截实证」；Q3（自动提醒）维持「先观测再定」不做
- **P3 删 2 条旧 byte 互锁**：P1b ②（twin 档位预设节/收尾时序行/Gate 例外段三段逐字同文）+ 1.0.7 ②（help↔README 档位段逐字同文）——四块内容已由第 28 断言 canonical↔四文件同步 + 8 锚串守卫全权；**覆盖差如实记**：围栏外节内文本不再逐字比对（D4 双保险按 1.0.12 预裁取消）。断言 29→**27**（方案「净 −1」系对试点前 27 基线口径：+1 闸 −2 旧）；删后 test-self 内 tp_sect/hp1 零残留引用（docs 存史引用保留并注记）
- **docs 落账**：孪生方案状态行 P2/P3 刷已行；裁决单「批 D P2/P3 待行」→已行；[评审-plan-孪生同文块生成化](docs/评审-plan-孪生同文块生成化.md) 补缺失状态戳（D2 纪律缺口，flutter-09 清点发现、让渡本批）并注其引用的 tp_* 函数已随 P3 删
- **边界如实记**：CI 的 `/tmp/ao_check` 不动——runner 每 job 全新无并发面；deny-list fixture 的 /tmp 命中系白名单逻辑样本（stdin 管道，不建目录）非夹具根
- **验证**：单实例 27/27；deny-list / stop-reminder fixture 随 test-self 全绿；改动全在测试脚本与 docs，模板 / hooks / 分发面未动
- **观测带数**：常驻基线——零常驻面变化；distill 四数——仍无数（止损线 2026-12-31）
- 双 json 1.0.15 + README 横幅同步；test-self 27 断言单实例与并行均绿

## 1.0.14 · 批E——checkout_discards 判据换「目标面」+ F9 销项 + docs 轮次化

> 依据链：[裁决单-2026-09-15](docs/裁决单-2026-09-15-1.0.10全面外审与四批处置.md) §6-①（需求方裁「换判据为目标面」）→ 本批落地；§6-② F9 全量纯函数版裁「不做」销项（判据更换后 checkout_discards 不再自解析 token，双解析器已不存在，纯函数版前提消失）；§8 F2 裁「恢复排期」落账（Windows 原生批另开，README 环境节措辞随批改）。批E 经独立 review（无 🔴，🟡×2 / 🟢×4，处置见下）。

- **判据更换（§6-①）**：checkout_discards 由「源是否为 HEAD」改为「**目标面写工作区 + 丢弃形态 pathspec**」——`git restore -h` 实证 `-W, --worktree` 是默认目标面（restore 默认写工作区），源取值（-s/--source，HEAD 还是 stash）不改变「覆盖工作区即丢弃」的事实，原判据与 git 语义相悖。旗标一律走 parse_flags（捆绑短旗标 / 长旗标 =值 同源），位置解析整段移除（函数净 −7 行），-s / -s贴值 / --source / --source=值 / --source 值 五拼法天然同判——1.0.11 F11 记录的「checkout_discards 自解析 token 不走 parse_flags」既存不一致就此收口
- **行为变更两格（fixture 翻转）**：`git restore -s stash@{1} .` 改拦（原放——v39「指定其他源=非丢弃」裁决随判据推翻，覆盖工作面即拦，净收紧）；`git restore --staged .` / `--staged -s stash@{1} .` 改放（原误拦——-S 只动暂存区不写工作区，本轮探针新发现的 FP 顺手修）
- **git 事实底座（本机 git 实证探针）**：checkout/switch 无 --source 选项（`git checkout --branch=x` / `git switch --create=x` 均拒——F11 豁免面不可达）；restore 的 `--source=<tree>` git 接受（可达，故收口有实际效力）
- **review 处置**（🟡×2 已修）：R1 W-override 分支首锁——`git restore -SW .`（S 豁免被 W 覆盖仍拦）此前零 fixture 走到、回归可静默翻转，BLOCK 补例；R2 空格长形态 `--source stash@{1} .` 补锁（探针已验未上闸）；R6 头注死指针修正只修一半（行号 19 实为 25）——去行号化改 grep 锚，:97 同款既存行号引用顺带去；R3 🟢 docstring 补「:/ 前缀源值窄误拦（deny 方向用户摩擦，deny-by-default 取舍内）」诚实边界；R4（`--` 后旗标形文件名，玩具场景）/ R5（force_switch 的 s/source 豁免 git 现不可达、头注已记）记档不修；R7 正向核验——头注/docstring/fixture/计数四方自洽，12 探针形态 trace 相符，`-bs` 捆绑建分支豁免顺带修正旧码 exact-token 漏豁免
- **F9 销项（§6-②）**：全量纯函数版不做——三类变异均落归一化全局删除规则（norm(变异) ≡ 原串），BLOCK 全绿则断言必绿（1.0.11 R3 复核已定），325 变异 ≈ +24s CI 无新甄别力；批E 后双解析器不存在，「重构安全关键件」理由消失
- **docs 轮次化**：删复盘两篇（批2c双坑 / 质量脚本与裸push双坑——结论已入 0.1.1 / 0.4.1 条目，git 史可寻回）；0.1.1 条目出处指针去链改注（「1.0.14 轮次化删除」）；checklist.md 核无具名引用
- **裁决单/方案落账**：裁决单状态行全刷（F2 恢复排期 / §6 两项已裁 / 支付 Q2=A+B〔Q1 仍待裁〕/ 批D P2/P3 待行）；支付方案 V6 行改需求方裁 A+B 两向并存，§5-4 修复时序改两向都走
- **fixture → 111**（实跑 70 拦 + 30 放 + 11 warn + 单调性 50 变异，0 失败；批E +3 拦翻转 1 放 / review +2 拦；计数以实跑输出为准）
- **观测带数**：常驻基线——本批零常驻面变化（改动全在 hooks / fixture / docs，模板面未动）；distill 四数——仍无数（止损线 2026-12-31）
- 双 json 1.0.14 + README 横幅同步；test-self 29 断言单实例跑（/tmp 固定路径并发坑勿并发，见 1.0.13 连带发现）

## 1.0.13 · test-self 非 git 树守卫——快照自测「draft 假红 / tag 假绿」显式拒绝

> 发现链：1.0.12 发版链末步「快照独立验证」（cache 是全仓快照 → 在快照上跑其自身自测）抓出 PASS=27 FAIL=1。**非本批引入**——1.0.9/1.0.10 快照同样 FAIL=1（cache 从来不是 clone）。根因：28 条断言中仅有的 2 条 git 依赖断言在无 .git 树里变形，方向还相反。

- **假红**：`release draft` 断言吃 git 报错码 128（期望 0）——快照上必 FAIL，幽灵红
- **假绿（更贵）**：`release tag 9.9.9` 断言期望 rc=1、实测确为 1，但走的是「读 HEAD plugin.json 失败」分支——其声称守护的「1.0.2 D2 防 tag 打在 bump 前旧树」版本比对**从未执行**
- **守卫**（fail-closed）：test-self 头部 `git rev-parse --is-inside-work-tree` 显式拒绝并说明原因（「插件 cache 是文件快照、非 git 仓」），不静默变形
- **第 29 断言（反向）**：脚本拷入非 git 目录跑须显式拒绝——判据三条件：rc≠0 **且** 提示语命中 **且** 输出无 PASS 行。rc≠0 单独不成立：守卫缺失时该拷贝会跑完全套、因既有 FAIL>0 同样退出非零（又一个假绿）
- **连带发现（本批未修，留独立裁决）**：test-self 夹具根用固定 /tmp 路径（cf-selftest/cf-upg/cf-ao1/cf-ao2/cf-pitfalls/cf-gi/cf-ao-dart；1.0.12 的 T6 已用 mktemp 但旧夹具未迁）——跨实例并发互踩致间歇假失败（同机维护会话并发跑套件实锤；机理：收尾 `rm -rf /tmp/cf-selftest` 删并发实例的 `$D/old` → install.sh `[ -d ]` → exit 2；gitignore 8 行 / memory 0 / AO 未跑起三种失败签名均可映射到共享路径互踩）。mktemp/PID 隔离修复独立批次裁
- **验证**：正跑 29/29；反向端到端（真拷贝非 git 目录）rc=1 + 提示命中 + 零 PASS 行；CI 在真 git 树不受影响
- test-self 28→**29**；双 json 1.0.13 + README 横幅同步

## 1.0.12 · 批D P1——孪生同文块生成化（canonical 单一源 + 双守卫 + 生成闸）

> 依据链：[裁决单-2026-09-15](docs/裁决单-2026-09-15-1.0.10全面外审与四批处置.md) F3（需求方裁「部分采纳·四块试点」）→ [方案 v3](docs/方案-2026-09-15-孪生同文块生成化.md)（**两轮独立评审**，消解 R1-R19；第二轮实证「消解 ≠ 闭环」——v2 的修订动作自引入 5 条新缺口，R17 系「修 R1 的动作反噬 R1 的成果」）→ 本批 P1 落地。**防漂移从「检测」前移到「构造」**。

- **canonical/ 四源**：档位预设节 / 收尾时序行 / Gate 例外段 / help↔README 档位段——从现模板**逐字提取**（非重写），sha 核验 app↔plugin 一致（`3b40a302…`/`972055…`/`24085e…`/`c2761b…`）
- **[scripts/render-blocks.py](scripts/render-blocks.py)**：围栏区间整块注入 + **双守卫**——① 登记一致性（全仓 `gen:` id 集合 == EXPECTED 键集，堵「新增块忘登记」）+ 计数（每 id×文件恰好 1 对围栏，堵「没跑起来却空过」）；② 内容同步（渲染后重读区间 == canonical，堵「围栏在、内容未改写」）。围栏标记手写为位置锚、**区间全部内容**由 canonical 生成（R17 修正：原设计把说明行写在围栏内，与整块替换语义自毁）
- **四文件加围栏**：app/plugin 模板各 +9 行（3 块 × 开/说明/闭）、help.md/README.md 各 +3 行；说明行区分双受众（「仓内维护者勿手改」+「消费方按 init 引导删减未选段」，与 `init.md:44` 同向不互斥）
- **test-self 第 28 断言**：生成闸——**/tmp 副本**渲染后与仓内比对（不原地改写被跟踪文件，守既有只写 /tmp 隔离）；**旧 byte 互锁 2 条并保**（D4 双保险，试点两个 minor 后另批删，净 −1）
- **验证**（证据分级：构建证据）：**围栏行 +9/+9/+3/+3，围栏外零改动**（相对 1.0.11 前置态逐字节 diff 核对——工作区叠有 1.0.11 批A/B/C 改动，裸 `git diff` 数值含前置批，口径见 review R3）；守卫有效性**实测**（手改围栏内→生成闸红；删围栏对→`rc=1`；**加固后四探针**：canonical 清空 / EXPECTED 清空 / 孤儿 canonical / 围栏挂未登记文件——皆 `rc=1`；锚串守卫**反向验证**→红）；render 幂等（两次跑皆 0 失败）；test-self **28/28** + deny-list fixture + stop-reminder 全绿
- **实施后独立 review**（无 🔴；9 条 R1-R9 已处置）——**守卫①** 由「id 集合」扩为 **(文件, id) 对级校验**（原实现向 `commands/help.md` 挂 `gear-preset` 围栏可带垃圾内容全绿，reviewer R1 实测）+ canonical 文件名集校验（堵孤儿源 R6）+ EXPECTED 非空下限（R5）；**守卫②** 补 canonical **正文长度下限**（原 canonical 清空/截断 → 双侧对称 → 比对与四方同源闸**皆绿**、整段静默消失——系相对旧 byte 互锁的**能力回退**，reviewer R2 实测）；**第 28 断言补锚串守卫**（8 个锚串直查仓内目标文件，堵 R2 的「双侧对称绿」残留，反向验证已过）；其余 R3（证据基线口径）/R4（README F2 措辞改「建议·待裁」）/R7（尾随空行语义注明）/R9（方案用例回填）随批处置
- **观测带数**：常驻面 app **16168**/18000、plugin **14867**/16500 字符（+9 行围栏，余量充足）；distill 四数——仍无数（止损线 2026-12-31 触发）
- **P2/P3 待行**：P2 观测 2 个 minor（render 是否被遗忘触发）；P3 试点通过后删 2 条旧 byte 断言（前置：守卫已就位 ✓）
- **维护者面指引**：README「每次 minor 例行」加「同文块改动」条（改 `canonical/<id>.md` + 跑 render，**勿直接改围栏区**；尾随空行语义注明）——机制上线但维护者不知情即等于无机制；CI 语法编译步纳入 `scripts/render-blocks.py`

## 1.0.11 · 批A 安全面收口 + 批B 漂移补充 + 批C 度量文档

> 依据链：[裁决单-2026-09-15](docs/裁决单-2026-09-15-1.0.10全面外审与四批处置.md)（1.0.10 全面外审四轮，F1-F16）**批 A**（F9/F10①/F11/F12/F13）+ **批 B 首项 F1**（F2 因验证手段待裁暂缓，见该单 §7）+ **批 C**（F4/F5/F7/F14/F15/F16/F10②）。批 A 全部先 fixture 红后修绿（fixture-first）；探测全程 json.dumps 构造（v41 纪律）。批 A 经独立 review（reviewer 轮，无 🔴）——R1/R2/R3 三条 🟡 已处置见下（含一次**事实声明超卖**：本条目初稿曾写「副作用已核」而未实跑，经 review 抓出改正）。

- **F11 长旗标 `=value` 剥值**：`parse_flags` 长旗标 `t[2:].split("=",1)[0]`——`--force=true` 按 `--force` 判。此前 push/clean（集合判定）放行、reset（子串判定）拦截的**判定不一致**收口。**今日不可利用**（已在无远端草稿仓实证 git 自身拒绝该语法：`error: option 'force' takes no value`），系防御纵深一致化。**连带面如实记**（R2 复核补）：剥值使 `force_switch` 的豁免集合对 `--branch=X`/`--create=X`/`--source=X` 长形态生效（旧/新版对照：`git checkout -f --source=other main` 等四例 deny→allow）——git 现拒该语法故不可达，未来 git 若为 checkout/switch 补 `--source=<tree>` 时属语义正确的豁免。**既存不一致（本批未触及，待裁）**：`checkout_discards` 自解析 token、不调 parse_flags，故 `--source=stash@{1}` 长形态仍 deny 而 `-s stash@{1}` 短形态 allow（后者系既有 fixture 裁决 `test_deny_list.py:111`）；全表无 `--source=` 长形态样本故无闸
- **F12 warn 层下载执行扩解释器面**：管道右侧由 shell 族扩至 `python3?|ruby|perl`——`curl x.sh | python3` 是下载执行第二常见形态，此前全放行。两步法（下载落盘再执行）/非管道形态仍不盖（头注诚实边界不变）
- **F13 `git filter-repo` 入 warn**：filter 判定改 `filter-(branch|repo)`——filter-repo 是 filter-branch 官方推荐继任者，重写历史等价高危，拦旧工具放行新工具是时效缺口
- **F9 归一化单调性性质断言（新机制）**：BLOCK 样本经三类「归一可还原」变异（引号插入 / 续行插入 / 反斜杠拼接）后**不得变 allow**——锁归一函数回归。样本取 `[::7]` 确定性抽样（防全量 subprocess 超时），位置 1/3·2/3；实跑 50 变异全绿。**价值界说（R3 复核修正，防高估）**：因三类变异均落在归一的全局删除规则上，`norm(变异) ≡ 原串` 恒成立，故本断言在 BLOCK 全绿时**必然全绿**——其独立价值仅在「归一函数回归」（如引号删除被收窄为词内）；首次跑红的 5 个变异系基准样本本身应拦未拦（F11 未修），**不构成本机制的独立价值证据**。全量纯函数版（提取 `normalize()` 后覆盖全样本 × 全位置）记为后续改进项（重构安全关键件收益/风险比待裁）
- **F10① 三 hook 输入契约 fail-open 显式声明**：deny-list / pending-updates / stop-reminder 头注各补一行（stdin 非法 JSON → exit 0）——输入由宿主构造风险低，fail-closed 恐误伤非 JSON 探活，**行为不改只补声明**（stop-reminder 静默四态已有 fixture 锁定）。**解释器边界如实记**（R4 复核补）：`python3?` 不匹配 `python2`（EOL 不再扩）；路径 / env / sudo 带参前缀形态均不盖——「解释器须紧贴管道符」系既存边界
- fixture 99→**105**（BLOCK +2 / WARN +4）+ 单调性 50 变异；防误伤探针 8 条全合理（`--force-with-lease` / stash drop / checkout -b / restore -s stash / curl 下载文件 / py_compile / ruby --version 均 allow；`filter-branch --help` 落 ask 系「形态匹配非语义分析」已声明边界）
- **含 F16 覆盖面台账要求**（README 维护节「major 版本前·外审」——批 C 项提前随本单落，R6 复核补依据链）
- 双 json 1.0.11 + README 横幅同步；test-self 26→**27** + deny-list fixture 全绿

### 批 C（度量与文档，随手项）

- **F15 无效命令修正**：分发面两处 `flutter pub dev publish --dry-run` → **`flutter pub publish --dry-run`**（pub.dev 是站点名非子命令，消费方真发 pub 包时会撞墙）——plugin 模板 §八 + skill `references/build-release.md`（复审轮补读产出）
- **F4 常驻面字数预算闸**（test-self 第 27 断言）：app/plugin 模板 + NAVIGATION 合并**字符数** ≤ 18000 / 16500（批C 实测 15833 / 14532 + ~12% 裕量）。**口径 = 字符数（python len）而非 `wc -m`**——macOS 未设 locale 时 `wc -m` 按字节计，本人批C 即踩此坑（同一文件 wc -m 27915〔字节〕vs len 14769〔字符〕）并写出错误结论「1.0.7 换算比自相矛盾」（实为字节/字符混淆，1.0.7 的 ≈3.1 字/token 与实测 14769 字符 / 4.6k token ≈ 3.2 吻合，无矛盾——该错误由本闸当场暴露，见裁决单 §4）。**本闸首个战果即抓出批C 自身的事实声明超卖**
- **F5 度量止损线改时间触发**：四数止损线由「2.0 前仍零样本」改「**2026-12-31 前仍零样本**」——版本里程碑可能长期不达，时间线更硬；首个 distill 周期列观测项第一
- **F7 维护者面概念地图**：README 维护节新增「概念地图（维护者速查）」——双 Gate / 收尾三档 / 项目档位 / 证据 5 级 / L0-L2 / 校验层 / 沉淀闸（含档位）/ 提速档 / 两类台账 / 观测带数 共 11 行「一句定义 + 权威落点」，只索引不复制正文
- **F14 performance.md 场景行**：SDK 选型节补「已有 RUM/Bugly 免费栈的团队优先沉淀现有栈接入坑（混淆符号表上传 / 维度口径 / 本地日志对账），不为此引新 SaaS」——生产栈（RUM+Bugly+自建本地日志）系成本动因下的既定决策，通用选项列举保留
- **F10② 角色卡 model 档位复核**：入 major 外审清单点名项（agents frontmatter 硬编码模型代号随演进过期）
- **F16 覆盖面台账要求**（随本单落，见上）

### 批 B 首项（F1 漂移队列盲区）

- **F1 git 快查补充盲区**：Bash 落盘的文件（`flutter create` / `mv` / `cp` / 重定向 / `build_runner` 生成器）不经 PostToolUse（matcher 仅 `Edit|Write|NotebookEdit`）故不进 `.pending-updates`——stop-reminder 队列非空时额外 `git status --porcelain -uall` 快查，检出未入队的 A/D/? 源文件并入提醒（排除 `.g.dart`/`.freezed.dart`/`.mocks.dart` 生成物与非 `.dart`）。**`-uall` 必需**——默认 git 把未追踪目录折叠成 `?? lib/` 单条目，展开才见具体文件（fixture 首跑即抓出此坑）。**设计取舍**：git 快查**不独立触发**（未提交改动是开发常态，独立触发会每次 Stop 重复打扰）——仅作队列非空时的补充信息，故「纯 Bash 落盘会话」仍不提醒（诚实边界，待观测后定是否加状态文件去重）；非 git 仓 / 超时（5s）静默降级
- stop-reminder fixture 五态→**七态**（+git 快查补充 / +非 git 仓降级），全绿

### 观测带数：常驻基线——本批零常驻面变化（改动全在 hooks / fixture / 文档，模板面未动）；distill 四数——仍无数（未到首个周期；止损线 F5 待处置）

## 1.0.10 · 常驻面收敛——§八/§九/§十一 按需下沉 + 近似规则去重

> 依据链：1.0.9 后注意力稀释专项分析（本仓对话）——稀释主因是常驻面**条数×相似度**而非 token 量（§十一两表 28 行高度同构映射是最大单簇）；裁决单 B-D1 遗留 C4「按需 @import 拆分 §七~§十一」2026-09-14 裁「独立小方案另议」，本批即该件首期——§七系脚手架（装后自删）不在常驻面，本批收 §八/§九/§十一 下沉 + 近似条合并（孪生镜像改）。**跳过三簇裁决记录**：硬编码（§一 vs §十——枚举类型 vs 响应式归口，信息不重叠）、收尾时序（§三 vs §五——1.0.5 已下沉细则，余为序列级双镜头）、ThemeExtension ×3（预设说明 / 架构纪律 / 路由指针三角色）——各有独立信息量，非真重复不动。

- **§十一 速查表下沉（双模板）**：App 向 14 行 / plugin 向 14 行场景→skill 映射表迁入 flutter-rules SKILL.md 新「dart-flutter skill 速查」节——查映射的时机恰是 skill 已触发的时机，常驻零收益；模板留单行指针（节头保留，节序号集不变）
- **§九 TDD 适用范围下沉（双模板）**：App 按层分档表 + 同构批量红绿注 + plugin 公开 API 全覆盖表 → 新 `references/testing.md`（按需 Read，逐字迁移未改写）；模板留「### TDD 适用范围」+ 一句指针，plugin 侧「public API 默认全覆盖」红线短语保留常驻
- **§8.2 Riverpod 四条下沉（app）**：→ 新 `references/state-management.md`（**选 A 时生效**语义 + 消费工程实战上移出处随迁——0.1.2）。**代价如实**：纪律从常驻降为按需，依赖 skill 触发与 review 把关——SKILL.md description 补「状态管理 / 测试选型」触发词、help.md skill 行同步，作补救
- **近似条合并（孪生镜像改，双模板同源对照改）**：§二 首条「禁止自动提交」删（§一 已含完整版并带「详见 §二」指针——原 ×3 收 1）；§一「风险操作先确认」枚举压为指针句（清单与四步确认流程权威在 §二）；app §八 assets 完全重启半句删（§四 权威份保留，§八 留微型指针）
- **SKILL.md**：按域取用表 +2 行（state-management / testing）；「与 dart-flutter 分工」注自指化（原指「项目 CLAUDE.md §十一速查表」，下沉后指本文件新节——防死指针）；索引 37→79 行（+2.7K 字按需触发面，换常驻 −3.6K 字；查映射与 skill 触发时机重合，不增实际读取量）
- test-self 26/26 复跑绿（节序号集 / §一~§六孪生条数 / 档位四方同源 / ga 串全过——§八/九/十一均不在孪生条数闸面，下沉不改节结构）
- **观测带数**：常驻基线——直计 app 模板 −2,191 字 / plugin −1,447 字（按 1.0.7 字↔token 换算 ≈ −0.7k / −0.46k token，新装投影 ≈4.8k；常驻条目 app −24 / plugin −20——§十一表行 + §九表行 + §8.2 四条 + §二 一条）；未复测（下次 minor 装机一并 `/context` 实测）；distill 四数——仍无数（未到首个周期；止损线已挂）
- **发布后追加（2026-09-15）**：release.sh verify-cache 最新版解析修复——`ls -v` 在 macOS BSD ls **非版本序**（系「unedited output」，字典序 1.0.9 > 1.0.10，`tail -1` 取到旧目录——verify 验旧不验新，且「dart-flutter skill 速查」串在 1.0.9 §十一节头本存在，双重假绿；1.0.10 发版链路当场实证抓出）改 `ls | sort -V`（与 commands/init.md 源定位同 idiom 对齐，本机实测 1.0.10 正确居尾），修复后以 1.0.10 独有串「已随 1.0.10 下沉」复验 ✅。同型排查：init.md `sort -V` 实测正常（消费侧无恙），全仓 `ls -v` 仅此一处（v59 BSD grep 坑同款环境假设）。维护者面脚本，不随 cache 分发、无消费影响，随下个版本号自然进快照

## 1.0.9 · 外审余项处置——warn 层（高危形态弹窗确认）+ 度量防空转 + VSCode 扩展环境节

> 依据链：1.0.8 后第五轮外审复验余项 🟡3（度量零数据——「无任何提醒与绑定」措辞经机检修正为「R<n> 编号已供 ledger、缺的是动作绑定」）+ 🟢12（VSCode 扩展环境无独立 CLI）+ 🟢7（先确认类操作散文化、无机制）。机制选型经 claude-code-guide 对官方文档核证后钉死：PreToolUse `permissionDecision: ask` 强制弹用户确认（自动批准模式亦然、分类器不得静默放行）、多决策优先级 deny > ask——additionalContext 伴随工具结果注入（事后），对「先确认」无效故不采。

- **🟢7 warn 层（高危形态「先确认」机制化）**：deny-list.py 增 warn 分支——全部未命中 deny 后，高危四形态（curl/wget | sh 下载执行、chmod -R、sudo 命令位、git filter-branch）改发 `permissionDecision: ask` 弹窗由需求方裁夺（不拦执行，人放行/否决）；deny 优先天然成立（命中 deny 已 exit）。sudo 判命令位（行首 / `; && || & |` 换行后）防 echo 谈论误弹；filter-branch 例自证词内 branch 过 GIT_SIG 分支判定不误拦
- **输出契约现代化（随批存量修正）**：`blocked()` 由官方已废弃顶层 `{"decision":"block"}` 迁至现行 `hookSpecificOutput`（旧形态仅靠映射兼容；ask 在旧形态无对应值，deny/ask 统一走现行契约）——test_deny_list 判定与 test-self 幂等断言 grep 口径随迁
- **fixture 92→99（+7 WARN_CASES）**：四形态 + 管道右侧 sudo + `&&` 后命令位 sudo + filter-branch；测试判定重构为三值（deny / ask / allow）；deny 优先由既有 BLOCK「sudo git reset --hard」「sudo -u root git clean -fd」背书
- **warn 边界（头注如实声明）**：bypassPermissions 下 ask 行为官方文档未覆盖；两步法（下载落盘再执行）无管道形态不覆盖；echo 内嵌形态词误弹（ask 误弹方向无害）；curl 多级管道只看首段——形态匹配非语义分析
- **🟡3 度量防空转三件**：distill §7 空态输出显式异常行（ledger 不存在或零新增不静默「无数」）+ reviewer 复核结论尾固定提醒主控回填 ledger（落账动作归主控）+ README 观测带数补四数止损线（2.0 前仍零样本 → 砍四数只留原始账）
- **🟢12 VSCode 扩展环境节**：README 新增「VSCode 扩展环境（无独立 claude CLI）」——扩展内嵌 claude 二进制代跑同款命令、路径随升级漂移不写死现查、装后等价（命令 / hooks / plugin update）；项目内模板升级与 init 走 cache glob 不依赖独立 CLI
- 双模板 hook 边界句各补 warn 层半句（deny 无放行承诺不变，warn 弹窗放行面显式化）；README 守护行 / 共存节、help.md hooks 行与链外恒在注同步
- test-self 26/26 复跑绿（README 维护节四组重构〔发布操作 / 每次 minor / major 前 / 原则与观测〕系本批配套整理，按触发时机归组防清单平铺回潮）
- **观测带数**：常驻基线——模板面净增约 80 字（两模板边界句半句 + 无新常驻件头），未复测（下次 minor 装机一并）；distill 四数——仍无数（未到首个周期；止损线已挂）

## 1.0.8 · 安全面收口——deny-list 三类拼合绕过堵死 + hooks python3 回退 + 治理句外迁

> 依据链：1.0.7 后第五轮外审（全面评审复验，探针实测取证）🔴×2 + 🟡×2——🔴1 deny-list 拼合绕过（bash 续行 / 转义拼接 / 引号拼接三类，10 实例现行全漏拦）、🔴2 hooks 命令 python3 单点依赖；🟡3 度量零数据（未到首个周期，无处置）、🟡5 维护者治理条文入消费面 + checklist 死指针。修复全部先探针验证后落地（json.dumps 构造 payload，循 v41 探测纪律）。

- **deny-list 三类拼合绕过堵死（外审 🔴1）**：分段前加三行归一——①bash 续行（`\`+换行）②转义拼接（`\x`→`x`，限 `\w`——`\ ` 与 `\$` 等 shell 转义保留）③引号删除（词内 `pu"sh"` / 旗标 `--fo"rce"` / 整词 `'rm'` / ANSI-C `$'rm'`）。归一方向一律「拼合」= 只增拦截面不开放行面（黑名单保守方向）。实测堵 10 形态——含 `echo "git push --force"`（引号串含签名：此前尾部引号黏在 `--force"` 上进 longs 集合反而不匹配，头注「字符串里破坏命令一并拦下」承诺实际不成立，归一后兑现）。已知代价（deny-by-default 既定取舍内）：commit message / echo 引号串引用破坏命令原文将误拦，走写工具 / 白名单规避（与 heredoc 误拦同类）
- **fixture 77→92（+15）**：BLOCK +10（三类绕过全谱）/ ALLOW +5（良性续行 / 引号串 / `find \;` 转义分号 / 引号裸词 / 整词引号白名单路径）；头注批次链补全。**计数订正**：1.0.0 所记「本地 75 fixture」系当时转抄未点数，AST 实点 77——历史条目不改写，计数以 test_deny_list.py 实跑输出为准
- **hooks python3 单点回退（外审 🔴2）**：hooks.json 三命令改 `python3 … || python …`——`blocked()` 走 exit(0)，`||` 仅在命令不存在（127）时触发回退，拦截决策不触发双跑（语义实测核实）
- **治理句外迁（外审 🟡5）**：双模板 §十二「既有协作偏好 4 字段…不计入单项开关 ≤6 上限…开关数超 6 触发收敛复核」句删（治理口径属维护者面，不入消费工程常驻模板）→ README 维护节新增「单项开关治理」条；消费面保留「收尾时序档与校验层属任务轴、不设单项开关」行为句。四方同源闸 ga 串 20→19（「不计入」随句移除）
- **checklist 死指针自含化（外审 🟡5b）**：「叙事见 crules-flutter 仓 git 历史」×3 改「私有仓生产实证，口径见头部」——指针指向消费工程不存在的 git 历史，恒死；头部实证口径总注已覆盖信任声明
- test-self 26/26 复跑绿（ga 串 19 化 + 双 json 1.0.8 + README 横幅同步）
- **观测带数**：常驻基线——本批模板侧净减（删 §十二 治理句约 90 字），无新增常驻件头，未复测（下次 minor 装机一并）；distill 四数——仍无数（未到首个周期）

## 1.0.7 · 档位化收口——外审五条处置 + Gate 例外台账机制化 + 校验层规格入分发面（26 断言）

> 依据链：1.0.6 后独立外审五发现（校验层悬空 / 台账无定义 / 守串不守文 / 基线口径 / 发版节奏）逐条复核定案（2026-09-15：两条全对、一条半对降级、一条量级修正、一条前提过时实质成立）；处置裁决——基线实测再裁、台账姊妹文件、规格入面、byte 互锁。

- **Gate 例外台账机制化（外审 🟡2——上批五评审+终审漏网的真缺口）**：定义落四处同源——双模板 §三 Gate 例外节（`.claude/memory/.gate-exceptions`，JSONL：日期/任务/豁免 Gate/理由/范围；只追加不改写、需求方事后审计）+ MAINTENANCE 不进 git 清单 + install.sh gitignore 幂等落位（3→4 行）+ 同源断言。选姊妹文件不并轨 `.review-ledger`：豁免条目无 review 发现，并轨将污染 distill 四数聚合口径（裁决总数/误报率分母）——豁免支点从文字承诺变可审计账本
- **校验层全规格入分发面（外审 🔴1 复核降 🟡 后处置）**：进阶/审查与复核纪律.md 新增校验层节（触发判据 / 隔离子代理 + sonnet 起步 / 推断级逐条·已验证抽查 / 三值结论附可复核证据 / 分流 fail-closed / 轮上限 1·预注册仲裁 / ledger 留痕）；双模板 §三重型档加指针串（入 canonical 串闸，20 串×2）——机制名与规格同在消费面，「规格见 X 而 X 不在分发面」悬空消除；A 案 P1 试点采证口径不变（方案 §7-P2 已戳提前）
- **守串升级守文（外审 🟡3 机制化）**：help↔README 档位说明段上 byte 级互锁断言（此前 8 个 canonical 串只守存在性，同段解说可各自演化——本段两处即逐字复制，钉死，改须双文件同改）；上手教程 §3 收尾段三档口径 + 交付汇报示意加收尾档行（原 P2 触点提前）；design-doc 裁剪档位补「文档轴 vs 任务轴、不互推」映射句（三套三档各归其轴）
- **常驻基线落账（外审 🟢4，裁「实测再裁」→ 发版当日实测）**：新装独立工程 `/context` 实测 **5.5k**——本包侧 ≈5.3k（CLAUDE.md 4.6k + NAVIGATION 索引 0.7k；其余 7 深模板按需 Read 不常驻），余 0.26k 为 Claude Code 自动记忆非本包；距 15K 线余量 ≈9.5k，**不破线**。存量消费工程 install 跳过已存在 = 零增量、沿 14.4k（其增量归因自身 CLAUDE.md，既有口径）。**单位口径修正**：`/context` 显示为 **token**，原文档「实测字符数」系误标（历史 14.4k 读数连续有效）；本批直计净增 +1.25K **字** ≈ +0.4k token（1.0.6 新装 ≈4.9k → 1.0.7 ≈5.3k，与实测吻合）。原「新装投影 ≈15.7K」系双重错配——消费工程混合基线当新装基线 + 字符增量加于 token 基线——**撤回**
- **坑卡池 10/10 满配额**：Windows IME 扫码枪卡（1.0.6 后补提）入池后满额——下一张卡进前须过配额裁决（合并/淘汰），配额闸首次真实触发
- **观测带数**：常驻基线——新装实测 **5.5k**（2026-09-15，独立新工程 /context，1.0.7）+ 存量沿 **14.4k**（2026-09-08 落档）；distill 四数——仍无数（未到首个周期）

## 1.0.6 · 速赢批 + 四轮外审收口——结构性遗留四项清零 + major 外审协议固化

> 依据链：三轮评审后结构性遗留排程（mem-trigger 孪生 / Windows / 裁决索引 / 升级自动化）+ 四轮独立外审三发现（计数漂移 / 实证可信度 / 度量断点）。外审协议本次首次按新维度跑通（风险面四必答 + 通用面五兜底）。

- **速赢批（A/C/D1/D4）**：删已落地审查质量落账方案（docs 轮次化首执）+ 分发面 5 处 docs 引用去路径化（防悬空指针，「被引用的 docs 先去引用再删」入义务）；design-doc §3.5 升级「行业基线与确定性分级」（沉淀类方案必填对标表；✅/⚠️/❓ 逐条分级，❓必进待确认给裁决选项）；mem-trigger 孪生消解（进阶侧改指针，MAINTENANCE 单一权威）；install.sh Windows 显式不支持警告（uname/OS 检测）
- **D3 升级自动化**：install.sh `--upgrade` 子命令——巡检（check-imports）→ y/N 确认 → 自调 `--force`（.new 伴生、memory 永不覆盖、EOF 默认取消零改动；`.new` 合并保持人工，有意边界）；README 升级节 6 行 shell 缩为 3 行
- **D2 裁决索引即状态戳**：docs/ 全部状态戳补齐「下一步动作」，`grep -n "^> 状态" docs/*.md` 一查即得全部等待态——零新文件、无第二份索引可漂移（否决 docs/README.md 手维护表格方案：那是再造孪生）
- **四轮外审三件事**：① help.md 进阶计数修正（5→6 篇）+ help 全景计数闸（声明数 vs 实际文件数，自称权威全表又犯 0.6.2 同型错，上闸根治）② 私有仓哈希实证总注（checklist / 坑库头部：「生产实证但外界不可复现，对外视作信任声明」；上移 skill 优先换公库链接）③ 观测带数义务（本条目即首次履行）
- **major 版本前外审协议固化**（README 维护节）：独立 subagent 全文重读；风险面必答——上下文经济 / 实效度量 / bus factor / 待裁清点；通用面兜底五项。产出走 review-ledger，评级仅趋势参考
- **观测带数（首次，如实）**：常驻基线快照 **14.4k**（2026-09-08 消费工程实测落档，本次未复测——下次 minor 复测）；distill 四数——**首期无数**（消费工程 ledger 尚无累计样本，机制 1.0.3 落地后未到首个 distill 周期）
- test-self 19→**22**（+upgrade 无戳中止 / 拒绝确认零改动 / help 计数闸）
- **发布后追加（2026-09-10）**：平台坑库 +2 卡——[Win7] Flutter SDK 上限 3.19.6 死线 + [Android] SDK 上限三段死线（3.22→API 21 弃 4.x；**3.38→API 24 弃 5.x/6.x**，最后可跑 5/6 = 3.35.x）。Android 卡实证于 saas-cashier master_new（3.38.10 构建，生产 Android <7.0 无法安装——`minSdkVersion = flutter.minSdkVersion` 随构建机 SDK 静默跳线的传导路径入卡）。勘误：本仓早前口径「API 24 未落 stable」系过期网页快照误判，经本地 SDK 源码（FlutterExtension.kt）+ 生产实证双重核正

## 1.0.5 · 二轮评审三发现收口——gitignore 全程机制化 + §五 细则下沉 + docs 轮次化成文

> 依据链：1.0.4 后二轮全面评审三发现（🟡×2 + 🟢×1，依赖核验零断言冲突）。**🟡1 取代 1.0.4 🟡1 的模板侧文字方案**（后人对照 1.0.4 找不到 §五 gitignore 字样即为此因）。

- **🟡1 gitignore 半程收口**：install.sh 幂等追加 `.gitignore` 三行（`indexes/` / `.pending-updates` / `.review-ledger`——缺失才加、已有跳过、dry-run 只报告）；MAINTENANCE「git 分层」从「消费项目手动加」改「安装器自动落位，想反着来装后删行」——MAINTENANCE 政策 → 安装器默认，手动义务归零
- **🟡2 §五 细则下沉**：双模板 §五 裁决回填句删与 MAINTENANCE 逐字重复的 append-only/不进 git/gitignore 细则（gitignore 义务已由 🟡1 机制接管），压回「口径见 distill §7」指针——模板常驻不留细则（B1 瘦身同款原则）
- **🟢3 docs 轮次化义务成文**：README 维护节与「skill 坑节重验」「预设栈审视」并列补第三条——每次 minor 清点 docs/，已落地且批齐的归档或删，裁决中途保留至批落地（防第三轮堆积）
- test-self 新增 gitignore 幂等断言（首装 3 行 / force 重装仍 3 行），19/19

## 1.0.4 · ledger 外审三发现收口——「不进 git」从意图变机制

> 依据链：1.0.3 落地后外审三发现（🟡×2 + 🟢×1，主会话逐条核验均成立——其中 🟡1 核出加码证据：MAINTENANCE.md 不进 git 清单本有 `.pending-updates` 机制先例，同域 `.review-ledger` 却只写意图）。

- **🟡1 gitignore 机制化**：双模板 §五 裁决回填句补「`.gitignore` 加一行 `.claude/memory/.review-ledger`」；MAINTENANCE.md「不进 git」清单加 `.review-ledger`（含防误报率考核理由）——消费工程 `git add .` 不再静默收走台账，§8「不入 git 双保险」名副其实
- **🟡2 note 转义约束 + 坏行容错**：distill §7 字段说明加「note 禁英文引号与换行（引号坏 JSON 行），中文引号「」表述」；读侧「缺字段**或坏行**一律跳过并计数报告」——6.2 原只覆盖缺字段未覆盖坏 JSON
- **🟢3 fid 语义入 ledger 侧**：字段说明补「fid 仅单报告内唯一、跨会话不唯一——勿按 fid 追踪裁决变迁」（producer 侧 reviewer.md 已有，ledger 字段说明同步）
- test-self 18/18（§五 双侧同源改，D1 孪生绿；横幅同步 1.0.4）

## 1.0.3 · 审查质量落账——review 裁决终态可量化（ledger + 四数聚合）

> 依据链：[方案](docs/方案-2026-09-08-审查质量落账与聚合.md)（主会话核验：四处现状锚点属实；C1 flock / §5「常驻 0」/ A1 字段计数三处按核验修正后执行）。背景：1.0.2 评审「方法论强在防错与沉淀、弱在主动提质——reviewer 采纳率/误报率只靠主观复盘」。

- **C1 裁决即落账**：需求方对 review 发现每次裁决（采纳 · 改写采纳 · 误报 · 撤条 · 搁置），主控追加一行 JSONL 到项目 `.claude/memory/.review-ledger`（append-only、不进 git；主控串行追加无并发面，不设锁）；`verified=推断` 且 `verdict=误报` 的行是核心资产
- **① reviewer 发现编号化（C2）**：输出格式 ①~④ 前加 **R<n> 编号**（报告内唯一）——「已验证/推断」字段本就存在，缺的只是可回指 id，裁决与 ledger 按条闭环
- **② 双模板 §五 裁决回填（C6）**：交付汇报必含项之后加「需求方裁决完 → 主控回填一行式」（复用沉淀候选提示同款时序；不设 hook——裁决语义事件 hook 感知不到）；§五 属 D1 孪生断言覆盖面，双侧同源改
- **③ distill §7 聚合（C3/C4/C5）**：读 ledger → 四数（总发现数 / 采纳率 / 误报率 / **按验证状态分桶误报率**——`推断` 级被证伪比例才是修订 reviewer.md 纪律的真信号）；N<30 只列明细不输出比率；`搁置` 不计分母、缺字段行跳过并计数；异常模式（如推断级误报率 >50%）作提名进 §5 闸——观测→修订走同一闸通道不开旁路；聚合输出不常驻任何文件
- 代价：常驻 ≈1 行噪声级（ledger 不 @import；reviewer.md ~3 行属按需载入面）；无新 hook / 无 CI 新断言——「治理从简」裁决不动摇，本批是该裁决的最低成本出口
- §9 三问按默认落地：ledger 不进 git / 搁置不计分母 / plan-reviewer 暂不接（C1 字段已留 agent 位，翻案存量行兼容）

## 1.0.2 · 评审后优化批一（速赢）——LICENSE 补缺 + tag 断档修复 + 语义闸 18 断言

> 依据链：[方案 v2](docs/方案-2026-09-08-评审后优化三批.md)（两轮评审 F1-F13 全消解版）→ [评审-plan](docs/评审-plan-评审后优化三批.md)（主会话评审轮 + plan-reviewer 独立上下文轮，2 🔴 双轮同判：版本撞号 / 溯源闸首跑即红，均本批前置消解）。裁决 2026-09-08：**Q1 MIT / Q2 历史 tag 不回补 / Q3 月度 workflow 缓**。

- **D1 LICENSE（评审 N1）**：MIT 全文 + plugin.json `"license": "MIT"`（manifest schema 正式字段）+ README 定位行声明——公库无许可证的法律模糊态收口
- **D2 tag 断档修复（评审 N2）**：release.sh 新增 `tag` 子命令——HEAD 双 json 版本校验（防 tag 打在 bump 前旧树）→ 打 tag → 推 origin（幂等；不推则消费者 clone 不可见）；发版链路头注更新为「bump → **commit → tag** → plugin update → verify-cache」；[check-imports.sh](scripts/check-imports.sh) 两个静默分支显式报告——SRC 非 git 仓（plugin cache 形态，真实消费者主路径，**先于 tag 判定被走到**）/ 源仓无 tag（改指 CHANGELOG 段人工对照）——此前 `2>/dev/null` 使 0.5.0+ 消费者的 memory 演进比对从未生效；历史 tag v0.5.0-v1.0.0 不回补（Q2 裁决：锚点模糊，错 tag 比无 tag 坏）
- **D3 distill 发起语义显式化（评审 N5）**：description「用户触发」→「用户触发或 AI 发起，闸内仍人工逐组裁决」+ 正文注记声明**故意不设** `disable-model-invocation`（交付汇报的沉淀候选提示依赖 AI 可发起）——发起 ≠ 落盘，消 frontmatter 与注记的共存矛盾
- **D4 聚合层铁律例外从句（外审 0.6.2 Y5 收口）**：frontend.md / backend.md「只允许单一」句后加例外——纯 UI 局部状态（选中态 / 输入草稿 / 动画进度）可直接本地组合不强制聚合层，判定线 = **是否引入第二个底层数据源**（非第二个状态）；修订既有条款而非 +bullet（防同节「只允许单一 vs 可本地组合」表面矛盾致 reviewer 误 FAIL）
- **D5 help.md 两节（外审 Y9 残余收口）**：「冲突时听谁的」优先级链表（需求方指令 > 项目模板 > superpowers/dart-flutter > flutter-rules > 模型默认；deny-list 与 AO lint 独立链外恒在）+「最小概念五条」（双 Gate / 证据 5 级 / 只报不改 / memory 永不覆盖 / 上手路径回链）——冲突时用户此前感知不到优先级链，只见行为「时严时松」
- **语义闸 17 → 18 断言**：+release tag 版本不匹配报错（`tag 9.9.9` 对 HEAD 实版本 exit≠0）；README 横幅版本与断言计数同步 1.0.2/18（横幅计数同步义务本批先行兑现——0.6.2 D1 同型漂移防线前移）

## 1.0.1 · docs 过程文档清账——15 篇已吸收文档删除（3408→237 行，−93%）

> 需求方裁决「没有用的文档可以删掉」：结论已进 CHANGELOG 的过程文档全文删除，git 历史可寻回。**保留 3 篇**：复盘-批 2c 双坑（双模板 ：109 活指针）、外审-0.6.2（裁决表 P2-P4 仍活）、archive/fork-coverage（1.0.0 刚归档）。

- **活引用随删改 3 处**：坑卡 C1/C3 出处指针（layout.md/platform-pitfalls.md 指吸收方案文档）→ 改指 CHANGELOG 0.6.0 条；stop-reminder 头注「复核之复核 §5」→「三审复核 §5」（文件名引用去文档化）；README 维护节「§4.8 的 15K 线」→「15K 线（0.4.x 设计档定档，口径以本节为准）」（原 1570 行设计档删除，口径已完整转述于维护节）
- CHANGELOG 历史条目内指向已删文档的链接失效为已知接受项（git 历史可寻回，不追溯改写历史账本）

## 1.0.0 · 独立成库——斩断与母版 crules 的联系（deny-list Vendor 终态）

> 外审 2026-09-08 P0 裁决落地：fork（v74-fork-base，2026-08）后两包事实自持、母版同步义务收益衰减至拐点以下，正式独立。**斩依赖不斩历史**——史实出处引用保留为溯源资产。

- **deny-list Vendor 终态（方案 a）**：`hooks/deny-list.py` / `test_deny_list.py` 删 `SYNCED-FROM` 戳改自持演进声明——本地 75 fixture 对抗样本库为权威，安全修复本地回归；CI 删「同步比对」步（原拉 crules 主分支 diff 步整体移除，ci.yml 六步→五步）
- **README 供应链节重写**：定位句改「完全独立、无母版依赖」；整删「与 crules 的关系」节（fork 基线/边界判据/跟不跟查表/同步义务）——「同项目二选一勿双装」改写为通用「与其他规则 plugin 共存」纪律保留；维护节「继承 crules v31」→「承本仓 v31 先例」、五维雷达决策改「不引入」措辞（决策本身仍有效）
- **规范性引用改自持措辞**：双模板六条「（跟随 crules v77）」→「（承 v77 先例）」——独立后母版不再是活纪律权威；`进阶/记忆库体系.md`「crules 源仓库中 memory/ 为模板」事实修正（本仓已是源）
- **fork-coverage 归档**：`docs/fork-coverage.md` → `docs/archive/`（Y10 分层归档首件——活文档转历史，install.sh 不复制 docs/ 零安装影响）；app 模板 ：262 断链指针改指 archive/ 路径
- **hooks 头注释去母版名**：pending-updates / stop-reminder「crules 记忆库…」→「crules-flutter …」；init.md / release.sh 措辞清理
- **史实保留清单（永不改写）**：`install.sh:2`、双模板 `:3` 与进阶各篇 `:3` 的「fork 自 crules v74」出处声明、`checklist.md:3`、`进阶/工程化流程.md:160`「crules 基线属根 CLAUDE.md §三」——出处史实与历史 CHANGELOG 条目（0.3.0 跟随 v77 等）均保留
- **随批修**：语义闸③裸 hive 检查 `grep -i 'hive'` 收窄为整词 `grep -iw`——B4 归档引入 `docs/archive/` 后 "archive" 含 "hive" 词级误配暴露既有闸盲点（装闸即抓，同 D1 先例）
- **验收**：test-self 17 PASS（无 SYNCED-FROM 相关断言）；全仓复扫 crules 引用命中集 == 史实保留清单（白名单式零清单外命中）

## 0.6.7 · 外审收口小批 + 质量脚本唯一入口

- **checklist 6 代码规范 +「质量脚本唯一入口」**：工程自定义 format / analyze / check 脚本即唯一入口，CLAUDE.md / §十二 写明并禁裸跑默认参数命令；排查插件行为先验 hook 加载路径（`hooks/hooks.json` 是否存在），声明文件 ≠ 已加载行为（实证 saas_pos_smart_edition：dart-flutter skill 引导的裸 `dart format` 默认 80 宽 × 工程 120 宽门禁，一次波及 166 文件；首判误归因插件 Stop hook，实为 agent 手动执行——hook 加载路径核验后证伪）
- **0.6.7 批（外审收口小批，计划评审两轮 v2 落地）**：① i18n.md easy_localization 裸并列 → 带「不推荐」注记（外审 G4/Y1 同型残留收口）；② 语义闸 +2 独立断言（test-self 15→**17**）——easy_localization 注记闸 + flutter_screenutil 白名单闸（注记词「已停更或维护缓慢」二选一，评审 🔴 消解）；③ README 新增「5 分钟上手路径」节（Y9，四段导览 + 指针防第三份同源口径）；④ 评审 v2 修订全吸收（PASS 计数口径 / 横幅同步）。**缓记**：Y11 守护覆盖矩阵归 P3（与 A1 溯源闸同批）。

## 0.6.6 · 实战复盘吸收批——报表模块多轮返工 + review 误报 M1/M2 契约定级

> 两份实战复盘（saas-cashier 报表模块，`29f490bae` / `51565c01c`）经 distill 吸收：字段契约靠猜多轮返工与 review 误报 M1/M2 均指向同一本质——**契约只存在于实现行为里，没有被显式化**。

- **reviewer agent 审查纪律 +2 条**：假设性发现必须标验证状态（`已验证（文件:行号）` / `推断（验证路径）`——未验证前提禁止直接给可达性等级，实证：最坏假设直接标 L1，人工核实 5 行代码即证伪）；错误处理类发现先读被调方契约（网络包装 / 拦截器的异常语义——结构对 ≠ 触发对）
- **checklist +3 处**：边界 4 +「调试期空值先显式暴露不加兜底文案」（兜底把字段错位变成「显示为其他」更迷惑的现象，延迟定位）；Git 规范 8 +「多仓 git -C 绝对路径 + push 前 `git remote -v` 核对目标仓」（实战 7 踩：cwd 命令间重置，裸 push 把主仓推出新远端分支）；复刻专项 +「追到 logic / 消费端确认字段服务端返回 vs 前端加工 + 样例响应注释优先」（entity 有字段 ≠ 接口返回）
- **layout.md 列表项 key 节 +治点**：StatefulWidget 常驻不卸载时切换数据源——实例复用致 `initState` 只读一次，挂 `ValueKey(切换侧标识)` 强制重挂 + widget 测试锁死（实证 `29f490bae` 日期滚轮）
- **frontend agent 工作流程 +1 步**：「参考 XX 样式」类需求动手前先确认目标组件 / 截图（实证：仅凭描述 4 轮返工）；动态条数布局先问单条 / 溢出排布
- **双模板实施纪律（跨仓条）扩充**：+`git -C` 一律绝对路径（cd 落位不可信）+ push 前 remote -v 核对——与 checklist 8 同源，双侧同步

## 0.6.5 · 坑卡例行核验刷新——iOS 26.x 与 Impeller 双卡 2026-09-08 复核

- **Impeller 卡**：desktop 3.47 默认经官方 blog 复核属实；+桌面初期阵痛实证 [flutter#191860](https://github.com/flutter/flutter/issues/191860)（Windows 3.47.1 Impeller 启动显著慢于 Skia——桌面升 3.47 启动回归先核此 issue）；最后核验 09-05 → 09-08
- **iOS 26.x 卡**：状态维持「未修复·官方跟踪中」；+社区口径「Flutter 团队不打算在 Cupertino 组件实现 Liquid Glass（设计决策非待修 bug）」标注（以官方 issue 里程碑为准）；`cupertino_native_better` 社区方案活跃维持；最后核验 09-04 → 09-08

## 0.6.4 · saas-cashier 生产实证吸收批——列表 key 错乱 / SP 启动白屏 / 图片解码异常 / Impeller Vulkan 崩溃

> 用户指认三笔生产问题（列表错乱加 key / Windows SP 白屏 / 图片异常），经 saas-cashier 全史 git 检索钉出实证后吸收；点单页库存角标错乱未钉到单笔 commit，按同型多笔实证吸收并如实标注。

- **坑库 +1 卡（8/≤10）**：[三方依赖] shared_preferences 初始化时序与文件损坏——**启动白屏**（SP init 挂起 / 抛错阻塞首帧）/ Android `channel-error`（pigeon channel 窗口期）/ deviceId 种子漂移「升级换号」；规避四条：init 失败降级默认配置继续启动 / 种子数据冻结文件化 / 备份恢复机制 / Android 重试 ×3。实证 `af24988e3` / `4017e21c1` / `4df1c2702` / `f890669f2`
- **Impeller 卡 +实证追加**：saas-cashier `d1a86dc1d`——Android POS 定制设备 Vulkan GPU SIGSEGV，`EnableImpeller=false` 回退 Skia 修复；定制设备 GPU 驱动是回退开关的现实主战场
- **layout.md 新增「列表项 key」节**：库存 / 选中态串行显示的防（key 绑业务 id 禁下标）与治（配置驱动子组件挂 `ValueKey(配置值)` 强制重建）——实证 `31302e77d` / `0111c1d7d` / 点单页库存角标同型
- **checklist 组件节 +1 条**：列表项 key 绑业务 id（涉增删重排时查）
- **performance.md 崩溃钩子 +扩展点实证**：`7d1573584`（生产问题）——Windows 图片解码 `Codec failed` 异常经 `FlutterError.onError` 静默捕获记录，不拖垮 App

## 0.6.3 · 留池四项收口批——性能·CI·监控三空白补域 + 记忆库钩子推广 + plugin §八 实体化

> 0.6.2 留池四项按序收口三项；第四项（POS 垂直拆层 core+pos-vertical）系开源定位裁决项，另行方案。

- **skill 新增两域文件**（`references/performance.md`）：DevTools 双线程归因（UI/Raster 列说话，不凭感觉）/ 图片按显示尺寸解码（`cacheWidth`——低配收银机 OOM 头号常见根因，大图场景必传）/ 低配设备实操序 / `FlutterError.onError` + `PlatformDispatcher.onError` 双钩子与 sentry·crashlytics·自建选型 / 符号化与上报纪律；（`references/build-release.md`）：flavor 与 dart-define 选型（共存多包才上 flavor）/ keystore 与 iOS 证书纪律 / `--obfuscate --split-debug-info` 与 symbols 归档 / App 发布前检查 + pub 发布检查全表。SKILL.md 按域取用表 +2 行
- **checklist**：性能节 +2 条（大图按显示尺寸解码 / 全局错误钩子在位）；新增「构建 / 发布专项」条件条 3 项（symbols 归档+混淆首跑回归 / 密钥不入库+环境值集中 / 发布前检查表）
- **记忆库钩子推广（软约定显式化）**：frontend/backend/platform/i18n/error/reviewer 六 agents 统一 +「记忆库联动」行（涉业务规则 / 不变量 / 惯用模式先 Read `business-rules` / `INVARIANTS` / `patterns`——防重复发明与破坏不变量）；plan-reviewer 原有对读保留
- **plugin 模板 §八 实体化**：平台通道选型（结构化多端对等优先 **Pigeon**——两侧签名漂移的机械化方案）+ pub 发布检查 4 项（dry-run 零警告 / semver 与 CHANGELOG 一致 / Kotlin↔Swift 对等与 federated 同步 / example 可跑 + 净工程拉取实测）——原为纯占位

## 0.6.2 · 🟢 轻微项清池批 + 外部复核必修批——审查留池全清 + 语义闸上闸

> [审查 §四](docs/审查-2026-09-05-时效性与合适性.md) 🟢 9 条：2 条已随 0.5.0 瘦身消化，7 条本批清；随后外部复核（AI-coding 侧）抓出必修 3 + 漂移 2，同批修并上闸。**两轮审查留池至此全空。**

- **必修（外部复核，全部核验属实）**：checklist:78 触控目标错标纠正——`48dp（Material/Android 最低推荐）/ 44pt（Apple HIG·iOS）`（原 44×44 误标 Material）；frontend.md + app §十 两处 screenutil 正面残留清除（改指 §七 所选方案——0.6.2 首轮只修了 checklist 漏了执行面）；app 预设 B 裸 `hive` → `hive_ce`（0.5.1 栈审视刷了 A 漏了 B 的同文件矛盾）
- **漂移修复**：README 横幅 0.5.2 → 0.6.2（滞后三个版本）；help.md hooks ×2 → ×3（0.5.2 stop-reminder 漏计——自称权威全表恰最不该漂）
- **语义闸上闸（test-self 第 15 断言）**：README 横幅版本 ↔ plugin.json 分发版本一致 / help hooks 数 ↔ `hooks/*.py` 实际数一致 / 停更栈禁推（agents 无 screenutil 推荐、app 无未注记裸 hive）——把本轮 grep 级可检的漂移形态机械化看守；首跑即抓到自注记误伤，口径与 hive 一致排除「停更」注记行
- **过度绝对化软化**：layout.md「不要混用 Expanded/Flexible」→ 合法常见写法 + 明确弹性意图（外部复核 🟡 采纳项）；app 预设 C 手写序列化 + 边界注记（skill 默认生成不手写，此为克制依赖例外）
- **🟢 轻微项 7 条**：checklist:45 `Selector` 按方案对号（provider `Selector` / Riverpod `select`）｜agents ×7 `§2`→`§二（提交策略）` 15 处｜error.md「修复」→「诊断与修复建议」｜platform.md 职责 + Web｜app 预设 C 注「仅极端克制依赖时选」｜memory/reference-map 三行餐饮示例压一行占位｜AO 头注 +flutter_lints 大版本复查
- **使用面同步补遗（0.6.0 漏同步）**：README「装完必填三处」① 与 init 引导补**适配方案三选一 + 字体策略**（公共必选）；README 升级节新增**跨版本迁移要点表**（≤0.3→0.4 checklist 重排与记忆库接线 / 0.5→0.6 两必填环节补答 / 任意跨度 memory 只对照不强合）——老工程合并 `.new` 此前只有机械三步、无合并要点指引
- **留池（独立裁决项，非本批）**：性能 profiling / CI·发布（flavor·签名·混淆·符号化）/ 线上崩溃监控三领域空白；POS 垂直内容拆 core+pos-vertical（开源定位裁决）；patterns/INVARIANTS 机械钩子推广；plugin §八 Pigeon/发布检查补位

## 0.6.1 · 审查留池收尾批——S16 checklist 补节 + S9-S11 关闭核验

> 审查文档（[时效性与合适性审查](docs/审查-2026-09-05-时效性与合适性.md)）留池项收尾：S9-S16 全部关闭，仅余 🟢 轻微项随日常维护消化。

- **S16**：checklist Flutter 专项补「无障碍」（对比度 / Semantics / 字体放大可用性 / 触控目标 ≥44-48dp）与「性能」（builder 懒加载 / 重活不落 build+Isolate.run / controller 与订阅释放）两小节——审查侧对齐 skill A11Y 声称的覆盖面
- **S11**：theming.md 对比度行补「WCAG 2.2」版本号（数值与 2.1 相同，纯口径）
- **S9/S10/S15 关闭核验**（对新结构重跑，随本批记入审查文档头注）：`compute(` 零命中、审美说教零命中（均随 0.5.0 瘦身消化）；google_fonts 分场景已由 0.6.0 A5 落地
- **审查文档头注刷新**：S1-S16 处置状态全量回填（此前 S9-S11 待重跑 / S13-S16 待裁决）

## 0.6.0 · 吸收与模板演进批——适配三选一 + 字体策略 + IoT 抽层 + 订单折算吸收

> minor 口径：模板**交互环节**变更（§七新增必选环节、文件头规则语义反转），非纯内容增补——沿 0.5.0「模板交互变化升 minor」先例。依据链：[适配方案](docs/方案-2026-09-08-适配三选一与字体策略.md)（评审终裁：仅 app 落正文 / 三档断点）· [IoT 抽层方案](docs/方案-2026-09-08-IoT外设知识抽层.md) · [订单折算吸收方案](docs/吸收方案-2026-09-05-订单折算复盘.md)（落点按 0.5.2 基线修订）· [实施计划](docs/实施计划-2026-09-08-0.6.0批.md)（评审两意见轮全采纳）

- **模板（app）**：§七 新增「屏幕适配方案【复制后三选一】」——A1 弹性优先+断点（三档 Compact<600/Medium<840/Expanded≥840，默认推荐）/ A2 设计稿缩放（screenutil ~28 个月无稳定版注记）/ A3 自定义；8.1 新增「字体策略（公共·必选）」四要素（字体打包 / 统一注入点禁内联 TextStyle / fontFamilyFallback / 设备字形转图兜底）——实证源 saas-cashier 三笔（bbf976e42 Android Roboto 全字重 / 0508ac9b5 Windows 普惠体 / 656558508 内联绕过复发）+ flutter#154166/#145069
- **模板（plugin）**：§八 +1 行指针（适配/字体属 App 形态课题，example 按模板 §七对号）——不落正文，防孪生守护（`###` 子节不入节序号集，C4 实证）
- **文件头 S13 渗漏修正（双模板）**：@Author 五件套从模板正文撤下 →「默认跟随项目现状」——存量带头循既有格式（不含 @Email，作者权威在 git）、无头不加、惯例不一致问一次落附录；plugin:254 @Author 文档头同步改写
- **checklist（5 处）**：:47 改「按 §七 所选方案对号审查」（解 screenutil 点名与模板 A1 默认的 🔴 矛盾）；:80 「暗黑 / 按所选方案适配」；组件/视图节 +2 字体条（统一注入点 / 打包字体+fallback）；**R1-R3 半句并入**（金额展示铁律→9 ｜ 窄屏极值→4 ｜ iOS 生成文件 pathspec→8）+ **R4 新增「复刻 / 折算专项」条件条**（一个控件查两遍 + 像素对齐对象界定 + 6.2 复跑）+ 0.6.0 差集标注
- **skill（订单折算吸收 C1-C4）**：layout.md +2 bullet（Row 内 Text ellipsis 须先包 Flexible/Expanded；UAX#14 无断词点长串逐字符 Wrap）；platform-pitfalls.md +2 卡（三方依赖 Riverpod defunct 三板斧——区间如实标未查证；Flutter SDK 系统字体回退不可信）——坑库 5→7 卡仍 ≤10 配额
- **skill（IoT 抽层 S14）**：新建 `references/iot-devices.md`——backend 角色卡「设备通信铁律」7 条迁入升格 + 8 类设备分节框架（外设按通信方式 / 多屏 / 独立 App 指针节），实证 3 处（173e731c1 网口漏打连发间隔 / aaa9995fd 文字转图 / db82458e5 全半角）；backend.md 铁律节 → 一行指针；error.md:26 通用表述保留 + 指针半句；theming.md google_fonts 分场景（**离线/内网设备禁运行时拉取**，字体打包 assets）；SKILL.md 按域取用表 +1 行
- **fork-coverage**：§六节题改「边界记账」通用名 + 追加 0.6.0 行（S13 公司制度渗漏修正 / S14 IoT 抽层 / 本批通用机制不反哺 crules）

## 0.5.2 · 清池批——A3 Stop 读侧闭环 + D3 hooks 降级链 + D2 + E 组打磨

- **A3 漂移队列读侧闭环**（复核之复核 §5 自守卫版）：新 Stop hook [stop-reminder.py](hooks/stop-reminder.py)——队列非空经 `additionalContext` 注入事实提醒（模型可据此补索引），`stop_hook_active` 自守卫防连环续轮（官方：与 decision:block 共享同一套 8 次上限——勘A 修正落地），文案事实陈述 <10k 字符；fixture 五态全绿（无队列/空队列/连环轮抑制/非空出提醒/坏输入）入 test-self；hooks.json +Stop 事件——pending-updates 写侧（PostToolUse）与读侧（Stop）闭环合龙，**新会话生效**
- **D3 hooks 降级显式化**：install.sh 双级警告（无 python3=三 hooks 全失效 / 缺 fcntl=仅漂移队列降级）+ pending-updates.py fcntl 条件导入（Windows 降级无锁 `O_APPEND` 追加——单行写原子性兜底，从「装了白装」变「降级可用」）+ README 环境要求措辞对齐
- **D2 standalone 缓解**：两模板 §九 +「未装 superpowers/dart-flutter 时本节可忽略」（叠加协作非前置依赖）
- **E1** README 升级命令空匹配守护（原 zsh glob 失败静默产出 `SRC=/..`）；**E2** install.sh 复制/写入失败计错不虚报（汇总 +失败数，非零退出）；**E4** CI 链接检查步（坑卡出处 404/410/5xx 红，反爬与限流态放行；本地预跑 21 条全绿）；**E5** 七 agents 默认 `model` 档位（i18n=haiku / frontend·backend·platform·error=sonnet / reviewer·plan-reviewer=opus）+ Agent编排 维护注（档位名随可用模型演进）
- **池清空**：三审裁决表全回填；余 B2/B3（常驻瘦身+基线实测）按裁决等真实试点观测后单开

## 0.5.1 · 留池裁决批——C2 三坑卡 + C1 预设栈刷新 + D1 双模板孪生守护

- **C2 坑库补强**（skill `references/platform-pitfalls.md`）：Android 基线卡扩两区间——**16KB page size**（Play 期限原 2025-11 延至 **2027-02-01**；Flutter 3.38 起默认 `ndkVersion` = NDK r28，3.38 blog 原句验真）与 **edge-to-edge 强制**（targetSdk 35 强制 / Android 16 豁免移除 + Flutter `SystemUiMode` 破坏性变更——沿用旧 opt-out 在 Android 16+ 可能崩溃，复核之复核「新3」落实）；新增 **Impeller 换代卡**（iOS 唯一引擎无 Skia 回退 / Android API 29+ 默认 / desktop 自 3.47 默认 / Web 仍 Skia——官方 availability 节逐字核验）；全部官方出处 + 最后核验 2026-09-05
- **C1 预设栈刷新**（app §七）：存储 hive→`shared_preferences`/`drift`（原版停更 2022-06 注记 + `hive_ce` 延续）、国际化 easy_localization→官方 `gen-l10n`/`slang`（维护缓慢不推荐）、适配 screenutil→`MediaQuery`/断点优先（停更 2024-05 + 多端短板注记）——五包 pub.dev 版本 2026-09-05 逐一核验；§七 头部加「最后核验」字段，**栈审视义务**入 README 维护节（与坑节义务并列，每次 minor）
- **D1 双模板孪生守护**：test-self 新断言（节序号集 + §一/三/四/五/六 条数一致；§二 plugin 独有「发版特殊性」条目系合法不对称、豁免注明）——**装闸即抓真漂移**：plugin §四 缺「静默失败验到现象层」条目（example assets 热重载同样适用），同批补齐
- **裁决记录**（选项卡 2026-09-05）：C1/C2/D1 进本批；A3（Stop hook 读侧自守卫版）留池；B2/B3（常驻瘦身+基线实测）等真实试点观测后单开

## 0.5.0 · B1 skill 瘦身拆分（三审裁决 P1 首批·skill-creator 流程执行）

- **结构**：SKILL.md 850 行/39.2KB 单文件 → **薄索引 33 行/4.3KB** + `references/` 四域文件（design-doc 方案骨架+配图 / platform-pitfalls 坑库 / theming / layout），合计 249 行/17.8KB——**触发加载 −89%**（progressive disclosure 官方三級形态：metadata 常驻 / 触发载索引 / 按域 Read）；维护者侧内容（坑库维护义务）随迁出消费侧常驻
- **删除账本**：通用最佳实践段删除（基线导言 persona / Interaction Guidelines / Package Management / Code Quality / Dart & Flutter Best Practices / API Design / Architecture / Lint 样例 / State-Routing-Serialization-Logging 代码长例 / 视觉设计铺陈）——2026 年模型已内化 + 与 lint 基线、模板 §十重复；项目特有内容（骨架 / 坑库 / 配图 / 优先级与降级机制）全保留，恢复源 = git 历史
- **指针修复 4 处**：app/plugin 模板方案 Gate 行与 help.md 场景表直指 `references/design-doc.md`；app §8.1 风格细则指针改写（原目标内容已删——通用归 lint 基线硬拦，细节按需查 theming/layout）
- **A/B 评测**（skill-creator 流程，3 场景 × 新旧版子代理对照）：**13 断言双绿**（内容可达性无损、按域路由三题全对、浓缩版 theming.md 扛住 lerp/copyWith 全例复用）+ 新版耗时均值 **−16.7%**（290.3/141.8/452.9 vs 330.2/243.1/489.7s）；断言全程序化判定——完整记录见 [docs/评测-2026-09-05-skill瘦身AB对照.md](docs/评测-2026-09-05-skill瘦身AB对照.md)
- **description 触发优化（不采纳·如实记载）**：20 条应触/不应触查询经 skill-creator run_loop 跑 3/5 轮即止损终止——三轮 Test recall 全钉 0–8% 地板（precision 100% 系「几乎不触发」另一面），**判定为评测查询设计与参考库型 skill 的结构性不适配**（文档化现象：模型对一行问答型查询凭内化知识直答、不咨询 skill——A/B 评测 6 子代理在「查规范」语境下均正确读取本 skill，真实消费触发正常），候选 description 全部从噪声中选出故不采纳、保留现版；教训：触发评估的应触查询须为**多步实质任务**。完整记录见 [评测文档 §5](docs/评测-2026-09-05-skill瘦身AB对照.md)

## 0.4.1 · 三审裁决 P0 批——lint 死配置修复 + 记忆库接线 + retrofit 主次排序

> 依据链：[外审](docs/外审-2026-09-04-0.4.0整体评审与优化方向.md) → [复核](docs/复核-2026-09-04-外审0.4.0逐条核实与勘误.md) → [复核之复核](docs/复核之复核-2026-09-05-复核文档勘误.md)（三审全实测/官方文档双源核验）；裁决记录见外审 §7

- **A1**：`analysis_options.yaml` 删两行死配置——`cancelled_token_use`（analyzer 诊断名非 lint 规则，3.5/3.47.2 双验 undefined_lint）与 `public_member_api_docs: false`（flutter_lints 未启用的空 disable，map 形态条目且扰动列表解析致报警行号偏移），意图注释保留（CancelToken 纪律落点 checklist 异步纪律节，custom_lint 二期候选）；test-self 增「AO 内容过真 analyzer 零 warning」断言（本机无 dart 时 SKIP）+ ci.yml 增 setup-dart 步硬拦——0.2.3 F2「真样本」教训对 AO **内容侧**补完闭环
- **A2**：两 CLAUDE.md 模板 §十二 +「记忆库接线」节——`@.claude/memory/NAVIGATION.md` 启动内联（最小集；MAINTENANCE/patterns/INVARIANTS 等保持涉域前 Read，**不整库 @import**——prose 引用不加载，经官方文档确证）；init 步骤4 +接线确认项（NAVIGATION 占位表裁剪联动）；memory README / 记忆库体系 twin 表「加载时机」列对齐事实；记忆库体系「会话开始时加载」示例块改 @ 语法——0.4.0 记忆体系从「装而不用」变真加载
- **E3**：flutter-rules description「重叠处以 skill 为准」→「以 dart-flutter skills 为准」（指代消歧）
- **R2**：app §七 预设 A 网络行改主次排序——`dio` + `interceptors` 默认，接口规模大可加 `retrofit`（声明式 codegen 层，与 Dio 非互斥；复核勘4 确证其活跃维护）
- **环境坑修复（bash 5.3，验证阻断）**：`set -u` 下 `$var` 紧邻多字节字符（中文标点）时 bash 5.3+ 会把多字节首字节吸入变量名致 **unbound 中止**（brew 2026-09-05 升级 bash 5.3.15 后实测炸出——install.sh 汇总行中止于文件已写完之后、exit 127；CI ubuntu bash 5.2 未触发故此前无感）——install / check-imports / test-self 共 12 处全部改 `${var}` 花括号隔离（LC_ALL=C 与花括号均免疫；v59 BSD grep 环境坑同款教训，注记于 test-self 头部）
- **裁决状态**：B1（skill 瘦身拆分·默认中档）已裁走官方 skill-creator 执行，P1 启动；B2/B3/C1 余项/C2/D1/A3/D2/D3/E1-E5 留池待裁（外审 §7 表）

## 0.4.0 · 易用性与知识沉淀体系（设计方案 v2.1 落地）

- **命令 ×3 新增**：`/help`（场景使用地图）/ `/distill`（沉淀定稿闸——五问 / 闸表 / 三操作 / 档位 / 坑卡归属）/ `/diagram`（存量文档补图，常驻文件拒加图）——与 init / update-memory 组成 5 命令面板
- **memory 模板 6 → 8**：`reference-map.md`（分域参考系，只存指针不存结论）+ `platform-pitfalls.md`（支持矩阵【装完必填·第三处】+ 结构化坑卡带**归属**字段：OS 平台 / Flutter SDK / 三方依赖 / 未定性）；NAVIGATION / MAINTENANCE / memory README / 记忆库体系 twin 表同步 +2
- **init 必填两处 → 三处**：+支持矩阵**三段式自动初稿**（①机械读：平台目录 + minSdk + Podfile，kts 变体 / 失败保留占位符并报告 → ②人核对 → ③人补实测上限）；install.sh「下一步」echo 同步
- **两 CLAUDE.md 模板**各四处改：完成定义 +review 结论与沉淀候选判据 / 方案 Gate +骨架指针行 / 依赖红线 +坑库×矩阵步 / §三 +收尾时序注（两模板同源对照改）
- **脚本**：check-imports +memory 演进提示（源侧新增 + git 两版本 diff，不做目标全量比对）；test-self 扩三断言（8 模板 / 三处必填 / twin 一致性）；.gitignore 补 `__pycache__/`
- **skill**（批 2）：方案骨架全文（裁剪档位 / 图型 / Gate 映射 / 行业参考槽位 / 6.2 自测用例表）+ 配图约定 + 平台坑节**预置首批**（三归属分节：Win7 permission_handler / iOS 26.x / Android 基线一卡多区间，每条带出处与最后核验；[调研记录](docs/调研-2026-09-04-平台坑预置首批.md) 15 链接抽查属实，查不到出处的按未查证不预置）+ description 补「写设计方案」触发词
- **review 增强**（批 2）：checklist 差集标注增补（吞异常形态学 / 资损红线新增为条目 9 / 关键节点日志 / 敏感交叉 / 边界 Flutter 化 / 兼容性硬判据 / 机械项归位）；审查纪律 +「review 主工位与范围」节；工程化流程 §5 时序对齐（复验 = 重跑构建 + 重审）+ §7 模板并入 Review 结论位 / 沉淀候选位
- **README 使用面重写**（批 3）：5 命令面板 + 场景地图（与 `/help` 同源，双侧同步义务）+ 收尾时序 sequence 图；落位物表 memory 6→8（点名 `reference-map` / `platform-pitfalls`）；必填两处→三处（+支持矩阵三段式）；维护节 + skill 坑节维护义务 + 沉淀闸蜜月期说明
- **示范与记账**（批 3）：进阶配图示范两处（方案评审闭环 flowchart / Agent编排 sequenceDiagram）；[fork-coverage §六](docs/fork-coverage.md) 0.4.0 边界记账（通用机制不反哺母版 / 技术栈相关只进本包）

## 0.3.0 · 跟随 crules v77——外部行为准则残差 3 条镜像

- **`app/CLAUDE.md` / `plugin/CLAUDE.md` 实施纪律各 +3 条**（跟/不跟查表：跟则 bump minor）：**假设显式化**（开工前列关键假设标注已核实/推断）/ **清理自身孤儿**（自身改动产生的失效 import/变量/函数同批清，预存死代码只报告）/ **更简方案推回**（更简路径提出而非擅自改，采纳归需求方）——措辞按本包精简风格镜像，源为 crules 母版 v77（karpathy-guidelines 残差吸收，整包不吸收理由见母版 CHANGELOG v77）

## 0.2.4 · README 使用文档补全发版

- **README「工程接入与升级」节新增**：落位物表（AO 三态 / memory 永不覆盖）/ agents 不复制说明 / 装完必填两处（§七三选一 + §十二附录）/ 项目模板升级三步命令（check-imports → install --force 出 .new 伴生 → 人工合并）/ `/crules-flutter:update-memory` 兜底——README 使用面与 0.2.2/0.2.3 实际行为对齐（此前落后两版）；状态行刷至外审四轮收口（f8d3084）

## 0.2.3 · 三轮外审 F1/F2 收口

- **F1** AO 判定重写：剥注释签名（`grep -vE '^[[:space:]]*#|空行'` 后非空行 ⊆ {flutter_lints include / linter: / rules:}，**白名单允许缩进**）——原 ≤6 行判定对真机 flutter create 的 28 行注释版无效，UPGRADE 曾是死代码（外审真机实测坐实）；修复过程自身再犯两小错（if/elif 拧反、白名单漏缩进的 `  rules:`），真机 fixture 三场景首验当场抓当场修
- **F2** 真机 28 行脚手架产物签入 `scripts/testdata/scaffold-analysis_options.yaml` + **test-self 扩至 8 断言**（+真脚手架→UPGRADE / 自定义→SIDE-CAR / force→memory KEEP+.new）——手工 E2E 固化回归，「测过了还要确认测的是真样本」教训落机制

## 0.2.2 · 二轮外审 N1-N6 收口 + 消费态首验补课

- **N1** `commands/init.md` 源定位改 **glob 自发现**（cache 最大版本）——`${CLAUDE_PLUGIN_ROOT}` 在 Bash 工具环境为空（实测），cache 用户原走死路
- **N2+N5** `install.sh` 三态写入：--force 改**安全升级**（模板类出 `.new` 伴生待人/AI 合并，不原地打爆已填内容）；**memory/ 永不覆盖**（含 --force）——制度资产语义
- **N3** analysis_options 智能落位：flutter create 脚手架特征（≤6 行纯 include）→ 升级替换留 `.scaffold-bak`；有自定义 → 落 `.crules-flutter.yaml` 伴生提示合并；头注修错（flutter_lints 须在 dev_dependencies，缺依赖 analyzer 静默跳过 include）
- **N4/N6** SKILL 第四处 Built-in 残留改写；memory 两文件裸命令改 `/crules-flutter:update-memory`
- **消费态首验补课**（外审总评采纳）：模拟 flutter create 壳从 cache/工作区真跑——首验当场再抓一个方法错：**cache 里是旧版脚本**（未 bump 先验 cache = 验旧不验新，v31 纪律重犯）；工作区版三场景全绿（脚手架 UPGRADE / force 出 .new 且 memory KEEP / 自定义 lint SIDE-CAR）

## 0.2.1 · 外审 #5——commands 化

- **`commands/init.md` 新增**（plugin 分发 → `/crules-flutter:init`）：分流（新项目 / 老项目无戳不自动装 / 有戳版本差）→ 跑 install.sh 机械安装 → 引导 §七必填与 §十二附录——消灭手动 install 步骤（外审 #5 推荐项）
- **`commands/update-memory.md` 新增**（→ `/crules-flutter:update-memory`）：记忆库全量刷新兜底命令（此前 #4 改为手动兜底的命令化回归）
- README「怎么用」②步改命令入口

## 0.2.0 · 外审 P1 收口轮（五项）

- **#2** `release.sh draft` 修复：CHANGELOG 路径 docs/→根 + 段头日期式→版本式（按顶部版本对应发版 commit 取边界，无锚 fallback 最近 10 条）；test-self 补 draft 断言（外审②）
- **#4** 失效引用清零：5 处「模板包同级 ../flutter/」→ 项目根 checklist.md；§十二两模板补 checklist 行；update-memory 指名改手动兜底；memory 两文件 crules 措辞；README 状态刷新（外审④）
- **#6** **agents 分发改 plugin-only**：install.sh 停止复制 agents（plugin 自动挂载 7 角色——消灭双通道 AUTO-SYNC 孪生，外审⑤），实测项目内无 agents 目录
- **#3** SKILL.md 预设适配：头部「与项目 §七/§八 冲突以项目模板为准」+ State Management / Navigation / 反三方默认三处矛盾改写 + 双 H1 修复 + MCP 工具降级注（外审③⑨）
- **#7** **lint 基线首期**：`analysis_options.yaml` 模板（flutter_lints + strict 三开关 + 规则对应 checklist 条目标注），install.sh 复制（项目已有则保留）；custom_lint 深度工具化留二期（外审⑧）

## 0.1.4 · CI 首跑红修复——同步比对剥戳逻辑

- **`ci.yml` 同步比对步**：剥戳从 `tail -n +2`（从第2行起=保留戳，错位）改 `sed '2d'`（删第2行戳，shebang 后）——CI 首跑红抓出的实现 bug，本地以 `git show origin/main` 模拟比对验证一致（v48「CI 首跑红→根因修复」同款先例）

## 0.1.3 · 批 3a 修复——skill 目录归位

- **`skills/flutter-rules/`**：SKILL.md 从 `.claude/skills/`（项目级约定）移至 plugin 根级 `skills/`（plugin 组件约定）——批 3a 消费侧首验抓出 Skills(0) 未挂载，plugin details 复验修复

## 0.1.2 · 批 3a——saas_pos 实战规范上移（§八两小节落地）

- **`app/CLAUDE.md` §八**：8.1 全栈通用（多 package assets 加载 / 文件头注释 / Import 排序——代码风格细则归 flutter-rules skill 不双份）+ 8.2 预设 A 特有（Notifier 模式 / Provider 就近组织 / ConsumerWidget 强制禁传 ref / autoDispose 策略——标「选 A 时生效」）；适用面判定 9 条入 [fork-coverage §三](docs/fork-coverage.md)；项目架构与业务域知识不上移（批 3b 下沉消费工程记忆库）

> 记能力级变化；fork 基线 crules `v74-fork-base`（ea4d25c）。版本口径：semver=分发版本，批号为实施批次。

## 0.1.0 · 批 2 收官（内容整合完成）

- **两模板本尊化**（批 2a）：app/plugin CLAUDE.md 重组为十二节——通用协作层（红线/提交/双 Gate/验证证据/完成定义/后台 diff）fork 自基线并修复旧孪生漂移（v50 安全红线、v51 提交语义分离等 6+ 条）；§八专项规范立占位（批 3 上移）；覆盖 diff 验收 [docs/fork-coverage.md](docs/fork-coverage.md)（全量 78% / 裁剪 18% 已归位进阶 / 场景替换 4%，无静默丢失）
- **知识层**（批 2b）：checklist 自持（通用 8 大类 + Flutter 专项）；进阶 5 篇 fork（链接重定位）；memory 6 模板 + agents 通用 3 角色落位（共 7 角色）；rules.md skill 化（flutter-rules，Testing 节去重留指针）
- **基建层**（批 2c）：hooks 三件 fork + `SYNCED-FROM: crules@ea4d25c` 戳；CI 四步含 **deny-list 同步比对**（crules 单一权威机械化看守）；scripts 三件（install --app/--plugin + 戳 + 护栏 / check-imports / release）；test-self 四断言（含 deny-list 幂等）

## 0.0.1 · 批 1（骨架）

- 建仓 + plugin 骨架 + README（种子库关系 / 共存指引 / 停用恢复）

## 0.1.1 · 批 2c 复盘整合

- **`app/CLAUDE.md` / `plugin/CLAUDE.md` 实施纪律各 +1 条**：「跨仓/跨目录操作一律绝对路径（cwd 会话间重置，实战 6 踩曾污染母版）+ 特殊字面串文件用专用写工具（防 deny-list 误拦）+ 跨仓收尾 git status 验零污染」——源：docs/复盘-2026-08-27-批2c双坑.md（1.0.14 轮次化删除，git 史可寻回）
