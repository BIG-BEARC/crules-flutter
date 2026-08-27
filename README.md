# crules-flutter

面向 **Flutter 工程**的独立协作规则 plugin——通用协作层 fork 自 [crules](https://github.com/BIG-BEARC/crules) 基线 `v74-fork-base`（commit ea4d25c），**此后独立演进、互不依赖**（唯一例外见「与 crules 的关系」）。

> **当前状态：批 2a/2b 已完成**——两模板重组为本尊（覆盖 diff 验收：[docs/fork-coverage.md](docs/fork-coverage.md)）、checklist 自持、进阶 5 篇 + memory + agents 通用角色落位、rules skill 化。**剩批 2c（hooks + CI 同步比对 + scripts）与批 3/4**（方案见 crules 仓 `docs/整合方案-crules-flutter.md`）。

---

## 怎么用

```bash
# ① 一次性：装 plugin（git URL 源，user scope，不进任何项目 git）
claude plugin marketplace add https://github.com/BIG-BEARC/crules-flutter.git --scope user
claude plugin install crules-flutter@crules-flutter-market --scope user

# ② 新工程：复制 app/CLAUDE.md（App）或 plugin/CLAUDE.md（Plugin/工具库）到项目根，
#    完成模板内【复制后必填】的技术栈选型
```

### 环境要求与更新信任

- **环境要求：macOS / Linux**（hooks 依赖 `python3` 与 `fcntl`；Windows 上 hook 静默失效，终极防线回到原生权限确认——批 2c 起携带 hooks）
- **更新信任（供应链）**：本 plugin 的 hooks 在每次 Bash 调用前执行——`plugin update` 后新 hook 代码静默生效，被污染的更新 = 任意代码执行。建议 update 前先看 hooks 变更（`git -C <本仓> diff <旧tag>..<新tag> -- hooks/`）或锁定 commit。

### 停用与恢复

| 操作 | 命令 |
|---|---|
| 停用（可逆） | `claude plugin disable crules-flutter@crules-flutter-market` |
| 恢复 | `claude plugin enable crules-flutter@crules-flutter-market`（**完整形态**，纯名会 not found；**新会话生效**——当前会话不装载 hooks，别在旧会话验证） |
| 彻底卸 | `claude plugin uninstall crules-flutter@crules-flutter-market` + `claude plugin marketplace remove crules-flutter-market` |

## 与 crules 的关系（种子库模式）

```text
crules（母版，保持活跃）──fork──► crules-flutter（本包，独立演进）
              ▲ deny-list 安全修复单向同步（CI 比对，见下）
```

- **fork 基线**：`v74-fork-base`（crules 的 CLAUDE.md / 进阶 / hooks / 机制件于此点复制，此后本包自持）
- **边界判据**：与 Dart/Flutter 无关的协作改进 → 在 crules 改，本包自行决定是否跟随；技术栈相关 → 只进本包
- **跟/不跟查表**：crules 的 **deny-list 安全修复必跟**（同步义务机械化，见下）；其余规则演进**默认不跟**；跟则 bump 本包 minor
- **deny-list 同步义务（唯一例外）**：`hooks/deny-list.py` 与 `hooks/test_deny_list.py` 以 crules 为单一权威（红队补丁只发生在母版）——文件头 `SYNCED-FROM: crules@<hash>` 戳 + CI 同步比对步（拉 crules 主分支两文件 diff，不一致 exit 1）。批 2c 落地。
- **双 plugin 共存**（同机器既维护 crules 又开发 Flutter 工程是常态）：**同一项目二选一**（crules 或 crules-flutter，勿双装）；同机器不同项目各装各的无冲突——万一两套 hooks 同项目双跑：deny-list 并集拦截（任一 block 即 block，保守无害）、pending-updates 写同一队列文件经 flock 幂等。

## 维护

- 本仓独立演进：bump 双 json → `plugin update` → cache 特征串验证（纪律继承 crules v31）
- 治理从简：README + CHANGELOG + 最简检查（crules 的五维雷达/评审轮次体系**不复制**——治理成本延后到真有痛感再付）
- 定期外审选项保留（crules 的独立 subagent 复审模式可复用，防规则滑向单项目特有）
