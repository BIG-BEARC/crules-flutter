#!/usr/bin/env bash
# crules-flutter 安装器（fork 自 crules install.sh 思路）——模板为「复制后必填」型（含技术栈三选一交互），故只有完整模式（无轻装 @ 导入）
# 用法：bash scripts/install.sh <目标项目根> --app | --plugin [--dry-run] [--force] [--upgrade] [--yes] [--allow-downgrade] [--new-only]
#       --upgrade = 升级三步打包：版本差巡检（check-imports.sh）→ 确认 → 自调 --force（三向合并默认开，memory 永不覆盖）
#       --yes = 升级免确认（无人值守正门——EOF/关闭 stdin 下默认保守取消，AI/脚本驱动用此档，1.0.34）
#       --allow-downgrade = 源旧于项目戳时显式放行降级（默认拒，防源错/手误把旧模板铺进新工程，1.0.34）
#       --new-only = 关三向合并退回 .new 全人工伴生（1.0.43 退路正门，方案 v2 D-2）
# 行为：模板（app|plugin/CLAUDE.md → 目标 CLAUDE.md + 版本戳）+ checklist/进阶/analysis_options → 项目根 + memory → .claude/memory/
#       agents 不复制——plugin 自动挂载 7 角色（plugin-only）
# 三态写入（v0.2.2，外审 N2/N3/N5；1.0.43 --force 优先进三向合并）：
#   不存在           → WRITE 写入（同时自存 dst.crules-base 模板快照——下轮合并的 base，方案 v2 D-5）
#   已存在 + 默认    → SKIP（不动）
#   已存在 + --force → MERGE：base（自存快照，退而求 cache 旧版模板）三向合并——对 base 零改动直替 /
#       零冲突自动并（写回+刷 base）/ 尾部撞戳位窄形自动解（仅 CLAUDE.md）/ 有冲突带标记写回+
#       .crules-conflicts 摘要且 base 与戳禁更新（评审 #6 三护栏，.crules-bak 先备份）；
#       无 base 可比 / --new-only / 无 git → UPDATE-NEW .new 伴生人工（旧语义保留）
#   memory/ 例外     → 永不覆盖（含 --force）——落地后即项目制度资产（business-rules/INVARIANTS 按 MAINTENANCE 进 git），模板只在缺失时落
# analysis_options 智能落位（N3）：已存在且为 flutter create 脚手架特征（≤6 行、仅 flutter_lints include、无自定义规则）→ 升级替换；
#   已存在且有自定义 → 落 .crules-flutter.yaml 伴生，报告提示人工合并
# 护栏：目标已有 CLAUDE.md 且无 crules-flutter 戳 → 中止（老项目人工合并）；有戳 → 按 --force 语义升级
set -uo pipefail
SRC=$(cd "$(dirname "$0")/.." && pwd)
# 1.0.34：取版本去 python 化 + 读不到即停。原 python3 单行在「无 python / 码页异常（1.0.21 P0-A 族，
#   显式 UTF-8 只堵了码页一条）/ 进程首启失败（2026-09-22 本机注入型管控偶发再证实状）」三态下都落
#   || VER="unknown" 兜底 → 照写 vunknown 戳 + 空模板半落盘 → 戳守卫（v[0-9]）认不出 → 此后升级
#   全被拦成「老项目无戳」。版本号纯 ASCII、码页无关，grep 直读（test-self 语义闸同 idiom）；
#   坏值不流进后续决策——读不到就停。
VER=$(grep -m1 -oE '"version":[[:space:]]*"[0-9]+\.[0-9]+\.[0-9]+"' "$SRC/.claude-plugin/plugin.json" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
[ -n "$VER" ] || { echo "❌ 读不到版本（$SRC/.claude-plugin/plugin.json）——中止，不写无版本戳"; exit 1; }
STAMP="<!-- crules-flutter: v$VER @ $(date +%Y-%m-%d) -->"
[ $# -ge 1 ] || { echo "用法: bash scripts/install.sh <目标项目根> --app|--plugin [--dry-run] [--force] [--upgrade] [--yes] [--allow-downgrade]"; exit 2; }
TARGET=$1; KIND=""; DRYRUN=0; FORCE=0; UPGRADE=0; YES=0; ALLOW_DOWN=0; NEWONLY=0
# 1.0.34：未知参数即红（原 for-case 缺默认分支，--forc 手误=静默普通安装）；循环跳过 $1（目标路径非开关）
for a in "${@:2}"; do case "$a" in
  --app) KIND=app;; --plugin) KIND=plugin;; --dry-run) DRYRUN=1;; --force) FORCE=1;;
  --upgrade) UPGRADE=1;; --yes) YES=1;; --allow-downgrade) ALLOW_DOWN=1;; --new-only) NEWONLY=1;;
  *) echo "❌ 未知参数: $a（用法见脚本头注）"; exit 2;; esac; done
