#!/usr/bin/env python3
# crules-flutter 记忆库漂移队列收尾提醒（Stop hook 读侧闭环——A3，2026-09-05 三审复核 §5 自守卫版）
# 机制（1.0.30 队列分文件对位读侧——D3/D4/D5/D8）：收尾时读**本会话自己的队列文件**——
#   - 项目根自 cwd 向上逐级找 .claude/memory/NAVIGATION.md 定根（D8，与写侧同源；cd 漂移不丢读侧）
#   - 有 session_id → .pending-updates.<sid>；自己为空且旧单文件存在 → 读旧单文件（D3——升级
#     存量一次性迁移读，写侧 1.0.30 起已不再写它）；无 session_id → 直接读旧单文件（D2 对位）
#   - 自己队列非空时顺带两件事：①孤儿只报不删（D4）——其他会话队列文件中 mtime 超 24h 的计一条数，
#     新鲜的不提（并行会话仍在途，不互扰）；②git 快查（批B F1）的「已入队」集合并入**所有**队列
#     文件的行（D5——他人已入队文件不再被误报成未入队）
#   - 自己队列与 legacy 皆空 → 静默退出（孤儿也不提——自己没事就闭嘴，防并行常态下互相打扰）
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
import json, os, subprocess, sys, time
from _common import (constitution_stamp, find_project_root, plugin_version,
                     sanitize_sid, version_key,
                     _hook_utf8_streams)  # 1.0.39 共享实现收编 / 1.0.40 陈旧检测三件入共享（hooks/_common.py）

# 进程期 AV 弹框压制（1.0.33，三 hook 同款同改；2026-09-22 A/B 实测）：Windows 注入型管控 agent
#   会使进程中途访问违例并弹模态框——hook 挂起等点击直至超时；脚本内 SetErrorMode(0x2) 即无框
#   静默死（rc 仍非零，走 1.0.22/1.0.24 兜底，判定行为零变化）。父进程预设会被 CPython 启动覆写
#   为 1，故必须脚本内设；压框失败仅退回原状；启动期 0xc0000142 族发生在用户代码前，不覆盖
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.kernel32.SetErrorMode(0x0002)
    except Exception:
        pass

ORPHAN_TTL = 24 * 3600  # 他人队列文件「孤儿」判定阈值（D4 只报不删；删除留给人）

# 流编码钉 UTF-8（1.0.21 Windows 实机 P0-A）——实现见 _common._hook_utf8_streams（1.0.39 收编）：
#   宿主码页非 UTF-8 时本 hook 的 print 中文或崩（该码页编不出该字，如 cp950 遇简体字形）或吐
#   非 UTF-8 字节（cp936），两者都使提醒 JSON 一字未能按契约送达。
_hook_utf8_streams()

def read_lines(path):
    try:
        with open(path, encoding="utf-8") as f:
            return [l.strip() for l in f if l.strip()]
    except OSError:
        return []

def norm_paths(ls):
    """队列行路径归一为正斜杠——与写侧落盘归一（pending-updates.py 1.0.30 R5 实测修）对位；
    兼容 1.0.30 之前 Windows 落下的反斜杠旧队列行，否则 git 正斜杠路径与之恒不匹配"""
    return {l.replace("\\", "/") for l in ls}

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
# 形状守卫（1.0.30 复读 N1，与写侧同）：JSON 解析成功 ≠ 形状合法——顶层非对象（[] / "x" / 123）
#   时 `data.get` 抛 AttributeError 且在 try 外即未捕获崩溃，与 fail-open 头注不符
if not isinstance(data, dict):
    sys.exit(0)
if data.get("stop_hook_active"):
    sys.exit(0)
root = find_project_root(os.getcwd())
if not root:
    sys.exit(0)
mem = os.path.join(root, ".claude", "memory")

