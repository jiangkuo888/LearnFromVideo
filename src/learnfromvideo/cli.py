"""LearnFromVideo cli; Hypit-derived workflow, see LICENSE and PROVENANCE.md."""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

from . import __version__
from .core import read, run, save
from .learning import search, validate
from .media import frames
from .pipeline import prepare
from .transcripts import parse_subtitles, transcribe, write_transcript


def main():
    parser = argparse.ArgumentParser(
        prog="lfv", description="LearnFromVideo evidence tools for AI agents"
    )
    parser.add_argument("--version", action="version", version=f"LearnFromVideo {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("source")
    p.add_argument("--out", required=True)
    p.add_argument("--goal", default="理解视频并提炼可复用知识与步骤")
    p.add_argument("--language", default="zh")
    p.add_argument("--every", type=int, default=30)
    p.add_argument("--browser-source")
    p.add_argument("--subtitles")
    p.add_argument("--cookies")
    p.add_argument("--asr", action="store_true")
    p.add_argument("--model", default="small")
    p = sub.add_parser("frames")
    p.add_argument("run")
    p.add_argument("--at", required=True)
    p.add_argument("--output", default="revisit")
    p = sub.add_parser("clip")
    p.add_argument("run")
    p.add_argument("--start", type=float, required=True)
    p.add_argument("--end", type=float, required=True)
    p = sub.add_parser("search")
    p.add_argument("run")
    p.add_argument("query")
    p = sub.add_parser("validate")
    p.add_argument("run")
    p = sub.add_parser("transcribe")
    p.add_argument("run")
    p.add_argument("--subtitles")
    p.add_argument("--language", default="zh")
    p.add_argument("--model", default="small")
    p = sub.add_parser("import-browser")
    p.add_argument("export")
    p.add_argument("--out", required=True)
    sub.add_parser("doctor")
    args = parser.parse_args()
    try:
        if args.command == "doctor":
            import importlib.util

            import yt_dlp.version

            print(
                json.dumps(
                    {
                        "learnfromvideo": __version__,
                        "python": sys.version.split()[0],
                        "yt_dlp": yt_dlp.version.__version__,
                        "ffmpeg": shutil.which("ffmpeg"),
                        "ffprobe": shutil.which("ffprobe"),
                        "node": shutil.which("node"),
                        "asr": bool(importlib.util.find_spec("faster_whisper")),
                    },
                    indent=2,
                )
            )
        elif args.command == "import-browser":
            data = read(args.export)
            directory = Path(args.out).resolve()
            if directory.exists() and any(directory.iterdir()):
                raise ValueError("Browser import output must be empty")
            source = data["source"]
            allowed = (
                "schema",
                "url",
                "id",
                "title",
                "duration",
                "author",
                "video_url",
                "audio_url",
                "user_agent",
            )
            save(directory / "browser-source.json", {k: source[k] for k in allowed if k in source})
            if data.get("subtitles"):
                save(directory / "subtitles.json", data["subtitles"])
            print(directory)
        elif args.command == "prepare":
            if args.every <= 0:
                raise ValueError("--every must be positive")
            prepare(args)
        else:
            folder = Path(args.run).resolve()
            if args.command == "frames":
                if Path(args.output).name != args.output or args.output in (".", ".."):
                    raise ValueError("--output must be one directory name inside run")
                print(
                    json.dumps(
                        frames(folder, [float(t) for t in args.at.split(",")], args.output),
                        indent=2,
                    )
                )
            elif args.command == "search":
                print(json.dumps(search(folder, args.query), ensure_ascii=False, indent=2))
            elif args.command == "validate":
                print(json.dumps(validate(folder), indent=2))
            elif args.command == "clip":
                duration = read(folder / "manifest.json")["duration"]
                if not (0 <= args.start < args.end <= duration):
                    raise ValueError("Clip must be within source")
                target = folder / f"clip-{args.start:g}-{args.end:g}.mp4"
                run(
                    [
                        "ffmpeg",
                        "-v",
                        "error",
                        "-nostdin",
                        "-n",
                        "-ss",
                        args.start,
                        "-i",
                        folder / "source.mp4",
                        "-t",
                        args.end - args.start,
                        "-c:v",
                        "libx264",
                        "-preset",
                        "fast",
                        "-c:a",
                        "aac",
                        target,
                    ]
                )
                print(target)
            elif args.command == "transcribe":
                m = read(folder / "manifest.json")
                segs = (
                    parse_subtitles(args.subtitles, m["duration"])
                    if args.subtitles
                    else transcribe(folder / "source.mp4", folder, args.language, args.model)
                )
                write_transcript(
                    folder,
                    segs,
                    "supplied-subtitles" if args.subtitles else "faster-whisper:" + args.model,
                    m["duration"],
                )
                m["state"] = (
                    "evidence-ready" if (folder / "frames/index.json").exists() else "needs-frames"
                )
                (folder / "validation.json").unlink(missing_ok=True)
                save(folder / "manifest.json", m)
                print(folder / "transcript.json")
    except Exception as e:
        print("LearnFromVideo: " + re.sub(r"https?://\S+", "[URL]", str(e)), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
