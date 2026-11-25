# 评审-plan-先查后写（v1–v4 四轮全文）

> **落盘纪律**：四轮评审报告由 plan-reviewer 输出、主控**原样落盘**（不修改 / 不过滤——`agents/plan-reviewer.md:51`）；第 1–2 轮原文系子代理回传帧内报告，主控仅剥离会话帧壳与帧缩进，正文逐字照录。逐条回应与消解落点见 [方案-先查后写-2026-11-24.md](方案-先查后写-2026-11-24.md) §0 四表。
> **轮次**：第 1 轮 2026-11-24（v1 全文级，🟡6＋绿 4，10 条全采纳）→ 第 2 轮 2026-11-25（v2 diff 级，黄 6＋绿 7 全处置）→ 第 3 轮 2026-11-25（v3 diff 级，红 0／黄 3／绿 7）→ 第 4 轮 2026-11-25（v4 diff 级，**需求方显式授权超轮**〔仓内闭环 max 3 轮〕，红 0／黄 0／绿 8 无须消解）。
> **记法注记**：第 1 轮原文用 🟡／🟢 记级；自第 2 轮起按「评审等级用文字」惯例改红／黄／绿——原文照录不改。

## 第 1 轮（v1 全文级 · 2026-11-24 · 结论：技术通过，🟡1–6 消解后再落终裁）

> **主控回应**：10 条全采纳。1–3 落 v2（dart-flutter 口径改可复现／重叠面评估后**主线改 C3+C6**——常驻红线＋预算上调方案作废〔需求方裁决〕／rootUri 三路＋跨平台）；4–5 随主线消解（预算零改动）；6 措辞改；7–10 各落点。原文照录如下。

### 原文

## 评审纪律声明

只评审、不修改被评审方案；只输出建议／发现；全程只用只读工具（Read／Grep／Glob），未调用任何修改工具。评审对象＝`/tmp/plan-flutter-fact-check-2026-11-24.md` 全文；方案内仓内引用已逐个定点开件核对，外部路径按切片包抽读。

**已核通过项（正面结论，不计发现）**：
- 引用真实性逐条命中——`canonical/redline-evidence.md:2-3` 两条证据红线；`app/CLAUDE.md:20-24`／`plugin/CLAUDE.md:20-24` redline-evidence 围栏；两模板 `:42`「外部依赖与网络操作先确认」；`app/CLAUDE.md:4` 三方分工句；`scripts/render-blocks.py:18` 用法、`:49` redline-evidence 登记、`:102-117` 围栏替换+守卫②、`:139-146` 正文下限守卫；`scripts/test-self.sh:216-229` 预算闸、`:219-222`「超线须显式裁」原文、`:271-317` 孪生同文块闸、`:301-310` 锚串循环；`.claude-plugin/plugin.json`／`marketplace.json` 1.3.13；`README.md:6` 1.3.13 横幅；`CHANGELOG.md:6` 当前形态 1.3.13；`skills/flutter-rules/SKILL.md:105` 通用段已删说明；`docs/方案-质量闸通电-2026-11-18.md:61` P6；`commands/init.md:122-124`「缺则补、永不覆盖」。
- 数字实测复核——关键词组在 `app/`／`plugin/`／`canonical/` 命中 0，全仓 86 行／22 文件（与方案一致）；`skills/flutter-rules/references/platform-pitfalls.md` 归属行恰好 22；`~/.pub-cache/hosted/pub.flutter-io.cn/` 存在且含 `lib/`+`CHANGELOG`+`README`+`example`（riverpod-2.6.1 等）；常驻字数 16913/16179 与分解式（14277+1971+665／13543+1971+665）自洽。
- 声明面四清单齐整——scope block 为逐文件粒度、无裸 `**`；影响面六行处置态封闭＋兼容性四面展开；UI 视觉规格 N/A（非 UI 任务）；批次卡四必答（独立判据／依赖方向／机械验证面／baseline 口径）全给。
- 范围控制——无夹带；D3 增量列为条件件、D4 预算上调列为阻塞待裁，均显式化未静默。

| # | 发现 | 严重程度 | 原因 / 证据 | 建议（只建议，不改） |
|---|------|---------|------------|-------------------|
| 1 | dart-flutter 官方插件「27 个 skill 5113 行」不可复现，「4 处」计数缺原测量命令 | 🟡 | 对 1.0.7 实装面实测：`~/.claude/plugins/cache/dart-flutter/dart-flutter/1.0.7/skills/` 下 `SKILL.md` 25 个、4923 行（含 `.agents` 6 个共 31；`skills/` 全部 32 文件 5437 行），均不等 27／5113。「3 文件」可由 pub.dev/源码命中佐证（`dart-use-ffigen/SKILL.md:81`、`dart-setup-ffi-assets/SKILL.md:76`、`dart-resolve-package-conflicts/SKILL.md:108`），「4 处」口径未给。方案 §3 行/§3.5 行自标「⚠️ 测量事实」但未附命令 | 附测量命令+原始输出（本仓 redline-evidence 要求数字出自本会话实读）；或改可复现口径。同时把「其无此条款」收窄为「读**已装版本源码**」——dart-flutter 确有 pub.dev 引用，但属「查版本/取依赖」，与新条「必要时再查官方文档」相容、不构成冲突 |
| 2 | 新红线与既有条款重叠面未评估，「零命中→需新增」判定过宽 | 🟡 | `app/CLAUDE.md:17`「必须先读后改」、`:19`「不得虚构…接口、参数」、redline-evidence「结论须出自实读取/运行」、`app:128`／`plugin:121`「参照物优先…读基准源码」、`skills/parity-rewrite/SKILL.md:75`「禁按模型形状反推手造」、`references/network-comms.md:21`「回调接线对着库源码核」均已部分覆盖。「零命中」系子串法（"读指定基准源码"不含"读源码"子串故漏）。§4.2「已排除」仅比对 `:42`，未比对上述六处 | 补一段「相对上述条款的增量＝从"特定任务/领域"泛化到"任意三方包日常调用"＋给出 pub-cache 定位」；或评估把 pub-cache 指针并入既有证据条/`:42` 而非新增第 3 条红线，交需求方裁 |
| 3 | 规则文本硬编码 `~/.pub-cache`，跨平台与 git/path 依赖不成立 | 🟡 | Windows 默认 `%LOCALAPPDATA%\Pub\Cache`、自定义 `PUB_CACHE`、`git:`／`path:` 覆盖依赖源码不在 pub-cache。本仓明确支持 Windows（`test-self.sh` cp950 注记、`hooks/deny-list.ps1`） | 改「本机已装版本包源码与 CHANGELOG（默认 pub cache，路径随平台/`PUB_CACHE`；git/path 依赖读其实际目录）」 |
| 4 | 预算上限数字的改动面不全，回显会误导 | 🟡 | `scripts/test-self.sh` 上限值出现在 3 行 6 处：`:225` 判据、`:226` PASS echo、`:228` FAIL echo。方案 D5 写「（:225）」、§5 写「预算上限两处数字改」；只改判据会让 PASS/FAIL 仍打印旧值 17000/16200，与 AC3「实测值」核验相矛盾 | 明确 3 行 6 处同改（判据＋两处回显文案） |
| 5 | 预算标定先于实测，plugin 余量仅约 20 字，AC3 有失败风险 | 🟡 | plugin 16179＋新增(≈151，含换行 1)≈16330 vs 新上限 16350，余约 20；app 余约 36。D1 给「144～150」但事实清单注「144（未含「**必须**」）」，实测口径模糊；若渲染实长>~170 则 AC3 直接不成立 | 先实测渲染后字数，再定上限＝旧值＋实测Δ＋小额裕量；或至少明示 plugin ~20 字余量为已知（后续任一增改即按既有「显式裁」再触闸） |
| 6 | AC1「恰好 1 次」与拟用机械机制不匹配 | 🟡 | 拟加锚串守卫是「围栏内子串存在」（`test-self.sh:295-300` `a in m.group(1)`），不校验出现次数。「恰好 1 次」实由 render 守卫①（(id,文件)恰 1 对围栏）+守卫②（内容==canonical）间接保证 | 据实改写 AC1 措辞（「红线区内恰 1 对围栏且内容==canonical，锚串在位」），避免「锚串命中」冒充「恰好 1 次」 |
| 7 | D6 引证错位（AO 专属裁决被用作宪法不覆盖存量的通据） | 🟢 | `docs/方案-质量闸通电-2026-11-18.md:61` P6 是「**AO 建议稿**…缺则补永不覆盖」；「宪法副本不覆盖存量」更直接依据是 `commands/init.md:122-124`「缺则补、永不覆盖（与 memory 种子同语义）」 | 改指 `commands/init.md` 或双注；结论本身成立，仅引证面收窄 |
| 8 | 坑库归因分布口径未注（混合归属计法） | 🟢 | 22 卡验证（`归属`=22），10+6+4+2+0=22 自洽；但 `platform-pitfalls.md:99`（SDK×OS）、`:126`（SDK×OS）双归属卡计入 SDK 的规则未写明 | 注明「混合归属计主责方」一行，防后续计数争议 |
| 9 | 自测 U3/U4 篡改还原方式未写（撞「篡改自测禁 git 回滚」纪律） | 🟢 | U3/U4 需删锚串/改回上限使闸变红再恢复；本仓纪律禁以 `git` 回滚做篡改自测 | 注明用原值/临时副本还原，不用 `git checkout` |
| 10 | AC5 tag 腿时点 | 🟢 | 版本一致闸 tag 腿或需「最新 tag 或紧后一版」容忍（`README.md:150`）；tag v1.3.14 需收口时显式推送指令，非实施者自动动作 | 注明 AC5 于收口批执行、依赖「紧后一版」容忍或 tag 已推送 |