[ "$KIND" = "app" ] || [ "$KIND" = "plugin" ] || { echo "❌ 须指定 --app 或 --plugin"; exit 2; }
[ -d "$TARGET" ] || { echo "❌ 目标目录不存在: $TARGET"; exit 2; }

# 降级守卫（1.0.34）：戳带版本且源更旧 → 默认拒，--allow-downgrade 显式放行。防源错/手误把旧模板
#   铺进新工程——.new 伴生只护「已存在文件」，AO 伴生/gitignore 仍直接写盘，方向须在入口拦。
#   sort -V 与 release.sh verify-cache 同 idiom（BSD/GNU 均认，仓库已验证先例）
guard_downgrade() { # $1=项目戳版本（空则过）
  [ -n "$1" ] || return 0
  [ "$VER" != "$1" ] || return 0
  [ "$(printf '%s\n%s\n' "$1" "$VER" | sort -V | head -1)" = "$VER" ] || return 0
  if [ "$ALLOW_DOWN" != "1" ]; then echo "❌ 源 v$VER 旧于项目 v$1——降级须 --allow-downgrade 显式放行"; exit 1; fi
  echo "🟡 显式降级放行（--allow-downgrade）：项目 v$1 → 源 v$VER"
}

# --upgrade 模式（1.0.6，D3）：巡检 → 确认 → 自调 --force；.new 合并仍人工（有意边界：合并判断不自动化）
if [ "$UPGRADE" = "1" ]; then
  [ -f "$TARGET/CLAUDE.md" ] && grep -qE '<!-- crules-flutter: v[0-9]' "$TARGET/CLAUDE.md" \
    || { echo "❌ 目标无 crules-flutter 戳——非本包装载工程，升级中止（老项目走人工合并）"; exit 1; }
  guard_downgrade "$(grep -oE '<!-- crules-flutter: v[0-9]+\.[0-9]+\.[0-9]+' "$TARGET/CLAUDE.md" | head -1 | sed 's/.*v//')"
  echo "== 升级巡检（源 v$VER → $TARGET）=="
  bash "$SRC/scripts/check-imports.sh" "$TARGET" || true
  if [ "$YES" = "1" ]; then REPLY=y
  else
    printf '应用升级？（三向合并默认开：零改动直替/自动并/冲突带标记呈人；--new-only 退回 .new 全人工；memory/ 永不覆盖）[y/N] '
    REPLY=; read -r REPLY || true   # 1.0.34：预置空串+吞 rc——EOF 与关闭 stdin 均落取消分支（无人值守默认保守取消，正门是 --yes）
  fi
  case "$REPLY" in
    y|Y|yes) if [ "$ALLOW_DOWN" = "1" ]; then exec bash "$0" "$TARGET" "--$KIND" --force --allow-downgrade
             else exec bash "$0" "$TARGET" "--$KIND" --force; fi ;;
    *) echo "已取消——未做任何改动"; exit 0 ;; esac
