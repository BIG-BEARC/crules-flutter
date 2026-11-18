#!/usr/bin/env python3
# crules-flutter 收尾机械比对（声明面成环批 1 · 2026-11-18，方案 docs/方案-质量验证机制-声明面成环-2026-11-18.md §4.2）
# 立论：三痛之「越界无提示」＋「质量证据自报」（1095602 diffScope/flutterAnalyze 自填字段）——
#   证词不可承重，须机械外置（no-op-gate 同源立论；「自报不可靠·验证须外置」既有纪律）。
# 职责：读方案档 crules-scope-v1 block（改动面清单）→ git 实际变化（diff＋untracked）→ 三分类：
#   命中清单 / 清单外新增·扩容候选 / 清单外改存量·越界嫌疑；噪音四类单列不计越界（不静默吞）。
# 纪律：记事实不出结论（「清单外·越界嫌疑」非「违规」，裁决归需求方——compliance-audit 先例）；
#   报告头绑 repo HEAD hash＋scope sha256＋revs（防「审的是旧 diff」）；参数全显式零自动发现
#   （多会话同仓并发先例）。
# 退出码（D2）：0 净 / 1 越界嫌疑≥1 / 2 用法·解析错（坏行/冲突/无 block/git 失败）。
# 解析规约（D1 冻结面，方案 §4.1.2）：` :: ` maxsplit=2 右段全吞；strip CRLF；空行与 # 注释行合法；
#   同路径 action 矛盾 rc2；命中只看路径，action 不符＝提示行不判越界；glob 经 fnmatch。
import argparse
import fnmatch
import hashlib
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BLOCK_BEGIN = re.compile(r"<!--\s*scope:begin\s+crules-scope-v1\s*-->")
BLOCK_END = re.compile(r"<!--\s*scope:end\s*-->")
ACTIONS = ("M", "A", "D", "")
# 生成文件登记表（方案 §4.2：随脚本走批维护，禁现场静默扩表）
GEN_PATTERNS = (
    "GeneratedPluginRegistrant.swift", "Generated.xcconfig",
    "flutter_export_environment.sh", "*.g.dart", "*.freezed.dart",
    "*.mocks.dart", ".flutter-plugins", ".flutter-plugins-dependencies",
)
GLOB_CHARS = "*?["


def die(msg):
    print(f"scope-audit: {msg}", file=sys.stderr)
    sys.exit(2)


class Entry:
    __slots__ = ("path", "action", "line")

    def __init__(self, path, action, line):
        self.path, self.action, self.line = path, action, line


def parse_scope(text):
    """→ (entries, errors)；errors 非空由调用方 die。"""
    entries, errors, inside = [], [], False
    seen = {}
    for no, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip("\r").strip()
        if BLOCK_BEGIN.search(raw):
            inside = True
            continue
        if BLOCK_END.search(raw):
            inside = False
            continue
        if not inside:
            continue
        if not line or line.startswith("#"):
            continue  # 规约 3：空行/注释行合法
        parts = line.split(" :: ", 2)  # 规约 1：maxsplit=2 右段全吞
        if len(parts) < 2:
            errors.append(f"坏行 L{no}: {line}（规约：path :: action :: note，action∈M/A/D/空）")
            continue
        path = parts[0].strip()
        if path.startswith("./"):  # 只剥字面前缀；lstrip("./") 会吃掉 .claude-plugin 类点开头路径
            path = path[2:]
        action = parts[1].strip()
        if action not in ACTIONS:
            errors.append(f"坏行 L{no}: action「{action}」不在封闭枚举 M/A/D/空")
            continue
        if not path:
            errors.append(f"坏行 L{no}: 路径为空")
            continue
        prev = seen.get(path)
        if prev is not None and prev[0] != action:  # 规约 4：矛盾 rc2（报双方行号）
            errors.append(f"同路径 action 矛盾: {path}（L{prev[1]}={prev[0] or '空'} vs L{no}={action or '空'}）")
            continue
        if prev is not None:
            continue  # 完全重复条目＝去重
        seen[path] = (action, no)
        entries.append(Entry(path, action, no))
    return entries, errors


