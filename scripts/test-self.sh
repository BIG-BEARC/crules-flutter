#!/usr/bin/env bash
# crules-flutter 脚本自测（批 2c）——应报错断言 + 幂等断言
# 注：幂等断言的测试命令经变量拼接构造（避免脚本源码含破坏命令完整字面串——deny-list 对
#     Bash 内字面串 deny-by-default，本文件须用 Write 工具落盘或分段拼接写入）
# 注2（bash 5.3 坑，2026-09-05）：set -u 下 $var 紧邻多字节字符（中文标点，如 $lst））会把多字节
#     首字节吸入变量名致 unbound 中止（brew bash 5.3.15 实测；LC_ALL=C 与 ${var} 花括号均免疫）——
#     本包三脚本此类位置一律花括号隔离（v59 BSD grep 环境坑同款教训）
# 1.0.42 断言：parity-rewrite 双扫描+尺寸 两闸入常驻断言区
set -uo pipefail
SRC=$(cd "$(dirname "$0")/.." && pwd)
# 环境守卫（1.0.13）：本脚本两条断言（draft / tag）依赖 git 历史，其余不依赖（1.0.38 50 → 1.0.39 51、1.0.41 +3 至 54、
# 1.0.42 +2 至 56——撞名/缺口/债龄三闸 + parity 两闸，其中缺口闸调 git tag 但不可读时自 SKIP；计数以实跑为准。
# 1.1.7 +1 至 59（合一断言；1.1.5/1.1.6 两批增量未逐批记账——外审 R8 勘误，防归因失真）
# 1.0.39/40 曾误记「52/0」、1.0.39 起点曾误记 48——09-24 三 tag 隔离实跑勘误：51/51/54，且本机无 pwsh 时 ps1 夹具
# SKIP 不计（有 pwsh 环境 +1），跨环境对数先对齐 SKIP 面）。在无 .git 的拷贝里
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
# 1.1.5 install 退役闸：任何形态 exit 1 + 指引 init + 零写入（老项目夹具顺带守 R0——树内仅原 CLAUDE.md）
t 1 "bash $SRC/scripts/install.sh $D/old --app"           "install 退役拒绝（任意形态，1.1.5）"
o=$(bash $SRC/scripts/install.sh $D/old --app 2>&1); irc=$?
[ "$irc" = "1" ] && echo "$o" | grep -q '/crules-flutter:init' \
  && [ "$(find "$D/old" -type f | wc -l | tr -d ' ')" = "1" ] \
  && { PASS=$((PASS+1)); echo "PASS  install 退役拒绝指向 init 且零写入（树内仅原 CLAUDE.md）"; } \
  || { FAIL=$((FAIL+1)); echo "FAIL  install 退役面（rc=$irc）"; }
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
t 0 "python3 $SRC/hooks/test_queue_contract.py"           "跨 hook 队列契约测试应全绿（1.0.39 D-4 写读互调）"
t 0 "python3 $SRC/hooks/test_compliance.py"               "compliance-audit fixture 应全绿（1.0.37 批2 遵守度事实账）"
# 1.0.42 断言①：parity-rewrite 零项目值+引用悬空双扫描——
# 扫 skills/parity-rewrite/ 全树：①禁列 token（05 计划 Global Constraints 全表 + 裸 ARB）
# 命中即红；②引用悬空式（spec 节号 `5.<数字>` / 裸 §<中文序号> / 「草案」）命中即红。
# token 与正则片段一律字符串拼接构造（:3–4 deny-list 同训：断言脚本不存全形字面，
# 扫描面日后扩围亦不自咬；「草稿」词面天然不咬，咬的是「草案」）。
pr_bad=$(python3 - "$SRC" <<'PYEOF'
import os, re, sys
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
root = sys.argv[1]
BAN = ['1.2' + '65', 'saas-' + 'cashier', 'saas-' + 'suite', 'saas_pos' + '_smart_edition',
       '.' + 'arb', 'zh_' + 'HK', 'AppTextStyle' + 's', 'AppColo' + 'rs', 'AppSpac' + 'ing',
       'smart-' + 'pos-', 'fvm' + ' ', 'crules-' + 'flutter',
       '03-' + 'code/', '01-' + 'specs/', 'Get.' + 'dialog', 'getGiveStr', 'ARB']
DR = re.compile('5' + chr(92) + '.[0-9]+' + '|' + '§' + '[一二三四五六七八九十]+' + '|' + '草' + '案')
base = os.path.join(root, 'skills', 'parity-rewrite')
bad = []
if not os.path.isdir(base):
    bad.append('skills/parity-rewrite/ 目录缺失（Task 1–3 交付被删？）')
for dp, dn, fn in os.walk(base):
    for f in sorted(fn):
        if not f.endswith('.md'): continue  # 只扫分发 md；二进制件（如 Finder .DS_Store）不属执法面，防解码假红/文件名残迹咬 token（1.0.42 批外置待验#2 收口）
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, root).replace(os.sep, '/')
        try: text = open(p, encoding='utf-8').read()
        except (OSError, UnicodeDecodeError) as e:
            bad.append(rel + ' 读取失败: ' + str(e)); continue
        for i, line in enumerate(text.splitlines(), 1):
            for tok in BAN:
                if tok in line:
                    bad.append(rel + ':' + str(i) + ' 禁列「' + tok + '」 ' + line.strip()[:60])
            m = DR.search(line)
            if m:
                bad.append(rel + ':' + str(i) + ' 引用悬空「' + m.group() + '」 ' + line.strip()[:60])
print(len(bad)); [print('  ↳ ' + b) for b in bad]
PYEOF
)
n_pr=$(printf '%s' "$pr_bad" | head -1)
if [ "${n_pr:-1}" = "0" ]; then
  PASS=$((PASS+1)); echo "PASS  parity-rewrite 零项目值+引用悬空双扫描"
else
  FAIL=$((FAIL+1)); echo "FAIL  parity-rewrite 双扫描命中 ×${n_pr:-?}（禁列项目值或 spec 节引用，就地改写/换指针）："; printf '%s\n' "$pr_bad" | tail -n +2
fi

# 1.0.42 断言②：parity-rewrite 尺寸闸——SKILL.md ≤10000 字符、
# references/ 与 templates/ 单文件 ≤12000 字符（先例 flutter-rules SKILL.md 实测 8054；
# 上限系 05 计划自设工程约束）。口径 = 字符数（python len，UTF-8 解码后），勿用 wc -m（:91 同训）。
sz_bad=$(python3 - "$SRC" <<'PYEOF'
import os, sys
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
root = sys.argv[1]
base = os.path.join(root, 'skills', 'parity-rewrite')
LIMIT_SKILL, LIMIT_SUB = 10000, 12000
bad = []
for relp, cap in [('SKILL.md', LIMIT_SKILL)]:
    p = os.path.join(base, relp)
    if not os.path.isfile(p): bad.append('缺 ' + relp); continue
    n = len(open(p, encoding='utf-8').read())
    if n > cap: bad.append(relp + ' ' + str(n) + ' 字符 > ' + str(cap))
for d, cap in [('references', LIMIT_SUB), ('templates', LIMIT_SUB)]:
    dd = os.path.join(base, d)
    if not os.path.isdir(dd): bad.append('缺 ' + d + '/ 目录'); continue
    for f in sorted(os.listdir(dd)):
        if not f.endswith('.md'): continue
        n = len(open(os.path.join(dd, f), encoding='utf-8').read())
        if n > cap: bad.append(d + '/' + f + ' ' + str(n) + ' 字符 > ' + str(cap))
print(len(bad)); [print('  ↳ ' + b) for b in bad]
PYEOF
)
n_sz=$(printf '%s' "$sz_bad" | head -1)
if [ "${n_sz:-1}" = "0" ]; then
  PASS=$((PASS+1)); echo "PASS  parity-rewrite 尺寸闸（SKILL.md ≤10000，references/ 与 templates/ 单文件 ≤12000 字符）"
else
  FAIL=$((FAIL+1)); echo "FAIL  parity-rewrite 尺寸超限 ×${n_sz:-?}（超限须拆分下沉，不静默上调预算）："; printf '%s\n' "$sz_bad" | tail -n +2
fi

t 1 "bash $SRC/scripts/release.sh tag 9.9.9"               "release tag 版本不匹配应报错（1.0.2 D2——防 tag 打在 bump 前旧树）"
# 非 git 树守卫的反向断言（1.0.13）：把脚本本身拷进非 git 目录跑，须**显式拒绝**。判据三条件缺一不可——
# rc≠0 单独不成立：守卫缺失时该拷贝会跑完全套，并因既有 FAIL>0 同样退出非零（又一个假绿）；故另须确认
# 提示语命中、且输出无 PASS 行（守卫在断言之前就中止，一条都没跑）。
GN="$D/nogit"; rm -rf "$GN"; mkdir -p "$GN/scripts"; cp "$SRC/scripts/test-self.sh" "$GN/scripts/"
go=$(bash "$GN/scripts/test-self.sh" 2>&1); grc=$?
[ "$grc" != "0" ] && echo "$go" | grep -q "须在 git 树内" && ! echo "$go" | grep -q '^PASS' \
  && { PASS=$((PASS+1)); echo "PASS  非 git 树守卫显式拒绝（1.0.13）"; } \
  || { FAIL=$((FAIL+1)); echo "FAIL  非 git 树守卫（rc=$grc——未拒绝 / 未在断言前中止）"; }
