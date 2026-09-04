# 主题 / 颜色 / 字体 / Material 3 / A11Y

> 触发场景：配置主题、暗黑模式、颜色令牌、字体、无障碍时 Read 本文件。来源：flutter-rules skill 主题与视觉各节（B1 瘦身浓缩——删视觉铺陈，保 API 全例）。

## 集中化主题

- `MaterialApp` 同时给 `theme` / `darkTheme`，`themeMode` 受控切换（`ThemeMode.light|dark|system`）
- 组件级样式在 `ThemeData` 里用 `appBarTheme` / `elevatedButtonTheme` / `cardTheme` 等统一归口——不散落在组件内
- 颜色 / 字号 / 间距**不硬编码**：归口主题或常量类（checklist「组件/视图」类硬门）

## ColorScheme（Material 3）

```dart
final ThemeData lightTheme = ThemeData(
  colorScheme: ColorScheme.fromSeed(
    seedColor: Colors.deepPurple,
    brightness: Brightness.light,
  ),
);
// darkTheme 同 seed + Brightness.dark——双端一致的和声色板
```

## ThemeExtension（自定义设计令牌——非标准 ThemeData 的槽位）

`copyWith` 与 `lerp` 都是必需（lerp 支撑暗黑过渡动画）：

```dart
@immutable
class MyColors extends ThemeExtension<MyColors> {
  const MyColors({required this.success, required this.danger});
  final Color? success;
  final Color? danger;

  @override
  ThemeExtension<MyColors> copyWith({Color? success, Color? danger}) =>
      MyColors(success: success ?? this.success, danger: danger ?? this.danger);

  @override
  ThemeExtension<MyColors> lerp(ThemeExtension<MyColors>? other, double t) {
    if (other is! MyColors) return this;
    return MyColors(
      success: Color.lerp(success, other.success, t),
      danger: Color.lerp(danger, other.danger, t),
    );
  }
}

// 注册：ThemeData(extensions: const <ThemeExtension<dynamic>>[MyColors(...)])
// 取用：Theme.of(context).extension<MyColors>()!.success
```

## WidgetStateProperty（状态相关的组件样式）

```dart
final ButtonStyle myButtonStyle = ButtonStyle(
  backgroundColor: WidgetStateProperty.resolveWith<Color>(
    (Set<WidgetState> states) =>
        states.contains(WidgetState.pressed) ? Colors.green : Colors.red,
  ),
);
// 各态同值用 WidgetStateProperty.all(...)
```

## 字体

- 全 App 限 1–2 个字族；自定义字体走 `google_fonts` 包 + `TextTheme` 统一挂载（不逐组件指定）
- 字号阶梯落在 `TextTheme`（displayLarge…labelSmall），组件从 `Theme.of(context).textTheme` 取

## 资源与网络图

- assets 在 `pubspec.yaml` 声明目录；跨 package 加载子工程资源须带 `package` 参数（见项目模板 §八）
- `Image.network` 必配 `loadingBuilder` + `errorBuilder`；缓存图用 `cached_network_image`

## 无障碍（A11Y）

- 文本对比度：正文 ≥ **4.5:1**，大字（18pt / 14pt bold）≥ **3:1**（WCAG）
- 系统字体放大后 UI 仍可用（禁固定高度容器锁死文字）
- 交互元素配 `Semantics` 语义标签；发布前 TalkBack / VoiceOver 过关键路径
