# Release checklist

1. Review LICENSE, NOTICE, dependency/model licensing and the source-available label.
2. Keep README platform claims tied to dated reports in examples/. Do not substitute
   unit tests for real network validation or describe unexecuted CI as passed.
3. Run lint, formatting and tests from CONTRIBUTING.md. Normal tests use generated
   local media and do not fetch models or third-party videos.
4. Run `uv build`, `uv run python scripts/package_skill.py`, and
   `uv run python scripts/check_release.py`. Inspect the wheel, source distribution
   and portable skill ZIP. They must retain attribution and omit private artifacts.
   Run `uv run python scripts/check_repository.py` for public-tree content, links
   and action pins. The release check writes SHA256SUMS and release-manifest.json;
   distribute only the versioned artifacts listed there, not stale files in dist/.
5. Test the ZIP from a clean directory. It must not need an upstream or author-local
   checkout. First run can install locked dependencies using uv.
   `uv run python scripts/smoke_release.py` verifies fresh wheel/skill installations.
6. Add a project repository URL and a private reporting channel when a public host
   is selected. No hosting account, remote, package name availability or publisher
   identity is assumed by this checkout.
   On GitHub, run CI on the first push before protecting the default branch. Enable
   required passing checks, pull-request review, dependency alerts and private
   vulnerability reporting. Select actual check names from the completed run.
   Inspect Actions artifacts before creating the first preview release. Publishing
   to a package index is a separate decision; no upload token is stored here.
7. Publish only after reviewing the generated release files and configured CI.

This preparation does not publish a repository, push Git commits, create a release
or upload to a package index. Keep network platform tests opt-in because login,
availability, rate limits and access rights vary by environment.

The current support tier is an alpha public source preview. Local Windows checks
are evidence for Windows only. Linux/macOS CI and repository-host settings cannot
be claimed complete before the selected host runs them. SHA-256 checksums detect
changes but are not signatures or publisher attestations.
