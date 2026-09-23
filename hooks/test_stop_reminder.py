#!/usr/bin/env python3
# stop-reminder.py fixture 回归（A3 起，1.0.30 扩，1.0.40 加陈旧提醒四态）——原四态（无队列静默 / 空队列静默 / stop_hook_active
#   抑制 / 队列非空出 additionalContext）+ 批B F1 git 快查 + 1.0.30 队列分文件八项（sid 路由 / legacy 回退 /
#   孤儿只报不删 / 新鲜不报 / sid 净化 / D5 已入队并集 / 读侧闸 / R6 文案指向 / R5 反斜杠归一 / N1 顶层形状）
#   + 宪法陈旧提醒四态，共 22 条检查
import json, os, subprocess, sys, tempfile, time

# 驱动自身 print 含中文（1.0.21 Windows 实机 P0-A，与 deny-list.py 同批）：宿主码页非 UTF-8
#   （简中 936 / 繁中 950…）时抛 UnicodeEncodeError 整跑即崩。读侧无需动——bytes.decode()
#   本就默认 UTF-8（子进程输出自 1.0.21 起为显式 UTF-8，两侧对齐）。
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stop-reminder.py")
# 宪法陈旧提醒闸（1.0.40）需要 plugin 版本可读：假 plugin.json 落**临时目录**（不污染分发面），
#   CLAUDE_PLUGIN_ROOT 指过去——与真宿主注入语义同形（compliance fixture 同款打法）
FAKE_PLUG_VER = "99.99.99"
_FAKE_DIR = tempfile.mkdtemp(prefix="cf-fakeplug.")
FAKE_ROOT = _FAKE_DIR
os.makedirs(os.path.join(FAKE_ROOT, ".claude-plugin"), exist_ok=True)
with open(os.path.join(FAKE_ROOT, ".claude-plugin", "plugin.json"), "w", encoding="utf-8") as f:
    json.dump({"name": "crules-flutter", "version": FAKE_PLUG_VER}, f)
fails = 0

def run(payload, cwd):
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=FAKE_ROOT)
    p = subprocess.run([sys.executable, HOOK], input=json.dumps(payload).encode(),
                       capture_output=True, cwd=cwd, env=env)
    return p.returncode, p.stdout.decode()

def check(name, cond):
    global fails
    print(("PASS  " if cond else "FAIL  ") + name)
    if not cond:
        fails += 1

with tempfile.TemporaryDirectory() as d:
    os.makedirs(os.path.join(d, ".claude", "memory"))
    open(os.path.join(d, ".claude", "memory", "NAVIGATION.md"), "w", encoding="utf-8").close()
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
    open(os.path.join(g.name, ".claude", "memory", "NAVIGATION.md"), "w", encoding="utf-8").close()
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

