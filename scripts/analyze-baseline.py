#!/usr/bin/env python3
# crules-flutter analyze 基线外置比对（质量闸通电批 1a · 2026-11-18，方案 docs/方案-质量闸通电-2026-11-18.md §4.1/E2/E3）
# 立论：三痛之「质量证据自报」（1095602 flutterAnalyze 自填字段）——证词不可承重，须机械外置
#   （姊妹篇 scope-audit 管文件面、本件管告警面；同源哲学两刀）。
# U7 通电实测定档（2026-11-18 · flutter 3.27.4/Dart 3.6.2 · /tmp 探针工程）：
#   1. flutter analyze --machine 【不跑】custom_lint 插件（蓄意双违规零报告）→ 单源不可行；
#   2. dart run custom_lint --format=json ＝官方机读口（schema v1：code/severity/location.line/
#      problemMessage；取数加 --no-fatal-infos --no-fatal-warnings 令工具 rc 恒 0，红绿由本件自出）；
#   3. 通电版本矩阵：消费版 0.6.4/2.3.10 不可编译（analyzer 7 API 断档）；0.7.3/2.6.4 裸解亦断
#      （analyzer_plugin 0.12.0 ↔ analyzer 7.6.0）；工作组合＝0.7.3＋2.6.4＋dependency_overrides
#      钉 analyzer_plugin 0.13.4（经 pubspec_overrides.yaml——custom_lint 插件宿主临时仓自行 pub get，
#      workspace.dart computePubspecOverride 只认该通道）。
# 取数口（让位规则钉死一处）：--from-snapshot / --analyze-cmd 注入缝（夹具免真跑 Flutter）；
#   缺省双源直跑＝flutter analyze --machine（原生面）＋dart run custom_lint --format=json（插件面）；
#   analysis_options 无 custom_lint 声明 → 跳过插件源并记行（未通电＝合理态，不静默）；有声明而跑挂
#   → rc2（通电断言失败不降级——假绿比报错更贵）。
# 比对键（评审黄 3 冻结）：path＋code＋severity；line/col 不入键（行漂移假对首跑狼来了主源），
#   仅展示。新增 error/info 同计 rc 1（Q5 裁决），报告三档分层＋error 列首；消除差集强制节
#   （防基线只增不减膨胀）；报告头绑工程 HEAD hash＋基线 sha256（姊妹篇同款绑定）。
# 退出码：0 无新增 / 1 新增≥1 / 2 用法·取数·解析错。
import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SCHEMA = "crules-analyze-baseline-v1"
SEV_RANK = {"ERROR": 0, "WARNING": 1, "INFO": 2}


def die(msg):
    print(f"analyze-baseline: {msg}", file=sys.stderr)
    sys.exit(2)


def norm_sev(s):
    s = (s or "").upper()
    return s if s in SEV_RANK else "INFO"


def rel(path, project):
    try:
        r = os.path.relpath(path, project)
        return r.replace(os.sep, "/") if not r.startswith("..") else path.replace(os.sep, "/")
    except ValueError:
        return path.replace(os.sep, "/")


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=isinstance(cmd, str))


def parse_machine_lines(text, project):
    """flutter analyze --machine 管道行：SEVERITY|TYPE|FILE|LINE|COL|MSG|CODE"""
    out = []
    for ln in text.splitlines():
        parts = ln.split("|")
        if len(parts) < 7 or parts[0].upper() not in SEV_RANK:
            continue
        sev, _typ, f, line, _col, msg, code = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6]
        try:
            line = int(line)
        except ValueError:
            continue
        out.append({"path": rel(f, project), "line": line, "severity": norm_sev(sev),
                    "code": code.strip() or "(no-code)", "msg": msg.strip()})
    return out