**关于范围**：scope block 含条件件 `skills/flutter-rules/SKILL.md :: M`（D3 待裁）。经查 `scripts/scope-audit.py:180-219` 只遍历 git 实际变化（判「清单外改存量/扩容候选」与 action 不符提示），不校验「声明但未变」——D3 若未裁则该文件不入 hits、不报错，条件件对 scope-audit 无害，可保留。

**§3.5 判定**：立论「不依赖行业对标、只依本仓两次返工实证（U7／1.3.13）」成立，且同行基线与「防凭记忆」两行均按仓内既有 `skills/flutter-rules/references/design-doc.md:39`「查不到标『未查证·凭记忆』」纪律标 ⚠️ 且明示不据此立论，分级基本合规；唯一软点是第 1 行的「测量事实」不可复现。

整体结论：技术通过（无 🔴；建议 🟡1–6 消解后再落 D1/D4 终裁）。

## 第 2 轮（v2 复审 diff 级 · 2026-11-25 · 结论：技术通过无红，黄 1–6 须消解）

> **主控回应**：黄 1–6 全消解（1 独立成节；2 锚补直查子句＋U2c；3 独占串＋链接形＋U2 拆发；4 机制改述三处＋docs 入扫后果承接；5 §4.5 第 8 项「逐行带证据」＋AC8＋U6；6 对照表＋评审原文随包）；绿 7–13 全处置（13 采纳「:18 半句指针」）。原文照录如下。

### 原文

# 方案评审：版本与三方包事实先查后写 v2（第 2 轮·diff 级）

> **评审纪律**：只评审、不修改被评审方案；只输出建议／发现；未调用任何修改工具（本轮仅 Read／Glob／Grep）。结论作为返回值交主控原样落盘。
> **被审成品**：`/tmp/plan-flutter-fact-check-2026-11-24-v2.md`；**v1 对照件**：`/tmp/plan-flutter-fact-check-2026-11-24.md`；**仓根**：`/Users/chuxiong/Downloads/ai-code/flutter`（HEAD 296eb91，工作区净）。下文 `路径:行号` 均相对仓根，绝对路径清单见文末。
> **本轮范围**：只评 v1→v2 改动面、10 条消解是否落实、v2 新增引用真实性；未变部分不重验。
> **等级写法**：按仓内「评审等级用文字」惯例——红＝阻断／黄＝须消解／绿＝建议。
> **落盘提示**：本文将存入 `docs/`，而 check-references 的 links 面扫全仓 md（见 #4），故全文不使用链接语法，路径示例一律行内代码。

## 一、评审表

