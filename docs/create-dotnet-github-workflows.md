# .NET GitHub Workflows

[简体中文](create-dotnet-github-workflows.zh-CN.md) · [Repository README](../README.md) · [Skill instructions](../skills/create-dotnet-github-workflows/SKILL.md)

Use `create-dotnet-github-workflows` to create, review, or update GitHub Actions CI and NuGet publishing workflows for .NET/C# repositories, including multiple target frameworks and independently versioned packages.

## What to provide

- The repository, applicable `AGENTS.md`, existing workflows, and build or release documentation.
- Solutions and projects, `global.json`, shared build/package properties, lock files, and NuGet configuration.
- The intended CI branches, required checks, and any existing package version, tag, signing, or registry conventions.

The skill inspects supported target frameworks, SDKs, test runtimes, VSTest or Microsoft.Testing.Platform runner selection, packable projects, and project references before choosing commands. It preserves existing conventions and consults current official action documentation when selecting versions or inputs.

## Outputs and dependencies

The result is repository-specific workflow YAML and updated workflow or release documentation, including bilingual pairs when present. CI covers restore, Release builds, supported test frameworks, appropriate caching, and existing analyzer, formatting, coverage, or report steps.

Validation needs a YAML parser that preserves `on` as a string. Use `actionlint` when available, Bash or Python for embedded scripts, and compatible .NET SDKs/runtimes for build and package checks. The skill reports unavailable checks explicitly.

NuGet release configuration is optional. When it is in scope, the [release reference](../skills/create-dotnet-github-workflows/references/nuget-releases.md) covers tag-derived versions, main-branch membership, independent or joint releases, project-reference dependencies, package inspection, and publication verification.

## Examples

```text
Use $create-dotnet-github-workflows to inspect this .NET repository
and configure pull-request and main-branch CI. Cover every supported
test framework and preserve the existing required check names.
```

```text
Use $create-dotnet-github-workflows to review our independent NuGet
release workflows. Check tag parsing, main-branch guards, package
selection, and ProjectReference dependency versions. Validate locally
with mocked publication; do not create tags or publish packages.
```

## Checks and execution scope

Validate YAML, local documentation links, and embedded scripts. Exercise tag parsers and branch guards in temporary Git repositories with mocked registry requests. For package or dependency changes, perform an isolated restore/build/test/pack run and inspect the actual `.nupkg` contents and dependency metadata.

Adding or reviewing workflows does not authorize creating tags, publishing packages, changing secrets, or creating a GitHub Release. Those actions need an explicit request. Configuration validation uses mocked publication and leaves real repository tags and package registries untouched.
