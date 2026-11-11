#!/usr/bin/env python3
# crules-flutter no-op 风暴闸（PreToolUse(Bash) hook · 2026-11-10，docs/方案-no-op风暴闸-2026-11-10.md
#   v2 已确认态——评审 docs/评审-plan-no-op风暴闸-2026-11-10.md 12 发现全数处置、需求方六裁 Q1–Q6）
# 立论（事故档案 super_printer 7afd4984/T2 子代理 a3202cc0，2026-11-10 诊断）：等待后台事件的会话
#   连发裸 no-op（true/:），每次＝一次全上下文 API 往返——44 分钟 446 次 ≈52.8M cache_read；
#   且模型已知正确姿势仍不改变行为（转录 L149 自证）→ 文案说教不可承重，须机械闸。
# 触发（D2，参数级可调）：同 sid 300s 滑动窗口内计数**达 15 后，第 16 发起 deny**——窗口率而非连发
#   计数（事故实况：真实排障命令与 no-op 交错，连发计数永不触发）。
# 升级（D8，Q6 需求方裁加）：同窗 deny 计达 5 次仍在发 → permissionDecision:"ask" 强制人裁弹窗
#   （deny-list ask 先例：自动批准模式下仍弹）——事故终局本就是人工中断，弹窗＝唯一不依赖模型
#   顺从的止损失口；ask 语义＝强制人看见（放行单次/拒绝/中断会话），非三选裁决。
# 出口契约（D9，评审阻塞发现 1 修复）：deny/ask 一律 JSON hookSpecificOutput.permissionDecision
#   ＋ reason ＋ **exit 0**——exit 2 会被 hooks.json 兜底链（python3 … || python …）拉起第二解释器
#   （空 stdin→fail-open exit 0）洗白成静默放行；exit 0 使 || 短路、JSON 判定幸存（deny-list
#   blocked()/warned() 同款，deny-list.py 头注 L93–L128 记载的正源）。
# 失效方向（D7）：**fail-open 放行**——止损闸与 deny-list 安全闸方向相反（安全闸自失效改判 ask，
#   见 deny-list gate_self_failure；本闸自失效弹窗比漏拦一次空转更扰人）。空 stdin（兜底链二次读）
#   /非 JSON/畸形形状/状态档坏损读写异常 → 一律 exit 0 静默；未捕获异常亦 exit 0（不设 ask 兜底）。
# 无根行为（Q5 需求方裁）：无记忆库根（find_project_root 为空）→ 静默不介入（compact-gate 同款
#   house 定根前提；代价＝无根工程零防护，方案 §1 盲区三扫声明）。
# 匹配面（D3＋诚实边界）：命令剥空白/尾注释后**整串等于** true 或 : —— `true && x`、`x || true`、
#   `sleep N`、`true;`（尾分号）、`TRUE`（大写）、echo 谈论等一律不计；绕行形态（/usr/bin/true、
#   command true、env true、FOO=bar true）**明知不堵**（止损闸只保已知形态，绕行升级留给观察窗）。
# 状态档（D5，Q4 需求方裁双形态）：.claude/memory/no-op-gate/<sanitize_sid>.json（窗口计数，
#   写时自修剪超窗两倍旧项；首命中顺带清扫 >7 天孤儿 sid 档——PreToolUse 无 startup 事件，
#   以「本 sid 首命中」为清扫时机，ledger 不在清扫面）；ledger.jsonl append-only 零重写只追加
#   （多会话同仓并发无锁纪律）。隐私对齐 compliance-audit：cmd 字段恒为裸 no-op 字面（true/:），
#   零对话正文。
# 口径注（评审发现 12）：同会话并发子代理共享父 sid 桶＝总负担口径，刻意为之（compact-gate
#   subagent 同桶先例）。
import json
import os
import re
import sys
import time
from _common import (find_project_root, plugin_version, sanitize_sid,
                     _hook_utf8_streams)

if sys.platform == "win32":
    try:   # 进程期 AV 弹框压制（六 hook 同款，deny-list 头注 L63+ 段详注）
        import ctypes
        ctypes.windll.kernel32.SetErrorMode(0x0002)
    except Exception:
        pass

WINDOW = 300.0        # 滑动窗口秒（D2）
HIT_LIMIT = 15        # 计数达此值后，下一发起 deny（Q2 默认随批可调）
ASK_AFTER_DENY = 5    # 同窗 deny 计达此值后，后续发改 ask（Q6）
ORPHAN_TTL = 7 * 86400  # 孤儿 sid 状态档清扫阈值（首命中顺带）

BARE_NOOP = re.compile(r"^(true|:)(\s*#.*)?$")   # 匹配前先 strip（首尾空白剥净，方案 D3 原话）

