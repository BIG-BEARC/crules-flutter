#!/usr/bin/env python3
# crules-flutter 记忆库漂移提醒队列（PostToolUse，随 plugin 分发）
# 机制（1.0.30 队列分文件——D1/D2/D6/D8）：Edit/Write 成功后，若项目启用了记忆库且被改文件
#   是包外源文件，则把其路径追加进**本会话自己的队列文件**（去重）：
#   - 项目根不再用 cwd 直拼，而是自 cwd **向上逐级找 .claude/memory/NAVIGATION.md** 定根
#     （D8——会话 cd 进子目录后 cwd 漂移，旧写法 `.claude/memory` 落空 → 整段静默丢队列）
#   - 有 session_id → .claude/memory/.pending-updates.<sid>（D1——并行会话各写各队列、收尾
#     各清各的，根治共享工作树下的队列互踩；sid 净化 [A-Za-z0-9_-] 后充当文件名，D6）
#   - 无 session_id → 旧单文件 .pending-updates（D2 兼容旧宿主；读侧 D3 对位做存量迁移读）
# 边界（v18 复盘）：不判意图、不阻止任何操作——只是把「记得更新索引」从记忆问题变成看得见的待办；
#   会话收尾主控看到队列非空即提示补索引（MAINTENANCE.md 自检清单）。
# 输入契约 fail-open（批A F10①，1.0.11）：stdin 非法 JSON → exit 0 静默——输入由宿主构造风险低，
#   fail-closed 恐误伤非 JSON 探活；本 hook 本就不阻止任何操作，静默即等价「无待办」
import json, os, re, sys

MAX_SID = 80  # sid 作文件名时的截断长度（与 stop-reminder.py 同源常量，改动需同步）

# stdin 编码显式化（1.0.21，Windows 实机 P0-A）：宿主送来的 JSON 是 UTF-8，非 UTF-8 码页
#   （简中 936 / 繁中 950…）下按码页解——实测**不抛**（Windows 标准流 errors=surrogateescape），
#   坏字节变孤立代理项：file_path 含非 ASCII（中文目录名）时被解成垃圾串，仍会写进队列但条目
#   不可用（失真，非漏记）。本 hook 不写 stdout/stderr（输出侧无 P0-A 之病），故只钉输入流。
try:
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

def find_project_root(start):
    """自 start 向上逐级找含 .claude/memory/NAVIGATION.md 的目录（1.0.30 D8）；到盘根未中 → None
    **与 stop-reminder.py 的 find_project_root 同源，改动须两处同步**（两 hook 随 plugin 独立分发，不引共享模块）"""
    d = os.path.abspath(start)
    while True:
        if os.path.exists(os.path.join(d, ".claude", "memory", "NAVIGATION.md")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
# 形状守卫（1.0.30 复读 N1）：JSON 解析成功 ≠ 形状合法——顶层非对象（[] / "x" / 123 / null）时
#   `data.get` 抛 AttributeError 且在 try 外即未捕获崩溃，与 fail-open 头注不符（崩溃路径实测复现）。
if not isinstance(data, dict):
    sys.exit(0)
# 取值类型守卫（1.0.30 收口 R3）：fail-open 契约不能只护非法 JSON——**合法 JSON 但字段异型**
#   （tool_input 非 dict / file_path 非字符串）时，下方 .get / realpath 会抛未捕获异常或产垃圾条目。
#   file_path 走严格类型判定：非字符串一律按「无此字段」退场（str() 化会把 12345 变成垃圾路径入队）。
_ti = data.get("tool_input")
fp = _ti.get("file_path") if isinstance(_ti, dict) else None
if not isinstance(fp, str) or not fp:
    sys.exit(0)
root = find_project_root(os.getcwd())
if not root:
    sys.exit(0)  # 记忆库未启用 → 不介入
mem = os.path.join(root, ".claude", "memory")
real = os.path.realpath(fp)
if real.startswith(os.path.realpath(mem) + os.sep):  # 记忆库自身文件不记
    sys.exit(0)
norm = real.replace(os.sep, "/")  # Windows 反斜杠路径归一后再判——旧写法正斜杠字面串在 Windows 恒不命中（1.0.30 D8 顺手修）
if "/.claude/" in norm or "/.git/" in norm:  # 配置与 git 内部不记
    sys.exit(0)
# sid → 文件名（净化规则与 stop-reminder.py 同源，改动须同步）
sid = re.sub(r"[^A-Za-z0-9_-]", "-", str(data.get("session_id") or ""))[:MAX_SID]  # D6 净化 + 截断
queue = os.path.join(mem, (".pending-updates." + sid) if sid else ".pending-updates")
try:
    lines = set()
    if os.path.exists(queue):
        with open(queue, encoding="utf-8") as f:
            # 读旧行**一并归一**（复读 N2）：队列若含 1.0.30 前 Windows 反斜杠行，再次入队时须
            #   自愈为单行正斜杠，否则同一文件在队列留正/反斜杠两行（去重按原始串比对）且永不自愈
            lines = {l.strip().replace("\\", "/") for l in f if l.strip()}
    # 入队路径落盘**统一正斜杠**（1.0.30 R5 实测修）：Windows 上 os.path.relpath 返回反斜杠，
    #   而 git status --porcelain 恒输出正斜杠（本机实测签名 M skills/flutter-rules/...）——
    #   不归一则读侧 `path not in known` 在 Windows 恒不匹配，「已入队不重复报」与 D5 声称双双失效
    lines.add(os.path.relpath(real, root).replace("\\", "/"))
    with open(queue, "a+", encoding="utf-8") as f:  # a+ 使 flock 生效于已存在/新建文件
        try:
            import fcntl
            fcntl.flock(f, fcntl.LOCK_EX)           # 防并发 async hook 读-改-写竞态
        except ImportError:
            pass  # Windows 无 fcntl（D3，2026-09-05）：降级无锁追加——O_APPEND 单行写具原子性，竞态窗口远小于「完全不记」
        f.seek(0)
        # 归一须两处都做：本行是 flock 后为防竞态的重读，**同样含旧行**——初版只归一了上面那次读取，
        #   被 N2 断言当场抓住（队列留正/反斜杠两行）
        lines |= {l.strip().replace("\\", "/") for l in f.read().splitlines() if l.strip()}
        f.seek(0); f.truncate()
        f.write("\n".join(sorted(lines)) + "\n")
except Exception:
    pass
sys.exit(0)
