# crules-flutter CHANGELOG
> 2026-10-23 裁（B 案）：历史段退役（直删，git 可回），本页只记当前版本、当前形态、最近一笔。
> 历史查证走 git tag ＋ docs/ 方案篇（正本）；长内容归 docs/changelog-annex/；黑话解码见
> [清单-黑话白话对照](docs/清单-黑话白话对照-2026-10-22.md)。
## 1.3.8 · 当前形态（本批更新：2026-11-12）
- 单人自用规则 plugin（不参与团队共享）。守护＝hooks 八件（硬拦/高危弹窗/漂移队列/收尾提醒/遵守度账/压缩恢复 v2 注入件＋PreCompact 观测件/no-op 风暴闸），强度四档明示（硬拦/弹窗人裁/观测/纪律，README 守护节）；分工＝七 agent；规范＝宪法四行指针＋副本＋checklist＋进阶篇（分层下沉 skill references）；沉淀＝memory 九模板＋/distill 闸；完整性＝引用完整性闸（scripts/check-references.py：md 死链＋入口悬空双断面，全分发面缺省，收口必跑、test-self 红绿双向看守）。
- 已落地（1.3.8 压缩恢复 v2 批）：compact-gate.py 换血为指针＋速率形——SessionStart(compact) 指针注入（「原文未损：transcript 路径＋span 直取纪律」，路径三级降级：输入字段→推导＋mtime 弱校验→目录指引）＋速率窗 runaway 收尾建议（主 auto ≥4/90min、混桶 any ≥8/90min〔sidechain 无键现行走档〕、子代理 sub ≥20/24h 只记 runaway-sub 零注入〔D7〕；回落半阈再武装、滚动 24h 上限 2）＋startup 断点回读（近 24h runaway 或任一 sid ≥3 发→断点指针，路径核验失败静默）；新件 hooks/compact-observe.py（PreCompact 观测：trigger/sidechain 分桶计数＋schema 2 账行，零拦截零注入；写序＝ledger 先行防双记）；共享库 hooks/_compact_core.py；翻账件 scripts/compact-report.py（只读零正文、双 schema 兼容——v1 存量 33 行计频次不迁移）。去重谓词＝同 sid 同 prompt_id（同发身份；ts ≤120s 近邻仅 prompt_id 缺失时 fallback，窗不放宽——放宽会在快连对上漏计）；弹窗链整条拆除（compact-gate-decision.py 删除＋hooks.json AskUserQuestion 条目删除，Q3 即拆；R2 裁「留」随需求方体验反馈翻转，记档 annex 2026-11 卷）。夹具 test_compact_gate.py 改写 36 检查＋test_compact_report.py 8 检查；断言 77→78＋hooks 计数闸口径扩 `_` 前缀排除；help.md/README 概念行/orchestration.md（Q9 三件套：span 摄入/窗口是缓存不是记忆/分解触发）随批。立论＝v1 六缺陷实证（隔夜阻塞 ×2、快照＝幸存摘要的劣化复制品、手动与失控同桶、无人值守无牙、snap_ok 只验新鲜度、事后-only）＋b5ae44d8 建库批实弹；方案＋评审档在档（docs/，探针判读与两轮评审对账全录）。
- 收口构成不变（一页＋bump 双 json＋README 横幅＋tag），版本一致闸看守（一页版本＝双 json＝README 横幅＝最新 tag 或紧后一版，四值全等＋tag 腿）。
- 最近一笔：1.3.8 压缩恢复 v2 批——如上「已落地」；前一笔 1.3.7 no-op 风暴闸批。
