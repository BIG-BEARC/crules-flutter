#!/usr/bin/env python3
# crules-flutter 压缩恢复 v2 · PreCompact 观测件（2026-11-12；方案 docs/方案-压缩恢复v2-指针
#   与速率-2026-11-12.md §4.2——探针 1 判读通过后落码：trigger 字段在场携实值 manual/auto、
#   PreCompact 亦携 transcript_path＋prompt_id（§6.1 实弹判读）。生产登记形＝单条无 matcher
#   ——探针实证 catchall 与专属条同事件并发，双登记即同发双行）。
# 职责仅两件（§4.2）：①计数入主窗（trigger/sidechain 分桶＝_compact_core.bucket_for；
#   sidechain 无键＝混桶 any_ts 现行走档）②ledger schema 2 行（prompt_id＝同发身份键，
#   SessionStart 侧去重谓词的配对面——§4.1）。
# 零拦截、零注入（v1 D1 死锁结论不翻案）；async:false（hooks.json，防与 SessionStart 读窗竞态）；
# fail-open 同款：任何异常静默 exit 0、零 stdout（观测件无阻断无注入职责）。
# 写序＝ledger 先行、状态殿后：状态落盘失败时去重仍中（漏窗一发出现在阈值面＝灵敏度小损，
#   双记＝误触 runaway——方向取舍见 §4.1「漏计比误计危险」的反面，误计更危险故防双记）。
# 隐私对齐 D6：账行只落枚举/布尔/opaque id——custom_instructions 不落、transcript_path 不落。
# Windows 纪律：hooks.json python3||python 兜底链＋进程期 SetErrorMode 压框（七 hook 同款）。
import json
import os
import sys
import time

from _common import find_project_root, plugin_version, sanitize_sid, _hook_utf8_streams
from _compact_core import append_ledger, feed_window, ledger_row, load_state, save_state

if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.kernel32.SetErrorMode(0x0002)
    except Exception:
        pass

_hook_utf8_streams()

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if not isinstance(data, dict):
    sys.exit(0)
if data.get("hook_event_name") not in (None, "PreCompact"):
    sys.exit(0)   # 防御性：非本事件不介入
sid = sanitize_sid(data.get("session_id"))
if not sid:
    sys.exit(0)   # 缺 sid → 不记（防空串回落共享计数文件互染，沿 v1）
root = find_project_root(data.get("cwd") if isinstance(data.get("cwd"), str) else os.getcwd())
if not root:
    sys.exit(0)   # 无记忆库根 → 不介入（house 闸同款定根前提）

trigger = data.get("trigger") if data.get("trigger") in ("manual", "auto") else "unknown"
sc = data.get("sidechain")
sidechain = sc if isinstance(sc, bool) else None
pid = data.get("prompt_id") if isinstance(data.get("prompt_id"), str) else None

try:
    gdir_path = os.path.join(root, ".claude", "memory", "compact-gate")
    state_path = os.path.join(gdir_path, sid + ".json")
    st = load_state(state_path)
    _bucket, n = feed_window(st, trigger, sidechain, time.time())
    append_ledger(gdir_path, ledger_row(sid, trigger, sidechain, "compact",
                                        n, pid, "compact-observe", plugin_version()))
    save_state(state_path, st)
except Exception:
    pass   # fail-open：观测件绝不干扰宿主事件流
sys.exit(0)
