#!/usr/bin/env python3
# crules 记忆库漂移队列收尾提醒（Stop hook 读侧闭环——A3，2026-09-05 复核之复核 §5 自守卫版）
# 机制：会话收尾时 .pending-updates 非空 → hookSpecificOutput.additionalContext 注入事实提醒，
#   模型可据此补索引（pending-updates.py 写侧的读侧对位；此前读侧仅 MAINTENANCE 自检清单软约定）
# 自守卫（防连环续轮——官方：additionalContext 与 decision:block 共享 stop_hook_active + 连续 8 次上限）：
#   stop_hook_active=true（本提醒刚触发的续轮）→ 直接 exit 0 不再提醒；自然停轮后队列仍非空会再提醒一次
#   ——接受此节奏（漂移本该尽快清），更复杂的「仅条数变化时提醒」留观测后再议
# 文案纪律：事实陈述（官方提示祈使句式系统指令可能触发注入防御）；hook 输出字符串 10k 字符上限
# 边界：不阻止停止、不写任何文件（只读队列）；Windows 无 python3 时本 hook 静默失效（同 deny-list，D3 降级警告兜底）
import json, os, sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if data.get("stop_hook_active"):
    sys.exit(0)
queue = os.path.join(os.getcwd(), ".claude", "memory", ".pending-updates")
try:
    lines = [l.strip() for l in open(queue, encoding="utf-8") if l.strip()]
except OSError:
    sys.exit(0)
if not lines:
    sys.exit(0)
first = lines[0][:120]
msg = (
    f"记忆库漂移队列非空：{len(lines)} 条待补索引（如 {first}）。"
    f"本轮改动若已收尾，按 .claude/memory/MAINTENANCE.md 触发表补对应索引后清空 .pending-updates；"
    f"仍在继续任务则可忽略本条，收尾时会再提示。"
)
print(json.dumps({"hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": msg[:10000]}}, ensure_ascii=False))
sys.exit(0)
