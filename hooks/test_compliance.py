#!/usr/bin/env python3
# compliance-audit.py fixture 回归（1.0.37 批2）——静默五态（非法 JSON / 顶层非对象 / 转录缺失 /
#   转录路径异型 / 轻量档无 NAVIGATION）+ 事实计数（编辑/执行/commit 格式/触发词/声明/deny 命中/
#   权限拒/派单令牌/弱签名三项）+ sidechain 跳过 + 解析坏行计数 + 截断（env 时间闸）+ 甄别列
#   （markers 只看末条 / closing_q）+ ledger 快照两态 + plugin_ver 打标 + sid 截断 + append 多次
#   触发 + 隐私红线（正文不入账）。
import json, os, subprocess, sys, tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "compliance-audit.py")
fails = 0

def check(name, cond):
    global fails
    print(("PASS  " if cond else "FAIL  ") + name)
    if not cond:
        fails += 1

def a(text=None, tools=(), sidechain=False, denial=None):
    """assistant 行：text 块 + tool_use 块；tools = [(name, input), ...]"""
    content = ([{"type": "text", "text": text}] if text is not None else []) + \
              [{"type": "tool_use", "name": n, "input": i} for n, i in tools]
    d = {"type": "assistant", "message": {"content": content}}
    if sidechain:
        d["isSidechain"] = True
    if denial:
        d["toolDenialKind"] = denial
    return d

def u(content):
    """user 行：str = 手输；list = tool_result 等块"""
    return {"type": "user", "message": {"content": content}}

def tr(text):
    return u([{"type": "tool_result", "content": text}])

def write_tp(d, name, lines):
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as f:
        for l in lines:
            f.write((l if isinstance(l, str) else json.dumps(l, ensure_ascii=False)) + "\n")
    return p

def run(payload, cwd, env=None):
    e = {**os.environ, **(env or {})}
    p = subprocess.run([sys.executable, HOOK], input=json.dumps(payload).encode(),
                       capture_output=True, cwd=cwd, env=e)
    return p.returncode, p.stdout

def read_log(d):
    p = os.path.join(d, ".claude", "memory", ".compliance-log")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]

def setup(with_nav=True):
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, ".claude", "memory"))
    if with_nav:
        open(os.path.join(d, ".claude", "memory", "NAVIGATION.md"), "w").close()
    return d

# —— 静默五态：任何一路都不许产生账行，且 rc=0（fail-open） ——
d = setup()
p = subprocess.run([sys.executable, HOOK], input=b"not-json", capture_output=True, cwd=d)
check("非法 JSON stdin → rc0 无账行", p.returncode == 0 and read_log(d) is None and p.stdout == b"")
p = subprocess.run([sys.executable, HOOK], input=b"[1,2]", capture_output=True, cwd=d)
check("顶层非对象 JSON → rc0 无账行（N1 形状守卫）", p.returncode == 0 and read_log(d) is None)
tp = write_tp(d, "t1.jsonl", [u("hi")])
p = subprocess.run([sys.executable, HOOK],
                   input=json.dumps({"transcript_path": tp, "cwd": d}).encode(),
                   capture_output=True, cwd=d)
check("缺 session_id/reason 不拦——仍落账（字段仅打标）", p.returncode == 0 and read_log(d) is not None)
os.remove(os.path.join(d, ".claude", "memory", ".compliance-log"))
rc, _ = run({"transcript_path": os.path.join(d, "nope.jsonl"), "cwd": d,
             "session_id": "s1", "reason": "other"}, d)
check("转录路径不存在 → rc0 无账行（无米不落空账）", rc == 0 and read_log(d) is None)
rc, _ = run({"transcript_path": 123, "cwd": d, "session_id": "s1", "reason": "other"}, d)
check("transcript_path 异型(int) → rc0 无账行", rc == 0 and read_log(d) is None)
d2 = setup(with_nav=False)
tp2 = write_tp(d2, "t.jsonl", [u("hi")])
rc, _ = run({"transcript_path": tp2, "cwd": d2, "session_id": "s1", "reason": "other"}, d2)
check("轻量档（无 NAVIGATION.md）→ rc0 无账行", rc == 0 and read_log(d2) is None)

