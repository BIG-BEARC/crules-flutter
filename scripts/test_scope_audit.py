#!/usr/bin/env python3
# scope-audit.py fixture（声明面成环批 1 · 2026-11-18，方案 docs/方案-质量验证机制-声明面成环-2026-11-18.md §6.2 U1–U12）
#   mktemp -d 现造 fixture 仓（非 /tmp 固定路径——多会话并发教训）：
#   - U1 净 / U2 越界 rc1 / U3 扩容候选 / U4 坏行＋同路径矛盾 rc2（行号）
#   - U5 git mv 双侧 D+A / U6 --baseline 跨提交分叉 / U7 note 含 :: / U8 CRLF / U9 空行注释
#   - U10 glob 命中＋action 不符提示 / U11 噪音单列（子模块指针＋生成文件）仅真越界计 rc1
#   - U12 已 commit 零工作区 diff → 空 diff 警示行；U13 中文路径（core.quotePath 实施发现，AC7 实证）；
#     U14 点开头路径（lstrip("./") 吃点实弹发现，收口批实证）；另附用法错三形
import os
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "scope-audit.py")
SCOPE_DIR = tempfile.mkdtemp(prefix="cf-scope.doc.")
_scope_seq = 0
fails = 0


def check(name, cond):
    global fails
    print(("PASS  " if cond else "FAIL  ") + name)
    if not cond:
        fails += 1


def sh(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {args} 失败: {p.stderr.strip()}")
    return p.stdout


def make_repo(extra_files=None):
    d = tempfile.mkdtemp(prefix="cf-scope.")
    sh(d, "init", "-q")
    sh(d, "config", "user.email", "t@t")
    sh(d, "config", "user.name", "t")
    files = {"app/a.dart": "a\n", "lib/b.dart": "b\n", "old.dart": "old\n", "z.g.dart": "gen\n"}
    files.update(extra_files or {})
    for p, c in files.items():
        full = os.path.join(d, p)
        os.makedirs(os.path.dirname(full), exist_ok=True) if os.path.dirname(p) else None
        with open(full, "w", encoding="utf-8") as f:
            f.write(c)
    sh(d, "add", "-A")
    sh(d, "commit", "-q", "-m", "base")
    return d


def write_scope(repo_dir, body, sep="\n"):
    # scope 档写在 fixture 仓外（独立档目录）：档本身若落仓内会以 untracked 计入扩容候选，
    # 污染用例计数——真实使用面里方案档自身应在它自己的 scope block 内声明
    global _scope_seq
    _scope_seq += 1
    path = os.path.join(SCOPE_DIR, f"scope_{_scope_seq}.md")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("<!-- scope:begin crules-scope-v1 -->" + sep
                + sep.join(body) + sep + "<!-- scope:end -->" + sep)
    return path


def touch(repo_dir, rel, text):
    full = os.path.join(repo_dir, rel)
    if os.path.dirname(rel):
        os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "a", encoding="utf-8") as f:
        f.write(text)


def run_audit(*args):
    p = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


# U1 净：清单内 M → rc 0＋命中 1＋报告头双绑定（HEAD hash＋scope sha256）
d = make_repo()
sp = write_scope(d, ["app/a.dart :: M :: 骨架增改"])
touch(d, "app/a.dart", "x\n")
hh = sh(d, "rev-parse", "HEAD").strip()
rc, out = run_audit("--scope", sp, "--repo", d)
check("U1 清单内 M → rc 0 命中 1＋HEAD/sha256 双绑定",
      rc == 0 and "命中清单（1）" in out and "app/a.dart" in out
      and hh[:12] in out and "sha256" in out)

# U2 越界：清单外 M 存量 → rc 1＋越界嫌疑列名
d = make_repo()
sp = write_scope(d, ["app/a.dart :: M"])
touch(d, "lib/b.dart", "x\n")
rc, out = run_audit("--scope", sp, "--repo", d)
check("U2 清单外改存量 → rc 1 越界嫌疑列该文件",
      rc == 1 and "清单外改存量·越界嫌疑（1）" in out and "lib/b.dart" in out)

