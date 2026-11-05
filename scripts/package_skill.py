"""Build a portable ZIP from one source tree; optionally install or explicitly update."""

import argparse
import hashlib
import json
import shutil
import tempfile
import tomllib
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def build(root, staging):
    skill = staging / "watch2skill"
    shutil.copytree(
        root / "skills/watch2skill",
        skill,
        ignore=shutil.ignore_patterns("runtime", ".venv", "__pycache__"),
    )
    runtime = skill / "scripts/runtime"
    runtime.mkdir(parents=True)
    for name in (
        "pyproject.toml",
        "uv.lock",
        "LICENSE",
        "NOTICE",
        "PROVENANCE.md",
        "README.md",
        "README.zh-CN.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "CHANGELOG.md",
        "CODE_OF_CONDUCT.md",
    ):
        shutil.copy2(root / name, runtime / name)
    for name in ("src", "vendor", "references", "docs", "examples"):
        shutil.copytree(root / name, runtime / name, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(root / "references/browser-export.js", skill / "references/browser-export.js")
    for name in ("LICENSE", "NOTICE", "PROVENANCE.md"):
        shutil.copy2(root / name, skill / name)
    version = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"][
        "version"
    ]
    checksums = {
        path.relative_to(skill).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(skill.rglob("*"), key=lambda p: p.relative_to(skill).as_posix())
        if path.is_file()
    }
    (skill / "bundle.json").write_text(
        json.dumps(
            {
                "schema": "learnfromvideo.skill-bundle@1",
                "version": version,
                "files": checksums,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return skill


def write_archive(skill, output):
    """Stable file ordering, permissions and timestamps for identical source inputs."""
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(skill.rglob("*"), key=lambda p: p.relative_to(skill).as_posix()):
            if path.is_symlink():
                raise ValueError("Skill bundles cannot contain symbolic links")
            if path.is_file():
                info = zipfile.ZipInfo(
                    f"{skill.name}/{path.relative_to(skill).as_posix()}", (1980, 1, 1, 0, 0, 0)
                )
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, path.read_bytes())


def install(skill, directory, update=False):
    """Replace the managed tree atomically and retain a rollback copy outside skills."""
    directory = directory.expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / skill.name
    if destination.is_symlink() or destination.resolve().parent != directory:
        raise ValueError("Skill destination must stay inside the selected installation directory")
    backup = None
    if destination.exists():
        if not update:
            raise ValueError(f"Skill already exists; use --update: {destination}")
        definition = destination / "SKILL.md"
        project = destination / "scripts/runtime/pyproject.toml"
        if (
            not definition.is_file()
            or "name: watch2skill" not in definition.read_text(encoding="utf-8")
            or not project.is_file()
            or tomllib.loads(project.read_text(encoding="utf-8"))["project"]["name"]
            != "watch2skill"
        ):
            raise ValueError("Refusing to replace an unrelated directory")
        backup_root = directory.parent / "watch2skill-backups"
        if backup_root.is_symlink() or backup_root.resolve().parent != directory.parent:
            raise ValueError("Backup directory must stay inside the installation parent")
        backup_root.mkdir(exist_ok=True)
        backup = backup_root / datetime.now(timezone.utc).strftime("watch2skill-%Y%m%dT%H%M%S%fZ")
    with tempfile.TemporaryDirectory(prefix=".watch2skill-install-", dir=directory) as temporary:
        staged = Path(temporary) / skill.name
        shutil.copytree(skill, staged)
        if backup:
            destination.rename(backup)
        try:
            staged.rename(destination)
        except OSError:
            if backup:
                backup.rename(destination)
            raise
    return destination, backup


def migrate_legacy(directory):
    """Archive only a verified legacy skill after the new skill is installed."""
    directory = directory.expanduser().resolve()
    legacy = directory / "learn-from-video"
    current = directory / "watch2skill"
    if not legacy.exists():
        return None
    for path in (legacy, current):
        if path.is_symlink() or path.resolve().parent != directory:
            raise ValueError("Skill migration must stay inside the installation directory")
    old_definition = legacy / "SKILL.md"
    old_project = legacy / "scripts/runtime/pyproject.toml"
    new_definition = current / "SKILL.md"
    if (
        not new_definition.is_file()
        or "name: watch2skill" not in new_definition.read_text(encoding="utf-8")
        or not old_definition.is_file()
        or "name: learn-from-video" not in old_definition.read_text(encoding="utf-8")
        or not old_project.is_file()
        or tomllib.loads(old_project.read_text(encoding="utf-8"))["project"]["name"]
        != "learnfromvideo"
    ):
        raise ValueError("Refusing to migrate an unverified legacy installation")
    backup_root = directory.parent / "watch2skill-backups"
    if backup_root.is_symlink() or backup_root.resolve().parent != directory.parent:
        raise ValueError("Backup directory must stay inside the installation parent")
    backup_root.mkdir(exist_ok=True)
    backup = backup_root / datetime.now(timezone.utc).strftime("learn-from-video-%Y%m%dT%H%M%S%fZ")
    legacy.rename(backup)
    return backup


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install", type=Path)
    parser.add_argument(
        "--migrate-legacy",
        action="store_true",
        help="Archive a verified learn-from-video skill after installation",
    )
    parser.add_argument(
        "--update", action="store_true", help="Explicitly update an existing installation"
    )
    parser.add_argument("--output", type=Path, default=root / "dist/watch2skill.zip")
    args = parser.parse_args()
    if args.update and not args.install:
        parser.error("--update requires --install")
    if args.migrate_legacy and not args.install:
        parser.error("--migrate-legacy requires --install")
    with tempfile.TemporaryDirectory(prefix="watch2skill-skill-") as temporary:
        staging = Path(temporary)
        skill = build(root, staging)
        output = args.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        archive = staging / "skill.zip"
        write_archive(skill, archive)
        shutil.copy2(archive, output)
        print(output)
        if args.install:
            destination, backup = install(skill, args.install, args.update)
            print(destination)
            if backup:
                print(f"Previous installation retained: {backup}")
            if args.migrate_legacy:
                previous = migrate_legacy(args.install)
                if previous:
                    print(f"Legacy skill retained: {previous}")


if __name__ == "__main__":
    main()
