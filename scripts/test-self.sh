#!/usr/bin/env bash
# crules-flutter 脚本自测（批 2c）——应报错断言 + 幂等断言
# 注：幂等断言的测试命令经变量拼接构造（避免脚本源码含破坏命令完整字面串——deny-list 对
#     Bash 内字面串 deny-by-default，本文件须用 Write 工具落盘或分段拼接写入）
# 注2（bash 5.3 坑，2026-09-05）：set -u 下 $var 紧邻多字节字符（中文标点，如 $lst））会把多字节
#     首字节吸入变量名致 unbound 中止（brew bash 5.3.15 实测；LC_ALL=C 与 ${var} 花括号均免疫）——
#     本包三脚本此类位置一律花括号隔离（v59 BSD grep 环境坑同款教训）
set -uo pipefail
SRC=$(cd "$(dirname "$0")/.." && pwd)
# 环境守卫（1.0.13）：本脚本两条断言（draft / tag）依赖 git 历史，其余 34 条不依赖（1.0.32 断言 31→36 时同步）。在无 .git 的拷贝里
# （典型：插件 cache = 全仓文件快照、非 clone）draft 吃 git 报错码 128 → **假红**；tag 则落到「读 HEAD 失败」
# 分支 → **假绿**，其声称守护的「1.0.2 D2 防 tag 打在 bump 前旧树」版本比对从未执行。假绿比报错更贵——
# 故显式拒绝，不静默变形。
git -C "$SRC" rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
  echo "❌ test-self.sh 须在 git 树内运行（draft/tag 两断言依赖 git 历史）——插件 cache 是文件快照、非 git 仓"; exit 1; }
PASS=0; FAIL=0
t() { eval "$2" >/dev/null 2>&1; rc=$?
  if [ "$rc" = "$1" ]; then PASS=$((PASS+1)); echo "PASS  $3"; else FAIL=$((FAIL+1)); echo "FAIL  $3（rc=$rc 期望 $1）"; fi; }
# 夹具根一律 mktemp（1.0.15）：固定 /tmp 路径跨实例并发互踩实锤（收尾 rm 删并发实例夹具 →
# install.sh [ -d ] exit 2 等四种失败签名，见 CHANGELOG 1.0.13 连带发现）；模板留 cf- 前缀可寻残骸
D=$(mktemp -d /tmp/cf-selftest.XXXXXX)
mkdir -p "$D/old"
printf '# 老项目\n' > "$D/old/CLAUDE.md"
t 1 "bash $SRC/scripts/install.sh $D/old --app"           "install 老项目（无戳）应中止"
t 1 "bash $SRC/scripts/release.sh abc"                     "release 非法版本号应报错"
t 0 "bash $SRC/scripts/release.sh draft"                    "release draft 应正常出稿（外审②回归断言）"
t 0 "python3 $SRC/hooks/test_deny_list.py"                 "deny-list fixture 应全绿"
# 1.0.17 批F2 双驱：ps1 侧夹具在 PowerShell 可得时全跑（CI pwsh 步），否则 SKIP 不红——
# 本机 mac 无 pwsh = SKIP（Windows 实机为用户最终闸，裁决单 §8）；不占断言数（同 AO dart SKIP 先例）
if command -v pwsh >/dev/null 2>&1; then
  t 0 "pwsh -NoProfile -File $SRC/hooks/test_deny_list.ps1" "deny-list.ps1 fixture 应全绿（pwsh）"
elif command -v powershell >/dev/null 2>&1; then
  t 0 "powershell -NoProfile -ExecutionPolicy Bypass -File $SRC/hooks/test_deny_list.ps1" "deny-list.ps1 fixture 应全绿（powershell）"
else
  echo "SKIP  deny-list.ps1 fixture（本机无 PowerShell——Windows 实机为最终闸，CI pwsh 步硬拦）"
fi
t 0 "python3 $SRC/hooks/test_stop_reminder.py"            "stop-reminder fixture 应全绿（A3 读侧闭环）"
t 0 "python3 $SRC/hooks/test_pending_updates.py"          "pending-updates 写侧 fixture 应全绿（1.0.30 队列分文件）"
t 1 "bash $SRC/scripts/release.sh tag 9.9.9"               "release tag 版本不匹配应报错（1.0.2 D2——防 tag 打在 bump 前旧树）"
# 非 git 树守卫的反向断言（1.0.13）：把脚本本身拷进非 git 目录跑，须**显式拒绝**。判据三条件缺一不可——
# rc≠0 单独不成立：守卫缺失时该拷贝会跑完全套，并因既有 FAIL>0 同样退出非零（又一个假绿）；故另须确认
# 提示语命中、且输出无 PASS 行（守卫在断言之前就中止，一条都没跑）。
GN="$D/nogit"; rm -rf "$GN"; mkdir -p "$GN/scripts"; cp "$SRC/scripts/test-self.sh" "$GN/scripts/"
go=$(bash "$GN/scripts/test-self.sh" 2>&1); grc=$?
[ "$grc" != "0" ] && echo "$go" | grep -q "须在 git 树内" && ! echo "$go" | grep -q '^PASS' \
  && { PASS=$((PASS+1)); echo "PASS  非 git 树守卫显式拒绝（1.0.13）"; } \
  || { FAIL=$((FAIL+1)); echo "FAIL  非 git 树守卫（rc=$grc——未拒绝 / 未在断言前中止）"; }
