# agent-skills 吸收评审稿（2026-10-19 外源分析）

> 状态：**已裁·存档**（2026-10-22 需求方裁 §7 五点：点1 **C 暂不立批、两稿并存档**〔照 context-mode 稿 §7 联动格〕；点2 已毙提案区开 .review-ledger 新区；点3 平台事实转触发制；点4 随 1.2.4 收编批入库；点5 随点1 悬置——明细见 §7 裁结列）——三轮「确定？」拷问毕：关键断言已机械核验，推断均显式标注，修正轨迹见 §5。本稿只落文档：未动任何受控文件、未执行源仓任何脚本、未 commit（呈工作区 diff 评审）。日期：2026-10-19 · 来源：addyosmani/agent-skills（本地快照 `/Users/chuxiong/Downloads/ai资料/agent-skills-main`，216 文件 1.6M，https://github.com/addyosmani/agent-skills ）· 许可：MIT（Copyright 2025 Addy Osmani，LICENSE 实读确认）· 面向对象：维护者/需求方 · 裁剪档位：标准（全节）。
> 一句话结论：方法论 skill 大半与本地体系重叠（superpowers＋宪法＋SDD 已覆盖）；真正缺口在**验证面**——本地对 skill 只有静态形状闸、没有行为面测试；其余为若干可单摘的机制点与三项机制储备。

## 1 来源与方法

| 项 | 内容 |
|---|---|
| 分析对象 | skills 25 个（190–400 行/个）＋ evals（三层评测）＋ hooks 4 件 ＋ scripts 校验器五件套 ＋ references 7 份 ＋ agents 4 件 ＋ commands 9 件 ＋ docs |
| 方法 | 全程只读（零执行源仓脚本/零安装）；三轮增量拷问，每轮以机械证据修正前轮结论 |
| 覆盖面 | skills 25/25（全文或目录级）、references 7、hooks 4、scripts、commands 9、agents 4、CONTRIBUTING、evals 主干；**未逐件读：docs/ 17 件中 16 件**（10 宿主接入 *-setup＋other-hosts，6 接入引导向 adoption/comparison/getting-started/onboarding/agents/advanced-per-agent，均与吸收判断无关）——2026-10-21 转录复核修正：原记「未读仅 8 份」不可复现，以此行为准 |
| 域不对口实证 | `grep -ril "flutter\|android\|swiftui\|uikit"` 全 skills＋references 仅 1 命中（性能清单一句「中端 Android 真机测 INP」，Web 性能语境顺带）——移动端实质内容为零 |

## 2 结论速览

| 优先 | 项 | 一句话 | 建议落点 | 成本 |
|---|---|---|---|---|
| 1 | evals 行为面（Tier2 路由对拍＋plugin eval fires/stays-quiet 对＋压力例） | 本地「静态有闸、行为无测」的直接补位 | test-self 断言区＋plugin eval 一次性跑 | Tier2 半天；plugin eval 有 token 成本 |
| 2 | 台账加「已毙提案」区 | 防多会话重复提出已被证据毙掉的方案 | .review-ledger 新区（倾向） | 近零 |
| 3 | orchestration 反模式镜＋平台事实三条 | 评审 agent 结构的固定检查面 | 进阶/Agent编排.md 增补 | 一节 |
| 4 | 机制点簇（constraint 五偷懒路径/循环性分级/Ratchet、doubt 四分类/怀疑剧场、含糊≠授权） | 逐条单摘，非整 skill 收编 | 宪法自检/坑卡/SDD 纪律各一行至半节 | 低 |
| 5 | 机制储备（simplify-ignore 遮蔽、sdd-cache exit-2＋ETag 委托、floor-guard 0/1/2 契约） | 现在记档，遇场景再启 | 坑卡/本稿留档 | 启用时再计 |

## 3 逐项评审卡

### 3.1 evals 行为面（优先 1）

**源仓机制**（evals/README.md＋run-evals.js，全文已读）：