| # | 发现 | 严重程度 | 原因 / 证据 | 建议（只建议，不改） |
|---|------|---------|------------|-------------------|
| 1 | D3 落位有逻辑缺口：新条挂在「依赖变更专项」条件条下，但该节头把创作期任务排除在外，「只补创作期触发」落空 | 黄 | `checklist.md:98` 节头原文「依赖变更专项（条件条——涉新增 / 升级第三方包时查，其余任务跳过）」。v2 §4.3 新条的触发是「写第三方包调用（非基础用法）或用版本相关特性前」，两个场景都不以新增／升级依赖为前提，按节头规则恰属「其余任务跳过」。新条唯一能被节头放行的场景是升级，而草稿偏偏没写「升级后报错」。另：节名「依赖变更」与新条「调用核验」类目不符 | 二选一：改节头条件为「涉新增 / 升级 / 调用第三方包（非基础用法）或用版本相关特性时查」（代价：既有四条被带进纯调用任务的检查面，多为一句话不适用）；或新条独立成节、自带条件条头。产出者定；改后 §5「checklist 依赖变更专项」一行同步 |
| 2 | AC3 没有能红的判据：checklist +1 条在全方案零看守，所引指针限定闸根本不扫 checklist.md | 黄 | `test-self.sh:515` 该闸扫描面只有 skills 与 进阶 两目录，匹配的是行内代码形态的 checklist 文件名；checklist.md 自身不在面内。D4 锚写「表行＋触发词＋文件在场」三件，无一子句落在 checklist.md。新条整条删掉，该闸仍绿，AC3 照样成立；§6.2 也无对应负证据——不能失败的检查组不成验证计划 | 锚补一子句直查 checklist.md 新条（文件名串即可；若坚持限定语再并「插件 cache」），§6.2 加一发「删该条→锚红」。草稿指针「查法见插件 cache checklist.md 同源的 skill references/…」是为过一个不管此文件的闸而生的绕口写法，建议直写「查法见 flutter-rules skill references/dependency-verification.md」 |
| 3 | SKILL.md 两处挂载的可红性没锁：锚串未指定，照「:101 形」写则 U2 红不了；表行草稿用裸路径，AC2 的「表行→文件互链」边无从失败 | 黄 | `test-self.sh:101` 对 SKILL.md 的两条 grep（flavors-channels、马甲包）在 frontmatter 句（`SKILL.md:3`）与表行（`:32`）两处都命中，只删其一锚仍绿——先例自带的弱点，照搬即继承。v2 §4.2 两处草稿都含 dependency-verification，U2「临时删 SKILL 表行→新挂载锚 FAIL」按此形不会发生。另：`SKILL.md:17-33` 既有 16 行的 Read 列全是链接形态（`[references/x.md](references/x.md)`），§4.2 草稿行是裸路径；links 面只认链接语法，这条边零看守 | 锚写明两处各自的独占串——按现草稿 frontmatter 句独占「三方包版本核验」、表行独占「定位已装版本」（依 SKILL.md 前 60 行成立，实施时全文 grep 复核）；U2 拆两发（删表行、删 frontmatter 句各红一次）。表行草稿改链接形态，方案稿内保持行内代码包裹 |
| 4 | 引证错位：「check-references links 面自动覆盖新文件」的机制引错，共三处（D4、§3 链接闸行、§5 check-references 行），并漏掉一个真实后果 | 黄 | `check-references.py:32-38` 的 DEFAULT_FACE_GLOBS 只在 entries 模式经 `expand_faces` 取面（`:119-125`）；links 模式走 `check_links`→`md_files()` 全仓遍历（`:40-45`、`:113-114`），不读该 glob。「新文件零登记入扫」结论成立，理由不成立；切片包「已核实事实清单」同一条同样写错。被漏掉的后果：links 面连 docs 目录一起扫（排除目录仅 .git、__pycache__、node_modules、.claude、.superpowers，`:29`）——本批新增的方案定稿与评审全文两份 docs 自动入死链面，文内任何链接语法的示例若不在行内代码或围栏内即红（相对路径按 docs 目录解析） | 三处改述为「links 面＝全仓 md 遍历（md_files），新文件零登记入扫；:36 glob 管的是 entries 面，新文件同时入 entries 面（正文写『X skill』须在册或在白名单）」。§4.5 加「两份 docs 落盘后复跑 links」；评审文档与逐条回应里的链接形态示例一律包行内代码 |
| 5 | 参考文件的内容事实在验证面里零核对项——与方案自身立论相矛盾 | 黄 | §4.1 骨架的承重内容是一组会变的事实（package_config 的 rootUri、各平台 pub cache 默认路径、PUB_CACHE、镜像目录名、fvm 生效版确认）。§4.5 七项与 §6.2 U1–U5 只验「文件在位、链接不断、锚能红」，没有一项验「文件里写的对不对」。本方案要解决的正是「会变的事实被凭记忆作答」；新件若照骨架凭记忆落笔，等于用同一个病去治这个病。本机无 Windows 实机（`test-self.sh:81` 注），Windows 路径一项天然不可本机实测。仓内既有纪律：参考条目须带查证出处，查不到标未查证（`references/design-doc.md:39`，v2 自己也引了这一行） | §4.5 加一项「文件内容事实逐行带证据」：本机可实测的贴命令与输出（pub cache 目录、任取一个真实工程读 package_config 的 rootUri、PUB_CACHE 现值）；本机不可实测的标出处或「未实测」，不裸写 |
| 6 | 消解可追溯性缺口：v2 文首没有「10 条发现的消解落点对照」，发现 4–7 在 v2 内零标记 | 黄 | v2 第 3、5 行只有状态句与主线变更句，无对照表（派发说明里写的「文首含对照」与成品不符）。全文可辨的落点标记只有 6 条：发现 1（§3 dart-flutter 行）、2（第 5 行主线变更依据）、3（§1 盲区三扫）、8（§3 坑库行）、9（§4.5 第 4 项）、10（§4.5 第 5 项）。发现 4–7 无任何标记，也无法从 v2 文内指认对应改动。第 1 轮评审原文不在切片包、/tmp 下只有两份方案稿；裁决选项卡（C3、C6 定义）原文同样不在包。这不是判定「未落实」，是本轮核不了 | v2 文首补 10 行对照（发现号→落点节行→状态）；或把第 1 轮评审原文随包定点补核 4–7。范围对照裁决原文一项同受此限 |
| 7 | D6 引证错位：所引「缺则补、永不覆盖」说的是 AO 建议稿，不是宪法副本 | 绿 | `commands/init.md:122-124` 在「AO 建议稿」节，对象是 analysis-options.suggested.yaml，括注「与 memory 种子同语义」。宪法副本的语义在 `:44-51`：不存在则拷；已存在且不一致＝「曾被手改或待升级」，diff 呈报、需求方确认后另行 cp 覆盖——是不静默覆盖，不是永不覆盖，存在人工确认的升级路。「永不覆盖」是 memory 种子（`:56`）。结论（不自动更新／存量本批不处理）不受影响；且 v2 宪法零改动，此半句在 v2 已是 v1 残留 | 改引 `commands/init.md:44-51` 并改措辞；或直接删此半句 |
| 8 | §8「与 checklist:101 被读成重复」的处置指向一个不存在的对象 | 绿 | 处置写「文件内『与坑库分工』节＋条目措辞锁定创作期触发」；§4.1 的「与坑库分工」讲的是坑库，骨架内没有一句讲与 checklist 依赖变更专项的分工 | 参考文件补一句（升级流程照 checklist 依赖变更专项；本件管写调用前核已装版本 API），或把风险行指向 §5 的那行分工说明 |
| 9 | §9「文件名可在实施时改（挂载锚与表行同批改即可）」少算，且给 scope block 留了不确定项 | 绿 | 文件名出现在 5 处——frontmatter 句、表行、checklist 条、scope block、test-self 锚。改名不同步 scope block，收尾 scope-audit 按路径分类会报越界 | v2 既已定名就删这条自由度；要留就写全 5 处并注明先改 scope block |
| 10 | dart-flutter 更正口径：数字核对通过，表述与测量命令三处小疵 | 绿 | (a) §3.5 测量命令是表格转义形态（竖线前带反斜杠），原样执行在 grep -E 下匹配字面竖线、零命中，不可复现；(b)「8 行命中系查版本／pub.dev 取依赖」不准：8 行里 3 行是 pub.dev，另 5 行是 source code 字面误命中（C/C++ 源码 3 行、许可证样板 2 行）——结论反而更稳；(c) 5437 行／5113 行本轮无 Bash 不可机械计，未核。附带一条正面证据：ffigen 第 81 行的指引是「查 pub.dev 最新版」，恰与本件「查已装版本」互补，可作不重叠的佐证 | 命令移出表格放代码块；(b) 改表述；(c) 留给带 Bash 的确认轮。另 §3.5 注「同行行按」疑为「同行一行按」笔误 |
| 11 | §3「『怎么查已装版本』配方｜全仓无（关键词法）」未列关键词，不可复现 | 绿 | 本轮以 package_config、pub-cache、已装版本、PUB_CACHE 四词全仓检索（含 .claude 目录）零命中，支持该结论；但 v1 同一格用的是另一组关键词且有 86 行对照，关键词不写明则数字无意义 | 格内或 §3.5 写明关键词 |
| 12 | 负证据探针建议在 /tmp 副本仓内跑，不动真仓工作区 | 绿 | U2 要在真仓临时删 SKILL 表行后跑全套 test-self；已禁 git checkout 还原，一旦中断会留下被改状态；多会话同仓时外溢到并发会话。test-self 自身先例即「在 /tmp 副本渲染后比对，不原地改写被跟踪文件」（`test-self.sh:271-272`） | U2／U3 写明在含 .git 的 /tmp 副本内执行；若坚持真仓，备份与还原放同一条命令链 |
| 13 | 可选补强：「引依赖／升级／排障」入口没有到新件的通路 | 绿 | 写之前最可能被打开的入口是 `SKILL.md:18` 那行（指向坑库）；新件只靠 frontmatter 概率触发加评审期 checklist。先例锚 `test-self.sh:101` 自带 build-release 互链子句 | 坑库文件头或 :18 行内容列加半句指针（按需面、零常驻）；做则 scope block 先加该文件。非本批必须 |

## 二、对派发五问的直接回答

