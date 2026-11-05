# Source and adaptations

Upstream: https://github.com/hypit-ai/hypit

Upstream source commit: 9693c09be9371e623b66fbfe22b59ae60afecc27.

Copyright © 2026 Hypit.AI. Original LICENSE retained verbatim, including additional conditions.

Copied snapshots:
- packages/yt-dlp/src/download.ts → vendor/hypit/yt-dlp/download.ts
- packages/yt-dlp/README.md → vendor/hypit/yt-dlp/README.md
- packages/media-local/src/file-frames.ts → vendor/hypit/media-local/file-frames.ts
- packages/media-local/README.md → vendor/hypit/media-local/README.md
- skills/hypit/references/creation/reference-video.md → references/hypit-reference-video.md

Python adapts config-isolated yt-dlp A/V acquisition, explicit FFmpeg ownership and iterative timestamped evidence reading. Added normalized subtitles, optional faster-whisper ASR, browser export input, retrieval and learning-reference validation. Copied TypeScript files are provenance references, not standalone executable modules. Version 0.2 separates acquisition, media, transcript, pipeline, learning, core and CLI modules; source and skill distributions retain the same license.

Unlike upstream native-PTS sequences, the Python extractor records requested seek times explicitly as requested_time. It does not claim native PTS precision.
