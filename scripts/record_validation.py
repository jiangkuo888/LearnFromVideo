"""Export a portable real-run report without full transcripts or private URLs."""

import argparse
import importlib.metadata
from pathlib import Path
from urllib.parse import urlsplit

from learnfromvideo.core import read, run, save


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    folder = args.run.resolve()
    manifest = read(folder / "manifest.json")
    source = manifest["source"]
    if urlsplit(source).scheme not in ("http", "https"):
        source = "local-file:" + Path(source).name
    if any(token in source.lower() for token in ("auth_key=", "upsig=", "signature=", "token=")):
        raise SystemExit("Refusing to publish a signed/private source address")
    transcript = read(folder / "transcript.json")
    probe = read(folder / "probe.json")
    report = {
        "report_schema": "learnfromvideo.validation-report@1",
        "recorded_at": manifest["created_at"],
        "source": source,
        "title": manifest.get("title"),
        "duration_seconds": manifest["duration"],
        "sha256": manifest["media_sha256"],
        "acquisition": manifest["acquisition"],
        "subtitle_streams": sum(s["codec_type"] == "subtitle" for s in probe["streams"]),
        "available_subtitle_language_count": len(manifest.get("available_subtitle_languages", [])),
        "available_auto_caption_language_count": len(
            manifest.get("available_auto_caption_languages", [])
        ),
        "transcript_origin": transcript["origin"],
        "transcript_segments": len(transcript["segments"]),
        "overview_frames": len(read(folder / "frames/index.json")),
        "revisit_frames": len(read(folder / "revisit/index.json")),
        "validation": read(folder / "validation.json"),
        "versions": {},
        "ffmpeg": run(["ffmpeg", "-version"], timeout=20).splitlines()[0],
        "scope": "Agent-reviewed captions/ASR and sampled visual evidence; no word-error-rate measurement.",
    }
    for name in ("learnfromvideo", "yt-dlp", "faster-whisper", "ctranslate2"):
        try:
            report["versions"][name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            report["versions"][name] = None
    save(args.out, report)
    print(args.out)


if __name__ == "__main__":
    main()
