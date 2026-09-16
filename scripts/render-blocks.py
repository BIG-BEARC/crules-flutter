#!/usr/bin/env python3
"""孪生同文块生成器（F3 · 1.0.12）

把四块「逐字同文块」由 canonical/ 单一源生成进目标文件——防漂移从**检测**前移到**构造**。
方案：docs/方案-2026-09-15-孪生同文块生成化.md（v3，两轮独立评审消解）

机制：
- 目标文件内以 `<!-- gen:<id> -->` … `<!-- /gen:<id> -->` 标记生成区间（**标记为手写位置锚**，
  本脚本不改动；围栏之间**全部**内容由 canonical/<id>.md 生成）
- 双守卫（防假绿）：
  ① 登记一致性 + 计数——扫描所有 `<!-- gen:` 的 id 集合须 == EXPECTED 键集合（堵「新增块忘登记」）；
     且每个 (id, 文件) 恰好 1 对围栏（堵「没跑起来却空过」）
  ② 内容同步——渲染后重读区间须 == canonical（堵「围栏在、内容未改写」）
- 幂等：重复执行产出恒等
- 语义注（review R7）：canonical 的**尾随换行被 rstrip 剥离**——生成的块以单一换行结尾；
  若某块需以空行结尾，须把空行写进正文（非文件尾），否则会被静默规范化掉

用法：python3 scripts/render-blocks.py [--check]
  --check：只校验不写入（CI 用；本地亦可用）
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON = "canonical"
MIN_BODY = 15   # canonical 正文最小长度（去说明行后）——防清空/截断静默抹除整段（review R2）

# 登记表：id → 目标文件（与 canonical/<id>.md 一一对应）
EXPECTED = {
    "gear-preset": ["app/CLAUDE.md", "plugin/CLAUDE.md"],
    "closing-tiers": ["app/CLAUDE.md", "plugin/CLAUDE.md"],
    "gate-exception": ["app/CLAUDE.md", "plugin/CLAUDE.md"],
    "gear-note": ["commands/help.md", "README.md"],
}


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def write(p, s):
    with open(os.path.join(ROOT, p), "w", encoding="utf-8") as f:
        f.write(s)


def scan_ids(text):
    """返回文本中所有 gen 标记的 id 列表（开标记）"""
    return re.findall(r"<!--\s*gen:([A-Za-z0-9_-]+)\s*-->", text)


def scan_targets():
    """分发面候选文件：README + app/ plugin/ commands/ 下全部 .md——守卫①c 的扫描面
    （含未登记文件，如 commands/init.md——堵「围栏落在未登记文件」的隐身，review R1）"""
    files = ["README.md"]
    for d in ("app", "plugin", "commands"):
        p = os.path.join(ROOT, d)
        if os.path.isdir(p):
            files += [f"{d}/{f}" for f in sorted(os.listdir(p)) if f.endswith(".md")]
    return files


def render_file(path, blocks, check):
    """把 path 内各 gen 区间替换为对应 canonical 内容；返回 (新文本, 错误列表)"""
    text = read(path)
    errs = []
    for bid, content in blocks.items():
        open_re, close_re = re.compile(r"<!--\s*gen:%s\s*-->" % bid), re.compile(r"<!--\s*/gen:%s\s*-->" % bid)
        starts, ends = list(open_re.finditer(text)), list(close_re.finditer(text))
        if len(starts) != 1 or len(ends) != 1 or starts[0].end() > ends[0].start():
            errs.append(f"{path}: 块 {bid} 围栏不恰好 1 对（开 {len(starts)} / 闭 {len(ends)}）")
            continue
        # 围栏之间全部内容 → canonical（含尾随换行的规范形：围栏行独占一行）
        new = text[: starts[0].end()] + "\n" + content.rstrip("\n") + "\n" + text[ends[0].start():]
        if new != text:
            if check:
                errs.append(f"{path}: 块 {bid} 与 canonical 不同步（--check 模式不写入）")
            else:
                text = new
    if not check and text != read(path):
        write(path, text)
    # 守卫② 内容同步：写后（或 check 时读原文）重读区间比对
    cur = read(path)
    for bid, content in blocks.items():
        m = re.search(r"<!--\s*gen:%s\s*-->\n(.*?)\n<!--\s*/gen:%s\s*-->" % (bid, bid), cur, re.S)
        if not m or m.group(1).rstrip("\n") != content.rstrip("\n"):
            errs.append(f"{path}: 块 {bid} 渲染后内容 != canonical（守卫②）")
    return errs


def main():
    check = "--check" in sys.argv
    errs = []
    # 守卫①a EXPECTED 非空——防「清空登记表 = 全体脱管」静默失效（review R5）
    if not EXPECTED:
        errs.append("守卫①: EXPECTED 为空——生成器脱管，拒绝空跑")
    # 守卫①b canonical/ 文件名集 == EXPECTED 键集——防孤儿源静默堆积（review R6）
    canon_ids = {f[:-3] for f in os.listdir(os.path.join(ROOT, CANON)) if f.endswith(".md")}
    if canon_ids != set(EXPECTED):
        errs.append(f"守卫①: canonical/ 文件名集 {sorted(canon_ids)} != EXPECTED 键集 {sorted(EXPECTED)}")
    # 守卫①c (文件, id) 对集合 == EXPECTED 展开集——堵「已登记 id 落在未登记文件」（review R1：
    # 原实现只比 id 集合，向 commands/help.md 挂 gear-preset 围栏可带垃圾内容全绿）
    pairs = {(p, i) for p in scan_targets() for i in set(scan_ids(read(p)))}
    expect_pairs = {(p, i) for i, fs in EXPECTED.items() for p in fs}
    if pairs != expect_pairs:
        if stray := sorted(pairs - expect_pairs):
            errs.append(f"守卫①: 未登记的 (文件, id) 对 = {stray}")
        if miss := sorted(expect_pairs - pairs):
            errs.append(f"守卫①: 登记的 (文件, id) 对缺围栏 = {miss}")
    # 守卫②a canonical 正文非空 + 下限——防清空/截断静默抹除整段（review R2：双侧同步故对称绿）
    blocks = {}
    for bid in EXPECTED:
        c = read(f"{CANON}/{bid}.md")
        blocks[bid] = c
        body = "\n".join(c.split("\n")[1:]).strip()   # 去首行说明行
        if len(body) < MIN_BODY:
            errs.append(f"守卫②: canonical/{bid}.md 正文仅 {len(body)} 字符（<{MIN_BODY}）——疑似清空/截断")
    for e in errs:
        print("FAIL", e)
    # 逐文件渲染（仅在有硬错时才中止写出）
    if not errs:
        for p in sorted({p for fs in EXPECTED.values() for p in fs}):
            errs += render_file(p, {bid: blocks[bid] for bid, fs in EXPECTED.items() if p in fs}, check)
    for e in errs:
        print("FAIL", e)
    print(f"render-blocks: {len(EXPECTED)} 块 × {len({p for fs in EXPECTED.values() for p in fs})} 文件, 失败 {len(errs)}")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
