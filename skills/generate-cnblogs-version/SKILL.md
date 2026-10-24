---
name: generate-cnblogs-version
description: "Generate a CNBlogs-ready Markdown version of an article using the installed dotnet-cnblog tool, uploading referenced local images and replacing their links while preserving the original. Use when the user asks for 生成博客园版本, 博客园格式, 转成博客园, or a CNBlogs version of a Markdown article. This prepares a file; publishing the article is a separate request."
---

# 生成博客园版本

直接调用已安装的 .NET 程序 [dotnet-cnblog](https://github.com/stulzq/dotnet-cnblogs-tool)，使用现有账号配置生成博客园 Markdown 版本。先执行，失败或输出不完整时再排查，不做环境、配置或图片兼容性的前置检查，也不自行实现一套转换器。

1. 使用用户指定的 Markdown，或当前对话中刚生成的文章；只有正文时先保存为 `.md`。来源不明确时再询问。
2. 直接运行：

   ```bash
   dotnet-cnblog proc -f "/absolute/path/article.md"
   ```

3. 检查生成的 `article-cnblog.md`：本地图片是否已替换为远程链接，正文和代码是否保留。工具可能跳过缺失图片，因此不能只看退出码。
4. 返回生成文件的链接。原稿保留不动；同名 `*-cnblog.md` 会被工具覆盖。

仅在遇到问题时处理对应原因：

- **找不到命令**：尝试已安装的 `~/.dotnet/tools/dotnet-cnblog`。确认未安装后，提供项目链接并提示 `dotnet tool install --global dotnet-cnblog`；缺少 `dotnet` 时提示安装 .NET SDK。
- **要求配置账号或认证失败**：提示用户在本机完成工具配置，Token 来自 [博客园设置](https://i.cnblogs.com/settings)。不在聊天中索取 Token，不重置现有配置。`--help` 也会触发配置初始化，不用于绕过这个问题。
- **图片未转换或显示异常**：按实际问题检查路径、图片语法或格式。相对路径以输入 Markdown 所在目录为基准；工具仅识别 `![alt](path)`，SVG 上传类型可能不合适。需要修正语法、保护被误处理的代码示例或导出 PNG 时，使用工作副本，保留原稿及图源。
- **部分上传后失败**：先检查已有输出和日志，只处理未完成部分，避免盲目重复上传整篇文章。

“生成博客园版本”包含上传文章引用的本地图片；用户明确要求离线或不上传时遵从该约束。此操作仅生成文件，不发布或更新博客文章。
