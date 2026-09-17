#!/usr/bin/env python3
# stop-reminder.py fixture 回归（A3）——四态：无队列静默 / 空队列静默 / stop_hook_active 抑制 / 队列非空出 additionalContext
import json, os, subprocess, sys, tempfile

# 驱动自身 print 含中文（1.0.21 Windows 实机 P0-A，与 deny-list.py 同批）：宿主码页非 UTF-8
#   （简中 936 / 繁中 950…）时抛 UnicodeEncodeError 整跑即崩。读侧无需动——bytes.decode()
#   本就默认 UTF-8（子进程输出自 1.0.21 起为显式 UTF-8，两侧对齐）。
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stop-reminder.py")
fails = 0

def run(payload, cwd):
    p = subprocess.run([sys.executable, HOOK], input=json.dumps(payload).encode(),
                       capture_output=True, cwd=cwd)
    return p.returncode, p.stdout.decode()

def check(name, cond):
    global fails
    print(("PASS  " if cond else "FAIL  ") + name)
    if not cond:
        fails += 1

with tempfile.TemporaryDirectory() as d:
    os.makedirs(os.path.join(d, ".claude", "memory"))
    base = {"hook_event_name": "Stop", "stop_hook_active": False}
    q = os.path.join(d, ".claude", "memory", ".pending-updates")

    rc, out = run(base, d)
    check("无队列文件 → 静默", rc == 0 and out == "")
    open(q, "w", encoding="utf-8").close()
    rc, out = run(base, d)
    check("队列空 → 静默", rc == 0 and out == "")
    with open(q, "w", encoding="utf-8") as f:
        f.write("lib/features/order/page.dart\nlib/core/network/api.dart\n")
    rc, out = run({**base, "stop_hook_active": True}, d)
    check("连环续轮（stop_hook_active）→ 抑制", rc == 0 and out == "")
    rc, out = run(base, d)
    ok = rc == 0 and out != ""
    if ok:
        j = json.loads(out)
        ac = j.get("hookSpecificOutput", {}).get("additionalContext", "")
        ok = j.get("hookSpecificOutput", {}).get("hookEventName") == "Stop" and "2 条待补索引" in ac and len(ac) < 10000
    check("队列非空 → Stop additionalContext（含条数事实，<10k）", ok)
    # 坏输入不死：非法 JSON / 缺字段
    p = subprocess.run([sys.executable, HOOK], input=b"not-json", capture_output=True, cwd=d)
    check("非法 JSON → exit 0 静默", p.returncode == 0 and p.stdout == b"")

    # 批B F1（1.0.12）：git 快查补充——队列非空 + git 检出未入队 .dart → 提醒含补充句；
    # 生成物（.g.dart）与非 .dart 不计；已入队文件不重复报
    g = tempfile.TemporaryDirectory()
    subprocess.run(["git", "init", "-q", g.name], capture_output=True)
    os.makedirs(os.path.join(g.name, ".claude", "memory"))
    with open(os.path.join(g.name, ".claude", "memory", ".pending-updates"), "w", encoding="utf-8") as f:
        f.write("lib/a.dart\n")
    for f_ in ("lib/a.dart", "lib/b.dart", "lib/c.g.dart", "notes.txt"):
        os.makedirs(os.path.dirname(os.path.join(g.name, f_)) or ".", exist_ok=True)
        open(os.path.join(g.name, f_), "w", encoding="utf-8").close()
    rc, out = run(base, g.name)
    ok = rc == 0 and out != ""
    if ok:
        ac = json.loads(out).get("hookSpecificOutput", {}).get("additionalContext", "")
        # 精确断言：只 1 个未入队（lib/b.dart）——注意队列示例位本身含 lib/a.dart，勿用它做排除断言
        ok = ("另 git 检出 1 个未入队源文件变更" in ac and "lib/b.dart" in ac
              and "c.g.dart" not in ac and "notes.txt" not in ac)
    check("git 快查补充（Bash 落盘盲区）——只报未入队非生成物 .dart", ok)
    # 非 git 仓：静默降级（不发补充句，不影响基础提醒）
    rc, out = run(base, d)
    ok = rc == 0 and out != "" and "未入队源文件变更" not in json.loads(out).get("hookSpecificOutput", {}).get("additionalContext", "")
    check("非 git 仓 → 补充句降级、基础提醒不受影响", ok)
    g.cleanup()

print(f"stop-reminder fixture: {'全绿' if fails == 0 else f'{fails} 失败'}")
sys.exit(1 if fails else 0)
