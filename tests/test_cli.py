import math
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from learnfromvideo.acquisition import download_stream
from learnfromvideo.core import save
from learnfromvideo.learning import search, validate
from learnfromvideo.transcripts import parse_subtitles, validate_segments


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_bilibili_and_vtt_import(self):
        save(self.root / "b.json", {"body": [{"from": 1, "to": 3, "content": "工具调用"}]})
        self.assertEqual(parse_subtitles(self.root / "b.json", 10)[0]["text"], "工具调用")
        (self.root / "s.vtt").write_text(
            "WEBVTT\n\n00:00:01.000 --> 00:00:03.000 align:start\n<b>工具</b> &amp; memory\n",
            encoding="utf-8",
        )
        self.assertEqual(parse_subtitles(self.root / "s.vtt", 10)[0]["text"], "工具 & memory")

    def test_reject_nonfinite_or_outside_transcript(self):
        for start, end in [(math.nan, 2), (1, math.inf), (-1, 2), (3, 2), (1, 30)]:
            with self.assertRaises(ValueError):
                validate_segments([{"start": start, "end": end, "text": "test"}], 10)

    def test_youtube_rolling_captions_do_not_repeat_context(self):
        path = self.root / "rolling.vtt"
        path.write_text(
            "WEBVTT\n\n00:00:00.000 --> 00:00:02.000\n"
            "python <00:00:01.000>is useful\n\n"
            "00:00:02.000 --> 00:00:02.010\npython is useful\n\n"
            "00:00:02.010 --> 00:00:04.000\npython is useful\nfor <00:00:03.000>learning\n",
            encoding="utf-8",
        )
        segments = parse_subtitles(path, 10)
        self.assertEqual([s["text"] for s in segments], ["python is useful", "for learning"])

    def test_ordinary_repeated_speech_is_preserved(self):
        path = self.root / "repeat.srt"
        path.write_text(
            "1\n00:00:00,000 --> 00:00:01,000\nhello world\n\n"
            "2\n00:00:01,000 --> 00:00:02,000\nhello world\n",
            encoding="utf-8",
        )
        self.assertEqual(len(parse_subtitles(path, 10)), 2)

    def fixture(self):
        save(
            self.root / "manifest.json",
            {"state": "evidence-ready", "duration": 10, "source": "https://example.com/watch?v=x"},
        )
        save(self.root / "frames/index.json", [{"path": "frames/a.jpg", "requested_time": 5}])
        (self.root / "frames/a.jpg").write_bytes(b"test")
        learning = {
            "summary": "summary",
            "claims": [
                {
                    "text": "observed",
                    "start": 4,
                    "end": 6,
                    "kind": "observation",
                    "evidence": ["frames/a.jpg"],
                }
            ],
            "reviewed_frames": ["frames/a.jpg"],
            "limitations": [],
            "practice": {"status": "not-run"},
        }
        save(self.root / "learning.json", learning)
        return learning

    def test_valid_references_do_not_claim_mastery(self):
        self.fixture()
        result = validate(self.root)
        self.assertTrue(result["passed"])
        self.assertEqual(result["practice"], "not-run")

    def test_reject_frame_outside_claim_interval(self):
        learning = self.fixture()
        learning["claims"][0]["end"] = 4.5
        save(self.root / "learning.json", learning)
        with self.assertRaises(ValueError):
            validate(self.root)

    def test_failed_recheck_invalidates_old_success(self):
        learning = self.fixture()
        validate(self.root)
        self.assertTrue((self.root / "validation.json").exists())
        learning["claims"][0]["end"] = 4.5
        save(self.root / "learning.json", learning)
        with self.assertRaises(ValueError):
            validate(self.root)
        self.assertFalse((self.root / "validation.json").exists())

    def test_reject_evidence_path_escape(self):
        learning = self.fixture()
        learning["reviewed_frames"] = ["../outside.jpg"]
        save(self.root / "learning.json", learning)
        with self.assertRaises(ValueError):
            validate(self.root)

    def test_search_retrieves_source_time(self):
        self.fixture()
        save(
            self.root / "chunks.json", [{"start": 1, "end": 8, "text": "工具与 memory", "id": "c0"}]
        )
        self.assertEqual(
            search(self.root, "memory")[0]["source_link"], "https://example.com/watch?v=x&t=1"
        )
        self.assertEqual(search(self.root, "unknown"), [])

    def test_parallel_http_ranges_reassemble_exact_bytes(self):
        payload = bytes(range(256)) * 20000

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                a, b = map(int, self.headers["Range"].removeprefix("bytes=").split("-"))
                self.send_response(206)
                self.send_header("Content-Range", f"bytes {a}-{b}/{len(payload)}")
                self.send_header("Content-Length", str(b - a + 1))
                self.end_headers()
                self.wfile.write(payload[a : b + 1])

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            output = self.root / "source.bin"
            download_stream(f"http://127.0.0.1:{server.server_port}/video", output, {})
            self.assertEqual(output.read_bytes(), payload)
            self.assertFalse(output.with_suffix(".part").exists())
        finally:
            server.shutdown()
            server.server_close()
            worker.join()


if __name__ == "__main__":
    unittest.main()
