"""Check built distributions for attribution and accidental private artifacts."""

import argparse
import hashlib
import json
import re
import stat
import tarfile
import tomllib
import zipfile
from pathlib import Path, PurePosixPath


def check(names):
    forbidden = {".git", ".venv", ".private", "runs", "logs", "__pycache__", ".env"}
    private_names = {"transcript.json", "transcript.md", "browser-source.json", "audio.wav"}
    for name in names:
        path = PurePosixPath(name.replace("\\", "/"))
        parts = set(path.parts)
        if path.is_absolute() or ".." in parts or re.match(r"^[A-Za-z]:", name):
            raise ValueError(f"Unsafe archive path: {name}")
        if (
            parts & forbidden
            or path.name in private_names
            or path.name.startswith((".env.", "cookies"))
            or path.suffix.lower()
            in {
                ".mp4",
                ".webm",
                ".wav",
                ".m4s",
                ".vtt",
                ".srt",
                ".pyc",
                ".bin",
                ".safetensors",
                ".pt",
            }
        ):
            raise ValueError(f"Private/generated artifact in release: {name}")


def scan_text(name, data):
    """Catch concrete private material; this is not a general secret-detection guarantee."""
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return
    patterns = {
        "signed media URL or credential": r"(?i)(?:auth_key|upsig|access_token|refresh_token|api_key|signature)=[A-Za-z0-9_-]{12,}",
        "private key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        "machine-specific user path": r"(?:[A-Za-z]:[/\\]Users[/\\][^\s<>/\\]+[/\\]|/(?:home|Users)/[^\s<>/]+/)",
    }
    for label, pattern in patterns.items():
        if re.search(pattern, text):
            raise ValueError(f"Possible {label} in {name}; inspect locally (value withheld)")


def inspect_archive(artifact, root):
    files = {}
    if artifact.suffix == ".gz":
        with tarfile.open(artifact) as archive:
            check(archive.getnames())
            for member in archive.getmembers():
                if member.issym() or member.islnk() or not (member.isfile() or member.isdir()):
                    raise ValueError(f"Unsafe archive entry: {member.name}")
                if member.isfile():
                    files[member.name] = archive.extractfile(member).read()
    else:
        with zipfile.ZipFile(artifact) as archive:
            check(archive.namelist())
            for member in archive.infolist():
                if stat.S_ISLNK(member.external_attr >> 16):
                    raise ValueError(f"Symbolic link in archive: {member.filename}")
                if not member.is_dir():
                    files[member.filename] = archive.read(member)
    for name, data in files.items():
        scan_text(name, data)
    for required in ("LICENSE", "NOTICE"):
        matches = [data for name, data in files.items() if name.endswith("/" + required)]
        if not matches or any(data != (root / required).read_bytes() for data in matches):
            raise ValueError(f"Missing or altered {required}: {artifact.name}")
    if artifact.name == "learn-from-video.zip":
        prefix = "learn-from-video/"
        bundle = json.loads(files[prefix + "bundle.json"])
        actual = {
            name[len(prefix) :]: hashlib.sha256(data).hexdigest()
            for name, data in files.items()
            if name != prefix + "bundle.json"
        }
        if bundle["files"] != actual:
            raise ValueError("Skill bundle integrity manifest does not match its contents")
    return len(files)


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, default=root / "dist")
    args = parser.parse_args()
    version = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"][
        "version"
    ]
    artifacts = [
        args.dist / f"learnfromvideo-{version}-py3-none-any.whl",
        args.dist / f"learnfromvideo-{version}.tar.gz",
        args.dist / "learn-from-video.zip",
    ]
    checksums, reports = [], []
    for artifact in artifacts:
        count = inspect_archive(artifact, root)
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        checksums.append(f"{digest}  {artifact.name}")
        reports.append({"artifact": artifact.name, "sha256": digest, "files": count})
        print(f"OK: {artifact.name} ({count} files)")
    (args.dist / "SHA256SUMS").write_text("\n".join(checksums) + "\n", encoding="utf-8")
    (args.dist / "release-manifest.json").write_text(
        json.dumps(
            {
                "version": version,
                "license": "LicenseRef-Hypit-Additional-Conditions",
                "artifacts": reports,
                "scope": "Local content and integrity checks; not publisher attestation.",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