1. **v2 新增引用真实性**：核了 12 处（checklist 围栏与节头、check-references 两处、test-self 四处、SKILL.md 两处、init.md、design-doc.md:39、dart-flutter 口径）。9 处吻合；2 处引证错位（#4 机制引错、#7 对象引错）；dart-flutter 数字口径吻合、表述与命令有小疵（#10）。
2. **10 条消解是否落实**：有落点标记的 6 条（发现 1／2／3／8／9／10）逐条对得上实物；发现 4–7 无标记且无原文，核不了（#6）。
3. **scope block 与 AC 可执行性**：scope block 10 项与 §1 老行为变更清单、D1–D6 内部一致，无漏登记面（先例 flavors-channels 全仓只落 4 件：CHANGELOG、test-self、build-release、SKILL.md）。AC 方面：AC2 表行边、AC3、AC4 的 U2 按现草稿不能红（#2、#3）；AC7／U5 可执行（预算闸 PASS 行打印实测数，`test-self.sh:226`）。
4. **与既有 :100-103 分工**：意图上不重叠——新条管创作期（写调用、用版本相关特性），既有四条管新增／升级流程；尾句「读 CHANGELOG／以测试判」与 :101、:103 同义但语境不同，可接受。但节头条件把新条的主场景排除掉了，分工声明在评审时走不到（#1）。
5. **范围是否扩大**：内部无溢出——§9 明确不做 agents/error.md 加行，宪法、双模板、canonical 零改动。对裁决原文的对照因选项卡不在包内无法闭合，按 v2 自述「新建参考文件＋SKILL 挂载＋checklist 兜底」三项均属裁决主线，看守锚与五件套是常规随批件。

## 三、核对通过项（不计入发现）

- `checklist.md:14-37` 围栏位置吻合；依赖变更专项节头 :98、四条 :100-103 吻合，「围栏外手写面」成立——孪生同文块闸在 /tmp 副本渲染后比对且围栏外不再逐字比（`test-self.sh:271-289`、注释 :274），围栏外加行不触发；编号对账只认行首粗体编号（`:523`），不受影响。§4.3「:103 后」插入点准确。
- `test-self.sh:1201-1202` 出口只看 FAIL；仓内无钉死 PASS 总数的位置（README :119／:150、ci.yml:54、release.sh 三处调用均无计数），90→91 成立。
- `test-self.sh:101` 先例在场（共 6 子句）；`:148-179` 尺寸闸只罩 parity-rewrite；check-references 红绿双向看守在位（`:420-432`）；check-references.py:28 EXTERNAL_SKILLS 在场。
- `SKILL.md:3` flavors-channels 句、`:32` 表行在场。细节：该句在 description 句中而非末段（其后还有两句），v2 自身写的「flavors-channels 句后」是准确的，派发清单的「末段」措辞不准，不影响方案。
- `references/design-doc.md:39` 引证准确（v2 新增引用）；§5 处置态用词（兼容／无影响论证／待证疑问单）与 :32 封闭四态一致。
- dart-flutter：SKILL.md 25 个、.md 27 个、全部 32 文件、关键词 8 行／3 文件（ffi-assets 4／ffigen 3／resolve-conflicts 1）全部吻合；「无读已装版本源码条款」经逐行看 8 行命中内容成立。
- `.claude-plugin/plugin.json` 现 1.3.13，bump 1.3.14 成立；baseline HEAD 296eb91 与现状一致。
- v2 四处草稿（frontmatter 句、表行、checklist 条、文件骨架）不踩消费面黑话禁令闸的禁词正则（`test-self.sh:715`）。
- frontmatter description 现长约 580 字符（手数），加草稿句后约 665。平台对该字段有长度上限，数值凭记忆未查证，按手数余量充足，仅备忘。

## 四、空缺态（未核，非判定未落实）

- 第 1 轮评审原文不在切片包 → 发现 4–7 的消解未核。
- 裁决选项卡原文不在切片包 → 范围对裁决的逐项对照未核。
- dart-flutter 行数（5113／5437）无 Bash 不可机械计，未核。
- 未变部分按派发要求未重验：预算实测值 16913／16179、PASS 现值 90、坑库 22 卡分布、`SKILL.md:105` 引证、消费面基线。
- 表行独占串（#3）只对 SKILL.md 前 60 行核过，全文独占性留实施时 grep。

## 涉及文件（绝对路径）

- `/tmp/plan-flutter-fact-check-2026-11-24-v2.md`（被审成品）
- `/tmp/plan-flutter-fact-check-2026-11-24.md`（v1 对照件）
- `/Users/chuxiong/Downloads/ai-code/flutter/checklist.md`
- `/Users/chuxiong/Downloads/ai-code/flutter/scripts/check-references.py`
- `/Users/chuxiong/Downloads/ai-code/flutter/scripts/test-self.sh`
- `/Users/chuxiong/Downloads/ai-code/flutter/skills/flutter-rules/SKILL.md`
- `/Users/chuxiong/Downloads/ai-code/flutter/skills/flutter-rules/references/design-doc.md`
- `/Users/chuxiong/Downloads/ai-code/flutter/commands/init.md`
- `/Users/chuxiong/Downloads/ai-code/flutter/.claude-plugin/plugin.json`
- `/Users/chuxiong/.claude/plugins/cache/dart-flutter/dart-flutter/1.0.7/skills/`（口径抽查目录）
- `/Users/chuxiong/.claude/plugins/cache/crules-flutter-market/crules-flutter/1.3.12/进阶/方案评审闭环.md`（评审纪律来源；本机 cache 为 1.3.12，仓内已到 1.3.13）

**整体结论：技术通过（无红项）；黄 1–6 须消解后再落终裁。**

## 第 3 轮（v3 复审 diff 级 · 2026-11-25 · 结论：红 0／黄 3／绿 7——技术通过，黄 3 须消解）

> **主控回应**：黄 3 由产出者消解、主控逐条 Bash 机械复核（复核结果标注于方案档 §0 第三表）：黄 1 三组关键词按组实测改写（9 词组 resident 4 行复现、v1 组 resident 0 复现、配方组全仓 0 复现）；黄 2 骨架改 rootUri 三路（`~/.pub-cache/git/` 检出带 pubspec.yaml 经 ls 实证，系第 1 轮评审建议原文之误的逐字继承——连评审自己都错了，本轮更正）；黄 3 ③ 草稿包行内代码。绿 7 全处置（4 全采纳——计数恰 1×3＋内容锚×2；5 补第三参；6 落点改写；7 改 17／六处；8 引文尾对齐；9 四小处；10 U0 基线＋轮次＋docs 前移）。原文照录如下。

### 原文

# 方案评审：版本与三方包事实先查后写 v3（第 3 轮·diff 级）

> **评审纪律声明**：只评审、不修改被评审方案；只输出建议／发现；全程只用 Read／Glob／Grep，未调用任何修改工具。结论作为返回值交主控原样落盘。
> **被审成品**：`/tmp/plan-flutter-fact-check-2026-11-24-v3.md`；**v2 对照件**：`/tmp/plan-flutter-fact-check-2026-11-24-v2.md`；**两轮评审原文**：`/tmp/round1-review.md`、`/tmp/round2-review.md`；**仓根**：`/Users/chuxiong/Downloads/ai-code/flutter`（HEAD 296eb91）。
> **切片包**：派发件以「已核实事实切片」为题给了 12 条 file:line 清单＋对照件＋两轮原文，按切片包契约的实质内容对待（标签非「切片包」字样，如实备注）。切片条目全部开件定点核对，未以全文 Read 兜底。
> **记忆库**：仓内 `.claude/memory/` 不存在，记忆库未启用，角色卡「对照 business-rules／INVARIANTS」两条自然不触发。
> **本轮范围**：只评 v2→v3 改动面、第 2 轮黄 1–6 消解、绿 7–13 处置、v3 新增引用与事实、范围；未变部分只抽查。等级用文字：红＝阻断／黄＝须消解／绿＝建议。
> **落盘提示**：本文将入 `docs/`，links 面扫全仓 md，故全文零裸链接语法，链接示例一律包行内代码。

## 一、评审表

