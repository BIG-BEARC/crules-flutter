# context-mode 吸收评审稿（2026-10-19/20 外源分析·已裁不立批·纯存档）

> 状态：**分析毕·拷问毕（context-mode 独立一轮，全局第四轮）·需求方已裁（2026-10-20「有必要进行吸收吗？」→ 必要性检验全项未过）：不立批吸收，本稿纯存档作查证货架**。关键断言均有机械证据，修正轨迹见 §5。本稿只落文档：未动任何受控文件、未执行源仓任何脚本、未 commit（呈工作区 diff 评审）。日期：2026-10-19 分析／10-20 裁决落档 · 来源：mksglu/context-mode（本地快照 `/Users/chuxiong/Downloads/ai资料/context-mode-main`，https://github.com/mksglu/context-mode ）· 许可：Elastic License 2.0（Copyright 2026 Mert Koseoglu，LICENSE 全文含限制段实读确认，口径见 §1.1）· 面向对象：维护者/需求方 · 裁剪档位：标准（全节）。
> 一句话结论：这是**运行时基础设施仓**（MCP 服务器＋11 ctx_* 工具＋SQLite 会话库＋15 宿主 hooks 适配），本体与插件宪法体系不同层、按类不收；真正可取的是其**自治纪律文档四份 ADR 里的方法与教训**——已全部核验入 §3 货架，触发线见 §6，无一项通过「本地实证的痛」检验，故不立批。

## 1 来源与方法

| 项 | 内容 |
|---|---|
| 分析对象 | 运行时基础设施本体（全仓 599 文件，构成见未读声明行，按类毙见 §4）＋**评审面**：ADR×4、SKILL.md＋anti-patterns、CLAUDE.md、LICENSE、BENCHMARK 头、UPSTREAM-CREDITS、routing.mjs 站点与节流实现段、契约测试、3 份机制测试 |
| 方法 | 全程只读（零执行源仓脚本/零安装）；先显式覆盖面声明、待核项显式标注（agent-skills 三轮拷问教训前置应用），再经一轮「确定？」拷问修正 |
| 覆盖面 | README 头、ADR-0001/0002/0003/0004 全文、skills/context-mode/SKILL.md＋references/anti-patterns.md、CLAUDE.md、LICENSE 全文（授权段＋限制段）、BENCHMARK.md 头、docs/UPSTREAM-CREDITS.md 头、hooks/core/routing.mjs（CASE A 站点 grep＋guidance 节流实现段 L36-127）、tests/core/server.test.ts 契约测试 grep（:1950/:5376/:5637）、guidance-throttle/stale-detection/extract-rule-detection 三测全文 |
| 未读声明 | 全仓 599，逐件触达 **17（2.8%）**，未读 582——src 96／tests 248／hooks 85／scripts 15／configs 44／web 29／skills 11／docs 4／bin 1／根与隐藏 ≈49——基础设施实现本体**未深入读取**，与吸收判断相关的是其纪律文档与机制语义；按类毙（§4 首行），非逐文件评审。2026-10-21 转录复核修正：原声明只列 src/tests，漏 hooks/configs/web 等未读面 |

### 1.1 许可口径（ELv2）

授予：复制/修改/再分发（含修改版），限自用与常规分发。**限制三条**（限制段实读）：①禁将软件作托管/受管服务向第三方提供；②禁动/绕 license key 功能；③禁抹许可与版权 notice；另附专利授权及书面侵权主张即终止条款。**对本仓的口径结论**：本稿吸收的只是机制、方法与教训的**记述**（事实与思想，非代码文本，原文零摘录）；且本库已裁不参与团队共享、无分发面——ELv2 不构成约束面。与 agent-skills（MIT）不同，此仓条款若日后涉及**代码级**借鉴须重审（管理服务条款不涉、notice 条款涉及再分发才触发）。

## 2 结论速览（已裁不立批·处置表）

| 处置 | 项 | 一句话 |
|---|---|---|
| 货架·触发线 §6-1 | ADR-0002＋ADR-0003 模型面向措辞纪律 | 两案词表＋probe-gated 改写＋契约测试锁措辞；本地 hook 措辞零事故，方法存案待触发 |
| 货架·触发线 §6-2 | ADR-0001「闸先于根因」反模式 | 完整案例级教训（误诊根因上建闸→闸成新 bug→整体回滚）；至多坑卡一行 |
| 货架·成本已降档 | 宪法读取事件 | compliance-audit 既有分类器加一 Read 分支即可（原以为要新机制）；无读数需求不建 |
| 出清 | guidance-throttle | stop-reminder 设计已含同语义（L21 实证），无缺口 |
| 不收 | 基础设施本体／BENCHMARK 数字／Think in Code／周期重提计数器／stale-detection | 见 §4 |

## 3 货架内容（查证用·非执行项）

### 3.1 ADR-0002＋0003：模型面向措辞纪律（本轮最高置信项）

**机制**（两 ADR 全文＋routing.mjs 站点＋契约测试实证）：

