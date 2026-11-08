# 技术动画

[English](render-technical-animations.md) · [仓库说明](../README.zh-CN.md) · [Skill 说明](../skills/render-technical-animations/SKILL.md)

`render-technical-animations` 用于解释架构、请求流转、并发和状态变化，默认生成适合放进 README 和技术文档的独立 SVG 动画。静态图已经能讲清楚时，使用 `draw-technical-diagrams`。

## 需要提供什么

- 相关代码或设计，包括请求归属、执行限制、完成条件和顺序保证。
- 要演示的事件顺序，以及图中不能暗示的行为。
- 输出位置、语言、展示尺寸和合适的播放时长。
- 是否需要交互控件，或明确要求导出 GIF。

Agent 应先确定事件时间线，再开始绘图。每次状态变化时，请求、执行名额、计数和说明文字都应一致。示意性的播放时间不能当作性能测量结果。

## 产物与依赖

默认产物是原生 SVG 动画，同一个文件既是可编辑源码，也是可嵌入文档的图片。动画使用矢量元素和 CSS 或 SMIL，不依赖 JavaScript、外部资源或内嵌位图帧。应提供无障碍说明，以及减少动态效果时显示的静态状态。详见 [SVG 参考](../skills/render-technical-animations/references/svg-animation.md)和[起始 SVG](../skills/render-technical-animations/assets/svg-animation/scene.svg)。

需要暂停、拖动进度、调速或修改参数时，可以额外提供 HTML。HTML 不是生成 SVG 必须经过的中间步骤。Skill 附带 [HTML 模板](../skills/render-technical-animations/assets/technical-animation/index.html)和[播放器 API](../skills/render-technical-animations/references/player-api.md)。

只有明确要求时才导出 GIF。附带的 Python 渲染器使用 Playwright 和 Pillow，可以渲染支持定位时间的 SVG 或 HTML 场景。环境安装、配置和命令见 [GIF 导出参考](../skills/render-technical-animations/references/gif-export.md)。渲染依赖与缓存应放在目标项目之外。

不会因为输出 SVG 就自动附带 PNG 或 GIF；用户或仓库明确要求其他格式时，再按要求提供。

## 示例

```text
使用 $render-technical-animations 解释当前仓库的请求合批流程。
展示两个执行名额，单批上限为四个请求；有空闲名额就立即取走队列中的请求，
不能让人误以为要等待凑满一批。分别输出中英文 SVG 到 docs/assets，播放速度要便于看清。
在两份 README 的图片下方，按事件顺序解释每一步发生了什么。
```

使用这个示例前，先确认实现符合这些合批规则。中英文版本应保持图形布局和时间线一致，并翻译全部可见文字。

## 检查与失败处理

先检查 XML、标识符、时间范围和本地引用，再查看关键状态变化前后及循环衔接处的实际画面。按 README 的展示尺寸检查文字、裁切、遮挡、计数和请求归属。既要直接打开 SVG，也要通过图片元素检查是否实际播放。XML 校验和静态截图都不能证明动画行为正确。

检查减少动态效果时的静态状态，并说明未验证的行为。浏览器模拟的减少动态效果设置，可能不会传递到作为图片嵌入的 SVG。浏览器里能播放，也不能直接证明 GitHub、NuGet 或其他发布平台支持动画；应说明实际测试过的环境。无法渲染或检查画面时，要明确指出尚未完成的检查。
