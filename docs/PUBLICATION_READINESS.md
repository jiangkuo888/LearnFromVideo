# Public source preview readiness — 0.2.1

Assessment date: 2026-11-05. Recommended tier: **alpha public source preview**.
This covers the local checkout and artifacts, not a hosted repository, legal
certification, universal platform availability or a production SLA.

## License

The owner chose to retain the Hypit additional-conditions license. Upstream LICENSE
was preserved byte-for-byte; NOTICE and provenance accompany distributions. Publish
as **source-available**, not MIT, unmodified Apache-2.0 or OSI-approved open source.
See [licensing](LICENSING.md). Removing vendor snapshots alone cannot relicense the
existing adaptations.

## Completed local checks

| Area | Evidence |
|---|---|
| Real inputs | Bilibili, YouTube captions and independent no-subtitle ASR with scoped [reports](../examples/README.md) |
| Behavior | 16 tests: generated-media integration, stale-validation removal, unsafe archive paths, tampering, stable ZIP bytes and safe skill updates |
| Code | Ruff lint/format; separate acquisition, transcripts, media, pipeline, learning and CLI modules |
| Metadata | Wheel and source distribution build; Twine metadata checks pass |
| Installation | Wheel and skill ZIP run in fresh directories outside the source checkout, reporting 0.2.1 |
| Artifact contents | Scans reject private media, concrete credential markers, personal paths, unsafe archive paths and altered attribution |
| Integrity | Per-file skill manifest; SHA256SUMS and release-manifest.json |
| Repository | Public content, local Markdown links and immutable Action references checked |
| Maintenance | Contribution/conduct guidance, issue/PR templates, dependency-update config and release procedure |
| CI definition | Three operating systems, read-only permissions, pinned Action commits, fixed uv version, timeouts, concurrency and build artifacts |

Tests do not fetch videos or models. Installation smoke checks can access the
package index. Content scanning cannot guarantee detection of every secret format.
Checksums are not publisher signatures. ZIP stability was tested for unchanged
file bytes with different modification times, not every compression runtime.

## Required on the selected hosting service

The public repository is [jiangkuo888/LearnFromVideo](https://github.com/jiangkuo888/LearnFromVideo).
Project URLs, private vulnerability reporting, dependency alerts and automatic
security updates are configured. The main branch requires the six matrix checks,
one PR approval and resolved conversations; force-push and deletion are disabled.
Administrators retain bypass capability for repository recovery.

[Initial CI](https://github.com/jiangkuo888/LearnFromVideo/actions/runs/42057344968)
passed on Linux and Windows with Python 3.11 and 3.13. The first macOS execution
then exposed an x64-only FFmpeg installer on an ARM runner. CI now uses native
FFmpeg provisioning on macOS while retaining both Python versions.
See [current runs](https://github.com/jiangkuo888/LearnFromVideo/actions/workflows/ci.yml)
for subsequent results.
Before announcing a tested release:

1. Select the repository owner/name and add real source, issue and documentation
   URLs to metadata. Do not invent maintainer identities or contact addresses.
2. Configure a private vulnerability-reporting route and document it in SECURITY.md.
3. Push reviewed source and run remote CI. Linux/macOS remain unverified; local
   Windows success is not cross-platform success.
4. After the first run, enable required passing checks, pull-request review,
   dependency alerts and applicable private vulnerability-reporting settings.
5. Publish only artifacts listed in release-manifest.json. Old files in dist are
   not part of this release. Package-index publishing is a separate decision.

Commands and rollback guidance: [releasing](RELEASING.md), [recovery](QUICKSTART.md).
No package-index upload or GitHub release has been created by this preparation.
