# 布局 / Overflow / 叠层 / 浮层

> 触发场景：布局选型、修 overflow / unbounded、叠层与浮层实现时 Read 本文件。来源：flutter-rules skill 布局节（B1 瘦身浓缩）。

## Row / Column 主轴分配

- **`Expanded`**：占满剩余空间（刚性）
- **`Flexible`**：可收缩不强制占满（柔性）。与 Expanded 同 Row/Column 混用是**合法常见写法**（如一列占满 + 一列按内容收缩），但须明确各子项的弹性意图，避免无意识的约束竞争
- **Row 内 `Text` 省略号须先包 `Flexible`/`Expanded`**：非弹性约束下 Text 取固有宽参与 Row 布局，裸 Text 加 `overflow: ellipsis` 不生效（实证：[订单折算复盘吸收方案 C1](../../../../docs/吸收方案-2026-09-05-订单折算复盘.md)）
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
- `build()` 内禁重活（请求 / 复杂计算）——自反馈死循环经典来源（见 checklist 反模式）
