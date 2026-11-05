"""Portable launcher; the bundled runtime does not depend on the original project."""

import shutil
import subprocess
import sys
from pathlib import Path

uv = shutil.which("uv")
if not uv:
    raise SystemExit("Watch2Skill requires uv on PATH")
runtime = Path(__file__).resolve().parent / "runtime"
if not (runtime / "pyproject.toml").exists():
    runtime = Path(__file__).resolve().parents[3]
if not (runtime / "pyproject.toml").exists():
    raise SystemExit(
        "Missing tool runtime. Install the built skill ZIP or use a full source checkout."
    )
arguments = sys.argv[1:]
needs_asr = "--asr" in arguments or (
    arguments and arguments[0] == "transcribe" and "--subtitles" not in arguments
)
extras = ["--extra", "asr"] if needs_asr else []
raise SystemExit(
    subprocess.call(
        [
            uv,
            "run",
            "--locked",
            "--no-dev",
            "--python",
            "3.11",
            "--project",
            str(runtime),
            *extras,
            "python",
            "-m",
            "watch2skill",
            *arguments,
        ]
    )
)
