#!/usr/bin/env python3
# compact-gate.py / compact-gate-decision.py fixture（2026-11-09 会话压缩计数闸，方案
#   docs/方案-会话压缩计数闸-2026-11-09.md §6.2 自测用例表逐条映射——逻辑用例十行＋hooks.json
#   登记断言＋哨兵/回传通道（Q9①）＋跨件集成（mute→静默）＋变异抽查锁两枚（classify 优先级／坏 state 重计））：
#   - 计数阶梯：第 1 次观测注入／≥2 次无 marker 人裁注入／第 3 次起无 marker 仍问（放行一次语义）
#   - marker 生效 → 静默但 ledger 行照落（判据 3 记账不断流）
#   - clear/startup → 删该 sid 计数与 marker；startup 顺带清扫 >7 天孤儿 sid 文件
#   - 坏输入/缺 sid/source 未知 → exit 0 不计不注（防空串回落共享计数文件互染）
#   - decision 件：非自家弹窗哨兵先核毫秒级快退零写面；自家 → tool_response.answers 裁决列回填，
#     「不再提醒」落 marker；answers 异型 → verdict=unparsed 如实记账
#   - hooks.json 登记：SessionStart matcher 裸 `compact|clear|startup`（\| 转义形永不匹配——防呆）、
#     PostToolUse(AskUserQuestion)、python3||python 兜底链
# 隐私对齐 compliance-audit：账行只落计数/布尔/裁决枚举/sid——零对话正文。
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
GATE = os.path.join(HERE, "compact-gate.py")
DECISION = os.path.join(HERE, "compact-gate-decision.py")
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


def run(hook, payload, cwd):
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=_FAKE_DIR)
    p = subprocess.run([sys.executable, hook], input=json.dumps(payload).encode(),
                       capture_output=True, cwd=cwd, env=env)
    return p.returncode, p.stdout.decode()


def proj():
    """带记忆库的临时消费工程（find_project_root 定根前提）"""
    d = tempfile.mkdtemp(prefix="cf-cgate.")
    os.makedirs(os.path.join(d, ".claude", "memory"))
    open(os.path.join(d, ".claude", "memory", "NAVIGATION.md"), "w", encoding="utf-8").close()
    return d


def gdir(d):
    return os.path.join(d, ".claude", "memory", "compact-gate")


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


def compact_payload(d, sid="sA", source="compact"):
    return {"hook_event_name": "SessionStart", "session_id": sid,
            "source": source, "cwd": d}


def ac_of(out):
    if not out.strip():
        return ""
    j = json.loads(out)
    hso = j.get("hookSpecificOutput", {})
    if hso.get("hookEventName") != "SessionStart":
        return ""
    return hso.get("additionalContext", "")


# —— 阶梯与注入（§6.2 逻辑用例 1–3） ——
d = proj()
rc, out = run(GATE, compact_payload(d), d)
ok = rc == 0 and "第 1 次" in ac_of(out) and "上限 2 次" in ac_of(out) and len(ac_of(out)) <= 300
st, led = state_of(d), ledger_of(d)
ok = ok and st and st.get("count") == 1 and not st.get("marker")
ok = ok and led and len(led) == 1 and led[0].get("event") == "compact-1st" \
    and led[0].get("count") == 1 and led[0].get("verdict") is None \
    and led[0].get("sid") == "sA" and led[0].get("plugin_ver") == FAKE_PLUG_VER
check("compact 第 1 次 → 观测注入（≤300 字符）＋计数=1＋ledger 行·未裁决", ok)

rc, out = run(GATE, compact_payload(d), d)
ok = rc == 0 and "已达同任务上限" in ac_of(out) and "[compact-gate]" in ac_of(out) \
    and "放行一次并记账" in ac_of(out) and "落快照后重开" in ac_of(out) and "不再提醒" in ac_of(out) \
    and "先落断点快照" in ac_of(out) and "完整路径" in ac_of(out) \
    and len(ac_of(out)) <= 300
st, led = state_of(d), ledger_of(d)
ok = ok and st and st.get("count") == 2 and led and len(led) == 2 \
    and led[1].get("event") == "compact-nth" and led[1].get("count") == 2
check("compact 第 2 次 → 人裁注入（三选项＋哨兵前缀＋先落快照指令）＋计数=2", ok)

