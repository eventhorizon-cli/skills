# Skills

English | [简体中文](README.zh-CN.md)

Reusable skills for AI coding agents: technical diagrams, CNBlogs Markdown conversion, and benchmark charts.

[Skill catalog](#skill-catalog) · [Installation](#installation) · [Documentation](#documentation) · [Compatibility](#compatibility)

## Skill catalog

| Skill | Use it to | Guide |
| --- | --- | --- |
| `draw-technical-diagrams` | Draw or revise flowcharts, architecture diagrams, and data flows | [User guide](docs/draw-technical-diagrams.md) · [Skill instructions](skills/draw-technical-diagrams/SKILL.md) |
| `generate-cnblogs-version` | Convert a Markdown article with `dotnet-cnblog` | [User guide](docs/generate-cnblogs-version.md) · [Skill instructions](skills/generate-cnblogs-version/SKILL.md) |
| `render-benchmark-charts` | Render and visually review SVG charts from measured CSV data | [User guide](docs/render-benchmark-charts.md) · [Skill instructions](skills/render-benchmark-charts/SKILL.md) |

Install the skills you need. Once recognized by your agent, use a natural-language request or invoke its `$skill-name` explicitly.

## Installation

Ask your agent to install the skill you need using its GitHub URL:

```text
https://github.com/eventhorizon-cli/skills/tree/main/skills/draw-technical-diagrams
https://github.com/eventhorizon-cli/skills/tree/main/skills/generate-cnblogs-version
https://github.com/eventhorizon-cli/skills/tree/main/skills/render-benchmark-charts
```

For a manual Codex installation:

```bash
git clone --depth 1 https://github.com/eventhorizon-cli/skills.git agent-skills
mkdir -p ~/.codex/skills
cp -R agent-skills/skills/draw-technical-diagrams ~/.codex/skills/
cp -R agent-skills/skills/generate-cnblogs-version ~/.codex/skills/
cp -R agent-skills/skills/render-benchmark-charts ~/.codex/skills/
```

Open a new task or restart the agent if an installed skill is not recognized. Other agents may use different installation directories.

## Usage

```text
Use $draw-technical-diagrams to draw an order flow and export a white-background PNG.
Use $generate-cnblogs-version to convert docs/article.md for CNBlogs.
Use $render-benchmark-charts to plot results.csv as SVG charts and visually review them.
```

## Documentation

The [technical diagrams guide](docs/draw-technical-diagrams.md) covers useful inputs, outputs, dependencies, examples, and failure handling. The [CNBlogs guide](docs/generate-cnblogs-version.md) covers conversion, image upload, configuration, and producing a file without publishing a post. The [benchmark charts guide](docs/render-benchmark-charts.md) covers CSV input, configuration, rendering, and visual checks. The [maintenance guide](docs/maintaining.md) covers syncing local skills and running checks.

The repository keeps skill implementations under `skills/`, user guides under `docs/`, and validation entry points under `scripts/`.

## Compatibility

The current usage and verification environment is **Codex on macOS**. Windows, Linux, and other agents have not been verified. Each skill's dependencies are listed in its user guide.

## License

[MIT](LICENSE).
