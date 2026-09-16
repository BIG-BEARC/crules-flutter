#!/usr/bin/env python3
# crules-flutter 破坏性命令 deny-list（PreToolUse 硬闸，随 plugin 分发）
# 原则：deny 只拦无歧义的破坏性命令，**不做任何意图判断**；被拦即请需求方人工执行；
# warn 层（1.0.9）：非 deny 的高危四形态改发 ask 弹窗由需求方裁夺——「风险操作先确认」
# 从散文变机制，不扩 deny 面（ask 不拦执行，人在弹窗放行/否决）
# 拦截族（git + rm，细则由 fixture 对抗样本库固化）：
#   git push --force / +refspec / --delete·:branch / reset --hard / clean -f / branch -D /
#   checkout·restore·switch 丢弃工作区或强切 / stash clear / rm 递归+强制
# warn 形态族（ask 层）：curl/wget|sh·python3·ruby·perl 下载执行、chmod -R、sudo 前缀、git filter-branch·filter-repo
# 匹配策略：
#   - 分段前先**拼合归一**（1.0.8）：bash 续行（\+换行）/ 转义拼接（\x→x，限 \w）/
#     引号删除（词内 pu"sh"、整词 'rm'、ANSI-C $'rm'）——归一方向一律拼合，只增拦截面
#   - 分段（; && || | 换行）后，git/rm 签名用**非锚定搜索**——前缀（sudo/env）、包裹（$()）、
#     全局选项（git -C dir）一次吃掉，不枚举前缀词
#   - token 判定前剥**配对引号**（引号 pathspec 逃逸 + 引号白名单误拦两病同治）
#   - 捆绑短旗标统一走 parse_flags（-fv ≡ -f -v）；rm 白名单用 normpath 而非 realpath
#     （macOS /tmp→/private/tmp 符号链接，realpath 反而误拦合法白名单）
#   - warn 层在分段全部未命中 deny 后于**整条归一 cmd** 上匹配（管道形态横跨分段，须整条看）；
#     deny 优先天然成立——命中 deny 已在 blocked() exit，走到 warn 的必非 deny
#   - 长旗标剥 =value（批A F11，1.0.11）：--force=true 按 --force 判——git 自身拒绝该语法
#     （option takes no value，无远端草稿仓实证）故今日不可利用，剥值系防御纵深一致化
#     （reset 的子串判定与 push/clean/branch 的集合判定对齐）。**连带面**：剥值亦使
#     force_switch 的豁免集合对 --branch=/--create=/--source= 长形态生效（checkout -f
#     --source=other main 等四例 deny→allow）——git 现拒该语法故不可达；未来 git 若为
#     checkout/switch 补 --source=<tree> 时该豁免属语义正确。**注**：checkout_discards
#     自解析 token 不调 parse_flags，--source=stash@{1} 长形态与 -s 短形态判定仍不一致
#     （既存，本批未触及；全表无 --source= 样本故无闸）
#   - 输入契约 fail-open（批A F10①）：stdin 非法 JSON → exit 0 静默放行——输入由宿主构造
#     风险低，fail-closed 恐误伤非 JSON 探活/心跳；如改须先核宿主行为再动
# 边界与局限（诚实声明）：
#   - 非锚定搜索会把字符串里的破坏命令（含引号内原文——1.0.8 归一后成立）一并拦下——
#     按 deny-by-default 哲学接受，误拦走白名单调整
#   - **黑名单无法穷尽**——本 hook 是安全网而非沙箱，终极防线是 Claude Code 原生权限确认与需求方审阅；
#     find -delete / 变量拼接 / 嵌套 eval / 写脚本再执行等不拦，chmod -R 为 warn 弹窗非硬拦
#     （覆盖矩阵与决策史见 CHANGELOG）
#   - warn 层边界：bypassPermissions 模式下 ask 行为官方文档未覆盖；两步法（下载落盘再执行）
#     无管道形态、warn 不覆盖；echo 内嵌形态词会误弹（ask 误弹方向无害）；curl 多级管道
#     （| tee | bash）只看首段——形态匹配非语义分析。解释器族（1.0.11 扩）：须紧贴管道符
#     （路径 /usr/bin/python3、env python3、sudo -u root python3 带参前缀均不盖）；
#     python3? 不匹配 python2（EOL 不再扩）；`| python3 -m json.tool` 格式化惯用法误弹（ask 无害）
import json, os, re, sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
cmd = (data.get("tool_input") or {}).get("command") or ""
if not cmd.strip():
    sys.exit(0)