- **Tier 2 路由测试**（免费、CI 安全）：正例 prompt 按 TF-IDF 对全部 description 排序，本 skill 须入 top-k（rank-1 率 CI 钉 ≥95%）；负例 prompt 带 `owner` 字段指认应压过它的邻位 skill——把负例从「真空通过」变成**成对路由测试**；两两 description 余弦相似度 ≥0.75 报错、≥0.5 警告（run-evals.js COLLISION_WARN/ERROR 常量实码在）；rank-1 下限作棘轮只升不降。
- **Tier 3 行为测试**（花 token、不进 CI）：execution 型在一次性 git 仓真跑，fixtures 物化后按 `expectations[]` 判 stream-json 全 trace；**压力例**（time-pressure／authority-pressure／sunk-cost fixtures 三实文件在）验证流程在 prompt 劝你跳过时是否仍守住。
- **`claude plugin eval`**（CLI ≥2.1.269）：每个能力配「该触发」＋「该闭嘴」一对 case，grader 三件（`tool_used: Skill` 正则＋回复判据 llm＋双臂消融 Δ）。

**本地缺口实证**：test-self.sh:1013-1022 的 D5 断言（parity-rewrite description 触发-only、工作流摘要句即红）是**静态形状闸**；grep 全仓无正/负例 prompt 对、无排序断言、无 plugin eval case。「description 合格时，skill 是否真的在该触发的 prompt 上触发、在邻位 prompt 上闭嘴」无任何测试。

**外部教训三条**（源仓实跑数据，坑卡候选）：① description 措辞是路由杠杆——TDD skill 加「即使代码内联粘贴、请求未提测试也适用」一句，触发 6/24→19/24，邻位 must-not-fire 保持 0/24；② skill 触发是随机的——读 Δ 与报告而非退出码，报数字须钉 `--model` 并记录 CLI 版本；③ case turn 预算 ≥10（经 slash command 两跳触发）。

**落点建议**：① Tier2 最小版——对本仓 2 个 skill 与邻位写正负例对；注意**不可直搬 run-evals.js**（英文 stopword/stem，本仓 description 是中文，须换字符 n-gram 或分词，见 §2.5 反噬面 1）；② plugin eval 一对——parity-rewrite 正例（「复刻/重写/迁移」族）＋负例（新功能开发，owner=flutter-rules），`claude plugin eval plugin/` 本机 2.1.286 实测可用（--help 验过，支持 --ablation 双臂）。

### 3.2 台账「已毙提案」区（优先 2，本轮降级修正）

**源仓机制**：evals/skill-impact.md——append-only 表，记录被 eval 证据否决的 skill/description 改动提案，含 rank-1 分数「before→after」列，目的为防贡献者重复提交已被毙方案。

**降级修正**：源仓该表**空模板零条目**（cat 全文实证）——机制在源头未经实战检验，其经验实际写在 evals README 散文里（「修 description，不修 eval」）。吸收它「有效」的证据不来自源仓，来自本地文化：.review-ledger 已有 R1–R14 实条目，缺的只是「已毙提案」这一个区。

**落点建议**：.review-ledger 加一区（列：日期/提案/毙因/机械证据/替代路径）；配套在裁决流程（distill 或方案评审闭环）加一句「提案被证据否决时入该区」。成本近零。

### 3.3 orchestration 反模式镜＋平台事实（优先 3）

**源仓机制**（references/orchestration-patterns.md，370 行全文已读）：治理规则「用户/slash command 才是编排者，人格不调人格」；五个认可模式（直调/单人格命令/扇出合并/用户驱动序列/研究隔离）；四个命名反模式——路由人格（纯转发无域值）、人格调人格（摘要丢上下文、失败模式相乘）、转述型编排器（每跳损信息＋2× token）、深人格树（编排深度封顶 1）；扇出前四问核验单；**收录新模式四门槛**（真实用过 ≥2 次＋仓内有实例＋说清既有模式为何不行＋能描述反模式影子）。

