# CNBlogs Version

[简体中文](generate-cnblogs-version.zh-CN.md) · [Repository README](../README.md) · [Skill instructions](../skills/generate-cnblogs-version/SKILL.md)

Use `generate-cnblogs-version` to create a CNBlogs Markdown copy with the installed [.NET `dotnet-cnblog` tool](https://github.com/stulzq/dotnet-cnblogs-tool).

## Input and output

Give the skill the source Markdown path, for example:

```text
Use $generate-cnblogs-version to generate a CNBlogs version of docs/article.md.
```

The original article is preserved. The result is a separate `article-cnblog.md` with local article images uploaded to the configured CNBlogs account and their references replaced with hosted URLs. An existing `*-cnblog.md` output may be overwritten. After each run, inspect that the body and code remain intact and that image references became hosted links; missing images may be skipped. This prepares a file; it does not publish or update a blog post.

## Command and configuration

The main command is:

```bash
dotnet-cnblog proc -f "/absolute/path/article.md"
```

If the tool is missing, install it from the [upstream project](https://github.com/stulzq/dotnet-cnblogs-tool):

```bash
dotnet tool install --global dotnet-cnblog
```

Complete account setup locally using the MetaWeblog token from [CNBlogs settings](https://i.cnblogs.com/settings). Keep the token in local tool configuration; do not put it in the article, documentation, or a commit.

## Failures

Run the existing tool directly first. Investigate configuration or output details only when it fails or produces an incomplete result. For a partial upload failure, inspect the existing output and logs, then retry only unfinished work to avoid reuploading the whole article. Keep the original source available while retrying. See the [skill instructions](../skills/generate-cnblogs-version/SKILL.md) for the agent execution rules.