fi
W=0; S=0; N=0; E=0; MG=0; CF=0

# ── 三向合并（1.0.43 · 方案 v2 甲；裁决 D-1/D-2/D-5，护栏=评审 #6 三条）────────
# base 来源（D-5）：① dst.crules-base 自存快照（上轮安装/合并成功落笔，恒可得）
#   ② 退 cache 旧版模板（按项目戳找宿主 cache——历史工程首轮过渡，宿主保留策略不可控）
#   ③ 皆无 / 无 git / --new-only → 调用侧退 .new（评审 #7：merge-file 只依赖 git 二进制，不要求目标/cache 是 git 仓）
# 窄形自动解（边界③）仅认「尾部内容撞戳位/gen 块」：ours 段去空行后仅剩旧戳行；base 段须空、
#   theirs 段仅 gen 围栏注释/新 STAMP/空行（2026-09-23 两工程实跑各 1 冲突块皆此形）。解=ours 去旧戳 + theirs 段接入。

base_for() { # $1=dst → echo base 路径或空
  [ -f "$1.crules-base" ] && { echo "$1.crules-base"; return; }
  local pv c
  # 版本优先取自文件自身戳（CLAUDE.md），无戳文件（checklist/进阶）退项目戳——同一安装版本
  pv=$(grep -m1 -oE '<!-- crules-flutter: v[0-9]+\.[0-9]+\.[0-9]+' "$1" 2>/dev/null | head -1 | sed 's/.*v//')
  [ -n "$pv" ] || pv=$(grep -m1 -oE '<!-- crules-flutter: v[0-9]+\.[0-9]+\.[0-9]+' "$TARGET/CLAUDE.md" 2>/dev/null | head -1 | sed 's/.*v//')
  [ -n "$pv" ] || return 0
  c="$HOME/.claude/plugins/cache/crules-flutter-market/crules-flutter/$pv/$MERGE_REL"
  [ -f "$c" ] && echo "$c"
}

