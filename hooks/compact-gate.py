#!/usr/bin/env python3
# crules-flutter 压缩恢复 v2 · 指针注入件（SessionStart hook · 2026-11-12；方案 docs/方案-压缩
#   恢复v2-指针与速率-2026-11-12.md §4.1。v1 阶梯注入/AskUserQuestion 转手/快照 mtime 核链随
#   Q3「即拆」整条退役（compact-gate-decision.py 删除；R2「留」翻转记档＝annex 2026-11 卷），
#   本件换血为指针＋速率形——同时清偿 v1 六缺陷，依据见方案 §3 实证）。
# 闸形（承 v1 D1）：只注入不拦截——PreCompact block 有恢复路径失败＋死锁面双证，不翻案。
# 指针（D3）：恢复＝指针非重建。每次压缩注入「原文未损：<transcript_path>＋span 直取纪律」
#   ——不再催模型写快照（v1 让模型重写幸存摘要的劣化复制品）。路径三级降级：输入
#   transcript_path 字段（探针实证在场）→ cwd+sid 推导＋存在性核验＋mtime 近邻弱校验
#   → projects 目录通用指引。
# 计数仲裁（§4.1，一轮 #1＋二轮 #1 L1 修正）：序号与 trigger 由 ledger 推导；去重谓词不依赖
#   trigger 值——**同 sid 且同 prompt_id＝同发事件**（实弹三行共享 prompt_id，§6.1 实弹判读），
#   且配对面只认 hook=compact-observe 行（SessionStart 自写行＝上一发完整事件，非本发配对）；
#   ts 近邻 ≤120s 仅 fallback（prompt_id 缺失/不等；窗不放宽——实弹对 96s、最短发间隔 175s，
#   放宽＝degrade-A 快连对漏计）。
# 速率告警（D4/Q4/Q10）：主窗 auto_ts ≥4/90min；混桶 any_ts ≥8/90min（sidechain 无键现行走档
#   ——同桶双阈值保守者生效）→ 追加收尾建议＋runaway 账行。再武装（评审 #6）：窗内计数回落
#   半阈以下复位，滚动 24h 上限 2 次（载体 runaway_ts＋rearmed，§4.3）。子代理聚合 sub_ts
#   ≥20/24h 只记 runaway-sub 账行、零注入（D7：子代理上下文非收尾指令的正确投递对象）。
# 回读通道（§2）：startup 翻账——近 24h runaway 或任一 sid ≥3 发压缩 → 注入断点指针一行
#   ＋handoff 账行（断点＝最近压缩账行 sid；路径推导＋存在性核验＋mtime 近邻弱校验，无则静默）。
# 状态（§4.3）：.claude/memory/compact-gate/<净化 sid>.json＝{auto_ts/any_ts/sub_ts/runaway_ts
#   ＋rearmed}（滚动窗自裁剪；v1 形 {count,marker} 缺键弃用）。clear 顺带清窗（D5 依赖解除——
#   窗自然衰减，不依赖 clear 到达；v1「clear 重置重新武装梯子」根因切除）。startup 顺带清扫
#   >7d 孤儿 sid 文件（不触 ledger）。ledger schema 2 追加式（旧行不迁移兼容）。
# 隐私对齐 D6：账行零对话正文零路径——sid/prompt_id 为 opaque id，枚举/布尔之外不落。
# 输入契约 fail-open（stop-reminder 同款）：stdin 非法 JSON / 顶层非对象 / 缺 sid / source 未知
#   → exit 0 不计不注。matcher 纪律沿 v1（裸 compact|clear|startup，resume 刻意不在列）。
# Windows 纪律：hooks.json python3||python 兜底链＋进程期 SetErrorMode 压框（七 hook 同款）。
import json
import os
import sys
import time

from _common import (emit_additional_context, find_project_root, plugin_version,
                     sanitize_sid, _hook_utf8_streams)
