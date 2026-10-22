# 布局 / Overflow / 叠层 / 浮层

> 触发场景：布局选型、修 overflow / unbounded、叠层与浮层、屏幕适配选型、字体策略实现时 Read 本文件。来源：flutter-rules skill 布局节（B1 瘦身浓缩）；2026-10-22 并入宪法模板 §七 屏幕适配 / 字体策略（1.3.0 分层批）。

## Row / Column 主轴分配

- **`Expanded`**：占满剩余空间（刚性）
- **`Flexible`**：可收缩不强制占满（柔性）。与 Expanded 同 Row/Column 混用是**合法常见写法**（如一列占满 + 一列按内容收缩），但须明确各子项的弹性意图，避免无意识的约束竞争
- **Row 内 `Text` 省略号须先包 `Flexible`/`Expanded`**：非弹性约束下 Text 取固有宽参与 Row 布局，裸 Text 加 `overflow: ellipsis` 不生效（实证：订单折算复盘吸收 C1，见 plugin 仓根 `CHANGELOG.md` 0.6.0 条）
- **`Wrap`**：子项会溢出时换行（标签流 / 动态长度 chips）

## 滚动与溢出

| 内容形态 | 用什么 |
|---|---|
| 固定内容超屏（表单/说明页） | `SingleChildScrollView` |
| 长列表 / 网格 | `ListView.builder` / `GridView.builder`（懒加载，禁全量 children） |
| 单子项缩放适配 | `FittedBox` |
| 按可用空间分支的响应式 | `LayoutBuilder`（配合 `MediaQuery`） |

### 列表项 key——状态错乱（库存角标 / 选中态串行）防与治

- **症状形态**：列表刷新 / 重排后，某行显示**别的行**的库存、售罄态或选中态——element 复用撞上「同类型项 + 状态随位置残留」
- **防**：列表项 `key` 绑**业务 id**（`ValueKey(spuId)` / `ValueKey(orderId)`），不绑数组下标（下标在增删 / 重排后指错对象，等于没绑）
- **治（配置驱动的子组件不重建）**：传给子组件的**配置值变了但 widget 类型没变**时（下拉选项、轮播间隔、角标数据），Flutter 判定可复用而跳过重建——给该子组件挂 `ValueKey(配置值)` 强制重建（实证：saas-cashier `31302e77d` 下拉选中后展示不刷新、`0111c1d7d` 轮播配置变更不生效、点单页商品卡库存角标错乱同型）
- **治（StatefulWidget 常驻不卸载时切换数据源）**：改共享 StatefulWidget 的展示来源（如日期弹窗切换左右侧日期）时，实例被复用则 `initState` / 字段只在**挂载时读一次**，切换侧后仍显示旧值——挂 `ValueKey(切换侧标识)` 强制重挂（实证：saas-cashier `29f490bae` 日期滚轮，widget 测试拖滚轮才暴露）；此类改动检查「实例是否复用」并用 widget 测试锁死

- **无断词点长串不自动换行**：UAX#14 断词规则下纯数字/字母串（订单号 / URL / UUID）整串无断词点，`softWrap` 照样横向溢出——解法逐字符 `Wrap` 或手动零宽断点（实证：同上复盘 C2）

## Stack 叠层

- **`Positioned`**：锚定边距精确定位
- **`Align`**：对齐式定位（`Alignment.center` 等）

## OverlayPortal（自定义下拉 / 工具提示类浮层）

浮层 UI「盖在一切之上」且自动管理 `OverlayEntry` 生命周期：

```dart
class _MyDropdownState extends State<MyDropdown> {
  final _controller = OverlayPortalController();

  @override
  Widget build(BuildContext context) => OverlayPortal(
        controller: _controller,
        overlayChildBuilder: (BuildContext context) => const Positioned(
          top: 50,
          left: 10,
          child: Card(child: Padding(
            padding: EdgeInsets.all(8.0),
            child: Text('overlay'),
          )),
        ),
        child: ElevatedButton(
          onPressed: _controller.toggle,
          child: const Text('Toggle'),
        ),
      );
}
```

## 通用纪律

- 私有 `Widget` 子类优于「返回 Widget 的私有方法」（build 拆分同理——const 化与重建粒度都受益）
- `build()` 内禁重活（请求 / 复杂计算）——自反馈死循环经典来源（见插件 cache `checklist.md` 反模式节）

## 屏幕适配方案（三选一——选定结果记 PROJECT.md §七；1.3.0 自宪法模板 §七 下沉）

**A1 弹性优先 + 断点（默认推荐·多端 / 长期项目）**
弹性组件（Expanded/Flexible/Wrap）优先 → LayoutBuilder 断点（Compact<600 /
Medium<840/Expanded≥840 三档语义化）→ 字号/间距走 ThemeExtension 离散档位。
禁连续缩放系数（与系统字体缩放冲突、多端破版）。桌面端可按需扩 large/extra-large 档。

**A2 设计稿缩放（按稿像素还原·单端项目）**
flutter_screenutil（.w/.h 按稿缩放）。注：5.9.3 后 ~28 个月无稳定版（维护缓慢）；
.sp 与系统字体缩放需显式协调；平板/桌面不适用。仅限存量沿用与像素还原型单端新项目。

**A3 自定义**（在此描述）

## 字体策略（公共·任一适配档皆必选；1.3.0 自宪法模板 §七 下沉）

- **关键字体打包进 app**，不依赖系统回退：Android 机型 OEM ROM 可能裁剪 Roboto/
  中文字重（字重只剩两档）；Windows 可能缺可用中文字体——按目标平台打包（如 Roboto
  全字重 + 桌面中文字体），pubspec 显式声明 family 与字重映射（离线 / 内网设备的
  google_fonts 禁用口径与坑卡见 [theming.md](theming.md)「自定义字体分场景」）
- **统一注入点**：平台条件 fontFamily 走统一 TextStyle 工厂/getter；**禁内联
  TextStyle**（内联即绕过注入，桌面端/OEM 机型即现字体缺陷）
- fontFamilyFallback 显式声明兜底链
- 打印等设备无法渲染的字形（维语/阿拉伯语等）：文字渲染为图的兜底链路
