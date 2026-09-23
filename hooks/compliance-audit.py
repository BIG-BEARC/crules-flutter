#!/usr/bin/env python3
# crules-flutter 宪法遵守度事实单（SessionEnd hook · 1.0.37 批2，随 plugin 分发）
# 定位：转录 → 每会话终结落**一行** JSONL 事实到 .claude/memory/.compliance-log。三原则承批1
#   （docs/普查-2026-09-22-宪法遵守度测量与批1探针.md）：①**记事实不出结论**——多会话共享工作树、
#   跨会话批次、窗口外授权使「违反」判定极易误伤，定罪归 distill 聚合与人（§五 ledger→§7→人 分工）；
#   「甄别列」= markers/closing_q/edits 三个**独立事实位**，组合判读留聚合侧，本 hook 不加综合字段。
#   ②**转录只作采料场**——本机实测留存仅数日，持久账必须由本 hook 落盘。③**窗口口径钉死**——
#   本账自装版起算、非全历史（「无数≠零样本」同族病的构造性预防）。
# 判据常量与 scripts/closing-audit.py（批1 探针 = 本 hook 前稿）同源——**改判据两处同步**；
#   找根/截断长/三流编码系 hooks/_common.py 共享实现（1.0.39 收编，本文件曾为第三例拷贝）。
# SessionEnd 契约边界（1.0.36 实核官方文档）：
#   - 每会话终结触发一次，reason ∈ clear|resume|logout|prompt_input_exit|other；多次终结多次触发
#     （resume 场景）——账本 append-only，重复触发是事实不是重复记账错误，聚合侧按 sid 归并。
#   - 输出 fire-and-forget（stdout 无人读）→ 本 hook 不打印，只写文件。
#   - **SessionEnd 各 hook 共享 1.5s 预算，per-hook timeout 可上调**——hooks.json 登记处显式
#     timeout 30，内部 BUDGET_S 10s 时间闸：到点截断扫描并带 truncated:true 落账（截断是事实，
#     不等于「零违反」——防慢转录被静默读成全遵守）。
#   - 转录滞后：终结瞬间最后几行可能未落盘 → 计数少几行属预期，聚合侧勿定罪。
# 静默与 fail-open：无 NAVIGATION.md（轻量档记忆库关）→ 不介入；stdin 非法 JSON / 顶层非对象 /
#   transcript_path 缺失或不可读 → exit 0 静默（本 hook 无阻断职责，静默=本会话无读数）。
#   解析率自身入账：transcript_lines/bad_lines 恒为事实两列——「解析静默归零读成全遵守」的锁。
# 隐私红线（§一）：**只落计数/布尔/截断短串**——永不落对话正文、命令原文、文件路径、提交信息；
#   tool_result 的 deny 字样检测在内存内子串命中即弃，result 文本不进账。
# 并发落盘：单行 <4KB，POSIX O_APPEND 原子；Windows 无 flock 沿 pending-updates D3 口径（窗口远小于不记）。
# 编码/AV 纪律：1.0.21 P0-A 三流钉 UTF-8；1.0.33 SetErrorMode——**四 hook 同款同改**（本文件为第四位）。
import json, os, re, sys, time
from _common import (MAX_SID, find_project_root,
                     _hook_utf8_streams)  # 1.0.39 共享实现收编（hooks/_common.py）

# 进程期 AV 弹框压制（1.0.33 同款，1.0.36 起四 hook 同款同改）：Windows 注入型管控 agent
#   会使进程中途访问违例并弹模态框——hook 挂起等点击直至超时；脚本内 SetErrorMode(0x2) 即无框
#   静默死。父进程预设会被 CPython 启动覆写，故必须脚本内设；压框失败仅退回原状
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.kernel32.SetErrorMode(0x0002)
    except Exception:
        pass

# 扫描时间闸（< hooks.json 登记的 timeout 30。同步执行会占用会话退出瞬间，闸须短——
#   实测转录均值 ≈400 行、5 万行大转录也仅 1–3s，10s 已覆盖极端态）。
#   env 覆写口仅供 fixture 测截断路径——真机不会有人设它；float 解析失败退默认（fail-open）
try:
    BUDGET_S = float(os.environ.get("CRULES_COMPLIANCE_BUDGET_S") or "10")
except ValueError:
    BUDGET_S = 10.0
TAIL_CAP = 4000    # 末条文本只留尾部这么长参与标记判定（内存占用上限，不进账）