| # | 发现 | 严重程度 | 原因 / 证据 | 建议（只建议，不改） |
|---|------|---------|------------|-------------------|
| 1 | §3 首行「①常驻面组」关键词与数字挂错：所列 9 词组在 app/、plugin/ 不是 0 命中；「86 行」是 v1 另一组关键词的数 | 黄 | v3:69 写「①常驻面组（官方／official／docs.flutter.dev／pub.dev／api.flutter.dev／源码／source code／installed version）在 app/、plugin/、canonical/ 0 命中（全仓 86 行作对照）」。按这 9 词、忽略大小写实测：`app/CLAUDE.md` 2 行（:128、:164）、`plugin/CLAUDE.md` 2 行（:121、:157）、canonical/ 0；全仓非隐藏目录 126 行／33 文件（限 .md 为 102 行／25 文件）。「双模板零命中＋仓内别处 86 行」出自 v1 的另一组关键词（v1:37「官方／pub.dev／读源码／查文档」）。此格是绿 11 消解时新写的。「配方全仓无」的结论不受影响——由②组独立支撑（我方复测 0 命中，`.claude` 另查亦 0） | ①组二选一：换回 v1 原正则并附命令；或按 9 词组改成实测值并附命令。取后者时，:128／:121 与 :164／:157 恰是第 1 轮发现 2 的部分重叠面，可在同格补一句增量（顺带闭合 #6） |
| 2 | 参考文件骨架一条承重事实错：git 依赖的源码在 pub cache 里，骨架写「不在 cache」 | 黄 | v3:116「git/path 依赖 → 读 pubspec 指向的实际目录（不在 cache）」。本机实况：cache 的 git 子目录下就是 git 依赖的检出——`~/.pub-cache/git/` 下有 file_saver（5 个不同 commit）、flutter_coverage_badge、lcov.dart 等带 pubspec.yaml 的检出目录，`git/cache/` 下是裸镜像。git 依赖的 pubspec 指向 URL 加 ref，不是本机目录；实际运行的是 cache 里按 commit 检出的那份（package_config 的 rootUri 指向该处——此点按 pub 行为陈述，未在本机 package_config 上直读）。只有 path 依赖不在 cache。错源＝第 1 轮评审发现 3 的建议原文被逐字继承，该半句是前轮评审自身的错，本轮更正。影响：这是本件核心配方，照写会把读者对 git 依赖引向找不到源码，正是本方案要治的病；§4.5 第 8 项的命令清单（PUB_CACHE 现值、列 hosted、rootUri 采样、flutter --version）测不到它；D1 标 ✅（`design-doc.md:41`：✅＝亲验 file:line 或 hash 齐），骨架事实实为未取证 | 骨架改按 rootUri 形态分三路：hosted → cache 的 hosted 目录；git → cache 的 git 目录（仓库名-commit）；path → pubspec 所指实际目录。§4.5 第 8 项加「列 cache 的 git 子目录」或 git 依赖 rootUri 采样。骨架事实在实施取证前标 ⚠️ |
| 3 | 「本稿全文不使用链接语法」不实：1 处裸链接，落盘即 links 面红 | 黄 | v3:7、§4.5 注 2、§0 黄 4 行均称零裸链接。全文方括号圆括号共 4 处：:138（行内代码内）、:150（行内代码内）、:204（围栏内）安全；:142（③ 坑库行指针草稿）在引用块内、未包行内代码。`check-references.py:47-65` 只跳围栏与行内反引号 span，引用块不豁免，相对路径按文件所在目录解析：落盘为 docs 下方案件后解析到 `docs/references/` → 不存在 → links rc 1 → `test-self.sh:420` 红 | :142 的链接示例包进行内代码或改纯文字路径；定稿落盘前对成品跑一次 links |
| 4 | 锚强度低于所引先例形（三处）；AC1 有一项无机械可红检查 | 绿 | (a) ③ 坑库行指针无专属子句：删 ③ 后四子句仍全绿，AC1「:18 指针在场」（v3:231）在 §6.2 无对应探针，可红性推演（v3:208）未声明此边界；先例 `test-self.sh:101` 的第三个挂载点（build-release 互链）是有专串的。(b)「按位置独占」只靠实施期一次性 grep（v3:153 表注），锚用 grep -q 不校验次数——日后同串在别处再现，删表行／删句即回到先例弱点，§8 的处置只有 CHANGELOG 注记这道非机械防线。(c) 新参考文件只有「文件在场」一个条件；先例对参考文件本体设两条内容锚（渠道矩阵、坑位速查），清空正文只留标题仍绿。另：AC1「独占串全文各恰 1 处」未带 §4.2 表注的「链接形子句除外」（该串实为 2 处） | ③ 加一子句查「先核已装版本」（现全仓 0 命中）；两条位置独占串改计数等于 1；参考文件加 package_config、PUB_CACHE 两条内容锚（两串现全仓 0 命中，实施后应只在该文件）；AC1 补例外 |
| 5 | §4.6 锚草稿缺第三参（标签），照抄即脚本中止 | 绿 | `test-self.sh:63-64` 的 t 函数在 PASS／FAIL 两支都无条件引用 `$3`，脚本 :9 为 `set -uo pipefail`——两参调用触发 unbound variable，非交互 shell 退出、不出汇总行。v3:198 已注「实施时照抄仓内现行写法」，故属草稿完整性问题 | 草稿补第三参标签 |
| 6 | §0 第 1 轮 2 行的落点指针落空 | 绿 | v3:16 称「增量分析落 §3 五档（app:17/:19/:128、plugin:121、parity-rewrite:75 部分重叠面在案）」；正文 §3 无此内容，这组行号串全文只在 :16 出现，「重叠」另仅 :218（讲的是 dart-flutter）。实际消解＝主线改 C3+C6、新红线方案作废。对照表是黄 6 的消解件，不宜留错指针 | 该格据实改写；或并入 #1 处理 |
| 7 | 计数漂移：既有表行实为 17 不是 16 | 绿 | v3:136「既有 16 行同形」，源头是第 2 轮评审原文 #3 的「:17-33 既有 16 行」，切片第 10 条同。`SKILL.md:17` 至 :33 共 17 行，全链接形结论成立。同性质：§0 绿 9 行「五处锁定」，采纳 ③ 后文件名引用位为六处 | 改 17；五处改六处或删计数 |
| 8 | ③ 草稿引文尾与现文不一致 | 绿 | v3:142 引「……不占消费工程字数）；」，`SKILL.md:18` 现文尾为「维护者侧内容也在此，不占消费侧常驻）」。实施者需猜是否改写尾巴。全部草稿已比对黑话禁令闸 BAN 正则（`test-self.sh:715`），零命中 | 引文改「……不占消费侧常驻）；」或明示尾巴改写 |
| 9 | 措辞对齐四小处 | 绿 | (a) checklist 新条正文（v3:162）只覆盖触发①②，「升级依赖后报错」只在节头——第 2 轮黄 1 指出的「草稿没写升级后报错」在条目层仍在。(b) 骨架（v3:127）裸写「照 checklist 依赖变更专项」：能过指针限定闸（:515 正则只认行内代码形态的 checklist 文件名），但 references/ 既有 5 处（build-release.md:30、:37，layout.md:65，performance.md:3、:33，theming.md:9）用「插件 cache」限定形，闸的立法意图（:513-514：消费工程根无此文件，裸写不可解析）对这一指向同样适用。(c) 骨架（v3:115）「本机 observed」分发后指代不明，应标谁的本机＋as-of。(d) §3 pub cache 行（v3:77）「工程一 package_config」无路径无命令，不可复现 | (a) 条目正文补「升级依赖后报错排障」；(b) 改限定形；(c)(d) 补标注 |
| 10 | 验证计划与落盘次序三小处 | 绿 | (a) U2a-c 缺副本基线对照：未先在未改副本跑出 91/0，「红」不能排除副本环境因素；AC4「按原值还原」是真仓措辞残留。(b) scope block（v3:180）与 §0 写「两轮评审全文」，本轮之后落盘应为三轮。(c) §7 依赖方向（v3:257）把 docs 两件排在看守锚之后，闭环正文 step 7 为「获批后第一个动作落盘评审记录→进实施」 | (a) U 表加一行「未改副本→91/0」；(b) 改三轮；(c) docs 落盘前移或写明后移理由 |