# —— 全量事实计数 ——
d3 = setup()
tp3 = write_tp(d3, "t.jsonl", [
    u("请提交"),                                                    # trigger_msgs
    a("改完了", tools=[("Edit", {"file_path": "lib/a.dart"}),
                       ("Write", {"file_path": "lib/b.dart"})]),     # edits=2
    a(tools=[("Bash", {"command": "flutter test"})]),               # execs=1 bash=1
    a(tools=[("Bash", {"command": 'git commit -m "feat: 甲"'})]),    # commits=1 fmt_ok=1
    a(tools=[("Bash", {"command": 'git commit -m "没有前缀"'})]),    # commits=2 fmt_ok 不变
    a("测试全绿 PASS=12"),                                           # claims=1
    tr("该命令被 crules-flutter 安全闸 拦截"),                        # denial_hits=1
    a(tools=[("Agent", {"subagent_type": "crules-flutter:reviewer",
                        "prompt": "【切片包】审"})]),                 # review=1 slice_pkg=1
    a(tools=[("Agent", {"subagent_type": "plan-reviewer", "prompt": "无令牌",
                        "run_in_background": True})]),              # review=2 slice_none bg=1
    a(tools=[("AskUserQuestion", {"questions": []})]),              # ask_user_question=1
    a("选一个：\n1) 甲\n2) 乙", tools=[("PowerShell", {"command": "git diff"})]),  # plain_options=1 git_diff_follow=1 bash+1
    a(tools=[(999, {})]),                                     # tool_use name 异型 → 跳过不崩、不计数
    a("收尾：review结论 无发现；沉淀候选 2；待裁决区 见上。要授权提交吗？"),      # markers 全 True + closing_q
])
rc, _ = run({"transcript_path": tp3, "cwd": d3, "session_id": "s-full", "reason": "clear"}, d3)
log = read_log(d3)
r = log[0] if log and len(log) == 1 else {}
check("正常会话 → 恰一行账（rc0、stdout 空 = fire-and-forget）",
      rc == 0 and len(log or []) == 1)
check("事实计数（edits2/execs1/commits2 格式1/claims1/触发词1）",
      (r.get("edits"), r.get("execs"), r.get("commits"), r.get("commit_fmt_ok"),
       r.get("claims"), r.get("trigger_msgs")) == (2, 1, 2, 1, 1, 1))
check("bash_calls 计数含全部 Bash/PowerShell 调用（4）", r.get("bash_calls") == 4)
check("派单计数（review2 包1 免0）+ deny 命中1 + 弱签名 bg1/diff1/askq1/opt1",
      (r.get("review_dispatch"), r.get("slice_pkg"), r.get("slice_exempt"),
       r.get("denial_hits")) == (2, 1, 0, 1) and
      (r.get("bg_dispatch"), r.get("git_diff_follow"), r.get("ask_user_question"),
       r.get("plain_options")) == (1, 1, 1, 1))
check("甄别列：末条含三件套标记全 True + closing_q True",
      all(r.get("markers", {}).values()) and r.get("closing_q") is True)
check("元数据打标（sid/reason/schema/plugin_ver 键在位）",
      r.get("sid") == "s-full" and r.get("reason") == "clear" and r.get("schema") == 1
      and "plugin_ver" in r)
check("ledger 快照：两账均缺 → None（区分「空账」与「无账」）",
      r.get("ledger_lines") == {".gate-exceptions": None, ".review-ledger": None})