# —— 判据常量：与 scripts/closing-audit.py 同源，改动两处同步 ——
EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}
EXEC_RE = re.compile(r"\b(flutter test|dart test|test-self|flutter analyze|dart analyze|pytest|npm test|dart run build_runner)\b")
COMMIT_RE = re.compile(r"\bgit\b[^;|]*\bcommit\b")
TRIGGER_RE = re.compile(r"(提交|推送|commit|push)", re.I)
CLAIM_RE = re.compile(r"(全绿|测试通过|0 失败|失败 0|PASS=|全部通过|零失败)")
MSG_TYPE_RE = re.compile(r"^(feat|fix|refactor|perf|build|ci|docs|style|test|chore): \S")
DENIAL_MARKS = ("请需求方人工执行", "crules-flutter 安全闸", "warn 层")
REVIEW_SUB_RE = re.compile(r"(reviewer|plan-reviewer)$")
# —— 弱签名三项（1.0.36 裁决：全带·只记）配套常量 ——
DIFF_RE = re.compile(r"\bgit\b[^;|]*\b(status|diff)\b")            # §六 后台 agent 展示 diff 的跟随面
CLOSING_Q_RE = re.compile(r"(授权提交|是否提交|可以提交|要提交|确认提交)")  # 三件套甄别列（坑①）
OPT_LINE_RE = re.compile(r"(?m)^\s*[1-9][)）.、:：]")               # §一 选项卡：纯文本列选项的形态
MARKER_RES = (("review结论", re.compile(r"review ?结论", re.I)),
              ("沉淀候选", re.compile(r"沉淀候选")),
              ("裁决区", re.compile(r"裁决区")))


# 流编码钉 UTF-8 / 向上找项目根 / sid 截断长——实现见 _common（1.0.39 收编四 hook 重复源）
_hook_utf8_streams()




def blocks(d):
    msg = d.get("message")
    if isinstance(msg, dict) and isinstance(msg.get("content"), list):
        return msg["content"]
    return []


def text_of(d):
    return "\n".join(b.get("text", "") for b in blocks(d)
                     if isinstance(b, dict) and b.get("type") == "text"
                     and isinstance(b.get("text"), str))


def result_text(b):
    """tool_result 内文本（截断、仅供子串命中即弃，不进账）"""
    rc = b.get("content")
    if isinstance(rc, str):
        return rc[:TAIL_CAP]
    if isinstance(rc, list):
        return "\n".join(x.get("text", "") for x in rc
                         if isinstance(x, dict) and isinstance(x.get("text"), str))[:TAIL_CAP]
    return ""


