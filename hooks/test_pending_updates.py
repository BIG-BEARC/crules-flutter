#!/usr/bin/env python3
# pending-updates.py 写侧 fixture（1.0.30 队列分文件）——sid 路由 / 回退 / D8 向上定根 / 去重 / 净化 /
#   边界 / R5 落盘正斜杠归一 / R3 异型字段 fail-open / N1 顶层形状 / N2 旧行自愈，共 12 条检查
import json, os, subprocess, sys, tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pending-updates.py")
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

def setup_project(d):
    os.makedirs(os.path.join(d, ".claude", "memory"))
    open(os.path.join(d, ".claude", "memory", "NAVIGATION.md"), "w", encoding="utf-8").close()

def payload(path, sid="s1"):
    p = {"hook_event_name": "PostToolUse", "tool_input": {"file_path": path}}
    if sid is not None:
        p["session_id"] = sid
    return p

def lines_of(queue):
    with open(queue, encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]

with tempfile.TemporaryDirectory() as d:
    setup_project(d)
    os.makedirs(os.path.join(d, "src"))
    fp = os.path.join(d, "src", "foo.py")
    open(fp, "w", encoding="utf-8").close()
    mem = os.path.join(d, ".claude", "memory")

    # sid 有 → 写自己会话队列文件，旧单文件不动
    run(payload(fp, "s1"), d)
    q1 = os.path.join(mem, ".pending-updates.s1")
    ok = os.path.exists(q1) and not os.path.exists(os.path.join(mem, ".pending-updates"))
    if ok:
        ok = lines_of(q1) and "foo.py" in lines_of(q1)[0]
    check("sid 有 → 写 .pending-updates.s1 且不建旧单文件（D1/D2）", ok)

    # 去重：同文件重复触发只留一行
    run(payload(fp, "s1"), d)
    check("同会话重复触发 → 去重单行", os.path.exists(q1) and len(lines_of(q1)) == 1)

    # 无 sid → 回退写旧单文件
    fp2 = os.path.join(d, "src", "bar.py")
    open(fp2, "w", encoding="utf-8").close()
    run(payload(fp2, None), d)
    ql = os.path.join(mem, ".pending-updates")
    check("无 sid → 回退写旧单文件（D2）", os.path.exists(ql) and "bar.py" in "".join(lines_of(ql)))

    # sid 净化：怪 sid 落净化名文件（D6）
    fp3 = os.path.join(d, "src", "baz.py")
    open(fp3, "w", encoding="utf-8").close()
    run(payload(fp3, "we!rd/s:id"), d)
    qs = os.path.join(mem, ".pending-updates.we-rd-s-id")
    check("怪 sid → 净化文件名 .pending-updates.we-rd-s-id（D6）", os.path.exists(qs) and "baz.py" in "".join(lines_of(qs)))

    # 边界保持：记忆库自身 / .claude 与 .git 内文件不入队（既有行为锁）
    n_before = len(os.listdir(mem))
    run(payload(os.path.join(d, ".claude", "memory", "NAVIGATION.md"), "s1"), d)
    run(payload(os.path.join(d, ".git", "HEAD"), "s1"), d)
    n_after = len(os.listdir(mem))
    check("记忆库自身与 .claude/.git 内文件不入队（既有边界）",
          n_before == n_after and os.path.exists(q1) and len(lines_of(q1)) == 1)

# D8：会话 cd 进子目录 → 向上找 NAVIGATION.md 定根，队列仍落项目根
with tempfile.TemporaryDirectory() as d:
    proj = os.path.join(d, "proj")
    deep = os.path.join(proj, "lib", "features")
    os.makedirs(deep)
    setup_project(proj)
    fp = os.path.join(deep, "page.py")
    open(fp, "w", encoding="utf-8").close()
    run(payload(fp, "s1"), deep)  # cwd = 深层子目录
    q = os.path.join(proj, ".claude", "memory", ".pending-updates.s1")
    check("cwd 在子目录 → 向上定根写项目根队列（D8）", os.path.exists(q) and "page.py" in "".join(lines_of(q)))

# 无记忆库项目 → 全链静默，不建任何 .claude
# （假设本临时目录的**祖先**无 .claude/memory/NAVIGATION.md——D8 向上定根后，祖先若有记忆库
#   本断言会误命中。tempfile 祖先为系统临时目录，正常环境成立；见 reviewer R7）
with tempfile.TemporaryDirectory() as d:
    fp = os.path.join(d, "x.py")
    open(fp, "w", encoding="utf-8").close()
    rc, out = run(payload(fp, "s1"), d)
    check("无 NAVIGATION → 静默不建队列", rc == 0 and out == "" and not os.path.exists(os.path.join(d, ".claude")))

