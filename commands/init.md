---
description: 初始化 crules-flutter——把 Flutter 工程接入协作规则（丁-Copy 指针落位 + 引导必填项）
disable-model-invocation: true
---

# /crules-flutter:init

把 crules-flutter 装进当前 Flutter 工程——**丁-Copy 形态**（1.1.5 起）：未跟踪指针 `.claude/CLAUDE.md`（四行）＋宪法副本 `.claude/crules/constitution.md`＋memory 种子。**不碰任何受控文件**（R0 红线）：根 CLAUDE.md / checklist / `analysis_options.yaml` / `进阶/` 一律不落位——权威源在插件 cache（去分发化，丁-Copy 裁 1.1.5；方案稿 2026-10-26 删档，插件仓 git 史可查）。

## 执行步骤

### 0. 定位源（glob 自发现——`${CLAUDE_PLUGIN_ROOT}` 仅 hook 进程内可用，Bash 工具环境为空，不可依赖）

```bash
# ① plugin cache 最大版本（命令的主受众——cache 安装用户）
ls -d ~/.claude/plugins/cache/*/crules-flutter/*/app/CLAUDE.md | sort -V | tail -1 | xargs dirname
# ② 找不到（本地开发态 / 手动部署）→ 提示需求方给 crules-flutter 仓库路径后停止
```

取到源根 `$SRC` 后一切操作用绝对路径；戳行版本 `$VER` 读 `$SRC/.claude-plugin/plugin.json` 的 `version`。

### 1. 分流（自动）

- **根 `CLAUDE.md` 有 `<!-- crules-flutter: v` 戳** → 丁-tracked 老形态（宪法曾复制进项目根 `CLAUDE.md`、随 git 跟踪）：**不自动迁移**（存量原子切=一次性授权批，宪法纪律：提醒≠代执行）——告知现状与迁移路径后停
- **`.claude/CLAUDE.md` 有戳**（指针已在）→ 刷新路径：走步骤 3（副本对拍 + 指针重写即刷戳），步骤 5 仅补未填项
- **两者皆无** → 新装（步骤 2 起）
- 根 `CLAUDE.md` 存在但**无戳**（项目自有宪法）→ 可共存（实证：同场双载、根先指针后、项目事实胜）——提示共存与优先级后继续
- `.claude/CLAUDE.md` 存在但**无戳**（本机自建件）→ **不覆盖**，呈需求方裁决

### 2. 问形态（新项目）

App 工程（`app/` 宪法）还是 Plugin/工具库（`plugin/` 宪法）？——不确定时看 `pubspec.yaml` 有无 `flutter.plugin.platforms` 声明。

### 3. 机械落位（bash 确定性操作；全部写**未跟踪本机态**）

