#!/usr/bin/env python3
# crules-flutter 收尾对账 dry-run（批1 · 2026-09-22 探针，维护者面，不随 plugin 分发）
# 定位：宪法遵守度的**事实单生成器**——只记事实、不出结论（定罪归 distill 聚合与人，
#   对齐 §五 ledger→§7 聚合→人裁决 的既有分工；多会话共享工作树下「违反」常为跨会话误判）。
# 输入：转录 .jsonl 文件或含转录的目录（~/.claude/projects/<仓>/）。转录只作采料场——
#   本机实测留存仅数日（窗口口径见 docs/普查 表头），持久账须批2 落盘 compliance-log。
# 检查集（六项，两栏切分见 docs/普查-2026-09-22）：
#   宣约档①交付汇报三件套（末条 assistant 文本 × review结论/沉淀候选/裁决区 标记）
#   世界侧②Gate 例外台账存在与行数 ③git commit 事件 × 用户触发词 ④验证声明 × 执行配对
#   宣约档⑤commit message 格式（<type>: 前缀） 派单⑥reviewer/plan-reviewer 切片包令牌
#   顺带：deny/ask 命中计数（转录白拿，反馈环样本）、解析率（防「解析静默归零读成全遵守」）
# schema 事实（2026-09-22 本机实探）：行 type ∈ assistant/user/…；工具调用在
#   message.content[] 的 tool_use 块（Bash/PowerShell→input.command，Agent→input.prompt）；
#   用户手输 = type user 且 message.content 为 str；toolDenialKind 字段记权限侧拒绝。
# 编码纪律（P0-A 自查即实证——探针首版 print 中文在 cp950 当场炸）：stdout/stderr 钉 UTF-8。
import glob
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}
EXEC_RE = re.compile(r"\b(flutter test|dart test|test-self|flutter analyze|dart analyze|pytest|npm test|dart run build_runner)\b")
COMMIT_RE = re.compile(r"\bgit\b[^;|]*\bcommit\b")
TRIGGER_RE = re.compile(r"(提交|推送|commit|push)", re.I)
CLAIM_RE = re.compile(r"(全绿|测试通过|0 失败|失败 0|PASS=|全部通过|零失败)")
MSG_TYPE_RE = re.compile(r"^(feat|fix|refactor|perf|build|ci|docs|style|test|chore): \S")
DENIAL_MARKS = ("请需求方人工执行", "crules-flutter 安全闸", "warn 层")


def blocks(d):
    msg = d.get("message")
    if isinstance(msg, dict) and isinstance(msg.get("content"), list):
        return msg["content"]
    return []


def text_of(d):
    """assistant 行的全部 text 块拼接"""
    return "\n".join(b.get("text", "") for b in blocks(d)
                     if isinstance(b, dict) and b.get("type") == "text")


def audit(path):
    facts = {
        "file": os.path.basename(path)[:8], "lines": 0, "bad": 0,
        "edits": 0, "bash": 0, "commits": 0, "commit_fmt_ok": 0, "commit_msgs": [],
        "user_msgs": 0, "trigger_msgs": 0,
        "claims": 0, "execs": 0, "claim_after_last_exec": None,
        "last_assistant_text": "", "markers": {},
        "review_dispatch": 0, "slice_pkg": 0, "slice_exempt": 0,
        "denial_hits": 0, "permission_denials": 0,
        "cwds": set(),
    }
    last_exec_pos = -1
    pos = 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            facts["lines"] += 1
            try:
                d = json.loads(line)
            except Exception:
                facts["bad"] += 1
                continue
            pos += 1
            t = d.get("type")
            if isinstance(d.get("cwd"), str):
                facts["cwds"].add(d["cwd"])
            if d.get("toolDenialKind"):
                facts["permission_denials"] += 1
            if t == "user":
                content = (d.get("message") or {}).get("content") if isinstance(d.get("message"), dict) else None
                if isinstance(content, str) and content.strip():
                    facts["user_msgs"] += 1
                    if TRIGGER_RE.search(content):
                        facts["trigger_msgs"] += 1
                # tool_result 里的 deny/ask 命中（hook 拦截回传文本）
                for b in blocks(d):
                    if isinstance(b, dict) and b.get("type") == "tool_result":
                        rc = b.get("content")
                        rs = rc if isinstance(rc, str) else json.dumps(rc, ensure_ascii=False)
                        if any(m in rs for m in DENIAL_MARKS):
                            facts["denial_hits"] += 1
            elif t == "assistant":
                txt = text_of(d)
                if txt.strip():
                    facts["last_assistant_text"] = txt
                if CLAIM_RE.search(txt):
                    facts["claims"] += 1
                for b in blocks(d):
                    if not isinstance(b, dict) or b.get("type") != "tool_use":
                        continue
                    name, inp = b.get("name", ""), (b.get("input") or {})
                    if name in EDIT_TOOLS:
                        facts["edits"] += 1
                    elif name in ("Bash", "PowerShell"):
                        cmd = str(inp.get("command", ""))
                        facts["bash"] += 1
                        if EXEC_RE.search(cmd):
                            facts["execs"] += 1
                            last_exec_pos = pos
                        if COMMIT_RE.search(cmd):
                            facts["commits"] += 1
                            m = re.search(r"-m\s+[\"'](.*?)[\"']", cmd, re.S)
                            msg = (m.group(1) if m else "").strip()
                            if msg:
                                first = msg.splitlines()[0]
                                facts["commit_msgs"].append(first)
                                if MSG_TYPE_RE.match(first):
                                    facts["commit_fmt_ok"] += 1
                    elif name == "Agent":
                        sub = str(inp.get("subagent_type", ""))
                        if re.search(r"(reviewer|plan-reviewer)$", sub.split(":")[-1]):
                            facts["review_dispatch"] += 1
                            pr = str(inp.get("prompt", ""))
                            if "【切片包】" in pr:
                                facts["slice_pkg"] += 1
                            if "【切片包-免】" in pr:
                                facts["slice_exempt"] += 1
    facts["claim_after_last_exec"] = None if not facts["claims"] else (last_exec_pos, pos)
    last = facts.pop("last_assistant_text")
    for label, pat in (("review结论", r"review ?结论"), ("沉淀候选", r"沉淀候选"), ("裁决区", r"裁决区")):
        facts["markers"][label] = bool(re.search(pat, last, re.I))
    return facts