# 1.0.30 队列分文件：sid 路由 / legacy 回退 / 孤儿只报不删（>24h）/ 已入队集并集
with tempfile.TemporaryDirectory() as d2:
    os.makedirs(os.path.join(d2, ".claude", "memory"))
    open(os.path.join(d2, ".claude", "memory", "NAVIGATION.md"), "w", encoding="utf-8").close()
    mem2 = os.path.join(d2, ".claude", "memory")
    own = os.path.join(mem2, ".pending-updates.s-main")
    legacy = os.path.join(mem2, ".pending-updates")
    other = os.path.join(mem2, ".pending-updates.s-other")
    now = time.time()
    sid_payload = {**base, "session_id": "s-main"}

    def ac_of(out):
        return json.loads(out).get("hookSpecificOutput", {}).get("additionalContext", "") if out else ""

    with open(own, "w", encoding="utf-8") as f:
        f.write("lib/own.dart\n")
    rc, out = run(sid_payload, d2)
    check("sid 有 → 读自己会话队列文件（D1）", rc == 0 and "1 条待补索引" in ac_of(out))

    os.remove(own)
    with open(legacy, "w", encoding="utf-8") as f:
        f.write("lib/legacy.dart\n")
    rc, out = run(sid_payload, d2)
    check("sid 有但自己队列空 → 回退读 legacy 单文件（D3 一次性迁移）", rc == 0 and "legacy.dart" in ac_of(out))

    os.remove(legacy)
    rc, out = run(sid_payload, d2)
    check("sid 有队列全空 → 静默", rc == 0 and out == "")

    with open(own, "w", encoding="utf-8") as f:
        f.write("lib/own.dart\n")
    with open(other, "w", encoding="utf-8") as f:
        f.write("lib/other.dart\n")
    old_t = now - 25 * 3600
    os.utime(other, (old_t, old_t))
    rc, out = run(sid_payload, d2)
    check("他人队列文件 >24h → 孤儿计数提示，只报不删（D4）", rc == 0 and "孤儿" in ac_of(out))
    os.utime(other, (now, now))
    rc, out = run(sid_payload, d2)
    check("他人队列文件新鲜 → 不报孤儿（D4 降噪）", rc == 0 and out != "" and "孤儿" not in ac_of(out))

    # sid 文件名净化：怪 sid 也能路由到净化后的文件（D6）
    san = os.path.join(mem2, ".pending-updates.we-rd-s-id")
    with open(san, "w", encoding="utf-8") as f:
        f.write("lib/san.dart\n")
    rc, out = run({**base, "session_id": "we!rd/s:id"}, d2)
    check("怪 sid → 净化后路由到 .pending-updates.we-rd-s-id（D6）", rc == 0 and "san.dart" in ac_of(out))
    os.remove(san)

    # D5：git 快查「已入队」集合并入他人队列文件——他人已入队文件不再报未入队
    g2 = tempfile.TemporaryDirectory()
    subprocess.run(["git", "init", "-q", g2.name], capture_output=True)
    os.makedirs(os.path.join(g2.name, ".claude", "memory"))
    open(os.path.join(g2.name, ".claude", "memory", "NAVIGATION.md"), "w", encoding="utf-8").close()
    own2 = os.path.join(g2.name, ".claude", "memory", ".pending-updates.s-main")
    other2 = os.path.join(g2.name, ".claude", "memory", ".pending-updates.s-other")
    with open(own2, "w", encoding="utf-8") as f:
        f.write("lib/a.dart\n")
    with open(other2, "w", encoding="utf-8") as f:
        f.write("lib/c.dart\n")
    for f_ in ("lib/a.dart", "lib/b.dart", "lib/c.dart"):
        os.makedirs(os.path.dirname(os.path.join(g2.name, f_)) or ".", exist_ok=True)
        open(os.path.join(g2.name, f_), "w", encoding="utf-8").close()
    rc, out = run(sid_payload, g2.name)
    ok = rc == 0 and out != ""
    if ok:
        ac = ac_of(out)
        ok = "另 git 检出 1 个未入队源文件变更" in ac and "lib/b.dart" in ac and "lib/c.dart" not in ac
    check("git 快查已入队集并入他人队列（D5）——c.dart 不再报未入队", ok)
    g2.cleanup()

    # 读侧闸位与写侧对齐（1.0.30 D8 定根伴生）：有队列文件但记忆库未启用（无 NAVIGATION.md）→ 静默
    with tempfile.TemporaryDirectory() as d3:
        os.makedirs(os.path.join(d3, ".claude", "memory"))
        with open(os.path.join(d3, ".claude", "memory", ".pending-updates"), "w", encoding="utf-8") as f:
            f.write("lib/x.dart\n")
        rc, out = run(base, d3)
        check("无 NAVIGATION.md → 静默（读侧闸与写侧对齐）", rc == 0 and out == "")

    # R6（1.0.30 修）：D3 回退命中时文案须指向**旧单文件**——报出的条目来自 legacy，若仍说「清空本会话
    #   队列文件」则用户清无可清（本会话队列本就为空），提醒会反复触发
    with tempfile.TemporaryDirectory() as d4:
        os.makedirs(os.path.join(d4, ".claude", "memory"))
        open(os.path.join(d4, ".claude", "memory", "NAVIGATION.md"), "w", encoding="utf-8").close()
        with open(os.path.join(d4, ".claude", "memory", ".pending-updates"), "w", encoding="utf-8") as f:
            f.write("lib/z.dart\n")
        rc, out = run(sid_payload, d4)
        ac = ac_of(out)
        check("D3 回退命中 → 文案指向旧单文件（R6）",
              rc == 0 and "旧单文件" in ac and ".pending-updates.s-main" not in ac)

    # R5 读侧（1.0.30 修）：1.0.30 之前 Windows 落下的**反斜杠**旧队列行，归一后仍须正确匹配 git
    #   已入队集——否则旧队列存在期间会把已入队文件误报为「未入队」（既有缺陷，非本批引入）
    g3 = tempfile.TemporaryDirectory()
    subprocess.run(["git", "init", "-q", g3.name], capture_output=True)
    os.makedirs(os.path.join(g3.name, ".claude", "memory"))
    open(os.path.join(g3.name, ".claude", "memory", "NAVIGATION.md"), "w", encoding="utf-8").close()
    with open(os.path.join(g3.name, ".claude", "memory", ".pending-updates.s-main"), "w", encoding="utf-8") as f:
        f.write("lib\\a.dart\n")   # 反斜杠旧格式（Windows 1.0.30 前落盘形态）
    for f_ in ("lib/a.dart", "lib/b.dart"):
        os.makedirs(os.path.dirname(os.path.join(g3.name, f_)) or ".", exist_ok=True)
        open(os.path.join(g3.name, f_), "w", encoding="utf-8").close()
    rc, out = run(sid_payload, g3.name)
    ok = rc == 0 and out != ""
    if ok:
        ac = ac_of(out)
        ok = "另 git 检出 1 个未入队源文件变更" in ac and "lib/b.dart" in ac and "lib/a.dart" not in ac
    check("反斜杠旧队列行归一后仍匹配（R5 读侧）——a.dart 不误报未入队", ok)
    g3.cleanup()

    # N1 读侧（1.0.30 修）：顶层非对象 JSON 不得崩——json.load 成功 ≠ 形状合法（与写侧同）
    with tempfile.TemporaryDirectory() as d5:
        os.makedirs(os.path.join(d5, ".claude", "memory"))
        open(os.path.join(d5, ".claude", "memory", "NAVIGATION.md"), "w", encoding="utf-8").close()
        rc, out = run([], d5)
        check("顶层非对象 JSON（[]）→ exit 0 静默（N1 读侧）", rc == 0 and out == "")

    # —— 宪法陈旧提醒闸（1.0.40 · N-1③）：戳 < 插件版即催升级，独立于队列状态 ——
    def stale_project(stamp):
        d6 = tempfile.mkdtemp()
        os.makedirs(os.path.join(d6, ".claude", "memory"))
        open(os.path.join(d6, ".claude", "memory", "NAVIGATION.md"), "w", encoding="utf-8").close()
        if stamp:
            open(os.path.join(d6, "CLAUDE.md"), "w", encoding="utf-8").write(
                f"# t\n\n<!-- crules-flutter: v{stamp} @ 2026-01-01 -->\n")
        return d6
    d6 = stale_project("1.0.25")   # 旧戳 + 假插件 99.99.99 + **队列空**
    rc, out = run({"hook_event_name": "Stop", "session_id": "stale-1", "stop_hook_active": False}, d6)
    ac = ac_of(out) if out.strip() else ""
    check("旧戳+队列空 → 陈旧提醒仍响（落点 bug 回归钉：不挂队列分支）",
          "宪法版本落后" in ac and "1.0.25" in ac and "99.99.99" in ac and "install.sh" in ac)
    rc2, out2 = run({"hook_event_name": "Stop", "session_id": "stale-1", "stop_hook_active": True}, d6)
    check("stop_hook_active 续轮抑制陈旧提醒（防连环）", out2 == "")
    d7 = stale_project(FAKE_PLUG_VER)   # 戳与插件同版
    rc3, out3 = run({"hook_event_name": "Stop", "session_id": "stale-1", "stop_hook_active": False}, d7)
    check("戳==插件版 → 静默", out3 == "")
    d8 = stale_project(None)            # 无戳（老项目/人工合并态；上方各既有断言的 temp 项目均此态=隐式回归）
    rc4, out4 = run({"hook_event_name": "Stop", "session_id": "stale-1", "stop_hook_active": False}, d8)
    check("无戳 → 静默（无从判不催）", out4 == "")

print(f"stop-reminder fixture: {'全绿' if fails == 0 else f'{fails} 失败'}")
sys.exit(1 if fails else 0)
