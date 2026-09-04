#!/usr/bin/env bash
# crules-flutter 安装痕迹巡检（fork 简化版：无轻装 @ 导入，只查版本戳 vs 源版本）
set -uo pipefail
SRC=$(cd "$(dirname "$0")/.." && pwd)
[ $# -ge 1 ] || { echo "用法: bash scripts/check-imports.sh <消费项目根>"; exit 2; }
TARGET=$1; CM="$TARGET/CLAUDE.md"
[ -f "$CM" ] || { echo "❌ 未找到 $CM"; exit 2; }
SRC_VER=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["version"])' "$SRC/.claude-plugin/plugin.json" 2>/dev/null) || SRC_VER="?"
STAMP=$(grep -oE '<!-- crules-flutter: v[0-9]+\.[0-9]+\.[0-9]+' "$CM" | head -1 | sed 's/.*v//')
if [ -n "$STAMP" ] && [ "$SRC_VER" != "?" ]; then
  if [ "$STAMP" = "$SRC_VER" ]; then echo "✅ 版本戳 v$STAMP 与源一致"
  else echo "🟡 版本差：项目装自 v$STAMP，源现为 v$SRC_VER——重跑 install.sh 或人工合并，聚焦两版本间变更"; fi
else echo "🟢 未检出 crules-flutter 戳（早期安装或非本包装载）"
fi

# memory 模板演进提示（v0.4.0）——只报告「源侧新增文件」+「源仓 git 两版本间模板 diff」，
# 不做目标全量比对（项目自定义内容会全成噪音）；KEEP 语义下机制演进靠人合并
if [ -d "$TARGET/.claude/memory" ]; then
  for f in "$SRC"/memory/*.md; do b=$(basename "$f")
    [ -f "$TARGET/.claude/memory/$b" ] || echo "🟡 memory 新模板未落位：$b（KEEP 语义不自动补——人工对照源模板合并）"
  done
  if [ -n "$STAMP" ] && [ "$STAMP" != "$SRC_VER" ] && git -C "$SRC" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git -C "$SRC" diff --name-only "v$STAMP" HEAD -- memory/ 2>/dev/null | while read -r m; do
      echo "🟡 memory 模板演进（v$STAMP→v$SRC_VER）：$m——人工对照合并"
    done
  fi
fi
exit 0
