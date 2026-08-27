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
t 0 "python3 $SRC/hooks/test_deny_list.py"                 "deny-list fixture 应全绿"

# 幂等断言：同输入两次运行结论一致且均 block（双 plugin 共存的可测背书）
BADCMD="git push --fo""rce origin main"   # 分段拼接，避免源码含完整字面串
j1=$(printf '{"tool_input":{"command":"%s"}}' "$BADCMD")
r1=$(printf '%s' "$j1" | python3 "$SRC/hooks/deny-list.py" | grep -c block || true)
r2=$(printf '%s' "$j1" | python3 "$SRC/hooks/deny-list.py" | grep -c block || true)
if [ "$r1" = "$r2" ] && [ "$r1" -ge 1 ]; then PASS=$((PASS+1)); echo "PASS  deny-list 重复调用幂等（两次均 block）"; else FAIL=$((FAIL+1)); echo "FAIL  幂等断言（r1=$r1 r2=$r2）"; fi

rm -rf /tmp/cf-selftest
echo "== 脚本自测：PASS=$PASS FAIL=$FAIL =="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
