"""Check public repository files, local Markdown links and immutable action references."""

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

from check_release import check, scan_text


def main():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        capture_output=True,
        check=True,
    )
    paths = {Path(name.decode("utf-8")) for name in result.stdout.split(b"\0") if name}
    check(relative.as_posix() for relative in paths)
    count = 0
    for relative in sorted(paths):
        path = root / relative
        if path.is_symlink():
            raise ValueError(f"Symbolic link in public source tree: {relative}")
        if not path.is_file():
            continue
        scan_text(relative.as_posix(), path.read_bytes())
        if (
            relative.suffix == ".md"
            and "vendor" not in relative.parts
            and relative.name != "hypit-reference-video.md"
        ):
            text = path.read_text(encoding="utf-8-sig")
            for match in re.finditer(r"\[[^\]]*\]\(([^\s)]+)\)", text):
                target = unquote(match[1].split("#", 1)[0])
                if not target or urlsplit(target).scheme or target.startswith("<"):
                    continue
                if not (path.parent / target).exists():
                    raise ValueError(f"Broken local link in {relative}: {target}")
        if relative.suffix in (".yml", ".yaml") and "workflows" in relative.parts:
            for reference in re.findall(r"uses:\s*([^\s#]+)", path.read_text(encoding="utf-8")):
                if not reference.startswith("./") and not re.fullmatch(
                    r"[^@]+@[0-9a-f]{40}", reference
                ):
                    raise ValueError(f"Unpinned action in {relative}: {reference}")
        count += 1
    print(f"Repository checks passed: {count} files; content, local links, action pins")


if __name__ == "__main__":
    main()
