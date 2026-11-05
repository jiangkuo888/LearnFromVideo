"""LearnFromVideo core; Hypit-derived workflow, see LICENSE and PROVENANCE.md."""

import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def run(args, timeout=900):
    p = subprocess.run(
        [str(x) for x in args],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        shell=False,
    )
    if p.returncode:
        raise RuntimeError(
            Path(str(args[0])).name + ": " + re.sub(r"https?://\S+", "[URL]", p.stderr[-2500:])
        )
    return p.stdout


def stamp(t):
    millis = round(float(t) * 1000)
    seconds, fraction = divmod(millis, 1000)
    return f"{seconds // 3600:02}:{seconds // 60 % 60:02}:{seconds % 60:02}.{fraction:03}"


def canonical(source):
    u = urlsplit(source)
    if u.scheme in ("http", "https"):
        if u.hostname in ("www.bilibili.com", "bilibili.com"):
            return urlunsplit((u.scheme, u.netloc, u.path, "", ""))
        return source
    return str(Path(source).resolve())