t 1 "bash $SRC/scripts/install.sh $D/old --app --upgrade"  "upgrade 无戳老项目应中止（D3·1.0.6）"
U=$(mktemp -d /tmp/cf-upg.XXXXXX)
printf '<!-- crules-flutter: v0.0.1 @ 2026-01-01 -->\n' > "$U/CLAUDE.md"
o=$(printf 'n\n' | bash $SRC/scripts/install.sh $U --app --upgrade 2>&1); rc=$?
[ "$rc" = "0" ] && ! ls "$U/checklist.md" >/dev/null 2>&1 && echo "$o" | grep -q 已取消 \
  && { PASS=$((PASS+1)); echo "PASS  upgrade 拒绝确认零改动（D3·1.0.6）"; } || { FAIL=$((FAIL+1)); echo "FAIL  upgrade 取消路径（rc=$rc）"; }
rm -rf "$U"   # 原代码从不收尾（靠下一跑开头 rm 兜底）——mktemp 化后兜底消失，须自清

# F2 回归三断言（真机 fixture 固化——2026-08-27 flutter create 28 行注释版产物签入 testdata/）
T1=$(mktemp -d /tmp/cf-ao1.XXXXXX); T2=$(mktemp -d /tmp/cf-ao2.XXXXXX)
cp "$SRC/scripts/testdata/scaffold-analysis_options.yaml" "$T1/analysis_options.yaml"
printf 'include: package:flutter_lints/flutter.yaml\nlinter:\n  rules:\n    - always_use_package_imports\n' > "$T2/analysis_options.yaml"
o1=$(bash $SRC/scripts/install.sh $T1 --app 2>/dev/null | grep -c UPGRADE)
[ "$o1" -ge 1 ] && [ -f "$T1/analysis_options.yaml.scaffold-bak" ] && { PASS=$((PASS+1)); echo "PASS  真机脚手架 fixture → UPGRADE（F1 回归）"; } || { FAIL=$((FAIL+1)); echo "FAIL  脚手架应 UPGRADE"; }
o2=$(bash $SRC/scripts/install.sh $T2 --app 2>/dev/null | grep -c SIDE-CAR)
[ "$o2" -ge 1 ] && grep -q 'always_use_package_imports' "$T2/analysis_options.yaml" && { PASS=$((PASS+1)); echo "PASS  自定义 lint → SIDE-CAR 伴生且原文保留"; } || { FAIL=$((FAIL+1)); echo "FAIL  自定义应 SIDE-CAR"; }
printf 'WR-SENTINEL\n' > "$T1/.claude/memory/business-rules.md"
bash $SRC/scripts/install.sh $T1 --app --force >/dev/null 2>&1
grep -q 'WR-SENTINEL' "$T1/.claude/memory/business-rules.md" && [ -f "$T1/CLAUDE.md.new" ] && { PASS=$((PASS+1)); echo "PASS  force 升级：memory 哨兵 KEEP + CLAUDE.md 出 .new"; } || { FAIL=$((FAIL+1)); echo "FAIL  force 安全升级"; }
rm -rf "$T1" "$T2"

