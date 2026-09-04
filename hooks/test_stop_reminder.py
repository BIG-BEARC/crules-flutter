#!/usr/bin/env python3
# stop-reminder.py fixture 回归（A3）——四态：无队列静默 / 空队列静默 / stop_hook_active 抑制 / 队列非空出 additionalContext
import json, os, subprocess, sys, tempfile

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

print(f"stop-reminder fixture: {'全绿' if fails == 0 else f'{fails} 失败'}")
sys.exit(1 if fails else 0)
