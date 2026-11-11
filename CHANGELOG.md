# crules-flutter CHANGELOG
> 2026-10-23 裁（B 案）：历史段退役（直删，git 可回），本页只记当前版本、当前形态、最近一笔。
> 历史查证走 git tag ＋ docs/ 方案篇（正本）；长内容归 docs/changelog-annex/；黑话解码见
> [清单-黑话白话对照](docs/清单-黑话白话对照-2026-10-22.md)。
## 1.3.7 · 当前形态（本批更新：2026-11-10）
- 单人自用规则 plugin（不参与团队共享）。守护＝hooks 八件（硬拦/高危弹窗/漂移队列/收尾提醒/遵守度账/压缩计数闸/裁决回传/no-op 风暴闸），强度四档明示（硬拦/弹窗人裁/观测/纪律，README 守护节）；分工＝七 agent；规范＝宪法四行指针＋副本＋checklist＋进阶篇（分层下沉 skill references）；沉淀＝memory 九模板＋/distill 闸；完整性＝引用完整性闸（scripts/check-references.py：md 死链＋入口悬空双断面，全分发面缺省，收口必跑、test-self 红绿双向看守）。
- 已落地（1.3.7 no-op 风暴闸批）：hooks/no-op-gate.py 挂 PreToolUse(Bash) 第八件——同 sid 300s 滑窗裸 true/: 计数达 15 后第 16 发 deny、同窗 deny×5 转 ask 人裁弹窗（Q6）；出口契约＝JSON permissionDecision＋exit 0（exit 2 会被 hooks.json 兜底链洗白成静默放行）；fail-open 方向（自失效静默放行，与 deny-list 安全闸的 ask 兜底相反）；无记忆库根静默不介入（Q5）；状态档＝per-sid .json＋append-only ledger.jsonl 双形态（Q4，修剪/孤儿扫落状态件、台账零重写）；匹配面＝剥空白/尾注释后整串等于 true 或 :（复合/绕行形态不计，绕行明知不堵入档）。hooks.json 七件→八件（PreToolUse 第二条 Bash matcher，deny-list 前置）；plan-reviewer 评审 12 发现全处置（阻塞 2：出口契约、状态档双形态）；需求方四裁（独立第八件/双形态台账/无根静默/ask 升级档）；夹具 hooks/test_noop_gate.py 18 检查（含真实兜底链端到端类捕器）；断言 73→74＋结构看守升双 Bash 条目；help.md hooks ×6→×7。立论＝super_printer 7afd4984 T2 子代理 a3202cc0 44min 连发裸 true 446 次（≈52.8M cache_read 空转；转录 L149 自证已知正确姿势 1 秒后仍违背——文案说教不可承重，须机械闸）；方案与评审档随批入库；步骤 0 探针终证（PreToolUse 子代理内触发）挂部署期首观察窗。
- 收口构成不变（一页＋bump 双 json＋README 横幅＋tag），版本一致闸看守（一页版本＝双 json＝README 横幅＝最新 tag 或紧后一版，四值全等＋tag 腿）。
- 最近一笔：1.3.7 no-op 风暴闸批——如上「已落地」；前一笔 1.3.6 引用完整性批同日先收（f08bd35，并行会话产出、需求方裁拆版两笔）。
