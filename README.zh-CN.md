# Skills

[English](README.md) | 简体中文

这是一个面向 AI 编程 Agent 的可复用 Skills 仓库，提供技术绘图和博客园 Markdown 版本生成能力。

[Skill 目录](#skill-目录) · [安装](#安装) · [兼容性](#兼容性)

## Skill 目录

| Skill | 用途 | 产物 |
| --- | --- | --- |
| [技术绘图](#技术绘图) | 根据文字、代码或草图生成并检查技术图 | 图片与可编辑图源 |
| [生成博客园版本](#生成博客园版本) | 使用已安装的 `dotnet-cnblog` 转换 Markdown 文章 | 替换好图片链接的 `*-cnblog.md` |

两个 Skill 可以按需安装。识别后可直接用自然语言提出需求，也可通过 `$skill-name` 显式调用。

## 安装

如果当前 Agent 支持从 GitHub 安装 Skill，可以直接交给它下面的地址：

```text
https://github.com/eventhorizon-cli/skills/tree/main/draw-technical-diagrams
https://github.com/eventhorizon-cli/skills/tree/main/generate-cnblogs-version
```

在 Codex 中手动安装时，可以克隆仓库并复制需要的 Skill：

```bash
git clone --depth 1 https://github.com/eventhorizon-cli/skills.git
mkdir -p ~/.codex/skills

# 技术绘图
cp -R skills/draw-technical-diagrams ~/.codex/skills/

# 生成博客园版本
cp -R skills/generate-cnblogs-version ~/.codex/skills/
```

如果安装后未识别，可以新建任务或重启 Agent。其他 Agent 的安装目录可能不同。

## 技术绘图

[`draw-technical-diagrams`](draw-technical-diagrams/SKILL.md)

根据文字、代码或已有草图，绘制流程图、系统架构图、组件图和数据流图。

- 布局适合时使用 Mermaid，需要精确排布或成图效果不好时直接绘制 SVG。
- 有 Node.js 时允许轻量尝试一次 Mermaid；运行环境、依赖下载或沙箱受阻时切换 SVG。
- 保留可编辑图源。使用 SVG 时，如果 Mermaid 能准确表达逻辑，也保留 `.mmd` 供 Agent 理解和修改；不要求渲染这份逻辑记录。
- 检查裁切、文字遮挡、连线歧义、箭头方向、长宽比和最终成图。

**调用示例**

```text
使用 $draw-technical-diagrams 绘制订单提交流程图：

提交订单 -> 校验 -> 写入数据库 -> 返回成功。
校验失败时返回错误。

输出白底 PNG 并保留可编辑图源；逻辑可用 Mermaid 表达时，也保留 .mmd。
```

**环境要求**

| 绘制方式 | 依赖 |
| --- | --- |
| Mermaid | Bash、Node.js/`npx`、无头 Chrome/Chromium；首次运行可能下载固定版本的 Mermaid CLI |
| 直接绘制 SVG | 不依赖 Mermaid；检查成图需要 SVG 查看器或渲染器，导出 PNG 需要可用的渲染器 |

完整规则见 [Skill 说明](draw-technical-diagrams/SKILL.md)。Mermaid 渲染脚本为 [`render-mermaid.sh`](draw-technical-diagrams/scripts/render-mermaid.sh)。

## 生成博客园版本

[`generate-cnblogs-version`](generate-cnblogs-version/SKILL.md) · 显示名称：**生成博客园版本**

调用已安装的 .NET 程序 [dotnet-cnblog](https://github.com/stulzq/dotnet-cnblogs-tool)，生成可粘贴到博客园 Markdown 编辑器的文章版本。

- 先直接执行工具，遇到报错或输出不完整时再排查。
- 通过已配置的博客园账号上传文章中的本地图片，并替换为远程链接。
- 保留原稿，生成 `article-cnblog.md`；不会发布或更新博客文章。

**调用示例**

```text
使用 $generate-cnblogs-version 为 docs/article.md 生成博客园版本。
```

文章已明确时，也可以直接说“生成博客园版本”或“转成博客园格式”。

**工具与配置**

复用现有安装和账号配置，执行命令为：

```bash
dotnet-cnblog proc -f "/absolute/path/article.md"
```

如果运行时发现工具未安装，Agent 会提供[上游项目链接](https://github.com/stulzq/dotnet-cnblogs-tool)并提示：

```bash
dotnet tool install --global dotnet-cnblog
```

需要配置账号时，在本机按工具提示操作，MetaWeblog Token 来自[博客园设置](https://i.cnblogs.com/settings)。转换失败的处理方式见 [Skill 说明](generate-cnblogs-version/SKILL.md)。

## 兼容性

目前仅在 Codex 和 macOS 环境中使用验证。Windows、Linux 以及其他 Agent 尚未验证，可能需要调整安装目录、运行时或脚本。Mermaid、Chrome 和 `npx` 等依赖只属于技术绘图 Skill 的 Mermaid 路径，不是两个 Skill 的共同要求。

## 许可证

本仓库使用 [MIT License](LICENSE)。
