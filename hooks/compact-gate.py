#!/usr/bin/env python3
# crules-flutter 会话压缩计数闸（SessionStart hook · 2026-11-09；Q1–Q9 需求方全裁通过后落码、
#   试点 R2 收口裁「留」2026-11-11——方案档随批终态删档，读数与裁决＝annex 2026-11 卷，git 史可查）
# 闸形（D1）：压缩后注入，不做压缩前拦截——PreCompact block 有恢复路径失败＋死锁面双证（方案 §3.5）。
# 阶梯（D2/Q2）：同任务上限 2 次＝**人裁触发点非硬上限**——第 1 次观测注入（催落快照）；≥2 次且无
#   marker 人裁注入（第 3 次起仍问＝「放行一次」语义的自然结果）；手动 /compact 与 idle compaction
#   同计数（SessionStart 输入无 trigger 字段，source=compact 不分 manual/auto）。
# 人裁回传（D3/Q3/Q4/Q9①）：本 hook 只注入；裁决由模型转手 AskUserQuestion（问题文本以
#   「[compact-gate]」开头并附快照文件完整路径），compact-gate-decision.py 挂 PostToolUse 回填
#   ledger 裁决列／snap_ok 快照 mtime 核／落 marker（1.3.5 续期批：去自报化——先落快照再弹窗，
#   试点首夜谎报快照一例实锤后裁——R2 读数见 annex 2026-11 卷）。
#   marker＝「本任务不再提醒」（clear 清零，与计数同文件存防跨计数残留；decision 件在 state 缺失
#   回落时可产 count=0+marker 态——无害：第 1 次档恒观测注入，静默只在 ≥2 档生效）。
# 无人值守缺省（D5/Q5）：不阻塞不静默——账行恒落（机械面），注入是建议非强制（遵守面）；
#   未裁决账行留浮现通道（下次压缩无 marker 再问 / 聚合侧翻账），与 MAINTENANCE 无人值守硬线同构。
# 状态落点（D6）：.claude/memory/compact-gate/<净化 sid>.json（house 形，复用 find_project_root＋
#   sanitize_sid，天然分工程分会话）；ledger 同目录 ledger.jsonl append-only（照 .compliance-log 形，
#   隐私对齐：只落计数/布尔/裁决枚举/sid，零对话正文）。clear/startup 删该 sid 状态；startup 顺带
#   清扫 >7 天孤儿 sid 文件（不触 ledger）。
# 输入契约 fail-open（stop-reminder 同款）：stdin 非法 JSON / 顶层非对象 / 缺 sid / source 未知
#   → exit 0 不计不注——缺 sid 落地即空串共享计数文件互染，防呆优先。
# matcher 纪律（hooks.json）：裸 `compact|clear|startup`——resume 刻意不在列（--continue 续会话
#   计数应延续）；JSON 内写 `\|` 转义形会按字面竖线匹配、永不触发（防呆断言在 test_compact_gate.py）。
# Windows 纪律：无 python3 时经 hooks.json 兜底链退化 python；进程期 SetErrorMode 压框（六 hook 同款）。
import json
import os
import sys
import time
from _common import (emit_additional_context, find_project_root,
                     plugin_version, sanitize_sid, _hook_utf8_streams)

if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.kernel32.SetErrorMode(0x0002)
    except Exception:
        pass

ORPHAN_TTL = 7 * 86400  # 孤儿 sid 状态文件清扫阈值（D6：startup 顺带，不触 ledger）
LIMIT = 2               # 同任务人裁触发点（Q2：非硬上限——放行后可超、超限进账）

_hook_utf8_streams()

COPY_1ST = (f"压缩计数：本会话第 1 次压缩（同任务上限 {LIMIT} 次）。断点快照尚未落盘。"
            "工程纪律要求压缩后立即落快照（台账/task 回写/结论归位）；摄入面节读、不回读整文件。")
COPY_NTH = (f"压缩计数：第 {{n}} 次压缩，已达同任务上限（{LIMIT} 次）。工程纪律要求：①先落断点快照（台账/task 回写），"
            "再以 AskUserQuestion 征询需求方裁决，问题文本以「[compact-gate]」开头并附快照文件完整路径，"
            "选项＝放行一次并记账／落快照后重开／本任务不再提醒；"
            "AskUserQuestion 不可用时落快照＋继续（compact-nth 账行 verdict=null 即未裁决记录）。")


def ledger_line(gdir_path, event, sid, count, verdict=None):
    rec = {"schema": 1,
           "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "sid": sid,
           "plugin_ver": plugin_version(),
           "hook": "compact-gate",
           "event": event,
           "count": count,
           "verdict": verdict}
    with open(os.path.join(gdir_path, "ledger.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def load_state(path):
    try:
        with open(path, encoding="utf-8") as f:
            st = json.load(f)
        if isinstance(st, dict) and isinstance(st.get("count"), int):
            return {"count": st["count"], "marker": bool(st.get("marker"))}
    except Exception:
        pass
    return {"count": 0, "marker": False}


def save_state(path, st):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False)


try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if not isinstance(data, dict):
    sys.exit(0)
sid = sanitize_sid(data.get("session_id"))
if not sid:
    sys.exit(0)   # 缺 sid → 不计不注（防空串回落共享计数文件互染）
source = data.get("source")
if source not in ("compact", "clear", "startup"):
    sys.exit(0)   # resume（--continue 应延续计数）与未知值防御性不介入
root = find_project_root(data.get("cwd") if isinstance(data.get("cwd"), str) else os.getcwd())
if not root:
    sys.exit(0)   # 无记忆库（轻量档/未 init）→ 不介入（house 闸同款定根前提）
gdir_path = os.path.join(root, ".claude", "memory", "compact-gate")
state_path = os.path.join(gdir_path, sid + ".json")

if source in ("clear", "startup"):
    try:
        os.remove(state_path)   # 任务边界：计数与 marker 同殁（Q4 本任务语义＝clear 前）
    except OSError:
        pass
    if source == "startup":
        try:   # 孤儿清扫（>7 天未动的 sid 状态文件；崩溃/收尾遗留），ledger 不在清扫面
            now = time.time()
            for name in os.listdir(gdir_path):
                p = os.path.join(gdir_path, name)
                if name.endswith(".json") and now - os.path.getmtime(p) > ORPHAN_TTL:
                    os.remove(p)
        except OSError:
            pass
    sys.exit(0)

# source == "compact"
try:
    os.makedirs(gdir_path, exist_ok=True)
except OSError:
    sys.exit(0)
st = load_state(state_path)
st["count"] += 1
n = st["count"]
if n == 1:
    emit_additional_context("SessionStart", COPY_1ST)
    event = "compact-1st"
elif not st["marker"]:
    emit_additional_context("SessionStart", COPY_NTH.format(n=n))
    event = "compact-nth"
else:
    event = "compact-muted"   # 不再提醒生效中：静默但记账不断流（判据 3）
try:
    ledger_line(gdir_path, event, sid, n)
except Exception:
    pass   # 记账失败不阻断注入（注入面优先；缺口由账行缺失在聚合侧显形）
try:
    save_state(state_path, st)
except Exception:
    pass
sys.exit(0)