# 1.1.5：install.sh 分发职责退役——D3 升级确认 / F2 AO 三态 / 1.0.43 三向合并四态断言面随之删除
#   （机制史见 CHANGELOG 1.0.6–1.0.43；现行升级=重跑 init 刷指针与副本，AO=memory 建议稿人择，
#    巡检=check-imports.sh；方案 docs/方案-2026-10-15-宪法载体丁-Copy.md C5/C6）

# 0.4.0 批1断言（1.1.5 改口径）：memory 种子 9 模板（含 PROJECT.md 锚点）——init 步骤③配方直拷
#   （install 退役，夹具按 commands/init.md 配方执行——缺则补、永不覆盖，不再经 install.sh）
T4=$(mktemp -d /tmp/cf-pitfalls.XXXXXX)
mkdir -p "$T4/.claude/memory"
for f in "$SRC"/memory/*.md; do [ -e "$T4/.claude/memory/$(basename "$f")" ] || cp "$f" "$T4/.claude/memory/$(basename "$f")"; done
nm=$(ls "$T4/.claude/memory"/*.md 2>/dev/null | wc -l | tr -d ' ')
[ "$nm" = "9" ] && { PASS=$((PASS+1)); echo "PASS  memory 种子 9 模板（init 配方直拷，缺则补语义）"; } || { FAIL=$((FAIL+1)); echo "FAIL  memory 种子应 9 模板（实为 ${nm}）"; }
rm -rf "$T4"
grep -q '支持矩阵' "$SRC/commands/init.md" && ! grep -q 'install\.sh' "$SRC/commands/init.md" \
  && { PASS=$((PASS+1)); echo "PASS  init 引导含矩阵且零 install 依赖（正门唯一）"; } || { FAIL=$((FAIL+1)); echo "FAIL  init 引导（矩阵缺失或 install 残留）"; }
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

# 1.0.12 批D P1：孪生同文块生成闸——canonical 单一源与六文件同步。**在 /tmp 副本渲染后比对**
# （不原地改写被跟踪文件——方案 §4 R16）；render 内含双守卫（登记一致性 + 内容同步）。
# P3 已行（1.0.15）：旧 byte 互锁 2 条删（试点两 minor〔1.0.13/1.0.14〕闸均绿）——覆盖差如实记：
# 围栏外节内文本不再逐字比对，围栏内由本闸 + 锚串守卫全权。
T6=$(mktemp -d)
mkdir -p "$T6/scripts" "$T6/canonical" "$T6/app" "$T6/plugin" "$T6/commands" "$T6/agents"
cp "$SRC/scripts/render-blocks.py" "$T6/scripts/"
cp "$SRC"/canonical/*.md "$T6/canonical/"
cp "$SRC/app/CLAUDE.md" "$T6/app/"; cp "$SRC/plugin/CLAUDE.md" "$T6/plugin/"
cp "$SRC/commands/help.md" "$T6/commands/"; cp "$SRC/README.md" "$T6/"
# checklist.md＋进阶/ 随 review-core 块（2026-10-19 评审批）入扫描面——副本与仓内扫描面同构，零维护
cp "$SRC/checklist.md" "$T6/"
cp -R "$SRC/进阶" "$T6/进阶"
# agents/ 七卡随 aggregate-exception（1.0.35）＋agent-memory-nav（2026-10-19 评审批）入扫描面
# （scan_targets 含 agents/——不拷则守卫①c 报缺围栏；全量拷与仓内扫描面同构，新增卡零维护）
cp "$SRC"/agents/*.md "$T6/agents/"
rout=$(python3 "$T6/scripts/render-blocks.py" 2>&1); rrc=$?
same=1
for p in app/CLAUDE.md plugin/CLAUDE.md commands/help.md README.md agents/*.md checklist.md "进阶/审查与复核纪律.md"; do cmp -s "$T6/$p" "$SRC/$p" || same=0; done
# 锚串守卫（review R2）：canonical 清空/截断时 render 双侧对称 → 比对仍绿；锚串**直查仓内**
# 目标文件（不经比对），堵「整段静默消失」——P3 删旧 byte 断言后这是各块的关键防线之一
# 1.0.40（verify 族普查）：锚串改在**围栏区间内**查找——全文件 grep 的残余暴露=同文件叙事句
# 含锚串字样即假绿（块被删仍在别处提到该短语）；围栏内查找把「提到」与「在位」区分开。
anchor_bad=0
in_fence() { python3 -c "
import re,sys
p,i,a=sys.argv[1],sys.argv[2],sys.argv[3]
t=open(p,encoding='utf-8').read()
m=re.search(r'<!--\s*gen:%s\s*-->\n(.*?)\n<!--\s*/gen:%s\s*-->'%(i,i),t,re.S)
sys.exit(0 if m and a in m.group(1) else 1)" "$SRC/$1" "$2" "$3"; }
for a in "app/CLAUDE.md|gear-preset|轻量〔light〕" "plugin/CLAUDE.md|gear-preset|轻量〔light〕" \
         "app/CLAUDE.md|closing-tiers|收尾时序**三档**" "plugin/CLAUDE.md|closing-tiers|收尾时序**三档**" \
         "app/CLAUDE.md|gate-exception|.gate-exceptions" "plugin/CLAUDE.md|gate-exception|.gate-exceptions" \
         "commands/help.md|gear-note|收尾档按任务规模三档判定" "README.md|gear-note|收尾档按任务规模三档判定" \
         "agents/backend.md|aggregate-exception|判定线 = 是否引入第二个" "agents/frontend.md|aggregate-exception|判定线 = 是否引入第二个" \
         "app/CLAUDE.md|redline-evidence|必须引用皆有实测依据" "plugin/CLAUDE.md|redline-evidence|必须引用皆有实测依据" \
         "app/CLAUDE.md|redline-review-check|方案评审必核两件事" "plugin/CLAUDE.md|redline-review-check|方案评审必核两件事" \
         "agents/backend.md|agent-memory-nav|记忆库联动：开工先 Read" "agents/reviewer.md|agent-memory-nav|记忆库联动：开工先 Read" \
         "checklist.md|review-core|资损红线" "进阶/审查与复核纪律.md|review-core|资损红线"; do
  af="${a%%|*}"; rest="${a#*|}"; bid="${rest%%|*}"; as="${rest#*|}"
  in_fence "$af" "$bid" "$as" || { anchor_bad=1; echo "  ↳ $af 围栏 $bid 内缺锚串「$as」——canonical 疑似清空/截断"; }
