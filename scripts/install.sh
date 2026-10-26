#!/usr/bin/env bash
# crules-flutter 安装器——分发职责已退役（1.1.5，方案 v4.0 Q6/C5/C6：载体裁丁-Copy、去分发化）
# 退役面：根 CLAUDE.md / checklist.md / 进阶/ / analysis_options.yaml 的分发与三向合并、
#   --upgrade / --yes / --allow-downgrade / --new-only、.gitignore 幂等落位（机器件与分发面
#   随分发职责一并消失——受控文件零接触 R0，权威源=插件 cache）
# 正门（丁-Copy）：/crules-flutter:init——`.claude/CLAUDE.md` 四行指针 + `.claude/crules/constitution.md`
#   副本 + memory 9 种子（缺则补、永不覆盖）；升级=重跑 init 刷指针与副本；巡检=scripts/check-imports.sh
# 本文件仅存迁移辅助位：阶段 4/5 一次性授权批（丁-tracked 存量原子切，设计待 Q5——未建前一律拒绝）
# 史：1.0.x 全量分发+三向合并机器 → 1.1.3 分发面默认不进 git → 1.1.5 分发退役（丁-Copy 裁；方案稿 2026-10-26 删档，git 史可查）
set -uo pipefail
echo "❌ install.sh 分发职责已退役（1.1.5）——工程接入 / 升级 / 模板刷新一律走 /crules-flutter:init（丁-Copy 指针形态，受控文件零接触）"
echo "   巡检：bash scripts/check-imports.sh <项目根>（cache 内跑，查版本差与 memory 模板演进）"
echo "   存量丁-tracked 工程迁移 = 阶段 4 一次性授权批（方案档 §7，待裁 Q5）"
exit 1