## 二、对评审五问的直接回答

**问 1：黄 1–6 是否逐条落实且判据可红**
- 黄 1：落实。§4.3 独立小节解开了节头条件矛盾——新节头三触发与参考文件「三触发」一致，:98 既有节头与 :100-103 四条不动，纯调用任务不被带进「依赖变更」检查面，「独立成节」的理由成立。可红（U2c）。小瑕见 #9(a)。
- 黄 2：落实。锚第 5 子句直查 `checklist.md`；可红。
- 黄 3：落实，**可红性推演成立**。按现草稿与现占用：删表行→「定位已装版本」0 命中；删句→「三方包版本核验」0 命中；删节→「三方包调用核验」0 命中，三发各使新锚 FAIL。脚本无 `set -e`，单条 FAIL 不中止；新锚之前的检查不因这三处删除而中止。残余三处见 #4。
- 黄 4：D4、§3、§5 三处机制改述与 `check-references.py` 实读一致；「本稿零裸链接」未达标（#3）。
- 黄 5：第 8 项、AC8、U6 在位；但骨架自带一条错事实，且第 8 项的命令清单测不到它（#2）。
- 黄 6：对照表在，两轮摘要忠实；一处落点指针落空（#6）。

**问 2：绿 7–13 处置是否恰当（含两处自主裁决）**
- 绿 7、8、9、10、12、13：处置恰当，落点在 v3 正文可指认。绿 11：关键词写明了，但挂错了组（#1）。
- 两处自主裁决均在裁决主线内，理由成立。「独立成节」是两条路里不把既有四条带进纯调用任务检查面的那条；「:18 指针」属 SKILL.md 挂载面内的小改，零常驻，scope 不新增文件。附两处待补：③ 无专串（#4）、引文尾不一致（#8）。最终由需求方裁。

**问 3：v3 新增引用与事实是否真实**
- 核了约 40 处。行号类全部与实读吻合（唯 #7 的计数漂移）；机制类吻合；`design-doc.md:39` 引文逐字一致；`init.md:44-51`、:56、:119-124 三处吻合。
- §3 的 dart-flutter 3 实义＋5 字面拆分：我方逐行复测一致（ffigen:81 查 pub.dev 最新版、resolve-conflicts:108 镜像 url、ffi-assets:76 直取 pub.dev 依赖；ffi-assets:3/:10/:115 与 ffigen:124/:160 为 source code 字面）。否定结论另换一根轴复查（installed／pub cache／package_config／.dart_tool 等 9 行命中）仍成立。
- §4.2 独占串安排表的「现占用 0」属实。§4.6 锚草稿逻辑成立，缺第三参（#5）。
- 不实 3 处：#1、#2、#3。§0 摘要忠实度良好，1 处落点落空（#6）。

**问 4：scope block／AC1–AC8／U1–U6 是否内部一致、可执行、可红**
- scope block 10 项与 §1 老行为变更清单、D1–D6、§7 一致；逐文件粒度、无裸 glob；无漏登记面（仓内没有 references 文件枚举面——以 network-comms.md 反查仅 8 件，README／help／memory 均无清单）。
- AC 与 U 映射完整。机械可红：AC2、AC3、AC4、AC6、AC7。只到存在性：AC1 的「:18 指针在场」与新文件「在场」（#4）。属收口批与评审面：AC5、AC8。
- 内部文字不一致三处：#4 末句、#10(b)(c)。

**问 5：范围有无溢出**
- 无溢出。SKILL.md 三件＝挂载；checklist 独立小节＝兜底；参考文件本体（含 SDK 版本与跨平台定位）在「版本与三方包事实先查后写」题内；看守锚、docs 两件、五件套是常规随批件。宪法、双模板、canonical、dart-flutter 插件、`agents/error.md` 零改动。对选项卡原文的对照受限于原文不在包（见空缺态），按 v3 自述对照成立。

## 三、核对通过项（不计发现）

- 行号全部吻合：`checklist.md:14-37` 围栏、:98 节头、:100-103 四条；`check-references.py:29`、:32-38、:40-45、:113-114、:119-125；`test-self.sh:9-10`、:60-64、:101（6 子句）、:148-179、:216-229、:271-272 注、:420-432、:513-520、:523、:715、:1201-1202；`SKILL.md:3`、:18、:32、:105。
- 机制口径：links＝`md_files()` 全仓遍历、排除目录五项；`DEFAULT_FACE_GLOBS` 管 entries 面，含 `skills/*/references/*.md` 与 `checklist.md`，不含方案／评审稿。v3 三处改述正确。
- 独占串四个外加「先核已装版本」，全仓 `*.md` 现 0 命中。配方组五词全仓 0 命中（含 `.claude` 显式路径）；换轴复查（pub cache／.pub-cache／hosted/／rootUri／已安装版本）仍 0。
- dart-flutter：`.md` 27 个（SKILL.md 25＋dart-build-cli-app 的 references 2）；§3.5 命令代码块形态可执行、路径实存。
- SKILL.md 三件草稿与 checklist 新节：不触黑话禁令闸、散文指针闸（:756 正则）、指针限定闸；checklist 条的「flutter-rules skill」在册。
- 独立小节位置在围栏外，编号对账只认行首粗体编号，不受影响。
- test-self 三处调用（ci.yml:54、release.sh:54、:110）均不钉 PASS 总数，90→91 成立；版本一致闸在 tag 不可读时自 SKIP（:878），副本仓可用；脚本须在 git 树内运行（:60），与「含 .git 的 /tmp 副本」一致。
- 常驻预算阈值 17000／16200 与脚本一致；SKILL.md 不在常驻预算与尺寸闸面内，「零常驻」成立。
- 影响面处置态用词在 `design-doc.md:32` 封闭四态内；兼容性四面在场；批次卡四必答在场；非 UI 任务，视觉规格清单不涉。
- 两轮评审原文无裸链接（round2 的方括号圆括号在行内代码内）。

## 四、空缺态（未核，非判定未落实）

- `dart.dev/tools/pub/environment-variables` 出处：无联网工具，未独立复核，沿切片第 3 条。
- dart-flutter 行数 5113／5437；pub cache 两域目录数 153／118／1087／454；pub.flutter-io.cn 域在场（沿第 1 轮）；PUB_CACHE 未设；工程一 package_config 版本值——需 Bash／环境，未核。
- 预算现值 16913／16179、PASS 现值 90：运行时输出，未重跑（未变面）。
- `scope-audit.py` 分类行为（切片第 12 条）：本轮未开件，沿第 1 轮核对。
- 选项卡原文（C3／C6 定义、「本批不处理」标签）：不在包。
- test-self 整体在 /tmp 含 .git 副本能否跑通：无 Bash 未核。
- frontmatter description 现长约 580 字符：未机械计数（粗估 540–580，不承重）。
- 关键词计数的隐藏目录面（`.github`、`.claude-plugin` 等）：Grep 工具默认不扫，`.claude` 已显式单查。

## 五、涉及文件（绝对路径）

