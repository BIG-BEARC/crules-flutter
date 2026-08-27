---
description: 初始化 crules-flutter——把 Flutter 工程接入协作规则（调 install.sh 机械安装 + 引导必填项）
disable-model-invocation: true
---

# /crules-flutter:init

把 crules-flutter 装进当前 Flutter 工程。**只动规则文件，不碰业务代码**。

## 执行步骤

### 0. 定位源（glob 自发现——`${CLAUDE_PLUGIN_ROOT}` 仅 hook 进程内可用，Bash 工具环境为空，不可依赖）

```bash
# ① plugin cache 最大版本（命令的主受众——cache 安装用户）
ls -d ~/.claude/plugins/cache/*/crules-flutter/*/scripts/install.sh | sort -V | tail -1
# ② 找不到（本地开发态 / 手动部署）→ 提示需求方给 crules-flutter 仓库路径后停止
```

取到源根后，后续 install / check-imports 均用该绝对路径（跨目录操作一律绝对路径纪律）。

### 1. 分流（自动）

- 项目根**无** `CLAUDE.md` → 新项目（步骤 2）
- **有** `CLAUDE.md`：
  - **无** `<!-- crules-flutter: v` 戳 → 老项目：**不自动安装**（禁静默覆盖）——提示需求方这是既有规则项目，给出选择：a) 人工对照模板合并（推荐：备份后逐节取舍，取舍记录落 `.claude/memory/decisions/`）b) 确认废弃旧规则后 `--force` 覆盖（须需求方显式确认）
  - **有戳** → 重装/升级：跑 `check-imports.sh` 报版本差 → 提示重跑 install（默认跳过已存在，改动聚焦两版本间变更）

### 2. 问形态（新项目）

App 工程（`app/` 模板）还是 Plugin/工具库（`plugin/` 模板）？——不确定时看 `pubspec.yaml` 有无 `flutter.plugin.platforms` 声明。

### 3. 跑机械安装（脚本确定性操作，AI 不手抄文件）

```bash
bash <源>/scripts/install.sh <项目根> --app | --plugin [--dry-run]
```

脚本行为：模板 CLAUDE.md + 版本戳 / checklist / `analysis_options.yaml`（项目已有 lint 配置则保留项目的）/ 进阶 / memory → 项目根；**agents 不复制**（plugin 已自动挂载 7 角色）；老项目护栏与幂等内建。需求方想先看全景时先跑 `--dry-run`。

### 4. 引导必填（AI 交互）

1. **§七【复制后必填】**：技术栈三选一（App）或插件类型二选一（Plugin）——逐项问清后**删掉未选项**、填「本项目最终技术栈/类型」行
2. **§十二项目附录 3 必填**：项目名 / 构建·分析·测试命令 / （协作偏好可选项提示：固定语言、提交触发词覆写、提速档）
3. 提示：flutter-rules skill 与 7 个 agent 已随 plugin 就位（无需复制）；导入巡检 `bash <源>/scripts/check-imports.sh <项目根>`

## 依据

- 机械/交互分工：install.sh 管确定性 cp（幂等可测），本命令管问答引导（外审 #5：消灭手动步骤 + agents plugin-only 后安装面更小）
- 禁静默覆盖：老项目分支不自动装（crules 老项目纪律同款）

## 注意

- 只装规则文件，**不写业务代码**；重跑安全（幂等，默认跳过已存在）