# U3 扩容：清单外 untracked 新增 → rc 0＋扩容候选
d = make_repo()
sp = write_scope(d, ["app/a.dart :: M"])
touch(d, "brand_new.dart", "n\n")
rc, out = run_audit("--scope", sp, "--repo", d)
check("U3 清单外新增 untracked → rc 0 扩容候选",
      rc == 0 and "清单外新增·扩容候选（1）" in out and "brand_new.dart" in out)

# U4 坏行＋同路径矛盾 → rc 2＋行号
d = make_repo()
sp = write_scope(d, ["app/a.dart :: M", "just-a-path"])
rc, out = run_audit("--scope", sp, "--repo", d)
ok_a = rc == 2 and "坏行 L" in out
sp = write_scope(d, ["app/a.dart :: M", "app/a.dart :: A"])
rc, out = run_audit("--scope", sp, "--repo", d)
ok_b = rc == 2 and "action 矛盾" in out and "L" in out
check("U4 段数不足坏行＋同路径 action 矛盾 → rc 2 报行号", ok_a and ok_b)

# U5 git mv：D+A 双侧均命中
d = make_repo()
sp = write_scope(d, ["old.dart :: D", "new.dart :: A"])
sh(d, "mv", "old.dart", "new.dart")
rc, out = run_audit("--scope", sp, "--repo", d)
check("U5 git mv 清单内文件 → D+A 双侧命中 rc 0",
      rc == 0 and "命中清单（2）" in out and "old.dart" in out and "new.dart" in out)

# U6 --baseline 跨提交分叉：已 commit 后显式 baseline 可见；口径标签在报告头
d = make_repo()
sp = write_scope(d, ["app/a.dart :: M"])
touch(d, "app/a.dart", "x\n")
sh(d, "add", "-A")
sh(d, "commit", "-q", "-m", "批改动")
rc, out = run_audit("--scope", sp, "--repo", d, "--baseline", "HEAD~1")
check("U6 --baseline HEAD~1 跨提交 → 命中 1 且口径标签在报告头",
      rc == 0 and "命中清单（1）" in out and "HEAD~1 .. 工作区" in out)

# U7 note 含 :: → maxsplit=2 右段全吞
d = make_repo()
sp = write_scope(d, ["app/a.dart :: M :: 备注带 :: 冒号 :: 三段以上"])
touch(d, "app/a.dart", "x\n")
rc, out = run_audit("--scope", sp, "--repo", d)
check("U7 note 含 :: → 右段全吞 rc 0", rc == 0 and "命中清单（1）" in out)

# U8 CRLF 行尾 → strip 后解析
d = make_repo()
sp = write_scope(d, ["app/a.dart :: M"], sep="\r\n")
touch(d, "app/a.dart", "x\n")
rc, out = run_audit("--scope", sp, "--repo", d)
check("U8 block CRLF 行尾 → 解析不受扰 rc 0", rc == 0 and "命中清单（1）" in out)

# U9 空行＋# 注释行合法
d = make_repo()
sp = write_scope(d, ["# 注释行合法", "", "app/a.dart :: M", ""])
touch(d, "app/a.dart", "x\n")
rc, out = run_audit("--scope", sp, "--repo", d)
check("U9 空行＋# 注释行 → 合法跳过 rc 0", rc == 0 and "命中清单（1）" in out)

# U10 glob×action：src/** 下新增 → 命中＋action 不符提示＋glob 计数，不判越界
d = make_repo()
sp = write_scope(d, ["src/** :: M"])
touch(d, "src/x.dart", "x\n")
rc, out = run_audit("--scope", sp, "--repo", d)
check("U10 glob 命中新增 → action 不符提示不判越界＋glob 计数",
      rc == 0 and "命中清单（1）" in out and "action 不符" in out
      and "src/x.dart" in out and "src/** ×1" in out and "越界嫌疑（0）" in out)