# 宪法陈旧提醒闸（1.0.40 · N-1③）：项目 CLAUDE.md 版本戳 < 已装 plugin 版本 → 催升级。
#   位置钉在定根之后、队列读取之前——**独立于队列状态**：目标宿主（消费工程）常态恰是
#   「刚收尾、队列空」，挂进队列非空分支等于闸对着该响的人永不响（设计评审抓出的落点 bug）。
#   覆盖边界（如实）：轻量档工程（无 NAVIGATION）在上方 root 判定即退，收不到本提醒——与
#   compliance 落账、漂移队列同覆盖面对齐；无戳（老项目人工合并态）静默（stamp=None）。
#   升级动作本身不自动化（写用户工程文件=破坏性面，宪法规矩：提醒≠代执行）。
plug_ver = plugin_version()
stamp_ver = constitution_stamp(root)
stale = ""
if plug_ver and stamp_ver:
    pk, sk = version_key(plug_ver), version_key(stamp_ver)
    if pk and sk and pk > sk:
        stale = (f"宪法版本落后：项目 CLAUDE.md v{stamp_ver}，插件已 v{plug_ver}——"
                 '升级跑 bash "$CLAUDE_PLUGIN_ROOT/scripts/install.sh" <项目根> --upgrade'
                 "（插件若也旧先 claude plugin update；--yes 免确认）。")

def emit(context):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "Stop",
                                             "additionalContext": context[:10000]}}, ensure_ascii=False))

# 取值类型守卫（1.0.30 收口 R3，与写侧同）：合法 JSON 但 session_id 非字符串时 re.sub 会抛未捕获异常，
#   与头注 fail-open 契约不符——str 守卫使异型退化为「无此字段」语义
sid = sanitize_sid(data.get("session_id"))  # 与写侧 D6 同规则净化（实现见 _common，1.0.39 收编单源）
own_name = (".pending-updates." + sid) if sid else ".pending-updates"
src_name = own_name   # 报出的条目实际来自哪个队列文件（R6——D3 回退命中时文案须指向 legacy，否则用户清无可清）
lines = read_lines(os.path.join(mem, own_name))
if not lines and sid:
    lines = read_lines(os.path.join(mem, ".pending-updates"))  # D3：升级存量一次性迁移读
    if lines:
        src_name = ".pending-updates"
if not lines:
    if stale:
        emit(stale)   # 队列空也要响（1.0.40 落点 bug 回归钉）
    sys.exit(0)
first = lines[0][:120]
msg = (stale + f"记忆库漂移队列非空：{len(lines)} 条待补索引（如 {first}）。")
# D4/D5：他人队列文件——行并入已入队集合（D5），mtime 超 ORPHAN_TTL 计孤儿（D4 只报不删，删除留给人）
now = time.time()
orphans = 0
known = norm_paths(lines)
try:
    known |= norm_paths(read_lines(os.path.join(mem, ".pending-updates")))  # legacy 存量也算已入队
    for name in os.listdir(mem):
        if not name.startswith(".pending-updates.") or name == own_name:
            continue
        p = os.path.join(mem, name)
        known |= norm_paths(read_lines(p))
        try:
            if now - os.path.getmtime(p) > ORPHAN_TTL:
                orphans += 1
        except OSError:
            pass
except OSError:
    pass
if orphans:
    msg += f"另有 {orphans} 个其他会话队列文件超 24 小时未清（孤儿，可能来自崩溃或已收尾会话），可按 MAINTENANCE.md 自检清理。"
extra = git_source_changes(root, known)
if extra:
    msg += (f"另 git 检出 {len(extra)} 个未入队源文件变更（如 {extra[0][:80]}）"
            f"——Bash 落盘路径（create / mv / 重定向 / 生成器）不进 PostToolUse 队列，请一并核对。")
clear_hint = (f"清空本会话队列文件 {own_name}" if src_name == own_name
              else "清空旧单文件 .pending-updates（升级存量，写侧 1.0.30 起已不再写它）")
msg += (f"本轮改动若已收尾，按 .claude/memory/MAINTENANCE.md 触发表补对应索引后{clear_hint}；"
        "仍在继续任务则可忽略本条，收尾时会再提示。")
emit(msg)
sys.exit(0)