rc, out = run(GATE, compact_payload(d), d)
ok = rc == 0 and "已达同任务上限" in ac_of(out)
st, led = state_of(d), ledger_of(d)
ok = ok and st and st.get("count") == 3 and led and len(led) == 3
check("compact 第 3 次·无 marker → 仍人裁注入（放行一次语义）＋计数=3", ok)
d = None  # mkdtemp 不随进程回收：cf- 前缀留残骸可寻（house 惯例，test-self 同款），OS tmp 清理兜底——下组另起新工程

# —— marker 生效 → 静默＋记账不断流（判据 3，§6.2 用例 4） ——
d2 = proj()
os.makedirs(gdir(d2), exist_ok=True)
with open(os.path.join(gdir(d2), "sB.json"), "w", encoding="utf-8") as f:
    json.dump({"count": 2, "marker": True}, f)
rc, out = run(GATE, compact_payload(d2, sid="sB"), d2)
ok = rc == 0 and ac_of(out) == ""
st, led = state_of(d2, "sB"), ledger_of(d2)
ok = ok and st and st.get("count") == 3 and led and len(led) == 1 \
    and led[0].get("event") == "compact-muted" and led[0].get("verdict") is None
check("marker 生效 → 静默＋ledger 行照落（记账不断流）", ok)

# —— clear / startup 清零与孤儿清扫（§6.2 用例 8–9） ——
rc, out = run(GATE, compact_payload(d2, sid="sB", source="clear"), d2)
ok = rc == 0 and ac_of(out) == "" and state_of(d2, "sB") is None and ledger_of(d2) and len(ledger_of(d2)) == 1
check("SessionStart(clear) → 删该 sid 计数与 marker、零注入、不记账", ok)

now = time.time()
for sid, age in (("sB", 8 * 86400), ("sC", 3600), ("sD", 6 * 86400)):
    with open(os.path.join(gdir(d2), sid + ".json"), "w", encoding="utf-8") as f:
        json.dump({"count": 1, "marker": False}, f)
    os.utime(os.path.join(gdir(d2), sid + ".json"), (now - age, now - age))
rc, out = run(GATE, compact_payload(d2, sid="sE", source="startup"), d2)
ok = rc == 0 and ac_of(out) == ""
ok = ok and state_of(d2, "sB") is None and state_of(d2, "sC") is not None \
    and state_of(d2, "sD") is not None and state_of(d2, "sE") is None
ok = ok and os.path.exists(os.path.join(gdir(d2), "ledger.jsonl"))   # 清扫不误删 ledger
check("SessionStart(startup) → 清零＋清扫 >7 天孤儿 sid 文件（6 天/1 小时保留、ledger 不动）", ok)

# —— 坏输入 / 缺 sid / 未知 source（§6.2 用例 10＋防呆） ——
d3 = proj()
p = subprocess.run([sys.executable, GATE], input=b"not-json", capture_output=True, cwd=d3)
check("非法 JSON → exit 0 静默零写面", p.returncode == 0 and p.stdout == b"" and ledger_of(d3) is None)
rc, out = run(GATE, {k: v for k, v in compact_payload(d3).items() if k != "session_id"}, d3)
ok = rc == 0 and ac_of(out) == "" and ledger_of(d3) is None and not os.path.exists(gdir(d3))
check("缺 session_id → exit 0 不计不注（防空串共享计数文件互染）", ok)
rc, out = run(GATE, compact_payload(d3, source="resume"), d3)
ok = rc == 0 and ac_of(out) == "" and ledger_of(d3) is None
rc2, out2 = run(GATE, {**compact_payload(d3), "source": None}, d3)
ok = ok and rc2 == 0 and ac_of(out2) == "" and ledger_of(d3) is None
check("source=resume/缺失 → 防御性不计数（matcher 已排除 resume，双保险）", ok)

# —— decision 件（Q9① 回传通道，§4 组件表） ——
QTEXT = "[compact-gate] 第 2 次压缩，已达同任务上限（2 次）。如何处置？"


def decision_payload(d, answers, qtext=QTEXT, sid="sX"):
    return {"hook_event_name": "PostToolUse", "session_id": sid, "cwd": d,
            "tool_name": "AskUserQuestion",
            "tool_input": {"questions": [{"question": qtext, "header": "压缩闸",
                                          "options": [], "multiSelect": False}]},
            "tool_response": {"answers": answers}}


