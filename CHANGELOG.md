# crules-flutter CHANGELOG
> 2026-10-23 裁（B 案）：历史段退役（直删，git 可回），本页只记当前版本、当前形态、最近一笔。
> 历史查证走 git tag ＋ docs/ 方案篇（正本）；长内容归 docs/changelog-annex/；黑话解码见
> [清单-黑话白话对照](docs/清单-黑话白话对照-2026-10-22.md)。
## 1.3.9 · 当前形态（本批更新：2026-11-14）
- 单人自用规则 plugin（不参与团队共享）。守护＝hooks 八件（硬拦/高危弹窗/漂移队列/收尾提醒/遵守度账/压缩恢复 v2 注入件＋PreCompact 观测件/no-op 风暴闸），强度四档明示（硬拦/弹窗人裁/观测/纪律，README 守护节）；分工＝七 agent；规范＝宪法四行指针＋副本＋checklist＋进阶篇（分层下沉 skill references）；沉淀＝memory 九模板＋/distill 闸；完整性＝引用完整性闸（scripts/check-references.py：md 死链＋入口悬空双断面，全分发面缺省，收口必跑、test-self 红绿双向看守）。
- 已落地（1.3.9 derive 净化修正批）：hooks/_compact_core.py derive_transcript 净化规则修正——transcript 目录推导由「只换斜线」改「全非字母数字转横线」（Claude Code 实际行为，生产磁盘双证 super_printer→super-printer、.git/modules→--git-modules-）；根含 `_`/`.` 的工程 L2 推导不再必 miss，startup 断点回读（derive-only 路）同修。夹具 test_compact_gate.py 新增 san() 按真实净化规则造伪家居（原夹具与实现共用同错规则＝共谋假绿形态）＋underscore/dot 根用例，检查 36→37（红 4 级联→修→绿）。生产实弹判读两工程记档：super_printer 夜跑 5.5h（去重零双记、runaway 单发即止、注入 7/8 送达 L1 真路径）＋saas-cashier 双代（v1 弹窗 ×14 峰值 3 弹/1.7h＋mute ×3 补 R2 判据 3 缺证面；v2 handoff 首实弹 ×4、L2 生产命中）；四发现（microcompact 定性/弃开 resume 吞注入/plugin 缓存瞬断/净化规则）录方案 §6.1 末，发现 2/3 落 §5 已知边界、annex 2026-11 卷 11-13 条。
- 已落地（1.3.9 分工卫生微批）：字体归属 A′ 切分（google_fonts/打包策略单源 layout.md「字体策略」，theming.md 只持令牌并回指——「references 命中文件数=1」断言看守）；Agent编排「调度三条」节补 fan-out 契约指针（两条内联＋orchestration 单源，专用断言钉行）；判据单源化——scripts/closing-audit.py 退役删档（批1 探针使命由生产 hook 承接，compliance-audit :9/:54 两处声明同步改）；上手教程加「文案基线 v1.3.9」戳＋minor 差 ≤1 tripwire 断言；外设四件锚口径行统一同款（iot-devices 核验戳独立成行）＋对拍断言；test-self +4 至 82、头注释明文测试落位惯例（fixture 随宿主目录）。方案＋Gate（Q1=C 退役／Q2=A′／Q3=仅指针／Q4=tripwire）＋隔离评审（3 阻塞 5 建议全吸收）见 docs/方案-分工卫生微批-2026-11-14.md。
- 收口构成不变（一页＋bump 双 json＋README 横幅＋tag），版本一致闸看守（一页版本＝双 json＝README 横幅＝最新 tag 或紧后一版，四值全等＋tag 腿）。
- 最近一笔：1.3.9 分工卫生微批——如上第二条「已落地」；前一笔 1.3.9 derive 净化修正批。