merge_step() { # $1=dst $2=theirs临时文件 $3=src快照 $4=窄形(空|tail) → rc 0=并入成功 1=退.new（无base/merge出错） 3=冲突带标记写回呈人
  local dst=$1 theirs=$2 snap=$3 tail=$4 base
  base=$(base_for "$dst")
  [ -n "$base" ] || return 1
  local work rc
  work=$(mktemp "${TMPDIR:-/tmp}/cf-merge.XXXXXX")
  cp "$dst" "$work"
  git merge-file "$work" "$base" "$theirs"; rc=$?   # rc=冲突块数（1..127），≥128 或负=错误
  if [ "$rc" -eq 0 ]; then                             # 自动并
    cp "$work" "$dst"; rm -f "$work"; cp "$snap" "$dst.crules-base"; return 0
  fi
  [ "$rc" -ge 128 ] && { rm -f "$work"; return 1; }   # merge-file 出错——原件不动，退 .new
  # 尾形判定（窄形自动解仅 CLAUDE.md 适用；两块制：<<<<<<< 段=ours、======= 至 >>>>>>> 段=theirs）：
  #   ours 段须以旧戳行收尾（前可带项目自有尾节，戳后不得再有非空内容）；
  #   theirs 段仅允许 gen 围栏注释/新 STAMP/空行——真决策内容不得落在 theirs
  if [ -n "$tail" ]; then
  local shape
  shape=$(awk -v stamp="$STAMP" '
    /^<{7} /{sect=1; o=""; ob=""; next} /^={7}$/{sect=2; next} /^>{7} /{sect=0; next}
    { line=$0; gsub(/^[ \t]+|[ \t]+$/, "", line)
      if (sect==1) { if (line == "") next
        if (line ~ /^<!-- crules-flutter: v[0-9]/) { ob=ob "\n" line; next }
        if (ob != "") bad=1   # 旧戳行后又出现非空内容 → 非尾形
        o = o "\n" line }
      else if (sect==2) { if (line == "") next
        if (line == stamp) next
        if (line ~ /^<!-- (gen:[a-z-]+|\/gen:[a-z-]+|仓内维护者勿手改)/) next
        bad=1 } }
    END{ print (bad ? "bad" : (o == "" ? "bad" : "ok")) }' "$work")
  if [ "$shape" = "ok" ]; then                         # 窄形解：去 ours 旧戳，theirs 段接入
    local res; res=$(mktemp "${TMPDIR:-/tmp}/cf-res.XXXXXX")
    awk '/^<{7} /{sect=1; next} /^={7}$/{sect=2; next} /^>{7} /{sect=0; next}
         sect==1 && $0 ~ /^<!-- crules-flutter: v[0-9]+\.[0-9]+\.[0-9]+ @ /{next}
         { print }' "$work" > "$res"
    cp "$res" "$dst"; rm -f "$work" "$res"
    grep -qF "$STAMP" "$dst" || printf '\n%s\n' "$STAMP" >> "$dst"   # 补戳防御（theirs 段正常自带新 STAMP）
    cp "$snap" "$dst.crules-base"; return 0
  fi
  fi
  # 真冲突呈人（任何可并文件皆带标记写回，宁冲突勿错并）：护栏①.bak 先备份；带标记写回；
  #   .crules-conflicts 摘要；base 不刷、旧戳随 ours 保留（护栏②）
  cp "$dst" "$dst.crules-bak"
  mv "$work" "$dst"
  awk '/^<{7} /{blk++; print "◆ 冲突块 " blk " " $2; sect=1; next}
       /^={7}$/{sect=2; next} /^>{7} /{sect=0; next}
       { print (sect==1 ? "  ◀ 项目侧 " : "  ▶ 模板侧 ") $0 }' "$dst" > "$dst.crules-conflicts"
  return 3
}

do_write() { # $1=描述 $2=目标 $3=内容(空则源复制 $4) [$5=never_force]
  local desc=$1 dst=$2 content=${3:-} src=${4:-} never=${5:-}
  if [ "$never" = "never" ] && [ -e "$dst" ]; then S=$((S+1)); echo "  KEEP（制度资产，永不覆盖）  $dst"; return; fi
  if [ -e "$dst" ] && [ "$FORCE" != "1" ]; then S=$((S+1)); echo "  SKIP（已存在）  $dst"; return; fi
  if [ "$DRYRUN" = "1" ]; then W=$((W+1)); echo "  DRY  $desc  $dst"; return; fi
  mkdir -p "$(dirname "$dst")"
  # --force + 可合并文件 + 非 --new-only + 有 git → 三向合并优先
  if [ "$FORCE" = "1" ] && [ "$NEWONLY" != "1" ] && [ -e "$dst" ] \
     && command -v git >/dev/null 2>&1 && [ -n "${MERGE_REL:-}" ]; then
    local theirs rc snap
    theirs=$(mktemp "${TMPDIR:-/tmp}/cf-theirs.XXXXXX")
    if [ -n "$content" ]; then printf '%s\n' "$content" > "$theirs"; snap="$theirs"
    else cp "$src" "$theirs"; snap="$src"; fi
    merge_step "$dst" "$theirs" "$snap" "$([ "$dst" = "$TARGET/CLAUDE.md" ] && echo tail)"
    rc=$?
    rm -f "$theirs"
    case $rc in
      0) MG=$((MG+1)); echo "  MERGE $desc  $dst"; return;;
      3) CF=$((CF+1)); echo "  MERGE-CONFLICT（已带标记写回+摘要，戳未动，解后请删 .crules-bak）  $dst.crules-conflicts"; return;;
    esac
    # rc=1 落回原 .new 路径
  fi
  local out="$dst"
  if [ -e "$dst" ] && [ "$FORCE" = "1" ]; then out="$dst.new"; fi
  if [ -n "$src" ]; then
    cp -R "$src" "$out" || { E=$((E+1)); echo "  ERROR（复制失败，不计入写入）  $dst"; return; }
  else
    printf '%s\n' "$content" > "$out" || { E=$((E+1)); echo "  ERROR（写入失败，不计入写入）  $dst"; return; }
  fi
  # 首装自存 base 快照——下轮 --force 合并的 base（D-5；out=$dst 且非 dry-run 蕴含 dst 原不存在）
  if [ "$out" = "$dst" ] && [ -n "${MERGE_REL:-}" ]; then
    if [ -n "$src" ]; then cp "$src" "$dst.crules-base" 2>/dev/null || true
    else printf '%s\n' "$content" > "$dst.crules-base" 2>/dev/null || true; fi
    if ! grep -qF 'crules-base' "$TARGET/.gitignore" 2>/dev/null; then
      [ -f "$TARGET/.gitignore" ] || printf '# crules-flutter：memory 本机生成物（政策与反悔方式见 .claude/memory/MAINTENANCE.md「git 分层」）\n' > "$TARGET/.gitignore"
      printf '*.crules-base\n*.crules-bak\n*.crules-conflicts\n' >> "$TARGET/.gitignore"
      echo "  GITIGNORE（合并伴生物 3 行）  $TARGET/.gitignore"
    fi
  fi
  if [ "$out" = "$dst.new" ]; then N=$((N+1)); echo "  UPDATE-NEW（对照合并后替换）  $out"
  else W=$((W+1)); echo "  WRITE $desc  $dst"; fi
}