- **两案词表**：CASE A（路由重定向——动作支持、换工具）必须以 `redirected to <ctx_tool>` 开头、肯定式声明能力（`<ctx_tool> has full network access`）、点名替代工具的祈使调用、以正向重试提示收尾；禁裸 `BLOCKED`、禁裸 NOT 否定、禁组织理由前缀（"for X efficiency"——HTTP 301 类比：服务器从不在 Location 后附 "for SEO efficiency"）。CASE B（真策略禁止）用 `denied`/`blocked by security policy`、须引违反的规则、可建议安全替代——模型此时停手上报**正是正确行为**。
- **实证数字**：裸 `blocked` → Opus 4.6 误读为网络限制而投降训练数据 **6/6**；改 `redirected` → **0/6**。NOT 括号句（"this is NOT a network restriction"）反使 Haiku 投降率 **0/6→2/6**——否定式恰好 prime 它想否认的框架（ironic process theory）。ADR-0002 侧：38 组 A/B 试验 × 6 探针，**措辞改写一律 probe-gated**（先测后改，禁凭直觉）。
- **契约测试锁措辞**：tests/core/server.test.ts:5637 `hook routing prompt-surface contract`——每条 CASE A 串必须以 "redirected" 开头、禁裸大写 BLOCKED、须点名 ≥1 个 ctx_* 替代、禁三族禁语。措辞规则机械化可查，非文档口头纪律。
- **源仓自身的滞后面**：其 CLAUDE.md 散文仍用 "BLOCKED — do NOT attempt" 标题——ADR 纪律与散文面脱节的活例；印证本地「宪法/散文/机制三层须同步」的既有实践。

