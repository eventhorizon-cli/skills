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
- 保留 Mermaid `.mmd` 源文件，方便后续阅读和修改。
- 使用固定版本的 Mermaid CLI 输出白底 PNG、SVG 或 PDF。
- 检查裁切、文字遮挡、连线歧义、箭头方向和异常长宽比。
- Mermaid 经过针对性调整后仍然无法稳定排线时，改用显式 SVG 固定布局。

## 环境要求

当前经过验证的运行环境需要：

- macOS。
- Codex，或其他能够加载这种 Skill 格式的 Agent。
- Bash。
- Node.js 和 `npx`。
- 可用的无头 Chrome 或 Chromium 环境。在已经验证的 macOS 环境中，脚本会优先使用 `/Applications` 中的 Google Chrome，否则交给 Mermaid CLI/Puppeteer 按默认方式处理。
- 第一次渲染时能够联网下载 Mermaid CLI。

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

请保留 .mmd，并输出白底高分辨率 PNG。
```

面对更复杂的系统，可以补充组件、系统边界、连接关系和阅读方向：

```text
请读取当前项目并绘制系统架构图。

按照真实归属划分 API、应用服务、消息中间件、Consumer 和数据库。
数据流使用实线，注册或发现关系使用虚线。
请保留 .mmd，并输出适合技术文章的白底高分辨率 PNG。
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
    └── render-mermaid.sh
```

## 实现原理

Skill 会引导 Agent 按照下面的流程处理：

```text
原始材料
  -> 识别组件和关系
  -> 生成 Mermaid 图源
  -> 渲染 PNG/SVG/PDF
  -> 检查最终图片
  -> 必要时修改并重新渲染
```

如果 Mermaid 经过针对性调整后仍然无法得到清晰、稳定的布局，Agent 会保留 `.mmd` 作为逻辑关系记录，创建显式 SVG 作为布局源，再输出最终的白底 PNG。

渲染脚本的调用方式如下：

```bash
<skill-dir>/scripts/render-mermaid.sh input.mmd output.png
```

完整的 Agent 工作流和图片检查规则可以查看 [`draw-technical-diagrams/SKILL.md`](draw-technical-diagrams/SKILL.md)。

## 许可证

本仓库使用 [MIT License](LICENSE)。
