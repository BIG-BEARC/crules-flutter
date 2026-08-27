#!/usr/bin/env python3
# SYNCED-FROM: crules@ea4d25c（deny-list.py——deny-list 安全修复以 crules 为单一权威，CI 同步比对步看守；变更须从 crules 同步后再动此文件）
# crules 破坏性命令 deny-list（PreToolUse 硬闸，随 plugin 分发）
# 原则：只 deny 无歧义的破坏性命令，**不做任何意图判断**；被拦即请需求方人工执行
# 名单（git + rm）：
#   git push --force（独立词匹配：--force-with-lease 单用放行；lease 在前 -f/--force 在后仍拦）/
#   +refspec 强推 / push --delete·:branch /
#   git reset --hard / git clean -f（-n dry-run 放行）/ git branch -D /
#   git checkout·restore·switch 丢弃工作区（pathspec：裸 . / ./ / -- . / :/ 全树 / * glob，**剥配对引号**；
#   -f/--force 强切且非建分支 -b/-c/指定源 -s）/ git stash clear（§2 对齐；drop·pop 不拦——v40 裁决）/ rm 递归+强制
# 匹配策略（v39 换轴，v40 收边）：
#   - 分段（; && || | 换行）后，git/rm 签名用**非锚定搜索**——前缀（sudo/env/FOO=1/带参）、
#     包裹（( )/$( )/反引号）、全局选项（git -C dir）一次吃掉，不枚举前缀词（打地鼠）
#   - token 判定前剥**配对引号**（一处治两病：引号 pathspec 逃逸 + 引号白名单路径误拦）
#   - rm 白名单用 **normpath 而非 realpath**（macOS /tmp→/private/tmp 符号链接，realpath 反而
#     误拦合法白名单；符号链接别名攻击明确不在防线内）
# 边界与局限（诚实声明）：
#   - 非锚定搜索会把字符串里的破坏命令一并拦下（如 echo '…git reset --hard…'）——按
#     deny-by-default 哲学接受，误拦走白名单调整
#   - **黑名单无法穷尽**——本 hook 是安全网而非沙箱，终极防线是 Claude Code 原生权限确认与需求方审阅
# 覆盖矩阵（C7，v50——哪些风险由谁兜底）：
#   | 风险类别                                                      | hook | 其余兜底 |
#   | git 破坏族（强推/硬重置/强删分支/丢弃工作区/clean/stash clear） | ✅拦 | fixture 回归；误拦走白名单 |
#   | rm 递归+强制（含 xargs 注入的空操作数形态）                    | ✅拦 | /tmp·/var/folders 白名单（normpath） |
#   | chmod -R / chown -R / find -delete / python -c 删文件         | ❌   | 根规则「风险操作先确认」+ 原生权限确认 |
#   | 变量拼接 / 嵌套 eval / 写脚本再执行 / stdin 注入路径            | ❌   | 同上（黑名单无法穷尽，归需求方审阅） |
# v47 收口（红→绿 fixture 先行）：push/branch/force_switch 旗标判定统一走 parse_flags（拆捆绑短旗标，-fv/-qf/-D 等价拼法一次收敛）；
#   push dry-run×force 组合信号即拦（裁定 B：clean -nd 是正当诊断、push -fn 不是，不对称有理由）；rm 空操作数拦（deny-by-default：
#   空操作数 rm -rf 为静默 no-op，典型场景即 xargs/stdin 注入）；重定向 token 剥离后再判白名单（修 /tmp/x 2>/dev/null 误拦）
# 决策边界（v18 复盘）：v18-A 撤销的是「意图判断类」hook；本 hook 不判意图、deny-by-default
import json, os, re, sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
cmd = (data.get("tool_input") or {}).get("command") or ""
if not cmd.strip():
    sys.exit(0)

def blocked(reason):
    reason += "；请需求方人工执行，不要尝试绕过（如需展示命令，直接在回复中写文本）"
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    sys.exit(0)

GIT_SIG = re.compile(r"\bgit\b[^;|]*?\b(push|reset|clean|branch|checkout|restore|switch|stash)\b")
RM_SIG = re.compile(r"(^|[\s(`$!])rm\b")

def strip_quotes(tok):
    """剥配对引号：'"."'→'.'（带空格的引号路径 split 不开，属既有局限，头注声明）"""
    if len(tok) >= 2 and tok[0] == tok[-1] and tok[0] in "\"'":
        return tok[1:-1]
    return tok

