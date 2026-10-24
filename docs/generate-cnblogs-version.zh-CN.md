# 生成博客园版本

[English](generate-cnblogs-version.md) · [仓库 README](../README.zh-CN.md) · [Skill 说明](../skills/generate-cnblogs-version/SKILL.md)

使用 `generate-cnblogs-version` 和已安装的 [.NET `dotnet-cnblog` 工具](https://github.com/stulzq/dotnet-cnblogs-tool)，生成适合博客园 Markdown 编辑器的文章副本。

## 输入与产物

提供原始 Markdown 路径，例如：

```text
使用 $generate-cnblogs-version 为 docs/article.md 生成博客园版本。
```

工具会保留原稿，生成单独的 `article-cnblog.md`，将文章中的本地图片上传到已配置的博客园账号，并替换为远程图片链接。已有的 `*-cnblog.md` 可能会被覆盖。每次运行后都要检查正文和代码是否保留、图片是否已替换为远程链接；缺失图片可能会被跳过。这个流程只准备文件，不会发布或更新博客文章。

## 命令与配置

主要命令为：

```bash
dotnet-cnblog proc -f "/absolute/path/article.md"
```

如果工具未安装，请参考[上游项目](https://github.com/stulzq/dotnet-cnblogs-tool)：

```bash
dotnet tool install --global dotnet-cnblog
```

在本机根据工具提示配置账号，MetaWeblog Token 来自[博客园设置](https://i.cnblogs.com/settings)。Token 应保存在本地工具配置中，不要写入文章、文档或提交记录。

## 失败处理

先直接运行现有工具；只有在运行失败或输出不完整时再排查配置和输出。部分图片上传失败时，先检查已有输出和日志，只重试未完成的部分，避免整篇文章重复上传。重试时保留原稿。完整的 Agent 执行规则见 [Skill 说明](../skills/generate-cnblogs-version/SKILL.md)。