# 0.4.0 批1断言（设计 §5 test-self 行）：落位 8 模板 / init 三处必填 / twin 一致性
T4=$(mktemp -d /tmp/cf-pitfalls.XXXXXX)
bash $SRC/scripts/install.sh $T4 --app >/dev/null 2>&1
nm=$(ls "$T4/.claude/memory"/*.md 2>/dev/null | wc -l | tr -d ' ')
[ "$nm" = "8" ] && { PASS=$((PASS+1)); echo "PASS  memory 落位 8 模板"; } || { FAIL=$((FAIL+1)); echo "FAIL  memory 应落位 8 模板（实为 ${nm}）"; }
rm -rf "$T4"
grep -q '支持矩阵' "$SRC/commands/init.md" && grep -q '矩阵' "$SRC/scripts/install.sh" && { PASS=$((PASS+1)); echo "PASS  init 必填三处引导（init.md + install.sh 下一步提示均含矩阵）"; } || { FAIL=$((FAIL+1)); echo "FAIL  init 三处缺矩阵引导"; }
# twin:mem-files 单一权威（0.5.1 断言，1.0.4 精简批减一向——进阶侧表已删改指针，
# 现只看守 memory/README.md 表 == 实际模板数；加载时机细节随表走）
act=$(ls "$SRC"/memory/*.md | grep -v 'README.md' | wc -l | tr -d ' ')
lst=$(sed -n '/twin:mem-files/,/^$/p' "$SRC/memory/README.md" | grep -oE '`[A-Za-z-]+\.md`' | sort -u | wc -l | tr -d ' ')
[ "$act" = "$lst" ] && [ "$act" -ge 7 ] && { PASS=$((PASS+1)); echo "PASS  twin:mem-files 一致（实际模板 $act = 表列 ${lst}）"; } || { FAIL=$((FAIL+1)); echo "FAIL  twin:mem-files 漂移（act=$act lst=${lst}）"; }

# help 全景计数闸（四轮外审①：help.md 自称权威全表却漏改进阶篇数——同型 0.6.2 自嘲带，上闸）
adv=$(ls "$SRC"/进阶/*.md | wc -l | tr -d ' ')
mem=$(ls "$SRC"/memory/*.md | wc -l | tr -d ' ')
said=$(sed -n 's/.*进阶 \([0-9][0-9]*\) 篇 + memory \([0-9][0-9]*\) 模板.*/\1 \2/p' "$SRC/commands/help.md" | head -1)
[ "$said" = "$adv $mem" ] && { PASS=$((PASS+1)); echo "PASS  help 全景计数一致（进阶 $adv + memory $mem）"; } || { FAIL=$((FAIL+1)); echo "FAIL  help 计数漂移（help 说「${said:-未匹配}」，实际 进阶 $adv + memory $mem）"; }

# 1.0.11 批C F4：常驻面字数预算闸——防「无意间回潮」（1.0.10 刚做过一轮 −0.7k 下沉）。
# 口径 = **字符数**（python len，UTF-8 解码后）——勿用 `wc -m`：macOS 未设 locale 时按字节计
# （实测同一文件 wc -m 27915〔字节〕vs len 14769〔字符〕，批C 本人即踩此坑并写错结论）。
# 锚值 = 批C 实测（app 15833 / plugin 14532），留 ~12% 裕量；超线须显式裁（裁模板 or
# 上调预算并记 CHANGELOG），不静默过。
zen_app=$(python3 -c "import sys;print(sum(len(open(f,encoding='utf-8').read()) for f in sys.argv[1:]))" "$SRC/app/CLAUDE.md" "$SRC/memory/NAVIGATION.md")
zen_plu=$(python3 -c "import sys;print(sum(len(open(f,encoding='utf-8').read()) for f in sys.argv[1:]))" "$SRC/plugin/CLAUDE.md" "$SRC/memory/NAVIGATION.md")
if [ "${zen_app:-0}" -le 18000 ] && [ "${zen_plu:-0}" -le 16500 ]; then
  PASS=$((PASS+1)); echo "PASS  常驻面字数预算（app ${zen_app}/18000，plugin ${zen_plu}/16500 字符）"
else
  FAIL=$((FAIL+1)); echo "FAIL  常驻面超预算（app ${zen_app}/18000，plugin ${zen_plu}/16500）——裁模板或显式上调预算记 CHANGELOG"
fi

# 0.4.1 断言（A1 回归）：模板 AO 内容过真 dart analyzer 零 warning（死配置零容忍——
# cancelled_token_use / map 形态 disable 两事件；本机无 dart 时 SKIP 不计 FAIL，CI 由 ci.yml setup-dart 步硬拦）
if command -v dart >/dev/null 2>&1; then
  DA=$(mktemp -d /tmp/cf-ao-dart.XXXXXX); rm -rf "$DA"   # mktemp 只占唯一名——dart create 要求目标目录不存在
  dart create --no-pub "$DA" >/dev/null 2>&1
  (cd "$DA" && dart pub add dev:flutter_lints >/dev/null 2>&1)
  cp "$SRC/analysis_options.yaml" "$DA/analysis_options.yaml"
  out=$( (cd "$DA" && dart analyze . 2>&1) || true )
  w=$(printf '%s' "$out" | grep -ciE 'warning|error' || true)
  ran=$(printf '%s' "$out" | grep -c 'Analyzing' || true)
  # 门 = 零 warning/error（死配置产 warning；脚手架 hello-world 撞 avoid_print 的 info 放行——
  # 老版 dart 输出「info - …」新版「info • …」均不匹配）；ran 守卫防「没跑起来却空过」的假绿
  [ "${w:-1}" -eq 0 ] && [ "${ran:-0}" -ge 1 ] && { PASS=$((PASS+1)); echo "PASS  模板 AO 内容过真 analyzer 零 warning（A1 回归）"; } || { FAIL=$((FAIL+1)); echo "FAIL  AO 内容含 warning/error ×${w:-?} 或未跑起（A1 回归）"; }
  rm -rf "$DA"
else
  echo "SKIP  AO 内容断言（本机无 dart；CI setup-dart 步硬拦）"
fi

# 1.0.12 批D P1：孪生同文块生成闸——canonical 单一源与四文件同步。**在 /tmp 副本渲染后比对**
# （不原地改写被跟踪文件——方案 §4 R16）；render 内含双守卫（登记一致性 + 内容同步）。
# P3 已行（1.0.15）：旧 byte 互锁 2 条删（试点两 minor〔1.0.13/1.0.14〕闸均绿）——覆盖差如实记：
# 围栏外节内文本不再逐字比对，围栏内由本闸 + 锚串守卫全权。
T6=$(mktemp -d)
mkdir -p "$T6/scripts" "$T6/canonical" "$T6/app" "$T6/plugin" "$T6/commands"
cp "$SRC/scripts/render-blocks.py" "$T6/scripts/"
cp "$SRC"/canonical/*.md "$T6/canonical/"
cp "$SRC/app/CLAUDE.md" "$T6/app/"; cp "$SRC/plugin/CLAUDE.md" "$T6/plugin/"
cp "$SRC/commands/help.md" "$T6/commands/"; cp "$SRC/README.md" "$T6/"
rout=$(python3 "$T6/scripts/render-blocks.py" 2>&1); rrc=$?
same=1
for p in app/CLAUDE.md plugin/CLAUDE.md commands/help.md README.md; do cmp -s "$T6/$p" "$SRC/$p" || same=0; done
# 锚串守卫（review R2）：canonical 清空/截断时 render 双侧对称 → 比对仍绿；锚串**直查仓内**
# 目标文件（不经比对），堵「整段静默消失」——P3 删旧 byte 断言后这是四块的关键防线之一
anchor_bad=0
for a in "app/CLAUDE.md|轻量〔light〕" "plugin/CLAUDE.md|轻量〔light〕" \
         "app/CLAUDE.md|收尾时序**三档**" "plugin/CLAUDE.md|收尾时序**三档**" \
         "app/CLAUDE.md|.gate-exceptions" "plugin/CLAUDE.md|.gate-exceptions" \
         "commands/help.md|收尾档按任务规模三档判定" "README.md|收尾档按任务规模三档判定"; do
  af="${a%%|*}"; as="${a##*|}"
  grep -qF -- "$as" "$SRC/$af" || { anchor_bad=1; echo "  ↳ $af 缺锚串「$as」——canonical 疑似清空/截断"; }
done
if [ "$rrc" = "0" ] && [ "$same" = "1" ] && [ "$anchor_bad" = "0" ]; then
  PASS=$((PASS+1)); echo "PASS  孪生同文块生成闸（canonical↔四文件同步 + 锚串在位）"
else
  FAIL=$((FAIL+1)); echo "FAIL  同文块异常（render rc=$rrc / 同步 $same / 锚串 $anchor_bad）：$(printf '%s' "$rout" | head -3 | tr '\n' ' ')"
fi
rm -rf "$T6"

# 0.5.1 断言（D1）：双模板孪生结构守护——节序号集一致 + 孪生节 ^- 条数一致
# （§二豁免：plugin 独有「发版特殊性」条目与破坏性操作行文差异系合法不对称；
#   与 twin:mem-files 同哲学——锚点机械守护替代「两模板同源对照改」人肉纪律）
tt_sec() { grep -oE '^## [一二三四五六七八九十]+、' "$1" | tr -d '\n'; }
tt_cnt() { awk -v sec="## $2、" 'index($0, sec)==1 {f=1; next} /^## /{f=0} f && /^- /{c++} END{print c+0}' "$1"; }
tt_ok=1
tsa=$(tt_sec "$SRC/app/CLAUDE.md"); tsp=$(tt_sec "$SRC/plugin/CLAUDE.md")
[ "$tsa" = "$tsp" ] || tt_ok=0
for s in 一 三 四 五 六; do
  [ "$(tt_cnt "$SRC/app/CLAUDE.md" "$s")" = "$(tt_cnt "$SRC/plugin/CLAUDE.md" "$s")" ] || { echo "  §$s 漂移：app=$(tt_cnt "$SRC/app/CLAUDE.md" "$s") plugin=$(tt_cnt "$SRC/plugin/CLAUDE.md" "$s")"; tt_ok=0; }
done
[ "$tt_ok" = "1" ] && { PASS=$((PASS+1)); echo "PASS  双模板孪生结构一致（节序号集 + §一/三/四/五/六 条数，D1 回归）"; } || { FAIL=$((FAIL+1)); echo "FAIL  双模板孪生漂移（见上——单侧改动须同源对照改或显式豁免）"; }

# 0.6.2 断言：孪生语义闸——对外口径三处一致 + 停更栈禁推（两轮审查抓到的 grep 级漂移上闸）
sem_ok=1
# ① README 横幅版本 == plugin.json 分发版本
pj_ver=$(grep -o '"version": "[^"]*"' "${SRC}/.claude-plugin/plugin.json" | head -1 | cut -d'"' -f4)
br_ver=$(grep -m1 '当前状态：' "${SRC}/README.md" | grep -oE '当前状态：[0-9]+\.[0-9]+\.[0-9]+' | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
if [ -n "${pj_ver}" ] && [ "${br_ver}" = "${pj_ver}" ]; then :; else sem_ok=0; echo "  ↳ README 横幅版本(${br_ver:-无}) ≠ plugin.json(${pj_ver})"; fi
# ② help.md hooks ×N == hooks/*.py 实际数
hook_n=$(ls "${SRC}"/hooks/*.py 2>/dev/null | grep -vc test_ || true)
help_n=$(grep -oE 'hooks ×[0-9]+' "${SRC}/commands/help.md" | head -1 | grep -oE '[0-9]+')
if [ -n "${help_n}" ] && [ "${help_n}" = "${hook_n}" ]; then :; else sem_ok=0; echo "  ↳ help.md hooks ×${help_n:-无} ≠ 实际 ${hook_n}"; fi
# ③ 停更栈禁推：agents 无 screenutil 正面示例；app 模板无未注记的裸 hive
su_hit=$(grep -ih screenutil "${SRC}"/agents/*.md 2>/dev/null | grep -cv '停更' || true)
[ "${su_hit}" -eq 0 ] || { sem_ok=0; echo "  ↳ agents 含 screenutil ×${su_hit}（A2 已判停更，勿作示例）"; }
bare_hive=$(grep -iw 'hive' "${SRC}/app/CLAUDE.md" | grep -cv '停更' || true)
[ "${bare_hive}" -eq 0 ] || { sem_ok=0; echo "  ↳ app 模板存在未注记裸 hive ×${bare_hive}（原版停更 2022-06，须 hive_ce 或停更注记）"; }
[ "${sem_ok}" = "1" ] && { PASS=$((PASS+1)); echo "PASS  孪生语义闸（横幅/help/hooks 版本口径 + 停更栈 screenutil·hive 禁推）"; } || { FAIL=$((FAIL+1)); echo "FAIL  语义闸（见上——对外口径与停更栈表述漂移）"; }

# 0.6.7 断言①：easy_localization 注记闸——agents 命中行须带「不推荐/维护缓慢」注记
# （外审 G4 残留：并列示例裸点名已被 §七 预设 A 判不推荐；沿用 :89 停更排除先例）
el_bad=$(grep -ih 'easy_localization' "${SRC}"/agents/*.md 2>/dev/null | grep -cv '不推荐\|维护缓慢\|停更' || true)
[ "${el_bad}" -eq 0 ] && { PASS=$((PASS+1)); echo "PASS  easy_localization 注记闸（agents 无裸并列点名）"; } || { FAIL=$((FAIL+1)); echo "FAIL  agents 含未注记 easy_localization ×${el_bad}（§七 预设 A 已判不推荐，须带注记）"; }

# 0.6.7 断言②：screenutil 白名单闸——全分发面 flutter_screenutil 命中行须带停更类注记
# （注记词「已停更 或 维护缓慢」二选一——app:185 前者 / §七 A2 档后者，实测措辞不同）
su_bad=$(grep -h 'flutter_screenutil' "${SRC}"/agents/*.md "${SRC}"/app/CLAUDE.md "${SRC}"/plugin/CLAUDE.md "${SRC}"/checklist.md 2>/dev/null | grep -cv '已停更\|停更\|维护缓慢' || true)
[ "${su_bad}" -eq 0 ] && { PASS=$((PASS+1)); echo "PASS  flutter_screenutil 白名单闸（命中仅停更/维护缓慢注记行）"; } || { FAIL=$((FAIL+1)); echo "FAIL  存在未注记 flutter_screenutil 正面表述 ×${su_bad}（A2 已判停更）"; }


# P1b 断言①：档位四方同源闸——§十二预设块 canonical 串双模板全查（19 串×2；1.0.7 增校验层指针串、
# 1.0.8 「不计入」随治理句外迁 README 维护节而移除），三档标记/默认
# help·README·init 各 4 串，收尾三档词 help·README 各 8 串，init 结构 2 串（方案 §7 P1b·A4：
# 四方 = 附录块 ↔ help ↔ README ↔ §三收尾行；逐条打印漂移，整块计 1 个 PASS/FAIL）
gear_ok=1
ga=('轻量〔light〕' '标准〔normal〕' '完整〔full〕' '默认标准' '按任务规模三档' '单点修复' '跨域大改' '公开 API' '资损面' 'review 豁免' 'Gate 例外台账' '校验层' '记忆库：关' '记忆库：开' '可单关' '编排：开' 'plan-reviewer：默认启用' '不可配置' '进阶/审查与复核纪律')
gb=('轻量〔light〕' '标准〔normal〕' '完整〔full〕' '默认标准')
gc=('按任务规模三档' '单点修复' '跨域大改' '公开 API' '资损面' 'review 豁免' 'Gate 例外台账' '校验层')
gd=('档位预设' '不可配置')
for f in app/CLAUDE.md plugin/CLAUDE.md; do
  for s in "${ga[@]}"; do grep -qF -- "${s}" "${SRC}/${f}" || { gear_ok=0; echo "  ↳ ${f} 缺「${s}」"; }; done
done
for f in commands/help.md README.md commands/init.md; do
  for s in "${gb[@]}"; do grep -qF -- "${s}" "${SRC}/${f}" || { gear_ok=0; echo "  ↳ ${f} 缺「${s}」"; }; done
done
for f in commands/help.md README.md; do
  for s in "${gc[@]}"; do grep -qF -- "${s}" "${SRC}/${f}" || { gear_ok=0; echo "  ↳ ${f} 缺「${s}」"; }; done
done
for s in "${gd[@]}"; do grep -qF -- "${s}" "${SRC}/commands/init.md" || { gear_ok=0; echo "  ↳ commands/init.md 缺「${s}」"; }; done
[ "${gear_ok}" = "1" ] && { PASS=$((PASS+1)); echo "PASS  档位四方同源闸（附录块↔help↔README↔§三收尾行，三档标记/默认/收尾三档/校验层）"; } || { FAIL=$((FAIL+1)); echo "FAIL  档位四方同源闸（见上漂移清单）"; }

# 1.0.7 断言①：Gate 例外台账同源闸——.gate-exceptions 定义四点同源（双模板 Gate 例外节 ↔ MAINTENANCE ↔ install.sh）
# （外审 🟡2 处置：台账被四处引用、零定义——定义落四处 + 上闸，防「意图先于机制」复发）
ge_ok=1
for f in app/CLAUDE.md plugin/CLAUDE.md memory/MAINTENANCE.md scripts/install.sh; do
  grep -qF -- ".gate-exceptions" "${SRC}/${f}" || { ge_ok=0; echo "  ↳ ${f} 缺「.gate-exceptions」"; }
done
[ "${ge_ok}" = "1" ] && { PASS=$((PASS+1)); echo "PASS  Gate 例外台账同源闸（双模板 Gate 例外节↔MAINTENANCE↔install.sh）"; } || { FAIL=$((FAIL+1)); echo "FAIL  Gate 例外台账同源闸（见上漂移清单）"; }

# 1.0.27 断言：评审包自护条款防删改检查——两张评审卡「缺包即停」条款 + 令牌语法须在位，被删/改时此处变红。
# 令牌契约见 进阶/Agent编排.md「评审包契约化」；若将来加 hooks 派单闸（派单时机械校验令牌），闸校验的
# 即同一令牌——本断言是其文档侧锚（F11 教训：新增执行面不得零断言）。
pk_ok=1
for f in agents/plan-reviewer.md agents/reviewer.md; do
  for s in '缺包即停' '【切片包】' '【切片包-免】'; do
    grep -qF -- "${s}" "${SRC}/${f}" || { pk_ok=0; echo "  ↳ ${f} 缺「${s}」"; }
  done
done
for s in '【切片包-免】' '派单前置条件'; do
  grep -qF -- "${s}" "${SRC}/进阶/Agent编排.md" || { pk_ok=0; echo "  ↳ 进阶/Agent编排.md 缺「${s}」"; }
done
[ "${pk_ok}" = "1" ] && { PASS=$((PASS+1)); echo "PASS  评审包自护条款在位（两卡缺包即停 + Agent编排 令牌/派单前置）"; } || { FAIL=$((FAIL+1)); echo "FAIL  评审包自护条款漂移（见上）"; }

# 1.0.32 信息架构批断言（外部信息架构评审三弱项 + 核实发现同族漂移）：链接解析 / 坑库速查对账 /
# memory 清单回潮 / checklist 指针限定与编号对账——共 5 条（31→36）
# ① 链接解析闸：全仓 md 链接须指向真实存在的文件（CHANGELOG 豁免——历史流水账链到后来
#    删除的文档属正常）。占位指引（指向按需创建的生成物）一律写纯文字、不写链接格式。
link_bad=$(python3 - "$SRC" <<'PYEOF'
import os, re, sys
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
root = sys.argv[1]
pat = re.compile(r'\[[^\]]*\]\(([^)]+)\)')
bad = []
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in ('.git', '__pycache__', '.claude', 'node_modules')]
    for fn in filenames:
        if not fn.endswith('.md'): continue
        p = os.path.join(dirpath, fn)
        rel = os.path.relpath(p, root).replace(os.sep, '/')
        if rel == 'CHANGELOG.md': continue
        for i, line in enumerate(open(p, encoding='utf-8').read().splitlines(), 1):
            for m in pat.finditer(line):
                t = m.group(1).strip()
                if t.startswith(('http://', 'https://', '#', 'mailto:')): continue
                path = t.split('#')[0]
                if not path: continue
                if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(p), path))):
                    bad.append(rel + ':' + str(i) + ' -> ' + t)
print(len(bad))
for b in bad: print('  ' + b)
PYEOF
)
n_dead=$(printf '%s' "$link_bad" | head -1)
if [ "${n_dead:-1}" = "0" ]; then
  PASS=$((PASS+1)); echo "PASS  链接解析闸（全仓 md 链接零死链，CHANGELOG 豁免）"
else
  FAIL=$((FAIL+1)); echo "FAIL  死链 ×${n_dead:-?}（占位改纯文字或补目标文件）："; printf '%s\n' "$link_bad" | tail -n +2
fi

# ② 坑库症状速查对账：每卡须带「关键词」行；「症状速查」表体须与全部卡（关键词/平台/卡题）
#    的机械重排一字不差——改卡不同步表、加卡漏补、手改表即红
idx_out=$(python3 - "$SRC/skills/flutter-rules/references/platform-pitfalls.md" <<'PYEOF'
import re, sys
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
lines = open(sys.argv[1], encoding='utf-8').read().splitlines()
cards = []
errs = []
i = 0
while i < len(lines):
    m = re.match(r'^### \[([^]]+)\]\s*(.+)$', lines[i])
    if m:
        kw = None
        j = i + 1
        while j < len(lines) and not lines[j].startswith('### ') and not lines[j].startswith('## '):
            km = re.match(r'^- 关键词：(.+)$', lines[j])
            if km: kw = km.group(1).strip(); break
            j += 1
        if kw is None: errs.append('卡缺关键词行: ' + lines[i])
        else: cards.append((kw, m.group(1).strip(), m.group(2).strip()))
    i += 1
exp = ['| ' + kw + ' | ' + plat + ' | ' + title + ' |' for kw, plat, title in cards]
act = []
in_sec = False
seen_hdr = 0
for ln in lines:
    if ln.startswith('## 症状速查'): in_sec = True; continue
    if in_sec and ln.startswith('## '): break
    if in_sec and ln.startswith('|'):
        seen_hdr += 1
        if seen_hdr > 2: act.append(ln)
if not in_sec: errs.append('缺 ## 症状速查 节')
if not cards: errs.append('未解析到坑卡')
if exp != act:
    errs.append('表与卡不一致（期望 ' + str(len(exp)) + ' 行，实际 ' + str(len(act)) + ' 行）')
    for k in range(max(len(exp), len(act))):
        e = exp[k] if k < len(exp) else '(缺行)'
        a = act[k] if k < len(act) else '(缺行)'
        if e != a: errs.append('  第' + str(k+1) + '行 期望: ' + e + ' / 实际: ' + a)
if errs:
    print('BAD'); [print(x) for x in errs]
else:
    print('OK ' + str(len(cards)))
PYEOF
)
if printf '%s' "$idx_out" | grep -q '^OK'; then
  PASS=$((PASS+1)); echo "PASS  坑库症状速查对账（$(printf '%s' "$idx_out" | head -1 | cut -d' ' -f2) 卡，表逐字一致）"
else
  FAIL=$((FAIL+1)); echo "FAIL  坑库速查表与卡不一致："; printf '%s\n' "$idx_out"
fi

# ③ memory 清单回潮闸：进阶/ 各篇代码围栏内不得罗列 ≥3 个 memory 模板文件名——
#    「哪个文件何时加载」单一权威在 memory/README.md 总表（抄即烂：记忆库体系.md 曾抄 5 漏 2）
enum_bad=$(python3 - "$SRC/进阶" <<'PYEOF'
import os, re, sys
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
names = ('NAVIGATION.md', 'MAINTENANCE.md', 'patterns.md', 'business-rules.md', 'INVARIANTS.md', 'reference-map.md', 'platform-pitfalls.md')
bad = []
d = sys.argv[1]
for fn in sorted(os.listdir(d)):
    if not fn.endswith('.md'): continue
    text = open(os.path.join(d, fn), encoding='utf-8').read()
    for block in re.findall(r'```(.*?)```', text, re.S):
        hits = {n for n in names if n in block}
        if len(hits) >= 3: bad.append(fn + ' 围栏内罗列 ' + str(len(hits)) + ' 个 memory 文件名')
print(len(bad))
for b in bad: print('  ' + b)
PYEOF
)
n_enum=$(printf '%s' "$enum_bad" | head -1)
if [ "${n_enum:-1}" = "0" ]; then
  PASS=$((PASS+1)); echo "PASS  memory 清单无回潮（进阶/ 围栏零罗列，单一权威在 memory/README.md）"
else
  FAIL=$((FAIL+1)); echo "FAIL  memory 清单回潮 ×${n_enum:-?}（改指针引用，不抄清单）："; printf '%s\n' "$enum_bad" | tail -n +2
fi

# ④ checklist 指针限定闸：skills 内提及 checklist 须带「项目根」——skill 随 plugin 缓存分发、
#    与 checklist.md（装在消费工程根）不同目录，裸写不可解析
ck_bad=$(grep -rn 'checklist' "$SRC/skills" | grep -v '项目根' || true)
if [ -z "$ck_bad" ]; then
  PASS=$((PASS+1)); echo "PASS  checklist 指针限定（skills 提及均带「项目根」）"
else
  FAIL=$((FAIL+1)); echo "FAIL  skills 内裸写 checklist（须「项目根 \`checklist.md\`）："; printf '%s\n' "$ck_bad"
fi

# ⑤ checklist 编号对账：通用条目 0–9 连续在位（自述「10 条·编号 0–9」与实际一致）
ck_nums=$(grep -oE '^\*\*[0-9]+\.' "$SRC/checklist.md" | grep -oE '[0-9]+' | sort -nu | tr -d '\n')
if [ "$ck_nums" = "0123456789" ]; then
  PASS=$((PASS+1)); echo "PASS  checklist 编号 0–9 对账（连续无缺号）"
else
  FAIL=$((FAIL+1)); echo "FAIL  checklist 编号漂移（实得 ${ck_nums:-无}，期望 0123456789）"
fi

# 1.0.33 断言：三 hook AV 弹框压制守卫防删改（36→37）——Windows 注入型管控 agent 会使 hook 进程期
# 访问违例弹模态框、挂起等点击直至超时；守卫（win32 判定 + SetErrorMode(0x2)）被删/改时此处变红。
# 必须落在脚本内部（CPython 启动覆写继承 error mode，父进程预设无效）；实测依据见 CHANGELOG 1.0.33。
av_ok=1
for f in hooks/deny-list.py hooks/pending-updates.py hooks/stop-reminder.py; do
  for s in 'sys.platform == "win32"' 'SetErrorMode(0x0002)'; do
    grep -qF -- "${s}" "${SRC}/${f}" || { av_ok=0; echo "  ↳ ${f} 缺「${s}」"; }
  done
done
[ "${av_ok}" = "1" ] && { PASS=$((PASS+1)); echo "PASS  三 hook AV 弹框压制守卫在位（win32 判定 + SetErrorMode）"; } || { FAIL=$((FAIL+1)); echo "FAIL  AV 弹框压制守卫漂移（见上）"; }

# 1.0.5 断言：gitignore 幂等落位——首装补四行（1.0.7 增 .gate-exceptions），重装不重复（取代 1.0.4 模板侧文字指引）
T5=$(mktemp -d /tmp/cf-gi.XXXXXX)
bash $SRC/scripts/install.sh "$T5" --app >/dev/null 2>&1
gi1=$(grep -c '^\.claude/memory' "$T5/.gitignore" 2>/dev/null) || gi1=0
bash $SRC/scripts/install.sh "$T5" --app --force >/dev/null 2>&1
gi2=$(grep -c '^\.claude/memory' "$T5/.gitignore" 2>/dev/null) || gi2=0
[ "${gi1}" = "4" ] && [ "${gi2}" = "4" ] && { PASS=$((PASS+1)); echo "PASS  gitignore 幂等落位（首装 4 行，force 重装仍 4 行）"; } || { FAIL=$((FAIL+1)); echo "FAIL  gitignore 落位（首装 ${gi1} 行 / 重装 ${gi2} 行，期望 4/4）"; }
rm -rf "$T5"

# 1.0.30 断言：gitignore entry 精确名 → 通配名（.pending-updates → .pending-updates*，队列按会话分文件）。
# 升级用户旧 gitignore 已有精确行——须迁移旧行而非留下双行近似重复（install.sh 精确行比对不会命中通配 entry）。
T5B=$(mktemp -d /tmp/cf-gi2.XXXXXX)
printf '.claude/memory/indexes/\n.claude/memory/.pending-updates\n.claude/memory/.review-ledger\n.claude/memory/.gate-exceptions\n' > "$T5B/.gitignore"
bash $SRC/scripts/install.sh "$T5B" --app >/dev/null 2>&1
gi3=$(grep -c '^\.claude/memory' "$T5B/.gitignore" 2>/dev/null) || gi3=0
gi_old=$(grep -cxF '.claude/memory/.pending-updates' "$T5B/.gitignore" 2>/dev/null) || gi_old=0
gi_new=$(grep -cxF '.claude/memory/.pending-updates*' "$T5B/.gitignore" 2>/dev/null) || gi_new=0
[ "${gi3}" = "4" ] && [ "${gi_old}" = "0" ] && [ "${gi_new}" = "1" ] \
  && { PASS=$((PASS+1)); echo "PASS  gitignore 升级迁移（旧精确行已换通配新行，仍 4 行）"; } \
  || { FAIL=$((FAIL+1)); echo "FAIL  gitignore 升级迁移（${gi3} 行 / 旧行 ${gi_old} / 新行 ${gi_new}，期望 4/0/1）"; }
rm -rf "$T5B"

# 幂等断言：同输入两次运行结论一致且均 deny（双 plugin 共存的可测背书；1.0.9 输出契约
# 现代化 block→permissionDecision deny，grep 口径随迁）
BADCMD="git push --fo""rce origin main"   # 分段拼接，避免源码含完整字面串
j1=$(printf '{"tool_input":{"command":"%s"}}' "$BADCMD")
r1=$(printf '%s' "$j1" | python3 "$SRC/hooks/deny-list.py" | grep -c '"deny"' || true)
r2=$(printf '%s' "$j1" | python3 "$SRC/hooks/deny-list.py" | grep -c '"deny"' || true)
if [ "$r1" = "$r2" ] && [ "$r1" -ge 1 ]; then PASS=$((PASS+1)); echo "PASS  deny-list 重复调用幂等（两次均 deny）"; else FAIL=$((FAIL+1)); echo "FAIL  幂等断言（r1=${r1} r2=${r2}）"; fi

rm -rf "$D"
echo "== 脚本自测：PASS=$PASS FAIL=$FAIL =="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