done
if [ "$rrc" = "0" ] && [ "$same" = "1" ] && [ "$anchor_bad" = "0" ]; then
  PASS=$((PASS+1)); echo "PASS  孪生同文块生成闸（canonical↔六文件同步 + 锚串在位）"
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
# ② help.md hooks ×N == hooks/*.py 实际数（_common.py 系 import 库非 hook，排除——1.0.39 收编批）
hook_n=$(ls "${SRC}"/hooks/*.py 2>/dev/null | grep -vE 'test_|_common' | grep -c . || true)
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

# 1.0.7 断言①：Gate 例外台账同源闸——.gate-exceptions 定义三点同源（双模板 Gate 例外节 ↔ MAINTENANCE）
# （外审 🟡2 处置：台账被引用、零定义——定义落位 + 上闸，防「意图先于机制」复发；
#  1.1.5 起第四点 install.sh 随分发退役删除）
ge_ok=1
for f in app/CLAUDE.md plugin/CLAUDE.md memory/MAINTENANCE.md; do
  grep -qF -- ".gate-exceptions" "${SRC}/${f}" || { ge_ok=0; echo "  ↳ ${f} 缺「.gate-exceptions」"; }
done
[ "${ge_ok}" = "1" ] && { PASS=$((PASS+1)); echo "PASS  Gate 例外台账同源闸（双模板 Gate 例外节↔MAINTENANCE）"; } || { FAIL=$((FAIL+1)); echo "FAIL  Gate 例外台账同源闸（见上漂移清单）"; }

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
    # .superpowers/ = 本机过程面（git 忽略、非分发面，1.0.42 主控裁决豁免——撞的是
    # 协调文档里的相对链接示例与正则字面，非仓内容器死链）
    dirnames[:] = [d for d in dirnames if d not in ('.git', '__pycache__', '.claude', 'node_modules', '.superpowers')]
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

# ④ checklist 指针限定闸：skills 与进阶内提及 checklist 须带「插件 cache」——两目录与
#    checklist.md 同在 plugin cache 版本树（1.1.5 去分发化，checklist 不再装进消费工程根），裸写不可解析
ck_bad=$(grep -rn --include='*.md' '`checklist\.md`' "$SRC/skills" "$SRC/进阶" 2>/dev/null | grep -v '插件 cache' || true)
if [ -z "$ck_bad" ]; then
  PASS=$((PASS+1)); echo "PASS  checklist 指针限定（skills·进阶 提及均带「插件 cache」）"
else
  FAIL=$((FAIL+1)); echo "FAIL  skills·进阶 内裸写 checklist（须「插件 cache \`checklist.md\`）："; printf '%s\n' "$ck_bad"
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
# 1.0.37：compliance-audit.py 入列（同款守卫，第四位）——「三 hook 同款同改」自此为四。
# 1.0.39（裁决 D-3）：文件清单由手列四行改**从 hooks.json 派生**——注册面即分发面，新 hook 登记自动
#   入检；手挑清单同族病（1.0.37 加第四位时人肉同步 5+ 处、release/CI 清单历史漏过）自此免修。
av_bad=$(python3 - "$SRC" <<'PYEOF'
import json, os, re, sys
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
root = sys.argv[1]
h = json.load(open(os.path.join(root, 'hooks', 'hooks.json'), encoding='utf-8'))['hooks']
scripts = sorted({m.group(1) for ev in h.values() for b in ev for x in b.get('hooks', [])
                  for m in [re.search(r'/hooks/([A-Za-z0-9_.-]+\.py)', x.get('command', ''))] if m})
errs = []
if not scripts:
    errs.append('hooks.json 未解析出任何 .py 注册脚本（派生清单失明——空集=全体脱管）')
for name in scripts:
    text = open(os.path.join(root, 'hooks', name), encoding='utf-8').read()
    for s in ('sys.platform == "win32"', 'SetErrorMode(0x0002)'):
        if s not in text: errs.append(name + ' 缺「' + s + '」')
print(len(errs)); [print('  ↳ ' + e) for e in errs]
PYEOF
)
n_av=$(printf '%s' "$av_bad" | head -1)
if [ "${n_av:-1}" = "0" ]; then
  PASS=$((PASS+1)); echo "PASS  注册 hook AV 弹框压制守卫在位（win32 判定 + SetErrorMode，清单自 hooks.json 派生 ×4）"
else
  FAIL=$((FAIL+1)); echo "FAIL  AV 弹框压制守卫漂移 ×${n_av:-?}（见上）"
fi

# 1.0.39 断言（裁决 D-1+D-2）：hooks 共享收编双锁——①收编名单禁回抄：_common 定义的
#   find_project_root/MAX_SID/sanitize_sid/_hook_utf8_streams 在任何生产 hook 顶层重现即红
#   （防第 5 个 hook「不知道有 _common」又抄一份——单文件抄一份时跨文件重名规则不触发）；
#   ②跨 hook 同名绊线：任意两生产 hook 顶层同名函数/同名常量字面即红（防**新**复制对，
#   glob 全量、新文件自动入网——手挑名单已被本会话两次数错证伪）。
#   不锁调用式顶层赋值（root/mem/sid 各 hook 语义有别，compliance 的 root 系带参调用，合法分叉）。
tw_bad=$(python3 - "$SRC" <<'PYEOF'
import ast, os, sys
from collections import defaultdict
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
root = sys.argv[1]
hdir = os.path.join(root, 'hooks')
def top_names(path):
    out = []
    for node in ast.parse(open(path, 'rb').read().decode('utf-8')).body:
        if isinstance(node, ast.FunctionDef):
            out.append(node.name)
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            out += [t.id for t in node.targets if isinstance(t, ast.Name)]
    return out
common = set(top_names(os.path.join(hdir, '_common.py')))
if not common:
    print(1); print('  ↳ _common.py 未解析出符号（双锁失明面）'); sys.exit(0)
prod = [f for f in sorted(os.listdir(hdir)) if f.endswith('.py')
        and not f.startswith('test_') and f != '_common.py']
errs = []
byname = defaultdict(list)
for f in prod:
    for n in top_names(os.path.join(hdir, f)):
        byname[n].append(f)
        if n in common: errs.append(f + ' 顶层重抄 _common 符号: ' + n)
for n, loc in sorted(byname.items()):
    if len(loc) > 1: errs.append('跨 hook 重名顶层符号: ' + n + ' @ ' + ','.join(loc))
print(len(errs)); [print('  ↳ ' + e) for e in errs]
PYEOF
)
n_tw=$(printf '%s' "$tw_bad" | head -1)
if [ "${n_tw:-1}" = "0" ]; then
  PASS=$((PASS+1)); echo "PASS  hooks 共享收编双锁（_common 禁回抄 + 跨 hook 同名绊线，1.0.39 D-2）"
else
  FAIL=$((FAIL+1)); echo "FAIL  hooks 复制病复发 ×${n_tw:-?}（见上——改用 from _common import …）"
fi

# 1.0.35 断言①：hooks.json 结构看守——注册面是 deny 闸的开关命门，此前全仓零断言（外部评审核实）。
# matcher 集漂移 / 引用脚本改名 / async 位翻转（deny 判定转 async = 判定赶不上执行，闸失效；
# pending-updates 转同步 = 每次编辑多一个前台等待）/ 路径缺 CLAUDE_PLUGIN_ROOT 前缀或 hooks/ 目录段
# （消费工程 cwd 下必解析失败）/ 兜底链 || 被删——五类翻转任一即红。
hjs=$(python3 - "$SRC" <<'PYEOF'
import json, os, sys
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
h = json.load(open(os.path.join(sys.argv[1], 'hooks', 'hooks.json'), encoding='utf-8'))['hooks']
errs = []
def handlers(event, matcher):
    # matcher=None = 无 matcher 键的块（Stop 全事件触发）
    if matcher is None:
        return [x for b in h.get(event, []) if 'matcher' not in b for x in b['hooks']]
    return [x for b in h.get(event, []) if b.get('matcher') == matcher for x in b['hooks']]
mt = {e: sorted(str(b.get('matcher')) for b in h.get(e, [])) for e in h}
if mt.get('PreToolUse') != ['Bash', 'PowerShell']: errs.append('PreToolUse matcher 集漂移: ' + str(mt.get('PreToolUse')))
if 'Edit|Write|NotebookEdit' not in mt.get('PostToolUse', []): errs.append('PostToolUse 缺 Edit|Write|NotebookEdit')
if 'None' not in mt.get('Stop', []): errs.append('Stop 缺无 matcher 全触发块')
for ev, m, script, want_async in (('PreToolUse', 'Bash', 'deny-list.py', False),
                                  ('PreToolUse', 'PowerShell', 'deny-list.ps1', False),
                                  ('PostToolUse', 'Edit|Write|NotebookEdit', 'pending-updates.py', True),
                                  ('Stop', None, 'stop-reminder.py', False),
                                  ('SessionEnd', None, 'compliance-audit.py', False)):
    hs = handlers(ev, m)
    if len(hs) != 1: errs.append(f'{ev}/{m} handler 数 {len(hs)} != 1'); continue
    c = hs[0].get('command', '')
    if ('${CLAUDE_PLUGIN_ROOT}/hooks/' + script) not in c:
        errs.append(f'{ev}/{m} 未引用 $' + '{CLAUDE_PLUGIN_ROOT}/hooks/' + script + '（含目录段整体路径）: ' + c[:80])
    if '||' not in c: errs.append(f'{ev}/{m} 兜底链 || 缺失')
    if bool(hs[0].get('async', False)) != want_async:
        errs.append(f'{ev}/{m} async 位翻转（应为 {str(want_async).lower()}）')
# 1.0.37：SessionEnd 预算契约——官方口径该事件默认共享 1.5s，per-hook timeout 须显式上调
# （内部 BUDGET_S=10 的截断闸假设 timeout≥15；低于它 = 大转录在写完账前就被宿主 kill）
for b in h.get('SessionEnd', []):
    for x in b.get('hooks', []):
        if not isinstance(x.get('timeout'), (int, float)) or x['timeout'] < 15:
            errs.append('SessionEnd hook timeout 缺失或 <15（1.5s 默认预算下 10s 扫描闸形同虚设）')
print(len(errs)); [print('  ' + e) for e in errs]
PYEOF
)
n_hjs=$(printf '%s' "$hjs" | head -1)
if [ "${n_hjs:-1}" = "0" ]; then
  PASS=$((PASS+1)); echo "PASS  hooks.json 结构看守（matcher 集 / 引用整体路径 / async 位 / 兜底链）"
else
  FAIL=$((FAIL+1)); echo "FAIL  hooks.json 结构漂移 ×${n_hjs:-?}："; printf '%s\n' "$hjs" | tail -n +2
fi

# 1.0.35 断言②：deny-list 双源对照表符号闸——锚点从行号改符号名（行号历史漂过两次：1.0.21 偏
# ~37 行 / 1.0.33 偏 11 行），符号名须真在 deny-list.py 中；表头「锚点口径（1.0.35 起）」守卫
# 防回写行号形（出现「# py L<数字>」即红）；py 侧 import 的 re 另核。
tab=$(python3 - "$SRC" <<'PYEOF'
import os, re, sys
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
src = sys.argv[1]
ps = open(os.path.join(src, 'hooks', 'deny-list.ps1'), encoding='utf-8').read()
py = open(os.path.join(src, 'hooks', 'deny-list.py'), encoding='utf-8').read()
errs = []
if '锚点口径（1.0.35 起）' not in ps: errs.append('对照表锚点口径注缺失（防回写行号形的守卫被删）')
if re.search(r'#\s*py\s+L\d', ps): errs.append('对照表出现行号形锚点「# py L<数字>」')
pat = re.compile(r'#\s*py\s+(.+?)\s+↔')
seen = set()
for line in ps.splitlines():
    m = pat.search(line)
    if not m:
        continue
    for tok in re.split(r'[/、,，]|  +', m.group(1)):
        tok = tok.strip()
        if not tok or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', tok):
            continue
        seen.add(tok)
        if tok not in py:
            errs.append('对照表符号在 py 中不存在: ' + tok)
missing = {'GIT_SIG', 'RM_SIG', 'TMP_ROOTS', 'WARN_SIGS', 'parse_flags', 'strip_quotes',
           'checkout_discards', 'force_switch', 'gate_self_failure', '_gate_excepthook', '_hook_utf8_streams'} - seen
if missing: errs.append('对照表缺符号行（符号闸失明面）: ' + ', '.join(sorted(missing)))
print(len(errs)); [print('  ' + e) for e in errs]
PYEOF
)
n_tab=$(printf '%s' "$tab" | head -1)
if [ "${n_tab:-1}" = "0" ]; then
  PASS=$((PASS+1)); echo "PASS  deny-list 对照表符号闸（符号名在 py 可解析 + 无行号回写 + 表头注在位）"
else
  FAIL=$((FAIL+1)); echo "FAIL  对照表符号漂移 ×${n_tab:-?}："; printf '%s\n' "$tab" | tail -n +2
fi

# 易用性/信息架构批断言（外部易用性评审核实 + 死指针普查实证同族二实例）：
# ① 消费面黑话禁令闸（宪法 §一 机械执法点）② 文件锚定散文指针闸（1.0.32 链接闸的散文态补全）
jargon_bad=$(python3 - "$SRC" <<'PYEOF'
import os, re, sys
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
root = sys.argv[1]
skip_dirs = {'.git', '__pycache__', '.claude', 'node_modules', '.superpowers'}   # 1.0.42 主控裁决豁免：过程面协调文档含正则字面
BAN = re.compile(r'批[A-F][0-9]?|[（(]\s*[A-F]\d{1,2}\s*[)）]|销案|金丝雀|撞号|外审\s*[#🟠🔴🟡]\d?|评审\s*[A-Z]\d|裁决单')
bad = []
for dp, dn, fn in os.walk(root):
    dn[:] = [d for d in dn if d not in skip_dirs]
    rel_dp = os.path.relpath(dp, root).replace(os.sep, '/')
    if rel_dp == 'docs' or rel_dp.startswith('docs/') or rel_dp == 'canonical': continue
    for f in fn:
        if not f.endswith('.md') or f == 'CHANGELOG.md': continue
        p = os.path.join(dp, f).replace(os.sep, '/')
        rel = os.path.relpath(p, root).replace(os.sep, '/')
        text = open(p, encoding='utf-8').read()
        if rel == 'README.md':
            cut = text.find('## 维护（以下面向本仓维护者）')
            if cut > 0: text = text[:cut]
        for i, line in enumerate(text.splitlines(), 1):
            if '<!--' in line: continue
            m = BAN.search(line)
            if m: bad.append(rel + ':' + str(i) + ' [' + m.group() + '] ' + line.strip()[:60])
print(len(bad)); [print('  ' + b) for b in bad]
PYEOF
)
n_jar=$(printf '%s' "$jargon_bad" | head -1)
if [ "${n_jar:-1}" = "0" ]; then
  PASS=$((PASS+1)); echo "PASS  消费面黑话禁令闸（分发 md 零内部代号，HTML 注释/维护者面豁免）"
else
  FAIL=$((FAIL+1)); echo "FAIL  消费面黑话命中 ×${n_jar:-?}（宪法 §一——内部代号移 CHANGELOG 或改大白话）："; printf '%s\n' "$jargon_bad" | tail -n +2
fi

ptr_bad=$(python3 - "$SRC" <<'PYEOF'
import os, re, sys
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
root = sys.argv[1]
skip_dirs = {'.git', '__pycache__', '.claude', 'node_modules'}
ANCHOR = {'README': ['README.md'], 'CHANGELOG': ['CHANGELOG.md'], 'MAINTENANCE': ['memory/MAINTENANCE.md'],
          'NAVIGATION': ['memory/NAVIGATION.md'], 'skill': ['skills/flutter-rules/SKILL.md'],
          'SKILL': ['skills/flutter-rules/SKILL.md'], '双模板': ['app/CLAUDE.md', 'plugin/CLAUDE.md'],
          '模板': ['app/CLAUDE.md', 'plugin/CLAUDE.md'], '上手教程': ['进阶/上手教程.md'],
          'Agent编排': ['进阶/Agent编排.md'], '记忆库体系': ['进阶/记忆库体系.md'],
          '工程化流程': ['进阶/工程化流程.md'], '审查与复核纪律': ['进阶/审查与复核纪律.md'],
          '方案评审闭环': ['进阶/方案评审闭环.md']}
pat = re.compile(r'(README|CHANGELOG|MAINTENANCE|NAVIGATION|双模板|skill|SKILL|上手教程|Agent编排|记忆库体系|工程化流程|审查与复核纪律|方案评审闭环|模板)[^\n「」]{0,8}[『「]([^』」]{2,25})[』」]\s*节')
def headings(fp):
    try: lines = open(fp, encoding='utf-8').read().splitlines()
    except OSError: return None
    return [re.sub(r'^#+\s*', '', l).strip(' `*') for l in lines if re.match(r'^#{1,6}\s', l)]
bad = []
for dp, dn, fn in os.walk(root):
    dn[:] = [d for d in dn if d not in skip_dirs]
    rel_dp = os.path.relpath(dp, root).replace(os.sep, '/')
    if rel_dp == 'docs' or rel_dp.startswith('docs/') or rel_dp == 'canonical': continue
    for f in fn:
        if not f.endswith('.md') or f == 'CHANGELOG.md': continue
        p = os.path.join(dp, f).replace(os.sep, '/')
        for i, line in enumerate(open(p, encoding='utf-8').read().splitlines(), 1):
            # 溯源豁免：「来源：X『Y』节（…拆出）」句指向拆分前的旧标题，改指即篡改历史
            if re.search(r'来源|出处|前身|拆出', line): continue
            for m in pat.finditer(line):
                hs = []
                miss = False
                for fp in [os.path.join(root, a.replace('/', os.sep)) for a in ANCHOR[m.group(1)]]:
                    h = headings(fp)
                    if h is None: miss = True; break
                    hs += h
                if miss:
                    bad.append(p + ':' + str(i) + ' 锚文件缺失 ' + m.group(1))
                elif not any(m.group(2) in h or h in m.group(2) for h in hs):
                    bad.append(os.path.relpath(p, root).replace(os.sep, '/') + ':' + str(i) + ' ' + m.group(1) + '「' + m.group(2) + '」节 → 目标标题不存在')
print(len(bad)); [print('  ' + b) for b in bad]
PYEOF
)
n_ptr=$(printf '%s' "$ptr_bad" | head -1)
if [ "${n_ptr:-1}" = "0" ]; then
  PASS=$((PASS+1)); echo "PASS  文件锚定散文指针闸（「X『Y』节」的 Y 须为 X 真实标题——实证死指针 help.md:7/:76 同族封闸）"
else
  FAIL=$((FAIL+1)); echo "FAIL  散文死指针 ×${n_ptr:-?}（补目标标题或改指针口径）："; printf '%s\n' "$ptr_bad" | tail -n +2
fi

# 1.0.41 轻量撞名消歧批断言 ×3：
# ① 撞名闸（E1/G1）——「轻量」在消费面（进阶/ + commands/ + README.md）只许落项目档位轴：
#   行级匹配白名单形「轻量〔light〕」「轻量档」（canonical/ 与 skills/ 不在扫面；1.0.38 曾占用
#   的裸「轻量 tier」「轻量起见」族措辞即红——后占用者已改「极简档」「简化起见」）。
# ② 版本缺口闸（E4/G3）——CHANGELOG 版本头 − git tag 差集须 ⊆ docs/清单-版本缺口与欠账.md 登记表
#   （先核后写：11 缺口已逐版分诊，需求方 09-23 裁「不回补」，登记表即终态）。非 git 树 SKIP 不计 FAIL。
# ③ 欠账龄闸（E2/G3）——⑤欠账表「起于」为版本形的行，债龄（当前 minor − 起于 minor）≤ N=10。
#   2026-09-23 需求方裁「上闸即咬」：/context 债起 1.0.10 债龄 30，本闸真树即红系设计意图，
#   封版（release tag 前跑全套 test-self）至行动甲 B 销账——展期须附需求方裁决引用。
# 1.1.0 版本滚动适配（2026-10-09 需求方裁：patch 位 0–19 封顶、满则进 minor）——②头/登记表正则去
#   1.0.x 硬编码；③计龄改线性 minor×20+patch（原 patch 直减在 minor 进位后归零成假绿，行过滤 minor≠0 同步撤）。
# 1.1.2 段序计龄（d 案，2026-10-10 轮次化批呈裁发现盲区）：线性 minor×20+patch 对 1.0.2x–1.0.51
#   遗留版起债为负龄恒绿（1.0.47→47 vs 现行 1.1.1→21）——非单调、纪元死数字基点（52）换纪元再适配。
#   改段序位次差：age = 起于版本自顶段序位次（最新段=0；CHANGELOG 段头文件序 = 发版序，缺口闸同哲学）。
#   两道 fail-closed：起于查无段头红（1.0.36 幽灵类跳号不许作起于）/ ≥1.0.0 段头严格降序破坏红
#   （前史 0.x 尾有 0.0.1/0.1.1 文件序异常〔已实测〕，降序断言豁免 0.x 段——债面永不触及）。
#   plugin.json 读取删除：顶段即当轮在飞版，release draft 段顶多致全表 +1，fail-safe 方向。
nm_bad=$(python3 - "$SRC" <<'PYEOF'
import os, re, sys
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
root = sys.argv[1]
WL = re.compile(r'轻量〔light〕|轻量档')
targets = ['README.md']
for d in ('进阶', 'commands'):
    targets += [d + '/' + f for f in sorted(os.listdir(os.path.join(root, d))) if f.endswith('.md')]
bad = []
ok = []
for rel in targets:
    for i, line in enumerate(open(os.path.join(root, rel.replace('/', os.sep)), encoding='utf-8').read().splitlines(), 1):
        if '轻量' in line:
            if WL.search(line): ok.append(rel + ':' + str(i))
            else: bad.append(rel + ':' + str(i) + ' ' + line.strip()[:50])
print(len(bad)); [print('  ↳ ' + b) for b in bad]; [print('  ✓ ' + o) for o in ok]
PYEOF
)
n_nm=$(printf '%s' "$nm_bad" | head -1)
if [ "${n_nm:-1}" = "0" ]; then
  PASS=$((PASS+1)); echo "PASS  轻量撞名闸（消费面「轻量」仅项目档位白名单形 ×$(printf '%s' "$nm_bad" | grep -c '^  ✓')，行级）白名单命中："
  printf '%s\n' "$nm_bad" | grep '^  ✓' || true
else
  FAIL=$((FAIL+1)); echo "FAIL  轻量裸用/轴混 ×${n_nm:-?}（改「极简档/简化起见」或补档位限定）："; printf '%s\n' "$nm_bad" | grep '^  ↳' || true
fi

gap_out=$(python3 - "$SRC" <<'PYEOF'
import os, re, subprocess, sys
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
root = sys.argv[1]
try:
    r = subprocess.run(['git', 'tag'], cwd=root, capture_output=True, text=True, timeout=10)
    if r.returncode != 0:
        print('SKIP'); sys.exit(0)
except Exception:
    print('SKIP'); sys.exit(0)
tags = {t.lstrip('v') for t in r.stdout.split() if re.match(r'^v?\d+\.\d+\.\d+$', t)}
heads = set(re.findall(r'^## (\d+\.\d+\.\d+)', open(os.path.join(root, 'CHANGELOG.md'), encoding='utf-8').read(), re.M))
# 1.1.0 滚动适配实跑勘误：全量正则被 0.6.x fork 前史段头咬红——0.x 无 tag 非缺口、不属 tag 纪律面，major≥1 过滤
heads = {v for v in heads if int(v.split('.')[0]) >= 1}
# 评审 P0-3：git 仓而 tag 集为空 = 检出环境缺 tag（浅克隆/未取 tag），闸瞎了——按红拒绝盲跑；
#   SKIP 仅限非 git 树（上方 rc≠0 分支）。实证：CI checkout 默认 fetch-depth=1 不取 tag，
#   零 tag 仓模拟 unreg=49 应红而本地 51 tag 全绿——同断言两环境结论相反即此盲区。
if not tags and heads:
    print('BAD')
    print('  ↳ 环境 tag 集为空而 CHANGELOG 有 1.x 段头——浅克隆/未取 tag（CI 需 fetch-depth: 0），闸拒绝盲跑')
    sys.exit(0)
# 当前版本豁免：release 链路 = bump（CHANGELOG 头先落）→ commit → tag 后打——
# tag 未打的当轮被扫即红是时序假缺口非登记缺口（1.0.41 首咬自证）；tag 必达闸兜其后
mver = re.search(r'"version":\s*"(\d+\.\d+\.\d+)"', open(os.path.join(root, '.claude-plugin', 'plugin.json'), encoding='utf-8').read())
if mver: heads.discard(mver.group(1))
reg_txt = open(os.path.join(root, 'docs', '清单-版本缺口与欠账.md'), encoding='utf-8').read()
sec1 = reg_txt.split('## 一、')[1].split('## 二、')[0] if '## 一、' in reg_txt else ''
reg = set(re.findall(r'^\| (\d+\.\d+\.\d+) \|', sec1, re.M))
missing = sorted(heads - tags, key=lambda s: [int(x) for x in s.split('.')])
unreg = [v for v in missing if v not in reg]
ghost = sorted(reg - set(missing), key=lambda s: [int(x) for x in s.split('.')])
if unreg or ghost:
    print('BAD')
    for v in unreg: print('  ↳ 版本缺口未登记: ' + v)
    for v in ghost: print('  ↳ 登记表幽灵行（已非缺口，删行）: ' + v)
else:
    print('OK ' + str(len(missing)))
PYEOF
)
if printf '%s' "$gap_out" | grep -q '^SKIP'; then
  echo "SKIP  版本缺口闸（git tag 不可读——非 git 树/超时，不计 FAIL，同 pwsh 先例）"
elif printf '%s' "$gap_out" | grep -q '^OK'; then
  PASS=$((PASS+1)); echo "PASS  版本缺口闸（差集 ⊆ 登记表双向对账，缺口 $(printf '%s' "$gap_out" | head -1 | cut -d' ' -f2) 个全在册）"
else
  FAIL=$((FAIL+1)); echo "FAIL  版本缺口登记漂移（新增缺口或登记表幽灵行）："; printf '%s\n' "$gap_out" | tail -n +2
fi

debt_out=$(python3 - "$SRC" <<'PYEOF'
import os, re, sys
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
root = sys.argv[1]
N = 10
txt = open(os.path.join(root, 'docs', '清单-版本缺口与欠账.md'), encoding='utf-8').read()
full = open(os.path.join(root, 'CHANGELOG.md'), encoding='utf-8').read()
heads = re.findall(r'^## (\d+)\.(\d+)\.(\d+)', full, re.M)
vers = ['%s.%s.%s' % h for h in heads]              # 文件序 = 新→旧（缺口闸同哲学）
pos = {v: i for i, v in enumerate(vers)}
# fail-closed ②：≥1.0.0 段头严格降序破坏 = 时序钟坏，整闸红（0.x 前史豁免——尾部有 0.0.1/0.1.1 实测异常，债面永不触及）
seq = [tuple(map(int, h)) for h in heads if int(h[0]) >= 1]
if not all(a > b for a, b in zip(seq, seq[1:])):
    print('BAD'); print('  ↳ CHANGELOG ≥1.0.0 段头文件序非严格降序——段序钟坏，先修段序再论债龄'); sys.exit(0)
sec2 = txt.split('## 二、')[1] if '## 二、' in txt else ''
sec2 = sec2.split('\n## ')[0]   # 只扫在册节——「三、已销账」读数留档行不得再数龄
errs = []
rows = 0
for line in sec2.splitlines():
    m = re.match(r'^\| [^|]+\| (\d+)\.(\d+)\.(\d+)[^|]*\|', line)
    if not m: continue   # 日期形/说明形「起于」行不数龄，人跟
    rows += 1
    key = '%s.%s.%s' % m.groups()
    if key not in pos:   # fail-closed ①：起于查无段头（1.0.36 幽灵类跳号不许作起于）
        errs.append('债行起于无段头: ' + line.split('|')[1].strip() + '（起于 ' + key + '）——段头缺失或幽灵版本，先核账')
        continue
    age = pos[key]
    if age > N: errs.append('债龄超限: ' + line.split('|')[1].strip() + '（起于 ' + key + '，段序龄 ' + str(age) + ' > N=' + str(N) + '）——还债或附需求方裁决引用展期')
if errs:
    print('BAD'); [print('  ↳ ' + e) for e in errs]
else:
    print('OK ' + str(rows))
PYEOF
)
if printf '%s' "$debt_out" | grep -q '^OK'; then
  PASS=$((PASS+1)); echo "PASS  欠账龄闸（版本形债行 ×$(printf '%s' "$debt_out" | head -1 | cut -d' ' -f2) 均 ≤N=10，段序计龄）"
else
  FAIL=$((FAIL+1)); echo "FAIL  欠账龄闸红（段序计龄：超限 / 起于无段头 / 段序钟坏；真树红系 09-23 裁决「咬」，展期=附裁决引用）："; printf '%s\n' "$debt_out" | tail -n +2
fi

# 1.0.34 批断言（1.1.5 大裁：install 退役后 ①未知参数 ③--yes ④降级 ⑤双跑 ⑥伴生哨兵随机制删除，
#   存续=⑧ 双 json / ⑨ 方向三态；版本读不到即停与戳链迁移至 check-imports 侧）——共 2 条
# ① 源版本读不到必须当场停（1.0.21 P0-A 同族——原 install 兜 vunknown 戳假绿；1.1.5 起读源方=check-imports）
GVB="$D/verbroke"; rm -rf "$GVB"; mkdir -p "$GVB/scripts" "$GVB/.claude-plugin" "$D/fresh"
cp "$SRC/scripts/check-imports.sh" "$GVB/scripts/"; printf 'not-json' > "$GVB/.claude-plugin/plugin.json"
o=$(bash "$GVB/scripts/check-imports.sh" "$D/fresh" 2>&1); vrc=$?
[ "$vrc" = "1" ] && echo "$o" | grep -q "读不到源版本" && ! echo "$o" | grep -q '未检出' \
  && { PASS=$((PASS+1)); echo "PASS  源版本读不到显式中止（check-imports 不兜假绿）"; } \
  || { FAIL=$((FAIL+1)); echo "FAIL  源版本读不到应中止（rc=$vrc）"; }
# ② check-imports 戳链：指针戳优先——双戳并存（指针 v0.0.1 + 根存量 v9.9.9）时报指针侧，
#   不把根存量误报成「丁-tracked 待迁移」（双戳并存=刚 init 刷过的正常态，非迁移债）
T9=$(mktemp -d /tmp/cf-ci.XXXXXX); mkdir -p "$T9/.claude"
printf '<!-- crules-flutter: v0.0.1 -->\n@crules/constitution.md\n' > "$T9/.claude/CLAUDE.md"
printf '<!-- crules-flutter: v9.9.9 @ 2026-01-01 -->\n' > "$T9/CLAUDE.md"
o9=$(bash "$SRC/scripts/check-imports.sh" "$T9" 2>&1); r9=$?
[ "$r9" = "0" ] && echo "$o9" | grep -q '指针（丁-Copy）' && ! echo "$o9" | grep -q '丁-tracked' \
  && { PASS=$((PASS+1)); echo "PASS  check-imports 戳链指针优先（双戳并存报指针侧，不误报迁移债）"; } \
  || { FAIL=$((FAIL+1)); echo "FAIL  check-imports 戳链（rc=$r9）"; }
rm -rf "$T9"
# ⑧ 双 json 版本相等（原只锁 README 横幅==plugin.json，marketplace 侧写后不验）+ release 闸防删改锚
#   （bump 读回断言 / bump·tag 跑 test-self / tag 树干净检查——tag 是消费者实际拿到的工件）
mk_ver=$(grep -m1 -oE '"version":[[:space:]]*"[0-9]+\.[0-9]+\.[0-9]+"' "${SRC}/.claude-plugin/marketplace.json" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
rl_ok=1
[ -n "${mk_ver}" ] && [ "${mk_ver}" = "${pj_ver}" ] || { rl_ok=0; echo "  ↳ marketplace.json(${mk_ver:-无}) ≠ plugin.json(${pj_ver})"; }
for s in '读回为' 'bash scripts/test-self.sh' 'git diff --quiet'; do
  grep -qF -- "$s" "${SRC}/scripts/release.sh" || { rl_ok=0; echo "  ↳ release.sh 缺闸锚「${s}」"; }
done
[ "${rl_ok}" = "1" ] && { PASS=$((PASS+1)); echo "PASS  双 json 相等 + release 闸锚在位（读回断言/test-self/树干净）"; } \
  || { FAIL=$((FAIL+1)); echo "FAIL  分发口径（见上）"; }
# ⑨ check-imports 方向三态：原只打「版本差」不分方向；SRC_VER 读不到原兜「?」伪装成「未检出戳」假绿
GCI="$D/cifake"; rm -rf "$GCI"; mkdir -p "$GCI/scripts" "$GCI/.claude-plugin" "$D/citgt"
cp "$SRC/scripts/check-imports.sh" "$GCI/scripts/"
printf '{\n  "version": "0.0.1"\n}\n' > "$GCI/.claude-plugin/plugin.json"
printf '<!-- crules-flutter: v9.9.9 @ 2026-01-01 -->\n' > "$D/citgt/CLAUDE.md"
# lag 改段序投影后需 CHANGELOG 可读且两版均在序（评审 M3 适配——守卫不削）：戳 9.9.9 段序 1、
# 源 0.0.1 段序 2 → ia−ib=−1 → 落「源更旧」分支，既有断言原样通过
printf '## 9.9.9 · a\n## 0.0.1 · b\n' > "$GCI/CHANGELOG.md"
oci=$(bash "$GCI/scripts/check-imports.sh" "$D/citgt" 2>&1); circ=$?
[ "$circ" = "0" ] && echo "$oci" | grep -q "源更旧" \
  && { PASS=$((PASS+1)); echo "PASS  check-imports 报降级方向（三态收口）"; } \
  || { FAIL=$((FAIL+1)); echo "FAIL  check-imports 方向（rc=$circ）"; }

# 1.1.5 断言：install.sh gitignore 幂等落位机制随分发职责退役（1.0.5/1.0.30/1.1.3 三段断言面删除）——
#   .claude/ 整目录 ignore 即全覆盖（MAINTENANCE「git 分层」自查），AI 不代写受控 .gitignore（R0）
if grep -q 'install\.sh' "$SRC/memory/MAINTENANCE.md"; then
  FAIL=$((FAIL+1)); echo "FAIL  MAINTENANCE 仍引用 install.sh（分发面残留指引）"
else
  PASS=$((PASS+1)); echo "PASS  MAINTENANCE 零 install.sh 残留（1.1.5 退役扫尾）"
fi

# 1.1.4 断言：消费工程双任务收尾吸收——总览双规 / 覆盖面枚举 / 矩阵证据四落位 + 黑话红线扩禁
#   （依据：2026-10-14 挂账对照失误复盘 + Wi-Fi 换装孤儿面复盘吸收；红线旧句只禁「造」不禁「用」，
#   扩禁后旧句双模板清零、新句双模板命中——防回退漂移）。
ov1=$(grep -c "任务总览表" "$SRC/进阶/工程化流程.md" 2>/dev/null) || ov1=0
ov2=$(grep -c "^## 进度" "$SRC/进阶/工程化流程.md" 2>/dev/null) || ov2=0
ov3=$(grep -c "未登记域禁落码" "$SRC/进阶/工程化流程.md" 2>/dev/null) || ov3=0
ov4=$(grep -c "规则全集矩阵" "$SRC/进阶/审查与复核纪律.md" 2>/dev/null) || ov4=0
[ "$ov1" -ge 1 ] && [ "$ov2" -ge 1 ] && [ "$ov3" -ge 1 ] && [ "$ov4" -ge 1 ] \
  && { PASS=$((PASS+1)); echo "PASS  1.1.4 吸收四落位（总览表/进度行/覆盖面枚举/矩阵证据）"; } \
  || { FAIL=$((FAIL+1)); echo "FAIL  1.1.4 四落位（总览表 ${ov1}/进度行 ${ov2}/枚举 ${ov3}/矩阵 ${ov4}，期望各 ≥1）"; }
jl_new=$(grep -l "不使用黑话与自造词" "$SRC/plugin/CLAUDE.md" "$SRC/app/CLAUDE.md" 2>/dev/null | wc -l | tr -d ' ')
jl_old=$(grep -l "不自创黑话新词" "$SRC/plugin/CLAUDE.md" "$SRC/app/CLAUDE.md" 2>/dev/null | wc -l | tr -d ' ')
[ "${jl_new:-0}" = "2" ] && [ "${jl_old:-0}" = "0" ] \
  && { PASS=$((PASS+1)); echo "PASS  黑话红线扩禁（新句双模板命中，旧句清零）"; } \
  || { FAIL=$((FAIL+1)); echo "FAIL  黑话红线（新句 ${jl_new:-?}/2，旧句残留 ${jl_old:-?}）"; }

# 幂等断言：同输入两次运行结论一致且均 deny（双 plugin 共存的可测背书；1.0.9 输出契约
# 现代化 block→permissionDecision deny，grep 口径随迁）
BADCMD="git push --fo""rce origin main"   # 分段拼接，避免源码含完整字面串
j1=$(printf '{"tool_input":{"command":"%s"}}' "$BADCMD")
r1=$(printf '%s' "$j1" | python3 "$SRC/hooks/deny-list.py" | grep -c '"deny"' || true)
r2=$(printf '%s' "$j1" | python3 "$SRC/hooks/deny-list.py" | grep -c '"deny"' || true)
if [ "$r1" = "$r2" ] && [ "$r1" -ge 1 ]; then PASS=$((PASS+1)); echo "PASS  deny-list 重复调用幂等（两次均 deny）"; else FAIL=$((FAIL+1)); echo "FAIL  幂等断言（r1=${r1} r2=${r2}）"; fi

# ── 1.1.5 丁-Copy 批（方案 docs/方案-2026-10-15-宪法载体丁-Copy.md 阶段 2 核心件）──────
#   载体=未跟踪指针 .claude/CLAUDE.md 四行 + .claude/crules/ 宪法副本（Q6 已裁 2026-10-15）。
#   断言面：双模板零 @ 内链（副本内相对导入会解析进 .claude/crules/ 空导入）/ 指针配方单源 /
#   宪法体积官方 4MiB cap / PROJECT.md 锚点种子 / agents×7 联动行 / T7 陈旧文案零 --upgrade /
#   戳读链 .claude/CLAUDE.md 优先→根回退（存量平滑）。
n_at=$(grep -c '^@' "$SRC/app/CLAUDE.md" 2>/dev/null); p_at=$(grep -c '^@' "$SRC/plugin/CLAUDE.md" 2>/dev/null)
[ "${n_at:-1}" = "0" ] && [ "${p_at:-1}" = "0" ] \
  && { PASS=$((PASS+1)); echo "PASS  丁-Copy 内链清理（双宪法模板零 @ 行）"; } \
  || { FAIL=$((FAIL+1)); echo "FAIL  内链清理（app ${n_at}/plugin ${p_at} @ 行，期望 0/0）"; }

ptr_files=$(grep -rl '@crules/constitution.md' "$SRC" --include='*.md' --exclude-dir=docs --exclude-dir=.git 2>/dev/null | tr '\n' ' ')
[ "$ptr_files" = "$SRC/commands/init.md " ] \
  && { PASS=$((PASS+1)); echo "PASS  指针四行配方单源（仅 commands/init.md）"; } \
  || { FAIL=$((FAIL+1)); echo "FAIL  配方单源（实际分布：${ptr_files:-无}）"; }

sz_a=$(wc -c < "$SRC/app/CLAUDE.md" | tr -d ' '); sz_p=$(wc -c < "$SRC/plugin/CLAUDE.md" | tr -d ' ')
[ "$sz_a" -lt 4194304 ] && [ "$sz_p" -lt 4194304 ] \
  && { PASS=$((PASS+1)); echo "PASS  宪法体积（app ${sz_a}B / plugin ${sz_p}B < 4MiB 官方 cap）"; } \
  || { FAIL=$((FAIL+1)); echo "FAIL  宪法体积（${sz_a}/${sz_p} ≥ 4MiB）"; }

if [ -f "$SRC/memory/PROJECT.md" ] && grep -q '§七 技术栈' "$SRC/memory/PROJECT.md"; then
  PASS=$((PASS+1)); echo "PASS  PROJECT.md 锚点模板种子在位（第 9 件 memory 种子）"
else
  FAIL=$((FAIL+1)); echo "FAIL  PROJECT.md 种子缺失"
fi

# 1.1.5 评审修正批（外审 R1）：双模板零「复制后手改」旧形态指令——丁-Copy 下副本 pristine、
# 选择落 PROJECT.md，模板文字不得再引导「复制到项目根/删未选项/在此填写」
legacy_bad=$(grep -n '【复制后\|复制到项目\|选定后删\|在此填写\|删掉未选' "$SRC/app/CLAUDE.md" "$SRC/plugin/CLAUDE.md" || true)
if [ -z "$legacy_bad" ]; then
  PASS=$((PASS+1)); echo "PASS  双模板零旧形态指令（复制后必填/删未选项族清零，1.1.5 评审 R1）"
else
  FAIL=$((FAIL+1)); echo "FAIL  双模板残留旧形态指令（丁-Copy 副本 pristine，选择落 PROJECT.md）："; printf '%s\n' "$legacy_bad"
fi

n_ag=$(grep -l '开工先 Read `.claude/memory/PROJECT.md`' "$SRC"/agents/*.md 2>/dev/null | wc -l | tr -d ' ')
[ "${n_ag:-0}" = "7" ] \
  && { PASS=$((PASS+1)); echo "PASS  agents×7 联动行补 PROJECT.md（C8）"; } \
  || { FAIL=$((FAIL+1)); echo "FAIL  agents 联动行（${n_ag:-0}/7）"; }

if grep -q -- '--upgrade' "$SRC/hooks/stop-reminder.py"; then
  FAIL=$((FAIL+1)); echo "FAIL  T7 陈旧文案仍含 --upgrade 引导"
else
  PASS=$((PASS+1)); echo "PASS  T7 陈旧文案零 install.sh --upgrade 引导（催 init 刷指针）"
fi

if grep -q 'constitution_sha256' "$SRC/commands/init.md" && grep -q 'constitution_sha256' "$SRC/hooks/stop-reminder.py"; then
  PASS=$((PASS+1)); echo "PASS  宪法哈希对拍双锚（init 写键＋stop-reminder 验键同在——2026-10-19 评审 P1-6）"
else
  FAIL=$((FAIL+1)); echo "FAIL  宪法哈希对拍双锚脱钩（init 写键或 stop-reminder 验键缺失——两端须同批动）"
fi

if grep -q 'command -v python3 || command -v python' "$SRC/commands/init.md" && grep -q 'state 哈希键缺失' "$SRC/commands/init.md" && grep -q '自检五条输出' "$SRC/commands/init.md"; then
  PASS=$((PASS+1)); echo "PASS  init 哈希写键解释器兜底＋落位自检行（只装 python 机器闸不静默失效——2026-10-19 终审修复）"
else
  FAIL=$((FAIL+1)); echo "FAIL  init 哈希写键兜底＋自检脱钩（解释器探测或自检呈报行或对账计数缺失——写键失败须可见）"
fi

# 1.2.2 止损执行批（2026-10-19 六行全裁）六闸——降格/同钟/不接线/瘦身/裁决闭合/外审降格
# ① 开关上限硬闸降格为例行自查（止损单 #5）：硬闸触发语清除＋例行自查语落位
zg_a=0
grep -q '触发「收敛成新档位」复核' "$SRC/README.md" && zg_a=1
grep -q '列轮次化清点例行自查项' "$SRC/README.md" || zg_a=1
[ "${zg_a}" = "0" ] && { PASS=$((PASS+1)); echo "PASS  开关上限降格闸（硬闸触发语已清、例行自查语在位——止损单 #5）"; } || { FAIL=$((FAIL+1)); echo "FAIL  开关上限降格闸（README 单项开关治理行仍含硬闸语或缺例行自查语）"; }

# ② 蜜月期同钟（止损单 #3）：用量门触发随四数线同钟裁
grep -q '沉淀闸蜜月期.*同钟' "$SRC/README.md" \
  && { PASS=$((PASS+1)); echo "PASS  蜜月期同钟闸（触发系用量门、随四数止损线同钟——止损单 #3）"; } \
  || { FAIL=$((FAIL+1)); echo "FAIL  蜜月期同钟闸（README 蜜月期行缺同钟注——用量门永不触发病形未挂钟）"; }

# ③ 聚合永不接线三面（止损单 #2）：README 概念地图＋MAINTENANCE＋欠账清单触发面
zg_c=0
grep -q '聚合永不接线' "$SRC/README.md" || zg_c=1
grep -q '聚合永不接线' "$SRC/memory/MAINTENANCE.md" || zg_c=1
grep -q '批3 聚合产出' "$SRC/docs/清单-版本缺口与欠账.md" && zg_c=1
[ "${zg_c}" = "0" ] && { PASS=$((PASS+1)); echo "PASS  聚合永不接线闸（三面同步——账降格原始事实账、「待接线」债销——止损单 #2）"; } || { FAIL=$((FAIL+1)); echo "FAIL  聚合永不接线闸（README/MAINTENANCE 缺裁定语或欠账清单触发面仍挂批3 聚合产出）"; }

# ④ gear-note 瘦身闸（止损单 #6）：canonical 源 12 锚串存活＋两剪除串不在（预设块不动由渲染闸守）
zg_d=0
for s in '轻量〔light〕' '标准〔normal〕' '完整〔full〕' '默认标准' '按任务规模三档' '单点修复' '跨域大改' '公开 API' '资损面' 'review 豁免' 'Gate 例外台账' '校验层'; do
  grep -qF -- "$s" "$SRC/canonical/gear-note.md" || { zg_d=1; echo "  ↳ canonical/gear-note.md 缺「$s」"; }
done
grep -qF '停维护；PROJECT.md 档位锚点留' "$SRC/canonical/gear-note.md" && { zg_d=1; echo "  ↳ 剪除串残留：停维护；PROJECT.md 档位锚点留（§十二预设块已逐字覆盖）"; }
grep -qF '极简收尾占比高' "$SRC/canonical/gear-note.md" && { zg_d=1; echo "  ↳ 剪除串残留：极简收尾占比高（预设块「极简占比高」已覆盖）"; }
[ "${zg_d}" = "0" ] && { PASS=$((PASS+1)); echo "PASS  档位条文瘦身闸（12 锚串存活＋剪除串清零——语义唯一源归预设块，止损单 #6）"; } || { FAIL=$((FAIL+1)); echo "FAIL  档位条文瘦身闸（见上漂移清单）"; }

# ⑤ 止损单裁决闭合闸（六行）：裁决列无空白＋行 4 降格合并裁决在册
zg_e=0
grep -qE '\|[[:space:]]*\|[[:space:]]*$' "$SRC/docs/清单-存量机制止损候选.md" && zg_e=1
grep -q '降为选项文本' "$SRC/docs/清单-存量机制止损候选.md" || zg_e=1
[ "${zg_e}" = "0" ] && { PASS=$((PASS+1)); echo "PASS  止损单裁决闭合闸（六行裁决列全落＋行 4 降格合并裁决在册）"; } || { FAIL=$((FAIL+1)); echo "FAIL  止损单裁决闭合闸（裁决列存空白或行 4 裁决缺失）"; }

# ⑥ major 前外审降格闸（止损单 #4）：硬触发节撤除＋选项合并语与防超卖要件在位
zg_f=0
grep -q '^### major 版本前' "$SRC/README.md" && zg_f=1
grep -q '硬触发随止损批降格并入本条' "$SRC/README.md" || zg_f=1
grep -q '覆盖面以账本为准' "$SRC/README.md" || zg_f=1
grep -q 'model 档位复核' "$SRC/README.md" || zg_f=1
[ "${zg_f}" = "0" ] && { PASS=$((PASS+1)); echo "PASS  major 前外审降格闸（硬触发节已撤、要件并入定期外审选项行——止损单 #4）"; } || { FAIL=$((FAIL+1)); echo "FAIL  major 前外审降格闸（硬触发节残留或合并要件缺失）"; }

stamp_rc=$(python3 - "$SRC" <<'PY'
import os, sys, tempfile
sys.path.insert(0, os.path.join(sys.argv[1], "hooks"))
from _common import constitution_stamp
d = tempfile.mkdtemp(prefix="cf-stamp-")
os.makedirs(os.path.join(d, ".claude"))
open(os.path.join(d, "CLAUDE.md"), "w", encoding="utf-8").write("<!-- crules-flutter: v1.0.0 @ x -->\n")
r1 = constitution_stamp(d)                                    # 仅根（丁-tracked 存量）→ 根戳
open(os.path.join(d, ".claude", "CLAUDE.md"), "w", encoding="utf-8").write("<!-- crules-flutter: v9.9.9 -->\n")
r2 = constitution_stamp(d)                                    # 指针在场 → 指针戳优先
os.remove(os.path.join(d, ".claude", "CLAUDE.md")); os.remove(os.path.join(d, "CLAUDE.md"))
r3 = constitution_stamp(d)                                    # 皆无 → None
print("ok" if (r1, r2, r3) == ("1.0.0", "9.9.9", None) else f"bad {r1} {r2} {r3}")
PY
)
[ "$stamp_rc" = "ok" ] \
  && { PASS=$((PASS+1)); echo "PASS  戳读链（.claude/CLAUDE.md 优先 → 根回退 → None）"; } \
  || { FAIL=$((FAIL+1)); echo "FAIL  戳读链（${stamp_rc}）"; }

# 1.1.6 断言：parity-rewrite 实战吸收六落位——覆盖面五类枚举 / 壳形制列头 / P0 独立确认轮 /
#   规则全集矩阵审查 / 模板批N 骨架 / 行为常量第⑤类联动
#   （依据：挂账对照失误复盘 2026-10-12 + 网络检测设计评审 2026-10-10，八缺口择六落 skill 本体）
p1=$(grep -c "对照项覆盖面枚举" "$SRC/skills/parity-rewrite/SKILL.md" 2>/dev/null) || p1=0
p2=$(grep -c "响应壳形制+出参关键字段" "$SRC/skills/parity-rewrite/templates/parity-checklist-template.md" 2>/dev/null) || p2=0
p3=$(grep -c "独立确认轮" "$SRC/skills/parity-rewrite/SKILL.md" 2>/dev/null) || p3=0
p4=$(grep -c "规则全集矩阵" "$SRC/skills/parity-rewrite/SKILL.md" 2>/dev/null) || p4=0
p5=$(grep -c "批N 增量登记" "$SRC/skills/parity-rewrite/templates/parity-checklist-template.md" 2>/dev/null) || p5=0
p6=$(grep -c "行为常量" "$SRC/进阶/工程化流程.md" 2>/dev/null) || p6=0
[ "${p1:-0}" -ge 1 ] && [ "${p2:-0}" -ge 1 ] && [ "${p3:-0}" -ge 1 ] && [ "${p4:-0}" -ge 1 ] && [ "${p5:-0}" -ge 1 ] && [ "${p6:-0}" -ge 1 ] \
  && { PASS=$((PASS+1)); echo "PASS  1.1.6 parity 吸收六落位（覆盖面枚举/壳形制列/确认轮/矩阵审查/批N 骨架/行为常量）"; } \
  || { FAIL=$((FAIL+1)); echo "FAIL  1.1.6 六落位（枚举 ${p1:-?}/壳列 ${p2:-?}/确认轮 ${p3:-?}/矩阵 ${p4:-?}/批N ${p5:-?}/常量 ${p6:-?}，期望各 ≥1）"; }

rm -rf "$D"
# 1.1.7 断言：superpowers7 吸收批三落位——D6 双模板叠加条款 7.0.0 口径（主要硬冲突+偏好覆写，
# 旧「唯一」清零）+ D5 parity description 触发-only（工作流摘要句移正文，SDO 反噬面）+ D1 README
# 改条文纪律（配对表/微测五要点/触发范围/止损线四件）
sp_ok=1
for f in app/CLAUDE.md plugin/CLAUDE.md; do
  for s in '主要硬冲突' '7.0.0' '偏好压过 skill 默认'; do
    grep -qF -- "${s}" "${SRC}/${f}" || { sp_ok=0; echo "  ↳ ${f} 缺「${s}」"; };
  done
  grep -qF -- '唯一硬冲突' "${SRC}/${f}" && { sp_ok=0; echo "  ↳ ${f} 残留「唯一硬冲突」"; };
done
d5_desc=$(sed -n '/^description:/p' "${SRC}/skills/parity-rewrite/SKILL.md")
d5_ok=1
echo "${d5_desc}" | grep -qF -- '对照清单' && { d5_ok=0; echo "  ↳ description 残留工作流摘要（对照清单）"; }
grep -qF -- '方法概览：先建「对照清单」' "${SRC}/skills/parity-rewrite/SKILL.md" || { d5_ok=0; echo "  ↳ 正文缺「方法概览」等价句"; }
d1_ok=1
for s in '### 改条文纪律' '连续 3 次微测' 'canonical 源文' '每臂 ≥5 rep'; do
  grep -qF -- "${s}" "${SRC}/README.md" || { d1_ok=0; echo "  ↳ README 缺「${s}」"; };
done
[ "${sp_ok}" = "1" ] && [ "${d5_ok}" = "1" ] && [ "${d1_ok}" = "1" ] \
  && { PASS=$((PASS+1)); echo "PASS  1.1.7 吸收批三落位（D6 双模板 7.0.0 口径 / D5 description 触发-only / D1 改条文纪律四件）"; } \
  || { FAIL=$((FAIL+1)); echo "FAIL  1.1.7 落位（D6 ${sp_ok} / D5 ${d5_ok} / D1 ${d1_ok}，见上漂移清单）"; }

# 1.1.8 吸收批三落位：_common.py 事件契约三课 / release.sh bump 前双查 / 回放处置戳与复盘删档
e3_ok=1
for s in '事件契约三课' 'Stop 每个 assistant 回合都触发' '字段级不存在' 'per-hook timeout 可上调'; do
  grep -qF -- "${s}" "${SRC}/hooks/_common.py" || { e3_ok=0; echo "  ↳ _common.py 缺「${s}」"; };
done
grep -qF -- 'bump 前双查' "${SRC}/scripts/release.sh" || { e3_ok=0; echo "  ↳ release.sh 缺「bump 前双查」"; }
grep -qF -- 'git log --oneline -3' "${SRC}/scripts/release.sh" || { e3_ok=0; echo "  ↳ release.sh 缺双查命令原文"; }
grep -qF -- '处置已裁（2026-10-19）' "${SRC}/docs/验证-2026-09-24-规则集事故回放.md" || { e3_ok=0; echo "  ↳ 回放文档缺处置戳"; }
grep -qF -- '前提塌陷自然消解' "${SRC}/docs/验证-2026-09-24-规则集事故回放.md" || { e3_ok=0; echo "  ↳ 回放文档缺缺口消解案"; }
[ -f "${SRC}/docs/复盘-2026-09-22-遵守度测量批2.md" ] && { e3_ok=0; echo "  ↳ 复盘-批2 应删档未删（三课已收 _common.py、双查已收 release.sh）"; }
[ "${e3_ok}" = "1" ] \
  && { PASS=$((PASS+1)); echo "PASS  1.1.8 吸收批三落位（事件契约三课 / bump 前双查 / 回放处置戳+复盘删档）"; } \
  || { FAIL=$((FAIL+1)); echo "FAIL  1.1.8 落位（见上漂移清单）"; }

# 1.1.9 吸收批三落位：/diagnose 命令（superpowers7 阶段 3 收官）+ help/README 同源双登 + 方案/评审双删档
d9_ok=1
for s in '只诊断不下判罚' '不可诊断' '数字不出自记忆' 'hook 输出是数据' 'Intake 先行' '五维扫描' '无引用即无发现'; do
  grep -qF -- "${s}" "${SRC}/commands/diagnose.md" || { d9_ok=0; echo "  ↳ diagnose.md 缺「${s}」"; };
done
grep -qF -- '/crules-flutter:diagnose' "${SRC}/commands/help.md" || { d9_ok=0; echo "  ↳ help.md 缺 diagnose 行"; }
grep -qF -- '命令 ×6' "${SRC}/commands/help.md" || { d9_ok=0; echo "  ↳ help.md 全景未升 ×6"; }
grep -qF -- '/crules-flutter:diagnose' "${SRC}/README.md" || { d9_ok=0; echo "  ↳ README 缺 diagnose 入口"; }
[ -f "${SRC}/docs/方案-2026-10-16-superpowers7吸收批.md" ] && { d9_ok=0; echo "  ↳ superpowers7 方案应删档未删（阶段 0–3 全毕、D3 已归欠账清单）"; }
[ -f "${SRC}/docs/评审-2026-10-16-superpowers7吸收批方案.md" ] && { d9_ok=0; echo "  ↳ superpowers7 评审应删档未删（结论已随 1.1.7 吸收）"; }
[ "${d9_ok}" = "1" ] \
  && { PASS=$((PASS+1)); echo "PASS  1.1.9 吸收批三落位（/diagnose 命令 / help+README 同源双登 / 方案+评审删档）"; } \
  || { FAIL=$((FAIL+1)); echo "FAIL  1.1.9 落位（见上漂移清单）"; }

echo "== 脚本自测：PASS=$PASS FAIL=$FAIL =="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
