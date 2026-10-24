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

Before changing a diagram, choose the work mode:

- **Faithful redraw** applies when an existing image, screenshot, or sketch is the source of truth. Preserve its observable nodes, edges, labels, grouping, and approximate geometry without silently redesigning the topology.
- **Semantic-first creation** applies when there is no existing image to preserve. Extract the node names, ownership, directed edges, branch conditions, timing states, and other semantic requirements before drawing.

Keep the chosen mode explicit. If an existing diagram is ambiguous, preserve the observable structure and call out the uncertainty instead of inventing a relationship.

Choose Mermaid for standard flows and sequences when automatic layout is clear. Use directly authored SVG when precise placement, fixed alignment, dense cross-group connections, or controlled routing is needed. If Mermaid is unavailable, blocked by its runtime or browser, or produces a poor layout, switch directly to SVG. Keep editable sources: `.mmd` for Mermaid and `.svg` for direct SVG. For SVG diagrams, also keep a `.mmd` logical model when Mermaid can faithfully express the relationships, even if Mermaid cannot run.

- Use left-to-right layouts for architecture and data-flow diagrams unless a short process naturally reads vertically.
- Keep groups tied to real ownership or deployment boundaries, use solid arrows for primary requests or data flow, and dashed arrows for discovery, registration, heartbeats, or other control-plane traffic.
- Inspect the rendered image for clipping, crowded text, ambiguous arrows, wrong arrow direction, and unsuitable proportions before delivery.

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

The Mermaid rendering script is [`render-mermaid.sh`](draw-technical-diagrams/scripts/render-mermaid.sh). It supports PNG, SVG, and PDF output and pins Mermaid CLI `11.12.0`.

**Static checks**

Run the bundled checks before opening the rendered image:

```bash
python3 <skill-dir>/scripts/validate-svg.py diagram.svg --strict
python3 <skill-dir>/scripts/check-markdown-diagrams.py README.md
```

`validate-svg.py` checks XML, canvas metadata, an explicit white background, text positioning, marker references, duplicate IDs, and duplicate path geometry. `check-markdown-diagrams.py` checks local Markdown and HTML image links, resolving relative paths from each Markdown file while ignoring remote, data, and fragment-only URLs. These checks are structural gates and do not replace visual inspection.

For more detail, see the [skill instructions](draw-technical-diagrams/SKILL.md).

**Repository layout**

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

**How it works**

```text
Source material
  -> identify components and relationships
  -> choose faithful redraw or semantic-first creation
  -> assess whether Mermaid suits the layout
  -> create Mermaid source or directly author SVG
  -> render the requested image format
  -> inspect and verify the final render
```

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