def parse_flags(tokens):
    """返回 (短旗标串, 长旗标集)：-nfd→'nfd'，--force→'force'"""
    short, longs = "", set()
    for t in tokens:
        if t.startswith("--") and len(t) > 2:
            longs.add(t[2:])
        elif t.startswith("-") and len(t) > 1:
            short += t[1:]
    return short, longs

def checkout_discards(seg_after_sub):
    """checkout/restore/switch 之后的 pathspec 是否丢弃形态：. ./ :/… *（剥引号，-- 直通）"""
    toks = seg_after_sub.split()
    for i, tok in enumerate(toks):
        if tok == "--":
            continue
        if tok.startswith("-"):
            if tok in ("-b", "--branch", "-c", "--create"):
                return False  # 建分支，非丢弃
            if tok in ("-s", "--source"):
                nxt = toks[i + 1] if i + 1 < len(toks) else ""
                if nxt == "HEAD" or nxt.startswith(("HEAD~", "HEAD^")):
                    continue  # 从 HEAD 恢复 = 丢弃工作区，不豁免（与 --source=HEAD 对齐）
                return False  # 指定其他源（stash 等）恢复，非丢弃（既有 fixture 决策）
            continue
        t = strip_quotes(tok)
        core = t.rstrip("/") or t
        if core in (".", "*") or t.startswith(":/") or core == ":":
            return True
    return False

def force_switch(seg_after_sub):
    """checkout/switch 带 -f/--force（含捆绑短旗标）且非建分支/指定源 → 强切丢弃未提交改动"""
    short, longs = parse_flags(seg_after_sub.split())
    force = "f" in short or "force" in longs
    exempt = any(c in short for c in "bcs") or bool(longs & {"branch", "create", "source"})
    return force and not exempt

for part in re.split(r";|&&|\|\||\||\r?\n", cmd):
    seg = part.strip()
    if not seg:
        continue

    m = GIT_SIG.search(seg)
    if m:
        sub = m.group(1)
        if sub == "push":
            short, longs = parse_flags(seg.split())
            if "f" in short or "force" in longs:
                blocked("破坏性命令（git push --force）：请人工确认后自行执行；确需强推建议人工用 --force-with-lease")
            if "delete" in longs or re.search(r"\s:[^\s]", seg):
                blocked("破坏性命令（git push 删除远端分支）：请人工确认后自行执行")
            if re.search(r"(^|\s)\+\S+", seg):
                blocked("破坏性命令（git push +refspec 强制覆盖远端）：请人工确认后自行执行")
        elif sub == "reset" and "--hard" in seg:
            blocked("破坏性命令（git reset --hard）：请人工确认后自行执行")
        elif sub == "clean":
            short, longs = parse_flags(seg.split())
            if ("f" in short or "force" in longs) and not ("n" in short or "dry-run" in longs):
                blocked("破坏性命令（git clean -f）：请人工确认后自行执行")
        elif sub == "branch":
            short, longs = parse_flags(seg.split())
            if "D" in short or (("d" in short or "delete" in longs) and ("f" in short or "force" in longs)):
                blocked("破坏性命令（git branch -D 强删分支）：请人工确认后自行执行")
        elif sub == "stash":
            rest = seg[m.end(1):].split()
            if rest and rest[0] == "clear":  # 只拦 clear（全删无恢复）；drop/pop 按 v40 裁决不拦
                blocked("破坏性命令（git stash clear 清空全部 stash）：请人工确认后自行执行")
        elif sub in ("checkout", "restore", "switch"):
            after = seg[m.end(1):]
            if force_switch(after) or checkout_discards(after):
                blocked("破坏性命令（git checkout/restore/switch 丢弃工作区改动）：请人工确认后自行执行")

    r = RM_SIG.search(seg)
    if r:
        tokens = seg[r.start():].split()  # rm 及其后 token（跳过前缀/包裹）
        short, longs = parse_flags(tokens)
        has_r = "r" in short or "recursive" in longs
        has_f = "f" in short or "force" in longs
        if has_r and has_f:
            REDIR = re.compile(r"^\d*[<>]")  # 重定向 token（2>&1 / 2>/dev/null / <file）不作 path
            paths = [os.path.normpath(os.path.expanduser(strip_quotes(t)))
                     for t in tokens[1:] if not t.startswith("-") and not REDIR.match(t)]
            if not paths or not all(p == "/tmp" or p.startswith("/tmp/") or p.startswith("/var/folders/") for p in paths):
                blocked("破坏性命令（rm 递归+强制，非临时目录或无操作数）：请人工确认后自行执行")
sys.exit(0)
