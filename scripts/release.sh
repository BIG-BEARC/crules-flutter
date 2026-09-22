#!/usr/bin/env bash
# crules-flutter plugin 发布辅助（fork 自 crules v74-fork-base，批 2c）——把 v31「bump 必 update + cache grep」机械步骤脚本化
# 用法：
#   scripts/release.sh <new-version>        同步双 json 版本号 + 双 json 读回断言 + 全套 test-self（任一失败即退出非零）
#   scripts/release.sh verify-cache <特征串>  在 cache 最大版本目录 grep 特征串（update 后的生效验证）
#   scripts/release.sh draft                CHANGELOG 建议段草稿（自顶部段日期后的 commits，stdout 人工过滤）
#   scripts/release.sh tag <ver>            校验 HEAD 双 json 版本一致 + 工作树干净 + 全套 test-self 后打 tag 并推 origin（幂等；防 tag 指向 bump 前旧树 / bump 后偷改树）
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
    # 1.0.21 Windows 实机 P0-A 同族：sys.stdin 缺显式编码 → 按宿主码页解 git show 的 UTF-8 输出，
    #   plugin.json 含中文 description → cp950 下 UnicodeDecodeError → 2>/dev/null 吞掉 → 「读 HEAD
    #   plugin.json 失败」把 tag 卡死在第一步。改走 buffer + 显式 UTF-8。
    head_ver=$(git show HEAD:.claude-plugin/plugin.json 2>/dev/null | python3 -c 'import json,sys;print(json.loads(sys.stdin.buffer.read().decode("utf-8"))["version"])' 2>/dev/null) || { echo "❌ 读 HEAD plugin.json 失败（非 git 仓 / 无提交？）"; exit 1; }
    [ "${ver}" = "${head_ver}" ] || { echo "❌ HEAD 提交内 plugin.json 为 v${head_ver} ≠ v${ver}——先 commit 含 bump 的改动再打 tag（防 tag 指向旧树；注意读的是提交内版本，工作区未提交的 bump 不算）"; exit 1; }
    # 1.0.34：tag 是消费者实际拿到的工件（check-imports 演进比对靠 tag）——打 tag 前两道硬闸：
    #   工作树干净（堵 bump 后偷改：bump 步的 test-self 验的是当时工作树，bump→commit→tag 之间仍可改文件）
    #   + 全套 test-self（堵改坏树出库）。执法点必须在 tag，不在 bump。
    git diff --quiet && git diff --cached --quiet || { echo "❌ 工作树不干净——tag 须打在已提交树上（先 commit 或 stash）"; exit 1; }
    bash scripts/test-self.sh
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
    # 版本序用 sort -V（1.0.10 发布后追加：BSD ls -v 非 GNU 版本序——字典序 1.0.9 > 1.0.10，
    # tail -1 取到旧版目录，verify 验旧不验新且特征串撞旧内容可假绿；v59 BSD grep 坑同款环境假设，
    # 与 commands/init.md 源定位同 idiom 对齐）
    latest=$(ls "$cache_root" | sort -V | tail -1)
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
sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # 1.0.21 Windows P0-A：宿主码页非 UTF-8 时 stdout 按该码页编码（实测 cp936 下本段输出为 cp936 字节、非 UTF-8）——终端同码页时显示正常，但任何 UTF-8 消费者（CI 日志 / Git Bash / 管道）读到乱码；且若消息含该码页**编不出**的字（如 cp950/Big5 遇简体「块」）则 print 抛 UnicodeEncodeError，因落在每轮写盘之后故双 json 停在半完成态。钉死 UTF-8 使输出与宿主码页解耦
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
    echo "== verify：双 json 读回断言 + 全套 test-self =="
    # 1.0.34：写后必读回（原只写不验，一次手工改动 marketplace.json 即静默漂移、无人拦）
    for f in .claude-plugin/plugin.json .claude-plugin/marketplace.json; do
      got=$(grep -m1 -oE '"version":[[:space:]]*"[0-9]+\.[0-9]+\.[0-9]+"' "$f" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
      [ "${got:-x}" = "$ver" ] || { echo "❌ $f 读回为 v${got:-无} ≠ v${ver}"; exit 1; }
    done
    # 1.0.34：删手工验证清单（原 py_compile 枚举 3/7 漂移实锤）——发版路径与 CI 跑同一个 test-self：
    # 三 fixture 子进程实跑 6 个 py + 生成闸实跑 render-blocks，7 个 py 全被真实执行，强于 py_compile 枚举
    bash scripts/test-self.sh
    echo "== 下一步（手工）== claude plugin update crules-flutter@crules-flutter-market && scripts/release.sh verify-cache '<本轮改动特征串>'"
    ;;
esac
