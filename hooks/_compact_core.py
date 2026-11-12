#!/usr/bin/env python3
# 压缩恢复 v2 共享核心（compact-gate.py＋compact-observe.py 两件合用；2026-11-12，
#   方案 docs/方案-压缩恢复v2-指针与速率-2026-11-12.md §4——D1「承重全机械」的落点；
#   上提单源先例＝_common.py 1.0.39 收编批。改动纪律同 _common：本件被两 hook import，
#   语法/行为错误爆炸半径两件齐坏——防线＝test-self compileall＋两件 fixture 子进程实跑）。
# 阈值常数为占位值待试点校准（§4.3 阈值校准注记）：主窗 ≥4/90min、混桶 ≥8/90min、
#   runaway-sub ≥20/24h；b5ae44d8 实弹回算——混桶峰值 ~7 不触、子代理 10 发不触、
#   主线程 4 发/52min 触发主窗 ≥4（兜底在）。
import json
import os
import time
from datetime import datetime

AUTO_LIMIT = 4           # 主窗阈值（D4/Q4：≥4 auto/90min——sidechain=false 主线程分桶档）
ANY_LIMIT = 8            # 混桶阈值（Q10-b 回落档：sidechain 无键的现行走档，保守者生效）
SUB_LIMIT = 20           # 子代理聚合阈值（D7：≥20/24h 只记账不注入）
WIN_SPAN = 90 * 60       # 主窗/混桶滚动窗
SUB_SPAN = 24 * 3600     # 子代理聚合窗
RUNAWAY_CAP_SPAN = 24 * 3600
RUNAWAY_CAP_N = 2        # runaway 注入滚动 24h 上限 2 次（评审 #6）
DEDUP_WIN = 120          # ts 近邻 fallback 窗（§4.1：实弹对间隔 96s、b5ae44d8 最短发间隔
                         #   175s>120s——放宽窗会把 degrade-A 快连对误并成漏计，不放宽）
ORPHAN_TTL = 7 * 86400   # 孤儿 sid 状态文件清扫阈值（沿 v1：startup 顺带，不触 ledger）

STATE_KEYS = ("auto_ts", "any_ts", "sub_ts", "runaway_ts")


def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def parse_ts(s):
    """ledger iso ts → epoch。strftime %z 产无冒号 +0800，<3.11 fromisoformat 不吃——补冒号兜底"""
    if not isinstance(s, str):
        return None
    try:
        return datetime.fromisoformat(s).timestamp()
    except Exception:
        pass
    try:
        if len(s) >= 5 and s[-5] in "+-":
            return datetime.fromisoformat(s[:-2] + ":" + s[-2:]).timestamp()
    except Exception:
        pass
    return None


def bucket_for(trigger, sidechain):
    """(桶名, 阈值)。sidechain=true→sub_ts（D7）；manual→不入窗（v1「手动与失控同桶」修正）；
    auto＋false→auto_ts 主窗；auto＋null→any_ts 混桶（现行走档）；unknown→any_ts 保守
    （§4.2 矩阵 degrade-A/B 行：失控检测按 any 桶阈值照跑）"""
    if sidechain is True:
        return "sub_ts", SUB_LIMIT
    if trigger == "manual":
        return None, None
    if trigger == "auto" and sidechain is False:
        return "auto_ts", AUTO_LIMIT
    return "any_ts", ANY_LIMIT


def empty_state():
    st = {k: [] for k in STATE_KEYS}
    st["rearmed"] = True   # 再武装初值＝预置（评审 #6：首次达阈即注入）
    return st


def load_state(path):
    """v1 形 {count,marker} 容忍：四键缺＝空窗弃用（评审 #7，不迁移）；坏 JSON 同弃"""
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        return empty_state()
    if not isinstance(raw, dict):
        return empty_state()
    st = empty_state()
    for k in STATE_KEYS:
        v = raw.get(k)
        if isinstance(v, list):
            st[k] = [float(x) for x in v if isinstance(x, (int, float))]
    st["rearmed"] = bool(raw.get("rearmed", True))
    return st


def save_state(path, st):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False)


def trim_state(st, now=None):
    """滚动窗自裁剪（§4.3）：主/混桶 90min、子聚合与 runaway 上限 24h"""
    now = now if now is not None else time.time()
    st["auto_ts"] = [t for t in st["auto_ts"] if t > now - WIN_SPAN]
    st["any_ts"] = [t for t in st["any_ts"] if t > now - WIN_SPAN]
    st["sub_ts"] = [t for t in st["sub_ts"] if t > now - SUB_SPAN]
    st["runaway_ts"] = [t for t in st["runaway_ts"] if t > now - RUNAWAY_CAP_SPAN]


def feed_window(st, trigger, sidechain, epoch):
    """入窗＋再武装观测（评审 #6：入窗前计数已 < 半阈＝出现过回落 → rearmed=True）。
    返回 (桶名, 入窗后计数)；manual 返回 (None, None)"""
    bucket, _ = bucket_for(trigger, sidechain)
    if bucket is None:
        return None, None
    trim_state(st, epoch)
    if bucket in ("auto_ts", "any_ts"):
        limit = AUTO_LIMIT if bucket == "auto_ts" else ANY_LIMIT
        if len(st[bucket]) * 2 < limit:
            st["rearmed"] = True
    st[bucket] = sorted(set(st[bucket] + [epoch]))
    return bucket, len(st[bucket])


def ledger_file(gdir_path):
    return os.path.join(gdir_path, "ledger.jsonl")


def append_ledger(gdir_path, rec):
    os.makedirs(gdir_path, exist_ok=True)
    with open(ledger_file(gdir_path), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def read_ledger(gdir_path):
    try:
        with open(ledger_file(gdir_path), encoding="utf-8") as fh:
            out = []
            for ln in fh:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    r = json.loads(ln)
                except Exception:
                    continue
                if isinstance(r, dict):
                    out.append(r)
            return out
    except OSError:
        return []


def ledger_row(sid, trigger, sidechain, event, n_window, prompt_id, hook, ver):
    """schema 2 行（§4.3）。隐私对齐 D6：零对话正文零路径——sid/prompt_id 均为 opaque id。
    trigger 列对 handoff 行载触发条件枚举（runaway|>=3/24h，评审 #11）"""
    return {"schema": 2, "ts": now_iso(), "sid": sid, "trigger": trigger,
            "sidechain": sidechain, "event": event, "n_window": n_window,
            "plugin_ver": ver, "hook": hook, "prompt_id": prompt_id}


def projects_dir():
    base = os.environ.get("CLAUDE_CONFIG_DIR")
    if not isinstance(base, str) or not base:
        base = os.path.join(os.path.expanduser("~"), ".claude")
    return os.path.join(base, "projects")


def derive_transcript(root, sid):
    """cwd+sid 推导（§4.1 L2／§2 回读）：~/.claude/projects/<cwd 斜线转横线>/<sid>.jsonl"""
    return os.path.join(projects_dir(), root.replace("/", "-"), sid + ".jsonl")
