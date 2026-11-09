# crules-flutter CHANGELOG
> 2026-10-23 裁（B 案）：历史段退役（直删，git 可回），本页只记当前版本、当前形态、最近一笔。
> 历史查证走 git tag ＋ docs/ 方案九篇（正本）；长内容归 docs/changelog-annex/；黑话解码见
> [清单-黑话白话对照](docs/清单-黑话白话对照-2026-10-22.md)。
## 1.3.3 · 当前形态（本批更新：2026-11-09）
- 单人自用规则 plugin（不参与团队共享）。守护＝hooks 五件（硬拦/高危弹窗/漂移队列/收尾提醒/遵守度账），强度四档明示（硬拦/弹窗人裁/观测/纪律，README 守护节）；分工＝七 agent；规范＝宪法四行指针＋副本＋checklist＋进阶篇（分层下沉 skill references）；沉淀＝memory 九模板＋/distill 闸。
- 已落地：外源吸收批（saas-suite 1095297 订金复刻批 1 复盘）——坑库 +2 测试卡（testWidgets 裸 Future.delayed 挂死：超时机制经 test_api 0.7.3 源码 Zone.root 真时器＋3.27.4 同栈受控复现双证改写；Text.rich find.text 拼接串须 textContaining(findRichText:)）；红线补「二手转述不作承重依据」（canonical 改源、双宪法重渲）；parity-rewrite 三件（Task「怎么验」时序前置检查、orchestration fan-out 契约·设计 v5 批 2 待实测、长批执行会话与台账）；design-doc 试点/优化类验收机制性指标条；欠账清单挂批 2 回流观察行；term-whitelist +2。随批另收 11-02 双与门坑卡（前笔 b7635c4）。
- 收口构成不变（一页＋bump 双 json＋README 横幅＋tag），版本一致闸看守（一页版本＝最新 tag＝双 json＝README 横幅，五值须全等）。
- 最近一笔：1.3.3 外源吸收批——如上「已落地」；评审批四组六项逐组裁决，组 4+5 二次终裁含两处删减（与红线重叠的回源条、非增量的定向测试条）。
