#!/usr/bin/env python3
# no-op-gate.py fixture（2026-11-10 no-op 风暴闸，方案 §6.2 自测用例表逐条映射——18 检查；
#   方案档 2026-11-11 轮次化删档，git tag v1.3.7 史可查）：
#   - 匹配面：裸 true/: 计数；复合/绕行形态（true && x、x || true、sleep、/usr/bin/true、true;、TRUE）零计数
#   - 风暴截断：同 sid 300s 计数达 15 后第 16 发 deny（JSON permissionDecision，exit 0——D9 契约）
#   - ask 升级：同窗 deny 5 次后第 21 发转 ask（D8）
#   - 窗口滚动：超窗陈旧计数自然衰减（预置陈旧 state → 新发 allow）
#   - fail-open：坏 JSON state / chmod 000 state → 放行重计（止损闸方向，与 deny-list ask 兜底不同向）
#   - 输入契约：空 stdin（兜底链二次读）/ 非 JSON / 缺 sid / 无记忆库根 → exit 0 静默零落盘
#   - 台账：命中行 cmd/decision/schema/hook 字段（隐私：cmd 恒裸 no-op 字面，零对话正文）
#   - 孤儿清扫：首命中顺带清 >7 天旧 sid 状态档（ledger 不在清扫面）
#   - hooks.json 登记：PreToolUse 第二条 Bash matcher、async:false、timeout、兜底链；deny-list 仍在列
#   - 兜底链端到端（评审发现 1 类捕器）：真实 `python3 … || python …` 链下 JSON deny 幸存、终退码 0
import json
import os
import subprocess
import sys
import tempfile
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "no-op-gate.py")
FAKE_PLUG_VER = "99.99.99"
_FAKE_DIR = tempfile.mkdtemp(prefix="cf-fakeplug.")
os.makedirs(os.path.join(_FAKE_DIR, ".claude-plugin"), exist_ok=True)
with open(os.path.join(_FAKE_DIR, ".claude-plugin", "plugin.json"), "w", encoding="utf-8") as f:
    json.dump({"name": "crules-flutter", "version": FAKE_PLUG_VER}, f)
fails = 0


def check(name, cond):
    global fails
    print(("PASS  " if cond else "FAIL  ") + name)
    if not cond:
        fails += 1


def run(payload, cwd, hook=GATE):
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=_FAKE_DIR)
    p = subprocess.run([sys.executable, hook], input=json.dumps(payload).encode(),
                       capture_output=True, cwd=cwd, env=env)
    return p.returncode, p.stdout.decode()


def run_chain(payload, cwd):
    """u8：宿主真实兜底链形态（评审发现 1 类捕器）——JSON+exit 0 契约下 deny 须幸存"""
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=_FAKE_DIR)
    chain = f'python3 "{GATE}" || python "{GATE}"'
    p = subprocess.run(["bash", "-c", chain], input=json.dumps(payload).encode(),
                       capture_output=True, cwd=cwd, env=env)
    return p.returncode, p.stdout.decode()


def proj():
    d = tempfile.mkdtemp(prefix="cf-noopgate.")
    os.makedirs(os.path.join(d, ".claude", "memory"))
    open(os.path.join(d, ".claude", "memory", "NAVIGATION.md"), "w", encoding="utf-8").close()
    return d


def gdir(d):
    return os.path.join(d, ".claude", "memory", "no-op-gate")


