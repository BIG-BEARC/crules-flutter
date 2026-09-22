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
#     checkout/switch 补 --source=<tree> 时该豁免属语义正确（checkout/switch 现无该选项，
#     git -h 实证）。**批E（1.0.14）收口**：checkout_discards 判据由「源是否为 HEAD」改为
#     「是否写工作区」——restore 的 -W/--worktree 是默认目标面（git restore -h 实证），
#     `-s stash@{1} .` 与 `-s HEAD .` 同样覆盖工作区，故 --source= / -s / -s<贴值> 三形态
#     同判 deny（原三者不一致）；同时修掉 `git restore --staged .` 的误拦（只动暂存区不写
#     工作区）。旗标统一走 parse_flags，该函数不再自解析 token
#   - 输入契约 fail-open（批A F10①）：**非空但非法 JSON** → exit 0 静默放行——输入由宿主构造
#     风险低，fail-closed 恐误伤非 JSON 探活/心跳；**已核宿主行为（1.0.22，官方 hooks 文档
#     2026-09-17）**：唯一靠退出码就能拦的是 exit 2，exit 1 等一律 non-blocking 放行 → 未捕获
#     异常与「兜底吃空 stdin」两条路都会静默 fail-open，故新增 gate_self_failure（见下方
#     L78+ 段注）：**stdin 空 / 未预期异常 → 改判 ask**（不静默放行、不硬锁死）。非空非法 JSON
#     维持 fail-open（F10① 未变）。
#   - 诚实边界（1.0.22 仍开口）：①首解释器被中途 kill（超时）→ 管道剩半截 JSON（非空非法）→
#     落 F10① 放行；②本文件语法错误 → 解释器根本没跑起来、excepthook 未安装 → exit 1 放行
#     （release.sh 的 test-self 全套是此路线的发行前闸——1.0.34 起由「py_compile+夹具」升级为本 fixture
#      子进程实跑本 hook，语法错误连 fixture 一起红；CI py_compile 步为编译层二次覆盖）；③两解释器皆缺 → exit 127 放行
#     （README 声明：终极防线回 Claude Code 原生权限确认）；④宿主超时的 hook 按官方口径本就不拦
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

# 流编码显式化（1.0.21，Windows 实机 P0-A）：宿主码页非 UTF-8 时 stdout 按该码页编码，两种后果
#   按「该码页能否编出消息里的字」分岔（2026-09-17 双码页实测）：
#   ①编不出 → blocked() 的 print 抛 UnicodeEncodeError，拦截 JSON **一字未出**即退出；hooks.json
#     的 `python3 … || python …` 兜底链再把它洗白——首个解释器已读完 stdin，兜底那次拿到空输入 →
#     json.load 失败 → exit 0，宿主侧与「无命中」不可区分（cp950/Big5 遇简体字形实测 exit 0 +
#     stdout 0 字节），hard gate 整体静默 fail-open。
#   ②编得出（如 cp936/GBK 对简体消息）→ 不崩，但 stdout 是 **cp936 字节而非 UTF-8**，宿主按
#     UTF-8 读则 reason 失真（决策字段系 ASCII，所测样本仍可解析——属未爆隐患，非安全态）。
#   stdin 方向**不抛**（Windows 标准流 errors=surrogateescape，实测）——坏字节变孤立代理项，
#   属「失真」而非「失败」：ASCII 骨架（rm/git 签名、/tmp 前缀）保留故判定面未见翻转，
#   但含非 ASCII 的路径/白名单串会被解成代理项垃圾。仍钉 UTF-8，使两侧语义与 ps1 一致。
# 修法 = 三流钉死 UTF-8，不依赖宿主码页，与 deny-list.ps1 入口段的 OpenStandardInput/Output +
#   UTF8Encoding($false) 同款（ps1 早有此手，py 侧补齐）。errors 两侧均 replace：编码侧防孤立
#   代理项（\udXXX）令闸门自毁，解码侧保住 ASCII 骨架（签名/路径仍可判）——两个方向都优于抛异常。
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

# 闸自身失效的承重兜底（1.0.22）：判据体位于本段之下，任何未预期异常都会让解释器以 **exit 1**
#   收场——而宿主对 PreToolUse 的语义是「exit 1 及一切非 0/2 码 = non-blocking error，动作照常
#   执行」（官方 hooks 文档 2026-09-17 查证：**唯一**靠退出码就能拦的是 exit 2；exit 0 且 stdout
#   无合法 JSON = 无判定 = 走正常权限流）。故未捕获异常 = 静默 fail-open，与本轮 `||` 双读 stdin
#   同属「闸失效 → 静默放行」家族：前者闸崩、后者兜底误读，两条路都汇到「宿主眼里什么都没发生」。
#   处置：判不出结果时**既不静默放行、也不硬锁死**，改判 ask 交需求方当场裁夺——与 warn 层同构
#   （ask 在自动批准模式下仍强制弹窗，官方口径）。JSON 走 ensure_ascii（纯 ASCII）→ 任何码页都
#   编得出，这条兜底自身不会再因编码二次失败（P0-A 同族教训：兜底必须比正路更不可能失败）。
def gate_self_failure(reason):
    try:
        sys.stdout.write(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
              "permissionDecision": "ask",
              "permissionDecisionReason": f"crules-flutter 安全闸自身失效（{reason}）——本次判定不可信，请人工裁夺"}},
              ensure_ascii=True) + "\n")
        sys.stdout.flush()
    except Exception:
        pass
    os._exit(0)   # 绕开默认 traceback 与 exit 1（非阻塞码）；stdout 已显式 flush