**平台事实三条**（源仓宣称，**未对官方文档核**）：plugin agents 的 `hooks`/`mcpServers`/`permissionMode` frontmatter 被静默忽略；teammate 模式下 persona 的 `skills` 字段失效；并行扇出须单回合多个 Agent 调用。核对手段现成：code.claude.com 文档 URL 加 `.md` 取带表原文。**未核前不入宪法。**

**落点建议**：进阶/Agent编排.md 增补「反模式镜」一节，对照本地 7 agents（backend/frontend/i18n/platform/reviewer/plan-reviewer/error）逐一过；四门槛并入本仓「新增机制/模式」裁决惯例。

### 3.4 机制点簇（优先 4，逐条单摘）

| # | 摘什么 | 源证据 | 本地落点 |
|---|---|---|---|
| 1 | **五偷懒路径 diff 监视单**：阈值被调低／测试变易（.skip、断言抽走）／检查器被静音（istanbul ignore、nosemgrep、gitleaks:allow、Stryker disable 四具名）／半成品（stub、空 catch、TODO 占位）／豁免表冒出新行。口诀「收紧无声，放松有声」 | constraint-driven-development SKILL Step 6 全文 | 对照 compliance-audit.py 与既有豁免闸逐条查缺（**对照动作未做**，属启用时任务） |
| 2 | **检查循环性三级**：External（外部工具意见）／Project（自有规则）／Suite（自写测试）。「全是 Suite 级的 bar 不值钱」 | 同上 Step 6 末 | 宪法自检问题成文：「本闸集至少一个外部意见？」——本地已有外部意见实践（实跑三工程只读、网络评审），未成文为固定自检 |
| 3 | **Ratchet 表**：「Measured, not yet enforced」——记今天的值＋方向（只升不降）＋容差 0.5% | 同上 Step 7 | 实跑观测行升级候选（双工程 v1.1.6 掉队由观察项转棘轮） |
| 4 | **评审材料隔离**：只传 ARTIFACT＋CONTRACT，不传 CLAIM——把结论喂给评审者＝让它验证结论 | doubt-driven-development SKILL Step 2/3 | plan-reviewer 已做完全隔离；此条是把原理明文化（呈评审材料纪律一行） |
| 5 | **findings 四分类**：契约误读→可执行→可接受代价（须明示）→噪音；fresh reviewer 缺上下文也会错，不因「新」盲从 | 同上 Step 4 | 方案评审闭环的回收纪律增补 |
| 6 | **3 轮封顶＋怀疑剧场信号**：≥2 轮有实质发现却 0 条可执行＝表演怀疑，停手上抛 | 同上 Step 5/Red Flags | 坑卡候选 |
| 7 | **含糊≠授权**：hedged 回应（「看起来行」「大概可以」）不算批准，须无歧义 affirmative | .claude/commands/build.md Step 4 全文已读 | SDD 执行纪律一行（「呈 diff 点头」的有效性判据成文） |

### 3.5 机制储备（优先 5，记档不立批）

| 储备 | 机制要点 | 启用场景 |
|---|---|---|
| **simplify-ignore 遮蔽**（hooks/，文档全文＋脚本头 40 行已读） | PreToolUse Read 把保护块换成内容哈希占位符（模型不可见）→ PostToolUse Edit/Write 还原重遮 → Stop 兜底展开；.recovered 崩溃恢复；bash 5.2 patsub_replacement 陷阱处理（与本地 bash 5.3 多字节教训同族） | 与 deny-list 互补：deny 拦*命令*（禁碰），遮蔽拦*视野*（看不见）。消费工程受控文件出现「须读不可改」需求时再启。**启用前先析与 deny-list 的判定序**（§2.5 反噬面 5） |
| **sdd-cache 诚实缓存**（SDD-CACHE.md 全文已读） | 三模式：① exit 2 拦截即注入（stderr 载荷回给模型作工具结果）＝钩子原语；② 无 TTL、新鲜度全权委托源站 ETag/304 再验证；③ 无验证器的响应一律不缓存 | 「缓存但不信内存」＝「验证须外置」的缓存版。webReader 双路 429 场景可参考；坑卡一行候选 |
| **floor-guard 参考实现**（references/floor-guard.md 全文已读） | 退出码 0/1/2 且「2 永不读作 0」（无 merge-base/非 git 仓→明拒不装干净——与 test-self「插件 cache 非 git 仓显式拒绝」同原则独立收敛）；阈值方向配对算法（方向读不出则任何变动都报——守不住沉默是错误默认）；删豁免行＝收紧＝静默放过 | 日后做质量条闸（CONSTRAINTS 类）的现成骨架 |

