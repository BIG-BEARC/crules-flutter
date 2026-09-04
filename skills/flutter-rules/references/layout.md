# 布局 / Overflow / 叠层 / 浮层

> 触发场景：布局选型、修 overflow / unbounded、叠层与浮层实现时 Read 本文件。来源：flutter-rules skill 布局节（B1 瘦身浓缩）。

## Row / Column 主轴分配

- **`Expanded`**：占满剩余空间（刚性）
- **`Flexible`**：可收缩不强制占满（柔性）——同一 Row/Column **不要混用** Expanded 与 Flexible
- **`Wrap`**：子项会溢出时换行（标签流 / 动态长度 chips）

## 滚动与溢出

| 内容形态 | 用什么 |
|---|---|
| 固定内容超屏（表单/说明页） | `SingleChildScrollView` |
| 长列表 / 网格 | `ListView.builder` / `GridView.builder`（懒加载，禁全量 children） |
| 单子项缩放适配 | `FittedBox` |
| 按可用空间分支的响应式 | `LayoutBuilder`（配合 `MediaQuery`） |

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