def parse_custom_lint_json(text, project):
    """dart run custom_lint --format=json：schema v1"""
    obj = json.loads(text)
    if obj.get("version") != 1 or not isinstance(obj.get("diagnostics"), list):
        raise ValueError("custom_lint JSON schema 不识（version≠1 或无 diagnostics）")
    out = []
    for d in obj["diagnostics"]:
        loc = d.get("location") or {}
        start = (loc.get("range") or {}).get("start") or {}
        out.append({"path": rel(loc.get("file", ""), project),
                    "line": int(start.get("line", 0)) or 0,
                    "severity": norm_sev(d.get("severity")),
                    "code": (d.get("code") or "(no-code)").strip(),
                    "msg": (d.get("problemMessage") or "").strip()})
    return out


def autodetect(text, project):
    t = text.lstrip()
    if t.startswith("{"):
        return parse_custom_lint_json(text, project)
    return parse_machine_lines(text, project)


def plugins_declared(project):
    ao = os.path.join(project, "analysis_options.yaml")
    try:
        return re.search(r"custom_lint", open(ao, encoding="utf-8", errors="replace").read()) is not None
    except OSError:
        return False


def collect(a, project):
    """→ (warnings:list, src_label:str, analyzer_label:str|None)"""
    if a.from_snapshot:
        obj = json.loads(open(a.from_snapshot, encoding="utf-8").read())
        return obj.get("diagnostics", []), f"注入缝 --from-snapshot {a.from_snapshot}", obj.get("analyzer")
    if a.analyze_cmd:
        p = run(a.analyze_cmd, project)
        if p.returncode != 0 and not p.stdout.strip():
            die(f"--analyze-cmd 退出 {p.returncode} 且无输出: {p.stderr.strip()[:200]}")
        return autodetect(p.stdout, project), f"注入缝 --analyze-cmd", None
    # 缺省双源直跑（U7 实测定档）
    w, labels = [], []
    p1 = run(["flutter", "analyze", "--machine"], project)
    if p1.returncode not in (0, 1):
        die(f"flutter analyze 失败（rc {p1.returncode}）: {(p1.stderr or p1.stdout).strip()[:200]}")
    w += parse_machine_lines(p1.stdout, project)
    labels.append("flutter analyze --machine（原生面）")
    if plugins_declared(project):
        p2 = run(["dart", "run", "custom_lint", "--format=json",
                  "--no-fatal-infos", "--no-fatal-warnings"], project)
        try:
            w += parse_custom_lint_json(p2.stdout, project)
        except (ValueError, json.JSONDecodeError) as ex:
            die(f"custom_lint 取数失败（analysis_options 已声明 plugins 而插件面跑挂——通电断言失败不降级）: {ex}\n"
                f"stderr: {p2.stderr.strip()[:300]}")
        labels.append("dart run custom_lint --format=json（插件面）")
    else:
        labels.append("插件面跳过（analysis_options 无 custom_lint 声明——未通电＝合理态）")
    ver = run(["flutter", "--version"], project)
    first = ver.stdout.splitlines()[0] if ver.stdout else ""
    analyzer_label = " • ".join(first.split(" • ")[:2]).strip() or None  # 去掉仓库 URL 尾巴
    return w, "＋".join(labels), analyzer_label


def key(w):
    return (w["path"], w["code"], w["severity"])


def dedup(ws):
    """同键去重，保留行号最小者（展示稳定）。"""
    best = {}
    for w in ws:
        k = key(w)
        if k not in best or w["line"] < best[k]["line"]:
            best[k] = w
    return best


def git_head(project):
    p = run(["git", "-C", project, "rev-parse", "HEAD"], project)
    return p.stdout.strip() if p.returncode == 0 else None


