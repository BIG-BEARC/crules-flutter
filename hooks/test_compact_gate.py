#!/usr/bin/env python3
# compact-gate.py / compact-observe.py fixture（压缩恢复 v2 · 2026-11-12，方案 docs/方案-压缩恢复v2-
#   指针与速率-2026-11-12.md §6.2——两轮评审 30 发现全处置后的 v4 终裁形；v1 阶梯/marker/哨兵回传面
#   随 Q3「即拆」整体退役，本夹具同步改写——改写清单见方案 §4.4）：
#   - 指针注入（D3）：每次压缩注入 transcript 指针＋span 直取纪律；路径三级降级（输入字段→cwd+sid
#     推导＋mtime 弱校验→projects 目录通用指引）
#   - 计数仲裁（§4.1，二轮 #1 L1）：去重谓词＝同 sid 同 prompt_id 即同发（ts 近邻 ≤120s 仅 fallback，
#     适用于 prompt_id 缺失/不等）；fixtures 挂方案两用例——同 prompt_id 远隔（>300s）去重、
#     异 prompt_id 175s 双计；degrade-A 组合（PreCompact=unknown＋SessionStart 去重）防谓词回归
#   - 速率窗（D4/Q4/Q10）：主窗 auto_ts ≥4/90min；混桶 any_ts ≥8/90min（sidechain 主线程无键的
#     现行走档）；manual 记账不入窗；sub_ts ≥20/24h 只记账（runaway-sub）不注入（D7）
#   - 再武装（评审 #6/二轮 #3）：回落半阈复位＋滚动 24h 上限 2 次（载体 runaway_ts＋rearmed）
#   - 回读通道（§2）：startup 翻账——runaway 或任一 sid ≥3 发/24h → 上次断点指针一行＋handoff 账行
#   - clear 顺带清窗（D5 依赖解除）；startup 孤儿清扫 >7d；v1 形 {count,marker} 状态容忍（评审 #7）
#   - 退役面（Q3）：compact-gate-decision.py 应不存在；hooks.json 应无 AskUserQuestion 条目；
#     PreCompact 单条无 matcher 登记（探针实证：catchall 与专属条同事件并发＝双登记即同发双行）
#   - 隐私（D6）：账行零正文零路径——断言行内无 transcript_path 键、无工程路径子串
import json
import os
import re
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
OBSERVE = os.path.join(HERE, "compact-observe.py")
DECISION = os.path.join(HERE, "compact-gate-decision.py")
FAKE_PLUG_VER = "99.99.99"
_FAKE_DIR = tempfile.mkdtemp(prefix="cf-fakeplug.")
os.makedirs(os.path.join(_FAKE_DIR, ".claude-plugin"), exist_ok=True)
with open(os.path.join(_FAKE_DIR, ".claude-plugin", "plugin.json"), "w", encoding="utf-8") as f:
    json.dump({"name": "crules-flutter", "version": FAKE_PLUG_VER}, f)
fails = 0
_seq = [0]


def check(name, cond):
    global fails
    print(("PASS  " if cond else "FAIL  ") + name)
    if not cond:
        fails += 1


def run(hook, payload, cwd, cfg_dir=None):
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=_FAKE_DIR)
    if cfg_dir:
        env["CLAUDE_CONFIG_DIR"] = cfg_dir
    else:
        env.pop("CLAUDE_CONFIG_DIR", None)
    p = subprocess.run([sys.executable, hook], input=json.dumps(payload).encode(),
                       capture_output=True, cwd=cwd, env=env)
    return p.returncode, p.stdout.decode()


def proj():
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


def put_state(d, sid, st):
    os.makedirs(gdir(d), exist_ok=True)
    with open(os.path.join(gdir(d), sid + ".json"), "w", encoding="utf-8") as f:
        json.dump(st, f)


def ledger_of(d):
    try:
        with open(os.path.join(gdir(d), "ledger.jsonl"), encoding="utf-8") as f:
            return [json.loads(ln) for ln in f if ln.strip()]
    except OSError:
        return None


def iso(epoch):
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(epoch))


