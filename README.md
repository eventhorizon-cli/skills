# Skills

English | [简体中文](README.zh-CN.md)

Reusable skills for AI coding agents: create technical diagrams and prepare Markdown articles for CNBlogs.

[Skill catalog](#skill-catalog) · [Installation](#installation) · [Compatibility](#compatibility)

## Skill catalog

| Skill | Use it to | Output |
| --- | --- | --- |
| [Technical diagrams](#technical-diagrams) | Draw or revise flowcharts, architecture diagrams, and data flows | Rendered images and editable diagram sources |
| [生成博客园版本 · CNBlogs version](#cnblogs-version) | Convert a Markdown article using the installed `dotnet-cnblog` tool | A separate `*-cnblog.md` with hosted image links |

Install either skill or both. Once recognized by your agent, use a natural-language request or invoke its `$skill-name` explicitly.

## Installation

**Ask your agent to install the skill you need** using its GitHub URL:

```text
Install this skill:
https://github.com/eventhorizon-cli/skills/tree/main/draw-technical-diagrams
```

```text
Install this skill:
https://github.com/eventhorizon-cli/skills/tree/main/generate-cnblogs-version
```

**For a manual Codex installation**, clone the repository and copy the directories you need:

```bash
git clone --depth 1 https://github.com/eventhorizon-cli/skills.git
mkdir -p ~/.codex/skills

# Technical diagrams
cp -R skills/draw-technical-diagrams ~/.codex/skills/

# CNBlogs version
cp -R skills/generate-cnblogs-version ~/.codex/skills/
```

If a newly installed skill is not recognized, open a new task or restart your agent. Other agents may use different installation directories.

## Technical diagrams

[`draw-technical-diagrams`](draw-technical-diagrams/SKILL.md)

Create flowcharts, system architecture diagrams, component diagrams, and data-flow diagrams from prose, code, or an existing sketch.

- Choose Mermaid for suitable layouts; use directly authored SVG when precise placement is needed or Mermaid renders poorly.
- With Node.js available, allow one lightweight Mermaid attempt. If the runtime, dependency download, or sandbox blocks it, switch to SVG.
- Keep editable sources. For SVG diagrams, also keep a `.mmd` logical model when Mermaid can faithfully express the relationships, even if Mermaid cannot run.
- Inspect the rendered image for clipping, crowded text, ambiguous arrows, and unsuitable proportions before delivery.

**Try it**

```text
Use $draw-technical-diagrams to draw this order flow:

Submit order -> validate -> save to database -> return success.
Return an error when validation fails.

Export a white-background PNG and keep editable sources, including a .mmd
logical model when the relationships can be represented in Mermaid.
```

**Dependencies**

| Rendering path | Requirements |
| --- | --- |
| Mermaid | Bash, Node.js/`npx`, and headless Chrome/Chromium; the first run may download the pinned Mermaid CLI |
| Direct SVG | No Mermaid runtime required; a working SVG viewer or renderer is needed for visual verification and PNG export |

See the [skill instructions](draw-technical-diagrams/SKILL.md) for layout and verification rules. The Mermaid helper is available at [`render-mermaid.sh`](draw-technical-diagrams/scripts/render-mermaid.sh).

## CNBlogs version

[`generate-cnblogs-version`](generate-cnblogs-version/SKILL.md) · Display name: **生成博客园版本**

Generate a Markdown copy ready for the CNBlogs Markdown editor, using the installed .NET program [dotnet-cnblog](https://github.com/stulzq/dotnet-cnblogs-tool).

- Run the existing tool directly, then investigate only if it fails or produces an incomplete result.
- Upload the article's local images to the configured CNBlogs account and replace their references with hosted URLs.
- Preserve the original and return `article-cnblog.md`. This prepares a file; it does not publish or update a blog post.

**Try it**

```text
Use $generate-cnblogs-version to generate a CNBlogs version of docs/article.md.
```

You can also say “生成博客园版本” or “转成博客园格式” when the article is clear from the conversation.

**Tool and setup**

The skill reuses your existing installation and account configuration. Its main command is:

```bash
dotnet-cnblog proc -f "/absolute/path/article.md"
```

If the tool is missing, the agent points to the [upstream project](https://github.com/stulzq/dotnet-cnblogs-tool) and suggests:

```bash
dotnet tool install --global dotnet-cnblog
```

If account setup is needed, complete the tool's prompts locally with a MetaWeblog token from [CNBlogs settings](https://i.cnblogs.com/settings). See the [skill instructions](generate-cnblogs-version/SKILL.md) for handling conversion failures.

## Compatibility

The current usage and verification environment is **Codex on macOS**. Windows, Linux, and other agents have not been verified. Dependencies are listed under each skill; installing one skill does not require the other skill's tools.

## License

[MIT](LICENSE).