echo "== crules-flutter 安装报告（kind=$KIND ver=v$VER$( [ "$DRYRUN" = "1" ] && echo ' · DRY-RUN' )$( [ "$FORCE" = "1" ] && echo ' · FORCE(三向合并)' )）=="
if [ -f "$TARGET/CLAUDE.md" ]; then
  if ! grep -qE '<!-- crules-flutter: v[0-9]' "$TARGET/CLAUDE.md"; then
    echo "❌ 目标已有 CLAUDE.md（无 crules-flutter 戳）——老项目请人工合并（禁静默覆盖）"; exit 1
  fi
  echo "🟢 检出 crules-flutter 戳——按重装/升级处理（默认跳过已存在；--force 三向合并，冲突带标记呈人；memory 永不覆盖）"
  guard_downgrade "$(grep -oE '<!-- crules-flutter: v[0-9]+\.[0-9]+\.[0-9]+' "$TARGET/CLAUDE.md" | head -1 | sed 's/.*v//')"
fi
MERGE_REL="$KIND/CLAUDE.md"
do_write "CLAUDE.md（$KIND 模板+戳）" "$TARGET/CLAUDE.md" "$(cat "$SRC/$KIND/CLAUDE.md")

$STAMP"
MERGE_REL="checklist.md" do_write "checklist.md" "$TARGET/checklist.md" "" "$SRC/checklist.md"
MERGE_REL=""