def state_of(d, sid="sA"):
    try:
        with open(os.path.join(gdir(d), sid + ".json"), encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        return None


def ledger_of(d):
    try:
        with open(os.path.join(gdir(d), "ledger.jsonl"), encoding="utf-8") as f:
            return [json.loads(ln) for ln in f if ln.strip()]
    except OSError:
        return None


def payload(d, cmd="true", sid="sA"):
    return {"hook_event_name": "PreToolUse", "tool_name": "Bash", "session_id": sid,
            "cwd": d, "tool_input": {"command": cmd}}


def decision_of(out):
    if not out.strip():
        return ""
    try:
        j = json.loads(out)
        hso = j.get("hookSpecificOutput", {})
        if hso.get("hookEventName") != "PreToolUse":
            return ""
        return hso.get("permissionDecision", "")
    except Exception:
        return ""


def seed_state(d, sid, hits, denies):
    os.makedirs(gdir(d), exist_ok=True)
    with open(os.path.join(gdir(d), sid + ".json"), "w", encoding="utf-8") as f:
        json.dump({"hits": hits, "denies": denies}, f)


# 1. 匹配面：复合/绕行形态零计数零落盘（u2＋诚实边界）
d = proj()
ok1 = True
for c in ("true && ls -la", "git status || true", "sleep 3", "/usr/bin/true",
          "true;", "TRUE", "echo true", "true_thing"):
    rc, out = run(payload(d, c), d)
    ok1 = ok1 and rc == 0 and not out.strip()
check("复合/绕行形态全放行且零记账", ok1
      and (ledger_of(d) in (None, [])) and state_of(d) is None)

# 2. 裸形态全计数（含空白/注释/: 变体）
d = proj()
for c in ("true", "   true   ", "true # idle", ":", ": #x"):
    run(payload(d, c), d)
rows = ledger_of(d) or []
check("裸 true/: 五变体全命中记账（decision=allow）",
      len(rows) == 5 and all(r.get("decision") == "allow" for r in rows))

# 3. 风暴截断：16 连发 → 1-15 allow 静默、第 16 发 deny（D2 归一后口径）
d = proj()
decisions = []
for i in range(16):
    rc, out = run(payload(d), d)
    decisions.append((rc, decision_of(out)))
check("第 16 发起 deny（前 15 发全 allow 静默）",
      all(rc == 0 for rc, _ in decisions)
      and all(dec == "" for _, dec in decisions[:15])
      and decisions[15][1] == "deny")

# 4. deny 文案断言：等待姿势①②＋子代理冲突消解句（D4）
d = proj()
for _ in range(15):
    run(payload(d), d)
rc, out = run(payload(d), d)
check("deny 文案含带超时等待/结束回合/最终回复消解句",
      rc == 0 and "带超时" in out and "结束回合" in out and "最终回复" in out
      and decision_of(out) == "deny")

# 5. ask 升级：16-20 发 deny×5、第 21 发转 ask（D8）
d = proj()
seq = []
for i in range(21):
    rc, out = run(payload(d), d)
    seq.append(decision_of(out))
check("同窗 deny 5 次后第 21 发转 ask",
      all(x == "" for x in seq[:15]) and seq[15:20] == ["deny"] * 5
      and seq[20] == "ask")

# 6. ask 文案人面向断言（16-20 发 deny 后第 21 发）
d = proj()
for _ in range(20):
    run(payload(d), d)
rc, out = run(payload(d), d)
check("ask 文案含人裁字样（由你定）", rc == 0 and decision_of(out) == "ask" and "由你定" in out)

# 7. 窗口滚动：预置 15 个陈旧 hits（>300s）→ 新发 allow 重计（u3）
d = proj()
old = time.time() - 400
seed_state(d, "sA", [old] * 15, [])
rc, out = run(payload(d), d)
st = state_of(d)
check("超窗陈旧计数自然衰减（新发 allow）",
      rc == 0 and decision_of(out) == "" and st is not None and len(st["hits"]) == 1)

# 8. 坏 JSON 状态档 → 放行重计（fail-open；u4 之一）
d = proj()
os.makedirs(gdir(d), exist_ok=True)
with open(os.path.join(gdir(d), "sA.json"), "w", encoding="utf-8") as f:
    f.write("{broken json!!")
rc, out = run(payload(d), d)
st = state_of(d)
check("坏 JSON state 放行且重计", rc == 0 and decision_of(out) == ""
      and st is not None and len(st["hits"]) == 1 and st["denies"] == [])

# 9. chmod 000 状态档 → 放行不崩（fail-open；u4 之二；win32 跳过）
if sys.platform != "win32":
    d = proj()
    os.makedirs(gdir(d), exist_ok=True)
    p = os.path.join(gdir(d), "sA.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump({"hits": [time.time()] * 15, "denies": []}, f)
    os.chmod(p, 0)
    rc, out = run(payload(d), d)
    os.chmod(p, 0o644)
    check("chmod 000 state 放行不崩（stderr 不入 stdout）", rc == 0 and not out.strip())
else:
    check("chmod 000 state（win32 SKIP 视绿）", True)

# 10. 空 stdin → exit 0 静默（兜底链二次读路径，止损闸 fail-open 方向）
d = proj()
env = dict(os.environ, CLAUDE_PLUGIN_ROOT=_FAKE_DIR)
p = subprocess.run([sys.executable, GATE], input=b"", capture_output=True, cwd=d, env=env)
check("空 stdin 静默放行（与 deny-list ask 兜底不同向，头注声明）",
      p.returncode == 0 and not p.stdout.decode().strip())

# 11. 非 JSON stdin → 静默放行
p = subprocess.run([sys.executable, GATE], input=b"not-json{", capture_output=True, cwd=d, env=env)
check("非 JSON stdin 静默放行", p.returncode == 0 and not p.stdout.decode().strip())

# 12. 缺 sid → 不计不拦零落盘
d = proj()
pl = payload(d)
del pl["session_id"]
rc, out = run(pl, d)
check("缺 sid 静默且零状态档", rc == 0 and not out.strip() and state_of(d) is None)

# 13. 无记忆库根 → 静默不介入（Q5 四裁；零落盘）
d = tempfile.mkdtemp(prefix="cf-noopgate-rootless.")
for _ in range(16):
    rc, out = run(payload(d), d)
check("无根工程 16 连发仍全静默零落盘",
      rc == 0 and not out.strip() and not os.path.exists(os.path.join(d, ".claude")))

# 14. 跨 sid 不互扰（u5）
d = proj()
for _ in range(10):
    run(payload(d, sid="sA"), d)
    run(payload(d, sid="sB"), d)
rc1, o1 = run(payload(d, sid="sA"), d)
check("跨 sid 各自计数互不累计（各 11 发仍 allow）",
      rc1 == 0 and decision_of(o1) == ""
      and os.path.exists(os.path.join(gdir(d), "sA.json"))
      and os.path.exists(os.path.join(gdir(d), "sB.json")))

# 15. 台账行字段（隐私：cmd 恒裸 no-op 字面）
d = proj()
run(payload(d), d)
run(payload(d, ":"), d)
rows = ledger_of(d)
check("台账行 schema/hook/cmd/decision 字段齐",
      rows and all(r.get("schema") == 1 and r.get("hook") == "no-op-gate"
                   and r.get("cmd") in ("true", ":") and r.get("decision") == "allow"
                   and r.get("sid") == "sA" for r in rows))

# 16. 孤儿清扫：首命中顺带清 >7 天旧档、ledger 不在清扫面
d = proj()
os.makedirs(gdir(d), exist_ok=True)
oldf = os.path.join(gdir(d), "zz-old.json")
open(oldf, "w", encoding="utf-8").close()
os.utime(oldf, (time.time() - 8 * 86400,) * 2)
led = os.path.join(gdir(d), "ledger.jsonl")
open(led, "w", encoding="utf-8").write("")  # 空 ledger 亦不在清扫面
os.utime(led, (time.time() - 8 * 86400,) * 2)
run(payload(d, sid="sFRESH"), d)
check("孤儿清扫：>7 天 sid 档被清、ledger 保留",
      not os.path.exists(oldf) and os.path.exists(led))

# 17. hooks.json 登记（PreToolUse 第二条 Bash matcher、async:false、timeout、兜底链；deny-list 仍在列）
with open(os.path.join(HERE, "hooks.json"), encoding="utf-8") as f:
    hj = json.load(f)
pre = hj.get("hooks", {}).get("PreToolUse", [])
bash_entries = [e for e in pre if e.get("matcher") == "Bash"]
gate_entry = next((e for e in bash_entries
                   if any("no-op-gate.py" in h.get("command", "") for h in e.get("hooks", []))), None)
deny_entry = next((e for e in bash_entries
                   if any("deny-list.py" in h.get("command", "") for h in e.get("hooks", []))), None)
gcmd = gate_entry["hooks"][0] if gate_entry else {}
check("hooks.json 登记：no-op-gate 第二条 Bash（async:false/timeout/兜底链）且 deny-list 仍在列",
      gate_entry is not None and deny_entry is not None
      and gcmd.get("async") is False and "timeout" in gcmd
      and "||" in gcmd.get("command", "")
      and bash_entries.index(deny_entry) < bash_entries.index(gate_entry))

# 18. 兜底链端到端（u8；评审发现 1 类捕器）：真实 || 链下 JSON deny 幸存、终退码 0
d = proj()
for _ in range(15):
    run(payload(d), d)
rc, out = run_chain(payload(d), d)
check("兜底链端到端：JSON deny 幸存且终退码 0（禁 exit 2 契约）",
      rc == 0 and decision_of(out) == "deny")

print(f"\n{'ALL GREEN' if fails == 0 else str(fails) + ' FAIL'}")
sys.exit(1 if fails else 0)
