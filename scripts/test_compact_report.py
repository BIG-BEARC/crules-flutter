#!/usr/bin/env python3
# compact-report.py fixture（压缩恢复 v2 · 2026-11-12，方案 §4.3 翻账件——只读、零正文，
#   头注释声明对齐 D6；试点判据①频次/主子比/trigger 比、判据⑤runaway 检出上报通路的数据面）：
#   - 按工程聚合：频次（按 sid）＋trigger 比（auto/manual/unknown）＋主子比（sidechain
#     true/false/null＝主/子/混）＋runaway / runaway-sub / handoff 清单
#   - 双 schema 兼容：schema 1 旧行（compact-1st/nth/muted，无 trigger/sidechain）计频次入
#     unknown/混桶——33 行存量不迁移（方案盲区三扫）
#   - 只读断言：运行前后 ledger 字节不变（mtime/内容双面）
#   - 零正文断言：输出不含工程路径/对话内容——只有 ledger 字段聚合值
import hashlib
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
REPORT = os.path.join(HERE, "compact-report.py")
fails = 0
NOW = time.time()


def check(name, cond):
    global fails
    print(("PASS  " if cond else "FAIL  ") + name)
    if not cond:
        fails += 1


def iso(epoch):
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(epoch))


def proj_with(rows):
    d = tempfile.mkdtemp(prefix="cf-creport.")
    g = os.path.join(d, ".claude", "memory", "compact-gate")
    os.makedirs(g)
    with open(os.path.join(g, "ledger.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return d


def run_report(*args):
    p = subprocess.run([sys.executable, REPORT, *args], capture_output=True)
    return p.returncode, p.stdout.decode()


rows = [
    # schema 2：sA 5 发压缩（auto3/manual1/unknown1；主2/子1/混2）＋runaway 2＋handoff 1
    {"schema": 2, "ts": iso(NOW - 4000), "sid": "sA", "trigger": "auto", "sidechain": False,
     "event": "compact", "n_window": 1, "plugin_ver": "1.3.8", "hook": "compact-observe", "prompt_id": "p1"},
    {"schema": 2, "ts": iso(NOW - 3600), "sid": "sA", "trigger": "auto", "sidechain": False,
     "event": "compact", "n_window": 2, "plugin_ver": "1.3.8", "hook": "compact-observe", "prompt_id": "p2"},
    {"schema": 2, "ts": iso(NOW - 3000), "sid": "sA", "trigger": "auto", "sidechain": None,
     "event": "compact", "n_window": 3, "plugin_ver": "1.3.8", "hook": "compact-observe", "prompt_id": "p3"},
    {"schema": 2, "ts": iso(NOW - 2000), "sid": "sA", "trigger": "manual", "sidechain": None,
     "event": "compact", "n_window": None, "plugin_ver": "1.3.8", "hook": "compact-observe", "prompt_id": "p4"},
    {"schema": 2, "ts": iso(NOW - 1000), "sid": "sA", "trigger": "unknown", "sidechain": True,
     "event": "compact", "n_window": 1, "plugin_ver": "1.3.8", "hook": "compact-gate", "prompt_id": None},
    {"schema": 2, "ts": iso(NOW - 3500), "sid": "sA", "trigger": "auto", "sidechain": False,
     "event": "runaway", "n_window": 8, "plugin_ver": "1.3.8", "hook": "compact-gate"},
    {"schema": 2, "ts": iso(NOW - 900), "sid": "sA", "trigger": "auto", "sidechain": None,
     "event": "runaway", "n_window": 8, "plugin_ver": "1.3.8", "hook": "compact-gate"},
    {"schema": 2, "ts": iso(NOW - 800), "sid": "sB", "trigger": "runaway", "sidechain": None,
     "event": "handoff", "n_window": 3, "plugin_ver": "1.3.8", "hook": "compact-gate"},
    # schema 1 旧行（v1 存量形态）：sB 2 发压缩
    {"schema": 1, "ts": iso(NOW - 5000), "sid": "sB", "plugin_ver": "1.3.5",
     "hook": "compact-gate", "event": "compact-1st", "count": 1, "verdict": None},
    {"schema": 1, "ts": iso(NOW - 4800), "sid": "sB", "plugin_ver": "1.3.5",
     "hook": "compact-gate", "event": "compact-nth", "count": 2, "verdict": "continue"},
    # schema 2：sB 子代理聚合
    {"schema": 2, "ts": iso(NOW - 700), "sid": "sB", "trigger": "auto", "sidechain": True,
     "event": "runaway-sub", "n_window": 20, "plugin_ver": "1.3.8", "hook": "compact-gate"},
]
d = proj_with(rows)
lpath = os.path.join(d, ".claude", "memory", "compact-gate", "ledger.jsonl")
with open(lpath, "rb") as f:
    digest_before = hashlib.sha256(f.read()).hexdigest()

rc, out = run_report(d)
ok = rc == 0 and "sid sA: 5 发" in out and "auto 3 / manual 1 / unknown 1" in out \
    and "主 2 / 子 1 / 混 2" in out and "sid sB: 2 发" in out and "unknown 2" in out
check("按 sid 聚合频次＋trigger 比＋主子比（schema2 行）", ok)

ok = "runaway: 2 笔" in out and "runaway-sub: 1 笔" in out and "handoff: 1 笔" in out \
    and iso(NOW - 3500) in out and "sid=sA" in out
check("runaway / runaway-sub / handoff 清单（ts＋sid 可寻址）", ok)

ok = "schema1 2＋schema2 9" in out and "compact-1st" not in out
check("双 schema 兼容：v1 旧行计频次（unknown 桶）且不报内部事件名", ok)

with open(lpath, "rb") as f:
    digest_after = hashlib.sha256(f.read()).hexdigest()
ok = digest_before == digest_after
check("只读：运行前后 ledger 字节不变", ok)

ok = d not in out and "transcript" not in out.lower() and "prompt_id" not in out
check("零正文：输出不含工程路径/transcript/prompt_id（D6 对齐）", ok)

d2 = tempfile.mkdtemp(prefix="cf-creport.")
os.makedirs(os.path.join(d2, ".claude", "memory", "compact-gate"))
open(os.path.join(d2, ".claude", "memory", "compact-gate", "ledger.jsonl"), "w").close()
rc, out = run_report(d2)
ok = rc == 0 and "0 行" in out
check("空 ledger → 友好输出 exit 0", ok)

rc, out = run_report()
ok = rc != 0 and "用法" in (out + "（缺工程根参数）")
check("无参数 → usage 非零退出", ok)

d3 = tempfile.mkdtemp(prefix="cf-creport.")
rc, out = run_report(d3)
ok = rc == 0 and "无 ledger" in out
check("无 compact-gate 目录 → 明示无账本 exit 0（不崩不猜）", ok)

print(f"compact-report fixture: {'全绿' if fails == 0 else f'{fails} 失败'}")
sys.exit(1 if fails else 0)
