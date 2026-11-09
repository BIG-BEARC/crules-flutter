# crules-flutter CHANGELOG
> 2026-10-23 裁（B 案）：历史段退役（直删，git 可回），本页只记当前版本、当前形态、最近一笔。
> 历史查证走 git tag ＋ docs/ 方案篇（正本）；长内容归 docs/changelog-annex/；黑话解码见
> [清单-黑话白话对照](docs/清单-黑话白话对照-2026-10-22.md)。
## 1.3.4 · 当前形态（本批更新：2026-11-09）
- 单人自用规则 plugin（不参与团队共享）。守护＝hooks 七件（硬拦/高危弹窗/漂移队列/收尾提醒/遵守度账/压缩计数闸/裁决回传），强度四档明示（硬拦/弹窗人裁/观测/纪律，README 守护节）；分工＝七 agent；规范＝宪法四行指针＋副本＋checklist＋进阶篇（分层下沉 skill references）；沉淀＝memory 九模板＋/distill 闸。
- 已落地（1.3.4 会话压缩计数闸批）：compact-gate.py 挂 SessionStart(compact|clear|startup)——第 1 次压缩观测注入催快照、≥2 次人裁注入（2＝触发点非硬上限；弹窗三选＝放行一次并记账／落快照后重开／本任务不再提醒；AskUserQuestion 不可用则自动落快照＋继续＋账记未裁决）、「不再提醒」marker 静默但记账不断流、clear/startup 清零＋清扫 >7 天孤儿 sid 文件；compact-gate-decision.py 挂 PostToolUse(AskUserQuestion) 哨兵回传——[compact-gate] 前缀核自家、非自家零文件触达快退、裁决机械回填账行、answers 异型记 unparsed 不猜。状态落消费工程 .claude/memory/compact-gate/（house 形；账行照 .compliance-log 形、零对话正文）。hooks.json 五件→七件（SessionStart matcher 裸竖线防呆、python3||python 兜底链）；emit 同构出口上提 _common 单源（跨 hook 重名绊线咬合后按 1.0.39 先例收编）；orchestration.md 长批压缩「3-5 软上限」收紧为 2 次人裁阶梯。纪律配套：cloud-kb session-management playbook v2（需求方六条＋2 次阶梯＋弹窗人裁语义，独立库随批一笔提交）。夹具 hooks/test_compact_gate.py 21 检查（含变异抽查锁两枚：classify 优先级、坏 state 重计）。方案与评审：docs/方案-会话压缩计数闸-2026-11-09.md（Q1–Q9 全裁后实施）；隔离子代理评审零 L1/L2 可收口；R1 止损线终裁「试点回填即裁」（阶段 3 试点读数回填时点强制三选裁决 留/拆/续期，判据 1/2/4 任一不达→拆为默认）。
- 收口构成不变（一页＋bump 双 json＋README 横幅＋tag），版本一致闸看守（一页版本＝最新 tag＝双 json＝README 横幅，五值须全等）。
- 最近一笔：1.3.4 会话压缩计数闸批——如上「已落地」；探针三行与试点判据读数挂阶段 1/3 回填（消费 cache 刷新后）。