d4 = proj()
# 非自家弹窗：哨兵先核 → 毫秒级快退零写面
rc, out = run(DECISION, decision_payload(d4, {"普通问题？": "选项一"}, qtext="普通问题？"), d4)
ok = rc == 0 and ac_of(out) == "" and ledger_of(d4) is None and not os.path.exists(gdir(d4))
check("decision 非自家（无哨兵前缀）→ 快退 exit 0 零写面", ok)

# 生产可达序先垫底：两次 compact 使 count=2（裁决只发生在人裁注入之后）
run(GATE, compact_payload(d4, sid="sX"), d4)
run(GATE, compact_payload(d4, sid="sX"), d4)
# 自家 · 不再提醒 → marker 落盘＋裁决列回填
rc, out = run(DECISION, decision_payload(d4, {QTEXT: {"answer": "本任务不再提醒"}}), d4)
st, led = state_of(d4, "sX"), ledger_of(d4)
ok = rc == 0 and st and st.get("marker") is True and st.get("count") == 2 \
    and led and len(led) == 3 and led[2].get("event") == "decision" \
    and led[2].get("verdict") == "mute"
check("decision 自家·不再提醒（answers 值为 dict 形）→ marker 落盘＋verdict=mute", ok)

# 静默端到端集成：marker 后第 3 次 compact → 静默＋记账不断流（mute 语义跨件闭环）
rc, out = run(GATE, compact_payload(d4, sid="sX"), d4)
led = ledger_of(d4)
ok = rc == 0 and ac_of(out) == "" and led and led[-1].get("event") == "compact-muted" \
    and led[-1].get("count") == 3 and len(led) == 4
check("集成：decision 落 marker 后同 sid compact → 静默＋记账", ok)

# 自家 · 放行一次 → 无 marker、下次仍问（同样走生产可达序）
d5 = proj()
run(GATE, compact_payload(d5, sid="sX"), d5)
run(GATE, compact_payload(d5, sid="sX"), d5)
rc, out = run(DECISION, decision_payload(d5, {QTEXT: "放行一次并记账"}), d5)
st, led = state_of(d5, "sX"), ledger_of(d5)
ok = rc == 0 and st and not st.get("marker") and st.get("count") == 2 \
    and led and led[2].get("verdict") == "continue"
rc, out = run(GATE, compact_payload(d5, sid="sX"), d5)
ok = ok and "已达同任务上限" in ac_of(out)
check("decision 自家·放行一次 → verdict=continue 无 marker，下次 compact 仍人裁注入", ok)

# 自家 · 重开 → verdict=reopen 无 marker
d6 = proj()
rc, out = run(DECISION, decision_payload(d6, {QTEXT: "落快照后重开"}), d6)
led = ledger_of(d6)
ok = rc == 0 and led and led[0].get("verdict") == "reopen" and not (state_of(d6, "sX") or {}).get("marker")
check("decision 自家·重开 → verdict=reopen 无 marker", ok)

# answers 异型 / 缺失 → unparsed 如实记账，不崩不误标 marker
d7 = proj()
rc, out = run(DECISION, {**decision_payload(d7, {}), "tool_response": "格式异常"}, d7)
led = ledger_of(d7)
ok = rc == 0 and led and led[0].get("verdict") == "unparsed"
rc2, out2 = run(DECISION, decision_payload(d7, {}), d7)   # answers 空对象
led = ledger_of(d7)
ok = ok and rc2 == 0 and len(led) == 2 and led[1].get("verdict") == "unparsed"
check("decision answers 异型/无对应键 → verdict=unparsed 零 marker", ok)

# tool_input 非预期形状（questions 缺/非列表）→ 快退不崩（另起新工程隔离账面）
d8 = proj()
rc, out = run(DECISION, {**decision_payload(d8, {}), "tool_input": {"questions": "坏形"}}, d8)
ok = rc == 0 and ledger_of(d8) is None and not os.path.exists(gdir(d8))
check("decision tool_input 坏形 → 哨兵不中快退零写面", ok)

# —— decision snap_ok 机械核（1.3.5 续期批：判据 2 量法机械化——问题文本取路径，mtime 对账末次压缩行） ——
d11 = proj()
run(GATE, compact_payload(d11, sid="sP"), d11)
run(GATE, compact_payload(d11, sid="sP"), d11)
snap = os.path.join(d11, "snapshot.md")
QP = "[compact-gate] 第 2 次压缩。断点快照已落 " + snap + " 。如何处置？"
open(snap, "w", encoding="utf-8").close()   # mtime=现在 ≥ 末次压缩行 → true
rc, out = run(DECISION, decision_payload(d11, {QP: "放行一次并记账"}, qtext=QP, sid="sP"), d11)
led = ledger_of(d11)
ok = rc == 0 and led and led[-1].get("verdict") == "continue" and led[-1].get("snap_ok") is True
check("decision 快照新鲜（mtime ≥ 末次压缩行）→ snap_ok=true", ok)

