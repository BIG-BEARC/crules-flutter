#!/usr/bin/env python3
# crules-flutter 记忆库漂移提醒队列（PostToolUse，随 plugin 分发）
# 机制：Edit/Write 成功后，若项目启用了记忆库（.claude/memory/NAVIGATION.md 存在）且被改文件
#   是包外源文件，则把其路径追加进 .claude/memory/.pending-updates（去重）。
# 边界（v18 复盘）：不判意图、不阻止任何操作——只是把「记得更新索引」从记忆问题变成看得见的待办；
#   会话收尾主控看到队列非空即提示补索引（MAINTENANCE.md 自检清单）。
# 输入契约 fail-open（批A F10①，1.0.11）：stdin 非法 JSON → exit 0 静默——输入由宿主构造风险低，
#   fail-closed 恐误伤非 JSON 探活；本 hook 本就不阻止任何操作，静默即等价「无待办」
import json, os, sys

# stdin 编码显式化（1.0.21，Windows 实机 P0-A）：宿主送来的 JSON 是 UTF-8，非 UTF-8 码页
#   （简中 936 / 繁中 950…）下按码页解——实测**不抛**（Windows 标准流 errors=surrogateescape），
#   坏字节变孤立代理项：file_path 含非 ASCII（中文目录名）时被解成垃圾串，仍会写进队列但条目
#   不可用（失真，非漏记）。本 hook 不写 stdout/stderr（输出侧无 P0-A 之病），故只钉输入流。
try:
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
fp = (data.get("tool_input") or {}).get("file_path") or ""
if not fp:
    sys.exit(0)
root = os.getcwd()
mem = os.path.join(root, ".claude", "memory")
if not os.path.exists(os.path.join(mem, "NAVIGATION.md")):  # 记忆库未启用 → 不介入
    sys.exit(0)
real = os.path.realpath(fp)
if real.startswith(os.path.realpath(mem) + os.sep):  # 记忆库自身文件不记
    sys.exit(0)
if "/.claude/" in real or "/.git/" in real:  # 配置与 git 内部不记
    sys.exit(0)
queue = os.path.join(mem, ".pending-updates")
try:
    lines = set()
    if os.path.exists(queue):
        lines = {l.strip() for l in open(queue, encoding="utf-8") if l.strip()}
    lines.add(os.path.relpath(real, root))
    with open(queue, "a+", encoding="utf-8") as f:  # a+ 使 flock 生效于已存在/新建文件
        try:
            import fcntl
            fcntl.flock(f, fcntl.LOCK_EX)           # 防并发 async hook 读-改-写竞态
        except ImportError:
            pass  # Windows 无 fcntl（D3，2026-09-05）：降级无锁追加——O_APPEND 单行写具原子性，竞态窗口远小于「完全不记」
        f.seek(0)
        lines |= {l.strip() for l in f.read().splitlines() if l.strip()}
        f.seek(0); f.truncate()
        f.write("\n".join(sorted(lines)) + "\n")
except Exception:
    pass
sys.exit(0)
