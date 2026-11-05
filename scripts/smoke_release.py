"""Install wheel and skill ZIP in fresh directories without the source checkout."""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from pathlib import Path


def execute(command, cwd):
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=240,
        check=True,
    )
    return result.stdout.strip()


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, default=root / "dist")
    args = parser.parse_args()
    uv = shutil.which("uv")
    if not uv:
        raise SystemExit("uv is required")
    version = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"][
        "version"
    ]
    wheel = (args.dist / f"watch2skill-{version}-py3-none-any.whl").resolve()
    bundle = (args.dist / "watch2skill.zip").resolve()
    with tempfile.TemporaryDirectory(prefix="watch2skill-install-smoke-") as temporary:
        work = Path(temporary)
        environment = work / "wheel-env"
        execute([uv, "venv", "--python", sys.executable, str(environment)], work)
        python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        execute([uv, "pip", "install", "--python", str(python), str(wheel)], work)
        wheel_version = execute([str(python), "-I", "-m", "watch2skill", "--version"], work)
        if wheel_version != f"Watch2Skill {version}":
            raise ValueError("Installed wheel version mismatch")
        with zipfile.ZipFile(bundle) as archive:
            archive.extractall(work / "skill")
        launcher = work / "skill/watch2skill/scripts/watch2skill.py"
        skill_version = execute([sys.executable, str(launcher), "--version"], work)
        if skill_version != wheel_version:
            raise ValueError("Installed skill version mismatch")
        print(
            json.dumps(
                {
                    "wheel": wheel_version,
                    "skill": skill_version,
                    "isolated_from_checkout": True,
                    "asr_model_downloaded": False,
                }
            )
        )


if __name__ == "__main__":
    main()
