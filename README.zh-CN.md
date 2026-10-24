# Skills

[English](README.md) | 简体中文

这是一个面向 AI 编程 Agent 的可复用 Skills 仓库，提供技术绘图和博客园 Markdown 版本生成能力。

[Skill 目录](#skill-目录) · [安装](#安装) · [仓库结构](#仓库结构) · [兼容性](#兼容性)

## Skill 目录

| Skill | 用途 | 产物 |
| --- | --- | --- |
| [技术绘图](#技术绘图) | 根据文字、代码或草图生成并检查技术图 | 图片与可编辑图源 |
| [生成博客园版本](#生成博客园版本) | 使用已安装的 `dotnet-cnblog` 转换 Markdown 文章 | 替换好图片链接的 `*-cnblog.md` |

两个 Skill 可以按需安装。识别后可直接用自然语言提出需求，也可通过 `$skill-name` 显式调用。

## 安装

如果当前 Agent 支持从 GitHub 安装 Skill，可以直接交给它下面的地址：

```text
https://github.com/eventhorizon-cli/skills/tree/main/skills/draw-technical-diagrams
https://github.com/eventhorizon-cli/skills/tree/main/skills/generate-cnblogs-version
```

在 Codex 中手动安装时，可以克隆仓库并复制需要的 Skill：

```bash
git clone --depth 1 https://github.com/eventhorizon-cli/skills.git agent-skills
mkdir -p ~/.codex/skills

# 技术绘图
cp -R agent-skills/skills/draw-technical-diagrams ~/.codex/skills/

# 生成博客园版本
cp -R agent-skills/skills/generate-cnblogs-version ~/.codex/skills/
```

如果安装后未识别，可以新建任务或重启 Agent。其他 Agent 的安装目录可能不同。

## 技术绘图

[`draw-technical-diagrams`](skills/draw-technical-diagrams/SKILL.md)

根据文字、代码或已有草图，绘制流程图、系统架构图、组件图和数据流图。

修改图之前，先选择工作模式：

- **忠实重绘**：已有图片、截图或手绘草图是事实来源时使用。保留可观察到的节点、连线、标签、分组和大致布局，不要悄悄改写拓扑关系。
- **语义优先创建**：没有需要保留的已有图片时使用。绘图前先提取节点名称、归属、方向关系、分支条件、时序状态和其他语义要求。

保持工作模式明确。已有图存在歧义时，保留可观察到的结构并说明不确定之处，不要自行补出新的关系。

标准流程和时序适合自动布局时使用 Mermaid。需要精确排布、固定对齐、密集的跨分组连线或可控路由时，直接编写 SVG。Mermaid 运行环境、浏览器或依赖下载受阻，或者成图效果不好时，直接切换到 SVG。保留可编辑图源：Mermaid 使用 `.mmd`，直接绘制使用 `.svg`。如果 SVG 的关系可以用 Mermaid 准确表达，也保留 `.mmd` 逻辑模型，即使 Mermaid 无法运行。

- 架构图和数据流图默认使用从左到右的布局；简短且天然适合纵向阅读的流程可以使用从上到下的布局。
- 分组应对应真实的归属或部署边界；主要请求或数据流使用实线，发现、注册、心跳等控制面流量使用虚线。
- 交付前检查最终图片是否裁切、文字拥挤、连线歧义、箭头方向错误或长宽比不合适。

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

Mermaid 渲染脚本为 [`render-mermaid.sh`](skills/draw-technical-diagrams/scripts/render-mermaid.sh)，支持 PNG、SVG 和 PDF，并固定使用 Mermaid CLI `11.12.0`。

**结构检查**

打开渲染图片前，先运行 Skill 自带的检查脚本：

```bash
python3 <skill-dir>/scripts/validate-svg.py diagram.svg --strict
python3 <skill-dir>/scripts/check-markdown-diagrams.py README.md
```

`validate-svg.py` 会检查 XML、画布元数据、显式白色背景、文本位置、marker 引用、重复 ID 和重复路径几何。`check-markdown-diagrams.py` 会检查 Markdown 和 HTML 中的本地图片链接，按照 Markdown 文件所在目录解析相对路径，并跳过远程 URL、data URL 和只包含锚点的 URL。这些检查用于结构校验，不能代替最终图片的视觉检查。

完整规则见 [Skill 说明](skills/draw-technical-diagrams/SKILL.md)。

**处理流程**

```text
原始材料
  -> 识别组件和关系
  -> 选择忠实重绘或语义优先创建
  -> 判断 Mermaid 是否适合当前布局
  -> 生成 Mermaid 图源或直接编写 SVG
  -> 渲染所需图片格式
  -> 检查并验证最终成图
```

## 生成博客园版本

[`generate-cnblogs-version`](skills/generate-cnblogs-version/SKILL.md) · 显示名称：**生成博客园版本**

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

需要配置账号时，在本机按工具提示操作，MetaWeblog Token 来自[博客园设置](https://i.cnblogs.com/settings)。转换失败的处理方式见 [Skill 说明](skills/generate-cnblogs-version/SKILL.md)。

## 仓库结构

```text
.
├── README.md
├── README.zh-CN.md
├── LICENSE
└── skills/
    ├── draw-technical-diagrams/
    └── generate-cnblogs-version/
```

## 兼容性

目前仅在 Codex 和 macOS 环境中使用验证。Windows、Linux 以及其他 Agent 尚未验证。各 Skill 的依赖分别列在对应章节中，安装其中一个 Skill 不需要安装另一个 Skill 的工具。

## 许可证

本仓库使用 [MIT License](LICENSE)。
