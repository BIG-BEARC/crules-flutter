# 评审：梳理-saas-suite-worktree架构规则-2026-11-05.md

- 评审对象：`docs/梳理-saas-suite-worktree架构规则-2026-11-05.md`（as-of 2026-11-05，untracked）
- 评审方式：plan-reviewer 后台 agent 全程只读独立复核（2026-11-10，距 as-of +5 天）；stat/ls/cat/grep＋git worktree/rev-parse/status/ls-tree/merge-base/rev-list/describe 等只读命令，零写操作、未 cd 进任何 worktree
- 总裁决：**需修订后可入库**——14 组主张复核仍真；4 项误差/漂移（写作期计数/因果错误 3＋记法 1）；修订已当场落回原文
- 本文为评审原文逐字落盘（下方引文即 agent 回传报告，未经改写）；处置记录在文末

---

## 评审原文

### 一、事实面复核（今日实测 vs 文档主张）

**仍真（14 组核过）**：

1. README §2 明写 feature_id＝TAPD 需求编号 — `README.md:60`，归属正确（`:54` 即「#### 2. 为 Feature 创建隔离 worktree」）
2. worktree.json 在位，四字段全对：worktreeRoot=`.worktrees`／branchPrefix=`feature/`／appliesTo=[cbg-dev, manual-feature-development]／sharedPrefixForSubrepositories=true — `.agents/runtime/worktree.json:3-9`；mtime 2026-10-20 早于 as-of，未漂移
3. `git worktree list`＝master＋1058651/1095297/1095602 三树，分支名 feature/<id> — 无多出、无消失
4. 子仓登记方式：三树 saas-cashier 各挂 feature/<id> 子分支、登记于子仓自己的表（`.git/modules/src/app/saas-cashier`），主仓表不可见；saas-cashier-light 仅 1058651 挂，另两树该路径 git 上溯回主仓表 — 与文档逐字一致
5. `.gitignore:60` `.worktrees/`、`:61` `/.saas-dev/`
6. 全部索引件在位：scripts/cbg-worktree-init（可执行）、scripts/ci/check_commit_messages.py、scripts/agent/cbg_environment.py、scripts/cbg-env-autofix、.agents/rules/git-worktree.md＋git-commit.md、.agents/commands/ 下 cbg-dev/cbg-env-doctor/cbg-env-autofix.md
7. rev-parse 双值：主仓 `.git`/`.git`；树 1058651 为 `.git/worktrees/1058651` vs `.git` — 与文档 :39 逐字一致
8. 63 子模块（grep -c `^\[submodule` .gitmodules＝63）；真身 detached＝pin（ls-tree HEAD＝b1c14b7b5＝describe v2.10.10）；指针互指四件 HEAD/index/commondir/gitdir 全在 — `.git/worktrees/1058651/`
9. 治理层逐条对源：强制 worktree 不再询问（git-worktree.md:9）、豁免三条（:11）、cbg-dev 豁免作废（:12）、禁重复建树（:10）、禁无差别初始化（:26）、原生优先（:13）、失败关闭（:44）、autofix 真实终端＋隐藏输入＋显式 --rotate-mcp-credentials（cbg-env-autofix.md:9、scripts/cbg-env-autofix:6）、提交顺序＋禁 add . /-A（:56-60）、检查点提交＋校验器（:64-76）、自动止于本地提交（:68）、清理三段（:81-97）、基线先报（:51-52）
10. cbg-dev.md:8 preflight 门禁逐字吻合：reasonCode=cbg-dev-worktree-required＋requiresAdmin=false＋FAIL＋四类状态（需求快照/绑定/manifest/事件账本）禁写
11. /feature-development 已弃用（该文件全文即弃用公告）；/cbg-dev 唯一入口（README:84）
12. manifest.currentRun／events.ndjson／.saas-dev 出处在案 — `.agents/workflows/feature-development/README.md:56,69,83`、README.md:85
13. as-of 实况三件今日复测：.saas-dev 四处不存在；未提交改动 1095297＝2、1095602＝15（与文档同数，5 天零漂移）
14. lineage 两 SHA（284b925bb、80ea80bce）均实测为 feature/1058651 与 feature/1095602 共同祖先（merge-base --is-ancestor 双 YES）

