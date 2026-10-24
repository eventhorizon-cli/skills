# Tag-driven NuGet releases

## Choose the contract

Preserve the repository's existing release convention. For a new monorepo convention, prefer concise hyphen prefixes,
such as `core-v<semver>` and `mmf-v<semver>`. These names are examples, not universal package names. Keep `v<semver>`
for joint releases only if the repository needs it. Slash and `package@version` styles are also valid; do not describe
one format as an industry requirement.

Document package selection and whether joint releases share one version. Parse tag input once and derive all versions
from it. Validate the entire version, including leading-zero and prerelease rules; state whether build metadata is
supported. Never evaluate tag content as shell code. Pass GitHub expressions through environment variables instead
of interpolating untrusted text directly into a `run` script.

Do not commit release version numbers into project files. Preserve existing versioning tooling if it already derives
versions correctly. When adding simple tag-derived versions, use command-line properties or temporary runner files.

## Enforce main-only tags

Honor the repository's release-branch policy; default new setups to `main` unless instructed otherwise.
Tag push events do not inherit a branch restriction from `branches: [main]`. To enforce main-only tags:

1. Check out sufficient history and tags (`fetch-depth: 0` when ancestry/tag discovery needs them).
2. Fetch `main`, peel the tag to a commit, and check `git merge-base --is-ancestor <tag-commit> origin/main`.
3. Reject failures before packing or publishing. Document whether historical main commits are allowed or the tag must
   equal the current main tip. Do not silently substitute one policy for the other.

An ancestry check validates commit membership, not who created a tag. Honor any existing repository release controls.

## Resolve package dependencies

Inspect the project-reference graph. A global `-p:Version=X` can unintentionally change all referenced package versions.

- For a joint same-version release, set each selected package and selected in-repository dependency package to the tag
  version. Pack and validate every selected package before publishing any; publish dependencies before dependents.
- For an independent dependent-package release, determine which compatible dependency version is already published.
  Preserve existing explicit version policy. For a simple repository without release tooling, the closest ancestor
  dependency-release tag can be used only with an explicit compatibility check against its source/build inputs.
  Do not select unrelated branch tags or assume that a Git tag proves a package exists in the registry.
- If shared source or build configuration changed after the dependency release, reject publication until the dependency
  is published, or use the joint-release path. Stable packages must not accidentally acquire prerelease dependencies.
- A dependency-only release must not publish dependent packages implicitly. Explain that source compatibility and
  independent package numbering are separate concerns.

For different versions in one build, a runner-temporary props file can condition properties on `MSBuildProjectName`:

```xml
<Project>
  <PropertyGroup Condition="'$(MSBuildProjectName)' == 'Example.Core'">
    <Version>DEPENDENCY_VERSION</Version>
    <PackageVersion>DEPENDENCY_VERSION</PackageVersion>
  </PropertyGroup>
  <PropertyGroup Condition="'$(MSBuildProjectName)' == 'Example.Storage'">
    <Version>RELEASE_VERSION</Version>
    <PackageVersion>RELEASE_VERSION</PackageVersion>
  </PropertyGroup>
</Project>
```

Replace placeholders with validated values and pass `-p:CustomAfterMicrosoftCommonProps=<temporary-file>` consistently
to restore/build/test/pack. Confirm the repository does not override these properties later. This hook reaches both
outer and inner multi-target evaluations; a hook after `Microsoft.Common.targets` alone can miss the outer pack build.
Check evaluated properties and the generated nuspec; do not rely solely on an MSBuild property printout. If emitting
XML from a shell heredoc, preserve literal `$(MSBuildProjectName)` rather than executing it as command substitution.

## Pack, inspect, then publish

- Build and test before packing. Pack only selected projects, preserving authors, repository/license metadata, package
  README inclusion, symbols, signing, and source-link policy. Verify the exact expected package file set.
- Inspect actual nupkg archives: package ID/version, assemblies for every supported TFM, README entries, and dependency
  versions/ranges in every framework group. Distinguish a minimum NuGet dependency version from an exact pinned range.
- Upload selected artifacts before publication. Keep release runs serialized with cancellation disabled. A single
  concurrency group prevents simultaneous publishers, but GitHub does not guarantee FIFO delivery of queued runs;
  choose an explicit queue policy if every tag must be processed.
- Use the repository's approved NuGet authentication and existing secret names. For new API-key configurations, use
  `NUGET_API_KEY`; never embed a key or print secrets. Add OIDC/trusted publishing only when requested or already established.
- Do not mask failures with `continue-on-error` or force a push. Use duplicate-package skipping only for the existing
  retry policy; validate identity/content before treating an immutable package as already published.
- If release execution is authorized, follow the repository's GitHub Release/assets policy and verify every selected
  package is downloadable from its registry before reporting completion. A successful push command alone is insufficient.

Smoke-test scoped/joint tags, malformed versions, non-main commits, missing/unpublished dependencies, changed dependency
inputs, stable/prerelease mismatches, wrong dependency metadata, and unexpected output packages. Mock publication; do
not send packages or tags as part of workflow validation.
