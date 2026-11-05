"""Offline CLI smoke test using generated media; no copyrighted fixtures or model download."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg required")
class LocalPipelineTests(unittest.TestCase):
    def test_generated_media_to_validated_learning(self):
        with tempfile.TemporaryDirectory(prefix="lfv-e2e-") as temporary:
            root = Path(temporary)
            media = root / "fixture.mp4"
            subprocess.run(
                [
                    "ffmpeg",
                    "-v",
                    "error",
                    "-nostdin",
                    "-n",
                    "-f",
                    "lavfi",
                    "-i",
                    "color=c=blue:s=320x180:r=10:d=2",
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=frequency=440:duration=2",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-c:a",
                    "aac",
                    "-shortest",
                    str(media),
                ],
                check=True,
                capture_output=True,
                timeout=30,
            )
            subtitles = root / "fixture.json"
            subtitles.write_text(
                json.dumps({"segments": [{"start": 0, "end": 1.9, "text": "blue fixture"}]}),
                encoding="utf-8",
            )
            run = root / "run"

            def cli(*arguments):
                result = subprocess.run(
                    [sys.executable, "-m", "learnfromvideo", *map(str, arguments)],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=45,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                return result.stdout

            cli("prepare", media, "--out", run, "--subtitles", subtitles, "--every", 1)
            manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["state"], "evidence-ready")
            cli("frames", run, "--at", "0.5")
            cli("clip", run, "--start", "0", "--end", "1")
            results = json.loads(cli("search", run, "blue"))
            self.assertEqual(results[0]["text"], "blue fixture")
            frame = "revisit/000000.500.jpg"
            learning = {
                "summary": "A generated blue video fixture.",
                "claims": [
                    {
                        "text": "Blue frame",
                        "start": 0,
                        "end": 1,
                        "kind": "observation",
                        "evidence": [frame],
                    }
                ],
                "reviewed_frames": [frame],
                "limitations": ["Automated test fixture only"],
                "practice": {"status": "not-run"},
            }
            (run / "learning.json").write_text(json.dumps(learning), encoding="utf-8")
            self.assertTrue(json.loads(cli("validate", run))["passed"])
