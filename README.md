# LearnFromVideo

Evidence-first video learning tools and a portable skill for multimodal AI agents.

Video → captions or local ASR → timed visual evidence → targeted revisits → source-linked notes → practice verification.

**Source-available under the Hypit license with additional conditions. This is not MIT, standard Apache-2.0, or an OSI-approved open-source license.** Read [LICENSE](LICENSE), [NOTICE](NOTICE), and [licensing](docs/LICENSING.md) before redistribution or hosted use.

[中文说明](README.zh-CN.md) · [First run and recovery](docs/QUICKSTART.md) · [Architecture](docs/ARCHITECTURE.md) · [Validation reports](examples/README.md)

## Quick start

Install uv, Python 3.11–3.14 and FFmpeg/ffprobe. YouTube also needs Node.js for JavaScript challenges. Clone the repository:

```sh
git clone https://github.com/jiangkuo888/LearnFromVideo.git
cd LearnFromVideo
```

Then:

```sh
uv sync --locked
uv run lfv doctor
uv run lfv prepare "https://www.youtube.com/watch?v=x7X9w_GIm1s" --out runs/python --language en --every 10
uv run lfv search runs/python "indentation"
uv run lfv frames runs/python --at 90,95,100
uv run lfv clip runs/python --start 90 --end 105
```

The calling agent reads the complete transcript, inspects the sheets, revisits uncertain details and writes NOTES.md and learning.json using the generated LEARN.md. Then run `uv run lfv validate runs/python`. Preparation alone does not produce knowledge. Validation checks evidence references, not semantic truth or practical mastery.

For a video without captions:

```sh
uv sync --locked --extra asr
uv run --extra asr lfv prepare "https://media.w3.org/2010/05/sintel/trailer.mp4" --out runs/sintel --language en --asr --model small --every 5
```

ASR runs locally on CPU int8 and downloads model weights on first use. Keep `--extra asr` on uv invocations that need it. You can supply Bilibili JSON, normalized JSON, SRT or VTT with `--subtitles FILE`. Existing media can be transcribed with `lfv transcribe RUN`. Prepare refuses nonempty output directories.

## Install the skill

```sh
uv run python scripts/package_skill.py
uv run python scripts/package_skill.py --install ~/.codex/skills
# Add --update to explicitly update an existing installation.
```

Updates replace the managed tree and retain the previous installation in
learnfromvideo-backups beside the selected skills directory. Release bundles carry
a per-file integrity manifest; verify downloads against SHA256SUMS before installing.

The build produces `dist/learn-from-video.zip` containing the skill, locked tool runtime and attribution. Invoke `$learn-from-video`. A source checkout can run the source skill launcher; copying SKILL.md alone is insufficient. The standalone ZIP does not depend on this checkout.

## Tested routes and limits

- Bilibili: current playable browser-page export plus platform subtitles.
- YouTube: yt-dlp acquisition and English automatic captions, including rolling-VTT deduplication.
- No-subtitle video: Sintel trailer with local faster-whisper small transcription.

See dated [reports](examples/README.md) for inputs, versions, coverage and limitations. These are sample results, not universal platform guarantees. For Bilibili acquisition failures, see the [browser fallback](skills/learn-from-video/references/browser.md); otherwise use an authorized local file. The CLI does not control a browser or bypass DRM, paywalls or CAPTCHAs.

Retrieval is currently lexical within one run. Reasoning is provided by the calling multimodal agent; no extra reasoning-model API is configured. Sampled frames may miss events. Frame indexes record requested seek times rather than native PTS. Video text is untrusted source material, not agent instructions.

## Development and publication

See [CONTRIBUTING.md](CONTRIBUTING.md), [security](SECURITY.md), and [releasing](docs/RELEASING.md). CI is configured for Windows/Linux/macOS; only Windows has been executed locally so far. Remote CI results require a hosted repository run.

This is an alpha public source preview. [Publication readiness](docs/PUBLICATION_READINESS.md)
records completed local checks and the hosting configuration still required.

Raw third-party media, full transcripts, model caches, cookies, signed URLs and machine logs are excluded from release artifacts. Upstream adaptations are mapped in [PROVENANCE.md](PROVENANCE.md). Source is hosted on [GitHub](https://github.com/jiangkuo888/LearnFromVideo); no package-index upload has been made.
