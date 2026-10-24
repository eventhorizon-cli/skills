# Skills

[English](README.md) | 简体中文

这是一个面向 AI 编程 Agent 的可复用 Skills 仓库，提供技术绘图和博客园 Markdown 版本生成能力。

[Skill 目录](#skill-目录) · [安装](#安装) · [文档](#文档) · [兼容性](#兼容性)

## Skill 目录

| Skill | 用途 | 文档 |
| --- | --- | --- |
| `draw-technical-diagrams` | 绘制或修改流程图、架构图和数据流图 | [用户指南](docs/draw-technical-diagrams.zh-CN.md) · [Skill 说明](skills/draw-technical-diagrams/SKILL.md) |
| `generate-cnblogs-version` | 使用 `dotnet-cnblog` 转换 Markdown 文章 | [用户指南](docs/generate-cnblogs-version.zh-CN.md) · [Skill 说明](skills/generate-cnblogs-version/SKILL.md) |

两个 Skill 可以按需安装。识别后可直接用自然语言提出需求，也可通过 `$skill-name` 显式调用。

## 安装

如果当前 Agent 支持从 GitHub 安装 Skill，可以交给它下面的地址：

```text
https://github.com/eventhorizon-cli/skills/tree/main/skills/draw-technical-diagrams
https://github.com/eventhorizon-cli/skills/tree/main/skills/generate-cnblogs-version
```

在 Codex 中手动安装：

```bash
git clone --depth 1 https://github.com/eventhorizon-cli/skills.git agent-skills
mkdir -p ~/.codex/skills
cp -R agent-skills/skills/draw-technical-diagrams ~/.codex/skills/
cp -R agent-skills/skills/generate-cnblogs-version ~/.codex/skills/
```

如果安装后未识别，可以新建任务或重启 Agent。其他 Agent 的安装目录可能不同。

## 使用示例

```text
使用 $draw-technical-diagrams 绘制订单流程并输出白底 PNG。
使用 $generate-cnblogs-version 将 docs/article.md 转换为博客园版本。
```

## 文档

[技术绘图指南](docs/draw-technical-diagrams.zh-CN.md)介绍需要提供的信息、产物、依赖、示例和失败处理。[博客园指南](docs/generate-cnblogs-version.zh-CN.md)介绍转换、图片上传、配置，以及上传图片后生成文件而不会发布文章。[维护指南](docs/maintaining.zh-CN.md)介绍同步本地 Skill 和运行检查。

仓库将 Skill 实现放在 `skills/`，用户指南放在 `docs/`，验证入口放在 `scripts/`。

## 兼容性

目前仅在 Codex 和 macOS 环境中使用验证。Windows、Linux 以及其他 Agent 尚未验证。各 Skill 的依赖列在对应用户指南中。

## 许可证

本仓库使用 [MIT License](LICENSE)。
