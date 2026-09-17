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

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(HERE, "fixtures", "deny-list-cases.json")

_doc = json.load(open(FIXTURES, encoding="utf-8"))
_CASES = [c for c in _doc["cases"] if c.get("lang", "both") in ("both", "bash")]
BLOCK_CASES = [c["cmd"] for c in _CASES if c["expect"] == "deny"]
ALLOW_CASES = [c["cmd"] for c in _CASES if c["expect"] == "allow"]
WARN_CASES = [c["cmd"] for c in _CASES if c["expect"] == "ask"]

def decision(case: str) -> str:
    """三值判定：deny / ask / allow（1.0.9 warn 层起拦放不再是二元）"""
    p = subprocess.run(
        [sys.executable, os.path.join(HERE, "deny-list.py")],
        input=json.dumps({"tool_input": {"command": case}}),
        capture_output=True, text=True, encoding="utf-8",
    )
    if '"deny"' in p.stdout:
        return "deny"
    if '"ask"' in p.stdout:
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
        if decision(c) != "deny":
            fails.append(f"应拦未拦: {c!r}")
    for c in ALLOW_CASES:
        if decision(c) != "allow":
            fails.append(f"应放未放: {c!r}")
    for c in WARN_CASES:
        if decision(c) != "ask":
            fails.append(f"应 warn 未 ask: {c!r}")
    mut_total = 0
    for c in BLOCK_CASES[::_MONO_STEP]:
        for m in _norm_mutants(c):
            mut_total += 1
            if decision(m) != "deny":
                fails.append(f"单调性破坏（变异后非 deny）: {m!r}")
    # v52：拦截文案回归断言（blocked() 单出口追加「不要尝试绕过」——拦/放二元测不出文案回归）
    p = subprocess.run(
        [sys.executable, os.path.join(HERE, "deny-list.py")],
        input=json.dumps({"tool_input": {"command": "git push --force origin main"}}),
        capture_output=True, text=True, encoding="utf-8",
    )
    if "不要尝试绕过" not in p.stdout:
        fails.append("拦截文案缺「不要尝试绕过」提示（blocked() 追加语回归）")
    for f in fails:
        print("FAIL", f)
    print(f"deny-list 测试(py 驱动): {len(BLOCK_CASES)} 拦 + {len(ALLOW_CASES)} 放 + {len(WARN_CASES)} warn + 单调性 {mut_total} 变异, 失败 {len(fails)}")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
