#!/usr/bin/env python3
"""新词两段闸·候选生成器（外源吸收批 ⑫，2026-10-27，1.3.2）

发布单「分发面新词过表」两段式的机械优先段：扫本批 diff 新增行产候选清单——只列不判
（观测面，不入 test-self 断言）。裁决权在需求方：逐词三选一（补录对照表 / 改白话 /
判常用词入白名单）。首例表征：2026-10-27 外源吸收批 diff。

输入＝git diff HEAD 新增行（已跟踪面）＋未跟踪文件全文（本批新档；.review-ledger 除外——
消费侧运行时件不入语料）；显式传参则只扫指定文件。
提取＝CJK 2–4 字滑窗高频（≥3）＋「」标记词（≥2）——两信号已经 spike 验证；加粗/表格
首列两信号未实现（候选清单性质允许，噪声由白名单消化）。
滤＝对照表两档已收录（黑话/白话列双向子串）＋白名单（scripts/term-whitelist.txt，
可选，首裁后落——一行一词，# 起头为注）。
用法：python3 scripts/term-candidates.py [files...]
"""
import os
import re
import subprocess
import sys
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOSSARY = os.path.join(ROOT, "docs/清单-黑话白话对照-2026-10-22.md")
WHITELIST = os.path.join(ROOT, "scripts/term-whitelist.txt")

known = set()
for line in open(GLOSSARY, encoding="utf-8"):
    if line.startswith("## "):
        continue
    if line.startswith("|"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0] not in ("黑话", "词", "---", "－"):
            for c in cells[:2]:  # 黑话列＋白话列双向；第三列起（出处）不入
                for t in re.split(r"[/／]", c):
                    t = re.sub(r"[（(].*", "", t).strip()
                    if t:
                        known.add(t)
    elif "·" in line and not line.startswith(">"):
        for item in line.split("·"):
            t = re.sub(r"[（(].*", "", item).strip()
            if 2 <= len(t) <= 12:
                known.add(t)

whitelist = set()
if os.path.exists(WHITELIST):
    for line in open(WHITELIST, encoding="utf-8"):
        t = line.split("#", 1)[0].strip()
        if t:
            whitelist.add(t)
known |= whitelist

# 语料：新增行（tracked diff ＋ untracked 全文；.review-ledger 运行时件除外）
lines = []
if len(sys.argv) > 1:
    for p in sys.argv[1:]:
        lines += open(p, encoding="utf-8").read().splitlines()
else:
    diff = subprocess.run(
        ["git", "diff", "HEAD", "-U0", "--diff-filter=AM"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    lines += [l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    ls = subprocess.run(
        ["git", "-c", "core.quotepath=off", "ls-files", "--others", "--exclude-standard"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    for p in ls.splitlines():
        if p == ".review-ledger" or not p.endswith((".md", ".py", ".sh", ".json")):
            continue
        lines += open(os.path.join(ROOT, p), encoding="utf-8").read().splitlines()

text = "\n".join(lines)

def is_known(g):
    return g in known or any(k in g or g in k for k in known)

freq = Counter()
for run in re.findall(r"[一-鿿]{2,}", text):
    for n in (2, 3, 4):
        for i in range(len(run) - n + 1):
            freq[run[i : i + n]] += 1

gram_hits = [
    (g, c) for g, c in freq.most_common()
    if c >= 3 and not is_known(g) and not any(
        g != h and c2 >= c and (g in h) for h, c2 in freq.items() if h.startswith(g) or h.endswith(g)
    )
]

quote_freq = Counter(re.findall(r"「([^」]{2,8})」", text))
quote_hits = [(g, c) for g, c in quote_freq.most_common() if c >= 2 and not is_known(g)]

src = "显式语料 %d 件" % (len(sys.argv) - 1) if len(sys.argv) > 1 else "本批 diff 面"
print(f"== {src}，新增行 {len(lines)} 行 / {len(text)} 字；对照表＋白名单已收录 {len(known)} 词 ==")
print("\n== 高频 CJK 候选（频次≥3，减已收录；只列不判，逐词三选一：补录对照表/改白话/白名单）==")
for g, c in gram_hits[:60]:
    print(f"{c:4d}  {g}")
print("\n== 「」标记词候选（频次≥2，减已收录）==")
for g, c in quote_hits[:25]:
    print(f"{c:4d}  {g}")
