---
name: create-dotnet-github-workflows
description: Create, review, or update GitHub Actions CI and NuGet publishing workflows for .NET/C# repositories. Use for dotnet restore/build/test pipelines, multiple target frameworks, SDK setup, NuGet caching, or tag-driven single-package and monorepo releases. Includes independent package versions, ProjectReference dependencies, main-only release tags, and package validation. Does not authorize creating tags or publishing packages.
---

# .NET GitHub Actions workflows

Create workflows that match the repository's actual build and release contracts. Keep simple repositories simple;
load [NuGet release guidance](references/nuget-releases.md) only when packaging or publication is in scope.

## Inspect the repository

- Read applicable `AGENTS.md`, existing workflows, and release documentation before editing.
- Use `rg --files` to find solutions (`.sln`/`.slnx`), projects, `global.json`, `Directory.Build.*`,
  `Directory.Packages.props`, lock files, and existing NuGet configuration. Preserve established conventions.
- Identify SDK selection, supported TFMs, test projects, test runner, packable projects, package IDs, and project references.
  Distinguish the SDK needed to compile from the runtimes needed to execute every supported test framework.
- Check whether tests use VSTest or Microsoft.Testing.Platform; their CLI switches differ. Honor `global.json` runner
  selection and inspect the installed SDK's help before choosing unfamiliar flags.
  For MTP selected through `global.json`, require .NET SDK 10+ and MTP 1.7+, and verify every selected test project
  supports MTP. Mixed runners require separately compatible configurations/invocations; splitting jobs alone does not
  override `global.json`. Use the installed SDK's MTP project/solution syntax rather than VSTest positional syntax.
- Identify existing required checks before renaming jobs or workflows. Do not change framework, language, package
  version, signing, coverage, or registry policy incidentally.
- Read current official action documentation before selecting action versions or new inputs. Honor repository SHA-pin
  policy and runner compatibility; do not copy stale action versions from examples.

## Build the CI workflow

1. Use `pull_request` and the repository's intended push branches. Add `merge_group` only when its merge queue needs it.
   Test untrusted PR code without publication credentials; do not execute it through privileged `pull_request_target`.
2. Start with `permissions: contents: read`. Grant extra permissions only to the jobs that need them.
3. Cancel superseded CI runs using a concurrency group scoped by workflow and PR/ref. Give jobs clear names so
   independently failing test projects and frameworks are distinguishable.
4. Install the repository's required SDKs/runtimes with `actions/setup-dotnet`. Respect `global.json` and its roll-forward
   policy. A library TFM is not, by itself, a reason to compile the entire solution under that TFM's SDK.
5. Cache NuGet packages using existing lock files when the setup action supports that configuration. Without lock files,
   use `actions/cache` with OS/architecture and relevant SDK, solution, project, `Directory.*`, lock/config file inputs.
   Do not enable lock-file-dependent caching against nonexistent locks or create a NuGet.config just for caching.
6. Restore once per compatible job, build in Release, then test the same built configuration. Use `--no-restore` and
   `--no-build` only when that job has already produced the required assets for the same TFMs and MSBuild properties.
7. Cover every supported test TFM. Use either an explicit project/TFM matrix or distinct project steps; avoid redundant
   whole-solution builds in every matrix cell. Benchmarks may target a newer framework than the libraries.
8. Preserve required formatting, analyzer, coverage, and test-report steps. Keep publication separate from ordinary CI.

Prefer existing commands. For a conventional VSTest solution, a compatible sequence is:

```bash
dotnet restore <solution>
dotnet build <solution> --configuration Release --no-restore
dotnet test <solution> --configuration Release --no-build --no-restore
```

Adapt project/TFM selection and runner-specific switches after inspection. Do not invent coverage thresholds or add
production dependencies to support CI.

## Validate without publishing

- Check the diff and local documentation links. Parse YAML with a YAML 1.2 parser or a base loader that preserves `on`
  as a string; a default YAML 1.1 loader can silently turn it into a Boolean.
- Run `actionlint` if available. Check embedded Bash with `bash -n` and compile embedded Python. If a checker is
  unavailable, report the checks actually completed rather than claiming that linter passed.
- For tag parsers and branch guards, exercise success/failure paths in temporary Git repositories with mocked registry
  requests. Never create test tags in the user's real repository.
- For packing/version/dependency changes, perform an isolated restore/build/test/pack smoke run and inspect the actual
  `.nupkg` files. YAML validation alone cannot prove package dependency correctness.
- Configuration-only edits do not need artificial unit tests or unrelated benchmark runs. Reuse completed checks when
  later edits only change documentation or validated tag prefixes.

Update workflow/release documentation and bilingual pairs when present. Report triggers, supported SDKs/TFMs, tag and
dependency behavior, checks run, and any unverified condition concisely. Creating workflows does not authorize pushing
tags, publishing packages, changing secrets, or creating a release; follow the user's explicit scope.

## Official references

- [GitHub workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [actions/setup-dotnet](https://github.com/actions/setup-dotnet)
- [dotnet test and runner selection](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test)
- [dotnet test with MTP](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test-mtp)
- [MSBuild customization hooks](https://learn.microsoft.com/en-us/visualstudio/msbuild/customize-net-builds)