## 4 不收清单

| 项 | 不收理由 | 证据级 |
|---|---|---|
| TDD／debugging／planning／incremental／spec-driven／context-engineering | superpowers 同名 skill＋canonical 体系覆盖 | description＋骨架 |
| interview-me | brainstorming 覆盖；「Q＋GUESS 一问一猜、95% 置信停手」微纪律可单摘一行，随裁决顺带 | 前 100 行 |
| frontend-ui／browser-testing／webperf／accessibility／security／performance／ci-cd／observability／shipping | Web 栈不对口（§1 grep 实证） | description＋grep |
| git-workflow-and-versioning | 收口批五件套＋版本滚动规则＋tag 闸覆盖；「tag 唯一事实源」本地踩坑后已机制化 | 目录＋关键节 |
| code-simplification | /simplify 内建覆盖五原则；后半 TS/Python/React 语言专节不对口 | 目录 |
| definition-of-done | AC vs 常备门槛之辨被 checklist.md＋closing-tiers 覆盖 | 全文 |
| documentation-and-adrs | 方案稿＋裁决记忆覆盖；仅「旧 ADR 不删、只 supersede」一句可取 | 关键节 |
| deprecation-and-migration（expand/contract 五步） | 生产库迁移通用知识；sqflite 迁移场景出现时挂 flutter-rules 坑库指针即可 | 关键节 |
| idea-refine 全套附件（SCAMPER/HMW/JTBD/pre-mortem） | 产品创意域，质量不低但不对口 | 抽读 |
| hooks（session-start/simplify-ignore 脚本本体/sdd-cache 脚本本体） | 本地 hook 体系更完备；机制要点已入 §3.5 储备 | 头部＋文档 |
| commands 9 件 | 薄编排壳（16–72 行）；机制面与授权批文化重叠 | ship/build 全文＋其余清单 |
| agents 4 件 | 五轴/角色与本地 reviewer/plan-reviewer 同位 | 头部 |
| 宿主接入 docs 8 份 | 接入向，与吸收无关 | 未读（声明无关） |

## 5 修正轨迹（三轮拷问增量，自报不可靠的对账）

| 轮 | 原断言 | 修正 |
|---|---|---|
| 1 | 「本地对 skill 触发零覆盖」 | 复核 test-self.sh 后改「**静态有闸（D5）、行为无测**」——test-self 72KB 远超初轮扫读认知 |
| 1 | 「MIT 协议允许」为推断 | LICENSE 实读确认；`claude plugin eval` 2.1.286 本机 --help 实测可用 |
| 2 | 首轮「重叠居多、无遗漏」 | 补读后新增 5 项：已毙提案区／orchestration 反模式镜／simplify-ignore／sdd-cache／floor-guard 细节＋skill-anatomy 机理印证（D5 的外部出处：「description 含流程步骤→模型跟摘要走不读全文」） |
| 3 | 已毙提案区列优先 2「价值高」 | 源仓空表零条目实证→降级理由改为「本地台账文化的自然延伸」，位次保留 |
| 3 | 「域不对口」为推断 | grep 机械实证（全仓 1 命中）；commands 全读；git-workflow/code-simplification 目录翻毕；**新增**含糊≠授权 |
| 复核 10-21 | 「未读仅 8 份宿主接入文档」 | docs/ 实为 17 件、逐件仅 skill-anatomy.md——未逐件 16 件（10 接入＋6 引导向）；原数不可复现，§1 覆盖面行已改 |
| 裁 10-22 | §7 点1 倾向「B 先行」 | 照 context-mode 稿 §7 联动格改判 C——两稿必要性检验同判；五点裁结落 §7 裁结列 |

