#!/usr/bin/env bash
# crules-flutter plugin 发布辅助（fork 自 crules v74-fork-base，批 2c）——把 v31「bump 必 update + cache grep」机械步骤脚本化
# 用法：
#   scripts/release.sh <new-version>        同步双 json 版本号 + verify 三命令（任一失败即退出非零）
#   scripts/release.sh verify-cache <特征串>  在 cache 最大版本目录 grep 特征串（update 后的生效验证）
#   scripts/release.sh draft                CHANGELOG 建议段草稿（自顶部段日期后的 commits，stdout 人工过滤）
# 说明：**bump 最后跑**——cache 是全仓库快照（含 README/docs/scripts），务必全部改动收尾后再
#       release.sh <ver>，中途再改文件则同版本不刷新（v31 W2：update 按版本号刷 cache），须再 bump；
#       plugin update 本脚本不代跑（完整形态实测为 `claude plugin update crules-flutter@crules-flutter-market`，
#       纯名 "crules" 会报 not found）；完整链路 = 全部改动收尾 → release.sh <ver> → plugin update → release.sh verify-cache '<本轮改动特征串>'
# draft 口径（W2③②）：跨年边界——以当前年拼顶部段日期，12-31 跨年跑会空输出（低危已知）；只列 commit subject 供人工编辑——CHANGELOG 记能力不记笔误、零分发文件轮不记
#       （v58/v59 先例），机械初稿不替人做过滤决定
set -euo pipefail
cd "$(dirname "$0")/.."

usage() { sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }
[ $# -ge 1 ] || usage

case "$1" in
  draft)
    # 取 CHANGELOG 顶部最近段日期（## MM-DD · …）之后的 commits，列 subject 供人工编段
    last_date=$(grep -m1 -oE '^## [0-9]{2}-[0-9]{2}' docs/CHANGELOG.md | grep -oE '[0-9]{2}-[0-9]{2}')
    echo "# CHANGELOG 建议段草稿（人工过滤：记能力不记笔误；零分发文件轮不记——v58/v59 先例）"
    echo "# 基准：顶部段日期 $last_date 之后的 commits（今日：$(date +%m-%d)）"
    git log --since="$(date +%Y)-$last_date 00:00:00" --pretty=format:'- %s（%h）'
    echo ""
    ;;
  verify-cache)
    [ $# -ge 2 ] || usage
    feat="$2"
    cache_root="$HOME/.claude/plugins/cache/crules-flutter-market/crules-flutter"
    [ -d "$cache_root" ] || { echo "❌ cache 不存在: $cache_root"; exit 1; }
    latest=$(ls -v "$cache_root" | tail -1)
    if grep -rl --include='*.md' --include='*.py' --include='*.json' --include='*.sh' --include='*.yml' -F "$feat" "$cache_root/$latest" 2>/dev/null | head -3 | grep -q .; then
      echo "✅ cache $latest 含特征串（新版本已生效）"
    else
      echo "❌ cache $latest 不含特征串——update 未生效或特征选错"; exit 1
    fi
    ;;
  *)
    ver="$1"
    echo "$ver" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$' || { echo "版本号格式: X.Y.Z"; exit 1; }
    python3 - "$ver" <<'PY'
import json, sys
ver = sys.argv[1]
for path, set_ver in (
    (".claude-plugin/plugin.json", lambda d: d.__setitem__("version", ver)),
    (".claude-plugin/marketplace.json", lambda d: d["plugins"][0].__setitem__("version", ver)),
):
    d = json.load(open(path, encoding="utf-8"))
    set_ver(d)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"已同步 {path} -> {ver}")
PY
    echo "== verify 三命令 =="
    echo "== （fork 无 check-consistency，跳过——deny-list fixture 与编译即验证）"
    python3 hooks/test_deny_list.py
    python3 -m py_compile hooks/deny-list.py hooks/test_deny_list.py hooks/pending-updates.py
    echo "== 下一步（手工）== claude plugin update crules-flutter@crules-flutter-market && scripts/release.sh verify-cache '<本轮改动特征串>'"
    ;;
esac