- `/tmp/plan-flutter-fact-check-2026-11-24-v3.md`（被审成品）
- `/tmp/plan-flutter-fact-check-2026-11-24-v2.md`（v2 对照件）
- `/tmp/plan-flutter-fact-check-2026-11-24.md`（v1，仅为核 #1、#6 定点 Grep 两处）
- `/tmp/round1-review.md`、`/tmp/round2-review.md`
- `/Users/chuxiong/Downloads/ai-code/flutter/skills/flutter-rules/SKILL.md`
- `/Users/chuxiong/Downloads/ai-code/flutter/checklist.md`
- `/Users/chuxiong/Downloads/ai-code/flutter/scripts/check-references.py`
- `/Users/chuxiong/Downloads/ai-code/flutter/scripts/test-self.sh`
- `/Users/chuxiong/Downloads/ai-code/flutter/commands/init.md`
- `/Users/chuxiong/Downloads/ai-code/flutter/skills/flutter-rules/references/design-doc.md`
- `/Users/chuxiong/Downloads/ai-code/flutter/skills/flutter-rules/references/`（build-release、layout、performance、theming——Grep）
- `/Users/chuxiong/Downloads/ai-code/flutter/app/CLAUDE.md`、`/Users/chuxiong/Downloads/ai-code/flutter/plugin/CLAUDE.md`（Grep）
- `/Users/chuxiong/Downloads/ai-code/flutter/canonical/redline-evidence.md`
- `/Users/chuxiong/Downloads/ai-code/flutter/README.md`、`/Users/chuxiong/Downloads/ai-code/flutter/scripts/release.sh`、`/Users/chuxiong/Downloads/ai-code/flutter/.github/workflows/ci.yml`（Grep）
- `/Users/chuxiong/.claude/plugins/cache/dart-flutter/dart-flutter/1.0.7/skills/`
- `/Users/chuxiong/.pub-cache/git/`
- `/Users/chuxiong/.claude/plugins/cache/crules-flutter-market/crules-flutter/1.3.13/进阶/方案评审闭环.md`（评审纪律来源）

**整体结论：红 0／黄 3／绿 7——技术通过，黄 3 须消解（#1 关键词数字挂错、#2 骨架 git 依赖事实错、#3 裸链接），非「无须消解」。**

## 第 4 轮（v4 复审 diff 级 · 2026-11-25 · 需求方授权超轮 · 结论：红 0／黄 0／绿 8——技术通过，无须消解）

> **主控回应**：8 绿系落盘前口径件，已全部顺手折入 v4（方案档 §0 第四表逐条列落点）：六发口径＋U2d/U2e 枚举、轮次口径、U0 批中态括注、41 条忠实度、骨架头 as-of 行、「命中行数恰 1」措辞＋链接形计数恰 2（可选件采纳）、U2e 负证据、实施细部四处（SDK 包 rootUri 限定语／工程一绝对基准目录／AC3 diff 仅新增行／test-self 记账行）。评审明示改后无须再派评审。原文照录如下。

### 原文

# 方案评审：版本与三方包事实先查后写 v4（第 4 轮·diff 级·需求方授权超轮）

## 评审纪律声明

只评审、不修改被评审方案；只输出建议／发现；全程只用 Read／Glob／Grep（只读工具），未调用任何修改工具，未跑 Bash。结论作为返回值交主控原样落盘。

- 被审成品：`/tmp/plan-flutter-fact-check-2026-11-24-v4.md`；v3 对照件：`/tmp/plan-flutter-fact-check-2026-11-24-v3.md`；三轮评审原文：`/tmp/round1-review.md`、`/tmp/round2-review.md`、`/tmp/round3-review.md`；仓根：`/Users/chuxiong/Downloads/ai-code/flutter`（HEAD 296eb91，工作区净）。
- 切片包：派发件以「已核实事实切片」为题给了 13 条 file:line 清单＋对照件＋三轮原文，按切片包契约的实质内容对待（标签非「切片包」字样，如实备注）。切片条目逐条开件定点核对，未以全文 Read 兜底。
- 记忆库：仓内 `.claude/memory/` 不存在（`.claude/` 下只有 probes／settings.json／compact-gate 探针件），记忆库未启用，角色卡「对照 business-rules／INVARIANTS」两条不触发。
- 本轮范围：只评 v3→v4 改动面、第 3 轮黄 1–3 消解、绿 4–10 处置、v4 新增引用与事实、范围；未变部分只抽查。等级用文字：红＝阻断／黄＝须消解／绿＝建议。
- 轮次：仓内闭环正文写「最多 3 轮」（`进阶/方案评审闭环.md` 循环守卫节）；本轮为授权超轮，派发件与 v4:6 口径一致，授权本身不在评审者可见面（见空缺态）。
- 落盘提示：本文将入 `docs/`、自动进 links 面，故全文零裸链接语法，路径示例一律行内代码。

## 一、评审表

| # | 发现 | 严重程度 | 原因 / 证据 | 建议（只建议，不改） |
|---|------|---------|------------|-------------------|
| 1 | 负证据口径未随 U2d 同步：AC4 与 §4.5 第 4 项仍写「四发」，第 4 项的枚举漏 U2d | 绿 | v4:219 枚举「U2a…U2b…U2c…U3」称四发；v4:268 AC4「负证据四发各红一次」；§6.2 负证据实为五发（U2a–U2d＋U3）。U2d 正是第 3 轮绿 4a 的消解件——照 AC4 字面验收，四发齐即可判过，:18 指针这一发可以不跑 | AC4 与 §4.5 第 4 项改「五发」并补枚举 U2d |
| 2 | 轮次口径内部矛盾：头注声明第 4 轮已授权，正文七处仍写「三轮」 | 绿 | v4:6 声明「第 4 轮已经需求方显式授权超轮」；而 v4:10（§0 标题）、:209（「v4＋三轮对照」）、:210（「三轮评审全文」）、:226（注 2「本稿与三轮评审原文均零裸链接」）、:317（「三轮评审 30 条」）仍是三轮。落盘约定＝评审文档含各轮评审全文（含首轮），本轮评审也须入盘。与第 3 轮绿 10b「两轮应三轮」同类复发 | 上述各处改「四轮」或「各轮」；§0 可补第 4 轮表；注 2 的零裸链接范围扩到本轮原文（本文已按零裸链接写） |
| 3 | U0 括注失准，前置措辞有歧义 | 绿 | v4:278 写「含 .git 的 /tmp 干净副本｜91/0（版本一致闸 tag 腿自 SKIP，`test-self.sh:878`）」。实读 `test-self.sh:858-863`：只有 `git describe` 取不到 tag 才 SKIP；含 .git 的副本 tag 可读，四值 1.3.14 对 tag v1.3.13 走「紧后一版」批中态 OK（`:865-872`），在 `:879-880` 计 PASS。SKIP 分支不计 PASS，两种结果总数差 1——91/0 只在「计 PASS」下成立。第 3 轮原文是条件句（「tag 不可读时自 SKIP」），v4 把它写成了断言。另「干净副本」可读成 HEAD 的干净副本，那是 90/0 | 括注改「版本一致闸走批中态计 PASS」或删；前置改「落地后工作区（含未提交改动）的含 .git 副本，未做变异前」 |
| 4 | §0／§3 摘要忠实度三处 | 绿 | (a) v4:317「三轮评审 30 条发现」——三轮原文实为 10＋13＋10＝33 条，§0 三表行数也是 10／13／10；(b) v4:49、:85「恰＝第 1 轮发现 2 的重叠面清单」——第 3 轮原文写的是「部分重叠面」；第 1 轮发现 2 的清单＝`app/CLAUDE.md:17`、`:19`、redline-evidence、`app:128`／`plugin:121`、`skills/parity-rewrite/SKILL.md:75`、`references/network-comms.md:21`，与 4 行只交 app:128／plugin:121 两行，`:164`／`:157` 不在其内；(c) v4:118「86 行系含非 md 文件口径」——同句自陈「未复现」，成因是推断不是实测 | (a) 改 33；(b) 改「部分重叠（app:128／plugin:121 两行）」；(c) 改「推断为含非 md 口径，未复现」 |
| 5 | §8「文件头标 as-of＋出处」在 §4.1 骨架里没有对应物 | 绿 | v4:306 的处置写「文件头标 as-of＋出处」；骨架文件头只有标题与触发行，as-of 只在 hosted 一行内，出处只在括注内。两处是 v4 同轮新写，互不对齐 | 二者取一：骨架文件头补一行 as-of＋出处；或 §8 改「行内标 as-of＋出处」 |
| 6 | 锚语义三处精度边界（机制本身成立） | 绿 | (a) `grep -c` 计的是命中行数不是出现次数：同一行出现两次仍绿——SKILL.md description 是单行，句内重复不红；(b) AC1「按位置计数恰 1」在锚里实为「文件内恰 1 行」，串换位不红；(c) 链接形子句是 `grep -q`：③ 也带链接形，② 单独改回裸路径（③ 保留）时该子句仍绿，AC1 括注「②③ 各一处」无机械对应。此边界自 ③ 引入即存在，非 v4 新增 | (a)(b) AC1 措辞改「命中行数恰 1」即可，机制不必动；(c) 可选：链接形改 `grep -c … \| grep -qx 2`，或把表行串与链接形并成单行匹配 |
| 7 | 「撞用自动变红」缺一发负证据 | 绿 | v4:305 以「计数恰 1 的锚在撞用时自动变红」为处置，这是本批新引入的机制。§6.2 五发全是「删→0→红」，没有「加→2→红」。按本仓纪律，不能失败的 check 组不成验证计划。另：该说法只在同文件、异行口径下成立，跨文件撞用不红（§4.2 表注已说明文件内作用域） | 加 U2e：副本内任一串在 SKILL.md 另起一行重复一次→新锚红；成本一发 |
| 8 | 实施细部备忘四处 | 绿 | (a) 骨架「唯一不在 cache 的一路」——限定在「三类 pubspec 依赖」内成立；package_config 里 SDK 自带包的 rootUri 也不在 cache（按 pub 通行为陈述，本机 package_config 未直读）；(b) 工程一路径「saas-suite/03-code/src/app/saas-cashier」是相对写法、未写基准目录，按此拼接未定位到该文件；(c) D3「既有四条与节头一字不动」没有 AC／U 对应（围栏外手写面无闸）；(d) test-self 头注记账行惯例（`test-self.sh:12-54` 每批一行「+1 至 N」）未列入实施步骤 | (a) 加限定语，实施 rootUri 采样时顺带看一眼 SDK 包条目；(b) 补基准目录；(c) AC3 补「checklist.md diff 仅新增行」；(d) 记账行随锚同改 |

