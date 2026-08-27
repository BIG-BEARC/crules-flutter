#!/usr/bin/env bash
# crules-flutter 安装器（fork 自 crules install.sh 思路）——模板为「复制后必填」型（含技术栈三选一交互），故只有完整模式（无轻装 @ 导入）
# 用法：bash scripts/install.sh <目标项目根> --app | --plugin [--dry-run] [--force]
# 行为：模板（app|plugin/CLAUDE.md → 目标 CLAUDE.md + 版本戳）+ checklist/进阶/analysis_options → 项目根 + memory → .claude/memory/
#       agents 不复制——plugin 自动挂载 7 角色（plugin-only）
# 三态写入（v0.2.2，外审 N2/N3/N5）：
#   不存在           → WRITE 写入
#   已存在 + 默认    → SKIP（不动）
#   已存在 + --force → UPDATE-NEW 写 .new 伴生（人/AI 对照合并后替换——升级不打爆已填内容）
#   memory/ 例外     → 永不覆盖（含 --force）——落地后即项目制度资产（business-rules/INVARIANTS 按 MAINTENANCE 进 git），模板只在缺失时落
# analysis_options 智能落位（N3）：已存在且为 flutter create 脚手架特征（≤6 行、仅 flutter_lints include、无自定义规则）→ 升级替换；
#   已存在且有自定义 → 落 .crules-flutter.yaml 伴生，报告提示人工合并
# 护栏：目标已有 CLAUDE.md 且无 crules-flutter 戳 → 中止（老项目人工合并）；有戳 → 按 --force 语义升级
set -uo pipefail
SRC=$(cd "$(dirname "$0")/.." && pwd)
VER=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["version"])' "$SRC/.claude-plugin/plugin.json" 2>/dev/null) || VER="unknown"
STAMP="<!-- crules-flutter: v$VER @ $(date +%Y-%m-%d) -->"
[ $# -ge 1 ] || { echo "用法: bash scripts/install.sh <目标项目根> --app|--plugin [--dry-run] [--force]"; exit 2; }
TARGET=$1; KIND=""; DRYRUN=0; FORCE=0
for a in "$@"; do case "$a" in --app) KIND=app;; --plugin) KIND=plugin;; --dry-run) DRYRUN=1;; --force) FORCE=1;; esac; done
[ "$KIND" = "app" ] || [ "$KIND" = "plugin" ] || { echo "❌ 须指定 --app 或 --plugin"; exit 2; }
[ -d "$TARGET" ] || { echo "❌ 目标目录不存在: $TARGET"; exit 2; }
W=0; S=0; N=0

do_write() { # $1=描述 $2=目标 $3=内容(空则源复制 $4) [$5=never_force]
  local desc=$1 dst=$2 content=${3:-} src=${4:-} never=${5:-}
  if [ "$never" = "never" ] && [ -e "$dst" ]; then S=$((S+1)); echo "  KEEP（制度资产，永不覆盖）  $dst"; return; fi
  if [ -e "$dst" ] && [ "$FORCE" != "1" ]; then S=$((S+1)); echo "  SKIP（已存在）  $dst"; return; fi
  if [ "$DRYRUN" = "1" ]; then W=$((W+1)); echo "  DRY  $desc  $dst"; return; fi
  mkdir -p "$(dirname "$dst")"
  local out="$dst"
  if [ -e "$dst" ] && [ "$FORCE" = "1" ]; then out="$dst.new"; fi
  if [ -n "$src" ]; then cp -R "$src" "$out"; else printf '%s\n' "$content" > "$out"; fi
  if [ "$out" = "$dst.new" ]; then N=$((N+1)); echo "  UPDATE-NEW（对照合并后替换）  $out"
  else W=$((W+1)); echo "  WRITE $desc  $dst"; fi
}

echo "== crules-flutter 安装报告（kind=$KIND ver=v$VER$( [ "$DRYRUN" = "1" ] && echo ' · DRY-RUN' )$( [ "$FORCE" = "1" ] && echo ' · FORCE(安全升级：.new 伴生)' )）=="
if [ -f "$TARGET/CLAUDE.md" ]; then
  if ! grep -qE '<!-- crules-flutter: v[0-9]' "$TARGET/CLAUDE.md"; then
    echo "❌ 目标已有 CLAUDE.md（无 crules-flutter 戳）——老项目请人工合并（禁静默覆盖）"; exit 1
  fi
  echo "🟢 检出 crules-flutter 戳——按重装/升级处理（默认跳过已存在；--force 出 .new 伴生；memory 永不覆盖）"
fi
do_write "CLAUDE.md（$KIND 模板+戳）" "$TARGET/CLAUDE.md" "$(cat "$SRC/$KIND/CLAUDE.md")

$STAMP"
do_write "checklist.md" "$TARGET/checklist.md" "" "$SRC/checklist.md"

# analysis_options 智能落位（N3）
AO="$TARGET/analysis_options.yaml"
if [ -f "$AO" ]; then
  # 剥注释/空行后签名判定（F1：真机 flutter create 是 28 行注释版，行数判定是死代码）——
  # 剩余非空行 ⊆ {flutter_lints include, linter:, rules:} 即脚手架默认（无自定义规则）
  stripped=$(grep -vE '^[[:space:]]*#|^[[:space:]]*$' "$AO")   # [[:space:]]：BSD grep 不认 \s（v59 探针同款坑）
  if printf '%s\n' "$stripped" | grep -qvE '^[[:space:]]*(include: package:flutter_lints/flutter.yaml|linter:|rules:)?[[:space:]]*$'; then
    if [ "$DRYRUN" != "1" ]; then cp "$SRC/analysis_options.yaml" "$TARGET/analysis_options.crules-flutter.yaml"; fi
    echo "  SIDE-CAR（项目已有自定义 lint，基线落伴生文件，请人工合并）  $TARGET/analysis_options.crules-flutter.yaml"
  else
    # 脚手架默认（无决策价值）→ 升级替换为基线，原文件留 .scaffold-bak
    if [ "$DRYRUN" != "1" ]; then cp "$AO" "$AO.scaffold-bak"; cp "$SRC/analysis_options.yaml" "$AO"; fi
    echo "  UPGRADE（脚手架默认 → lint 基线，原文件留 .scaffold-bak）  $AO"
  fi
else
  do_write "analysis_options.yaml（lint 基线）" "$AO" "" "$SRC/analysis_options.yaml"
fi

for f in "$SRC"/进阶/*.md; do do_write "进阶/$(basename "$f")" "$TARGET/进阶/$(basename "$f")" "" "$f"; done
for f in "$SRC"/memory/*.md; do do_write ".claude/memory/$(basename "$f")" "$TARGET/.claude/memory/$(basename "$f")" "" "$f" "never"; done
echo "== 汇总：写入 $W，跳过/保留 $S，.new 待合并 $N =="
echo "== 下一步 == ① 完成 CLAUDE.md §七【复制后必填】三选一 ② 填 §十二附录 ③ 有 .new 文件时对照合并后替换 ④ flutter-rules skill 与 7 agents 已随 plugin 就位"
exit 0
