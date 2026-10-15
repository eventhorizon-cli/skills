# Skills

English | [简体中文](README.zh-CN.md)

Reusable skills for AI coding agents. This repository currently contains `draw-technical-diagrams`, a skill for creating and revising technical flowcharts, system architecture diagrams, component diagrams, and data-flow diagrams.

> **Compatibility:** This skill has only been tested with Codex on macOS, so macOS is currently the only supported platform. Windows and Linux have not been verified and may not work because of dependency, path, or script differences. Other agents may be able to use the skill, but their installation paths and invocation methods can differ.

## Available Skills

| Skill | Description |
| --- | --- |
| [`draw-technical-diagrams`](draw-technical-diagrams) | Creates readable technical diagrams from prose, code, or an existing sketch, then renders and verifies the final image. |

## What It Does

`draw-technical-diagrams` gives an agent a repeatable workflow for technical diagrams:

- Creates flowcharts, architecture diagrams, component diagrams, and data-flow diagrams.
- Preserves editable source: `.mmd` for Mermaid and `.svg` for directly authored layouts.
- Renders white-background PNG, SVG, or PDF files with a pinned Mermaid CLI version when using Mermaid.
- Checks clipping, text overlap, ambiguous connections, arrow direction, and unsuitable aspect ratios.
- Uses direct SVG from the start when Mermaid is unsuitable, or switches immediately when Mermaid's rendered result is poor.

## Requirements

The currently verified setup uses macOS and Codex, or another agent that can load skills in this format. The Mermaid rendering script additionally requires:

- Bash.
- Node.js and `npx`.
- A headless Chrome or Chromium environment. On the verified macOS setup, the script prefers Google Chrome from `/Applications` and otherwise falls back to the Mermaid CLI/Puppeteer default.
- Network access on the first render to download Mermaid CLI.

Direct SVG authoring does not require the Mermaid CLI stack. PNG output from SVG requires an available SVG renderer.

## Installation

If your agent can install a skill from GitHub, give it the skill URL:

```text
Install and use this skill:
https://github.com/eventhorizon-cli/skills/tree/main/draw-technical-diagrams
```

For a manual Codex installation, clone the repository and copy the skill into the Codex skills directory:

```bash
git clone --depth 1 https://github.com/eventhorizon-cli/skills.git
mkdir -p ~/.codex/skills
cp -R skills/draw-technical-diagrams ~/.codex/skills/
```

Restart Codex or open a new task if the current task does not recognize the newly installed skill. For another agent, copy the directory to that agent's supported skills location.

## Usage

Once installed and recognized, the skill can be selected automatically when you ask the agent to draw or revise a technical diagram. In Codex, you can also invoke it explicitly with `$draw-technical-diagrams`.

A simple request can start with a short process:

```text
Draw an order submission flow:

Submit order -> validate order -> save to database -> return success.
Return an error when validation fails.

Keep the editable source (.mmd for Mermaid or .svg for direct SVG) and export
a high-resolution PNG with a white background.
```

For a more complex system, provide components, boundaries, connections, and the intended reading direction:

```text
Read the current project and draw its system architecture.

Separate the API, application service, message broker, consumer, and database
into their real ownership boundaries. Use solid lines for data flow and dashed
lines for registration or discovery. Keep the editable source (.mmd for
Mermaid or .svg for direct SVG) and export a high-resolution white-background
PNG suitable for a technical article.
```

A complex diagram may not match your expectations on the first attempt. Continue the conversation and point out concrete problems, such as an arrow connected to the wrong node, an image that is too wide, or details that should be moved into a separate diagram. Because the source is preserved, the agent can revise and render the existing diagram instead of starting over.

## Repository Layout

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
    └── render-mermaid.sh
```

## How It Works

The skill guides the agent through this workflow:

```text
Source material
  -> identify components and relationships
  -> assess whether Mermaid suits the layout
  -> create Mermaid source or directly author SVG
  -> render the requested image format
  -> inspect the rendered image
  -> switch directly to SVG if Mermaid's result is poor
  -> verify the final render
```

If Mermaid is unsuitable, the agent starts directly with SVG without a trial render. If a Mermaid render is poor, the agent switches immediately to an explicit SVG layout and keeps any existing `.mmd` as the logical model. Direct SVG diagrams do not require a `.mmd` companion. SVG can be delivered directly or rendered to a white-background PNG as needed.

The Mermaid rendering entry point is:

```bash
<skill-dir>/scripts/render-mermaid.sh input.mmd output.png
```

See [`draw-technical-diagrams/SKILL.md`](draw-technical-diagrams/SKILL.md) for the complete agent workflow and verification rules.

## License

This repository is licensed under the [MIT License](LICENSE).
