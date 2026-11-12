#!/usr/bin/env python3
# crules-flutter 压缩恢复 v2 · 翻账件（2026-11-12；方案 docs/方案-压缩恢复v2-指针与速率-
#   2026-11-12.md §4.3）。**只读、零正文**（头注释声明对齐 D6）：本件只读 ledger 字段做
#   聚合——频次（按 sid）/trigger 比（auto·manual·unknown）/主子比（sidechain
#   true·false·null＝子·主·混）/runaway·runaway-sub·handoff 清单；不触 transcript、
#   不落任何文件、输出零对话正文零路径（工程路径也不印——只印 basename）。
# 双 schema 兼容：schema 1 旧行（compact-1st/nth/muted，无 trigger/sidechain）计频次入
#   unknown/混桶——33 行存量不迁移（方案盲区三扫）；内部事件名不外印。
# 试点判据挂点（§6.2）：①频次对读（before/after，主/子口径分列）⑤runaway 检出→上报通路演练。
# 用法：python3 compact-report.py <工程根> [<工程根>…]　（无参数 → usage 退出 1）
import json
import os
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

TRIG_KEYS = ("auto", "manual", "unknown")


def report(root):
    print(f"== compact-gate 翻账（{time.strftime('%Y-%m-%dT%H:%M:%S%z')}）==")
    path = os.path.join(root, ".claude", "memory", "compact-gate", "ledger.jsonl")
    rows = []
    if not os.path.exists(path):
        print(f"无 ledger（未部署或未压缩）：{os.path.basename(root.rstrip('/'))}")
        return
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if isinstance(r, dict):
                rows.append(r)
    n1 = sum(1 for r in rows if r.get("schema") == 1)
    n2 = sum(1 for r in rows if r.get("schema") == 2)
    compacts = [r for r in rows if str(r.get("event", "")).startswith("compact")]
    runaways = [r for r in rows if r.get("event") == "runaway"]
    subs = [r for r in rows if r.get("event") == "runaway-sub"]
    handoffs = [r for r in rows if r.get("event") == "handoff"]
    print(f"ledger: {len(rows)} 行（schema1 {n1}＋schema2 {n2}）；压缩 {len(compacts)} 发")
    sids = []
    for r in compacts:
        if r.get("sid") not in sids:
            sids.append(r.get("sid"))
    for s in sids:
        mine = [r for r in compacts if r.get("sid") == s]
        trig = {k: 0 for k in TRIG_KEYS}
        bkt = {"主": 0, "子": 0, "混": 0}
        for r in mine:
            trig[r.get("trigger") if r.get("trigger") in TRIG_KEYS else "unknown"] += 1
            sc = r.get("sidechain")
            bkt["子" if sc is True else "主" if sc is False else "混"] += 1
        print(f"sid {s}: {len(mine)} 发（auto {trig['auto']} / manual {trig['manual']} / "
              f"unknown {trig['unknown']}｜主 {bkt['主']} / 子 {bkt['子']} / 混 {bkt['混']}）")
    print(f"runaway: {len(runaways)} 笔")
    for r in runaways:
        print(f"  - {r.get('ts')} sid={r.get('sid')} n_window={r.get('n_window')}")
    print(f"runaway-sub: {len(subs)} 笔")
    for r in subs:
        print(f"  - {r.get('ts')} sid={r.get('sid')} n_window={r.get('n_window')}")
    print(f"handoff: {len(handoffs)} 笔")
    for r in handoffs:
        print(f"  - {r.get('ts')} sid={r.get('sid')} trigger={r.get('trigger')}")


def main():
    if len(sys.argv) < 2:
        print("用法：python3 compact-report.py <工程根> [<工程根>…]")
        return 1
    for root in sys.argv[1:]:
        try:
            report(root)
        except Exception as e:   # 单工程失败不阻断多工程翻账
            print(f"（{os.path.basename(root.rstrip('/'))} 读取失败：{type(e).__name__}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