from _compact_core import (DEDUP_WIN, ORPHAN_TTL, RUNAWAY_CAP_N, SUB_LIMIT,
                           append_ledger, bucket_for, derive_transcript, feed_window,
                           ledger_row, load_state, parse_ts, projects_dir, read_ledger,
                           save_state, trim_state)

if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.kernel32.SetErrorMode(0x0002)
    except Exception:
        pass

_hook_utf8_streams()


def resolve_pointer(data, root, sid, last_compact_epoch):
    """路径三级降级（§4.1）：输入字段 → 推导＋存在性＋mtime 弱校验 → 通用指引"""
    tp = data.get("transcript_path")
    if isinstance(tp, str) and os.path.exists(tp):
        return tp
    cand = derive_transcript(root, sid)
    if os.path.exists(cand):
        try:
            anchor = last_compact_epoch if last_compact_epoch else time.time()
            if os.path.getmtime(cand) > anchor - 24 * 3600:   # 弱校验：近 24h 有写
                return cand
        except OSError:
            pass
    return (projects_dir() + " 下按工程目录与 sid 定位 transcript（本机推导未命中——"
            "指针降级为指引，勿因此整文件扫描）")


def handoff(root, sid, gdir_path, data):
    """startup 回读（§2）：近 24h runaway 或任一 sid ≥3 发 → 断点指针一行＋handoff 账行"""
    now = time.time()
    rows = read_ledger(gdir_path)
    recent = [r for r in rows if (parse_ts(r.get("ts")) or 0) > now - 24 * 3600]
    compacts24 = [r for r in recent if str(r.get("event", "")).startswith("compact")]
    has_runaway = any(r.get("event") == "runaway" for r in recent)
    per = {}
    for r in compacts24:
        per[r.get("sid")] = per.get(r.get("sid"), 0) + 1
    if has_runaway:
        cond = "runaway"
    elif any(c >= 3 for c in per.values()):
        cond = ">=3/24h"
    else:
        return   # 无回读条件 → 静默
    last = compacts24[-1] if compacts24 else \
        [r for r in recent if r.get("event") == "runaway"][-1]
    bp_sid = last.get("sid")
    n_bp = sum(1 for r in compacts24 if r.get("sid") == bp_sid)
    last_ts = parse_ts(last.get("ts"))
    cand = derive_transcript(root, bp_sid)
    try:
        fresh = last_ts is not None and os.path.getmtime(cand) >= last_ts - 300
    except OSError:
        fresh = False
    if not fresh:
        return   # 存在性核验/mtime 近邻弱校验失败 → 静默（§2）
    emit_additional_context(
        "SessionStart",
        f"[compact-recovery] 上次断点：transcript {cand}（该 sid 近 {n_bp} 发压缩）。"
        "继任会话需要细节时 grep/jq 直取相关 span，勿整文件回读。")
    pid = data.get("prompt_id") if isinstance(data.get("prompt_id"), str) else None
    append_ledger(gdir_path,
                  ledger_row(sid, cond, None, "handoff", n_bp, pid,
                             "compact-gate", plugin_version()))


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
    sys.exit(0)   # 无记忆库根 → 不介入（house 闸同款定根前提）
gdir_path = os.path.join(root, ".claude", "memory", "compact-gate")
state_path = os.path.join(gdir_path, sid + ".json")

if source == "clear":
    try:
        os.remove(state_path)   # D5：顺带清窗（fail-open；clear 不到无碍——窗自然衰减）
    except OSError:
        pass
    sys.exit(0)

if source == "startup":
    try:   # 孤儿清扫沿 v1（>7d sid 状态文件；ledger 不在清扫面）
        now = time.time()
        for name in os.listdir(gdir_path):
            p = os.path.join(gdir_path, name)
            if name.endswith(".json") and now - os.path.getmtime(p) > ORPHAN_TTL:
                os.remove(p)
    except OSError:
        pass
    try:
        handoff(root, sid, gdir_path, data)
    except Exception:
        pass   # fail-open：回读失败不阻塞会话启动
    sys.exit(0)