## 6 Review Focus（评审双用·五类最可能反噬面）

1. **Tier2 中文适配成本被低估**：run-evals.js 的 stopword/stem 是英文词面法，本仓 description 是中文——直搬必红。最小版须先定中文相似度口径（字符 n-gram 或分词），否则「半天」变烂尾。裁决前请评审人确认接受此口径选型负担。
2. **plugin eval 随机性**：源仓实测 5/7、21/27——单次红≠缺陷，须多跑读 Δ；**不可把 stochastic 结果直接写进 test-self 断言**（test-self 须确定性），plugin eval 只能是按需人工跑的独立层。
3. **压力例入 test-self＝自循环**：压力 fixtures 若由本地脚本判，属 Suite 级——按 §3.4-2 循环性分级，不得宣称外部效力；真正的压力验证仍是实跑/网络评审那类外部意见。
4. **已毙提案区进 .review-ledger（本机私域不进 git）**：跨机不可见，多会话同机前提才成立——与本仓「不参与团队共享」裁决一致，但若未来换机须随 memory 体系迁移。
5. **遮蔽 hook 与 deny-list 叠加序未析**：两者同挂 PreToolUse 时的执行顺序、遮蔽态下 deny 判定读到的是占位符还是原文——储备项启用前必须先析，本文档只记机制不背书启用。

## 7 待裁决点

| # | 裁决 | 选项 | 裁结（2026-10-22 需求方） |
|---|---|---|---|
| 1 | 是否立批吸收 | A 立批，先 §3.1 Tier2 最小版／B 只做零成本两行（已毙提案区＋含糊≠授权）／C 暂不立批，本稿存档 | **C 暂不立批、两稿并存档**——照 context-mode 稿 §7 联动格改判（原倾向「B 先行」作废）：必要性检验全项未过，两仓均未证明本地痛点，「印证的产物是方法可信，不是立批理由」；原倾向 B 的两行亦同判（零痛点实证） |
| 2 | 已毙提案区落点 | A .review-ledger 新区／B canonical 新件 | **A 已执行**（2026-10-22 开区，本机私域零 commit；首条目＝10-19 字符串考古假阴） |
| 3 | 平台事实三条 | A 先对官方文档核再定去留／B 不入 | **触发制**——本仓哪天要用 agents frontmatter 的 hooks/mcpServers/permissionMode 或 teammate skills 字段，先核（文档 URL 加 .md）再定去留；现无消费面不预核 |
| 4 | 本稿处置 | A 随批入库 docs/／B 留存工作区不入库 | **A 已执行**——随 1.2.4 docs 收编批入库 |
| 5 | Tier2 扫描面 | A 仅本仓 2 skills 对拍／B 含 superpowers 邻位（英文词面） | **随点1 悬置**（C 裁下 Tier2 不建，扫描面无从谈起；触发线复现时按 A 重议） |

## 8 非目标与边界

- **不动消费工程受控文件**：本稿全部建议的落点均在本仓；三 POS 工程零接触。
- **不执行源仓任何内容**：分析全程只读；run-evals/validate-*/hooks 脚本零执行。
- **不 commit**：SDD 适配（实施者不 commit、呈 diff 评审）；入库随需求方裁决后的批走。
- **摘录注记**：源仓 MIT；本文档只记机制与出处路径，原文零摘录；日后若整段引用入坑卡/canonical，留来源注记（本仓不参与团队共享，无分发义务）。
