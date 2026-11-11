#!/usr/bin/env python3
# crules-flutter 会话压缩计数闸·裁决回传件（PostToolUse(AskUserQuestion) hook · 2026-11-09，
#   Q9① 哨兵件；与 compact-gate.py 成对——试点 R2 收口裁「留」2026-11-11，方案档随批终态删档、git 史可查）
# 通道基线（方案 §3.5）：AskUserQuestion 是普通工具名，PostToolUse 可匹配其调用与结果，
#   tool_response 携带 answers——本件读回传、机械回填，不依赖模型自写 marker（Q9③ 最弱路弃）。
# 哨兵先核（防误染他人弹窗）：tool_input.questions 里任一问题文本以「[compact-gate]」开头才算自家
#   ——非自家在**任何文件触达之前**毫秒级快退 exit 0（零写面；全工程弹窗都过此件，快退是常态路径）。
# 裁决映射（D3/Q3/Q4）：按注入文案的选项措辞做子串分类——「不再提醒」→ mute＋marker 落盘（本任务
#   =clear 前）；「重开」→ reopen；「放行」→ continue（无 marker，下次压缩无 marker 再问＝放行一次）。
#   其他／answers 异型 → verdict=unparsed 如实记账，零 marker（遵守度账显形，不猜）。
#   子串优先级 mute > reopen > continue：Other 自由文本同时命中时记最不打扰档（误 mute 的代价是
#   少弹窗＋账行在，误弹的代价是疲劳——非对称取轻）。
# answers 形状边界（诚实）：宿主 answers 键/值形未经本机探针实证（阶段 1 探针行回填）；本件兼容
#   值为字符串或 {answer: str} 两形，解析不出即 unparsed——账行可见、可修，不静默丢裁决。
# snap_ok 机械核（1.3.5 续期批，判据 2 量法机械化；试点首夜谎报快照一例后裁——R2 读数＝annex 2026-11 卷）：
#   问题文本正则取快照路径（注入文案已要求完整路径），mtime 对账 ledger 该 sid 末次压缩行 ts——
#   ≥ 为 true、早于为 false（点名文件不存在亦 false＝谎报显形）；无路径/无前序行/解析失败 → null 不猜。
#   账行零正文不变（只落布尔，不落路径）。
# 隐私对齐：账行只落裁决枚举/sid/计数，零问题正文零答案原文。
# Windows 纪律：hooks.json 兜底链＋进程期 SetErrorMode 压框（六 hook 同款同改）。
import json
import os
import re
import sys
import time
from datetime import datetime

from _common import (find_project_root, plugin_version, sanitize_sid,
                     _hook_utf8_streams)

if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.kernel32.SetErrorMode(0x0002)
    except Exception:
        pass

SENTINEL = "[compact-gate]"
# 快照路径（注入文案要求完整路径）；字符类排除空白与全角标点，防把句尾「）。」吃进路径
SNAP_RE = re.compile(r"/[^\s「」『』（）()，。；,;:：·]+?\.(?:md|json|txt|log)(?![\w.])")

_hook_utf8_streams()


def classify(answer):
    if not isinstance(answer, str):
        return None
    if "不再提醒" in answer:
        return "mute"
    if "重开" in answer:
        return "reopen"
    if "放行" in answer:
        return "continue"
    return None


try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if not isinstance(data, dict):
    sys.exit(0)

# —— 哨兵先核：零文件触达的快退路径（非自家弹窗是绝对常态） ——
ti = data.get("tool_input")
qtexts = []
if isinstance(ti, dict) and isinstance(ti.get("questions"), list):
    for q in ti["questions"]:
        if isinstance(q, dict) and isinstance(q.get("question"), str) and q["question"].startswith(SENTINEL):
            qtexts.append(q["question"])
if not qtexts:
    sys.exit(0)

sid = sanitize_sid(data.get("session_id"))
root = find_project_root(data.get("cwd") if isinstance(data.get("cwd"), str) else os.getcwd())
verdict = "unparsed"
if root and isinstance(data.get("tool_response"), dict):
    answers = data.get("tool_response", {}).get("answers")
    if isinstance(answers, dict):
        for qt in qtexts:
            ans = answers.get(qt)
            if isinstance(ans, dict):
                ans = ans.get("answer")
            v = classify(ans)
            if v:
                verdict = v
                break
try:
    if root:
        gdir_path = os.path.join(root, ".claude", "memory", "compact-gate")
        try:
            os.makedirs(gdir_path, exist_ok=True)
        except OSError:
            gdir_path = None
        if gdir_path:
            # snap_ok：问题文本取路径 → mtime 对账末次压缩行 ts（1.3.5 续期批，判据 2 机械化）
            snap_ok = None
            m = SNAP_RE.search(qtexts[0]) if qtexts else None
            if m:
                mt = None
                cwd = data.get("cwd") if isinstance(data.get("cwd"), str) else "."
                for cand in (m.group(0), os.path.join(cwd, m.group(0))):
                    try:
                        mt = os.path.getmtime(cand)
                        break
                    except OSError:
                        continue
                base_ts = None
                try:
                    with open(os.path.join(gdir_path, "ledger.jsonl"), encoding="utf-8") as fh:
                        for ln in fh:
                            try:
                                r = json.loads(ln)
                            except Exception:
                                continue
                            if isinstance(r, dict) and r.get("sid") == sid \
                                    and str(r.get("event", "")).startswith("compact"):
                                base_ts = r.get("ts")
                except OSError:
                    pass
                if mt is None:
                    snap_ok = False   # 点名路径但文件不在＝谎报显形
                elif base_ts:
                    try:
                        snap_ok = mt >= datetime.fromisoformat(base_ts).timestamp()
                    except Exception:
                        snap_ok = None   # 解析不出不猜
            rec = {"schema": 1,
                   "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                   "sid": sid,
                   "plugin_ver": plugin_version(),
                   "hook": "compact-gate-decision",
                   "event": "decision",
                   "count": None,
                   "verdict": verdict,
                   "snap_ok": snap_ok}
            with open(os.path.join(gdir_path, "ledger.jsonl"), "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if verdict == "mute" and sid:
                spath = os.path.join(gdir_path, sid + ".json")
                try:
                    with open(spath, encoding="utf-8") as f:
                        st = json.load(f)
                    if not (isinstance(st, dict) and isinstance(st.get("count"), int)):
                        st = {"count": 0, "marker": False}
                except Exception:
                    st = {"count": 0, "marker": False}
                st["marker"] = True
                try:
                    with open(spath, "w", encoding="utf-8") as f:
                        json.dump(st, f, ensure_ascii=False)
                except Exception:
                    pass   # marker 落盘失败不崩——下次压缩无 marker 会再问（宁可多问不可丢账）
except Exception:
    pass   # fail-open（观测件同款）：无阻断职责，静默＝本次回传无读数
sys.exit(0)
