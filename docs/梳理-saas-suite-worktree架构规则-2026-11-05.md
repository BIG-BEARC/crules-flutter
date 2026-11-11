# 梳理：saas-suite worktree 架构规则

- 对象仓：`/Users/chuxiong/AndroidStudioProjects/ai/saas-suite`（外部工程，非本库消费工程）
- as-of：2026-11-05（全部证据当日实测；该仓演进中，读数会过期）
- 复核：2026-11-10 独立评审通过（14 组主张复测仍真、4 项误差已修——详档 [评审-梳理-saas-suite-worktree架构规则-2026-11-10](评审-梳理-saas-suite-worktree架构规则-2026-11-10.md)）
- 取证方式：规范与命令文档通读＋磁盘/ git 命令实测（`git worktree list`、`find` 指针文件、`rev-parse` 双值比对、子仓登记表）；TAPD ID 语义为 README §2 明文＋需求方口头双确认

## 总览：一个 ID、四层结构

```
TAPD 需求 ID ─── 一个 ID 贯穿三处：目录名 · 主/子仓分支名 · commit scope
      │
 ④ 工具层   doctor(只读)→autofix→worktree add→worktree-init→/cbg-dev→清理
 ③ 治理层   worktree.json 唯一配置源＋规范文档＋三道写入门禁
 ② 结构层   主仓 worktree＋受影响子仓 worktree（嵌子模块路径、同名分支）
 ① 机制层   git linked worktree：共享对象库·独立 HEAD/index·双指针
```

## ① 机制层（纯 git 原生，零定制）

- linked worktree：所有树共享一份 objects/refs；每树独立 HEAD＋index；`.worktrees/<id>/.git` 指针文件与 `.git/worktrees/<id>/` 管理目录（含 HEAD、index、commondir、gitdir）互指。
- 子仓（63 个子模块）真身＝`.git/modules/<路径>`，detached 在主仓 pin 的 SHA 上；子仓 worktree 从真身挂出，登记在子仓自己的 worktree 表——主仓 `git worktree list` 看不到它们。
- 宿主无关：IDE、CLI、Agent 都当普通目录用。

## ② 标识与结构规则

- ID 即 TAPD 需求编号（README §2：`feature_id="<TAPD需求编号>"`），一处获取三处使用：目录 `.worktrees/<id>/`、主仓＋子仓分支 `feature/<id>`（`sharedPrefixForSubrepositories: true`，精确同名）、commit scope `feat(<id>):`。外部需求系统与 git 状态双向可追溯。
- 双层结构：主仓 worktree 必建；子仓只建本次 Feature 波及的（明令禁无差别初始化全部子模块）；子仓 worktree 放进主 worktree 对应的子模块路径——每任务一棵完整可直接构建的目录树。
- 实况（as-of 当日）：三任务（1058651 / 1095297 / 1095602）全带 `src/app/saas-cashier` 子仓 worktree，1058651 另带 saas-cashier-light；worktree 命名同仓唯一（后缀实名为 `saas-cashier1`／`saas-cashier2`，无连字符）。
- 建树前 `.worktrees/` 必须已被 gitignore（防整棵工作树入库）。

## ③ 治理层：唯一配置源＋强制边界

- `.agents/runtime/worktree.json`（10 行）是目录根、分支前缀、适用范围的机器可读唯一配置源；`/cbg-dev`、手工开发、一切 Agent 工具都必须读它，约定不落第二处。
- 强制矩阵：Feature 开发默认强制 worktree、不再逐次询问；豁免仅三条——普通纯 `docs/` 任务、只读分析、代码评审；走 `/cbg-dev` 时豁免全部作废（优先级：cbg-dev 强制 ＞ 纯文档例外），只改文档也必须在树里。
- 已在合规树中禁重复建树。

## ④ 门禁：三道防线，全是机械判据

1. 开工自检：首次写文件前记录 `git rev-parse --git-dir` 与 `--git-common-dir`——两者相等＝仍在主 checkout＝不得写（实测：主仓两者同为 `.git`；树内一为 `.git/worktrees/<id>`、一为 `.git`）。
2. `/cbg-dev` preflight：写入任何 Feature 状态（需求快照、绑定、manifest、事件账本）之前，校验「linked worktree＋当前分支精确等于 `feature/<feature-id>`」；不合规返回 `FAIL`＋`reasonCode=cbg-dev-worktree-required`＋`requiresAdmin=false`（定性为成员站错位置，非管理员故障）。
3. 违规定性：读过规则仍在主 checkout 写实现文件＝执行协议失败，必须先迁移恢复主工作区再继续。

另有工具优先级：有原生 worktree 能力（如 EnterWorktree）先用原生，`git worktree add` 只是 fallback——避免宿主管不到的幽灵状态。