**误差/漂移（4 项）**：

- **建议**「7 行」实为 10 行 — `wc -l .agents/runtime/worktree.json`＝10；mtime 2026-10-20（早于 as-of），系写作时计数错误而非漂移
- **建议**「领先 2003 提交系 pin 基线老于分支基线所致」因果句与实测相悖：merge-base(master, feature-tip)＝pin 本身（分支基线即 pin，describe＝v2.10.10-14-g6233bf145），不存在「pin 老于分支基线」；今日任何 ref 对均无 2003（pin→master 0、→origin/master 13、→dev 54、→tip 14、分支总数 10471/12464）→ 数字无法核，「非任务提交量」定性成立（任务提交仅 +14），但因果断言被证据否定
- **备注**「saas-cashier / -1 / -2 后缀」实名无连字符：管理目录实测 `saas-cashier1`／`saas-cashier2` — `.git/modules/src/app/saas-cashier/worktrees/`；「同仓唯一」实质成立
- **备注**「九步」实际八阶段：README 流程图（:15-24）八行，文档自己列举的也只八项

**无法核**：「需求方口头双确认」（口头证据，非可检件）；「领先 2003」数字本身（as-of 观测今日不复现）。

### 二、内部一致性

- 四层总览（①-④）与正文八节：⑤-⑧（初始化/提交/清理/入口）超出四层名目且未声明映射，但内容分别归属工具层与治理层操作面，无矛盾 — 备注
- 「三道写入门禁」总览与 ④ 三项一一对应；⑥「Agent 可自动本地提交」与⑦「清理须显式授权」分域不冲突；纪律条目间未发现相互矛盾
- as-of 节奏自洽且是本件最强项：易变实况（:28、:68、:81-83）全部显式挂 as-of，与规则面（③-⑦，引源文件、源 mtime 未变）清晰分离

### 三、入库裁决：需修订后可入库

必改点（入库前四件）：

1. `:33`「7 行」→「10 行」（或删行数只留字段描述）
2. `:83` 因果句改写或降级：按实测改为「分支基线＝pin（v2.10.10），任务提交仅 +14；『领先 2003』读数 as-of 后未复现、成因未查」
3. `:28` 后缀记法对齐实名 saas-cashier1/2
4. `:66`「九步」→「八步」

适配面评估：本仓 docs/ 已有 dated 快照型文件入库先例（`git ls-files docs/` 含 方案-会话压缩计数闸-2026-11-09.md 等），「梳理-」型同类；本仓 memory 已存 saas-suite worktree/TAPD 事实条目，本件是其在飞批（1095297）的证据底座，放本仓有实际用途。快照口径够格：规则面引源可回溯、实况面今日复测仍真。

**边界问题（只提不裁，需求方定）**：记忆载「云店业务/硬件/纪律单源在 cloud-kb」——saas-suite 系云店套件，其 worktree 工程纪律类梳理是否应归 cloud-kb engineering/ 与单源边界存在张力；但本件性质是「工程过程快照＋服务本仓批务」而非业务域知识，两种归置均有理据，须需求方显式裁。另：入库时是否按本仓习惯补一行「2026-11-10 独立复核通过」脚注，亦归需求方定。

---

## 处置记录（2026-11-10 当场）

| 评审发现 | 处置 |
| --- | --- |
| 必改 1「7 行」 | 已改 `:33`→「10 行」 |
| 必改 2 因果句 | 已改写 `:83`：数字弃承重＋分支基线＝pin＋任务提交 +14＋原因果句明撤 |
| 必改 3 后缀记法 | 已改 `:28`→「saas-cashier1／saas-cashier2，无连字符」 |
| 必改 4「九步」 | 已改 `:66`→「八步」 |
| 边界问题（cloud-kb vs 本仓、复核脚注） | 只提不裁——归需求方，见呈报表 |