**本地对位**（机械证据）：[deny-list.py:165](../hooks/deny-list.py#L165) 「；请需求方人工执行，不要尝试绕过（如需展示命令，直接在回复中写文本）」含裸 NOT 构式，**但属 CASE B**（真禁止，停手上报正确），且已附安全替代（「直接在回复中写文本」）恰合 CASE B「MAY suggest」——现状无病。warn 层「确认无误后放行」已是肯定句式。test-self.sh 全文 grep 四条 hook 措辞串（不要尝试绕过/请需求方人工执行/安全闸自身失效/确认无误后放行）**零命中**——「hook 模型面向措辞无契约闸」自推断升机械实证，属缺口记录而非事故记录。**若日后改任何 hook 措辞，按 ADR-0002 须 probe-gated，禁凭直觉改。**

### 3.2 ADR-0001：闸先于根因（完整案例级教训）

为治 #560（五进程同写 SQLite，WAL 失控 238MB、ctx_search 挂死），v1.0.128 上 O_EXCL 锁文件＋`locking_mode=EXCLUSIVE` 双闸；后查明真根因是 #559（`/ctx-upgrade` 后旧 MCP 子进程不死、僵尸双写）＋#561（宿主误检→写跨会话共享路径）。**真因修掉后，锁在解一个已不存在的问题**，反而挡死「双会话同库」合法场景（多窗口用户 `DatabaseLockedError` 无法工作），v1.0.130 整体回滚。评审形态：10 个并行 grill verdicts（UX/SQLite/Security/Perf/Architect/Test/SRE/PM/Data/DevEx）。

三个对位面：①「闸先于根因」反模式——防御闸建立在误诊上，闸本身成新 bug；与本地「机制先裁后立」同族的外部实证，坑卡候选一行。②#561 病形＝跨会话共享路径互踩，正是本地 memory「test-self /tmp 固定路径不抗并发」同病；其修向＝per-session 命名空间（该仓节流态即 `tmpdir/context-mode-guidance-${sessionId}`）。③10 角色 grill 评审与本地评审文化同构，佐证不吸收。

### 3.3 两项待核清账（拷问轮就地清偿）

| 原待核 | 裁定 | 机械证据 |
|---|---|---|
| 「宪法读取事件」compliance-audit 是否已覆盖 | **未覆盖**；吸收成本降档为既有分类器加一分支 | [compliance-audit.py:157](../hooks/compliance-audit.py#L157) 解析 tool_use 块，分支仅 EDIT_TOOLS／Bash/PowerShell（含 EXEC/COMMIT/DIFF 子计数）／Agent／AskUserQuestion，**无 Read 分支**；transcript 解析骨架（bad_lines/sidechain/异型 name 跳过）现成 |
| stop-reminder 是否需要 guidance-throttle 语义 | **设计已覆盖**，guidance-throttle 出清 | [stop-reminder.py:21](../hooks/stop-reminder.py#L21) 明文：未提交改动提醒「独立触发会在每次 Stop 重复打扰」故仅作队列非空时的补充信息；各闸按 state/版本戳分叉 |

### 3.4 微项（零成本留档句）

- **referenced-not-vendored 的 description token 经济学**（UPSTREAM-CREDITS.md）：上游 skill 只引用不内置，理由「装给每个用户＝为他们永不调用的工具付 description token」——对本地 2 skills 的 description 预算文化是外部印证，坑卡一句候选。
- **ADR-0004 指标口径漂移自纠案**：同机数据两算（SLICE B 口径 56% vs 严格压缩口径 95.4%，差 49 点系把 496 份重复捕获的 CLAUDE.md 计入分子）；口径修正以 ADR＋fixture 测试钉死。＝「指标语义变更须入 ADR」外部先例，与本地 compliance-audit「记事实不出结论」同向；同时是 §4 毙 BENCHMARK 数字的依据。

## 4 不收清单

| 项 | 不收理由 | 证据级 |
|---|---|---|
| MCP 服务器／ctx_* 11 工具／SQLite/FTS5 会话库／15 宿主 hooks 适配 | 运行时基础设施，与插件宪法体系不同层；本地无宿主改造需求 | README/ADR/目录级 |
| BENCHMARK 数字 | ADR-0004 自认口径漂移史（56%↔95.4% 同数据两说）；修正后方信，故历史数字不引 | ADR-0004 全文＋BENCHMARK 头 |
| guidance-throttle 机制本体 | §3.3 清账：stop-reminder 设计已含同语义 | 实现段 L36-127 实读 |
| stale-detection | 与本地 sha256 对拍同构、本地已有；外部印证一句即可 | 测试全文 |
| Think in Code | 宪法一行候选经必要性检验未过（边际价值） | SKILL.md |
| 周期重提计数器（默认 10） | 同上；stop-reminder 现无「长会话保鲜」需求 | routing.mjs L53-60 |

## 5 修正轨迹（初析一轮＋拷问一轮·自报不可靠的对账）

| 轮 | 原断言 | 修正 |
|---|---|---|
| 初析 | （方法前置）显式覆盖面声明＋两项待核显式标注——非修正，记方法：agent-skills 三轮教训的前置应用 | — |
| 拷问（全局第四轮） | 四 ADR 只读三 | **ADR-0001 漏读**→补读全文，升入 §3.2 完整案例级（恰沾本地多会话并发痛点） |
| 同上 | ELv2 只读授权段 | 限制段补读：三限制落码，§1.1 口径完整 |
| 同上 | guidance-throttle「一次即永默」 | 实现面＝per-session 文件态＋周期计数器（默认 10）；测试面语义无误、实现面表述欠准 |
| 同上 | 两项待核悬置 | 就地清账（§3.3）：Read 分支缺＝实证缺口；stop-reminder＝已覆盖 |
| 同上 | 「hook 措辞无契约闸」为推断 | test-self 四串 grep 零命中→升机械实证（§3.1） |
| 落档前 | 转录核对拷问轮数 | context-mode 独立拷问**一轮**（此前会话内自称「第三轮」系沿用 agent-skills 累计计数的口误，本稿按实写） |
| 复核 10-21 | 未读声明只列 src/tests | 转录回放全量 tool_use 复核：逐件触达 17/599，未读面补全（hooks 85／configs 44／web 29／scripts 15 等）；§1 未读声明行已改 |

## 6 升格触发线（观察项模式·不触发即长置货架）

1. **hook 措辞变更提案出现**（deny-list／warn 层／stop-reminder／pending-updates 任一改字）→ §3.1 方法适用：两案词表对号＋probe-gated（先行为对照后改，方法可用 agent-skills 稿 §3.1 plugin eval/Tier3，两仓独立收敛互证）；届时再议「措辞契约闸」入 test-self（缺口已实证、事故未发生——无病不立闸）。
2. **并发互踩第二例**（本地首例已在 memory）→ §3.2 ADR-0001 作外部案例引证＋per-session 命名空间修向；坑卡一行可随任一在飞批顺带呈 diff。
3. **合宪性争议需要「本会话是否读过宪法文件」读数** → §3.3 分类器加 Read 分支（compliance-audit 记事实原则不变，只加列不出结论）。

## 7 与 agent-skills 评审稿（2026-10-19）的关系

- **交叉印证**：本仓 ADR-0002「措辞改写 probe-gated」与 agent-skills「plugin eval fires/stays-quiet 对拍」独立收敛于同一命题——**面向模型的文本改动须行为验证，禁凭直觉**。两仓方法论互证提高置信。但印证的产物是「方法可信」，**不是**「立批理由」：两仓都未证明本地有此痛点（§3.1 零事故、agent-skills 稿 §3.1 静态有闸）。
- **裁决联动**：经本次必要性检验，agent-skills 稿 §7 裁决点 1 的倾向应由「B 先行」改判 **C（暂不立批，两稿并存档）**。该格改动已落：2026-10-22 需求方点头，agent-skills 稿 §7 点1 改判 C 已落格（两稿并存档，随 1.2.4 docs 收编批入库）。

## 8 非目标与边界

- **不动消费工程受控文件**：本稿全部内容落本仓 docs/；三 POS 工程零接触。
- **不执行源仓任何内容**：全程只读；MCP 服务器/hooks/测试零执行零安装。
- **不 commit**：SDD 适配（实施者不 commit、呈 diff 评审）；入库随需求方裁决。
- **零摘录**：只记机制、数字结论与出处路径，原文零摘录；ELv2 口径见 §1.1。