def main():
    ap = argparse.ArgumentParser(description="analyze 告警 ↔ 基线 机械比对（记事实不出结论——裁决归需求方）")
    ap.add_argument("--project", default=os.getcwd(), help="目标 Flutter 工程根（默认 cwd；显式传参防多会话误属）")
    ap.add_argument("--baseline", help="基线 json 路径（--init-baseline 时为写出路径，否则必填）")
    ap.add_argument("--init-baseline", action="store_true", help="首跑冻结：以当前告警全量生成基线（Q1 裁决：只拦新增）")
    ap.add_argument("--analyze-cmd", help="注入缝：自定义取数命令（输出 machine 管道行或 custom_lint JSON）")
    ap.add_argument("--from-snapshot", help="注入缝：直接读告警快照 json（夹具用，免真跑 Flutter）")
    a = ap.parse_args()
    if a.analyze_cmd and a.from_snapshot:
        die("--analyze-cmd 与 --from-snapshot 互斥")
    if not a.init_baseline and not a.baseline:
        die("缺 --baseline（或改用 --init-baseline 首跑冻结）")

    project = os.path.abspath(a.project)
    if not os.path.isdir(project):
        die(f"工程目录不存在: {project}")
    head = git_head(project)
    cur, src_label, analyzer_label = collect(a, project)
    cur_map = dedup(cur)

    if a.init_baseline:
        doc = {"schema": SCHEMA, "analyzer": analyzer_label,
               "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "project_head": head,
               "diagnostics": sorted(cur_map.values(), key=lambda w: (w["path"], w["code"], w["severity"]))}
        with open(a.baseline, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print(f"首跑冻结：{len(cur_map)} 条存量入基线 {a.baseline}（Q1 裁决＝冻结存量只拦新增；"
              f"re-init 走显式重跑，禁静默自更新）")
        return

    try:
        raw = open(a.baseline, "rb").read()
    except OSError as ex:
        die(f"基线不可读: {ex}")
    sha = hashlib.sha256(raw).hexdigest()
    try:
        bl = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as ex:
        die(f"基线不可读: {ex}")
    if bl.get("schema") != SCHEMA:
        die(f"基线 schema 不识: {bl.get('schema')}（本件只认 {SCHEMA}）")
    bl_map = dedup(bl.get("diagnostics", []))

    new_keys = cur_map.keys() - bl_map.keys()
    gone_keys = bl_map.keys() - cur_map.keys()
    new = sorted((cur_map[k] for k in new_keys),
                 key=lambda w: (SEV_RANK[w["severity"]], w["path"], w["code"], w["line"]))
    gone = sorted((bl_map[k] for k in gone_keys),
                  key=lambda w: (w["path"], w["code"], w["severity"]))
    sev_cnt = {s: sum(1 for w in new if w["severity"] == s) for s in ("ERROR", "WARNING", "INFO")}

    print("# analyze-baseline 报告（记事实不出结论——裁决归需求方）")
    print(f"- project: {project} @ {head[:12] if head else '（非 git 仓·无 HEAD 锚）'}")
    print(f"- baseline: {a.baseline}（sha256 {sha[:16]}）· schema {bl.get('schema')}"
          f" · analyzer {bl.get('analyzer') or '（未记）'} · created {bl.get('created') or '（未记）'}"
          f" · head {(bl.get('project_head') or '无')[:12]}")
    print(f"- 取数口: {src_label}")
    print(f"- 汇总: 基线 {len(bl_map)} / 现存 {len(cur_map)} / 新增 {len(new)}"
          f"（error {sev_cnt['ERROR']}/warning {sev_cnt['WARNING']}/info {sev_cnt['INFO']}） / 消除 {len(gone)}")
    if bl.get("analyzer") and analyzer_label and bl["analyzer"] != analyzer_label:
        print(f"- ⚠️ analyzer 版本不一致（基线 {bl['analyzer']} ≠ 当前 {analyzer_label}）——告警面漂移先查这里")
    if not bl.get("project_head"):
        print("- ⚠️ 基线缺 project_head——跨批语义锚缺失（老 schema 降级读）")

    if new:
        print(f"\n## 新增告警（{len(new)}）〔error 列首〕")
        for w in new:
            print(f"- {w['path']}:{w['line']}  [{w['severity']}｜{w['code']}] {w['msg']}")
    print(f"\n## 消除差集（{len(gone)}）〔防基线只增不减膨胀〕")
    for w in gone:
        print(f"- {w['path']}  [{w['severity']}｜{w['code']}] 已不在现存集")
    sys.exit(1 if new else 0)


if __name__ == "__main__":
    main()
