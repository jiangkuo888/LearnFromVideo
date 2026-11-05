# First successful run

Install uv, Python 3.11+, FFmpeg/ffprobe and Node.js. From a source checkout:

```sh
uv sync --locked
uv run watch2skill --version
uv run watch2skill doctor
uv run watch2skill prepare "https://www.youtube.com/watch?v=x7X9w_GIm1s" --out runs/first --language en --every 10
```

Doctor reports inventory, not a successful pipeline test. A null ffmpeg or ffprobe
path means that executable still needs installation or a PATH fix.

`evidence-ready` means transcript and frame evidence were generated. Your
multimodal agent reads runs/first/LEARN.md, the complete transcript and every
overview sheet, then revisits relevant details before writing NOTES.md and
learning.json. Finish with `uv run watch2skill validate runs/first`.

validation.json confirms reference structure and includes the SHA-256 of the
learning document it checked. It does not prove the claims true. Revalidation
failure removes the old success report.

## No-subtitle input

```sh
uv sync --locked --extra asr
uv run --extra asr watch2skill prepare "path/to/video.mp4" --out runs/speech --language en --asr --model small
```

First use downloads model weights. CPU int8 requires no GPU. You may also supply a
local model path with --model. Empty ASR output is failure to obtain a usable timed
transcript, not proof that no speech exists.

## Recovery

| Symptom | Action |
|---|---|
| Nonempty output directory | Preserve it and use a new run for fresh preparation. |
| needs-transcript | Use `transcribe RUN --subtitles FILE`, or local ASR. |
| Model download failure | Keep the frames generated before ASR and retry transcribe after fixing model access. |
| Missing frame evidence | Run `frames RUN --at SECONDS`, then inspect the images before citing them. |
| HTTP 412, login or rate limits | Use a normally playable supported browser route or an authorized local file. |
| Claim validation failure | Correct its range/evidence, or narrow the claim; do not invent observations. |

ASR recovery: `uv run --extra asr watch2skill transcribe RUN --language en --model small`.
Recovery commands require completed media and duration in manifest.json. If
acquisition failed before those exist, fix access and prepare a fresh run.

## Portable skill

Build and install with scripts/package_skill.py, or unpack the verified skill ZIP
into a clean directory. Keep the entire folder and runtime; do not overlay an old
installation manually. The source installer supports --update, completely replaces
the managed tree, and retains the previous copy in watch2skill-backups beside
the chosen skills directory.