def scan(path, deadline):
    """流式单遍扫描转录 → 事实 dict。到 deadline 截断（truncated=True 落账）"""
    f = {"transcript_lines": 0, "bad_lines": 0, "sidechain_lines": 0,
         "edits": 0, "bash_calls": 0, "commits": 0, "commit_fmt_ok": 0,
         "trigger_msgs": 0, "claims": 0, "execs": 0,
         "review_dispatch": 0, "slice_pkg": 0, "slice_exempt": 0,
         "denial_hits": 0, "permission_denials": 0,
         "bg_dispatch": 0, "git_diff_follow": 0,
         "ask_user_question": 0, "plain_options": 0,
         "truncated": False}
    tail = ""
    with open(path, encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh):
            if i and i % 64 == 0 and time.monotonic() > deadline:
                # i==0 恒放行：deadline 已过期也要至少处理一行，截断读数才非零态可比
                f["truncated"] = True
                break
            line = line.strip()
            if not line:
                continue
            f["transcript_lines"] += 1
            try:
                d = json.loads(line)
            except Exception:
                f["bad_lines"] += 1
                continue
            if not isinstance(d, dict):
                f["bad_lines"] += 1
                continue
            if d.get("isSidechain"):
                # 子代理行整行跳过事实抽取——宣约档检查的对象是**主控**的输出物；
                # 子代理退回与否（派单契约的代理侧自护）留聚合侧扩采（普查表 §3 坑⓪）
                f["sidechain_lines"] += 1
                continue
            if d.get("toolDenialKind"):
                f["permission_denials"] += 1
            t = d.get("type")
            if t == "user":
                content = (d.get("message") or {}).get("content") if isinstance(d.get("message"), dict) else None
                if isinstance(content, str) and content.strip() and TRIGGER_RE.search(content):
                    f["trigger_msgs"] += 1
                for b in blocks(d):
                    if isinstance(b, dict) and b.get("type") == "tool_result":
                        rs = result_text(b)
                        if any(m in rs for m in DENIAL_MARKS):
                            f["denial_hits"] += 1
            elif t == "assistant":
                txt = text_of(d)
                if txt.strip():
                    tail = txt[-TAIL_CAP:]
                if CLAIM_RE.search(txt):
                    f["claims"] += 1
                if OPT_LINE_RE.search(txt):
                    f["plain_options"] += 1
                for b in blocks(d):
                    if not isinstance(b, dict) or b.get("type") != "tool_use":
                        continue
                    name = b.get("name")
                    if not isinstance(name, str):
                        continue   # 异型 name（1.0.30 R3 口径）：按「非工具块」跳过，勿让整个账崩
                    inp = b.get("input") if isinstance(b.get("input"), dict) else {}
                    if name in EDIT_TOOLS:
                        f["edits"] += 1
                    elif name in ("Bash", "PowerShell"):
                        cmd = str(inp.get("command", ""))
                        f["bash_calls"] += 1
                        if EXEC_RE.search(cmd):
                            f["execs"] += 1
                        if COMMIT_RE.search(cmd):
                            f["commits"] += 1
                            m = re.search(r"-m\s+[\"'](.*?)[\"']", cmd, re.S)
                            if m and MSG_TYPE_RE.match(m.group(1).strip().splitlines()[0]
                                                        if m.group(1).strip() else ""):
                                f["commit_fmt_ok"] += 1
                        if DIFF_RE.search(cmd):
                            f["git_diff_follow"] += 1
                    elif name == "Agent":
                        sub = str(inp.get("subagent_type", ""))
                        if REVIEW_SUB_RE.search(sub.split(":")[-1]):
                            f["review_dispatch"] += 1
                            pr = str(inp.get("prompt", ""))
                            if "【切片包】" in pr:
                                f["slice_pkg"] += 1
                            if "【切片包-免】" in pr:
                                f["slice_exempt"] += 1
                        if inp.get("run_in_background") is True:
                            f["bg_dispatch"] += 1
                    elif name == "AskUserQuestion":
                        f["ask_user_question"] += 1
    f["_tail"] = tail
    return f


def ledger_lines(mem):
    """收尾时刻两台账行数（存在才计，缺失=None——区分「空账」与「无账」）"""
    out = {}
    for name in (".gate-exceptions", ".review-ledger"):
        try:
            with open(os.path.join(mem, name), encoding="utf-8", errors="replace") as fh:
                out[name] = sum(1 for l in fh if l.strip())
        except OSError:
            out[name] = None
    return out


def plugin_version():
    """账行打标产生它的 plugin 版本（窗口口径的另一半：不同版本判据不同，聚合须可分层）"""
    root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if not isinstance(root, str) or not root:
        return None
    try:
        with open(os.path.join(root, ".claude-plugin", "plugin.json"), encoding="utf-8") as fh:
            j = json.load(fh)
        v = j.get("version") if isinstance(j, dict) else None
        return v if isinstance(v, str) else None
    except Exception:
        return None


try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if not isinstance(data, dict):
    sys.exit(0)   # 形状守卫（1.0.30 N1 同款）：JSON 解析成功 ≠ 形状合法
tp = data.get("transcript_path")
if not isinstance(tp, str) or not tp or not os.path.isfile(tp):
    sys.exit(0)  # 采料场不在——无米不落空账（区别于 lines=0：文件在而空是事实）
cwd = data.get("cwd") if isinstance(data.get("cwd"), str) else os.getcwd()
root = find_project_root(cwd)
if not root:
    sys.exit(0)  # 轻量档（记忆库关）→ 不介入
try:
    mem = os.path.join(root, ".claude", "memory")
    facts = scan(tp, time.monotonic() + BUDGET_S)
    tail = facts.pop("_tail")
    rec = {"schema": 1,
           "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "sid": str(data.get("session_id") or "")[:MAX_SID],
           "reason": str(data.get("reason") or "")[:40],
           "plugin_ver": plugin_version()}
    rec.update(facts)
    rec["markers"] = {label: bool(rx.search(tail)) for label, rx in MARKER_RES}
    rec["closing_q"] = bool(CLOSING_Q_RE.search(tail))
    rec["ledger_lines"] = ledger_lines(mem)
    with open(os.path.join(mem, ".compliance-log"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
except Exception:
    pass  # fail-open：观测件无阻断职责，静默=本会话无读数（缺口由解析率列在聚合侧显形）
sys.exit(0)
