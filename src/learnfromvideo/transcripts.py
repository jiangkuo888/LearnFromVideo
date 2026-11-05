"""LearnFromVideo transcripts; Hypit-derived workflow, see LICENSE and PROVENANCE.md."""

import html
import json
import math
import re
from pathlib import Path

from .core import run, save, stamp


def validate_segments(segments, duration):
    result = []
    for s in segments:
        a, b, text = float(s["start"]), float(s["end"]), str(s["text"]).strip()
        if not (math.isfinite(a) and math.isfinite(b) and 0 <= a < b <= duration + 2):
            raise ValueError(f"Invalid transcript interval: {a}..{b}")
        if text:
            result.append({"start": a, "end": b, "text": text})
    if not result:
        raise ValueError("No timed transcript segments")
    return sorted(result, key=lambda s: (s["start"], s["end"]))


def parse_subtitles(path, duration):
    content = Path(path).read_text(encoding="utf-8-sig")
    if content.lstrip().startswith(("{", "[")):
        data = json.loads(content)
        if isinstance(data, dict) and "body" in data:
            segs = [
                {"start": x["from"], "end": x["to"], "text": x["content"]} for x in data["body"]
            ]
        else:
            segs = data if isinstance(data, list) else data["segments"]
    else:
        segs = []
        rolling = bool(re.search(r"<\d{2}:\d{2}:\d{2}\.\d{3}>", content))
        pattern = r"(?m)^(\d{1,2}:\d{2}(?::\d{2})?[.,]\d{3})\s*-->\s*(\d{1,2}:\d{2}(?::\d{2})?[.,]\d{3})[^\n]*\n(.*?)(?=\n\s*\n|\Z)"

        def sec(t):
            return sum(
                float(v) * 60**i for i, v in enumerate(reversed(t.replace(",", ".").split(":")))
            )

        for m in re.finditer(pattern, content, re.S):
            segs.append(
                {
                    "start": sec(m[1]),
                    "end": sec(m[2]),
                    "text": html.unescape(re.sub(r"<[^>]*>", "", m[3])).replace("\n", " "),
                }
            )
        if rolling:
            # YouTube auto-captions repeat the previous line in adjacent cues.
            # Apply overlap removal only to explicitly timestamped rolling VTT;
            # ordinary captions may legitimately repeat spoken phrases.
            cleaned, previous, previous_end = [], [], -1
            for segment in segs:
                words = segment["text"].split()
                overlap = 0
                if segment["start"] <= previous_end + 0.25:
                    for size in range(min(len(previous), len(words)), 0, -1):
                        if previous[-size:] == words[:size]:
                            if size >= 2 or size == len(words):
                                overlap = size
                            break
                previous, previous_end = words, segment["end"]
                if overlap == len(words):
                    if cleaned:
                        cleaned[-1]["end"] = max(cleaned[-1]["end"], segment["end"])
                    continue
                cleaned.append(segment | {"text": " ".join(words[overlap:])})
            segs = cleaned
    return validate_segments(segs, duration)


def transcribe(media, folder, language, model):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise RuntimeError("Install optional ASR with uv sync --extra asr, or supply subtitles")
    audio = folder / "audio.wav"
    if not audio.exists():
        run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-nostdin",
                "-n",
                "-i",
                media,
                "-vn",
                "-ar",
                "16000",
                "-ac",
                "1",
                audio,
            ]
        )
    recognizer = WhisperModel(model, device="cpu", compute_type="int8")
    segments, _ = recognizer.transcribe(str(audio), language=language, vad_filter=True)
    return [{"start": s.start, "end": s.end, "text": s.text} for s in segments]


def write_transcript(folder, segments, origin, duration):
    segments = validate_segments(segments, duration)
    save(
        folder / "transcript.json",
        {"schema": "learnfromvideo.transcript@1", "origin": origin, "segments": segments},
    )
    (folder / "transcript.md").write_text(
        "\n".join(f"[{stamp(s['start'])}–{stamp(s['end'])}] {s['text']}" for s in segments),
        encoding="utf-8",
    )
    chunks = []
    for s in segments:
        if not chunks or s["start"] >= chunks[-1]["start"] + 90:
            chunks.append({"id": f"c{len(chunks):04}", **s})
        else:
            chunks[-1]["end"] = max(chunks[-1]["end"], s["end"])
            chunks[-1]["text"] += " " + s["text"]
    save(folder / "chunks.json", chunks)