```bash
ROOT=<项目根>; SRC=<源根>; KIND=app 或 plugin
VER=$(grep -m1 -oE '"version":[[:space:]]*"[0-9]+\.[0-9]+\.[0-9]+"' "$SRC/.claude-plugin/plugin.json" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
mkdir -p "$ROOT/.claude/crules" "$ROOT/.claude/memory" "$ROOT/.claude/memory/indexes" "$ROOT/.claude/memory/decisions"

# R0 基线快照（落位前 tracked 面状态，收尾自检对比用；无 git 仓时为空文件）
git -C "$ROOT" status --porcelain 2>/dev/null | sort > "/tmp/crules-init-baseline.$$" || : > "/tmp/crules-init-baseline.$$"

# ① 宪法副本（共享纪律层——项目内容一律不写进副本，保持 pristine 可哈希对拍）
#    不存在 → 拷；已存在且不一致 → 曾被手改或待升级：先 diff 呈报，需求方确认后
#    AI 另行执行同型 cp（本块不静默覆盖——禁静默覆盖）
if [ ! -f "$ROOT/.claude/crules/constitution.md" ]; then
  cp "$SRC/$KIND/CLAUDE.md" "$ROOT/.claude/crules/constitution.md"
elif ! cmp -s "$SRC/$KIND/CLAUDE.md" "$ROOT/.claude/crules/constitution.md"; then
  echo "副本不一致——AI 先 diff 呈报，经需求方确认后另行执行 cp 覆盖"
fi

# ② 指针四行（本文件=配方单一事实源，勿在他处复制）
printf '<!-- crules-flutter: v%s -->\n@crules/constitution.md\n@memory/NAVIGATION.md\n@memory/PROJECT.md\n' "$VER" > "$ROOT/.claude/CLAUDE.md"

# ③ memory 种子（9 件含 PROJECT.md）：缺则补、**永不覆盖**（落地即项目制度资产）
for f in "$SRC"/memory/*.md; do
  [ -e "$ROOT/.claude/memory/$(basename "$f")" ] || cp "$f" "$ROOT/.claude/memory/$(basename "$f")"
done

# 宪法副本哈希入 state（副本内容漂移此前零检测面，机制化于 2026-10-19）——读改写保留既有键。
# 解释器 python3→python 兜底探测（hooks 同规：只装 python 无 python3 别名的机器也落位）；
#   两解释器皆缺或写键失败，自检区「state 哈希键」行显式呈报——对拍闸不生效不允许静默。
PYBIN="$(command -v python3 || command -v python || true)"
if [ -n "$PYBIN" ]; then "$PYBIN" - "$ROOT/.claude/crules/constitution.md" "$ROOT/.claude/memory/.crules-state" <<'PY'
import hashlib, os, sys
src, state = sys.argv[1], sys.argv[2]
sha = hashlib.sha256(open(src, "rb").read()).hexdigest()
d = {}
if os.path.exists(state):
    for ln in open(state, encoding="utf-8"):
        if "=" in ln:
            k, v = ln.strip().split("=", 1); d[k] = v
d["constitution_sha256"] = sha
d.setdefault("ao_adopted", "0")   # state 首建时补 AO 缺省（与下 ④ 行幂等共存）
open(state, "w", encoding="utf-8").write("".join(f"{k}={v}\n" for k, v in d.items()))
PY
fi

# ④ 本机态标记（AO 人择通道记账）
[ -f "$ROOT/.claude/memory/.crules-state" ] || printf 'ao_adopted=0\n' > "$ROOT/.claude/memory/.crules-state"
```

**落位后自检（逐条跑、输出贴给需求方）**：

```bash
[ "$(grep -c '^@' "$ROOT/.claude/CLAUDE.md")" = "3" ]                      # 指针 ③ 行导入
cmp -s "$SRC/$KIND/CLAUDE.md" "$ROOT/.claude/crules/constitution.md"       # 副本逐字
! grep -q '^@' "$ROOT/.claude/crules/constitution.md"                      # 宪法源零 @ 内链（1.1.5 清理恒真）
grep -q '^constitution_sha256=' "$ROOT/.claude/memory/.crules-state" 2>/dev/null \
  && echo "state 哈希键已落位" \
  || echo "❌ state 哈希键缺失——副本对拍闸在本机不生效（解释器缺或写键失败），收尾汇报如实呈报"
# R0 自检：对比基线，只看 init 期间**新增**的 tracked 变动（存量脏行不归因于 init）
git -C "$ROOT" status --porcelain 2>/dev/null | sort > "/tmp/crules-init-after.$$" || : > "/tmp/crules-init-after.$$"
if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  comm -13 "/tmp/crules-init-baseline.$$" "/tmp/crules-init-after.$$" | grep -v '^??' \
    && echo "❌ init 新增 tracked 变动" || echo "R0 绿：init 零新增 tracked 变动（untracked 新增属预期）"
else
  echo "无 git 仓库——R0 自检跳过（无可对比面，如实呈报）"
fi
rm -f "/tmp/crules-init-baseline.$$" "/tmp/crules-init-after.$$"
```

（`.claude/` 已 ignore 的工程连 untracked 都不出现；无 ignore 行工程出现 `?? .claude/` 属预期——提示需求方按 MAINTENANCE「git 分层」处理，AI 不代写受控 `.gitignore`。）

### 4. AGENTS.md 抑制检测

