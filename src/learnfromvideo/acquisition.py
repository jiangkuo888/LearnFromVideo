"""LearnFromVideo acquisition; Hypit-derived workflow, see LICENSE and PROVENANCE.md."""

import re
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlsplit

import requests

from .core import canonical, read, run


def download_stream(url, path, headers):
    if urlsplit(url).scheme not in ("http", "https"):
        raise ValueError("Media URL must be HTTP(S)")
    temp = path.with_suffix(".part")
    # Bounded standard HTTP ranges avoid proxy buffering of large media responses.
    # No auth material or signed addresses are persisted in progress/error logs.
    first = requests.get(url, headers=headers | {"Range": "bytes=0-0"}, timeout=(20, 45))
    first.raise_for_status()
    match = re.fullmatch(r"bytes 0-0/(\d+)", first.headers.get("Content-Range", ""))
    if first.status_code == 206 and match:
        total, block_size = int(match[1]), 2 * 1024 * 1024

        def get_block(start):
            end = min(total - 1, start + block_size - 1)
            for attempt in range(2):
                try:
                    r = requests.get(
                        url, headers=headers | {"Range": f"bytes={start}-{end}"}, timeout=(20, 60)
                    )
                    r.raise_for_status()
                    if (
                        r.status_code != 206
                        or r.headers.get("Content-Range") != f"bytes {start}-{end}/{total}"
                        or len(r.content) != end - start + 1
                    ):
                        raise RuntimeError("CDN returned inconsistent byte range")
                    return r.content
                except (requests.RequestException, RuntimeError):
                    if attempt:
                        raise
                    time.sleep(1)

        with temp.open("wb") as f, ThreadPoolExecutor(max_workers=4) as pool:
            for i, data in enumerate(pool.map(get_block, range(0, total, block_size))):
                f.write(data)
                if i % 10 == 0:
                    print(
                        f"Downloading {path.name}: {min((i + 1) * block_size, total)}/{total} bytes",
                        flush=True,
                    )
        if temp.stat().st_size != total:
            raise RuntimeError("Downloaded size mismatch")
    else:
        first.close()
        with requests.get(url, headers=headers, stream=True, timeout=(20, 60)) as r:
            r.raise_for_status()
            with temp.open("wb") as f:
                for block in r.iter_content(1024 * 1024):
                    f.write(block)
    temp.replace(path)


def acquire(args, folder):
    source, target = canonical(args.source), folder / "source.mp4"
    if args.browser_source:
        data = read(args.browser_source)
        if canonical(data["url"]) != source:
            raise ValueError("Browser export belongs to another source")
        headers = {"Referer": source, "User-Agent": data.get("user_agent", "Mozilla/5.0")}
        for key in ("video", "audio"):
            download_stream(data[key + "_url"], folder / (key + ".m4s"), headers)
        run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-nostdin",
                "-n",
                "-i",
                folder / "video.m4s",
                "-i",
                folder / "audio.m4s",
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-c",
                "copy",
                target,
            ]
        )
        for key in ("video", "audio"):
            (folder / (key + ".m4s")).unlink()
        return {k: data.get(k) for k in ("id", "title", "author")} | {
            "acquisition": "browser-export"
        }
    if urlsplit(source).scheme not in ("http", "https"):
        shutil.copyfile(source, target)
        return {"title": Path(source).stem, "acquisition": "local-file"}
    cmd = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--ignore-config",
        "--no-update",
        "--no-remote-components",
        "--no-plugin-dirs",
        "--no-playlist",
        "--no-progress",
        "--no-js-runtimes",
        "--js-runtimes",
        "node",
        "--format",
        "bv*+ba/b",
        "--format-sort",
        "res:1080,vcodec:h264",
        "--merge-output-format",
        "mp4",
        "--write-info-json",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs",
        args.language + ".*",
        "--sub-format",
        "vtt/srt/best",
        "--output",
        str(folder / "source.%(ext)s"),
    ]
    if args.cookies:
        cmd += ["--cookies", str(Path(args.cookies).resolve())]
    run(cmd + [source])
    info = read(folder / "source.info.json")
    (folder / "source.info.json").unlink()  # Avoid retaining expiring URLs / request metadata.
    if not target.exists():
        candidates = [p for p in folder.glob("source.*") if p.suffix in (".mkv", ".webm", ".mov")]
        if len(candidates) != 1:
            raise RuntimeError("No unique downloaded video")
        run(["ffmpeg", "-v", "error", "-nostdin", "-n", "-i", candidates[0], "-c", "copy", target])
        candidates[0].unlink()
    return {
        "id": info.get("id"),
        "title": info.get("title"),
        "author": info.get("uploader"),
        "acquisition": "yt-dlp",
        "available_subtitle_languages": sorted(info.get("subtitles", {})),
        "available_auto_caption_languages": sorted(info.get("automatic_captions", {})),
    }