# —— markers 只看**末条**文本（中途说过 ≠ 收尾说了）——
d4 = setup()
tp4 = write_tp(d4, "t.jsonl", [
    a("本批 review结论 已出。"),
    a("最终交付如下。"),
])
run({"transcript_path": tp4, "cwd": d4, "session_id": "s4", "reason": "other"}, d4)
r4 = (read_log(d4) or [{}])[0]
check("markers 仅取末条文本（中途提过 ≠ 收尾标志）",
      r4.get("markers") == {"review结论": False, "沉淀候选": False, "裁决区": False})

# —— 坏行 / sidechain / 截断 ——
d5 = setup()
tp5 = write_tp(d5, "t.jsonl", [
    "{ 坏 json",
    u("ok"),
    "null",                                    # 合法 JSON 但顶层非对象 → 计坏行
    a(tools=[("Edit", {"file_path": "x"})], sidechain=True),   # sidechain 不计 edits
    a(),                                       # 空 content 也计数正常
])
run({"transcript_path": tp5, "cwd": d5, "session_id": "s5", "reason": "other"}, d5)
r5 = (read_log(d5) or [{}])[0]
check("坏行计数入账（2 坏 / 5 行——解析率显式化防静默归零）",
      r5.get("bad_lines") == 2 and r5.get("transcript_lines") == 5)
check("sidechain 行整行跳过抽取（edits=0 但 sidechain_lines=1）",
      r5.get("edits") == 0 and r5.get("sidechain_lines") == 1)
d6 = setup()
tp6 = write_tp(d6, "t.jsonl", [u("行%d" % i) for i in range(300)])
run({"transcript_path": tp6, "cwd": d6, "session_id": "s6", "reason": "other"}, d6,
    env={"CRULES_COMPLIANCE_BUDGET_S": "0"})
r6 = (read_log(d6) or [{}])[0]
check("时间闸到期截断 → truncated:true 且至少扫过 1 行（非零态可比）",
      r6.get("truncated") is True and r6.get("transcript_lines", 0) >= 1)

# —— 空转录 = 事实（区别于「路径不存在」的不落账）——
d7 = setup()
tp7 = write_tp(d7, "t.jsonl", [])
run({"transcript_path": tp7, "cwd": d7, "session_id": "s7", "reason": "other"}, d7)
r7 = (read_log(d7) or [{}])[0]
check("空转录 → 落账且 transcript_lines=0", r7.get("transcript_lines") == 0)

# —— ledger 快照 / plugin_ver / sid 截断 / 多次触发 / 隐私 ——
with open(os.path.join(d7, ".claude", "memory", ".gate-exceptions"), "w", encoding="utf-8") as f:
    f.write('{"a":1}\n\n{"b":2}\n')
pr = setup()
os.makedirs(os.path.join(pr, ".claude-plugin"))
with open(os.path.join(pr, ".claude-plugin", "plugin.json"), "w", encoding="utf-8") as f:
    json.dump({"version": "9.9.9"}, f)
run({"transcript_path": tp7, "cwd": d7, "session_id": "x" * 200, "reason": "resume"}, d7,
    env={"CLAUDE_PLUGIN_ROOT": pr})
rows = read_log(d7)
r7b = rows[-1]
check("ledger 快照计入非空行（gate-exceptions=2）",
      r7b.get("ledger_lines", {}).get(".gate-exceptions") == 2)
check("plugin_ver 自 CLAUDE_PLUGIN_ROOT 读取；sid 截断 MAX_SID=80",
      r7b.get("plugin_ver") == "9.9.9" and len(r7b.get("sid", "")) == 80)
check("append-only：同会话二次触发（resume 场景）落两行、不覆盖",
      len(rows) == 2 and rows[0].get("reason") == "other")
raw = open(os.path.join(d7, ".claude", "memory", ".compliance-log"), encoding="utf-8").read()
check("隐私红线：账面无对话正文/命令/路径（手输文本与 file_path 不入账）",
      "请提交" not in raw and "lib/a.dart" not in raw and "flutter test" not in raw)

print(f"compliance-audit fixture: {'全绿' if fails == 0 else f'{fails} 失败'}")
sys.exit(1 if fails else 0)