## 二、对评审五问的直接回答

**问 1：第 3 轮黄 1–3 是否落实且事实准确**——三条全部落实，事实面三处措辞见 #4、一处限定见 #8。
- 黄 1：落实。§3 按三组关键词改写、各组带命令。我方复测四个数全部复现：v1 组 resident 0；9 词组 resident 恰 4 行、行号全对；配方组全仓 0；v1 组全仓 .md 67 行／14 文件。
- 黄 2：落实。骨架改 rootUri 三路；D1 拆「决策 ✅／骨架事实 ⚠️」；§4.5 第 8 项加 git 检出采样。本机实况核对：`~/.pub-cache/git/` 下 8 个检出目录（file_saver 6 个 commit、flutter_coverage_badge、lcov.dart）均带 pubspec.yaml，命名＝仓库名-40 位 commit，与骨架一致；`git/cache/` 下为裸镜像；hosted 形态实存。骨架未见错事实。file_saver 是 6 个 commit，v4 写 6 正确（第 3 轮原文写 5，少数一）。
- 黄 3：落实。v4 全文 `](` 恰 4 处，均在行内代码或围栏内，零 URL。

**问 2：第 3 轮绿 4–10 处置是否恰当**——十条全部恰当，落点在 v4 可指认。三处自主裁决均在裁决主线内，理由成立；绿 4 全采纳带来的副作用只有 #1 的口径漏同步。

**问 3：v4 新增引用与事实是否真实**——核了约 45 处，行号类零漂移。§0 三表 30 行摘要 28 行忠实、2 行失准（#4a 总数、#4b「恰＝」）；§4.2 看守串表属实（现占用 0 全仓复测、邻位防误逐条成立）；§4.6 锚草稿逻辑成立（四态退出码 1/0/1/1 推演一致）；不实或失准合计 #3、#4、#5。

**问 4：scope／AC／U 是否内部一致、可执行、可红**——U2d 推演成立；五发负证据逐一推演均红；AC1 机制＝命中行数恰 1，对「删→红」「异行撞→红」两条成立，精度边界见 #6；不一致两处（#1、#3）；AC→U 映射完整。

**问 5：范围有无溢出；头注声明是否如实**——无溢出（逐项对照裁决主线成立；宪法、双模板、canonical、dart-flutter 插件、agents/error.md 零改动）。头注与派发件口径一致；授权行为本身不在评审者可见面，记空缺态。

## 三、核对通过项（不计发现）

- 行号零漂移：test-self.sh :9/:60-61/:62-64/:101/:148-179/:216-229/:420-432/:513-520/:523/:715/:756/:878/:1201-1202；check-references.py :29/:32-38/:40-45/:47-65/:113-114；SKILL.md :3/:17-33/:18/:32/:105；checklist.md :14-37/:98/:100-103；init.md :44-51/:56；design-doc.md :32/:39/:41；ci.yml:54；release.sh:54/:110。
- 机制口径与各闸边：links 面遍历与跳过逻辑、entries 面 glob、references 文件头无格式闸、专项节名无枚举面、骨架×指针限定闸（同行带「插件 cache」可过——切片第 13 条未覆盖、本轮补核）、草稿×黑话禁令闸/散文指针闸、黑话禁令闸与散文指针闸均跳过 docs/、常驻预算闸口径不含 SKILL.md。
- dart-flutter 8 行逐行吻合；消费工程路径不触禁写面（消费工程名禁写只扫 skills/parity-rewrite/，docs/ 既有 12 件已载同类路径 38 处）。
- 声明面四清单齐整；切片自查更正两处（切片第 7 条「5 处」实为 6 行——v4 未引该计数；第 3 条 4 处位置一致）。

## 四、空缺态（未核，非判定未落实）

- dart.dev 出处：无联网工具，未独立复核，沿切片第 2 条。
- 运行时值未重跑：PASS 现值 90、预算 16913/16179、hosted 目录数、dart-flutter 行数、frontmatter 现长。
- test-self 整体在 /tmp 含 .git 副本能否跑通：无 Bash 未核；副本制作方式未在方案写明。
- 工程一 package_config：按 v4 相对路径未定位；rootUri 三形态未直读；mtime 与版本值沿切片。
- 锚草稿未执行；链接形 BRE 模式在 test-self.sh 内无先例，按 POSIX BRE 语义为字面量，首跑即证。
- 第 4 轮授权行为不在评审者可见面；选项卡原文不在包；v1 旧口径 86 行未复现；隐藏目录面 Grep 默认不扫且均非 .md。

## 五、涉及文件（绝对路径）

v4、v3、v1、三轮评审原文（/tmp）；仓内 test-self.sh、check-references.py、SKILL.md、checklist.md、design-doc.md、references 四件（Grep）、init.md、app/plugin CLAUDE.md（Grep）、README.md、ci.yml、release.sh、memory/（Grep）；dart-flutter cache skills/（Grep）；~/.pub-cache 三目录（Glob）；1.3.13 cache 进阶/方案评审闭环.md。

**整体结论：红 0／黄 0／绿 8——技术通过，无须消解。绿 1–5 属落盘前宜顺手同步的口径件，改后无须再派评审。**
