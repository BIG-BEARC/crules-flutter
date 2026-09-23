#!/usr/bin/env python3
# crules-flutter hooks 共享实现（1.0.39 · docs/裁决单-2026-09-22-防漂移批 D-1，需求方批准）
# 收编此前各 hook 逐字重复的三件事：找项目根 / sid 净化截断 / 三流钉 UTF-8。
#   历史：pending/stop/compliance 三份 find_project_root+MAX_SID、stop/deny/compliance 三份
#   _hook_utf8_streams——各文件以「改动须两处同步」注释互指维持，无机械保障（幻影决策
#   「不引共享模块」的核实与推翻过程见裁决单 §0 末行）。
# 分发说明：hook 由 hooks.json 以 python3 <插件目录>/hooks/x.py 整目录随 plugin 安装启动，
#   Python 将脚本所在目录置于 sys.path[0]，`import _common` 直接可用，无需路径样板。
# 改动纪律：本文件被全部 python hook import——语法/行为错误爆炸半径为四 hook 齐坏；
#   防线=CI/test-self 的 compileall（1.0.39 起自动覆盖本文件）+ 各 hook fixture 子进程实跑。
import json
import os
import re
import sys

MAX_SID = 80  # sid 作文件名时的截断长度


def find_project_root(start):
    """自 start 向上逐级找含 .claude/memory/NAVIGATION.md 的目录（1.0.30 D8）；到盘根未中 → None"""
    d = os.path.abspath(start)
    while True:
        if os.path.exists(os.path.join(d, ".claude", "memory", "NAVIGATION.md")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def sanitize_sid(raw):
    """session_id 净化为文件名片段（D6）：非 [A-Za-z0-9_-] 换 '-'，截断 MAX_SID；
    str() 化使异型入参（1.0.30 R3：合法 JSON 但 session_id 非字符串）退化为字符串语义不抛"""
    return re.sub(r"[^A-Za-z0-9_-]", "-", str(raw or ""))[:MAX_SID]


def plugin_version():
    """已安装插件的版本（账行打标 / 宪法陈旧检测共用）——CLAUDE_PLUGIN_ROOT 由宿主注入
    （hook 进程必得；fixture 显式设）。缺 env / 读不到 / 形状不合 → None（调用侧静默）"""
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


def constitution_stamp(root):
    """项目 CLAUDE.md 的 crules-flutter 版本戳（install.sh STAMP 同形态，首匹配同 install.sh
    grep head -1 行为）；无文件 / 无戳 → None（老项目人工合并态——陈旧检测对 None 静默）"""
    try:
        with open(os.path.join(root, "CLAUDE.md"), encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return None
    m = re.search(r"<!-- crules-flutter: v(\d+\.\d+\.\d+)", text)
    return m.group(1) if m else None


def version_key(ver):
    """'1.0.25' → (1,0,25) 供版本序比较；非纯数字段 → None（调用侧静默）"""
    try:
        return tuple(int(p) for p in ver.split("."))
    except ValueError:
        return None


def _hook_utf8_streams():
    """非 UTF-8 码页宿主（简中 936 / 繁中 950…）下 print 中文崩或吐非 UTF-8 字节、
    读侧坏字节失真（1.0.21 Windows 实机 P0-A）——三流显式钉 UTF-8，errors=replace 两侧兜底"""
    for name in ("stdin", "stdout", "stderr"):
        s = getattr(sys, name, None)
        if s is None:
            continue
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
            continue
        except Exception:
            pass
        try:   # Python < 3.7 无 reconfigure：退到重包 TextIOWrapper
            import io
            setattr(sys, name, io.TextIOWrapper(s.buffer, encoding="utf-8", errors="replace"))
        except Exception:
            pass
