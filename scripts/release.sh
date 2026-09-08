#!/usr/bin/env bash
# crules-flutter plugin 发布辅助（fork 自 crules v74-fork-base，批 2c）——把 v31「bump 必 update + cache grep」机械步骤脚本化
# 用法：
#   scripts/release.sh <new-version>        同步双 json 版本号 + verify 三命令（任一失败即退出非零）
#   scripts/release.sh verify-cache <特征串>  在 cache 最大版本目录 grep 特征串（update 后的生效验证）
#   scripts/release.sh draft                CHANGELOG 建议段草稿（自顶部段日期后的 commits，stdout 人工过滤）
#   scripts/release.sh tag <ver>            校验 HEAD 双 json 版本一致后打 tag 并推 origin（幂等；防 tag 指向 bump 前旧树）
# 说明：**bump 最后跑**——cache 是全仓库快照（含 README/docs/scripts），务必全部改动收尾后再
#       release.sh <ver>，中途再改文件则同版本不刷新（v31 W2：update 按版本号刷 cache），须再 bump；
#       plugin update 本脚本不代跑（完整形态实测为 `claude plugin update crules-flutter@crules-flutter-market`，
#       纯名 "crules-flutter" 会报 not found）；完整链路 = 全部改动收尾 → release.sh <ver> → **commit →
#       release.sh tag <ver>**（tag 打在含 bump 的提交上并推远端——不推则消费者 clone 侧 fetch 不可见，
#       check-imports 的 memory 演进比对依赖 tag）→ plugin update → release.sh verify-cache '<本轮改动特征串>'
# draft 口径（W2③②）：跨年边界——以当前年拼顶部段日期，12-31 跨年跑会空输出（低危已知）；只列 commit subject 供人工编辑——CHANGELOG 记能力不记笔误、零分发文件轮不记
#       （v58/v59 先例），机械初稿不替人做过滤决定
set -euo pipefail
cd "$(dirname "$0")/.."

usage() { sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }
[ $# -ge 1 ] || usage

case "$1" in
  draft)
    # fork 版：CHANGELOG 在仓库根、段头为版本式（## X.Y.Z · …）——按「顶部版本号对应的发版 commit」取边界
    top_ver=$(grep -m1 -oE '^## [0-9]+\.[0-9]+\.[0-9]+' CHANGELOG.md | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
    echo "# CHANGELOG 建议段草稿（人工过滤：记能力不记笔误）"
    echo "# 基准：顶部版本 v$top_ver 发版 commit 之后的未记 commits"
    anchor=$(git log --oneline --grep="$top_ver" -1 --format=%H || true)
    if [ -n "$anchor" ]; then
      git log "${anchor}..HEAD" --pretty=format:'- %s（%h）' | grep -v "^$" || echo "-（无未记 commits）"
    else
      echo "# ⚠️ 未找到含 $top_ver 的发版 commit，列最近 10 条供人工筛："
      git log -10 --pretty=format:'- %s（%h）'
    fi
    echo ""
    ;;
  tag)
    # 1.0.2（评审 N2/F7）：tag 打在含 bump 的提交上 + 推远端——check-imports 的 memory 演进比对依赖 tag；
    # HEAD 双 json 版本校验防「tag 指向 bump 前旧树」（bump 未 commit 时 HEAD json 仍是旧版本号，当场拦）
    [ $# -ge 2 ] || usage
    ver="$2"
    echo "$ver" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$' || { echo "版本号格式: X.Y.Z"; exit 1; }
    head_ver=$(git show HEAD:.claude-plugin/plugin.json 2>/dev/null | python3 -c 'import json,sys;print(json.load(sys.stdin)["version"])' 2>/dev/null) || { echo "❌ 读 HEAD plugin.json 失败（非 git 仓 / 无提交？）"; exit 1; }
    [ "${ver}" = "${head_ver}" ] || { echo "❌ HEAD 提交内 plugin.json 为 v${head_ver} ≠ v${ver}——先 commit 含 bump 的改动再打 tag（防 tag 指向旧树；注意读的是提交内版本，工作区未提交的 bump 不算）"; exit 1; }
    if git rev-parse -q --verify "refs/tags/v${ver}" >/dev/null; then
      echo "🟡 tag v${ver} 已存在，跳过（幂等）"
    else
      git tag "v${ver}" || { echo "❌ tag 创建失败"; exit 1; }
      git push origin "v${ver}" || { echo "❌ tag v${ver} 已建但推送失败——手动 git push origin v${ver}（不推则消费者 clone 不可见）"; exit 1; }
      echo "✅ tag v${ver} 已创建并推送（消费者侧 git fetch --tags 后 check-imports 演进比对可用）"
    fi
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