# 拼合归一（1.0.8 外审处置）：bash 把一个词拆开写的三类写法先拼回——①续行（\+换行）
# ②转义拼接（\x→x，限 \w——\ 与 \$ 等 shell 转义保留）③引号删除（词内 pu"sh"、
# 整词 'rm'、ANSI-C $'rm'）。归一方向一律「拼合」= 只增拦截面不开放行面（黑名单
# 保守方向）；代价：引号串内破坏命令原文（commit message / echo）将误拦——与
# heredoc 误拦同类，deny-by-default 既定取舍
cmd = re.sub(r"\\\r?\n", "", cmd)
cmd = re.sub(r"\\(\w)", r"\1", cmd)
cmd = re.sub(r"['\"]", "", cmd)

def blocked(reason):
    # 1.0.9：输出契约现代化——顶层 {"decision":"block"} 为官方已废弃旧形态（仅靠映射兼容），
    # 迁至 hookSpecificOutput；ask 在旧形态无对应值，deny/ask 统一走现行契约
    reason += "；请需求方人工执行，不要尝试绕过（如需展示命令，直接在回复中写文本）"
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
          "permissionDecision": "deny", "permissionDecisionReason": reason}}, ensure_ascii=False))
    sys.exit(0)

def warned(why):
    # warn 层出口（1.0.9）：ask 强制弹用户确认——官方口径：自动批准模式下 ask 仍强制弹窗、
    # 分类器不得静默放行；reason 呈给用户。多决策时官方优先级 deny > ask，与本进程
    # 「deny 先 exit 才可能到 warn」的次序一致
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
          "permissionDecision": "ask",
          "permissionDecisionReason": f"crules-flutter warn 层：{why}——危险面大，确认无误后放行"}}, ensure_ascii=False))
    sys.exit(0)

GIT_SIG = re.compile(r"\bgit\b[^;|]*?\b(push|reset|clean|branch|checkout|restore|switch|stash)\b")
RM_SIG = re.compile(r"(^|[\s(`$!])rm\b")

def strip_quotes(tok):
    """剥配对引号：'"."'→'.'（带空格的引号路径 split 不开，属既有局限，头注声明）"""
    if len(tok) >= 2 and tok[0] == tok[-1] and tok[0] in "\"'":
        return tok[1:-1]
    return tok

def parse_flags(tokens):
    """返回 (短旗标串, 长旗标集)：-nfd→'nfd'，--force→'force'，--force=x 剥值取 'force'（F11）"""
    short, longs = "", set()
    for t in tokens:
        if t.startswith("--") and len(t) > 2:
            longs.add(t[2:].split("=", 1)[0])
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

# warn 层（1.0.9 外审 🟢7）：高危四形态「先确认」机制化，全部未命中 deny 才到此处。
# sudo 判「命令位」（行首 / ; && || & | 换行之后）而非词中出现——防 echo 谈论 sudo 误弹；
# curl|sh、chmod -R、filter-branch 限段内（[^;|]* 不跨段）
WARN_SIGS = [
    (re.compile(r"\b(curl|wget)\b[^;|]*\|\s*(?:sudo\s+)?(?:(?:ba|z|da)?sh|python3?|ruby|perl)\b"), "网络内容直接进解释器（curl/wget | sh/python/ruby/perl）"),
    (re.compile(r"\bchmod\b[^;|]*\s-R"), "递归改权限（chmod -R）"),
    (re.compile(r"(?:^\s*|[;&|\n]\s*)sudo\b"), "提权执行（sudo）"),
    (re.compile(r"\bgit\b[^;|]*\bfilter-(?:branch|repo)\b"), "重写历史（git filter-branch / filter-repo）"),
]
for sig, why in WARN_SIGS:
    if sig.search(cmd):
        warned(why)
sys.exit(0)