## ⑤ 初始化协议（凭据是重点）

- 建树后必跑 `./scripts/cbg-worktree-init`：按当前分支的 MCP Registry，从 Git common dir 的私密凭据库为本树本地渲染 `.mcp.json`／`.codex/config.toml`——Token 只落本树、不进 git、不跨树复制。
- 失败关闭：缺凭据、新 Provider、共享库损坏→初始化直接失败；此时才由人在可信 checkout 的真实交互终端跑 `cbg-env-autofix`（隐藏输入；轮换须显式 `--rotate-mcp-credentials`）；严禁在聊天中发 Token。
- 权限分层：Doctor 只读诊断／Autofix 只修私密配置与本地资产／Agent 生成资产由管理员或 CI 随仓发布。
- 开工基线：分别记录主仓与各子仓基线 SHA＋跑与改动范围匹配的基线检查；基线红先报告，不得默认算在本次改动头上。

## ⑥ 提交纪律

- 顺序：子仓先（中文约定式提交，另有 `.agents/rules/git-commit.md`）→ 主仓后（子模块引用＋需求文档）；主仓禁 `git add .`／`-A`，按路径精确暂存。
- 检查点提交：Agent 可自动做本地提交（逻辑拆分＋精确暂存＋提交信息校验器复核 `scripts/ci/check_commit_messages.py`，主/子仓各用各的基线 SHA）。
- 自动边界：本地提交为止——push、PR、合并、删分支必须等人显式指示。

## ⑦ 清理纪律

- 时机：须人显式表达「本地合并并清理」语义；单纯确认「已合并」不构成清理授权。
- 范围：仅限自建受控目录（`.worktrees/` 或 worktree.json 配置处）；IDE/Codex 等宿主管理的树不碰，交还宿主。
- 顺序：子仓先、主仓后；只用非强制命令 `git worktree remove`／`git branch -d`，被拒（未提交改动/未合并提交）即留现场人工处理，禁 `--force`／`-D`。

## ⑧ 入口与状态

- 成员标准流程八步：更新 master＋子模块→`/cbg-env-doctor`→必要时 `cbg-env-autofix`→建树→`cbg-worktree-init`→`/cbg-dev <id>` 启动或 `/cbg-dev` 恢复→人工门禁→验证提交交付。
- `/cbg-dev` 是唯一入口（`/feature-development` 已弃用）；需求经 TAPD MCP 只读白名单拉成快照；工作流状态（manifest.currentRun／events.ndjson）设计上放 `.saas-dev/`（已 gitignore）。
- as-of 实况：`.saas-dev/` 主仓与三树均不存在——现存三任务是手工路径建树或账本已清，`/cbg-dev` 全流程无在盘实例。

## 设计原则提炼

1. 一 ID 贯穿全链路——需求系统↔git↔提交历史三方互相指认；
2. 配置唯一且机器可读——约定不靠人记；
3. 门禁全是机械判据（指针比对、精确分支名）——不赌 Agent 自觉；
4. 失败关闭——凭据/共享库异常宁可停机不降级；
5. Agent 权限最小化——自动范围止于本地提交；
6. 破坏性动作授权显式化——合并确认与清理授权解耦，非强制命令兜底。

## 边界与未查项（as-of 当日）

- 1095297 与 1095602 的未提交改动（2 项 / 15 项）内容未展开。
- 1095602 与 1058651 主仓共享 lineage（284b925bb、80ea80bce 两笔同 SHA），推断为前后续需求关系，未见文字记载。
- 「领先 2003 提交」读数：2026-11-10 复核对任何 ref 对均不复现、成因未查，数字本身弃承重；可确认的是分支基线即子模块 pin（merge-base(master, feature-tip)＝pin 本身，v2.10.10），任务提交仅 +14——「非任务提交量」定性成立，原「pin 老于分支基线」因果句与实测相悖，已撤。
- `/cbg-dev` 工作流引擎全貌（快照/复审投影/receipt/管理员视图/improvements 生命周期）未展开，本文仅覆盖其与 worktree 相关的门禁部分。

## 源文件索引（saas-suite 内）

| 件 | 路径 |
| --- | --- |
| 规范本体 | `.agents/rules/git-worktree.md` |
| 唯一配置源 | `.agents/runtime/worktree.json` |
| 流程入口 | `README.md` §普通研发人员标准流程 |
| 门禁执行 | `.agents/commands/cbg-dev.md` |
| 凭据渲染 | `scripts/cbg-worktree-init` → `scripts/agent/cbg_environment.py` |
| 环境诊断/修复 | `/cbg-env-doctor`（只读）、`./scripts/cbg-env-autofix` |