def put_ledger(d, rows):
    os.makedirs(gdir(d), exist_ok=True)
    with open(os.path.join(gdir(d), "ledger.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def gate_payload(d, sid="sA", source="compact", prompt_id=None, tpath=None):
    p = {"hook_event_name": "SessionStart", "session_id": sid,
         "source": source, "cwd": d}
    if prompt_id is not None:
        p["prompt_id"] = prompt_id
    if tpath is not None:
        p["transcript_path"] = tpath
    return p


def obs_payload(d, sid="sA", trigger=None, prompt_id=None, sidechain=...):
    p = {"hook_event_name": "PreCompact", "session_id": sid, "cwd": d}
    if trigger is not None:
        p["trigger"] = trigger
    if prompt_id is not None:
        p["prompt_id"] = prompt_id
    if sidechain is not ...:
        p["sidechain"] = sidechain
    return p


def ac_of(out):
    if not out.strip():
        return ""
    try:
        j = json.loads(out)
    except Exception:
        return ""
    hso = j.get("hookSpecificOutput", {})
    if hso.get("hookEventName") != "SessionStart":
        return ""
    return hso.get("additionalContext", "")


def compacts(led, sid):
    return [r for r in (led or [])
            if isinstance(r, dict) and r.get("sid") == sid and r.get("event") == "compact"]


def san(d):
    """Claude Code 实际净化规则（1.3.9 修正依据）：路径全非字母数字转横线，不止斜线——
    生产双证：super_printer → super-printer、.git/modules → --git-modules-"""
    return re.sub(r"[^A-Za-z0-9]", "-", d)


def cfg_for(d):
    """CLAUDE_CONFIG_DIR 伪家居：projects/<sanitized-root>/ 可造 transcript"""
    c = tempfile.mkdtemp(prefix="cf-cfg.")
    os.makedirs(os.path.join(c, "projects", san(d)), exist_ok=True)
    return c


def make_transcript(d, cfg, sid):
    p = os.path.join(cfg, "projects", san(d), sid + ".jsonl")
    with open(p, "w", encoding="utf-8") as f:
        f.write('{"probe":true}\n')
    return p


NOW = time.time()

# —— 指针注入＋degrade-B 独立记账（§4.2 矩阵末行，D3 文案） ——
d = proj()
tp = os.path.join(d, "t.jsonl")
open(tp, "w", encoding="utf-8").close()
rc, out = run(GATE, gate_payload(d, tpath=tp), d)
ac = ac_of(out)
ok = rc == 0 and "[compact-recovery]" in ac and "第 1 次压缩" in ac \
    and "trigger: unknown" in ac and tp in ac and "勿整文件回读" in ac and len(ac) <= 500
led = ledger_of(d)
ok = ok and led and len(led) == 1 and led[0].get("schema") == 2 \
    and led[0].get("event") == "compact" and led[0].get("trigger") == "unknown" \
    and led[0].get("sidechain") is None and led[0].get("hook") == "compact-gate" \
    and led[0].get("prompt_id") is None and led[0].get("plugin_ver") == FAKE_PLUG_VER
st = state_of(d)
ok = ok and st and len(st.get("any_ts") or []) == 1 and st.get("auto_ts") == [] \
    and st.get("sub_ts") == [] and st.get("rearmed") is True
check("compact 首发（degrade-B）→ 指针注入（L1 输入路径）＋schema2 行＋any_ts 窗=1", ok)

rc, out = run(GATE, gate_payload(d, prompt_id="p2", tpath=tp), d)
ok = rc == 0 and "第 2 次压缩" in ac_of(out) and len(compacts(ledger_of(d), "sA")) == 2
check("序号由 ledger 推导（第 2 发 N=2，阶梯语义退役——文案同形）", ok)

# —— 路径三级降级（§4.1） ——
d2 = proj()
cfg = cfg_for(d2)
tp2 = make_transcript(d2, cfg, "sA")
rc, out = run(GATE, gate_payload(d2), d2, cfg_dir=cfg)   # 无 transcript_path 字段 → L2 推导
ok = rc == 0 and tp2 in ac_of(out)
check("路径 L2：无输入字段 → cwd+sid 推导＋存在性核验命中", ok)

d3 = proj()
cfg3 = cfg_for(d3)   # projects 目录在、该 sid 文件缺 → L3 通用指引
rc, out = run(GATE, gate_payload(d3), d3, cfg_dir=cfg3)
ac3 = ac_of(out)
ok = rc == 0 and "projects" in ac3 and ".jsonl" not in ac3
check("路径 L3：推导未命中 → projects 目录通用指引（不猜具体路径）", ok)

# —— 路径 L2 净化修正（1.3.9：super_printer 实弹根含 _ 推导 miss 溯源；v1 夹具与实现
#    共用 replace("/","-") 同错——夹具改按 Claude Code 真实净化规则造家居，红→修→绿） ——
d6u = os.path.join(tempfile.mkdtemp(prefix="cf-cgate."), "super_printer")   # 根含 _ 与 .
os.makedirs(os.path.join(d6u, ".claude", "memory"))   # 定根脚手架（find_project_root 判据）
open(os.path.join(d6u, ".claude", "memory", "NAVIGATION.md"), "w", encoding="utf-8").close()
cfg6 = cfg_for(d6u)
tp6 = make_transcript(d6u, cfg6, "sA")
rc, out = run(GATE, gate_payload(d6u), d6u, cfg_dir=cfg6)   # 无 transcript_path → L2 推导
ok = rc == 0 and tp6 in ac_of(out)
check("路径 L2（净化修正）：根含 _/. → 全非字母数字转横线后命中（startup 回读同路同修）", ok)

# —— PreCompact 观测件（§4.2：零拦截零注入，记账＋入窗） ——
d4 = proj()
rc, out = run(OBSERVE, obs_payload(d4, trigger="manual", prompt_id="m1"), d4)
led = ledger_of(d4)
st = state_of(d4)
ok = rc == 0 and out == "" and led and len(led) == 1 \
    and led[0].get("trigger") == "manual" and led[0].get("hook") == "compact-observe" \
    and led[0].get("event") == "compact" and led[0].get("n_window") is None \
    and st and st.get("auto_ts") == [] and st.get("any_ts") == [] and st.get("sub_ts") == []
check("PreCompact manual → 零 stdout＋schema2 行（trigger=manual）＋不入窗（桶语义修正）", ok)

rc, out = run(OBSERVE, obs_payload(d4, trigger="auto", prompt_id="m2"), d4)
led, st = ledger_of(d4), state_of(d4)
ok = rc == 0 and out == "" and compacts(led, "sA")[-1].get("trigger") == "auto" \
    and compacts(led, "sA")[-1].get("n_window") == 1 and len(st.get("any_ts") or []) == 1
check("PreCompact auto（sidechain 无键＝混桶现行走档）→ any_ts 入窗 n_window=1", ok)

rc, out = run(OBSERVE, obs_payload(d4, trigger="auto", prompt_id="m3", sidechain=True), d4)
led, st = ledger_of(d4), state_of(d4)
ok = rc == 0 and compacts(led, "sA")[-1].get("sidechain") is True \
    and len(st.get("sub_ts") or []) == 1 and len(st.get("any_ts") or []) == 1
check("PreCompact sidechain=true（a 路保留）→ sub_ts 桶", ok)

p = subprocess.run([sys.executable, OBSERVE], input=b"not-json", capture_output=True, cwd=d4)
ok = p.returncode == 0 and p.stdout == b"" and len(compacts(ledger_of(d4), "sA")) == 3
d5 = proj()
rc2, out2 = run(OBSERVE, {k: v for k, v in obs_payload(d5).items() if k != "session_id"}, d5)
ok = ok and rc2 == 0 and out2 == "" and ledger_of(d5) is None and not os.path.exists(gdir(d5))
check("PreCompact 坏 JSON/缺 sid → exit 0 零写面（fail-open 同款）", ok)

# —— 计数仲裁（§4.1：prompt_id 身份谓词＋ts fallback；fixtures 两用例＋degrade-A） ——
d6 = proj()
run(OBSERVE, obs_payload(d6, trigger="auto", prompt_id="P1"), d6)
rc, out = run(GATE, gate_payload(d6, prompt_id="P1"), d6)
led, st = ledger_of(d6), state_of(d6)
ok = rc == 0 and "trigger: auto" in ac_of(out) and len(compacts(led, "sA")) == 1 \
    and len(st.get("any_ts") or []) == 1
check("主路径去重：PreCompact(P1,auto)→SessionStart(P1) → 单行单入窗＋注入携 trigger=auto", ok)

d7 = proj()
run(OBSERVE, obs_payload(d7, prompt_id="P2"), d7)   # trigger 字段缺＝degrade-A
rc, out = run(GATE, gate_payload(d7, prompt_id="P2"), d7)
led = ledger_of(d7)
ok = rc == 0 and "trigger: unknown" in ac_of(out) and len(compacts(led, "sA")) == 1
check("degrade-A 组合：PreCompact=unknown＋SessionStart 同 prompt_id → 去重仍中（谓词不看 trigger）", ok)

d8 = proj()
rows = [{"schema": 2, "ts": iso(NOW - 600), "sid": "sA", "trigger": "auto",
         "sidechain": None, "event": "compact", "n_window": 1,
         "plugin_ver": FAKE_PLUG_VER, "hook": "compact-observe", "prompt_id": "PX"}]
put_ledger(d8, rows)
put_state(d8, "sA", {"auto_ts": [], "any_ts": [NOW - 600], "sub_ts": [], "runaway_ts": [], "rearmed": True})
rc, out = run(GATE, gate_payload(d8, prompt_id="PX"), d8)
ok = rc == 0 and len(compacts(ledger_of(d8), "sA")) == 1 and len(state_of(d8).get("any_ts") or []) == 1
check("同 prompt_id 远隔（>300s）→ 去重（身份谓词不受间隔影响——方案用例①）", ok)

d9 = proj()
rows = [{"schema": 2, "ts": iso(NOW - 175), "sid": "sA", "trigger": "auto",
         "sidechain": None, "event": "compact", "n_window": 1,
         "plugin_ver": FAKE_PLUG_VER, "hook": "compact-observe", "prompt_id": "PA"}]
put_ledger(d9, rows)
put_state(d9, "sA", {"auto_ts": [], "any_ts": [NOW - 175], "sub_ts": [], "runaway_ts": [], "rearmed": True})
rc, out = run(GATE, gate_payload(d9, prompt_id="PB"), d9)
ok = rc == 0 and len(compacts(ledger_of(d9), "sA")) == 2 \
    and len(state_of(d9).get("any_ts") or []) == 2
check("异 prompt_id 175s → 双计（fallback 窗 120s 外——方案用例②，最短发间隔不误并）", ok)

d10 = proj()
rows = [{"schema": 2, "ts": iso(NOW - 30), "sid": "sA", "trigger": "auto",
         "sidechain": None, "event": "compact", "n_window": 1,
         "plugin_ver": FAKE_PLUG_VER, "hook": "compact-observe"}]   # 旧行无 prompt_id 键
put_ledger(d10, rows)
put_state(d10, "sA", {"auto_ts": [], "any_ts": [NOW - 30], "sub_ts": [], "runaway_ts": [], "rearmed": True})
rc, out = run(GATE, gate_payload(d10), d10)   # 输入也无 prompt_id → fallback 生效
ok = rc == 0 and len(compacts(ledger_of(d10), "sA")) == 1 and len(state_of(d10).get("any_ts") or []) == 1
check("prompt_id 双缺 → ts 近邻 fallback（≤120s）去重中", ok)

# —— 速率窗（D4/Q4/Q10：混桶 ≥8、主窗 ≥4、manual 不入窗、sub 只记账） ——
d11 = proj()
tp11 = os.path.join(d11, "t.jsonl")
open(tp11, "w", encoding="utf-8").close()
for i in range(7):   # 7 发 auto 对（混桶 7 < 8）
    run(OBSERVE, obs_payload(d11, trigger="auto", prompt_id=f"a{i}"), d11)
rc, out = run(GATE, gate_payload(d11, prompt_id="a6", tpath=tp11), d11)
ok = rc == 0 and "速率异常" not in ac_of(out) \
    and not any(r.get("event") == "runaway" for r in ledger_of(d11) or [])
check("混桶 7 发/90min → 不触（≥8 占位阈——b5ae44d8 峰值 ~7 不误报）", ok)

run(OBSERVE, obs_payload(d11, trigger="auto", prompt_id="a7"), d11)
rc, out = run(GATE, gate_payload(d11, prompt_id="a7", tpath=tp11), d11)
ac11 = ac_of(out)
led11, st11 = ledger_of(d11), state_of(d11)
rw = [r for r in led11 if r.get("event") == "runaway"]
ok = rc == 0 and "速率异常" in ac11 and "窗内 8 发" in ac11 and "落终态" in ac11 \
    and len(rw) == 1 and rw[0].get("n_window") == 8 \
    and len(st11.get("runaway_ts") or []) == 1 and st11.get("rearmed") is False
check("混桶第 8 发 → 速率告警叠加＋runaway 账行＋runaway_ts 记载＋rearmed 卸载", ok)

for i in (8, 9):   # 未回落连发 → 不重触
    run(OBSERVE, obs_payload(d11, trigger="auto", prompt_id=f"a{i}"), d11)
    rc, out = run(GATE, gate_payload(d11, prompt_id=f"a{i}", tpath=tp11), d11)
led11 = ledger_of(d11)
ok = len([r for r in led11 if r.get("event") == "runaway"]) == 1 \
    and "速率异常" not in ac_of(out)
check("触发后未回落（窗 9-10 发）→ 不重触（防 b5ae44d8 式 16 连注）", ok)

st11["any_ts"] = [NOW - 7200] * 3   # 窗老化殆尽 → 下次入窗 pre_len 0 < 半阈 → 再武装
put_state(d11, "sA", st11)
for i in range(10, 18):
    run(OBSERVE, obs_payload(d11, trigger="auto", prompt_id=f"a{i}"), d11)
rc, out = run(GATE, gate_payload(d11, prompt_id="a17", tpath=tp11), d11)
led11, st11 = ledger_of(d11), state_of(d11)
ok = len([r for r in led11 if r.get("event") == "runaway"]) == 2 \
    and "速率异常" in ac_of(out) and len(st11.get("runaway_ts") or []) == 2
check("回落半阈以下再达阈 → 再武装二次注入（评审 #6）", ok)

d12 = proj()
tp12 = os.path.join(d12, "t.jsonl")
open(tp12, "w", encoding="utf-8").close()
run(OBSERVE, obs_payload(d12, trigger="auto", prompt_id="z0"), d12)
put_state(d12, "sA", {"auto_ts": [], "any_ts": [NOW - 3600, NOW - 7200], "sub_ts": [],
                      "runaway_ts": [NOW - 3600, NOW - 7200], "rearmed": True})
for i in range(1, 8):
    run(OBSERVE, obs_payload(d12, trigger="auto", prompt_id=f"z{i}"), d12)
rc, out = run(GATE, gate_payload(d12, prompt_id="z7", tpath=tp12), d12)
led12 = ledger_of(d12)
ok = rc == 0 and len([r for r in led12 if r.get("event") == "runaway"]) == 0 \
    and "速率异常" not in ac_of(out)
check("滚动 24h 上限 2 次 → 第三次拒绝（只注入指针）", ok)

d13 = proj()
tp13 = os.path.join(d13, "t.jsonl")
open(tp13, "w", encoding="utf-8").close()
for i in range(3):
    run(OBSERVE, obs_payload(d13, trigger="auto", prompt_id=f"b{i}", sidechain=False), d13)
rc, out = run(GATE, gate_payload(d13, prompt_id="b3", tpath=tp13), d13)
led13, st13 = ledger_of(d13), state_of(d13)
# gate 独立记账（b3 无对行）入第 4 条 → 主窗 ≥4 触发
run(OBSERVE, obs_payload(d13, trigger="auto", prompt_id="b3", sidechain=False), d13)
rc, out = run(GATE, gate_payload(d13, prompt_id="b3", tpath=tp13), d13)
led13, st13 = ledger_of(d13), state_of(d13)
ok = len(st13.get("auto_ts") or []) == 4 \
    and len([r for r in led13 if r.get("event") == "runaway"]) == 1 and "速率异常" in ac_of(out)
check("a 路保留：sidechain=false＋auto → auto_ts 主窗 ≥4/90min 触发（现行混桶外的分桶档）", ok)

d14 = proj()
tp14 = os.path.join(d14, "t.jsonl")
open(tp14, "w", encoding="utf-8").close()
for i in range(5):
    run(OBSERVE, obs_payload(d14, trigger="manual", prompt_id=f"c{i}"), d14)
rc, out = run(GATE, gate_payload(d14, prompt_id="c4", tpath=tp14), d14)
led14, st14 = ledger_of(d14), state_of(d14)
ok = len(compacts(led14, "sA")) == 5 and st14.get("auto_ts") == [] and st14.get("any_ts") == [] \
    and st14.get("sub_ts") == [] \
    and "trigger: manual" in ac_of(out) and "速率异常" not in ac_of(out)
check("manual 记账不入窗（v1「手动与失控同桶」缺陷修正）——5 发零 runaway、三窗全空", ok)

d15 = proj()
for i in range(19):
    run(OBSERVE, obs_payload(d15, trigger="auto", prompt_id=f"s{i}", sidechain=True), d15)
run(OBSERVE, obs_payload(d15, trigger="auto", prompt_id="s19", sidechain=True), d15)
rc, out = run(GATE, gate_payload(d15, prompt_id="s19"), d15)
led15, st15 = ledger_of(d15), state_of(d15)
ok = rc == 0 and out.strip() == "" and len(st15.get("sub_ts") or []) == 20 \
    and len([r for r in led15 if r.get("event") == "runaway-sub"]) == 1
check("子代理聚合 ≥20/24h → runaway-sub 只记账零注入（D7：投递对象不存在）", ok)

d16 = proj()
for i in range(10):
    run(OBSERVE, obs_payload(d16, trigger="auto", prompt_id=f"t{i}", sidechain=True), d16)
rc, out = run(GATE, gate_payload(d16, prompt_id="t9"), d16)
ok = rc == 0 and out.strip() == "" \
    and not any(r.get("event") == "runaway-sub" for r in ledger_of(d16) or [])
check("子代理 10 发/24h → 不触 runaway-sub（b5ae44d8 实弹 10 发不误报）", ok)

# —— clear / startup（D5＋孤儿清扫＋回读通道 §2） ——
d17 = proj()
put_state(d17, "sA", {"auto_ts": [NOW], "any_ts": [], "sub_ts": [], "runaway_ts": [], "rearmed": False})
led17_len = 0
rc, out = run(GATE, gate_payload(d17, source="clear"), d17)
ok = rc == 0 and ac_of(out) == "" and state_of(d17, "sA") is None \
    and ledger_of(d17) is None
check("clear → 顺带清窗（状态文件删）＋零注入零账行（D5 依赖解除）", ok)

d18 = proj()
os.makedirs(gdir(d18), exist_ok=True)
for sid, age in (("old1", 8 * 86400), ("old2", 6 * 86400), ("keep", 3600)):
    with open(os.path.join(gdir(d18), sid + ".json"), "w", encoding="utf-8") as f:
        json.dump({"auto_ts": [], "any_ts": [], "sub_ts": [], "runaway_ts": [], "rearmed": True}, f)
    os.utime(os.path.join(gdir(d18), sid + ".json"), (NOW - age, NOW - age))
open(os.path.join(gdir(d18), "ledger.jsonl"), "w", encoding="utf-8").close()
rc, out = run(GATE, gate_payload(d18, sid="new", source="startup"), d18)
ok = rc == 0 and ac_of(out) == "" \
    and not os.path.exists(os.path.join(gdir(d18), "old1.json")) \
    and os.path.exists(os.path.join(gdir(d18), "old2.json")) \
    and os.path.exists(os.path.join(gdir(d18), "keep.json")) \
    and os.path.exists(os.path.join(gdir(d18), "ledger.jsonl"))
check("startup → 孤儿清扫 >7d（6 天/1h 保留、ledger 不动）＋无回读条件静默", ok)

d19 = proj()
cfg19 = cfg_for(d19)
tp19 = make_transcript(d19, cfg19, "sOLD")
put_ledger(d19, [{"schema": 2, "ts": iso(NOW - 3600 * i), "sid": "sOLD",
                  "trigger": "auto", "sidechain": None, "event": "compact",
                  "n_window": i, "plugin_ver": FAKE_PLUG_VER,
                  "hook": "compact-observe", "prompt_id": f"o{i}"} for i in range(3)])
rc, out = run(GATE, gate_payload(d19, sid="sNEW", source="startup"), d19, cfg_dir=cfg19)
ac19 = ac_of(out)
led19 = ledger_of(d19)
hd = [r for r in led19 if r.get("event") == "handoff"]
ok = rc == 0 and "上次断点" in ac19 and tp19 in ac19 and "近 3 发" in ac19 \
    and len(hd) == 1 and hd[0].get("trigger") == ">=3/24h" and hd[0].get("sid") == "sNEW" \
    and hd[0].get("n_window") == 3
check("startup 回读·≥3/24h → 断点指针一行＋handoff 账行（trigger=条件枚举）", ok)

d20 = proj()
cfg20 = cfg_for(d20)
tp20 = make_transcript(d20, cfg20, "sR")
put_ledger(d20, [{"schema": 2, "ts": iso(NOW - 600), "sid": "sR", "trigger": "auto",
                  "sidechain": None, "event": "compact", "n_window": 8,
                  "plugin_ver": FAKE_PLUG_VER, "hook": "compact-observe", "prompt_id": "r0"},
                 {"schema": 2, "ts": iso(NOW - 590), "sid": "sR", "trigger": "auto",
                  "sidechain": None, "event": "runaway", "n_window": 8,
                  "plugin_ver": FAKE_PLUG_VER, "hook": "compact-gate"}])
rc, out = run(GATE, gate_payload(d20, sid="sNEW", source="startup"), d20, cfg_dir=cfg20)
hd = [r for r in ledger_of(d20) if r.get("event") == "handoff"]
ok = rc == 0 and "上次断点" in ac_of(out) and len(hd) == 1 and hd[0].get("trigger") == "runaway"
check("startup 回读·runaway 条件 → 注入＋handoff（trigger=runaway 优先枚举）", ok)

d21 = proj()
put_ledger(d21, [{"schema": 2, "ts": iso(NOW - 600), "sid": "sX", "trigger": "auto",
                  "sidechain": None, "event": "compact", "n_window": 1,
                  "plugin_ver": FAKE_PLUG_VER, "hook": "compact-observe", "prompt_id": "q0"},
                 {"schema": 2, "ts": iso(NOW - 500), "sid": "sX", "trigger": "auto",
                  "sidechain": None, "event": "compact", "n_window": 2,
                  "plugin_ver": FAKE_PLUG_VER, "hook": "compact-observe", "prompt_id": "q1"}])
rc, out = run(GATE, gate_payload(d21, sid="sNEW", source="startup"), d21)
ok = rc == 0 and ac_of(out) == "" and not any(r.get("event") == "handoff" for r in ledger_of(d21))
check("startup 回读不触（<3 发且无 runaway）→ 静默零账行", ok)

d22 = proj()
cfg22 = cfg_for(d22)   # ledger 达阈但 transcript 文件缺 → mtime 核失败 → 静默
put_ledger(d22, [{"schema": 2, "ts": iso(NOW - 3600 * i), "sid": "sGONE",
                  "trigger": "auto", "sidechain": None, "event": "compact",
                  "n_window": i, "plugin_ver": FAKE_PLUG_VER,
                  "hook": "compact-observe", "prompt_id": f"g{i}"} for i in range(3)])
rc, out = run(GATE, gate_payload(d22, sid="sNEW", source="startup"), d22, cfg_dir=cfg22)
ok = rc == 0 and ac_of(out) == "" and not any(r.get("event") == "handoff" for r in ledger_of(d22))
check("startup 断点 transcript 缺 → 存在性核验失败静默（无 handoff 账行）", ok)

# —— 坏输入 / 旧状态容忍（评审 #7）/ 隐私 ——
d23 = proj()
p = subprocess.run([sys.executable, GATE], input=b"not-json", capture_output=True, cwd=d23)
ok = p.returncode == 0 and p.stdout == b"" and ledger_of(d23) is None
rc, out = run(GATE, {k: v for k, v in gate_payload(d23).items() if k != "session_id"}, d23)
ok = ok and rc == 0 and ac_of(out) == "" and not os.path.exists(gdir(d23))
rc2, out2 = run(GATE, gate_payload(d23, source="resume"), d23)
ok = ok and rc2 == 0 and ac_of(out2) == "" and ledger_of(d23) is None
check("gate 坏 JSON/缺 sid/source=resume → exit 0 零写面（防呆沿 v1）", ok)

d24 = proj()
tp24 = os.path.join(d24, "t.jsonl")
open(tp24, "w", encoding="utf-8").close()
put_state(d24, "sA", {"count": 2, "marker": True})   # v1 形
rc, out = run(GATE, gate_payload(d24, tpath=tp24), d24)
st24 = state_of(d24)
ok = rc == 0 and "第 1 次压缩" in ac_of(out) and st24 \
    and st24.get("auto_ts") == [] and len(st24.get("any_ts") or []) == 1 \
    and "count" not in st24 and "marker" not in st24
check("v1 形 {count,marker} 状态 → 缺键弃用从空窗起（不迁移不崩）", ok)

d25 = proj()
tp25 = os.path.join(d25, "t.jsonl")
open(tp25, "w", encoding="utf-8").close()
os.makedirs(gdir(d25), exist_ok=True)
with open(os.path.join(gdir(d25), "sA.json"), "w", encoding="utf-8") as f:
    f.write("{corrupt json")
rc, out = run(GATE, gate_payload(d25, tpath=tp25), d25)
ok = rc == 0 and "第 1 次压缩" in ac_of(out) and len(state_of(d25).get("any_ts") or []) == 1
check("坏状态文件 → 从空窗起不崩（沿 v1 变异锁）", ok)

d26 = proj()
run(GATE, gate_payload(d26), d26)
run(OBSERVE, obs_payload(d26, trigger="auto", prompt_id="k1"), d26)
raw = open(os.path.join(gdir(d26), "ledger.jsonl"), encoding="utf-8").read()
ok = "transcript_path" not in raw and d26 not in raw and "custom_instructions" not in raw
check("隐私（D6）：账行零路径零正文——无 transcript_path/工程路径/custom_instructions 键", ok)

# —— 退役面＋登记断言（Q3 即拆＋§6.1 生产登记形） ——
ok = not os.path.exists(DECISION)
check("Q3 即拆：compact-gate-decision.py 已退役（文件不在——防无批复活）", ok)

with open(os.path.join(HERE, "hooks.json"), encoding="utf-8") as f:
    hj_raw = f.read()
try:
    hj = json.loads(hj_raw).get("hooks", {})
except Exception:
    hj = {}
ss = hj.get("SessionStart") or []
pc = hj.get("PreCompact") or []
pt = hj.get("PostToolUse") or []
ss_m = [e.get("matcher") for e in ss]
check("hooks.json SessionStart matcher＝裸 compact|clear|startup（\\| 转义形永不匹配——防呆沿 v1）",
      "compact|clear|startup" in ss_m and "compact\\|clear\\|startup" not in hj_raw.replace("\\\\", "\\"))
pc_cmds = [h.get("command", "") for e in pc for h in e.get("hooks", [])]
ok = len(pc) == 1 and pc[0].get("matcher") is None and len(pc_cmds) == 1 \
    and "compact-observe.py" in pc_cmds[0] and "|| python " in pc_cmds[0] \
    and pc[0].get("hooks", [{}])[0].get("async") is False \
    and pc[0].get("hooks", [{}])[0].get("timeout") == 10
check("hooks.json PreCompact＝单条无 matcher 登记（探针实证双登记即同发双行）＋async:false＋timeout 10", ok)
ok = not any(e.get("matcher") == "AskUserQuestion" for e in pt) \
    and "compact-gate-decision.py" not in hj_raw
check("hooks.json PostToolUse(AskUserQuestion) 条目已删（弹窗链整条拆除——防复活）", ok)

print(f"compact-gate v2 fixture: {'全绿' if fails == 0 else f'{fails} 失败'}")
sys.exit(1 if fails else 0)
