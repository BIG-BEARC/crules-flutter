#!/usr/bin/env python3
# 溯源：源自 crules v74 fork；1.0.0（2026-09）起随 deny-list.py Vendor 终态自持演进（fixture 库本地为权威）
"""deny-list 回归测试（v37 沉淀——修正 v35「单测 15/15 跑完即弃、无文件无痕」）。

跑法：python3 hooks/test_deny_list.py（scripts/test-self.sh 的「deny-list fixture 应全绿」断言调用）
**1.0.17 批F2 起夹具单源双驱**：用例本体在 hooks/fixtures/deny-list-cases.json（本文件与
test_deny_list.ps1 共读）；本驱动跑 lang∈{both,bash} 子集，ps 侧由 PowerShell 驱动跑 lang∈{both,ps}。
lang 缺省=both。计数以实跑输出为准（历史条目转抄数不作权威——1.0.0「75」实点为 77）。
fixture 原则：该拦全拦（含 v37 外审 5 绕过、1.0.8 拼合绕过 10 形态）、该放全放
（含 --force-with-lease / /tmp 白名单）、高危弹窗（1.0.9 warn 层：四形态 ask 非 deny）；
新增绕过形态时**先加 fixture（红）→ 修 deny-list 双源（绿）**，测试即对抗样本库。
探测纪律（v41，第三轮红队假证据教训）：对 deny-list 做人工/脚本探测时，输入 JSON
必须用 json.dumps 构造（如本文件 decision() 的 input 构造），**禁止 shell 手拼**——手拼含引号命令会产生
非法 JSON，脚本 json.load 失败即 exit(0)，探测结果恒为「放行」的假证据。（ps 驱动同款纪律。）
1.0.22 起契约面加锁：**空/纯空白 stdin → ask**（闸自身失效兜底）、**非空非法 JSON 仍 fail-open**
（F10① 不变）——两条同测，防「一并收口」或「一并放开」的过度修正。
启动失败（子进程没起来）与判定失败**分开处置、分开计数**（见 _spawn）：前者是环境故障
（本机注入型终端管控 agent 所致），后者才是被测对象的失败——混成一团会让红无从下手。
"""
import json, os, subprocess, sys

# 编码显式化（1.0.21，Windows 实机 P0-A，与 deny-list.py 同批）：①驱动自身 print 含中文，
#   宿主码页非 UTF-8 时抛 UnicodeEncodeError 整跑即崩；②子进程输出自 1.0.21 起为显式 UTF-8，
#   父端 `text=True` 默认按宿主码页解 → cp950 下解码错/乱码（ps 驱动的 StandardOutputEncoding
#   =UTF8 同款处置）。两侧钉死，本驱动与宿主码页解耦。
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# 子进程启动失败的降噪（2026-09-17 实机定位）：本机装联软 UniAccess 终端管控 agent，它把 32 位
#   `Vozokopot.dll` 挂在 AppInit_DLLs 上（64 位 hive 与 WOW6432Node **两处**均 LoadAppInit_DLLs=1）
#   → 每个加载 user32 的新进程启动时都被注入，注入失败即 STATUS_DLL_INIT_FAILED(0xc0000142)，
#   Windows 弹**加载器级硬错误框**——**不进 WER、不进事件日志**（故「日志干净」不是「没发生」的证据）。
#   本文件是全仓唯一密集 spawn 的组件（每遍约 165 个 python 子进程），故在此设 error mode：
#   SEM_FAILCRITICALERRORS(0x1) 抑制该类硬错误框，**官方口径：子进程继承父进程的 error mode**
#   → 一次设置覆盖本次跑出的全部子进程；NOGPFAULTERRORBOX(0x2)、NOOPENFILEERRORBOX(0x8000) 同族补齐。
#   诚实边界：故障本身偶发、无法按需复现，故「抑制生效」属**机制正确 + 未实测**；且本措施只挡弹窗、
#   不挡「子进程起不来」本身——后者由下方 decision() 的启动失败重试与计数兜住。
if os.name == "nt":
    try:
        import ctypes
        ctypes.windll.kernel32.SetErrorMode(0x0001 | 0x0002 | 0x8000)
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(HERE, "fixtures", "deny-list-cases.json")