def _gate_excepthook(exc_type, exc, tb):
    gate_self_failure(exc_type.__name__)

sys.excepthook = _gate_excepthook

try:
    raw = sys.stdin.read()
except Exception:
    raw = ""
if not raw.strip():
    # stdin 为空 = 本次调用的参数根本没到（宿主**总会**送 JSON）→ 判据无从谈起。最现实的成因是
    # hooks.json 的 `python3 … || python …` 兜底链：首解释器读完 stdin 后因任何原因非零退出，
    # 兜底那次立即 EOF 只拿到空串（2026-09-17 单管道模型实测 0 字节 → 旧写法 json.load 抛
    # JSONDecodeError → 走 except exit 0），宿主侧与「无命中」**完全不可区分** = 静默放行的正源。
    # 归入「闸自身失效」同判 ask。残余边界：若首解释器被**中途 kill**（超时），管道里剩的是
    # 半截 JSON（非空且非法）→ 仍落入下方 F10① 的 fail-open，未收口（见头注诚实声明）。
    gate_self_failure("stdin 为空（参数未送达，疑为兜底解释器二次读取）")
try:
    data = json.loads(raw)
except Exception:
    sys.exit(0)   # F10① 原样保留：**非空**但非法 JSON 仍 fail-open（疑为探活/心跳，fail-closed 误伤正常流更糟）
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

# rm 白名单根（1.0.21 Windows 实机）：根与 token **同经 normpath** 再比较——原写法拿字面
#   "/tmp/" 去比 normpath 后的 token，而 Windows 的 normpath 把 / 翻成 \（normpath("/tmp/junk")
#   = "\tmp\junk"），前缀恒不命中 → /tmp、/var/folders 白名单族 5 例 both-allow 夹具在 Windows
#   全数误拦（macOS/Linux 上 normpath 不翻分隔符，故 CI 长期绿、掩盖此病）。归一后 POSIX 语义
#   逐字不变（normpath("/tmp") 仍为 "/tmp"），Windows 侧与 deny-list.ps1 D-e「字面 /tmp
#   /var/folders 跨界仍对」的声明对齐（双源对照表 temp 根一项）。
TMP_ROOTS = (os.path.normpath("/tmp"), os.path.normpath("/var/folders"))

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
    """是否丢弃工作区改动——判据 = **目标面写工作区** + 丢弃形态 pathspec（. ./ :/… *）。

    批E（1.0.14）换判据：原判「源是否为 HEAD」（-s HEAD 算丢弃 / -s 其他算非丢弃）与 git
    事实相悖——restore 的 `-W/--worktree` 是默认目标面（git restore -h 实证），`-s stash@{1} .`
    与 `-s HEAD .` 一样覆盖工作区。改判目标面后 **-s/--source 取值不参与判定**，长/短/贴值
    三形态天然同判（原三者判定不一致，系 F11 剥值连带面的既存项）；本函数不再需要「哪个
    旗标吃值」的位置解析。旗标一律走 parse_flags（捆绑短旗标与长旗标 =value 同源）。
    只动暂存区（-S/--staged 且无 -W/--worktree）不写工作区，不拦（原误拦，批E 修）。
    已知窄误拦（review R3，接受）：空格形态的源值若以 `:/` 开头（git 修订语法 `:/text`）
    会落入 pathspec 扫描判拦（`-s ":/fix login" x.dart`）——deny 方向用户摩擦，deny-by-default
    取舍内；贴值/=值 形态无此问题（token 以 `-` 开头整体跳过）。
    """
    toks = seg_after_sub.split()
    short, longs = parse_flags(toks)
    if "b" in short or "c" in short or longs & {"branch", "create"}:
        return False  # 建分支，非丢弃
    if ("S" in short or "staged" in longs) and not ("W" in short or "worktree" in longs):
        return False  # 目标面仅暂存区（restore -S），工作区不动
    for tok in toks:
        if tok == "--" or tok.startswith("-"):
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
            if not paths or not all(any(p == rt or p.startswith(rt + os.sep) for rt in TMP_ROOTS)
                                    for p in paths):
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
