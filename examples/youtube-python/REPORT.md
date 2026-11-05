# YouTube validation — 2026-11-05

Source: [Python in 100 Seconds — Fireship](https://www.youtube.com/watch?v=x7X9w_GIm1s).
Tool version: 0.2.0. Full portable metrics: [validation.json](validation.json).

Reproduction from a prepared checkout:

```sh
uv run watch2skill prepare "https://www.youtube.com/watch?v=x7X9w_GIm1s" --out runs/youtube-python --language en --every 10
uv run watch2skill frames runs/youtube-python --at 66,74,95,100,113,119,130
uv run python examples/youtube-python/practice.py
# Agent reads transcript and images, writes NOTES.md + learning.json.
uv run watch2skill validate runs/youtube-python
```

Observed: direct yt-dlp acquisition succeeded, no browser export or cookies supplied.
The source duration was 143.341 seconds. Automatic captions initially repeated
rolling context; normalization was fixed and regression-tested. The cleaned
transcript contains 72 segments, with the original VTT retained only in the local
run. 15 overview frames and 7 revisit frames were actually inspected.

Four source-linked learning claims passed structural validation. The original
practice script passed five concept checks. [Notes](NOTES.md) explain the learned
concepts, visual corrections and limits. This is not a Python-course mastery test,
nor a guarantee that every YouTube video is downloadable. No independent ASR word
accuracy evaluation was performed; this sample used platform captions.

Raw video, full captions and frame images are not included in the repository.