项目根有 `AGENTS.md` → 提示：宿主对部分形态以 AGENTS.md 优先、可能抑制 CLAUDE.md 家族加载——宪法仍建议落位，整合与否由需求方裁决，不静默改写。

### 5. 引导必填（AI 交互——**全部写 `.claude/memory/PROJECT.md`**，宪法副本永不改）

1. **§七 技术栈**：App 三选一（含适配方案 A1 弹性+断点〔默认推荐〕/ A2 设计稿缩放 / A3 自定义）或 Plugin 类型二选一（方案全文在 flutter-rules skill `references/layout.md` 适配节 / `references/state-management.md` 预设族——1.3.0 自宪法下沉）；**字体策略**公共必选（离线/内网设备提示字体打包路线，坑卡「系统字体回退不可信」）→ 写 PROJECT.md「§七」节
2. **档位预设三选一**（轻量〔light〕/ 标准〔normal〕/ 完整〔full〕，无档位行 = 默认标准）→ 写 PROJECT.md 档位行。**不可配置项**（deny-list hook / 协作红线 / lint 硬拦）无开关，不引导配置。**轻量档另触发**：仅删指针 ③ 行（NAVIGATION 常驻导入关）——指针 ④ 行与 PROJECT.md **必留**（档位行 / §七 / §十二 是 agents·skills·宪法覆写的锚点，删即断链）；其余 memory 种子留着、停维护即「记忆库关」（不删文件，将来升档零成本）
3. **项目附录 3 必填**：项目名 / 构建·分析·测试命令 /（协作偏好可选项）→ PROJECT.md「§十二」节
4. **支持矩阵三段式** → `.claude/memory/platform-pitfalls.md` 头部：①机械读（`ls` 平台目录、`grep minSdk` / `platform :ios`；解析失败保留占位符不瞎填）②人核对（未发版平台划掉）③人补（实测上限、现场设备实态）
5. **NAVIGATION 占位表裁剪**：删/改 `<common-widget-dir>` 等占位行为项目实际目录（防每会话内联占位垃圾）
6. 提示：flutter-rules / parity-rewrite 两 skill、7 个 agent 已随 plugin 就位；上手 15 分钟闭环见 cache `进阶/上手教程.md`

### 6. AO 建议稿（AO 人择通道——静态 lint 从「随发」转「建议」，零功能损失：三工程基线从未生效）

```bash
# 缺则补、永不覆盖（与 memory 种子同语义——需求方对建议稿的手批注不丢）
[ -f "$ROOT/.claude/memory/analysis-options.suggested.yaml" ] \
  || cp "$SRC/analysis_options.yaml" "$ROOT/.claude/memory/analysis-options.suggested.yaml"
```

提示需求方：采纳=手工并入项目自己的 `analysis_options.yaml`（受控文件，AI 不代改），采纳后把 `.claude/memory/.crules-state` 的 `ao_adopted` 置 1（复核时机：flutter_lints 大版本升级时人工复核建议稿——自动提示待接线）。

### 7. 收尾汇报

落位清单（指针/副本 sha256/种子件数/state 哈希键成败）＋自检五条输出＋R0 机械证据（基线对比输出贴出）＋一句「删 `.claude/CLAUDE.md` 指针（连同 `.claude/crules/`）即整体回退；`.claude/memory/` 为项目资产，去留自裁」。

## 依据

- 丁-Copy 载体（v4.0·Q6 裁，2026-10-15；方案稿 2026-10-26 删档，插件仓 git 史可查）：全内部相对导入零审批面、`-p` 直载实证、副本本机自持抗丢
- R0：常态机制永不写受控文件——本命令全部写未跟踪本机态，机械自检可证
- 禁静默覆盖：副本对拍不一致 / 无戳 `.claude/CLAUDE.md` / 丁-tracked 存量，三者一律呈人裁决

## 注意

- 只动规则载体与 memory 种子，**不写业务代码**；重跑安全（幂等：种子缺则补、副本对拍、指针重写）
- 消费工程内禁 `claude -p` 冒烟（探针一律 /tmp 沙盒）
