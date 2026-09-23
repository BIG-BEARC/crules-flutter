#!/usr/bin/env python3
# 跨 hook 队列契约测试（1.0.39 · 裁决单-2026-09-22 D-4）——写侧 pending-updates.py 真调产出
#   队列 → 读侧 stop-reminder.py 真调消费，锁两 hook 对同一文件契约（队列名 sid 路由 / 落盘
#   正斜杠 / 净化规则）的互操作。与两侧各自 fixture 的分工：那些各测各侧内部逻辑，本文件测
#   「写出来的东西读侧认不认」——1.0.30 R5（写侧反斜杠落盘、读侧 git 正斜杠恒不匹配）正是
#   这个盲区咬过的实账；_common 收编后同源函数不会再漂，但队列**格式契约**仍是两文件约定，
#   只有互调能锁。
import json, os, subprocess, sys, tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
WRITER = os.path.join(HERE, "pending-updates.py")
READER = os.path.join(HERE, "stop-reminder.py")
fails = 0

def run(hook, payload, cwd):
    p = subprocess.run([sys.executable, hook], input=json.dumps(payload).encode(),
                       capture_output=True, cwd=cwd)
    return p.returncode, p.stdout.decode("utf-8", "replace")

def check(name, cond):
    global fails
    print(("PASS  " if cond else "FAIL  ") + name)
    if not cond:
        fails += 1

def setup_project(d):
    os.makedirs(os.path.join(d, ".claude", "memory"))
    open(os.path.join(d, ".claude", "memory", "NAVIGATION.md"), "w", encoding="utf-8").close()

def write_event(path, sid):
    return {"hook_event_name": "PostToolUse", "session_id": sid,
            "tool_input": {"file_path": path}}

def stop_event(sid):
    return {"hook_event_name": "Stop", "session_id": sid, "stop_hook_active": False}

def reminder_out(sid, cwd):
    rc, out = run(READER, stop_event(sid), cwd)
    return rc, out

def ctx_of(out):
    """从 Stop hook 输出 JSON 取 additionalContext（无输出返回 None）"""
    if not out.strip():
        return None
    try:
        return json.loads(out)["hookSpecificOutput"]["additionalContext"]
    except Exception:
        return "BAD-JSON:" + out[:80]

# 契约 1：正常 sid——写侧落盘的文件名与内容，读侧必须消费到
with tempfile.TemporaryDirectory() as d:
    setup_project(d)
    os.makedirs(os.path.join(d, "lib"))
    fp = os.path.join(d, "lib", "contract_a.dart")
    open(fp, "w", encoding="utf-8").close()
    rrc, rerr = run(WRITER, write_event(fp, "conv-1"), d)
    check("写侧 exit 0 且无 stderr", rrc == 0 and rerr == "")
    q = os.path.join(d, ".claude", "memory", ".pending-updates.conv-1")
    check("写侧落盘读侧同名可读（sid 直进文件名）", os.path.isfile(q))
    rc, out = reminder_out("conv-1", d)
    ctx = ctx_of(out)
    check("读侧提醒命中写侧条目", ctx is not None and "contract_a.dart" in ctx)

# 契约 2：怪 sid 净化名——写侧 sanitize 出的队列文件，读侧同规则必须对上
#（收编前这是两份 re.sub 字面串；收编后同源，此断言防的是未来分叉/格式约定漂）
with tempfile.TemporaryDirectory() as d:
    setup_project(d)
    fp = os.path.join(d, "weird.dart")
    open(fp, "w", encoding="utf-8").close()
    run(WRITER, write_event(fp, "we!rd/conv:2"), d)
    q = os.path.join(d, ".claude", "memory", ".pending-updates.we-rd-conv-2")
    check("怪 sid 写侧净化落盘 .pending-updates.we-rd-conv-2", os.path.isfile(q))
    rc, out = reminder_out("we!rd/conv:2", d)
    check("读侧同怪 sid 消费到净化队列", "weird.dart" in (ctx_of(out) or ""))

# 契约 3：会话隔离——A 会话的队列，B 会话的 Stop 不读（不串台）
with tempfile.TemporaryDirectory() as d:
    setup_project(d)
    fp = os.path.join(d, "mine.dart")
    open(fp, "w", encoding="utf-8").close()
    run(WRITER, write_event(fp, "conv-A"), d)
    rc, out = reminder_out("conv-B", d)
    check("B 会话 Stop 对 A 会话队列静默（并行不互扰）", out.strip() == "")

# 契约 4：无 sid 写 legacy 单文件——读侧 D2/D3 对位消费
with tempfile.TemporaryDirectory() as d:
    setup_project(d)
    fp = os.path.join(d, "legacy.dart")
    open(fp, "w", encoding="utf-8").close()
    ev = write_event(fp, "conv-4")
    del ev["session_id"]
    run(WRITER, ev, d)
    q = os.path.join(d, ".claude", "memory", ".pending-updates")
    check("无 sid 写旧单文件（D2）", os.path.isfile(q))
    rc, out = reminder_out("conv-4", d)
    ctx = ctx_of(out)
    check("有 sid 的读侧迁移消费 legacy 行（D3）", ctx is not None and "legacy.dart" in ctx)

# 契约 5：正斜杠落盘行在 git 快查并集下语义一致——写入深层路径，读侧提醒条数正确、
#   不出现「同文件两行」形态（写侧去重 + 读侧 norm_paths 归一的联合面）
with tempfile.TemporaryDirectory() as d:
    setup_project(d)
    os.makedirs(os.path.join(d, "lib", "features"))
    fp = os.path.join(d, "lib", "features", "deep.dart")
    open(fp, "w", encoding="utf-8").close()
    run(WRITER, write_event(fp, "conv-5"), d)
    run(WRITER, write_event(fp, "conv-5"), d)  # 重触发
    q = os.path.join(d, ".claude", "memory", ".pending-updates.conv-5")
    lines = [l.strip() for l in open(q, encoding="utf-8") if l.strip()]
    check("重复写去重单行 + 正斜杠深层路径", lines == ["lib/features/deep.dart"])
    rc, out = reminder_out("conv-5", d)
    ctx = ctx_of(out)
    check("读侧报 1 条非 2 条", ctx is not None and "1 条" in ctx)

print(f"queue-contract fixture: {'全绿' if fails == 0 else f'{fails} 失败'}")
sys.exit(1 if fails else 0)
