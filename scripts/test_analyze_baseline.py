#!/usr/bin/env python3
# analyze-baseline.py fixture（质量闸通电批 1a · 2026-11-18，方案 docs/方案-质量闸通电-2026-11-18.md §6.2）
#   全部走注入缝（--from-snapshot 喂告警快照 json），夹具零真跑 Flutter（本仓 CI 无 Flutter SDK，
#   评审黄 4 消解）；U7 通电生效性＝真机实跑，证据在方案档 §6.2 U7 行，不入本夹具。
#   - U1 净 / U2 新增 rc1 / U3 消除差集 / U4 analyzer 版本警示 / U5 基线坏三形 rc2
#   - U6 --init-baseline 四要素 / U8 行漂移不假对（键无行号）/ U9 severity 分层＋error 列首；附用法错两形
import json
import os
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "analyze-baseline.py")
PROJ = tempfile.mkdtemp(prefix="cf-ab.proj.")
BL_DIR = tempfile.mkdtemp(prefix="cf-ab.bl.")
_seq = 0
fails = 0


def check(name, cond):
    global fails
    print(("PASS  " if cond else "FAIL  ") + name)
    if not cond:
        fails += 1


def sh(*args):
    p = subprocess.run(["git", "-C", PROJ, *args], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {args} 失败: {p.stderr.strip()}")
    return p.stdout


def run_ab(*args):
    p = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def path_for(tag):
    global _seq
    _seq += 1
    return os.path.join(BL_DIR, f"{tag}_{_seq}.json")


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    return path


def baseline(dis, analyzer="fixture-同版", head="0" * 40):
    return write_json(path_for("bl"), {"schema": "crules-analyze-baseline-v1",
                                       "analyzer": analyzer, "created": "2026-11-18T00:00:00+00:00",
                                       "project_head": head, "diagnostics": dis})


def snap(dis, analyzer="fixture-同版"):
    return write_json(path_for("snap"), {"analyzer": analyzer, "diagnostics": dis})


def d(path, code="code_x", sev="INFO", line=1, msg="探针告警"):
    return {"path": path, "line": line, "severity": sev, "code": code, "msg": msg}


sh("init", "-q")
sh("config", "user.email", "t@t")
sh("config", "user.name", "t")
with open(os.path.join(PROJ, "pubspec.yaml"), "w", encoding="utf-8") as f:
    f.write("name: probe\n")
sh("add", "-A")
sh("commit", "-q", "-m", "base")
head = sh("rev-parse", "HEAD").strip()

# U1 净：基线与现存同键同版 → rc 0＋sha256 双绑定在场
bl = baseline([d("lib/a.dart", line=3)])
rc, out = run_ab("--project", PROJ, "--baseline", bl, "--from-snapshot", snap([d("lib/a.dart", line=3)]))
check("U1 基线＝现存 → rc 0 无新增＋报告头 sha256 绑定",
      rc == 0 and "新增 0" in out and "消除 0" in out and "sha256" in out and head[:12] in out)

# U2 新增：基线无 B → rc 1 且逐条列 file:line:code:severity:msg
bl = baseline([d("lib/a.dart")])
rc, out = run_ab("--project", PROJ, "--baseline", bl,
                 "--from-snapshot", snap([d("lib/a.dart"), d("lib/b.dart", code="code_b", line=12, sev="WARNING")]))
check("U2 清单外新增 → rc 1 逐条列 file:line:code:severity:msg",
      rc == 1 and "lib/b.dart:12" in out and "[WARNING｜code_b]" in out)

# U3 消除差集：基线含 C 现已无 → rc 0＋消除节列 C（防基线只增不减膨胀）
bl = baseline([d("lib/a.dart"), d("lib/c.dart", code="code_c")])
rc, out = run_ab("--project", PROJ, "--baseline", bl, "--from-snapshot", snap([d("lib/a.dart")]))
check("U3 消除差集节强制在场 → 旧告警消失可见",
      rc == 0 and "消除差集（1）" in out and "lib/c.dart" in out and "code_c" in out)

# U4 analyzer 版本不一致 → 警示行（比对语义降级可见）
bl = baseline([d("lib/a.dart")], analyzer="fixture-老版")
rc, out = run_ab("--project", PROJ, "--baseline", bl,
                 "--from-snapshot", snap([d("lib/a.dart")], analyzer="fixture-新版"))
check("U4 基线 analyzer≠当前 → 警示行（版本漂移先查这里）",
      rc == 0 and "analyzer 版本不一致" in out and "fixture-老版" in out and "fixture-新版" in out)

# U5 基线坏三形 → rc 2（文件缺失／坏 json／schema 不识）
rc1, out1 = run_ab("--project", PROJ, "--baseline", os.path.join(BL_DIR, "NOPE.json"),
                   "--from-snapshot", snap([]))
bad = os.path.join(BL_DIR, "bad.json")
with open(bad, "w", encoding="utf-8") as f:
    f.write("{不是json")
rc2_, out2 = run_ab("--project", PROJ, "--baseline", bad, "--from-snapshot", snap([]))
wrong = write_json(path_for("wrong"), {"schema": "别家-v9", "diagnostics": []})
rc3, out3 = run_ab("--project", PROJ, "--baseline", wrong, "--from-snapshot", snap([]))
check("U5 基线坏三形 → rc 2（缺档／坏 json／schema 不识）",
      rc1 == 2 and rc2_ == 2 and rc3 == 2 and "schema 不识" in out3)

# U6 --init-baseline：注入缝喂源 → 生成 schema 四要素齐全基线
init_path = path_for("init")
rc, out = run_ab("--project", PROJ, "--baseline", init_path, "--init-baseline",
                 "--from-snapshot", snap([d("lib/a.dart"), d("lib/b.dart")], analyzer="fixture-冻结版"))
doc = json.load(open(init_path, encoding="utf-8")) if os.path.isfile(init_path) else {}
check("U6 --init-baseline → 四要素齐全（schema/analyzer/created/project_head）＋冻结提示",
      rc == 0 and doc.get("schema") == "crules-analyze-baseline-v1"
      and doc.get("analyzer") == "fixture-冻结版" and bool(doc.get("created"))
      and doc.get("project_head") == head and len(doc.get("diagnostics", [])) == 2
      and "首跑冻结" in out and "禁静默自更新" in out)

# U8 行漂移：基线 A@L10 现存 A@L12 → 判「仍 A」非「新增＋消除」假对（键不含行号）
bl = baseline([d("lib/a.dart", line=10)])
rc, out = run_ab("--project", PROJ, "--baseline", bl, "--from-snapshot", snap([d("lib/a.dart", line=12)]))
check("U8 行漂移（L10→L12）→ 同键不假对（rc 0·新增 0·消除 0）",
      rc == 0 and "新增 0" in out and "消除 0" in out)

# U9 severity 分层：新增 error 1＋info 1 → rc 1·三档计数·error 列首
bl = baseline([])
rc, out = run_ab("--project", PROJ, "--baseline", bl,
                 "--from-snapshot", snap([d("lib/i.dart", sev="INFO"), d("lib/e.dart", sev="ERROR", code="code_e")]))
ok_order = out.find("lib/e.dart") != -1 and out.find("lib/i.dart") != -1 \
    and out.find("lib/e.dart") < out.find("lib/i.dart")
check("U9 新增 error＋info → rc 1·三档分层计数·error 列首",
      rc == 1 and "error 1/warning 0/info 1" in out and ok_order)

# 附：用法错两形 → rc 2（缺 --baseline／注入缝互斥）
rc1, out1 = run_ab("--project", PROJ, "--from-snapshot", snap([]))
rc2_, out2 = run_ab("--project", PROJ, "--baseline", baseline([]),
                    "--analyze-cmd", "true", "--from-snapshot", snap([]))
check("附 用法错两形 → rc 2（缺 --baseline／--analyze-cmd 与 --from-snapshot 互斥）",
      rc1 == 2 and rc2_ == 2 and "互斥" in out2)

print(f"analyze-baseline fixture: {'全绿' if fails == 0 else f'{fails} 失败'}")
sys.exit(1 if fails else 0)
