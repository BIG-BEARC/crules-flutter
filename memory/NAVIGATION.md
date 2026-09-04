# 项目代码导航

> AI 在本项目找东西的**第一站**。先看这里，定位到对应索引文件，再 Read 源码确认细节。
>
> 本文件为**模板**，需按项目实际目录结构填充。

## 想找什么 → 去哪查（模板，按项目实际改）

> 下表是索引结构示例，术语偏 Flutter / 移动端；非 Flutter 项目按自身技术栈替换（如 widget→组件、view→页面、provider→状态）。Flutter 专项清单见**项目根 `checklist.md`**（安装时随模板落位）。

### 通用基础设施

| 我想找... | 查这个索引 | 源码位置 |
|---|---|---|
| 通用组件（按钮、弹窗、列表、空状态等） | [widgets.md](indexes/widgets.md) | `<common-widget-dir>` |
| 数据模型（DTO / 实体类） | [models.md](indexes/models.md) | `<model-dir>` |
| 枚举类型 | [enumerations.md](indexes/enumerations.md) | `<enum-dir>` |
| 扩展方法 | [extensions.md](indexes/extensions.md) | `<extension-dir>` |
| 混入 / 复用基类 | [mixins.md](indexes/mixins.md) | `<mixin-dir>` |
| 全局配置 / 常量 | [config.md](indexes/config.md) | `<config-dir>` |

### 核心服务

| 我想找... | 查这个索引 | 源码位置 |
|---|---|---|
| 网络层 | [network.md](indexes/network.md) | `<network-dir>` |
| 数据层 / 仓储 | [repository.md](indexes/repository.md) | `<repository-dir>` |

### 状态管理

| 我想找... | 查这个索引 | 源码位置 |
|---|---|---|
| 状态单元（全局状态） | [providers.md](indexes/providers.md) | `<state-dir>` |
| 业务领域状态 | [providers.md](indexes/providers.md) | `<state-dir>/<domain>/` |

### 工具函数

| 我想找... | 查这个索引 | 源码位置 |
|---|---|---|
| 工具函数（日期、加密、Toast、权限等） | [utils.md](indexes/utils.md) | `<utils-dir>` |

### 业务页面

| 我想找... | 查这个索引 | 源码位置 |
|---|---|---|
| 业务页面（按模块分） | [views.md](indexes/views.md) | `<views-dir>/<模块>/` |

### 其他

| 我想找... | 查这个索引 | 源码位置 |
|---|---|---|
| 路由表 | [routes.md](indexes/routes.md) | `<routes-config-file>` |
| 国际化 Key 与资源 | [i18n.md](indexes/i18n.md) | `<i18n-resources-dir>` |
| 调试相关 | [debug.md](indexes/debug.md) | `<debug-dir>` |
| 同行 / 领域参考系（谁值得看、去哪查） | [reference-map.md](reference-map.md) | — |
| 平台坑（支持矩阵 / 坑卡检索） | [platform-pitfalls.md](platform-pitfalls.md) | — |
| 项目特有代码模式 | [../patterns.md](patterns.md) | — |
| 设计决策历史 | [../decisions/](decisions/) | — |

> `indexes/*.md` 在启用记忆库时按需创建（每个核心目录一个）；上表为占位示例，按项目实际目录填充。

## 实现新功能前的强制流程

1. **定位** —— 在上表找到对应索引文件，Read 一遍
2. **检查复用** —— 索引里如果有现成的组件 / 工具 / 抽象能用，**优先扩展或调用，不新建**
3. **遵守约定** —— 按项目编码规范实现
4. **不确定就问** —— 命名 / 位置 / 抽象边界拿不准时，反问需求方

## 索引维护规则

见 [MAINTENANCE.md](MAINTENANCE.md)
