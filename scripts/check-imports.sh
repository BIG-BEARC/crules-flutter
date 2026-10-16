#!/usr/bin/env bash
# crules-flutter 安装痕迹巡检——戳读链 1.1.5 起：`.claude/CLAUDE.md` 指针戳（丁-Copy）优先 → 根 CLAUDE.md（丁-tracked 存量）回退
set -uo pipefail
SRC=$(cd "$(dirname "$0")/.." && pwd)
[ $# -ge 1 ] || { echo "用法: bash scripts/check-imports.sh <消费项目根>"; exit 2; }
TARGET=$1
# 1.0.34：SRC_VER 读不到原兜「?」→ 落 🟢「未检出戳」假绿（失败被伪装成状态）。改 grep 直读 + 读不到
#   即停（版本号纯 ASCII 码页无关）；版本差三态报方向——源更旧时劝人刷等于劝人降级，故旧向只报不动
SRC_VER=$(grep -m1 -oE '"version":[[:space:]]*"[0-9]+\.[0-9]+\.[0-9]+"' "$SRC/.claude-plugin/plugin.json" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
[ -n "$SRC_VER" ] || { echo "❌ 读不到源版本（$SRC/.claude-plugin/plugin.json）——中止"; exit 1; }
# 1.1.5：戳读链迁移（同 hooks/_common.py constitution_stamp——指针优先，根回退存量平滑）
STAMP=""; STAMP_FORM=""
for cm in "$TARGET/.claude/CLAUDE.md" "$TARGET/CLAUDE.md"; do
  [ -f "$cm" ] || continue
  STAMP=$(grep -oE '<!-- crules-flutter: v[0-9]+\.[0-9]+\.[0-9]+' "$cm" | head -1 | sed 's/.*v//')
  if [ -n "$STAMP" ]; then
    case "$cm" in
      */.claude/CLAUDE.md) STAMP_FORM="指针（丁-Copy）" ;;
      *) STAMP_FORM="根 CLAUDE.md（丁-tracked 存量——迁移=阶段 4 授权批）" ;;
    esac
    break
  fi
done
if [ -n "$STAMP" ]; then
  if [ "$STAMP" = "$SRC_VER" ]; then echo "✅ 版本戳 v$STAMP 与源一致（${STAMP_FORM}）"
  elif [ "$(printf '%s\n%s\n' "$STAMP" "$SRC_VER" | sort -V | head -1)" = "$SRC_VER" ]; then
    echo "🟡 源更旧：项目 ${STAMP_FORM} v${STAMP}，源现为 v${SRC_VER}——勿刷（plugin update 回滚态由需求方裁）"
  else
    echo "🟡 可升级：项目 ${STAMP_FORM} v${STAMP}，源现为 v${SRC_VER}——跑 /crules-flutter:init 刷指针与副本，聚焦两版本间变更"
  fi
else echo "🟢 未检出 crules-flutter 戳（早期安装或非本包装载——新装走 /crules-flutter:init）"
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