# U11 噪音单列：子模块指针 M＋生成文件 M＋真越界 M → 仅真越界计 rc 1
d = make_repo({".gitmodules": '[submodule "x"]\n\tpath = subm\n\turl = https://example/x.git\n'})
sh(d, "update-index", "--add", "--cacheinfo", "160000,0000000000000000000000000000000000000001,subm")
sh(d, "commit", "-q", "-m", "sublink")
sh(d, "update-index", "--cacheinfo", "160000,0000000000000000000000000000000000000002,subm")
sp = write_scope(d, ["app/a.dart :: M"])
touch(d, "z.g.dart", "x\n")       # 生成文件·清单外
touch(d, "lib/b.dart", "x\n")     # 真越界
rc, out = run_audit("--scope", sp, "--repo", d)
check("U11 子模块指针＋生成文件单列噪音 → 仅真越界计 rc 1",
      rc == 1 and "已知噪音·子模块指针（不计越界）（1）" in out and "subm" in out
      and "已知噪音·生成文件（不计越界）（1）" in out and "z.g.dart" in out
      and "清单外改存量·越界嫌疑（1）" in out and "lib/b.dart" in out)

# U12 已 commit 零工作区 diff → rc 0＋空 diff 警示行
d = make_repo()
sp = write_scope(d, ["app/a.dart :: M"])
touch(d, "app/a.dart", "x\n")
sh(d, "add", "-A")
sh(d, "commit", "-q", "-m", "批改动")
rc, out = run_audit("--scope", sp, "--repo", d)
check("U12 已 commit 零工作区 diff → 空 diff 警示行（假绿比报错更贵）",
      rc == 0 and "空 diff" in out and "--baseline" in out)

# U13 非 ASCII 路径：git core.quotePath 默认八进制转义致中文路径漏判（AC7 自反首审实证）→ 修复后字面命中
d = make_repo({"组件/卡片.dart": "c\n"})
sp = write_scope(d, ["组件/卡片.dart :: M"])
touch(d, "组件/卡片.dart", "x\n")
touch(d, "组件/新文件.dart", "n\n")
rc, out = run_audit("--scope", sp, "--repo", d)
check("U13 中文路径 quotePath=false → 字面命中不转义误判",
      rc == 0 and "命中清单（1）" in out and "组件/卡片.dart" in out
      and "扩容候选（1）" in out and "组件/新文件.dart" in out
      and "350" not in out)

# U14 点开头路径：lstrip("./") 会把 .claude-plugin 类路径的开头点吃掉致漏判（收口批实弹发现）→ 修复后字面命中
d = make_repo()
os.makedirs(os.path.join(d, ".claude-plugin"), exist_ok=True)
with open(os.path.join(d, ".claude-plugin", "plugin.json"), "w", encoding="utf-8") as f:
    f.write('{"version": "1.3.9"}\n')
sh(d, "add", "-A")
sh(d, "commit", "-q", "-m", "dotdir")
with open(os.path.join(d, ".claude-plugin", "plugin.json"), "a", encoding="utf-8") as f:
    f.write('{"x": 1}\n')
sp = write_scope(d, [".claude-plugin/plugin.json :: M :: bump", "app/a.dart :: M"])
touch(d, "app/a.dart", "x\n")
rc, out = run_audit("--scope", sp, "--repo", d)
check("U14 点开头路径 → 字面命中不被 lstrip 吃掉",
      rc == 0 and "命中清单（2）" in out and ".claude-plugin/plugin.json" in out
      and "越界嫌疑（0）" in out)

# 附：用法错三形 → rc 2（缺 --scope／--head 单给／档无 block）
rc1, out1 = run_audit("--repo", d)
rc2, out2 = run_audit("--scope", sp, "--repo", d, "--head", "HEAD")
noblk = os.path.join(SCOPE_DIR, "NOBLOCK.md")
with open(noblk, "w", encoding="utf-8") as f:
    f.write("无 block 的普通方案档\n")
rc3, out3 = run_audit("--scope", noblk, "--repo", d)
check("附 用法错三形 → rc 2（缺参／--head 单给／无 block 明示散文判回落）",
      rc1 == 2 and rc2 == 2 and rc3 == 2 and "scope 缺失" in out3)

print(f"scope-audit fixture: {'全绿' if fails == 0 else f'{fails} 失败'}")
sys.exit(1 if fails else 0)
