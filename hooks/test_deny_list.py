#!/usr/bin/env python3
# SYNCED-FROM: crules@ea4d25c（test_deny_list.py——deny-list 安全修复以 crules 为单一权威，CI 同步比对步看守；变更须从 crules 同步后再动此文件）
"""deny-list 回归测试（v37 沉淀——修正 v35「单测 15/15 跑完即弃、无文件无痕」）。

跑法：python3 hooks/test_deny_list.py（scripts/check-consistency.sh 的 H 查调用）
fixture 原则：该拦全拦（含 v37 外审 5 绕过）、该放全放（含 --force-with-lease / /tmp 白名单）；
新增绕过形态时**先加 fixture（红）→ 修 deny-list（绿）**，测试即对抗样本库。
探测纪律（v41，第三轮红队假证据教训）：对 deny-list 做人工/脚本探测时，输入 JSON
必须用 json.dumps 构造（如本文件 :97），**禁止 shell 手拼**——手拼含引号命令会产生
非法 JSON，脚本 json.load 失败即 exit(0)，探测结果恒为「放行」的假证据。
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))

# 应拦：v35 原 10 例 + v37 外审绕过 5 例 + 加固新增 4 例
BLOCK_CASES = [
    # --- v35 原有 ---
    "git push --force origin main",
    "git reset --hard HEAD~1",
    "rm -rf ~/Downloads",
    "rm -rf build",
    "git clean -fd",
    "git branch -D feat",
    "cd src && rm -rf lib",
    "echo hi && git reset --hard",
    "git checkout -- .",
    "git push origin :old-branch",
    # --- v37 外审绕过（回归防线）---
    "echo hi\ngit reset --hard HEAD",        # 换行切分
    "true | git push --force origin main",   # 单管道切分
    "git push origin +main:main",            # +refspec 强推
    "git checkout .",                        # 裸 . 不带 --
    "git restore :/",                        # 全树 pathspec
    "rm --recursive --force build",          # 长选项
    # --- v37 加固新增 ---
    "git restore .",
    "git checkout :/",
    "FOO=1 git reset --hard",                # 前缀环境变量赋值
    "command git clean -fd",                 # command 前缀
    # --- v39 红队 8 向量（v38 外审裁定收敛修复）---
    "sudo git reset --hard",                 # 前缀同族：sudo
    "env git push --force origin main",      # 前缀同族：env
    "(git reset --hard HEAD)",               # 子 shell 包裹
    "$(git push --force origin main)",       # 命令替换包裹
    "git checkout ./",                       # 尾斜杠逃逸（v37 漏修）
    "git restore ./",                        # 同上
    "git checkout -- *",                     # glob 等价全丢弃
    "rm -rf /tmp/../Users",                  # 白名单前缀穿越（normpath 收口）
    # --- v39 前轮未修 3 + 追加 ---
    "git -C somedir reset --hard",           # 全局选项插花
    "git push origin +main",                 # +refspec 无冒号强推
    "sudo -u root git clean -fd",            # 带参数前缀
    "echo `git reset --hard`",               # 反引号包裹
    "echo '参考：git reset --hard 的用法'",   # 字符串误拦样本（deny-by-default 文档化取舍）
    # --- v40 红队 R1-R3 + 边角（外审复核全属实）---
    "git checkout -f main",                  # R1：-f 强切丢弃未提交改动
    "git checkout -f",                       # R1 同族：无 pathspec
    "git switch -f main",                    # R1 同族（外审补充：switch 不在签名内）
    'git checkout "."',                      # R2：引号 pathspec
    'git restore "./"',                      # R2 同上
    "git checkout -- '*'",                   # R2 同根：引号 glob（v39 残留#1）
    "git stash clear",                       # R3 裁决：clear 进名单
    "git push --force-with-lease --force origin main",  # 边角：lease 在前 force 在后（git 语义 force 生效）
    "git restore -s HEAD .",                 # v39 残留#2：-s HEAD 与 --source=HEAD 对齐
    "git log --grep=checkout .",             # v39 残留#3：选项值含签名词的 FP 类（文档化取舍）
    # --- v47 批次一（08-18 外审 5 向量 + 裁定 B dry-run×force 信号即拦 + 空操作数）---
    "find . -name '*.log' | xargs rm -rf",     # 向量1：xargs 注入，rm 无显式操作数（paths 空集空真放行）
    "git branch --delete --force feat",        # 向量2：-D 长选项等价拼法
    "git branch -d -f feat",                   # 向量3：-D 分离旗标等价拼法
    "git push -fv origin main",                # 向量4：push 短旗标捆绑（-fq 同族）
    "git checkout -qf main",                   # 向量5：force_switch 捆绑 -qf ≠ -f
    "git push -fn origin main",                # 裁定 B：dry-run×force 组合信号即拦
    "git push --dry-run --force origin main",  # 裁定 B 同上（长选项组合；当前已拦，行为锁定）
    "git push -n origin +main",                # 裁定 B：dry-run + refspec 强推（当前已拦，锁定）
    "git push --delete -n origin old-branch",  # 裁定 B：dry-run + 删远端分支（当前已拦，锁定）
    "rm -rf build 2>&1",                       # 重定向 token 兼查：非白名单路径 + 重定向 → 仍拦
]

# 应放：正常命令 / 白名单 / 安全变体
ALLOW_CASES = [
    "git push origin main",
    "git push --force-with-lease",           # 安全强推变体
    "git push origin main:main",             # 普通 refspec（无 +）
    "git status",
    "rm -rf /tmp/junk",                      # 临时目录白名单
    "rm build",                              # 无递归
    "rm -r build_dir",                       # 只递归无强制
    "ls -la",
    "git log --oneline",
    "git checkout main",                     # 切分支（非丢弃）
    "git checkout -b feat",                  # 建分支
    "git restore -s stash@{1} .",            # 指定源恢复（非丢弃工作区）
    "echo 'a|b'",                            # 引号内的管道符
    "pip install --force",                   # 非 git push 的 --force
    # --- v39 dry-run 放行（修 v38 发现的误拦）---
    "git clean -nfd",                        # -n dry-run，无害
    "git clean -nd",                         # 同上
    # --- v40（R2 白名单引号 / R3 裁决边界 / 新签名 FP 边界锁定）---
    'rm -rf "/tmp/x"',                       # R2 误拦修复：引号白名单路径
    'rm -rf "/var/folders/abc"',             # 同上
    "git stash drop stash@{1}",              # R3 裁决边界：drop 不进名单
    "git stash pop",                         # R3 裁决边界：pop 不拦
    "git switch main",                       # switch 基础形态不误拦
    "git switch -c feat",                    # switch 建分支不拦
    "git checkout -f -b hotfix",             # -f 搭配 -b 建分支：例外放行
    # --- v47 重定向 FP 修复（重定向 token 不作 path 参与白名单判定）---
    "rm -rf /tmp/x 2>/dev/null",               # 白名单路径 + 重定向 → 放（当前误拦，修复后放行）
]

def should_block(case: str) -> bool:
    p = subprocess.run(
        [sys.executable, os.path.join(HERE, "deny-list.py")],
        input=json.dumps({"tool_input": {"command": case}}),
        capture_output=True, text=True,
    )
    return '"block"' in p.stdout

def main() -> int:
    fails = []
    for c in BLOCK_CASES:
        if not should_block(c):
            fails.append(f"应拦未拦: {c!r}")
    for c in ALLOW_CASES:
        if should_block(c):
            fails.append(f"应放未放: {c!r}")
    # v52：拦截文案回归断言（blocked() 单出口追加「不要尝试绕过」——拦/放二元测不出文案回归）
    p = subprocess.run(
        [sys.executable, os.path.join(HERE, "deny-list.py")],
        input=json.dumps({"tool_input": {"command": "git push --force origin main"}}),
        capture_output=True, text=True,
    )
    if "不要尝试绕过" not in p.stdout:
        fails.append("拦截文案缺「不要尝试绕过」提示（blocked() 追加语回归）")
    for f in fails:
        print("FAIL", f)
    print(f"deny-list 测试: {len(BLOCK_CASES)} 拦 + {len(ALLOW_CASES)} 放, 失败 {len(fails)}")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
