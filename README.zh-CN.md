# Skills

[English](README.md) | 简体中文

这是一个面向 AI 编程 Agent 的可复用 Skills 仓库。目前包含 `draw-technical-diagrams`，用于创建和修改技术流程图、系统架构图、组件图和数据流图。

> **兼容性说明：** 这个 Skill 目前只在 macOS 上通过 Codex 完成了实际测试，因此当前只保证在 macOS 上可用。Windows 和 Linux 尚未经过验证，可能会因为依赖、路径或脚本差异而无法运行。其他 Agent 理论上也可以使用，但安装目录和调用方式可能不同。

## 当前包含的 Skills

| Skill | 说明 |
| --- | --- |
| [`draw-technical-diagrams`](draw-technical-diagrams) | 根据文字、代码或已有草图生成可读的技术图，并渲染和检查最终图片。 |

## 它能做什么

`draw-technical-diagrams` 为 Agent 提供了一套可重复执行的技术绘图流程：

- 绘制流程图、系统架构图、组件图和数据流图。
- 保留可编辑源文件：使用 Mermaid 时保留 `.mmd`，直接绘制 SVG 时保留 `.svg`。
- 区分忠实重绘和语义优先的新图，避免在重绘已有图时悄悄改变拓扑关系。
- 使用 Mermaid 时，通过固定版本的 Mermaid CLI 输出白底 PNG、SVG 或 PDF。
- 在视觉检查前运行不依赖第三方包的 SVG 结构校验和 Markdown 图片链接校验。
- 检查裁切、文字遮挡、连线歧义、箭头方向和异常长宽比。
- 判断 Mermaid 不适合时直接绘制 SVG；Mermaid 成图效果不好时也立即切换 SVG。

## 环境要求

当前经过验证的运行环境为 macOS 和 Codex（或其他能够加载这种 Skill 格式的 Agent）。Mermaid 渲染脚本还需要：

- Bash。
- Node.js 和 `npx`。
- 可用的无头 Chrome 或 Chromium 环境。在已经验证的 macOS 环境中，脚本会优先使用 `/Applications` 中的 Google Chrome，否则交给 Mermaid CLI/Puppeteer 按默认方式处理。
- 第一次渲染时能够联网下载 Mermaid CLI。

直接编写 SVG 不依赖 Mermaid CLI 及其运行环境。如果需要从 SVG 输出 PNG，则需要可用的 SVG 渲染器。

## 安装

如果当前 Agent 支持从 GitHub 安装 Skill，可以直接把 Skill 地址交给它：

```text
请安装并使用下面的 Skill：
https://github.com/eventhorizon-cli/skills/tree/main/draw-technical-diagrams
```

在 Codex 中手动安装时，可以克隆仓库，再将 Skill 复制到 Codex 的 Skills 目录：

```bash
git clone --depth 1 https://github.com/eventhorizon-cli/skills.git
mkdir -p ~/.codex/skills
cp -R skills/draw-technical-diagrams ~/.codex/skills/
```

如果当前任务没有识别到刚安装的 Skill，可以重启 Codex，或者重新打开一个任务。使用其他 Agent 时，需要将目录复制到对应 Agent 支持的 Skills 位置。

## 使用方式

Skill 安装并被识别后，直接要求 Agent 绘制或修改技术图，通常就会自动触发。在 Codex 中，也可以使用 `$draw-technical-diagrams` 显式调用。

简单的流程图只需要提供主要步骤：

```text
请画一张订单提交流程图：

用户提交订单 -> 校验订单 -> 写入数据库 -> 返回成功。
校验失败时直接返回错误。

请保留可编辑源文件（Mermaid 为 .mmd，直接绘制 SVG 为 .svg），并输出白底高分辨率 PNG。
```

面对更复杂的系统，可以补充组件、系统边界、连接关系和阅读方向：

```text
请读取当前项目并绘制系统架构图。

按照真实归属划分 API、应用服务、消息中间件、Consumer 和数据库。
数据流使用实线，注册或发现关系使用虚线。
请保留可编辑源文件（Mermaid 为 .mmd，直接绘制 SVG 为 .svg），并输出适合技术文章的白底高分辨率 PNG。
```

复杂图不一定一次就能达到预期。如果结果不合适，可以继续与 Agent 沟通，并指出具体问题，例如箭头连接到了错误的节点、图片太宽，或者某些细节应该拆成另一张图。由于图源会被保留，Agent 可以继续修改并重新渲染，不需要从头开始。

## 仓库结构

```text
draw-technical-diagrams/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
│   ├── mermaid.config.json
│   └── puppeteer.macos.json
├── references/
│   └── layout-patterns.md
└── scripts/
    ├── check-markdown-diagrams.py
    ├── validate-svg.py
    └── render-mermaid.sh
```

## 实现原理

Skill 会引导 Agent 按照下面的流程处理：

```text
原始材料
  -> 识别组件和关系
  -> 判断 Mermaid 是否适合当前布局
  -> 生成 Mermaid 图源或直接编写 SVG
  -> 渲染所需图片格式
  -> 检查最终图片
  -> Mermaid 成图效果不好时直接切换 SVG
  -> 验证最终成图
```

如果判断 Mermaid 不适合，Agent 会直接绘制 SVG，无需先试画 Mermaid。如果 Mermaid 成图效果不好，也会立即改用显式 SVG 布局，并保留已有的 `.mmd` 作为逻辑关系记录。只要直接绘制的 SVG 关系可以用 Mermaid 准确表达，Agent 也会保留配套的 `.mmd`，方便复核拓扑关系。最终可以直接交付 SVG，或按需输出白底 PNG。

Mermaid 渲染脚本的调用方式如下：

```bash
<skill-dir>/scripts/render-mermaid.sh input.mmd output.png
```

发布图之前，可以先检查正在编辑的 Markdown 中的本地图片引用。这个脚本
会按照每个 Markdown 文件所在目录解析相对路径，支持 `![alt](image.svg)`
和 HTML 的 `<img src="image.svg">` 两种写法，并跳过远程 URL、data URL
以及只包含锚点的链接：

```bash
python3 <skill-dir>/scripts/check-markdown-diagrams.py README.md docs/design
```

脚本会输出每个本地引用及其所在行。所有本地图片都存在时退出码为 `0`；
发现一个或多个缺失图片时退出码为 `1`；输入文件不存在或无法读取时退出码
为 `2`。

对于直接编写的 SVG，可以在视觉检查前运行不依赖第三方包的结构检查：

```bash
python3 <skill-dir>/scripts/validate-svg.py diagram.svg --strict
```

这个校验器会检查 XML、画布元数据、显式白色背景覆盖、文本定位、marker
引用、重复 ID 和重复路径几何。警告会单独输出，加入 `--strict` 后警告也会
使校验失败。

完整的 Agent 工作流和图片检查规则可以查看 [`draw-technical-diagrams/SKILL.md`](draw-technical-diagrams/SKILL.md)。

## 许可证

本仓库使用 [MIT License](LICENSE)。