DENY_MSG = ("[no-op-gate] 检测到 no-op 风暴（300s 内 ≥15 次裸 true/:）。每次无操作命令＝一次"
            "全上下文 API 往返。改用其一：①单条带超时的等待命令（如 `sleep 30 && tail -c 500 "
            "<输出档>` 或 `until <条件>; do sleep 5; done`，一次调用等到事件）；②主线程可直接"
            "结束回合等事件唤醒。子代理注意：宿主「不要结束回合」指勿以最终回复收尾（那会终止你），"
            "中途等待用①即可。不要再发裸 no-op。")
ASK_MSG = ("[no-op-gate·人裁] 本会话 no-op 风暴已 deny 5 次仍在持续（模型在等待后台事件时空转，"
           "每轮≈全上下文 API 往返）。放行本次／拒绝并让它换姿势／直接中断会话，由你定。")

_hook_utf8_streams()

try:
    raw = sys.stdin.read()
except Exception:
    sys.exit(0)
if not raw.strip():
    sys.exit(0)   # 空 stdin＝兜底链二次读（首解释器非零退出）→ fail-open（止损方向，头注 D7）
try:
    data = json.loads(raw)
except Exception:
    sys.exit(0)   # 非空非法 JSON（探活族）→ fail-open（deny-list F10① 同判）
if not isinstance(data, dict):
    sys.exit(0)
_ti = data.get("tool_input")
cmd = _ti.get("command") if isinstance(_ti, dict) else None
if not isinstance(cmd, str) or not BARE_NOOP.match(cmd.strip()):
    sys.exit(0)   # 非裸 no-op：不计不拦零成本放行（匹配面前置，误伤面第一道）
sid = sanitize_sid(data.get("session_id"))
if not sid:
    sys.exit(0)   # 缺 sid → 不计不拦（防空串回落共享计数文件互染，compact-gate 同判）
cwd = data.get("cwd") if isinstance(data.get("cwd"), str) else os.getcwd()
root = find_project_root(cwd)
if not root:
    sys.exit(0)   # Q5：无记忆库根 → 静默不介入

try:   # 判据体整体 fail-open（D7：任何未预期异常 → 放行，不设 ask 兜底）
    gdir = os.path.join(root, ".claude", "memory", "no-op-gate")
    state_path = os.path.join(gdir, sid + ".json")
    first_hit = not os.path.exists(state_path)
    now = time.time()
    cutoff = now - WINDOW

    st = {"hits": [], "denies": []}
    try:
        with open(state_path, encoding="utf-8") as f:
            loaded = json.load(f)
        if isinstance(loaded, dict):
            for key in ("hits", "denies"):
                v = loaded.get(key)
                if isinstance(v, list):
                    st[key] = [t for t in v if isinstance(t, (int, float))]
    except Exception:
        pass   # 坏/缺状态档 → 重计（fail-open）

    # 窗口修剪（deny 计数同窗口径）→ 计入本次命中 → 判定
    st["hits"] = [t for t in st["hits"] if t >= cutoff]
    st["denies"] = [t for t in st["denies"] if t >= cutoff]
    st["hits"].append(now)
    decision = "allow"
    if len(st["hits"]) > HIT_LIMIT:
        if len(st["denies"]) >= ASK_AFTER_DENY:
            decision = "ask"
        else:
            decision = "deny"
            st["denies"].append(now)

    try:   # 状态档保存失败 → 本次判定照出（下轮重计，fail-open 方向）
        os.makedirs(gdir, exist_ok=True)
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(st, f, ensure_ascii=False)
        if first_hit:   # 本 sid 首命中顺带孤儿清扫（>7 天 sid 档；ledger/非 .json 不在清扫面）
            try:
                for name in os.listdir(gdir):
                    p = os.path.join(gdir, name)
                    if name.endswith(".json") and os.path.getmtime(p) < now - ORPHAN_TTL:
                        os.remove(p)
            except OSError:
                pass
    except Exception:
        pass

    try:   # 台账只追加（append-only 零重写；记账失败不阻断判定）
        with open(os.path.join(gdir, "ledger.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"schema": 1,
                                 "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                                 "sid": sid,
                                 "plugin_ver": plugin_version(),
                                 "hook": "no-op-gate",
                                 "event": "hit",
                                 "cmd": cmd.strip(),
                                 "decision": decision}, ensure_ascii=False) + "\n")
    except Exception:
        pass

    if decision in ("deny", "ask"):
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
              "permissionDecision": decision,
              "permissionDecisionReason": DENY_MSG if decision == "deny" else ASK_MSG}},
              ensure_ascii=False))
except Exception:
    pass
sys.exit(0)