# R5（1.0.30 实测修）：落盘路径统一正斜杠——Windows 上 os.path.relpath 返回反斜杠，而 git status
#   --porcelain 恒输出正斜杠（本机实测签名 M skills/flutter-rules/...）；不归一则读侧「已入队」比对
#   在 Windows 恒不匹配，既有「已入队不重复报」与 D5 声称双双失效。本断言在 Linux 上恒真、Windows 上真判。
with tempfile.TemporaryDirectory() as d:
    setup_project(d)
    os.makedirs(os.path.join(d, "lib", "features"))
    fp = os.path.join(d, "lib", "features", "page.py")
    open(fp, "w", encoding="utf-8").close()
    run(payload(fp, "s1"), d)
    q = os.path.join(d, ".claude", "memory", ".pending-updates.s1")
    ok = os.path.exists(q)
    line = lines_of(q)[0] if ok and lines_of(q) else ""
    check("落盘路径统一正斜杠（R5——与 git porcelain 对齐，Windows 反斜杠会致去重失效）",
          ok and line == "lib/features/page.py")

# R3（1.0.30 收口）：fail-open 契约不止护非法 JSON——**合法 JSON 但字段异型**须同样静默退场，
#   不得抛未捕获异常（旧写法 re.sub / .get 在异型字段上会崩，与头注声称不符）
with tempfile.TemporaryDirectory() as d:
    setup_project(d)
    rc1, out1 = run({"hook_event_name": "PostToolUse", "session_id": 123,
                     "tool_input": {"file_path": os.path.join(d, "a.py")}}, d)
    rc2, out2 = run({"hook_event_name": "PostToolUse", "tool_input": "not-a-dict"}, d)
    check("异型字段（session_id 非字符串 / tool_input 非 dict）→ exit 0 静默（R3）",
          rc1 == 0 and out1 == "" and rc2 == 0 and out2 == "")
    # file_path 非字符串：须按「无此字段」退场，不得 str() 成垃圾串入队（失真 != 有效条目）
    # 注：载荷须带 session_id——否则退化写 legacy 单文件，断言查 .s1 会假绿（本断言初版即踩此坑）
    rc3, out3 = run({"hook_event_name": "PostToolUse", "session_id": "s1",
                     "tool_input": {"file_path": 12345}}, d)
    q = os.path.join(d, ".claude", "memory", ".pending-updates.s1")
    check("file_path 非字符串 → 静默且不产垃圾行（R3 相邻）", rc3 == 0 and out3 == "" and not os.path.exists(q))

# N1（复读新发现）：合法 JSON 但**顶层非对象**（[] / "x" / 123 / null）→ data.get 抛 AttributeError，
#   在 try 外 → 未捕获崩溃，与「fail-open」头注不符。JSON 解析成功不等于形状合法，须显式判 dict。
with tempfile.TemporaryDirectory() as d:
    setup_project(d)
    rc, out = run([], d)
    rc2b, out2b = run("just-a-string", d)
    check("顶层非对象 JSON（[] / 字符串）→ exit 0 静默（N1）",
          rc == 0 and out == "" and rc2b == 0 and out2b == "")

# N2（复读新发现）：队列已含**反斜杠旧行**（Windows 1.0.30 前落盘形态）时再次入队——须在读旧行处
#   一并归一，否则同一文件在队列里留正/反斜杠两行（去重按原始串比对）且永不自愈
with tempfile.TemporaryDirectory() as d:
    setup_project(d)
    os.makedirs(os.path.join(d, "lib"))
    fp = os.path.join(d, "lib", "a.py")
    open(fp, "w", encoding="utf-8").close()
    q = os.path.join(d, ".claude", "memory", ".pending-updates.s1")
    with open(q, "w", encoding="utf-8") as f:
        f.write("lib\\a.py\n")   # 旧反斜杠行
    run(payload(fp, "s1"), d)
    check("旧反斜杠行再入队 → 归一自愈不留两行（N2）", lines_of(q) == ["lib/a.py"])

print(f"pending-updates fixture: {'全绿' if fails == 0 else f'{fails} 失败'}")
sys.exit(1 if fails else 0)
