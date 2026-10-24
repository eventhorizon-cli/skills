# 技术绘图

[English](draw-technical-diagrams.md) · [仓库 README](../README.zh-CN.md) · [Skill 说明](../skills/draw-technical-diagrams/SKILL.md)

使用 `draw-technical-diagrams` 根据文字、代码或已有草图创建和修改流程图、系统架构图、组件图和数据流图。

## 需要提供的信息

- 如果已有图片、截图或草图，请说明它是事实来源。结果应忠实重绘可观察到的节点、标签、分组、连线和大致布局。
- 如果是新图，请说明组件、归属边界、方向关系、分支条件、时序或等待状态，以及必须保持区分的事件。
- 说明所需输出格式、目标文章或文档宽度，以及是否需要交付可编辑图源。

Skill 会区分忠实重绘和语义优先创建。执行规则和布局要求见 [Skill 说明](../skills/draw-technical-diagrams/SKILL.md)。

## 产物与依赖

可编辑图源使用 Mermaid 时为 `.mmd`，直接绘制时为 `.svg`。Mermaid 可以输出 PNG、SVG 或 PDF。如果直接绘制的 SVG 关系可以由 Mermaid 准确表达，也会保留配套的 `.mmd` 逻辑模型。

| 方式 | 依赖 |
| --- | --- |
| Mermaid | Bash、Node.js/`npx` 和无头 Chrome/Chromium；首次渲染可能下载固定版本的 Mermaid CLI |
| 直接绘制 SVG | 不依赖 Mermaid；视觉检查和导出 PNG 需要 SVG 查看器或渲染器 |

Mermaid 渲染脚本为 [`render-mermaid.sh`](../skills/draw-technical-diagrams/scripts/render-mermaid.sh)。Mermaid 无法在当前环境运行或成图效果不合适时，可以直接使用 SVG，并说明无法预览或导出的部分。

## 调用示例

新建流程图：

```text
使用 $draw-technical-diagrams 绘制订单提交流程图：

提交订单 -> 校验 -> 写入数据库 -> 返回成功。
校验失败时返回错误。

输出白底 PNG 并保留可编辑图源。
```

绘制架构图：

```text
请读取当前项目并绘制系统架构图。
按照真实归属划分 API、应用服务、消息中间件、Consumer 和数据库，
清楚表示请求路径和注册路径。
请保留可编辑图源，并输出适合文章使用的白底 PNG。
```

## 检查与失败处理

视觉检查前运行 Skill 自带的结构检查：

```bash
python3 <skill-dir>/scripts/validate-svg.py diagram.svg --strict
python3 <skill-dir>/scripts/check-markdown-diagrams.py README.md
```

这些检查会发现结构不正确的 SVG，以及 Markdown 或 HTML 中损坏的本地图片链接。检查不能代替打开最终图片；还要确认没有裁切、文字重叠、箭头端点错误、分支难以区分和长宽比异常。如果没有查看器或栅格化工具，应明确说明预览或导出未经验证。

Mermaid 的依赖、浏览器或下载受阻时，直接切换到 SVG，不要把环境配置作为完成绘图的前提。Mermaid 成图效果不好时，直接调整 SVG 布局，并保留用户要求的逻辑图源。