os.utime(snap, (now - 3 * 3600, now - 3 * 3600))   # 陈旧 3h（早于末次压缩行）→ false 谎报显形
rc, out = run(DECISION, decision_payload(d11, {QP: "放行一次并记账"}, qtext=QP, sid="sP"), d11)
led = ledger_of(d11)
ok = rc == 0 and led and led[-1].get("snap_ok") is False
check("decision 快照陈旧（mtime < 末次压缩行）→ snap_ok=false（谎报显形）", ok)

QN = "[compact-gate] 第 2 次压缩。如何处置？"   # 无路径 → null 不猜
rc, out = run(DECISION, decision_payload(d11, {QN: "放行一次并记账"}, qtext=QN, sid="sP"), d11)
led = ledger_of(d11)
ok = rc == 0 and led and led[-1].get("snap_ok") is None
check("decision 问题无快照路径 → snap_ok=null（不猜）", ok)

# —— 变异抽查锁（2026-11-09 评审点名两缺口） ——
# ① classify 子串优先级：答案同命中「不再提醒」＋「放行」→ mute 优先（mute>reopen>continue 换序即红）
d9 = proj()
run(GATE, compact_payload(d9, sid="sY"), d9)
run(GATE, compact_payload(d9, sid="sY"), d9)
rc, out = run(DECISION, decision_payload(d9, {QTEXT: "不放行了，本任务不再提醒"}, qtext=QTEXT, sid="sY"), d9)
led = ledger_of(d9)
ok = rc == 0 and led and led[2].get("verdict") == "mute" \
    and (state_of(d9, "sY") or {}).get("marker") is True
check("classify 优先级：答案同命中「不再提醒」＋「放行」→ mute 优先", ok)

# ② gate 坏 state 文件（坏 JSON）→ load_state 回落从 0 重计走观测档，不崩不误档
d10 = proj()
os.makedirs(gdir(d10), exist_ok=True)
with open(os.path.join(gdir(d10), "sZ.json"), "w", encoding="utf-8") as f:
    f.write("{corrupt json")
rc, out = run(GATE, compact_payload(d10, sid="sZ"), d10)
st, led = state_of(d10, "sZ"), ledger_of(d10)
ok = rc == 0 and "第 1 次" in ac_of(out) and st and st.get("count") == 1 \
    and led and len(led) == 1 and led[0].get("event") == "compact-1st"
check("gate 坏 state 文件（坏 JSON）→ 从 0 重计走观测档", ok)

# —— hooks.json 登记断言（防呆：matcher 裸竖线；python3||python 兜底链） ——
with open(os.path.join(HERE, "hooks.json"), encoding="utf-8") as f:
    hj_raw = f.read()
try:
    hj = json.loads(hj_raw).get("hooks", {})
except Exception:
    hj = {}
ss = hj.get("SessionStart") or []
pt = hj.get("PostToolUse") or []
ss_m = [e.get("matcher") for e in ss]
pt_m = [e.get("matcher") for e in pt]
check("hooks.json SessionStart matcher＝裸 compact|clear|startup（\\| 转义形永不匹配——防呆）",
      "compact|clear|startup" in ss_m and "compact\\|clear\\|startup" not in hj_raw.replace("\\\\", "\\"))
check("hooks.json PostToolUse 含 AskUserQuestion 登记且指向 compact-gate-decision.py",
      "AskUserQuestion" in pt_m
      and any("compact-gate-decision.py" in h.get("command", "")
              for e in pt if e.get("matcher") == "AskUserQuestion" for h in e.get("hooks", [])))
new_hooks = [h for e in ss + pt
             if e.get("matcher") in ("compact|clear|startup", "AskUserQuestion")
             for h in e.get("hooks", [])]
check("新两件均 python3||python 兜底链（Windows 无 python3 静默失效先例同款）",
      len(new_hooks) == 2 and all("|| python " in h.get("command", "") for h in new_hooks))

print(f"compact-gate fixture: {'全绿' if fails == 0 else f'{fails} 失败'}")
sys.exit(1 if fails else 0)