def find_ledger(cwds):
    """自转录 cwd 上溯找宪法层 .claude/memory/，报 Gate 台账 / review-ledger 行数（存在才计）"""
    out = {}
    for cwd in cwds:
        d = os.path.abspath(cwd)
        while True:
            mem = os.path.join(d, ".claude", "memory")
            if os.path.exists(os.path.join(mem, "NAVIGATION.md")):
                for name in (".gate-exceptions", ".review-ledger"):
                    p = os.path.join(mem, name)
                    try:
                        with open(p, encoding="utf-8", errors="replace") as f:
                            out[name] = sum(1 for l in f if l.strip())
                    except OSError:
                        out[name] = None
                return d, out
            parent = os.path.dirname(d)
            if parent == d:
                return None, out
            d = parent
    return None, out


def main(argv):
    paths = []
    for a in argv:
        if os.path.isdir(a):
            paths += sorted(glob.glob(os.path.join(a, "*.jsonl")))
        elif os.path.exists(a):
            paths.append(a)
    if not paths:
        print("用法: closing-audit.py <转录.jsonl | 目录> [...]（只读事实单，不落盘不改动）")
        return 2
    tot = {"sess": 0, "bad_lines": 0, "all_lines": 0, "edit_sessions": 0,
           "edit_sessions_missing_marker": 0, "review_dispatch": 0, "slice_none": 0,
           "commits": 0, "commit_no_trigger_window": 0, "claims": 0, "execs": 0,
           "denial_hits": 0}
    for p in paths:
        f = audit(p)
        tot["sess"] += 1
        tot["bad_lines"] += f["bad"]
        tot["all_lines"] += f["lines"]
        implemented = f["edits"] > 0
        missing = [k for k, v in f["markers"].items() if not v]
        if implemented:
            tot["edit_sessions"] += 1
            if missing:
                tot["edit_sessions_missing_marker"] += 1
        tot["review_dispatch"] += f["review_dispatch"]
        tot["slice_none"] += max(0, f["review_dispatch"] - f["slice_pkg"] - f["slice_exempt"])
        tot["commits"] += f["commits"]
        if f["commits"] and f["trigger_msgs"] == 0:
            tot["commit_no_trigger_window"] += f["commits"]
        tot["claims"] += f["claims"]
        tot["execs"] += f["execs"]
        tot["denial_hits"] += f["denial_hits"]
        root, ledgers = find_ledger(f["cwds"])
        parse_pct = 100.0 * (f["lines"] - f["bad"]) / max(1, f["lines"])
        print(f"[{f['file']}] 行{f['lines']} 解析{parse_pct:.0f}% | 编辑{f['edits']} bash{f['bash']}"
              f" commit{f['commits']} 触发词{f['trigger_msgs']} | 声明{f['claims']}/执行{f['execs']}"
              f" | 派单{f['review_dispatch']}(包{f['slice_pkg']}/免{f['slice_exempt']})"
              f" | deny/ask命中{f['denial_hits']} 权限拒{f['permission_denials']}"
              f" | 末条三件套缺失:{','.join(missing) if missing else '无'}"
              f" | 根:{os.path.basename(root) if root else '(无宪法层)'}"
              f" 台账:{ledgers or '{}'}")
    pr = 100.0 * (tot["all_lines"] - tot["bad_lines"]) / max(1, tot["all_lines"])
    print(f"\n== 汇总 == 会话{tot['sess']} 解析率{pr:.1f}%"
          f" | 实施类会话{tot['edit_sessions']}(缺三件套{tot['edit_sessions_missing_marker']})"
          f" | 评审派单{tot['review_dispatch']}(无包令牌{tot['slice_none']})"
          f" | commit{tot['commits']}(触发词窗口为0的会话内{tot['commit_no_trigger_window']})"
          f" | 声明{tot['claims']}/执行{tot['execs']} | deny/ask命中{tot['denial_hits']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
