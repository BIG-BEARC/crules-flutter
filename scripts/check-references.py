#!/usr/bin/env python3
"""引用完整性闸——md 死链＋入口悬空双断面（1.0.32 链接解析闸的接替件，语义承继＋增强）。

  links   md 互链死链：[文](目标) 相对路径目标须存在。跳过 code fence 与行内反引号 span
         （示例内容不作真链核——对 1.0.32 闸的增强，防「错误示例」假红）；file#anchor
         只剥片段，锚点存在性校验缓（phase 2）。
  entries 入口悬空：/crules-flutter:X 须有 commands/X.md 或 agents/X.md（只守斜杠命令
         形口径，无斜杠提及形不设防）；「X skill」须在本仓 skills/ 或外部白名单。缺省
         面＝全分发面 glob（README/checklist/CHANGELOG/commands/agents/进阶/docs 清单·
         梳理/skills SKILL·references·templates/app·plugin CLAUDE/memory/canonical）；
         方案·评审·验证 transient 稿不入面（工作稿可引未来入口；示例命令一律写
         /crules-flutter:<占位> 形——尖括号不入正则，即逃生形）。

语义承继（自 test-self 1.0.32 内联闸，裁决随迁）：
  - .superpowers/ 豁免（1.0.42 主控裁决：本机 SDD 过程面，非分发面）；
  - changelog-annex 入扫（1.3.1 B 案撤豁免：单页化后无历史流水账死链面）；
  - 占位指引一律纯文字、不写链接格式（1.0.32 纪律：白名单只认 scheme 与空锚）。

盲区清单（假绿向，登记不修）：reference-style [t][ref]；badge 嵌套外层；unclosed
fence 后尾段；URL 含圆括号截断；无斜杠命令提及形；含数字/大写命令名。

用法：python3 scripts/check-references.py <仓根> links
      python3 scripts/check-references.py <仓根> entries [面...]   # 缺省＝全分发面
退出码：0 绿／1 有发现／2 用法错。红绿双向断言在 scripts/test-self.sh（防假绿——零发现
须有对照红证明探针活着）。改断面（白名单／面集）须同步 test-self 断言与 README 巡检行。"""
import glob, os, re, sys

EXTERNAL_SKILLS = {"dart-flutter", "superpowers", "browser-skill"}  # 外部插件技能，非本仓件
EXCLUDE_DIRS = {".git", "__pycache__", "node_modules", ".claude", ".superpowers"}  # .superpowers：1.0.42 裁决豁免
LINK_RE = re.compile(r'\[([^\]]*)\]\(<*([^)>\s]+)>*(?:\s+"[^"]*")?\)')
INLINE_SPAN_RE = re.compile(r'`[^`]+`')
DEFAULT_FACE_GLOBS = [
    "README.md", "checklist.md", "CHANGELOG.md",
    "commands/*.md", "agents/*.md", "进阶/*.md",
    "docs/清单*.md", "docs/梳理*.md",
    "skills/*/SKILL.md", "skills/*/references/*.md", "skills/*/templates/*.md",
    "app/CLAUDE.md", "plugin/CLAUDE.md", "memory/*.md", "canonical/*.md",
]

def md_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            if fn.endswith(".md"):
                yield os.path.join(dirpath, fn)

def check_links(root):
    dead = []
    for p in md_files(root):
        in_fence = False
        with open(p, encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, 1):
                if line.lstrip().startswith(("```", "~~~")):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                for _, tgt in LINK_RE.findall(INLINE_SPAN_RE.sub(' ', line)):
                    t = tgt.split("#")[0].strip()
                    if not t or re.match(r"^[a-z][a-z0-9+.-]*:", t):  # scheme 与空锚外无白名单——占位走纯文字（1.0.32 纪律）
                        continue
                    resolved = os.path.normpath(os.path.join(os.path.dirname(p), t))
                    if not os.path.exists(resolved):
                        dead.append(f"{os.path.relpath(p, root)}:{i} -> {t}")
    return dead

def check_entries(root, faces):
    missing, skill_unknown = [], []
    prefix_files = {}
    for sub in ("commands", "agents"):
        d = os.path.join(root, sub)
        if os.path.isdir(d):
            for fn in os.listdir(d):
                if fn.endswith(".md"):
                    prefix_files.setdefault(fn[:-3], []).append(sub)
    skill_dirs = set()
    sd = os.path.join(root, "skills")
    if os.path.isdir(sd):
        skill_dirs = {d for d in os.listdir(sd) if os.path.isdir(os.path.join(sd, d))}
    skill_re = re.compile(r'\b([a-z][a-z0-9-]*)\**\s+skill\b')
    cmd_re = re.compile(r"/crules-flutter:([a-z-]+)")
    for face in faces:
        p = os.path.join(root, face)
        if not os.path.isfile(p):
            missing.append(f"[面缺失] {face}")
            continue
        text = open(p, encoding="utf-8", errors="replace").read()
        for n in sorted(set(cmd_re.findall(text))):
            if n not in prefix_files:
                missing.append(f"{face}: /crules-flutter:{n} 无件（commands/agents 均无）")
        for n in sorted(set(skill_re.findall(text))):
            if n in skill_dirs or n in EXTERNAL_SKILLS:
                continue
            skill_unknown.append(f"{face}: 「{n} skill」不在本仓 skills/ 且不在外部白名单")
    return missing, skill_unknown

def expand_faces(root, patterns):
    """默认面 glob 展开；无通配符的固定面未命中＝发现（README 缺失不该静默绿）。"""
    faces, missing_fixed = [], []
    for pat in patterns:
        hit = [os.path.relpath(p, root) for p in glob.glob(os.path.join(root, pat))]
        if hit:
            faces.extend(sorted(hit))
        elif "*" not in pat:
            missing_fixed.append(pat)
    return faces, missing_fixed

def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    root = os.path.abspath(sys.argv[1])
    mode = sys.argv[2]
    if mode == "links":
        dead = check_links(root)
        print(f"[links] 死链 {len(dead)} 条（annex 入扫）")
        for d in dead:
            print("  " + d)
        sys.exit(1 if dead else 0)
    if mode == "entries":
        faces = sys.argv[3:]
        if any(f.startswith("--") for f in faces):
            print("entries 不认旗标（links 亦无旗标——annex 恒入扫）"); sys.exit(2)
        missing_fixed = []
        if not faces:
            faces, missing_fixed = expand_faces(root, DEFAULT_FACE_GLOBS)
        missing, unknown = check_entries(root, faces)
        missing += [f"[面缺失·固定面] {f}" for f in missing_fixed]
        print(f"[entries] 面 {len(faces)} 件")
        print(f"  悬空入口 {len(missing)} 条")
        for m in missing:
            print("   ! " + m)
        print(f"  未识技能 {len(unknown)} 条（白名单候选）")
        for u in unknown:
            print("   ? " + u)
        sys.exit(1 if missing else 0)
    print("mode 须为 links|entries"); sys.exit(2)

if __name__ == "__main__":
    main()
