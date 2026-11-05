"""LearnFromVideo media; Hypit-derived workflow, see LICENSE and PROVENANCE.md."""

import json
import math
import sys

from PIL import Image, ImageDraw, ImageFont

from .core import read, run, save, stamp


def probe(media):
    return json.loads(
        run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", media], 60)
    )


def frames(folder, times, output="frames"):
    duration = read(folder / "manifest.json")["duration"]
    directory = folder / output
    directory.mkdir(parents=True, exist_ok=True)
    evidence = (
        {x["path"]: x for x in read(directory / "index.json")}
        if (directory / "index.json").exists()
        else {}
    )
    for t in times:
        if not math.isfinite(t) or not 0 <= t < duration:
            raise ValueError(f"Frame time {t} outside source")
        path = directory / f"{t:010.3f}.jpg"
        if not path.exists():
            run(
                [
                    "ffmpeg",
                    "-v",
                    "error",
                    "-nostdin",
                    "-n",
                    "-ss",
                    t,
                    "-i",
                    folder / "source.mp4",
                    "-map",
                    "0:v:0",
                    "-frames:v",
                    "1",
                    "-vf",
                    "scale=1280:-2",
                    "-q:v",
                    "2",
                    path,
                ],
                60,
            )
        if not path.exists():
            raise RuntimeError(f"No decoded frame at {t}")
        relative = path.relative_to(folder).as_posix()
        evidence[relative] = {"id": f"f{t:010.3f}", "requested_time": t, "path": relative}
    evidence = sorted(evidence.values(), key=lambda x: x["requested_time"])
    save(directory / "index.json", evidence)
    manifest = read(folder / "manifest.json")
    if manifest["state"] == "needs-frames" and (folder / "transcript.json").exists():
        manifest["state"] = "evidence-ready"
        save(folder / "manifest.json", manifest)
    font = (
        ImageFont.truetype("arial.ttf", 18) if sys.platform == "win32" else ImageFont.load_default()
    )
    for page in range(0, len(evidence), 12):
        group = evidence[page : page + 12]
        sheet = Image.new("RGB", (1440, 300 * math.ceil(len(group) / 3)), "#151515")
        draw = ImageDraw.Draw(sheet)
        for i, item in enumerate(group):
            with Image.open(folder / item["path"]) as im:
                im.thumbnail((480, 270))
                x, y = i % 3 * 480, i // 3 * 300
                sheet.paste(im, (x, y))
                draw.text(
                    (x + 8, y + 274),
                    f"{item['id']} {stamp(item['requested_time'])}",
                    font=font,
                    fill="white",
                )
        sheet.save(directory / f"sheet-{page // 12:03}.jpg", quality=90)
    return evidence
