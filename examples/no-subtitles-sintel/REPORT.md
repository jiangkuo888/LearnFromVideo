# No-subtitle / local-ASR validation — 2026-11-05

Source: [Sintel trailer hosted by W3C](https://media.w3.org/2010/05/sintel/trailer.mp4).
Tool version: 0.2.0. Full portable metrics: [validation.json](validation.json).

```sh
uv sync --locked --extra asr
uv run --extra asr watch2skill prepare "https://media.w3.org/2010/05/sintel/trailer.mp4" --out runs/no-subtitles-sintel --language en --every 5 --asr --model small
uv run --extra asr watch2skill frames runs/no-subtitles-sintel --at 11,13,15,30
# Agent reads ASR and images, writes NOTES.md + learning.json.
uv run --extra asr watch2skill validate runs/no-subtitles-sintel
```

Absence checks: zero subtitle streams in ffprobe, no supplied subtitle file, zero
subtitle languages and zero automatic-caption languages in extraction metadata.
This is an independent public video, not a caption-stripped copy of the YouTube sample.

Observed: 52.208333-second MP4 acquired successfully. Local faster-whisper small,
CPU int8 with VAD, generated two dialogue segments (approximately 11.92–14.72 and
14.72–20.43 seconds). No hosted transcription service or paid API was used. All
11 overview frames and 4 revisit frames were inspected.

Three learning claims passed structural validation. Practice is explicitly
not-run: this is a narrative trailer, not an actionable tutorial. Successful ASR
execution is separate from semantic accuracy; there is no manually aligned ground
truth, word-error-rate score or claim that all audio events were understood.
See [notes](NOTES.md) for the limited content reading.

The end credits visible in the local source attribute Blender Foundation and
Creative Commons Attribution 3.0. The repository nevertheless distributes no media
or full transcript; source licensing remains separate from the tool's license.
