# AI 记忆库 (.claude/memory/)

本目录是 Claude Code 的**结构化代码记忆库**，用于：

1. **防止重复造轮子** —— 实现新功能前必查，确认是否已有可复用的组件 / 工具 / 抽象
2. **保留架构决策** —— 关键架构决策的「为什么」
3. **加速大项目检索** —— 给 AI 一份「地图」，不用每次全库 grep

> git 纳管政策（单一权威见 [MAINTENANCE.md](MAINTENANCE.md)「git 分层」节）：**制度资产工程自裁纳管（默认本机态）、生成物不进**——`patterns.md` / `business-rules.md` / `INVARIANTS.md` / `decisions/` 要跨机不丢可自行纳管，`indexes/` / `.pending-updates*`（漂移队列，1.0.30 起按会话分文件）本机。crules-flutter 仓库中本目录是**种子模板**（init 种子到工程 `.claude/memory/`，缺则补、永不覆盖）。
> 完整维护规则见插件 cache `进阶/记忆库体系.md`；本目录运行时规则见 [MAINTENANCE.md](MAINTENANCE.md)。

## 文件结构

<!-- twin:mem-files -->
| 文件 | 用途 | 加载时机 |
|---|---|---|
| `NAVIGATION.md` | 顶层导航地图，告诉 AI 去哪找东西 | `.claude/CLAUDE.md` 指针 ③ 行启动内联（丁-Copy 接线，1.1.5） |
| `PROJECT.md` | 项目事实锚点：§七 技术栈 / §十二 附录·档位 / 支持矩阵指针（宪法副本保持原样、项目事实落此） | `.claude/CLAUDE.md` 指针 ④ 行启动内联；init 填写 |
| `MAINTENANCE.md` | 自动维护规则，AI 何时该更新本库 | NAVIGATION 指针按需 Read（不常驻） |
| `patterns.md` | 项目特有代码模式 | 实现新功能前 Read |
| `business-rules.md` | 业务真实规则（业务可达性，软约束·审查 Gate 拦） | 审查 / 方案评审涉域前 Read |
| `INVARIANTS.md` | 技术不变量（任何路径都必须成立，硬约束·测试拦） | 改约束密集模块前 Read |
| `reference-map.md` | 分域调研参考系（只存指针不存结论） | 涉成熟领域做方案前 Read |
| `platform-pitfalls.md` | 平台坑库（支持矩阵 + 结构化坑卡） | 引依赖 / 写平台代码 / 升级前 Read |
| `indexes/*.md` | 各核心目录的代码索引 | 在该目录工作前 Read |
| `decisions/YYYY-MM-DD-*.md` | 单次重要架构决策日志 | 涉及该模块改动时 Read |

## 触发更新

- 全量刷新：在 Claude Code 里发送 `/crules-flutter:update-memory`
- 自动维护：AI 执行新建 / 重命名 / 删除源文件、新增状态单元 / 组件 / 路由 / 接口、做出架构决策等操作时**必须顺手**更新对应索引

## 维护原则

- **索引只记「是什么、在哪里」**，不记完整 API（完整 API 让 AI 现场 Read 源文件）
- **决策只记「为什么、踩过什么坑」**，不记代码本身
- **过期立即删** —— 文件被删了对应条目也要删