# analysis_options 智能落位（N3；1.0.34 补幂等与 --force 语义：原两分支无条件写盘——脚手架被替换成
#   基线后二次运行即被判「自定义」翻进 SIDE-CAR、多出重复伴生；伴生每次重拷冲掉用户已合并改动）
AO="$TARGET/analysis_options.yaml"; SC="$TARGET/analysis_options.crules-flutter.yaml"
if [ -f "$AO" ]; then
  if cmp -s "$SRC/analysis_options.yaml" "$AO"; then
    echo "  SKIP（已是本包基线）  $AO"
  else
    # 剥注释/空行后签名判定（F1：真机 flutter create 是 28 行注释版，行数判定是死代码）——
    # 剩余非空行 ⊆ {flutter_lints include, linter:, rules:} 即脚手架默认（无自定义规则）
    stripped=$(grep -vE '^[[:space:]]*#|^[[:space:]]*$' "$AO")   # [[:space:]]：BSD grep 不认 \s（v59 探针同款坑）
    if printf '%s\n' "$stripped" | grep -qvE '^[[:space:]]*(include: package:flutter_lints/flutter.yaml|linter:|rules:)?[[:space:]]*$'; then
      # 项目自定义 → 伴生三态（与 do_write 同语义）：缺失才写 / 已在默认 SKIP / --force 出 .new
      if [ -e "$SC" ] && [ "$FORCE" != "1" ]; then
        echo "  SKIP（伴生已在，防重拷冲掉已合并改动）  $SC"
      elif [ "$DRYRUN" = "1" ]; then
        echo "  DRY  伴生基线  $SC"
      elif [ -e "$SC" ] && [ "$FORCE" = "1" ]; then
        cp "$SRC/analysis_options.yaml" "$SC.new"; echo "  UPDATE-NEW（伴生对照合并后替换）  $SC.new"
      else
        cp "$SRC/analysis_options.yaml" "$SC"; echo "  SIDE-CAR（项目已有自定义 lint，基线落伴生文件，请人工合并）  $SC"
      fi
    else
      # 脚手架默认（无决策价值）→ 升级替换为基线，原文件留 .scaffold-bak
      if [ "$DRYRUN" != "1" ]; then cp "$AO" "$AO.scaffold-bak"; cp "$SRC/analysis_options.yaml" "$AO"; fi
      echo "  UPGRADE（脚手架默认 → lint 基线，原文件留 .scaffold-bak）  $AO"
    fi
  fi
else
  do_write "analysis_options.yaml（lint 基线）" "$AO" "" "$SRC/analysis_options.yaml"
fi

