#!/usr/bin/env python3
# crules-flutter 记忆库漂移队列收尾提醒（Stop hook 读侧闭环——A3，2026-09-05 三审复核 §5 自守卫版）
# 机制：会话收尾时 .pending-updates 非空 → hookSpecificOutput.additionalContext 注入事实提醒，
#   模型可据此补索引（pending-updates.py 写侧的读侧对位；此前读侧仅 MAINTENANCE 自检清单软约定）
# 自守卫（防连环续轮——官方：additionalContext 与 decision:block 共享 stop_hook_active + 连续 8 次上限）：
#   stop_hook_active=true（本提醒刚触发的续轮）→ 直接 exit 0 不再提醒；自然停轮后队列仍非空会再提醒一次
#   ——接受此节奏（漂移本该尽快清），更复杂的「仅条数变化时提醒」留观测后再议
# 文案纪律：事实陈述（官方提示祈使句式系统指令可能触发注入防御）；hook 输出字符串 10k 字符上限
# 边界：不阻止停止、不写任何文件（只读队列）；Windows 无 python3 时本 hook 静默失效（同 deny-list，D3 降级警告兜底）。
# 输入契约 fail-open（批A F10①，1.0.11）：stdin 非法 JSON → exit 0 静默——输入由宿主构造风险低，
#   fail-closed 恐误伤非 JSON 探活；本 hook 只读队列、不阻止停止，静默即等价「无待办」（其静默四态已有 fixture 锁定）
# 批B F1（1.0.12）漂移盲区补充：Bash 落盘的文件（flutter create / mv / cp / 重定向 / build_runner
#   生成器）不经 PostToolUse（matcher 仅 Edit|Write|NotebookEdit）故不进队列——队列非空时额外
#   git status 快查，检出未入队的 A/D/? 源文件并入提醒。**设计取舍**：git 快查**不独立触发**
#   （未提交改动是开发常态，独立触发会在每次 Stop 重复打扰）——仅作队列非空时的补充信息，
#   故「纯 Bash 落盘会话」仍不提醒（诚实边界，待观测后定是否加状态文件去重）。耗时受 timeout 5s 约束
import json, os, subprocess, sys

# 流编码显式化（1.0.21，Windows 实机 P0-A）：宿主码页非 UTF-8 时本 hook 的 print 中文或崩
#   （该码页编不出该字，如 cp950 遇简体字形）或吐非 UTF-8 字节（cp936），两者都使提醒 JSON
#   一字未能按契约送达——与 deny-list.py 同批同因，见该文件头注的双码页实测与兜底链放大效应。
#   stdin 方向不抛（Windows 标准流 errors=surrogateescape），坏字节变孤立代理项＝失真非失败。
def _hook_utf8_streams():
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

_hook_utf8_streams()


def git_source_changes(root, known):
    """git status 检出未入队的源文件变更（A/D/?）——Bash 落盘盲区补充；非 git 仓/超时静默返回 []
    -uall 必需：默认 git 把未追踪**目录**折叠成单条目（?? lib/），展开才见具体文件"""
    try:
        p = subprocess.run(["git", "-C", root, "status", "--porcelain", "-uall"],
                           capture_output=True, text=True, timeout=5)
    except Exception:
        return []
    if p.returncode != 0:
        return []
    out = []
    for line in p.stdout.splitlines():
        if len(line) < 4:
            continue
        code, path = line[:2], line[3:].strip().strip('"')
        if not any(c in code for c in "AD?"):
            continue
        if not path.endswith(".dart") or path.endswith((".g.dart", ".freezed.dart", ".mocks.dart")):
            continue
        if path not in known:
            out.append(path)
    return out

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
msg = f"记忆库漂移队列非空：{len(lines)} 条待补索引（如 {first}）。"
extra = git_source_changes(os.getcwd(), set(lines))
if extra:
    msg += (f"另 git 检出 {len(extra)} 个未入队源文件变更（如 {extra[0][:80]}）"
            f"——Bash 落盘路径（create / mv / 重定向 / 生成器）不进 PostToolUse 队列，请一并核对。")
msg += ("本轮改动若已收尾，按 .claude/memory/MAINTENANCE.md 触发表补对应索引后清空 .pending-updates；"
        "仍在继续任务则可忽略本条，收尾时会再提示。")
print(json.dumps({"hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": msg[:10000]}}, ensure_ascii=False))
sys.exit(0)
