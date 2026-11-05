# Changelog

## 0.2.1 — 2026-11-05

- Added version diagnostics and invalidate stale success reports on failed rechecks.
- Made skill ZIP output stable across input modification times, with a per-file
  integrity manifest and release SHA256SUMS.
- Replace installed skills without stale files; retain an external rollback copy
  and refuse unrelated or out-of-directory targets.
- Added archive content/integrity scans, local-link checks, installation smoke tests,
  community templates, immutable CI action pins and weekly dependency update config.
- Prepared public source preview documentation while retaining the inherited license.

## 0.2.0 — 2026-11-05

- Validated a YouTube automatic-caption path and an independent no-subtitle local-ASR path.
- Removed repeated rolling-caption context without deleting ordinary repeated speech.
- Split acquisition, transcripts, media, pipeline, learning, core and CLI modules.
- Added millisecond time labels and preserved visual evidence before optional ASR.
- Added portable validation reports, an original Python practice example and an offline
  generated-media integration test.
- Added source-available licensing clarity, NOTICE, contribution/security/release guidance,
  English/Chinese READMEs, a cross-platform CI definition and release artifact checks.
- Build portable skill ZIPs from one authoritative source tree; support explicit updates.

## 0.1.0 — 2026-11-05

- Initial Hypit-derived local CLI, Bilibili browser-export validation and LearnFromVideo skill.