for f in "$SRC"/进阶/*.md; do MERGE_REL="进阶/$(basename "$f")" do_write "进阶/$(basename "$f")" "$TARGET/进阶/$(basename "$f")" "" "$f"; done
MERGE_REL=""
for f in "$SRC"/memory/*.md; do do_write ".claude/memory/$(basename "$f")" "$TARGET/.claude/memory/$(basename "$f")" "" "$f" "never"; done

# 骨架目录兜底（易用性批）：indexes/ 与 decisions/ 多文档引用为写入目标但无预建方——
#   功能从未坏（Claude Code Write 自动建父目录），坏的是首用者核对清单时把「目录暂不存在」
#   读成死引用（NAVIGATION「按需创建」是设计契约，此两行让目标树形状与文档一致）。dry-run 不建（只读承诺）
if [ "$DRYRUN" != "1" ]; then
  mkdir -p "$TARGET/.claude/memory/indexes" "$TARGET/.claude/memory/decisions"
fi

# 本机生成物 gitignore 幂等落位（1.0.5——取代 1.0.4 的模板侧文字指引：MAINTENANCE git 分层政策由安装器落成默认；1.0.7 增 .gate-exceptions）
# 五行缺失才追加，已有跳过；与 --force 无关（重复追加无意义）；dry-run 只报告
# 1.0.30：队列 entry 由精确名 `.pending-updates` 改通配 `.pending-updates*`（按会话分文件后同名多份）——
#   精确行比对不会命中通配 entry，故升级用户须**迁移旧行**（删除 + 追加），否则留下双行近似重复
#   （注：dry-run 只报告「将追加 N 行」，迁移动作本身不执行、故 GI_ADD 计数不含「删旧行」）
# 1.0.37：增 `.compliance-log`（SessionEnd 遵守度事实账——本机观测面，隐私红线见 hook 头注，不进 git）
GI="$TARGET/.gitignore"
GI_ADD=0
for entry in ".claude/memory/indexes/" ".claude/memory/.pending-updates*" ".claude/memory/.review-ledger" ".claude/memory/.gate-exceptions" ".claude/memory/.compliance-log"; do
  if [ -f "$GI" ] && grep -qxF "$entry" "$GI"; then continue; fi
  if [ "$DRYRUN" != "1" ]; then
    if [ "$entry" = ".claude/memory/.pending-updates*" ] && [ -f "$GI" ] \
       && grep -qxF ".claude/memory/.pending-updates" "$GI"; then
      grep -vxF ".claude/memory/.pending-updates" "$GI" > "${GI}.tmp" || true
      mv "${GI}.tmp" "$GI"
    fi
    [ -f "$GI" ] || printf '# crules-flutter：memory 本机生成物（政策与反悔方式见 .claude/memory/MAINTENANCE.md「git 分层」）\n' > "$GI"
    printf '%s\n' "$entry" >> "$GI"
  fi
  GI_ADD=$((GI_ADD+1))
done
[ "$GI_ADD" -gt 0 ] && echo "  GITIGNORE（幂等追加 ${GI_ADD} 行本机生成物）  $GI"
echo "== 汇总：写入 ${W}，跳过/保留 ${S}，合并并入 ${MG}，冲突待解 ${CF}，.new 待合并 ${N}，失败 ${E} =="
[ "${CF}" -eq 0 ] || echo "⚠️ 有 ${CF} 处冲突已带标记写回宪法文件——解标记前该文件非完整宪法；戳与 base 未动，逐块裁决后删 .crules-bak 与 .crules-conflicts"

# D3：hooks 环境显式降级警告（不阻塞安装——静默降级改显式，2026-09-05）
# D4（1.0.6 Windows 显式警告；1.0.17 批F2 改分层）：Windows 不再是「hooks 不支持」——
# deny-list 已有 PowerShell 原生实现（deny-list.ps1，PowerShell 工具会话生效）；
# 漂移队列 / Stop 提醒 / 遵守度事实账仍需 python（Git Bash/WSL 或 PATH 有 python 时可跑）
case "$(uname -s 2>/dev/null)/${OS:-}" in
  MINGW*|MSYS*|CYGWIN*)
    # Git Bash 会话：四 python hooks 取决于 python3（下方统一检测），deny-list 双实现各管各的 shell 域
    echo "ℹ️ Windows（Git Bash 会话）：Bash 工具走 deny-list.py、PowerShell 工具走 deny-list.ps1（1.0.17 起）——破坏性命令两域都拦；漂移队列/Stop 提醒/遵守度事实账需 python" ;;
  *Windows_NT)
    # cmd 直跑 install.sh（无 uname）：原生 PowerShell 会话形态
    echo "ℹ️ Windows 原生会话：deny-list 硬闸走 deny-list.ps1（PowerShell 工具 matcher，1.0.17 起，ps1 属用户实机验证面）；漂移队列/Stop 提醒/遵守度事实账需 python（无则缺），防线回到 Claude Code 原生权限确认" ;;
  *) : ;;
esac
if command -v python3 >/dev/null 2>&1; then
  python3 -c "import fcntl" 2>/dev/null || echo "⚠️ 本机 python3 缺 fcntl（Windows 常见）——deny-list 硬闸与 Stop 收尾提醒可用，pending-updates 漂移队列降级为无锁追加（仍记录）；compliance-log 单行追加本就不依赖 fcntl"
else
  echo "⚠️ 本机无 python3——deny-list.py / 漂移队列 / Stop 收尾提醒 / 遵守度事实账四 python hooks 不生效（Windows 原生 PowerShell 会话的 deny-list 走 ps1 不受此限，1.0.17 起）；防线回到 Claude Code 原生权限确认（README「环境要求与更新信任」）"
fi

echo "== 下一步 == ① 完成 CLAUDE.md §七【复制后必填】三选一 ② 填 §十二附录 ③ 填 .claude/memory/platform-pitfalls.md 支持矩阵（/crules-flutter:init 三段式初稿） ④ 有冲突标记或 .new 文件时对照合并后替换 ⑤ flutter-rules skill 与 7 agents 已随 plugin 就位"
[ "${E}" -eq 0 ] || exit 1
exit 0
