#!/usr/bin/env bash
# crules-flutter 安装器（fork 自 crules install.sh 思路，批 2c）——模板为「复制后必填」型（含技术栈三选一交互），故只有完整模式（无轻装 @ 导入）
# 用法：bash scripts/install.sh <目标项目根> --app | --plugin [--dry-run] [--force]
# 行为：模板（app|plugin/CLAUDE.md → 目标 CLAUDE.md + 版本戳）+ checklist/进阶 → 项目根 + agents → .claude/agents/ + memory → .claude/memory/
# 护栏：目标已有 CLAUDE.md 且无 crules-flutter 戳 → 中止（老项目人工合并）；有戳 → 重装（默认跳过已存在）
set -uo pipefail
SRC=$(cd "$(dirname "$0")/.." && pwd)
VER=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["version"])' "$SRC/.claude-plugin/plugin.json" 2>/dev/null) || VER="unknown"
STAMP="<!-- crules-flutter: v$VER @ $(date +%Y-%m-%d) -->"
[ $# -ge 1 ] || { echo "用法: bash scripts/install.sh <目标项目根> --app|--plugin [--dry-run] [--force]"; exit 2; }
TARGET=$1; KIND=""; DRYRUN=0; FORCE=0
for a in "$@"; do case "$a" in --app) KIND=app;; --plugin) KIND=plugin;; --dry-run) DRYRUN=1;; --force) FORCE=1;; esac; done
[ "$KIND" = "app" ] || [ "$KIND" = "plugin" ] || { echo "❌ 须指定 --app 或 --plugin"; exit 2; }
[ -d "$TARGET" ] || { echo "❌ 目标目录不存在: $TARGET"; exit 2; }
W=0; S=0
do_write() { local desc=$1 dst=$2 content=${3:-} src=${4:-}
  if [ -e "$dst" ] && [ "$FORCE" != "1" ]; then S=$((S+1)); echo "  SKIP（已存在）  $dst"; return; fi
  if [ "$DRYRUN" = "1" ]; then W=$((W+1)); echo "  DRY  $desc  $dst"; return; fi
  mkdir -p "$(dirname "$dst")"
  if [ -n "$src" ]; then cp -R "$src" "$dst"; else printf '%s\n' "$content" > "$dst"; fi
  W=$((W+1)); echo "  WRITE $desc  $dst"
}
echo "== crules-flutter 安装报告（kind=$KIND ver=v$VER$( [ "$DRYRUN" = "1" ] && echo ' · DRY-RUN' )$( [ "$FORCE" = "1" ] && echo ' · FORCE' )）=="
if [ -f "$TARGET/CLAUDE.md" ]; then
  if ! grep -qE '<!-- crules-flutter: v[0-9]' "$TARGET/CLAUDE.md"; then
    echo "❌ 目标已有 CLAUDE.md（无 crules-flutter 戳）——老项目请人工合并（禁静默覆盖）"; exit 1
  fi
  echo "🟢 检出 crules-flutter 戳——按重装处理（默认跳过已存在，--force 覆盖）"
fi
do_write "CLAUDE.md（$KIND 模板+戳）" "$TARGET/CLAUDE.md" "$(cat "$SRC/$KIND/CLAUDE.md")

$STAMP"
do_write "checklist.md" "$TARGET/checklist.md" "" "$SRC/checklist.md"
for f in "$SRC"/进阶/*.md; do do_write "进阶/$(basename "$f")" "$TARGET/进阶/$(basename "$f")" "" "$f"; done
for f in "$SRC"/agents/*.md; do do_write ".claude/agents/$(basename "$f")" "$TARGET/.claude/agents/$(basename "$f")" "" "$f"; done
for f in "$SRC"/memory/*.md; do do_write ".claude/memory/$(basename "$f")" "$TARGET/.claude/memory/$(basename "$f")" "" "$f"; done
echo "== 汇总：写入/将写 $W，跳过 $S =="
echo "== 下一步 == ① 完成 CLAUDE.md §七【复制后必填】三选一 ② 填 §十二项目附录 ③ flutter-rules skill 随 plugin 自动可用"
exit 0