def git(repo, *args):
    # core.quotePath=false：非 ASCII 路径直出（默认八进制转义会致中文路径漏判——AC7 自反首审实证：
    # 进阶/审查与复核纪律.md 被转义成 "\350\277\233..." 与 block 字面路径不匹配、误报越界）
    p = subprocess.run(["git", "-C", repo, "-c", "core.quotePath=false", *args],
                       capture_output=True, text=True)
    if p.returncode != 0:
        die(f"git {' '.join(args)} 失败: {p.stderr.strip()[:200]}")
    return p.stdout


def load_submodules(repo):
    gm = os.path.join(repo, ".gitmodules")
    paths = set()
    if os.path.isfile(gm):
        try:
            for ln in open(gm, encoding="utf-8", errors="replace"):
                m = re.match(r"\s*path\s*=\s*(\S+)", ln)
                if m:
                    paths.add(m.group(1))
        except OSError:
            pass
    return paths


def is_gen(path):
    name = path.rsplit("/", 1)[-1]
    return any(fnmatch.fnmatch(name, pat) or fnmatch.fnmatch(path, pat) for pat in GEN_PATTERNS)


def match_entry(path, entries):
    """→ (entry|None, via_glob:bool, case_hint:bool)；命中只看路径。"""
    for e in entries:  # 1 字面精确
        if e.path == path and not any(c in e.path for c in GLOB_CHARS):
            return e, False, False
    for e in entries:  # 2 glob
        if any(c in e.path for c in GLOB_CHARS) and fnmatch.fnmatch(path, e.path):
            return e, True, False
    lp = path.lower()  # 3 大小写回退（macOS 不敏感 FS——显式提示不静默）
    for e in entries:
        if e.path.lower() == lp and not any(c in e.path for c in GLOB_CHARS):
            return e, False, True
    for e in entries:
        if any(c in e.path for c in GLOB_CHARS) and fnmatch.fnmatch(lp, e.path.lower()):
            return e, True, True
    return None, False, False


