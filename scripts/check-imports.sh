#!/usr/bin/env bash
# crules-flutter 安装痕迹巡检（fork 简化版：无轻装 @ 导入，只查版本戳 vs 源版本）
set -uo pipefail
SRC=$(cd "$(dirname "$0")/.." && pwd)
[ $# -ge 1 ] || { echo "用法: bash scripts/check-imports.sh <消费项目根>"; exit 2; }
TARGET=$1; CM="$TARGET/CLAUDE.md"
[ -f "$CM" ] || { echo "❌ 未找到 $CM"; exit 2; }
# 1.0.34：SRC_VER 读不到原兜「?」→ 落 🟢「未检出戳」假绿（失败被伪装成状态）。改 grep 直读 + 读不到
#   即停（与 install.sh 同 idiom，版本号纯 ASCII 码页无关）；版本差改三态报方向——原只说「差」不分
#   升降，源更旧时也建议「重跑 install.sh」等于劝人降级
SRC_VER=$(grep -m1 -oE '"version":[[:space:]]*"[0-9]+\.[0-9]+\.[0-9]+"' "$SRC/.claude-plugin/plugin.json" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
[ -n "$SRC_VER" ] || { echo "❌ 读不到源版本（$SRC/.claude-plugin/plugin.json）——中止"; exit 1; }
STAMP=$(grep -oE '<!-- crules-flutter: v[0-9]+\.[0-9]+\.[0-9]+' "$CM" | head -1 | sed 's/.*v//')
if [ -n "$STAMP" ]; then
  if [ "$STAMP" = "$SRC_VER" ]; then echo "✅ 版本戳 v$STAMP 与源一致"
  elif [ "$(printf '%s\n%s\n' "$STAMP" "$SRC_VER" | sort -V | head -1)" = "$SRC_VER" ]; then
    echo "🟡 源更旧：项目装自 v${STAMP}，源现为 v${SRC_VER}——降级须 install.sh --allow-downgrade 显式放行，勿直接重装"
  else
    echo "🟡 可升级：项目装自 v${STAMP}，源现为 v${SRC_VER}——重跑 install.sh 或人工合并，聚焦两版本间变更"
  fi
else echo "🟢 未检出 crules-flutter 戳（早期安装或非本包装载）"
fi

# memory 模板演进提示（v0.4.0）——只报告「源侧新增文件」+「源仓 git 两版本间模板 diff」，
# 不做目标全量比对（项目自定义内容会全成噪音）；KEEP 语义下机制演进靠人合并
if [ -d "$TARGET/.claude/memory" ]; then
  for f in "$SRC"/memory/*.md; do b=$(basename "$f")
    [ -f "$TARGET/.claude/memory/$b" ] || echo "🟡 memory 新模板未落位：${b}（KEEP 语义不自动补——人工对照源模板合并）"
  done
  if [ -n "$STAMP" ] && [ "$STAMP" != "$SRC_VER" ]; then
    # 两个静默分支显式报告（1.0.2 评审 N2/F7）：此前 SRC 非 git 仓与无 tag 均被静默吞掉——
    # 0.5.0+ 消费者的 memory 演进比对从未生效
    if ! git -C "$SRC" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      echo "🟡 SRC 非 git 仓（plugin cache 形态）——memory 模板演进比对需克隆路径：git clone 本仓 → git fetch --tags → 重跑本脚本"
    elif ! git -C "$SRC" rev-parse -q --verify "refs/tags/v$STAMP" >/dev/null; then
      echo "🟡 源仓无 tag v${STAMP}（1.0.2 前发版未打 tag，历史不回补）——memory 模板演进比对不可用，改按 CHANGELOG v${STAMP}→v${SRC_VER} 段人工对照"
    else
      git -C "$SRC" diff --name-only "v$STAMP" HEAD -- memory/ 2>/dev/null | while read -r m; do
        echo "🟡 memory 模板演进（v${STAMP}→v${SRC_VER}）：${m}——人工对照合并"
      done
    fi
  fi
fi
exit 0