# source == "compact"
try:
    os.makedirs(gdir_path, exist_ok=True)
except OSError:
    sys.exit(0)

pid = data.get("prompt_id") if isinstance(data.get("prompt_id"), str) else None
sc = data.get("sidechain")
rows = read_ledger(gdir_path)
now = time.time()

# —— 计数仲裁：配对面只认 PreCompact 观测行（hook 字段区分写入者，§4.1） ——
last = None
for r in rows:
    if r.get("sid") == sid and r.get("event") == "compact":
        last = r   # 该 sid 末条 compact 行
dup = False
trig = "unknown"
sidechain = sc if isinstance(sc, bool) else None
if last is not None and last.get("hook") == "compact-observe":
    lt = parse_ts(last.get("ts"))
    lpid = last.get("prompt_id")
    if pid and isinstance(lpid, str) and pid == lpid:
        dup = True   # 同发身份命中（谓词主面，不受压缩耗时长短影响）
    elif lt is not None and now - lt <= DEDUP_WIN:
        dup = True   # fallback：prompt_id 缺失/不等＋近邻 ≤120s
if last is not None:
    trig = last.get("trigger") if last.get("trigger") in ("manual", "auto") else "unknown"
    lsc = last.get("sidechain")
    if isinstance(lsc, bool):
        sidechain = lsc

st = load_state(state_path)
mutated = False
if not dup:
    bucket, n = feed_window(st, "unknown", sidechain, now)
    append_ledger(gdir_path,
                  ledger_row(sid, "unknown", sidechain, "compact", n, pid,
                             "compact-gate", plugin_version()))
    mutated = True

# —— 速率判定（§4.1：仅主窗/混桶注入收尾建议；子代理聚合只记账） ——
fired = False
cnt = 0
bucket, limit = bucket_for(trig, sidechain)
trim_state(st, now)
if bucket == "sub_ts":
    cnt = len(st["sub_ts"])
    if cnt >= SUB_LIMIT:
        append_ledger(gdir_path,
                      ledger_row(sid, trig, sidechain, "runaway-sub", cnt, None,
                                 "compact-gate", plugin_version()))
        mutated = True
elif bucket is not None:
    cnt = len(st[bucket])
    if cnt >= limit and st.get("rearmed", True) and len(st["runaway_ts"]) < RUNAWAY_CAP_N:
        st["runaway_ts"].append(now)
        st["rearmed"] = False
        append_ledger(gdir_path,
                      ledger_row(sid, trig, sidechain, "runaway", cnt, None,
                                 "compact-gate", plugin_version()))
        mutated = True
        fired = True
if mutated:
    try:
        save_state(state_path, st)
    except Exception:
        pass   # 状态落盘失败不阻断注入（下次读账窗短一拍，阈值面小损可忍）

if sidechain is True:
    sys.exit(0)   # D7：子代理上下文零注入（非收尾指令的正确投递对象）

n_count = sum(1 for r in rows if r.get("sid") == sid and r.get("event") == "compact") \
    + (0 if dup else 1)
try:
    path = resolve_pointer(data, root, sid, parse_ts(last.get("ts")) if last else None)
except Exception:
    path = projects_dir() + "（指针解析异常——降级为指引）"
copy = (f"[compact-recovery] 第 {n_count} 次压缩（trigger: {trig}）。原文未损：{path}。"
        "恢复纪律：需要细节时 grep/jq 该文件直取相关 span，勿整文件回读、"
        "勿凭摘要臆断已读过的内容。")
if fired:
    copy += (f"上下文消耗速率异常（窗内 {cnt} 发）。建议：落终态→报告→任务分解；"
             "原文指针同上。")
try:
    emit_additional_context("SessionStart", copy)
except Exception:
    pass
sys.exit(0)