_doc = json.load(open(FIXTURES, encoding="utf-8"))
_CASES = [c for c in _doc["cases"] if c.get("lang", "both") in ("both", "bash")]
BLOCK_CASES = [c["cmd"] for c in _CASES if c["expect"] == "deny"]
ALLOW_CASES = [c["cmd"] for c in _CASES if c["expect"] == "allow"]
WARN_CASES = [c["cmd"] for c in _CASES if c["expect"] == "ask"]

def _raw_spawn(stdin_text: str):
    """喂任意 stdin 跑一次 deny-list.py，返回 (rc, stdout)。子进程根本起不来（OSError）时 rc=None。
    返回 rc **而非抛异常**：本机装注入型终端管控 agent，密集 spawn 下偶发进程启动失败
    （STATUS_DLL_INIT_FAILED），抛出去会让整个驱动崩掉、拿不到其余用例的证据。"""
    try:
        p = subprocess.run(
            [sys.executable, os.path.join(HERE, "deny-list.py")],
            input=stdin_text, capture_output=True, text=True, encoding="utf-8",
        )
        return p.returncode, p.stdout
    except OSError:
        return None, ""

# 启动失败的可观测计数（**不许静默**）：rc≠0 且 stdout 空 = 子进程没能产出契约，与「判成 allow」
#   是两件事——旧写法把二者混成「非 deny」一条红，根因无从下手（2026-09-17 实机概率红实证）。
#   处置：分辨后再判——启动失败重试一次（环境故障不该算被测对象失败），仍失败才计 SPAWN_FAIL
#   并按当次实得值报；重试与失败次数**一律进汇总行**，故「本机在丢进程」永远看得见、不会变成假绿。
SPAWN_RETRY = 0
SPAWN_FAIL = 0

def _spawn(stdin_text: str):
    """带启动失败重试的 spawn（见上方纪律）；返回 (rc, stdout)。"""
    global SPAWN_RETRY, SPAWN_FAIL
    rc, out = _raw_spawn(stdin_text)
    if rc != 0 and not out.strip():
        SPAWN_RETRY += 1
        rc, out = _raw_spawn(stdin_text)
        if rc != 0 and not out.strip():
            SPAWN_FAIL += 1
    return rc, out

def decision(case: str) -> str:
    """三值判定：deny / ask / allow（1.0.9 warn 层起拦放不再是二元）"""
    _, out = _spawn(json.dumps({"tool_input": {"command": case}}))
    if '"deny"' in out:
        return "deny"
    if '"ask"' in out:
        return "ask"
    return "allow"

# 批A F9（1.0.11）：归一化单调性属性断言——deny 样本经「归一化可还原」的变异后不得变 allow。
# 「归一方向一律拼合 = 只增拦截面」是 deny-list 头注声称的不变量，此处上机器锁。
# **价值界说（R3 复核修正，防高估）**：三类变异均落在归一的全局删除规则上（任意位置可删），
# 故 norm(变异) ≡ 原串恒成立 → 本断言在 BLOCK 全绿时必然全绿，独立价值仅在「归一函数回归」
# （如引号删除被收窄为词内时变异会红）。全量纯函数版（提取 normalize() 覆盖全样本×全位置）
# 系后续改进项——需重构 deny-list 主流程，收益/风险比待裁，暂以黑盒版锁回归。
# 样本取 BLOCK 谱系确定性抽样（step 见 fixtures monotonicity.step），位置取 1/3、2/3 处，
# 防全量 subprocess 超时
_MONO_STEP = _doc["monotonicity"]["step"]

