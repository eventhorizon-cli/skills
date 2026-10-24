# .NET GitHub 工作流

[English](create-dotnet-github-workflows.md) · [仓库 README](../README.zh-CN.md) · [Skill 说明](../skills/create-dotnet-github-workflows/SKILL.md)

使用 `create-dotnet-github-workflows` 创建、检查或更新 .NET/C# 仓库的 GitHub Actions CI 和 NuGet 发布工作流，支持多目标框架和包的独立版本管理。

## 需要提供的信息

- 仓库、适用的 `AGENTS.md`、已有工作流，以及构建或发布文档。
- 解决方案和项目、`global.json`、共享构建与包属性、锁文件和 NuGet 配置。
- CI 目标分支、必需检查，以及已有的包版本、标签、签名或仓库约定。

Skill 会先检查目标框架、SDK、测试运行时、VSTest 或 Microsoft.Testing.Platform 选择、可打包项目和项目引用，再确定执行命令。配置沿用已有约定，选择 Action 版本或输入参数时查阅当前官方文档。

## 产物与依赖

产物是适配当前仓库的工作流 YAML，以及更新后的工作流或发布文档；已有双语文档时同步更新。CI 覆盖还原、Release 构建、受支持框架的测试、适当的缓存，以及已有的分析器、格式、覆盖率或报告步骤。

验证需要能将 `on` 保留为字符串的 YAML 解析器。可用时使用 `actionlint`；嵌入脚本使用 Bash 或 Python 检查，构建和打包检查需要兼容的 .NET SDK 与运行时。Skill 会明确说明无法完成的检查。

按任务需要配置 NuGet 发布工作流。[发布参考](../skills/create-dotnet-github-workflows/references/nuget-releases.md)涵盖从标签推导版本、检查提交是否属于主分支、独立或联合发布、项目引用依赖、包内容检查和发布结果验证。

## 使用示例

```text
使用 $create-dotnet-github-workflows 检查当前 .NET 仓库，
配置 Pull Request 和 main 分支的 CI，覆盖所有受支持的测试框架，
保留已有的必需检查名称。
```

```text
使用 $create-dotnet-github-workflows 检查独立 NuGet 发布工作流。
检查标签解析、主分支限制、包选择和 ProjectReference 依赖版本。
在本地模拟发布完成验证，不创建标签或发布包。
```

## 检查与执行范围

检查 YAML、本地文档链接和嵌入脚本。标签解析和分支限制在临时 Git 仓库中验证，并模拟注册表请求。涉及包或依赖修改时，在隔离环境中执行还原、构建、测试和打包，并检查实际 `.nupkg` 内容与依赖元数据。

创建或检查工作流的授权范围仅包含配置工作。创建标签、发布包、修改密钥和创建 GitHub Release 需要明确请求。配置验证采用模拟发布，保留真实仓库标签和包注册表的状态。