def main():
    ap = argparse.ArgumentParser(description="改动面清单 ↔ git 实际变化 机械比对（记事实不出结论）")
    ap.add_argument("--scope", required=True, help="方案档路径（含 crules-scope-v1 block）")
    ap.add_argument("--repo", default=os.getcwd(), help="目标 git 仓（默认 cwd；显式传参防多会话误属）")
    ap.add_argument("--baseline", help="diff 起点 rev（缺省＝HEAD：工作区＋暂存面）")
    ap.add_argument("--head", help="diff 终点 rev（需与 --baseline 同给）")
    a = ap.parse_args()
    if a.head and not a.baseline:
        die("--head 须与 --baseline 同给")

    try:
        text = open(a.scope, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError) as ex:
        die(f"scope 档不可读: {ex}")

    entries, errors = parse_scope(text)
    if errors:
        for e in errors:
            print(f"scope-audit: {e}", file=sys.stderr)
        die("block 解析失败（rc2）——禁静默跳行")
    if not entries:
        die(f"scope 缺失：{a.scope} 无 crules-scope-v1 block（散文判回落条 7 旧口径）")

    repo = a.repo
    head_hash = git(repo, "rev-parse", "HEAD").strip()
    if a.baseline and a.head:
        diff_src = ("rev-range", a.baseline, a.head)
        out = git(repo, "diff", "--name-status", f"{a.baseline}..{a.head}")
    elif a.baseline:
        diff_src = ("rev-to-worktree", a.baseline, None)
        out = git(repo, "diff", "--name-status", a.baseline)
    else:
        diff_src = ("head-to-worktree", "HEAD", None)
        out = git(repo, "diff", "--name-status", "HEAD")
    submods = load_submodules(repo)
    untracked = [ln[3:].strip().strip('"')
                 for ln in git(repo, "status", "--porcelain", "-uall").splitlines()
                 if ln.startswith("??")]

    hits, overreach, expand, noise_sub, noise_gen = [], [], [], [], []
    hints, glob_hits = [], {}

    def judge(path, actual):
        if path in submods:
            noise_sub.append((path, actual))
            return
        e, via_glob, case_hint = match_entry(path, entries)
        if e is not None:
            hits.append((path, actual, e))
            if via_glob:
                glob_hits[e.path] = glob_hits.get(e.path, 0) + 1
            if e.action and e.action != actual:
                hints.append(f"action 不符: {path}（声明 {e.action} 实际 {actual}——命中不判越界）")
            if case_hint:
                hints.append(f"大小写不一致: 实际 {path} ~ 声明 {e.path}")
            return
        if is_gen(path):
            noise_gen.append((path, actual))
            return
        (expand if actual == "A" else overreach).append((path, actual))

    for ln in out.splitlines():
        if not ln.strip():
            continue
        cols = ln.split("\t")
        st, path = cols[0], cols[1]
        if st.startswith("R"):  # 重命名拆 D+A 双侧判
            judge(cols[1], "D")
            judge(cols[2], "A")
        elif st.startswith("C"):
            judge(cols[2], "A")
        else:
            judge(path, "A" if st.startswith("A") else "M")  # M/T/其余按 M 存量

    for path in untracked:
        e, _, _ = match_entry(path, entries)
        if e is not None:
            judge(path, "A")
        elif is_gen(path):
            noise_gen.append((path, "untracked"))
        else:
            expand.append((path, "untracked"))

    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    base_lbl = diff_src[1] + (f" .. {diff_src[2]}" if diff_src[2] else " .. 工作区")
    print("# scope-audit 报告（记事实不出结论——裁决归需求方）")
    print(f"- scope: {a.scope}（sha256 {sha[:16]}）")
    print(f"- repo: {repo} @ {head_hash[:12]}")
    print(f"- diff 口径: {base_lbl}＋untracked(-uall)")
    print(f"- 汇总: 命中 {len(hits)} / 越界嫌疑 {len(overreach)} / 扩容候选 {len(expand)}"
          f" / 噪音·子模块 {len(noise_sub)} / 噪音·生成 {len(noise_gen)}")
    if diff_src[0] == "head-to-worktree" and not (hits or overreach or expand or noise_sub or noise_gen):
        print("- ⚠️ 空 diff——若本批含已提交改动，请显式 `--baseline <起点 rev>`（假绿比报错更贵）")

    def section(title, rows, fmt):
        print(f"\n## {title}（{len(rows)}）")
        for r in rows:
            print("- " + fmt(r))

    section("命中清单", hits, lambda r: f"{r[0]}  [{r[1]}｜声明 {r[2].action or '不限'}]")
    section("清单外改存量·越界嫌疑", overreach, lambda r: f"{r[0]}  [{r[1]}——清单无此路径，逐条解释或还原]")
    section("清单外新增·扩容候选", expand, lambda r: f"{r[0]}  [{r[1]}——若合理请补清单]")
    section("已知噪音·子模块指针（不计越界）", noise_sub, lambda r: f"{r[0]}  [{r[1]}——子模块指针变更]")
    section("已知噪音·生成文件（不计越界）", noise_gen, lambda r: f"{r[0]}  [{r[1]}——建议还原或补清单]")
    if glob_hits:
        print("\n## glob 命中计数（宽 glob 可见化）")
        for p, c in sorted(glob_hits.items()):
            print(f"- {p} ×{c}")
    if hints:
        print("\n## 提示")
        for h in hints:
            print("- " + h)

    sys.exit(1 if overreach else 0)


if __name__ == "__main__":
    main()