def _norm_mutants(cmd: str):
    n = len(cmd)
    if n < 8:
        return []
    outs = []
    for pos in (n // 3, 2 * n // 3):
        if pos >= n:
            continue
        outs.append(cmd[:pos] + '"' + cmd[pos:])            # 引号插入
        outs.append(cmd[:pos] + "\\\n" + cmd[pos:])         # 续行插入
    i = n // 3
    while i < n and not (cmd[i].isalnum() or cmd[i] == "_"):
        i += 1
    if i < n:
        outs.append(cmd[:i] + "\\" + cmd[i:])               # 反斜杠拼接（词字符前）
    return outs

def main() -> int:
    fails = []
    for c in BLOCK_CASES:
        v = decision(c)
        if v != "deny":
            fails.append(f"应拦未拦: {c!r}（实得 {v}）")
    for c in ALLOW_CASES:
        v = decision(c)
        if v != "allow":
            fails.append(f"应放未放: {c!r}（实得 {v}）")
    for c in WARN_CASES:
        v = decision(c)
        if v != "ask":
            fails.append(f"应 warn 未 ask: {c!r}（实得 {v}）")
    mut_total = 0
    for c in BLOCK_CASES[::_MONO_STEP]:
        for m in _norm_mutants(c):
            mut_total += 1
            v = decision(m)
            if v != "deny":
                # 实得值必须打出来：`allow` = 子进程无输出（宿主侧「无判定」，含 spawn 失败/空 stdin
                # 被旧写法静默放行），`ask` = 闸自身失效兜底（1.0.22 起）。两者根因完全不同，
                # 只打「非 deny」会把它们混成一条无从下手的红（2026-09-17 实机概率红即此）。
                fails.append(f"单调性破坏（变异后非 deny，实得 {v}）: {m!r}")
    # v52：拦截文案回归断言（blocked() 单出口追加「不要尝试绕过」——拦/放二元测不出文案回归）
    _, txt_out = _spawn(json.dumps({"tool_input": {"command": "git push --force origin main"}}))
    if "不要尝试绕过" not in txt_out:
        fails.append("拦截文案缺「不要尝试绕过」提示（blocked() 追加语回归）")
    # 1.0.22：闸自身失效兜底契约锁——**空 stdin / 纯空白 stdin → ask**（gate_self_failure）。
    #   宿主**总会**送 JSON，stdin 空即「参数没到」（最现实成因：hooks.json 的 `python3 … || python …`
    #   兜底链首解释器读完 stdin 后非零退出，兜底那次立即 EOF）。旧写法落 json.load 失败 → except
    #   exit 0 零输出 → 与「无命中」不可区分 = 静默 fail-open；本条即该行为的回归锁。
    #   非空非法 JSON 的 fail-open（F10①）**不变**，由下方第三例钉住——两者必须同测，
    #   否则「把两条路一起改成 ask」的过度收口不会被发现。
    for label, stdin_text, want_ask in (("空 stdin", "", True),
                                        ("纯空白 stdin", "  \n\t ", True),
                                        ("非空非法 JSON", "{not json", False)):
        qrc, qout = _spawn(stdin_text)
        got_ask = '"ask"' in qout
        if got_ask != want_ask or qrc != 0:
            fails.append(f"闸自身失效契约破（{label}）: rc={qrc} stdout={qout!r}")
        if want_ask and "crules-flutter" not in qout:
            fails.append(f"闸自身失效 ask 未带闸标识（{label}）: stdout={qout!r}")
    for f in fails:
        print("FAIL", f)
    # 启动失败计数进汇总行（**不为零必现形**）：本机注入型 agent 下「在丢进程」必须可见，
    # 否则重试就把一次真实的环境故障洗成了无痕的绿（假绿比红更贵——test-self.sh 头注同款纪律）。
    spawn_note = ""
    if SPAWN_RETRY or SPAWN_FAIL:
        spawn_note = f"  子进程启动失败：重试 {SPAWN_RETRY} 次 / 仍失败 {SPAWN_FAIL} 次"
    print(f"deny-list 测试(py 驱动): {len(BLOCK_CASES)} 拦 + {len(ALLOW_CASES)} 放 + {len(WARN_CASES)} warn + 单调性 {mut_total} 变异 + 契约锁 4, 失败 {len(fails)}{spawn_note}")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
