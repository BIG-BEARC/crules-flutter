#!/usr/bin/env bash
# crules-flutter 脚本自测（批 2c）——应报错断言 + 幂等断言
# 注：幂等断言的测试命令经变量拼接构造（避免脚本源码含破坏命令完整字面串——deny-list 对
#     Bash 内字面串 deny-by-default，本文件须用 Write 工具落盘或分段拼接写入）
set -uo pipefail
SRC=$(cd "$(dirname "$0")/.." && pwd)
PASS=0; FAIL=0
t() { eval "$2" >/dev/null 2>&1; rc=$?
  if [ "$rc" = "$1" ]; then PASS=$((PASS+1)); echo "PASS  $3"; else FAIL=$((FAIL+1)); echo "FAIL  $3（rc=$rc 期望 $1）"; fi; }
D=/tmp/cf-selftest
mkdir -p "$D/old"
printf '# 老项目\n' > "$D/old/CLAUDE.md"
t 1 "bash $SRC/scripts/install.sh $D/old --app"           "install 老项目（无戳）应中止"
t 1 "bash $SRC/scripts/release.sh abc"                     "release 非法版本号应报错"
t 0 "bash $SRC/scripts/release.sh draft"                    "release draft 应正常出稿（外审②回归断言）"
t 0 "python3 $SRC/hooks/test_deny_list.py"                 "deny-list fixture 应全绿"

# F2 回归三断言（真机 fixture 固化——2026-08-27 flutter create 28 行注释版产物签入 testdata/）
T1=/tmp/cf-ao1; T2=/tmp/cf-ao2; mkdir -p "$T1" "$T2"
cp "$SRC/scripts/testdata/scaffold-analysis_options.yaml" "$T1/analysis_options.yaml"
printf 'include: package:flutter_lints/flutter.yaml\nlinter:\n  rules:\n    - always_use_package_imports\n' > "$T2/analysis_options.yaml"
o1=$(bash $SRC/scripts/install.sh $T1 --app 2>/dev/null | grep -c UPGRADE)
[ "$o1" -ge 1 ] && [ -f "$T1/analysis_options.yaml.scaffold-bak" ] && { PASS=$((PASS+1)); echo "PASS  真机脚手架 fixture → UPGRADE（F1 回归）"; } || { FAIL=$((FAIL+1)); echo "FAIL  脚手架应 UPGRADE"; }
o2=$(bash $SRC/scripts/install.sh $T2 --app 2>/dev/null | grep -c SIDE-CAR)
[ "$o2" -ge 1 ] && grep -q 'always_use_package_imports' "$T2/analysis_options.yaml" && { PASS=$((PASS+1)); echo "PASS  自定义 lint → SIDE-CAR 伴生且原文保留"; } || { FAIL=$((FAIL+1)); echo "FAIL  自定义应 SIDE-CAR"; }
printf 'WR-SENTINEL\n' > "$T1/.claude/memory/business-rules.md"
bash $SRC/scripts/install.sh $T1 --app --force >/dev/null 2>&1
grep -q 'WR-SENTINEL' "$T1/.claude/memory/business-rules.md" && [ -f "$T1/CLAUDE.md.new" ] && { PASS=$((PASS+1)); echo "PASS  force 升级：memory 哨兵 KEEP + CLAUDE.md 出 .new"; } || { FAIL=$((FAIL+1)); echo "FAIL  force 安全升级"; }
rm -rf /tmp/cf-ao1 /tmp/cf-ao2

# 0.4.0 批1断言（设计 §5 test-self 行）：落位 8 模板 / init 三处必填 / twin 一致性
T4=/tmp/cf-pitfalls; mkdir -p "$T4"
bash $SRC/scripts/install.sh $T4 --app >/dev/null 2>&1
nm=$(ls "$T4/.claude/memory"/*.md 2>/dev/null | wc -l | tr -d ' ')
[ "$nm" = "8" ] && { PASS=$((PASS+1)); echo "PASS  memory 落位 8 模板"; } || { FAIL=$((FAIL+1)); echo "FAIL  memory 应落位 8 模板（实为 $nm）"; }
rm -rf "$T4"
grep -q '支持矩阵' "$SRC/commands/init.md" && grep -q '矩阵' "$SRC/scripts/install.sh" && { PASS=$((PASS+1)); echo "PASS  init 必填三处引导（init.md + install.sh 下一步提示均含矩阵）"; } || { FAIL=$((FAIL+1)); echo "FAIL  init 三处缺矩阵引导"; }
tw1=$(sed -n '/twin:mem-files/,/^$/p' "$SRC/memory/README.md" | grep -c '^| `')
tw2=$(sed -n '/twin:mem-files/,/^$/p' "$SRC/进阶/记忆库体系.md" | grep -c '^| `')
act=$(ls "$SRC"/memory/*.md | grep -v 'README.md' | wc -l | tr -d ' ')
lst=$(sed -n '/twin:mem-files/,/^$/p' "$SRC/memory/README.md" | grep -oE '`[A-Za-z-]+\.md`' | sort -u | wc -l | tr -d ' ')
[ "$tw1" = "$tw2" ] && [ "$act" = "$lst" ] && [ "$tw1" -ge 7 ] && { PASS=$((PASS+1)); echo "PASS  twin:mem-files 一致（双侧 $tw1 行，实际模板 $act = 表列 $lst）"; } || { FAIL=$((FAIL+1)); echo "FAIL  twin:mem-files 漂移（tw1=$tw1 tw2=$tw2 act=$act lst=$lst）"; }

# 幂等断言：同输入两次运行结论一致且均 block（双 plugin 共存的可测背书）
BADCMD="git push --fo""rce origin main"   # 分段拼接，避免源码含完整字面串
j1=$(printf '{"tool_input":{"command":"%s"}}' "$BADCMD")
r1=$(printf '%s' "$j1" | python3 "$SRC/hooks/deny-list.py" | grep -c block || true)
r2=$(printf '%s' "$j1" | python3 "$SRC/hooks/deny-list.py" | grep -c block || true)
if [ "$r1" = "$r2" ] && [ "$r1" -ge 1 ]; then PASS=$((PASS+1)); echo "PASS  deny-list 重复调用幂等（两次均 block）"; else FAIL=$((FAIL+1)); echo "FAIL  幂等断言（r1=$r1 r2=$r2）"; fi

rm -rf /tmp/cf-selftest
echo "== 脚本自测：PASS=$PASS FAIL=$FAIL =="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
